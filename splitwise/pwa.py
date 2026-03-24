import io
import json
import os
import secrets
import hashlib
from http import cookies
from urllib.parse import urlencode
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

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
from splitwise.persistence import DEFAULT_PERSISTENCE_DIR, PersistenceStore
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


class LocalSplitwiseAdapter(object):
    def __init__(self, backend_app, current_user_id, origin):
        self.backend_app = backend_app
        self.current_user_id = current_user_id
        self.origin = origin if origin.endswith("/") else origin + "/"

    def getAuthorizeURL(self):
        content = self._request("POST", "/api/v3.0/get_request_token")
        credentials = self._parse_form_payload(content)
        return "%sauthorize?oauth_token=%s" % (self.origin, credentials["oauth_token"]), credentials["oauth_token_secret"]

    def getAccessToken(self, oauth_token, oauth_token_secret, oauth_verifier):
        del oauth_token, oauth_token_secret, oauth_verifier
        content = self._request("POST", "/api/v3.0/get_access_token")
        credentials = self._parse_form_payload(content)
        return credentials

    def getOAuth2AuthorizeURL(self, redirect_uri, state=None):
        state = state or secrets.token_urlsafe(12)
        query = urlencode({"client_id": "local-demo", "redirect_uri": redirect_uri, "state": state})
        return "%soauth/authorize?%s" % (self.origin, query), state

    def getOAuth2AccessToken(self, code, redirect_uri):
        return self._request("POST", "/oauth/token", {"code": code, "redirect_uri": redirect_uri})

    def getCurrentUser(self):
        return self._request("GET", "/api/v3.0/get_current_user")["user"]

    def getUser(self, id):
        return self._request("GET", "/api/v3.0/get_user/%s" % id)["user"]

    def updateUser(self, user):
        payload = self._request("POST", "/api/v3.0/update_user", self._user_payload(user))
        return payload["user"], payload.get("errors") or None

    def getFriends(self):
        return self._request("GET", "/api/v3.0/get_friends")["friends"]

    def getGroups(self):
        return self._request("GET", "/api/v3.0/get_groups")["groups"]

    def getGroup(self, id=0):
        return self._request("GET", "/api/v3.0/get_group/%s" % id)["group"]

    def createGroup(self, group):
        payload = self._request("POST", "/api/v3.0/create_group", self._group_payload(group))
        return payload["group"], payload.get("errors") or None

    def deleteGroup(self, id):
        payload = self._request("POST", "/api/v3.0/delete_group/%s" % id)
        return payload["success"], payload.get("errors") or None

    def addUserToGroup(self, user, group_id):
        payload = self._request(
            "POST",
            "/api/v3.0/add_user_to_group",
            dict(self._user_payload(user), group_id=group_id),
        )
        return payload["success"], payload["user"], payload.get("errors") or None

    def getExpenses(self, **filters):
        query = urlencode(filters)
        path = "/api/v3.0/get_expenses"
        if query:
            path += "?" + query
        return self._request("GET", path)["expenses"]

    def getExpense(self, id):
        return self._request("GET", "/api/v3.0/get_expense/%s" % id)["expense"]

    def createExpense(self, expense):
        payload = self._request("POST", "/api/v3.0/create_expense", self._expense_payload(expense))
        return payload["expenses"][0], payload.get("errors") or None

    def updateExpense(self, expense):
        payload = self._request(
            "POST",
            "/api/v3.0/update_expense/%s" % expense.id,
            self._expense_payload(expense),
        )
        return payload["expenses"][0], payload.get("errors") or None

    def deleteExpense(self, id):
        payload = self._request("POST", "/api/v3.0/delete_expense/%s" % id)
        return payload["success"], payload.get("errors") or None

    def getCurrencies(self):
        return self._request("GET", "/api/v3.0/get_currencies")["currencies"]

    def getCategories(self):
        return self._request("GET", "/api/v3.0/get_categories")["categories"]

    def getComments(self, expense_id):
        return self._request("GET", "/api/v3.0/get_comments?expense_id=%s" % expense_id)["comments"]

    def createComment(self, expense_id, content):
        payload = self._request("POST", "/api/v3.0/create_comment", {"expense_id": expense_id, "content": content})
        return payload["comment"], payload.get("errors") or None

    def getNotifications(self, updated_since=None, limit=None):
        query = {}
        if updated_since is not None:
            query["updated_since"] = updated_since
        if limit is not None:
            query["limit"] = limit
        path = "/api/v3.0/get_notifications"
        if query:
            path += "?" + urlencode(query)
        return self._request("GET", path)["notifications"]

    def _request(self, method, path, payload=None):
        body = b""
        if payload is not None and method == "POST":
            body = json.dumps(payload).encode("utf-8")
        environ = {}
        setup_testing_defaults(environ)
        environ["REQUEST_METHOD"] = method
        environ["PATH_INFO"] = path
        environ["QUERY_STRING"] = ""
        if "?" in path:
            environ["PATH_INFO"], environ["QUERY_STRING"] = path.split("?", 1)
        environ["CONTENT_LENGTH"] = str(len(body))
        environ["CONTENT_TYPE"] = "application/json"
        environ["wsgi.input"] = io.BytesIO(body)
        environ["HTTP_X_SPLITWISE_USER_ID"] = str(self.current_user_id)

        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        raw = b"".join(self.backend_app(environ, start_response))
        content_type = captured["headers"].get("Content-Type", "")
        decoded = raw.decode("utf-8")
        if "application/json" in content_type:
            parsed = json.loads(decoded)
            if not captured["status"].startswith("200"):
                raise ValueError(parsed.get("error") or parsed.get("errors", {}).get("base", ["Request failed"])[0])
            return parsed
        if not captured["status"].startswith("200"):
            raise ValueError(decoded or "Request failed")
        return decoded

    def _parse_form_payload(self, content):
        values = {}
        for part in content.split("&"):
            key, raw_value = part.split("=", 1)
            values[key] = raw_value
        return values

    def _user_payload(self, user):
        payload = {}
        if getattr(user, "id", None) is not None:
            payload["id"] = user.id
        if getattr(user, "first_name", None) is not None:
            payload["first_name"] = user.first_name
        if getattr(user, "last_name", None) is not None:
            payload["last_name"] = user.last_name
        if getattr(user, "email", None) is not None:
            payload["email"] = user.email
        return payload

    def _group_payload(self, group):
        payload = {}
        if getattr(group, "name", None) is not None:
            payload["name"] = group.name
        if getattr(group, "group_type", None) is not None:
            payload["group_type"] = group.group_type
        if getattr(group, "whiteboard", None) is not None:
            payload["whiteboard"] = group.whiteboard
        if getattr(group, "country_code", None) is not None:
            payload["country_code"] = group.country_code
        members = []
        for member in getattr(group, "members", []) or []:
            members.append(self._user_payload(member))
        for index, member in enumerate(members):
            for key, value in member.items():
                payload["users__%s__%s" % (index, key)] = value
        return payload

    def _expense_payload(self, expense):
        payload = {}
        for field in ("id", "group_id", "description", "cost", "payment", "friendship_id", "date", "currency_code", "details"):
            value = getattr(expense, field, None)
            if value is not None:
                payload[field] = value
        for field in ("repeats", "repeat_interval", "email_reminder", "email_reminder_in_advance", "next_repeat"):
            value = getattr(expense, field, None)
            if value is not None:
                payload[field] = value
        if getattr(expense, "category", None) is not None and getattr(expense.category, "id", None) is not None:
            payload["category_id"] = expense.category.id
        if getattr(expense, "split_equally", None) is not None:
            payload["split_equally"] = expense.split_equally
        if getattr(expense, "split_method", None) is not None:
            payload["split_method"] = expense.split_method
        users = []
        for user in getattr(expense, "users", []) or []:
            user_payload = {}
            if getattr(user, "id", None) is not None:
                user_payload["user_id"] = user.id
            if getattr(user, "paid_share", None) is not None:
                user_payload["paid_share"] = user.paid_share
            if getattr(user, "owed_share", None) is not None:
                user_payload["owed_share"] = user.owed_share
            users.append(user_payload)
        for index, user in enumerate(users):
            for key, value in user.items():
                payload["users__%s__%s" % (index, key)] = value
        for collection_name in ("payers", "participants"):
            items = []
            for item in getattr(expense, collection_name, []) or []:
                if isinstance(item, dict):
                    items.append(item)
                elif hasattr(item, "__dict__"):
                    items.append(item.__dict__)
            for index, item in enumerate(items):
                for key, value in item.items():
                    if key == "id":
                        key = "user_id"
                    payload["%s__%s__%s" % (collection_name, index, key)] = value
        return payload


class SplitwisePWAApp(object):
    def __init__(self, splitwise_factory=Splitwise, environment=None):
        self.splitwise_factory = splitwise_factory
        self.environment = environment or os.environ
        self.persistence = self._build_persistence_store()
        self.sessions = self.persistence.load_sessions() if self.persistence else {}
        self.backend_app = create_backend_app(persistence=self.persistence)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/") or "/"
        method = environ.get("REQUEST_METHOD", "GET").upper()
        session_id, session, session_cookie = self._get_session(environ)
        previous_session_fingerprint = None
        if self._session_can_change(method, path):
            previous_session_fingerprint = self._session_fingerprint(session)
        headers = self._default_headers(session_cookie)

        try:
            status, payload, content_type = self._route_request(method, path, environ, session, session_id)
            self._persist_sessions_if_changed(session, previous_session_fingerprint)
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

    def _build_persistence_store(self):
        if self.environment.get("KV_REST_API_URL") and self.environment.get("KV_REST_API_TOKEN"):
            return PersistenceStore(environment=self.environment)
        if self.environment.get("SPLITWISE_PERSISTENCE_DIR"):
            return PersistenceStore(environment=self.environment)
        if self.environment.get("VERCEL"):
            persisted_environment = dict(self.environment)
            persisted_environment.setdefault("SPLITWISE_PERSISTENCE_DIR", DEFAULT_PERSISTENCE_DIR)
            return PersistenceStore(environment=persisted_environment)
        return None

    def _persist_sessions(self):
        if self.persistence:
            self.persistence.save_sessions(self.sessions)

    def _persist_sessions_if_changed(self, session, previous_session_fingerprint):
        if not self.persistence or previous_session_fingerprint is None:
            return
        if self._session_fingerprint(session) != previous_session_fingerprint:
            self._persist_sessions()

    def _session_fingerprint(self, session):
        serialized = json.dumps(self._serialize(session), sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def _session_can_change(self, method, path):
        if method != "POST":
            return False
        if path == "/api/session":
            return True
        if path.startswith("/api/local/"):
            return True
        # Keep this list in sync with the operation handlers that write OAuth data into the session.
        if path.startswith("/api/operations/") and path.rsplit("/", 1)[-1] in (
            "getAuthorizeURL",
            "getAccessToken",
            "getOAuth2AuthorizeURL",
            "getOAuth2AccessToken",
        ):
            return True
        return False

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
            return self._delegate_to_backend(environ, session)
        if method == "GET":
            return self._handle_get(path, session, session_id)
        if method == "POST":
            return self._handle_post(path, environ, session)
        return "404 Not Found", {"error": "Route not found"}, "json"

    def _delegate_to_backend(self, environ, session):
        captured = {}
        delegated_environ = dict(environ)
        if session.get("local_user_id") and "HTTP_X_SPLITWISE_USER_ID" not in delegated_environ:
            delegated_environ["HTTP_X_SPLITWISE_USER_ID"] = str(session["local_user_id"])

        def start_response(status, response_headers):
            captured["status"] = status
            captured["headers"] = response_headers

        body = b"".join(self.backend_app(delegated_environ, start_response))
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
                "authenticated": bool(session.get("local_user_id")),
                "local_user": self._serialize(self._local_user(session)),
            }, "json"

        return "404 Not Found", {"error": "Route not found"}, "json"

    def _handle_post(self, path, environ, session):
        payload = self._read_json(environ)
        if path == "/api/local/register":
            return "200 OK", self._handle_local_register(payload, session), "json"

        if path == "/api/local/login":
            return "200 OK", self._handle_local_login(payload, session), "json"

        if path == "/api/local/logout":
            return "200 OK", self._handle_local_logout(session), "json"

        if path == "/api/local/friends":
            return "200 OK", self._handle_local_add_friend(payload, session), "json"

        if path == "/api/local/friend-requests":
            return "200 OK", self._handle_local_send_friend_request(payload, session), "json"

        if path == "/api/local/friend-requests/list":
            return "200 OK", self._handle_local_list_friend_requests(session), "json"

        if path == "/api/local/friend-requests/respond":
            return "200 OK", self._handle_local_respond_friend_request(payload, session), "json"

        if path == "/api/local/profile":
            return "200 OK", self._handle_local_profile_update(payload, session), "json"

        if path == "/api/local/password":
            return "200 OK", self._handle_local_password_update(payload, session), "json"

        if path == "/api/local/groups/update":
            return "200 OK", self._handle_local_group_update(payload, session), "json"

        if path == "/api/local/groups/members/add":
            return "200 OK", self._handle_local_group_member_add(payload, session), "json"

        if path == "/api/local/groups/members/remove":
            return "200 OK", self._handle_local_group_member_remove(payload, session), "json"

        if path == "/api/local/groups/leave":
            return "200 OK", self._handle_local_group_leave(payload, session), "json"

        if path == "/api/local/groups/archive":
            return "200 OK", self._handle_local_group_archive(payload, session), "json"

        if path == "/api/local/groups/admin":
            return "200 OK", self._handle_local_group_admin(payload, session), "json"

        if path == "/api/local/settlements":
            return "200 OK", self._handle_local_settlement(payload, session), "json"

        if path == "/api/local/expense-series/update":
            return "200 OK", self._handle_local_expense_series_update(payload, session), "json"

        if path == "/api/local/expense-series/pause":
            return "200 OK", self._handle_local_expense_series_pause(payload, session), "json"

        if path == "/api/local/expense-series/resume":
            return "200 OK", self._handle_local_expense_series_resume(payload, session), "json"

        if path == "/api/local/expense-series/cancel":
            return "200 OK", self._handle_local_expense_series_cancel(payload, session), "json"

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
                "data": self._dispatch_operation(operation, payload, session, environ),
            }, "json"

        return "404 Not Found", {"error": "Route not found"}, "json"

    def _dispatch_operation(self, operation, payload, session, environ):
        client = self._build_client(session, environ)
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

    def _build_client(self, session, environ):
        if session.get("local_user_id"):
            return LocalSplitwiseAdapter(
                self.backend_app,
                session["local_user_id"],
                self._request_origin(environ),
            )
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
        if session.get("local_user_id"):
            return True
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
        if "split_method" in payload:
            expense.split_method = payload["split_method"]
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
        if "payers" in payload:
            expense.payers = [
                {
                    "user_id": payer.get("user_id", payer.get("id")),
                    "paid_share": payer.get("paid_share", payer.get("payer_amount")),
                }
                for payer in payload["payers"]
            ]
        if "participants" in payload:
            expense.participants = [
                {
                    "user_id": participant.get("user_id", participant.get("id")),
                    "included": participant.get("included"),
                    "split_value": participant.get("split_value"),
                }
                for participant in payload["participants"]
            ]
        for field in ("repeats", "repeat_interval", "email_reminder", "email_reminder_in_advance", "next_repeat"):
            if field in payload:
                setattr(expense, field, payload[field])
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
            "local_account": bool(session.get("local_user_id")),
            "consumer_key": bool(session.get("consumer_key") or self.environment.get("SPLITWISE_CONSUMER_KEY")),
            "consumer_secret": bool(session.get("consumer_secret") or self.environment.get("SPLITWISE_CONSUMER_SECRET")),
            "api_key": bool(session.get("api_key")),
            "access_token": bool(session.get("access_token")),
            "oauth2_access_token": bool(session.get("oauth2_access_token")),
        }

    def _handle_local_register(self, payload, session):
        user = self.backend_app.register_account(
            payload.get("first_name"),
            payload.get("email"),
            payload.get("password"),
            last_name=payload.get("last_name"),
        )
        session["local_user_id"] = user["id"]
        return {"ok": True, "user": user}

    def _handle_local_login(self, payload, session):
        user = self.backend_app.authenticate_account(payload.get("email"), payload.get("password"))
        session["local_user_id"] = user["id"]
        return {"ok": True, "user": user}

    def _handle_local_logout(self, session):
        session.pop("local_user_id", None)
        return {"ok": True}

    def _handle_local_add_friend(self, payload, session):
        user_id = self._require_local_user_id(session)
        friend = self.backend_app.add_friend(user_id, email=payload.get("email"), user_id=payload.get("user_id"))
        return {"ok": True, "friend": friend}

    def _handle_local_send_friend_request(self, payload, session):
        user_id = self._require_local_user_id(session)
        request_payload = self.backend_app.send_friend_request(user_id, email=payload.get("email"), user_id=payload.get("user_id"))
        return {"ok": True, "request": request_payload}

    def _handle_local_list_friend_requests(self, session):
        user_id = self._require_local_user_id(session)
        return {"ok": True, "requests": self.backend_app.list_friend_requests(user_id)}

    def _handle_local_respond_friend_request(self, payload, session):
        user_id = self._require_local_user_id(session)
        result = self.backend_app.respond_friend_request(user_id, payload.get("request_id"), accept=bool(payload.get("accept", True)))
        return {"ok": True, "result": result}

    def _handle_local_profile_update(self, payload, session):
        user_id = self._require_local_user_id(session)
        user = self.backend_app.update_account(
            user_id,
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            email=payload.get("email"),
        )
        return {"ok": True, "user": user}

    def _handle_local_password_update(self, payload, session):
        user_id = self._require_local_user_id(session)
        result = self.backend_app.update_password(user_id, payload.get("current_password"), payload.get("new_password"))
        return {"ok": True, "result": result}

    def _handle_local_group_update(self, payload, session):
        user_id = self._require_local_user_id(session)
        group = self.backend_app.update_group(
            user_id,
            payload.get("group_id"),
            name=payload.get("name"),
            whiteboard=payload.get("whiteboard"),
        )
        return {"ok": True, "group": group}

    def _handle_local_group_member_add(self, payload, session):
        user_id = self._require_local_user_id(session)
        group = self.backend_app.add_group_member(user_id, payload.get("group_id"), payload.get("user_id"))
        return {"ok": True, "group": group}

    def _handle_local_group_member_remove(self, payload, session):
        user_id = self._require_local_user_id(session)
        group = self.backend_app.remove_group_member(user_id, payload.get("group_id"), payload.get("user_id"))
        return {"ok": True, "group": group}

    def _handle_local_group_leave(self, payload, session):
        user_id = self._require_local_user_id(session)
        result = self.backend_app.leave_group(user_id, payload.get("group_id"))
        return {"ok": True, "result": result}

    def _handle_local_group_archive(self, payload, session):
        user_id = self._require_local_user_id(session)
        group = self.backend_app.set_group_archived(user_id, payload.get("group_id"), payload.get("archived"))
        return {"ok": True, "group": group}

    def _handle_local_group_admin(self, payload, session):
        user_id = self._require_local_user_id(session)
        group = self.backend_app.set_group_admin(user_id, payload.get("group_id"), payload.get("user_id"), bool(payload.get("is_admin")))
        return {"ok": True, "group": group}

    def _handle_local_settlement(self, payload, session):
        user_id = self._require_local_user_id(session)
        settlement = self.backend_app.record_settlement(
            user_id,
            payload.get("other_user_id"),
            payload.get("amount"),
            group_id=payload.get("group_id"),
            note=payload.get("note"),
            date=payload.get("date"),
            from_user_id=payload.get("from_user_id"),
            to_user_id=payload.get("to_user_id"),
        )
        return {"ok": True, "settlement": settlement}

    def _handle_local_expense_series_update(self, payload, session):
        user_id = self._require_local_user_id(session)
        expense = payload.get("expense", {})
        series_id = payload.get("series_id") or expense.get("series_id")
        adapter = LocalSplitwiseAdapter(self.backend_app, user_id, "http://local/")
        updated = self.backend_app.update_expense_series(
            user_id,
            series_id,
            adapter._expense_payload(self._build_expense(expense)),
        )
        return {"ok": True, "expense": updated}

    def _handle_local_expense_series_pause(self, payload, session):
        user_id = self._require_local_user_id(session)
        expense = self.backend_app.pause_expense_series(user_id, payload.get("series_id"))
        return {"ok": True, "expense": expense}

    def _handle_local_expense_series_resume(self, payload, session):
        user_id = self._require_local_user_id(session)
        expense = self.backend_app.resume_expense_series(user_id, payload.get("series_id"))
        return {"ok": True, "expense": expense}

    def _handle_local_expense_series_cancel(self, payload, session):
        user_id = self._require_local_user_id(session)
        expense = self.backend_app.cancel_expense_series(user_id, payload.get("series_id"))
        return {"ok": True, "expense": expense}

    def _require_local_user_id(self, session):
        user_id = session.get("local_user_id")
        if not user_id:
            raise ValueError("Sign in to a local account first")
        return user_id

    def _local_user(self, session):
        user_id = session.get("local_user_id")
        if not user_id:
            return None
        return self.backend_app.state["users"].get(user_id)

    def _request_origin(self, environ):
        scheme = environ.get("wsgi.url_scheme", "http")
        host = environ.get("HTTP_HOST") or environ.get("SERVER_NAME") or "127.0.0.1"
        return "%s://%s/" % (scheme, host)

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
