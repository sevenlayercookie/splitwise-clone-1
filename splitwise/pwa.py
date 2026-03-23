import json
import os
import secrets
from http import cookies
from wsgiref.simple_server import make_server

from splitwise import Splitwise
from splitwise.backend import create_backend_app
from splitwise.category import Category
from splitwise.exception import (
    SplitwiseBadRequestException,
    SplitwiseException,
    SplitwiseNotAllowedException,
    SplitwiseNotFoundException,
    SplitwiseUnauthorizedException,
)
from splitwise.expense import Expense
from splitwise.group import Group
from splitwise.pwa_assets import APP_JS, ICON_SVG, INDEX_HTML, MANIFEST_JSON, SERVICE_WORKER_JS, STYLES_CSS
from splitwise.user import ExpenseUser, User

SDK_METHODS = [
    "getAuthorizeURL",
    "getAccessToken",
    "getOAuth2AuthorizeURL",
    "getOAuth2AccessToken",
    "getCurrentUser",
    "getUser",
    "updateUser",
    "getFriends",
    "getGroups",
    "getGroup",
    "createGroup",
    "deleteGroup",
    "addUserToGroup",
    "getExpenses",
    "getExpense",
    "createExpense",
    "updateExpense",
    "deleteExpense",
    "getCurrencies",
    "getCategories",
    "getComments",
    "createComment",
    "getNotifications",
]

STATIC_ROUTES = {
    "/": ("text/html; charset=utf-8", INDEX_HTML),
    "/styles.css": ("text/css; charset=utf-8", STYLES_CSS),
    "/app.js": ("application/javascript; charset=utf-8", APP_JS),
    "/manifest.json": ("application/manifest+json; charset=utf-8", MANIFEST_JSON),
    "/sw.js": ("application/javascript; charset=utf-8", SERVICE_WORKER_JS),
    "/icon.svg": ("image/svg+xml; charset=utf-8", ICON_SVG),
}

ERROR_STATUS = {
    SplitwiseBadRequestException: "400 Bad Request",
    SplitwiseUnauthorizedException: "401 Unauthorized",
    SplitwiseNotAllowedException: "403 Forbidden",
    SplitwiseNotFoundException: "404 Not Found",
}


class SplitwisePWAApp(object):
    def __init__(self, splitwise_factory=Splitwise, environment=None):
        self.splitwise_factory = splitwise_factory
        self.environment = environment or os.environ
        self.sessions = {}
        self.backend_app = create_backend_app()

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/") or "/"
        method = environ.get("REQUEST_METHOD", "GET").upper()
        session_id, session, session_cookie = self._get_session(environ)
        headers = self._default_headers(session_cookie)

        try:
            status, payload, content_type = self._route_request(method, path, environ, session, session_id)
            if content_type == "json":
                return self._respond_json(start_response, status, payload, headers)
            return self._respond(start_response, status, payload, headers, content_type)
        except ValueError as exc:
            return self._respond_json(start_response, "400 Bad Request", {"error": str(exc)}, headers)
        except SplitwiseException as exc:
            status = ERROR_STATUS.get(type(exc), "500 Internal Server Error")
            return self._respond_json(start_response, status, {"error": str(exc)}, headers)
        except Exception as exc:  # pragma: no cover - protective fallback
            return self._respond_json(start_response, "500 Internal Server Error", {"error": str(exc)}, headers)

    def _default_headers(self, session_cookie):
        headers = [
            ("X-Content-Type-Options", "nosniff"),
            ("Referrer-Policy", "same-origin"),
            (
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data: https:; style-src 'self'; "
                "script-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'",
            ),
        ]
        if session_cookie:
            headers.append(("Set-Cookie", session_cookie))
        return headers

    def _route_request(self, method, path, environ, session, session_id):
        if path.startswith("/api/v3.0/") or path in ("/authorize", "/oauth/authorize", "/oauth/token"):
            return self._delegate_to_backend(environ)
        if method == "GET":
            return self._handle_get(path, session, session_id)
        if method == "POST":
            return self._handle_post(path, environ, session)
        return "404 Not Found", {"error": "Route not found"}, "json"

    def _delegate_to_backend(self, environ):
        captured = {}

        def start_response(status, response_headers):
            captured["status"] = status
            captured["headers"] = response_headers

        body = b"".join(self.backend_app(environ, start_response))
        content_type = "application/octet-stream"
        for header, value in captured.get("headers", []):
            if header.lower() == "content-type":
                content_type = value
                break
        return captured["status"], body, content_type

    def _handle_get(self, path, session, session_id):
        if path in STATIC_ROUTES:
            content_type, body = STATIC_ROUTES[path]
            return "200 OK", body, content_type

        if path == "/api/config":
            return "200 OK", {
                "configured": self._has_client_credentials(session),
                "sdk_methods": SDK_METHODS,
                "session": self._session_summary(session),
                "session_id": session_id,
            }, "json"

        return "404 Not Found", {"error": "Route not found"}, "json"

    def _handle_post(self, path, environ, session):
        payload = self._read_json(environ)
        if path == "/api/session":
            self._merge_session(session, payload)
            return "200 OK", {"ok": True, "session": self._session_summary(session)}, "json"

        if path == "/api/session/clear":
            session.clear()
            return "200 OK", {"ok": True}, "json"

        if path.startswith("/api/operations/"):
            operation = path.rsplit("/", 1)[-1]
            if operation not in SDK_METHODS:
                return "404 Not Found", {"error": "Unknown operation"}, "json"
            return "200 OK", {
                "ok": True,
                "operation": operation,
                "data": self._dispatch_operation(operation, payload, session),
            }, "json"

        return "404 Not Found", {"error": "Route not found"}, "json"

    def _dispatch_operation(self, operation, payload, session):
        client = self._build_client(session)
        handlers = {
            "getAuthorizeURL": self._op_get_authorize_url,
            "getAccessToken": self._op_get_access_token,
            "getOAuth2AuthorizeURL": self._op_get_oauth2_authorize_url,
            "getOAuth2AccessToken": self._op_get_oauth2_access_token,
            "getCurrentUser": self._op_get_current_user,
            "getUser": self._op_get_user,
            "updateUser": self._op_update_user,
            "getFriends": self._op_get_friends,
            "getGroups": self._op_get_groups,
            "getGroup": self._op_get_group,
            "createGroup": self._op_create_group,
            "deleteGroup": self._op_delete_group,
            "addUserToGroup": self._op_add_user_to_group,
            "getExpenses": self._op_get_expenses,
            "getExpense": self._op_get_expense,
            "createExpense": self._op_create_expense,
            "updateExpense": self._op_update_expense,
            "deleteExpense": self._op_delete_expense,
            "getCurrencies": self._op_get_currencies,
            "getCategories": self._op_get_categories,
            "getComments": self._op_get_comments,
            "createComment": self._op_create_comment,
            "getNotifications": self._op_get_notifications,
        }
        return handlers[operation](client, payload, session)

    def _op_get_authorize_url(self, client, payload, session):
        authorize_url, oauth_token_secret = client.getAuthorizeURL()
        session["oauth_token_secret"] = oauth_token_secret
        return {"authorize_url": authorize_url, "oauth_token_secret": oauth_token_secret}

    def _op_get_access_token(self, client, payload, session):
        oauth_token_secret = payload.get("oauth_token_secret") or session.get("oauth_token_secret")
        if not oauth_token_secret:
            raise ValueError("oauth_token_secret is required before exchanging an OAuth 1 verifier")
        access_token = client.getAccessToken(payload["oauth_token"], oauth_token_secret, payload["oauth_verifier"])
        session["access_token"] = access_token
        return access_token

    def _op_get_oauth2_authorize_url(self, client, payload, session):
        authorize_url, state = client.getOAuth2AuthorizeURL(payload["redirect_uri"], payload.get("state"))
        session["oauth2_state"] = state
        return {"authorize_url": authorize_url, "state": state}

    def _op_get_oauth2_access_token(self, client, payload, session):
        access_token = client.getOAuth2AccessToken(payload["code"], payload["redirect_uri"])
        session["oauth2_access_token"] = access_token
        return access_token

    def _op_get_current_user(self, client, payload, session):
        return self._serialize(client.getCurrentUser())

    def _op_get_user(self, client, payload, session):
        return self._serialize(client.getUser(payload["id"]))

    def _op_update_user(self, client, payload, session):
        user, errors = client.updateUser(self._build_user(payload.get("user", {})))
        return {"user": self._serialize(user), "errors": self._serialize(errors)}

    def _op_get_friends(self, client, payload, session):
        return self._serialize(client.getFriends())

    def _op_get_groups(self, client, payload, session):
        return self._serialize(client.getGroups())

    def _op_get_group(self, client, payload, session):
        return self._serialize(client.getGroup(payload.get("id", 0)))

    def _op_create_group(self, client, payload, session):
        group, errors = client.createGroup(self._build_group(payload.get("group", {})))
        return {"group": self._serialize(group), "errors": self._serialize(errors)}

    def _op_delete_group(self, client, payload, session):
        success, errors = client.deleteGroup(payload["id"])
        return {"success": success, "errors": self._serialize(errors)}

    def _op_add_user_to_group(self, client, payload, session):
        success, user, errors = client.addUserToGroup(self._build_user(payload.get("user", {})), payload["group_id"])
        return {"success": success, "user": self._serialize(user), "errors": self._serialize(errors)}

    def _op_get_expenses(self, client, payload, session):
        filters = dict(payload)
        if "visible" in filters:
            filters["visible"] = bool(filters["visible"])
        return self._serialize(client.getExpenses(**filters))

    def _op_get_expense(self, client, payload, session):
        return self._serialize(client.getExpense(payload["id"]))

    def _op_create_expense(self, client, payload, session):
        expense, errors = client.createExpense(self._build_expense(payload.get("expense", {})))
        return {"expense": self._serialize(expense), "errors": self._serialize(errors)}

    def _op_update_expense(self, client, payload, session):
        expense, errors = client.updateExpense(self._build_expense(payload.get("expense", {})))
        return {"expense": self._serialize(expense), "errors": self._serialize(errors)}

    def _op_delete_expense(self, client, payload, session):
        success, errors = client.deleteExpense(payload["id"])
        return {"success": success, "errors": self._serialize(errors)}

    def _op_get_currencies(self, client, payload, session):
        return self._serialize(client.getCurrencies())

    def _op_get_categories(self, client, payload, session):
        return self._serialize(client.getCategories())

    def _op_get_comments(self, client, payload, session):
        return self._serialize(client.getComments(payload["expense_id"]))

    def _op_create_comment(self, client, payload, session):
        comment, errors = client.createComment(payload["expense_id"], payload["content"])
        return {"comment": self._serialize(comment), "errors": self._serialize(errors)}

    def _op_get_notifications(self, client, payload, session):
        return self._serialize(client.getNotifications(payload.get("updated_since"), payload.get("limit")))

    def _build_client(self, session):
        consumer_key = session.get("consumer_key") or self.environment.get("SPLITWISE_CONSUMER_KEY")
        consumer_secret = session.get("consumer_secret") or self.environment.get("SPLITWISE_CONSUMER_SECRET")
        if not consumer_key or not consumer_secret:
            raise ValueError("consumer_key and consumer_secret are required in session or environment")
        base_url = self.environment.get("SPLITWISE_BACKEND_BASE_URL")
        oauth_base_url = self.environment.get("SPLITWISE_BACKEND_OAUTH_BASE_URL")
        kwargs = dict(
            access_token=session.get("access_token"),
            oauth2_access_token=session.get("oauth2_access_token"),
            api_key=session.get("api_key"),
        )
        if base_url:
            kwargs["base_url"] = base_url
        if oauth_base_url:
            kwargs["oauth_base_url"] = oauth_base_url
        try:
            return self.splitwise_factory(
                consumer_key,
                consumer_secret,
                **kwargs
            )
        except TypeError:
            # Preserve compatibility with injected SDK doubles or older Splitwise
            # constructors that do not accept backend override kwargs.
            kwargs.pop("base_url", None)
            kwargs.pop("oauth_base_url", None)
            return self.splitwise_factory(
                consumer_key,
                consumer_secret,
                **kwargs
            )

    def _has_client_credentials(self, session):
        return bool(
            session.get("consumer_key") or self.environment.get("SPLITWISE_CONSUMER_KEY")
        ) and bool(
            session.get("consumer_secret") or self.environment.get("SPLITWISE_CONSUMER_SECRET")
        )

    def _merge_session(self, session, payload):
        allowed = {"consumer_key", "consumer_secret", "api_key", "access_token", "oauth2_access_token"}
        for key in allowed:
            if key in payload:
                if payload[key] in (None, ""):
                    session.pop(key, None)
                else:
                    session[key] = payload[key]

    def _build_user(self, payload):
        user = User()
        if "id" in payload:
            user.setId(payload["id"])
        if "first_name" in payload:
            user.setFirstName(payload["first_name"])
        if "last_name" in payload:
            user.setLastName(payload["last_name"])
        if "email" in payload:
            user.setEmail(payload["email"])
        return user

    def _build_group(self, payload):
        group = Group()
        if "name" in payload:
            group.setName(payload["name"])
        if "group_type" in payload:
            group.setGroupType(payload["group_type"])
        if "whiteboard" in payload:
            group.setWhiteBoard(payload["whiteboard"])
        if "country_code" in payload:
            group.setCountryCode(payload["country_code"])
        if "members" in payload:
            members = [self._build_user(member) for member in payload["members"]]
            group.setMembers(members)
        return group

    def _build_expense(self, payload):
        expense = Expense()
        field_setters = {
            "id": expense.setId,
            "group_id": expense.setGroupId,
            "description": expense.setDescription,
            "cost": expense.setCost,
            "payment": expense.setPayment,
            "friendship_id": expense.setFriendshipId,
            "date": expense.setDate,
            "currency_code": expense.setCurrencyCode,
            "details": expense.setDetails,
            "receipt_path": expense.setReceipt,
        }
        for key, setter in field_setters.items():
            if key in payload:
                setter(payload[key])
        if "split_equally" in payload:
            expense.setSplitEqually(payload["split_equally"])
        if "category_id" in payload:
            category = Category()
            category.setId(payload["category_id"])
            expense.setCategory(category)
        if "users" in payload:
            users = []
            for user_payload in payload["users"]:
                user = ExpenseUser()
                if "id" in user_payload:
                    user.setId(user_payload["id"])
                if "paid_share" in user_payload:
                    user.setPaidShare(user_payload["paid_share"])
                if "owed_share" in user_payload:
                    user.setOwedShare(user_payload["owed_share"])
                users.append(user)
            expense.setUsers(users)
        return expense

    def _serialize(self, value):
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return {key: self._serialize(val) for key, val in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._serialize(item) for item in value]
        if hasattr(value, "__dict__"):
            return {key: self._serialize(val) for key, val in value.__dict__.items()}
        return value

    def _read_json(self, environ):
        body_length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(body_length) if body_length else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _get_session(self, environ):
        cookie_header = environ.get("HTTP_COOKIE", "")
        jar = cookies.SimpleCookie()
        jar.load(cookie_header)
        current = jar.get("splitwise_pwa")
        if current and current.value in self.sessions:
            return current.value, self.sessions[current.value], None
        session_id = secrets.token_urlsafe(24)
        self.sessions[session_id] = {}
        cookie = cookies.SimpleCookie()
        cookie["splitwise_pwa"] = session_id
        cookie["splitwise_pwa"]["httponly"] = True
        cookie["splitwise_pwa"]["path"] = "/"
        cookie["splitwise_pwa"]["samesite"] = "Lax"
        return session_id, self.sessions[session_id], cookie.output(header="").strip()

    def _session_summary(self, session):
        return {
            "consumer_key": bool(session.get("consumer_key") or self.environment.get("SPLITWISE_CONSUMER_KEY")),
            "consumer_secret": bool(session.get("consumer_secret") or self.environment.get("SPLITWISE_CONSUMER_SECRET")),
            "api_key": bool(session.get("api_key")),
            "access_token": bool(session.get("access_token")),
            "oauth2_access_token": bool(session.get("oauth2_access_token")),
        }

    def _respond(self, start_response, status, body, headers, content_type):
        payload = body.encode("utf-8") if isinstance(body, str) else body
        response_headers = list(headers) + [("Content-Type", content_type), ("Content-Length", str(len(payload)))]
        start_response(status, response_headers)
        return [payload]

    def _respond_json(self, start_response, status, payload, headers):
        return self._respond(start_response, status, json.dumps(payload), headers, "application/json; charset=utf-8")


def create_app(splitwise_factory=Splitwise, environment=None):
    return SplitwisePWAApp(splitwise_factory=splitwise_factory, environment=environment)


def main():
    host = os.environ.get("SPLITWISE_PWA_HOST", "127.0.0.1")
    port = int(os.environ.get("SPLITWISE_PWA_PORT", "8765"))
    app = create_app()
    with make_server(host, port, app) as server:
        print("Splitwise PWA listening on http://%s:%s" % (host, port))
        server.serve_forever()


if __name__ == "__main__":
    main()
