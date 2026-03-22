import json
import os
import secrets
from http import cookies
from wsgiref.simple_server import make_server

from splitwise import Splitwise
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

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/") or "/"
        method = environ.get("REQUEST_METHOD", "GET").upper()
        session_id, session, session_cookie = self._get_session(environ)
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

        try:
            if method == "GET" and path in STATIC_ROUTES:
                content_type, body = STATIC_ROUTES[path]
                return self._respond(start_response, "200 OK", body, headers, content_type)

            if method == "GET" and path == "/api/config":
                payload = {
                    "configured": self._has_client_credentials(session),
                    "sdk_methods": SDK_METHODS,
                    "session": self._session_summary(session),
                    "session_id": session_id,
                }
                return self._respond_json(start_response, "200 OK", payload, headers)

            if method == "POST" and path == "/api/session":
                payload = self._read_json(environ)
                self._merge_session(session, payload)
                return self._respond_json(
                    start_response,
                    "200 OK",
                    {"ok": True, "session": self._session_summary(session)},
                    headers,
                )

            if method == "POST" and path == "/api/session/clear":
                session.clear()
                return self._respond_json(start_response, "200 OK", {"ok": True}, headers)

            if method == "POST" and path.startswith("/api/operations/"):
                operation = path.rsplit("/", 1)[-1]
                if operation not in SDK_METHODS:
                    return self._respond_json(start_response, "404 Not Found", {"error": "Unknown operation"}, headers)
                payload = self._read_json(environ)
                result = self._dispatch_operation(operation, payload, session)
                return self._respond_json(
                    start_response,
                    "200 OK",
                    {"ok": True, "operation": operation, "data": result},
                    headers,
                )

            return self._respond_json(start_response, "404 Not Found", {"error": "Route not found"}, headers)
        except ValueError as exc:
            return self._respond_json(start_response, "400 Bad Request", {"error": str(exc)}, headers)
        except SplitwiseException as exc:
            status = ERROR_STATUS.get(type(exc), "500 Internal Server Error")
            return self._respond_json(start_response, status, {"error": str(exc)}, headers)
        except Exception as exc:  # pragma: no cover - protective fallback
            return self._respond_json(start_response, "500 Internal Server Error", {"error": str(exc)}, headers)

    def _dispatch_operation(self, operation, payload, session):
        client = self._build_client(session)

        if operation == "getAuthorizeURL":
            authorize_url, oauth_token_secret = client.getAuthorizeURL()
            session["oauth_token_secret"] = oauth_token_secret
            return {"authorize_url": authorize_url, "oauth_token_secret": oauth_token_secret}

        if operation == "getAccessToken":
            oauth_token_secret = payload.get("oauth_token_secret") or session.get("oauth_token_secret")
            if not oauth_token_secret:
                raise ValueError("oauth_token_secret is required before exchanging an OAuth 1 verifier")
            access_token = client.getAccessToken(payload["oauth_token"], oauth_token_secret, payload["oauth_verifier"])
            session["access_token"] = access_token
            return access_token

        if operation == "getOAuth2AuthorizeURL":
            authorize_url, state = client.getOAuth2AuthorizeURL(payload["redirect_uri"], payload.get("state"))
            session["oauth2_state"] = state
            return {"authorize_url": authorize_url, "state": state}

        if operation == "getOAuth2AccessToken":
            access_token = client.getOAuth2AccessToken(payload["code"], payload["redirect_uri"])
            session["oauth2_access_token"] = access_token
            return access_token

        if operation == "getCurrentUser":
            return self._serialize(client.getCurrentUser())

        if operation == "getUser":
            return self._serialize(client.getUser(payload["id"]))

        if operation == "updateUser":
            user, errors = client.updateUser(self._build_user(payload.get("user", {})))
            return {"user": self._serialize(user), "errors": self._serialize(errors)}

        if operation == "getFriends":
            return self._serialize(client.getFriends())

        if operation == "getGroups":
            return self._serialize(client.getGroups())

        if operation == "getGroup":
            return self._serialize(client.getGroup(payload.get("id", 0)))

        if operation == "createGroup":
            group, errors = client.createGroup(self._build_group(payload.get("group", {})))
            return {"group": self._serialize(group), "errors": self._serialize(errors)}

        if operation == "deleteGroup":
            success, errors = client.deleteGroup(payload["id"])
            return {"success": success, "errors": self._serialize(errors)}

        if operation == "addUserToGroup":
            success, user, errors = client.addUserToGroup(self._build_user(payload.get("user", {})), payload["group_id"])
            return {"success": success, "user": self._serialize(user), "errors": self._serialize(errors)}

        if operation == "getExpenses":
            filters = dict(payload)
            if "visible" in filters:
                filters["visible"] = bool(filters["visible"])
            return self._serialize(client.getExpenses(**filters))

        if operation == "getExpense":
            return self._serialize(client.getExpense(payload["id"]))

        if operation == "createExpense":
            expense, errors = client.createExpense(self._build_expense(payload.get("expense", {})))
            return {"expense": self._serialize(expense), "errors": self._serialize(errors)}

        if operation == "updateExpense":
            expense, errors = client.updateExpense(self._build_expense(payload.get("expense", {})))
            return {"expense": self._serialize(expense), "errors": self._serialize(errors)}

        if operation == "deleteExpense":
            success, errors = client.deleteExpense(payload["id"])
            return {"success": success, "errors": self._serialize(errors)}

        if operation == "getCurrencies":
            return self._serialize(client.getCurrencies())

        if operation == "getCategories":
            return self._serialize(client.getCategories())

        if operation == "getComments":
            return self._serialize(client.getComments(payload["expense_id"]))

        if operation == "createComment":
            comment, errors = client.createComment(payload["expense_id"], payload["content"])
            return {"comment": self._serialize(comment), "errors": self._serialize(errors)}

        if operation == "getNotifications":
            return self._serialize(client.getNotifications(payload.get("updated_since"), payload.get("limit")))

        raise ValueError("Unsupported operation")

    def _build_client(self, session):
        consumer_key = session.get("consumer_key") or self.environment.get("SPLITWISE_CONSUMER_KEY")
        consumer_secret = session.get("consumer_secret") or self.environment.get("SPLITWISE_CONSUMER_SECRET")
        if not consumer_key or not consumer_secret:
            raise ValueError("consumer_key and consumer_secret are required in session or environment")
        return self.splitwise_factory(
            consumer_key,
            consumer_secret,
            access_token=session.get("access_token"),
            oauth2_access_token=session.get("oauth2_access_token"),
            api_key=session.get("api_key"),
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
