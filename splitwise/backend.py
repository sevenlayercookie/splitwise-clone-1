import json
import logging
import secrets
import hashlib
import hmac
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from email.parser import BytesParser
from email.policy import default
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

LOGGER = logging.getLogger(__name__)


class SplitwiseBackendApp(object):
    def __init__(self, initial_state=None):
        self.state = initial_state or _default_state()

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/") or "/"
        current_user_id = self._resolve_current_user_id(environ)
        try:
            status, payload, content_type = self._route(method, path, environ, current_user_id)
            return self._respond(start_response, status, payload, content_type)
        except ValueError as exc:
            return self._respond_json(start_response, "400 Bad Request", {"errors": {"base": [str(exc)]}})
        except KeyError:
            return self._respond_json(start_response, "404 Not Found", {"errors": {"base": ["Resource not found"]}})
        except Exception as exc:  # pragma: no cover - protective fallback
            LOGGER.exception("Unhandled backend error: %s", exc)
            return self._respond_json(start_response, "500 Internal Server Error", {"errors": {"base": ["Internal server error"]}})

    def _route(self, method, path, environ, current_user_id):
        if method == "OPTIONS":
            return "200 OK", b"", "text/plain; charset=utf-8"

        if method == "POST" and path == "/api/v3.0/get_request_token":
            return self._handle_get_request_token()
        if method == "POST" and path == "/api/v3.0/get_access_token":
            return self._handle_get_access_token()
        if method == "GET" and path in ("/authorize", "/oauth/authorize"):
            return self._handle_authorize(environ)
        if method == "POST" and path == "/oauth/token":
            return self._handle_oauth2_token(environ)

        if not path.startswith("/api/v3.0/"):
            return "404 Not Found", {"errors": {"base": ["Route not found"]}}, "json"

        params = self._read_params(environ)
        endpoint = path[len("/api/v3.0/"):]
        if method == "GET" and endpoint in (
            "get_current_user",
            "get_friends",
            "get_groups",
            "get_expenses",
            "get_notifications",
        ):
            self.sync_recurring_expenses(current_user_id)
        if method == "GET" and (endpoint.startswith("get_group/") or endpoint.startswith("get_expense/")):
            self.sync_recurring_expenses(current_user_id)

        if method == "GET" and endpoint == "get_current_user":
            return "200 OK", {"user": self._current_user_payload(current_user_id)}, "json"
        if method == "GET" and endpoint.startswith("get_user/"):
            user_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "user id")
            return "200 OK", {"user": self._user_payload(user_id)}, "json"
        if method == "POST" and endpoint == "update_user":
            return self._handle_update_user(params)
        if method == "GET" and endpoint == "get_friends":
            return "200 OK", {"friends": self._list_friends(current_user_id)}, "json"
        if method == "GET" and endpoint == "get_groups":
            return "200 OK", {"groups": self._list_groups(current_user_id)}, "json"
        if method == "GET" and endpoint.startswith("get_group/"):
            group_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "group id")
            return "200 OK", {"group": self._group_payload(group_id, current_user_id)}, "json"
        if method == "POST" and endpoint == "create_group":
            return self._handle_create_group(params, current_user_id)
        if method == "POST" and endpoint == "add_user_to_group":
            return self._handle_add_user_to_group(params, current_user_id)
        if method == "POST" and endpoint.startswith("delete_group/"):
            group_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "group id")
            return self._handle_delete_group(group_id, current_user_id)
        if method == "GET" and endpoint == "get_currencies":
            return "200 OK", {"currencies": list(self.state["currencies"])}, "json"
        if method == "GET" and endpoint == "get_categories":
            return "200 OK", {"categories": list(self.state["categories"])}, "json"
        if method == "GET" and endpoint == "get_expenses":
            return self._handle_get_expenses(params, current_user_id)
        if method == "GET" and endpoint.startswith("get_expense/"):
            expense_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "expense id")
            return "200 OK", {"expense": self._expense_payload(expense_id, current_user_id)}, "json"
        if method == "POST" and endpoint == "create_expense":
            return self._handle_create_expense(params, current_user_id)
        if method == "POST" and endpoint.startswith("update_expense/"):
            expense_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "expense id")
            return self._handle_update_expense(expense_id, params, current_user_id)
        if method == "POST" and endpoint.startswith("delete_expense/"):
            expense_id = self._parse_int(endpoint.rsplit("/", 1)[-1], "expense id")
            return self._handle_delete_expense(expense_id, current_user_id)
        if method == "GET" and endpoint == "get_comments":
            return self._handle_get_comments(params)
        if method == "POST" and endpoint == "create_comment":
            return self._handle_create_comment(params, current_user_id)
        if method == "GET" and endpoint == "get_notifications":
            return self._handle_get_notifications(params, current_user_id)

        return "404 Not Found", {"errors": {"base": ["Route not found"]}}, "json"

    def _handle_get_request_token(self):
        token = "request-%s" % secrets.token_hex(8)
        secret = "secret-%s" % secrets.token_hex(8)
        self.state["oauth1_request_tokens"][token] = secret
        payload = "oauth_token=%s&oauth_token_secret=%s" % (token, secret)
        return "200 OK", payload.encode("utf-8"), "application/x-www-form-urlencoded; charset=utf-8"

    def _handle_get_access_token(self):
        token = "access-%s" % secrets.token_hex(8)
        secret = "access-secret-%s" % secrets.token_hex(8)
        payload = "oauth_token=%s&oauth_token_secret=%s" % (token, secret)
        return "200 OK", payload.encode("utf-8"), "application/x-www-form-urlencoded; charset=utf-8"

    def _handle_authorize(self, environ):
        params = self._read_params(environ)
        oauth_token = params.get("oauth_token", "")
        verifier = "verifier-%s" % secrets.token_hex(4)
        body = json.dumps({"oauth_token": oauth_token, "oauth_verifier": verifier}).encode("utf-8")
        return "200 OK", body, "application/json; charset=utf-8"

    def _handle_oauth2_token(self, environ):
        params = self._read_params(environ)
        token = {
            "access_token": "oauth2-%s" % secrets.token_hex(12),
            "token_type": "bearer",
            "scope": params.get("scope") or "read write",
        }
        return "200 OK", token, "json"

    def _handle_update_user(self, params):
        user_id = self._parse_int(params.get("id"), "user id")
        user = self._ensure_user(
            user_id,
            first_name=params.get("first_name"),
            last_name=params.get("last_name"),
            email=params.get("email"),
        )
        if params.get("first_name") is not None:
            user["first_name"] = params.get("first_name")
        if "last_name" in params:
            user["last_name"] = params.get("last_name")
        if params.get("email") is not None:
            user["email"] = params.get("email")
        return "200 OK", {"user": self._current_user_payload(user_id), "errors": {}}, "json"

    def _handle_create_group(self, params, current_user_id):
        group_id = self._next_id("group")
        members = [current_user_id]
        index = 0
        while True:
            prefix = "users__%s__" % index
            if prefix + "first_name" not in params and prefix + "user_id" not in params and prefix + "id" not in params:
                break
            member_id = params.get(prefix + "user_id")
            if member_id is None:
                member_id = params.get(prefix + "id")
            if member_id is not None:
                member_id = self._parse_int(member_id, "user id")
                member = self._ensure_user(
                    member_id,
                    first_name=params.get(prefix + "first_name"),
                    last_name=params.get(prefix + "last_name"),
                    email=params.get(prefix + "email"),
                )
            else:
                member = self._create_user(
                    first_name=params.get(prefix + "first_name") or "Guest",
                    last_name=params.get(prefix + "last_name"),
                    email=params.get(prefix + "email"),
                )
                member_id = member["id"]
            if member_id not in members:
                members.append(member_id)
            index += 1

        group = {
            "id": group_id,
            "name": params.get("name") or "Untitled group",
            "group_type": params.get("group_type"),
            "whiteboard": params.get("whiteboard"),
            "country_code": params.get("country_code") or "US",
            "created_at": self._now(),
            "updated_at": self._now(),
            "simplify_by_default": self._parse_bool(params.get("simplify_by_default"), False),
            "member_ids": members,
            "owner_id": current_user_id,
            "admin_ids": [],
            "archived": False,
            "deleted": False,
        }
        self.state["groups"][group_id] = group
        self._add_notification("Group '%s' created" % group["name"], "group", group_id, current_user_id)
        return "200 OK", {"group": self._group_payload(group_id, current_user_id)}, "json"

    def _handle_add_user_to_group(self, params, current_user_id):
        group_id = self._parse_int(params.get("group_id"), "group id")
        group = self._require_group(group_id)
        if not self._can_manage_group(group, current_user_id):
            raise ValueError("Only group owners or admins can add new users")
        user_id = params.get("user_id") or params.get("id")
        if user_id is not None:
            user = self._ensure_user(
                self._parse_int(user_id, "user id"),
                first_name=params.get("first_name"),
                last_name=params.get("last_name"),
                email=params.get("email"),
            )
        else:
            user = self._create_user(
                first_name=params.get("first_name") or "Guest",
                last_name=params.get("last_name"),
                email=params.get("email"),
            )
        if user["id"] not in group["member_ids"]:
            group["member_ids"].append(user["id"])
            group["updated_at"] = self._now()
        self._add_notification("%s added to %s" % (user["first_name"], group["name"]), "group", group_id, current_user_id)
        return "200 OK", {"success": True, "user": self._friend_payload(user["id"]), "errors": {}}, "json"

    def _handle_delete_group(self, group_id, current_user_id):
        if group_id == 0:
            raise ValueError("Group 0 cannot be deleted")
        group = self._require_group(group_id)
        if not self._can_manage_group(group, current_user_id):
            raise ValueError("Only group owners or admins can delete this group")
        group["deleted"] = True
        group["updated_at"] = self._now()
        self._add_notification("Group '%s' deleted" % group["name"], "group", group_id, current_user_id)
        return "200 OK", {"success": True, "errors": {}}, "json"

    def _handle_get_expenses(self, params, current_user_id):
        expenses = []
        for expense in self.state["expenses"].values():
            if self._matches_expense_filters(expense, params, current_user_id):
                expenses.append(self._expense_payload(expense["id"], current_user_id))
        expenses.sort(key=lambda item: item["updated_at"], reverse=True)
        offset = int(params.get("offset") or 0)
        limit = params.get("limit")
        if limit is not None:
            limit = int(limit)
            expenses = expenses[offset:offset + limit]
        else:
            expenses = expenses[offset:]
        return "200 OK", {"expenses": expenses}, "json"

    def _handle_create_expense(self, params, current_user_id):
        expense_id = self._next_id("expense")
        expense = self._build_expense_record(expense_id, params, current_user_id, existing=None)
        self.state["expenses"][expense_id] = expense
        self._add_notification("Expense '%s' created" % expense["description"], "expense", expense_id, current_user_id)
        return "200 OK", {"expenses": [self._expense_payload(expense_id, current_user_id)], "errors": {}}, "json"

    def _handle_update_expense(self, expense_id, params, current_user_id):
        existing = self._require_expense(expense_id)
        expense = self._build_expense_record(expense_id, params, current_user_id, existing=existing)
        expense["created_at"] = existing["created_at"]
        self.state["expenses"][expense_id] = expense
        self._add_notification("Expense '%s' updated" % expense["description"], "expense", expense_id, current_user_id)
        return "200 OK", {"expenses": [self._expense_payload(expense_id, current_user_id)], "errors": {}}, "json"

    def _handle_delete_expense(self, expense_id, current_user_id):
        expense = self._require_expense(expense_id)
        expense["deleted_at"] = self._now()
        expense["deleted_by"] = current_user_id
        expense["updated_at"] = expense["deleted_at"]
        self._add_notification("Expense '%s' deleted" % expense["description"], "expense", expense_id, current_user_id)
        return "200 OK", {"success": True, "errors": {}}, "json"

    def _handle_get_comments(self, params):
        expense_id = self._parse_int(params.get("expense_id"), "expense id")
        comments = [self._comment_payload(comment_id) for comment_id in self.state["expense_comments"].get(expense_id, [])]
        return "200 OK", {"comments": comments}, "json"

    def _handle_create_comment(self, params, current_user_id):
        expense_id = self._parse_int(params.get("expense_id"), "expense id")
        self._require_expense(expense_id)
        content = params.get("content")
        if not content:
            raise ValueError("content is required")
        comment_id = self._next_id("comment")
        comment = {
            "id": comment_id,
            "expense_id": expense_id,
            "content": content,
            "created_at": self._now(),
            "deleted_at": None,
            "user_id": current_user_id,
        }
        self.state["comments"][comment_id] = comment
        self.state["expense_comments"].setdefault(expense_id, []).append(comment_id)
        self._add_notification("Comment added to expense %s" % expense_id, "expense", expense_id, current_user_id)
        return "200 OK", {"comment": self._comment_payload(comment_id), "errors": {}}, "json"

    def _handle_get_notifications(self, params, current_user_id):
        notifications = [
            self._notification_payload(item["id"])
            for item in self.state["notifications"]
            if item.get("created_by") == current_user_id or item.get("visible_to_all")
        ]
        updated_since = params.get("updated_since")
        if updated_since:
            notifications = [item for item in notifications if item["created_at"] >= updated_since]
        limit = params.get("limit")
        if limit is not None:
            notifications = notifications[:int(limit)]
        return "200 OK", {"notifications": notifications}, "json"

    def _build_expense_record(self, expense_id, params, current_user_id, existing=None):
        if existing is None:
            created_at = self._now()
            created_by = current_user_id
        else:
            created_at = existing["created_at"]
            created_by = existing["created_by"]

        group_id = params.get("group_id")
        if group_id is None and existing is not None:
            group_id = existing.get("group_id")
        group = None
        if group_id is not None:
            group_id = self._parse_int(group_id, "group id")
            group = self._require_group(group_id)
            if current_user_id not in group["member_ids"]:
                raise ValueError("You can only add expenses to your own groups")

        users = self._extract_expense_users(params, current_user_id, existing)
        if not users:
            raise ValueError("at least one expense user is required")
        if group is not None:
            member_ids = set(group["member_ids"])
            if any(share["user_id"] not in member_ids for share in users):
                raise ValueError("Expense users must belong to the selected group")

        description = params.get("description")
        if description is None and existing is not None:
            description = existing["description"]
        if not description:
            raise ValueError("description is required")

        cost = params.get("cost")
        if cost is None and existing is not None:
            cost = existing["cost"]
        if cost is None:
            raise ValueError("cost is required")

        split_method = self._normalize_split_method(
            params.get("split_method"),
            existing=existing,
            split_equally=params.get("split_equally"),
        )
        participants = self._extract_expense_participants(
            params,
            users,
            group_member_ids=(group or {}).get("member_ids"),
            existing=existing,
        )
        payers = self._extract_expense_payers(params, users, existing=existing)
        if group is not None:
            member_ids = set(group["member_ids"])
            if any(item["user_id"] not in member_ids for item in participants):
                raise ValueError("Expense participants must belong to the selected group")
            if any(item["user_id"] not in member_ids for item in payers):
                raise ValueError("Expense payers must belong to the selected group")

        category_id = params.get("category_id")
        if category_id is None and existing is not None:
            category_id = existing.get("category_id")
        if category_id is None:
            category_id = self.state["categories"][0]["id"]
        category_id = self._parse_int(category_id, "category id")

        repeats = self._parse_bool(params.get("repeats"), (existing or {}).get("repeats", False))
        repeat_interval = params.get("repeat_interval")
        if repeat_interval is None and existing is not None:
            repeat_interval = existing.get("repeat_interval")
        repeat_interval = self._normalize_repeat_interval(repeat_interval, repeats)
        email_reminder = self._parse_bool(params.get("email_reminder"), (existing or {}).get("email_reminder", False))
        email_reminder_in_advance = params.get("email_reminder_in_advance")
        if email_reminder_in_advance in (None, ""):
            email_reminder_in_advance = (existing or {}).get("email_reminder_in_advance", -1)
        else:
            email_reminder_in_advance = int(email_reminder_in_advance)
        next_repeat = params.get("next_repeat")
        if next_repeat in (None, ""):
            next_repeat = self._next_repeat_value(
                params.get("date") or (existing or {}).get("date") or self._now(),
                repeat_interval,
                existing=(existing or {}).get("next_repeat"),
                repeats=repeats,
            )
        series_id = params.get("series_id")
        if series_id in (None, ""):
            series_id = (existing or {}).get("series_id")
        if repeats and series_id in (None, ""):
            series_id = self._next_id("recurring_series")
        elif series_id not in (None, ""):
            series_id = int(series_id)
        series_root_expense_id = params.get("series_root_expense_id")
        if series_root_expense_id in (None, ""):
            series_root_expense_id = (existing or {}).get("series_root_expense_id")
        if series_root_expense_id not in (None, ""):
            series_root_expense_id = int(series_root_expense_id)
        elif repeats:
            series_root_expense_id = expense_id
        series_paused = self._parse_bool(params.get("series_paused"), (existing or {}).get("series_paused", False))
        series_cancelled = self._parse_bool(params.get("series_cancelled"), (existing or {}).get("series_cancelled", False))
        expense = {
            "id": expense_id,
            "group_id": group_id,
            "friendship_id": None,
            "expense_bundle_id": None,
            "description": description,
            "repeats": repeats,
            "repeat_interval": repeat_interval,
            "email_reminder": email_reminder,
            "email_reminder_in_advance": email_reminder_in_advance,
            "next_repeat": next_repeat,
            "details": params.get("details") if params.get("details") is not None else (existing or {}).get("details"),
            "payment": self._parse_bool(params.get("payment"), (existing or {}).get("payment", False)),
            "creation_method": None,
            "transaction_method": "offline",
            "transaction_confirmed": False,
            "cost": str(cost),
            "currency_code": params.get("currency_code") or (existing or {}).get("currency_code") or self.state["currencies"][0]["currency_code"],
            "date": params.get("date") or (existing or {}).get("date") or self._now(),
            "created_at": created_at,
            "created_by": created_by,
            "updated_at": self._now(),
            "updated_by": current_user_id,
            "deleted_at": None if existing is None else existing.get("deleted_at"),
            "deleted_by": None if existing is None else existing.get("deleted_by"),
            "category_id": category_id,
            "receipt": {"original": None, "large": None},
            "user_shares": users,
            "split_equally": split_method == "equal",
            "split_method": split_method,
            "payers": payers,
            "participants": participants,
            "series_id": series_id,
            "series_root_expense_id": series_root_expense_id,
            "parent_expense_id": params.get("parent_expense_id") if params.get("parent_expense_id") is not None else (existing or {}).get("parent_expense_id"),
            "series_paused": series_paused,
            "series_cancelled": series_cancelled,
        }
        return expense

    def _extract_expense_users(self, params, current_user_id, existing=None):
        users = []
        index = 0
        while True:
            prefix = "users__%s__" % index
            if prefix + "user_id" not in params:
                break
            user_id = self._parse_int(params.get(prefix + "user_id"), "user id")
            self._ensure_user(user_id)
            users.append({
                "user_id": user_id,
                "paid_share": self._money(params.get(prefix + "paid_share", "0")),
                "owed_share": self._money(params.get(prefix + "owed_share", "0")),
            })
            index += 1
        if users:
            return users
        if existing is not None:
            return list(existing["user_shares"])
        return [{"user_id": current_user_id, "paid_share": self._money(params.get("cost", "0")), "owed_share": self._money(params.get("cost", "0"))}]

    def _extract_expense_payers(self, params, users, existing=None):
        payers = []
        index = 0
        while True:
            prefix = "payers__%s__" % index
            if prefix + "user_id" not in params:
                break
            user_id = self._parse_int(params.get(prefix + "user_id"), "payer user id")
            self._ensure_user(user_id)
            payers.append({
                "user_id": user_id,
                "paid_share": self._money(params.get(prefix + "paid_share", "0")),
            })
            index += 1
        if payers:
            return payers
        if existing is not None and existing.get("payers"):
            return list(existing["payers"])
        derived = []
        for share in users:
            if Decimal(share["paid_share"]) > 0:
                derived.append({"user_id": share["user_id"], "paid_share": share["paid_share"]})
        return derived

    def _extract_expense_participants(self, params, users, group_member_ids=None, existing=None):
        participants = []
        index = 0
        existing_map = {item["user_id"]: item for item in (existing or {}).get("participants", [])}
        share_map = {item["user_id"]: item for item in users}
        while True:
            prefix = "participants__%s__" % index
            if prefix + "user_id" not in params:
                break
            user_id = self._parse_int(params.get(prefix + "user_id"), "participant user id")
            self._ensure_user(user_id)
            existing_participant = existing_map.get(user_id, {})
            split_value = params.get(prefix + "split_value")
            if split_value in (None, ""):
                split_value = existing_participant.get("split_value")
            if split_value in (None, "") and user_id in share_map:
                split_value = share_map[user_id]["owed_share"]
            participants.append({
                "user_id": user_id,
                "included": self._parse_bool(params.get(prefix + "included"), existing_participant.get("included", True)),
                "split_value": split_value,
            })
            index += 1
        if participants:
            return participants
        if existing is not None and existing.get("participants"):
            return list(existing["participants"])
        if group_member_ids:
            return [
                {
                    "user_id": user_id,
                    "included": True,
                    "split_value": share_map[user_id]["owed_share"] if user_id in share_map else None,
                }
                for user_id in group_member_ids
            ]
        return [{"user_id": share["user_id"], "included": True, "split_value": share["owed_share"]} for share in users]

    def _normalize_split_method(self, split_method, existing=None, split_equally=None):
        method = str(split_method or "").strip().lower()
        if not method and existing is not None:
            method = str(existing.get("split_method") or "").strip().lower()
        if not method:
            split_equally_value = self._parse_bool(split_equally, (existing or {}).get("split_equally", False))
            return "equal" if split_equally_value else "exact"
        if method == "custom":
            # Legacy: map deprecated "custom" split mode to the explicit exact-amount variant.
            return "exact"
        if method not in ("equal", "exact", "percentage", "shares"):
            raise ValueError("split_method must be one of: equal, exact, percentage, shares")
        return method

    def _matches_expense_filters(self, expense, params, current_user_id):
        if not self._expense_visible_to_user(expense, current_user_id):
            return False
        visible = params.get("visible")
        if visible is not None and self._parse_bool(visible, True) and expense.get("deleted_at"):
            return False
        if params.get("group_id") is not None:
            if expense.get("group_id") != self._parse_int(params.get("group_id"), "group id"):
                return False
        if params.get("friend_id") is not None:
            friend_id = self._parse_int(params.get("friend_id"), "friend id")
            if friend_id not in [item["user_id"] for item in expense["user_shares"]]:
                return False
        if params.get("dated_after") and expense["date"] < params.get("dated_after"):
            return False
        if params.get("dated_before") and expense["date"] > params.get("dated_before"):
            return False
        if params.get("updated_after") and expense["updated_at"] < params.get("updated_after"):
            return False
        if params.get("updated_before") and expense["updated_at"] > params.get("updated_before"):
            return False
        return True

    def _list_friends(self, current_user_id):
        friend_ids = sorted(self.state["friendships"].get(current_user_id, set()))
        return [self._friend_payload(user_id, current_user_id) for user_id in friend_ids]

    def _list_groups(self, current_user_id):
        group_ids = sorted(
            group_id
            for group_id, group in self.state["groups"].items()
            if not group.get("deleted") and current_user_id in group["member_ids"]
        )
        return [self._group_payload(group_id, current_user_id) for group_id in group_ids]

    def _current_user_payload(self, user_id):
        user = self._require_user(user_id)
        payload = self._user_base_payload(user)
        payload.update({
            "default_currency": self.state["currencies"][0]["currency_code"],
            "locale": "en",
            "date_format": "YYYY-MM-DD",
            "default_group_id": 0,
            "pending_friend_requests": len([
                item for item in self.state["friend_requests"].values()
                if item["to_user_id"] == user_id and item["status"] == "pending"
            ]),
        })
        return payload

    def _user_payload(self, user_id):
        return self._user_base_payload(self._require_user(user_id))

    def _friend_payload(self, user_id, current_user_id=None):
        user = self._require_user(user_id)
        payload = self._user_base_payload(user)
        payload["updated_at"] = user["updated_at"]
        payload["balance"] = self._friend_balances(user_id, current_user_id or self.state["current_user_id"])
        payload["balances"] = payload["balance"]
        payload["groups"] = self._friend_groups(user_id, current_user_id or self.state["current_user_id"])
        return payload

    def _group_payload(self, group_id, current_user_id=None):
        group = self._require_group(group_id)
        current_user_id = current_user_id or self.state["current_user_id"]
        if current_user_id not in group["member_ids"]:
            raise KeyError(group_id)
        repayments = self._group_repayments(group_id)
        return {
            "id": group["id"],
            "name": group["name"],
            "created_at": group["created_at"],
            "updated_at": group["updated_at"],
            "simplify_by_default": group["simplify_by_default"],
            "group_type": group.get("group_type"),
            "whiteboard": group.get("whiteboard"),
            "invite_link": "https://example.local/groups/%s" % group["id"],
            "country_code": group.get("country_code") or "US",
            "original_debts": repayments,
            "simplified_debts": repayments,
            "members": [self._friend_payload(member_id, current_user_id) for member_id in group["member_ids"]],
            "owner_id": group.get("owner_id"),
            "admin_ids": list(group.get("admin_ids") or []),
            "archived": bool(group.get("archived")),
            "current_user_role": self._group_role(group, current_user_id),
            "can_manage": self._can_manage_group(group, current_user_id),
        }

    def _expense_payload(self, expense_id, current_user_id=None):
        expense = self._require_expense(expense_id)
        current_user_id = current_user_id or self.state["current_user_id"]
        if not self._expense_visible_to_user(expense, current_user_id):
            raise KeyError(expense_id)
        users = []
        repayments = []
        creditors = []
        debtors = []
        currency_code = expense["currency_code"]
        participant_map = {item["user_id"]: item for item in expense.get("participants", [])}
        payer_map = {item["user_id"]: item for item in expense.get("payers", [])}
        for share in expense["user_shares"]:
            net = Decimal(share["paid_share"]) - Decimal(share["owed_share"])
            net_value = self._money(net)
            user_id = share["user_id"]
            user_payload = self._user_base_payload(self._require_user(user_id))
            users.append({
                "user": user_payload,
                "user_id": user_id,
                "paid_share": share["paid_share"],
                "owed_share": share["owed_share"],
                "net_balance": net_value,
                "included": participant_map.get(user_id, {}).get("included", True),
                "split_value": participant_map.get(user_id, {}).get("split_value"),
                "payer_amount": payer_map.get(user_id, {}).get("paid_share", share["paid_share"]),
            })
            if net > 0:
                creditors.append([user_id, net])
            elif net < 0:
                debtors.append([user_id, -net])

        for debtor_id, remaining in debtors:
            while remaining > 0 and creditors:
                creditor_id, available = creditors[0]
                amount = min(remaining, available)
                repayments.append({
                    "from": debtor_id,
                    "to": creditor_id,
                    "amount": self._money(amount),
                    "currency_code": currency_code,
                })
                remaining -= amount
                creditors[0][1] -= amount
                if creditors[0][1] <= 0:
                    creditors.pop(0)

        category = next((item for item in self.state["categories"] if item["id"] == expense["category_id"]), self.state["categories"][0])
        comments = self.state["expense_comments"].get(expense_id, [])
        return {
            "id": expense["id"],
            "group_id": expense["group_id"],
            "friendship_id": expense["friendship_id"],
            "expense_bundle_id": expense["expense_bundle_id"],
            "description": expense["description"],
            "repeats": expense["repeats"],
            "repeat_interval": expense["repeat_interval"],
            "email_reminder": expense["email_reminder"],
            "email_reminder_in_advance": expense["email_reminder_in_advance"],
            "next_repeat": expense["next_repeat"],
            "details": expense["details"],
            "comments_count": len(comments),
            "payment": expense["payment"],
            "creation_method": expense["creation_method"],
            "transaction_method": expense["transaction_method"],
            "transaction_confirmed": expense["transaction_confirmed"],
            "cost": expense["cost"],
            "currency_code": expense["currency_code"],
            "created_by": self._user_base_payload(self._require_user(expense["created_by"])),
            "date": expense["date"],
            "created_at": expense["created_at"],
            "updated_at": expense["updated_at"],
            "deleted_at": expense["deleted_at"],
            "receipt": expense["receipt"],
            "category": {"id": category["id"], "name": category["name"]},
            "updated_by": self._user_base_payload(self._require_user(expense["updated_by"])) if expense["updated_by"] is not None else None,
            "deleted_by": self._user_base_payload(self._require_user(expense["deleted_by"])) if expense["deleted_by"] is not None else None,
            "repayments": repayments,
            "users": users,
            "split_equally": expense.get("split_equally", False),
            "split_method": expense.get("split_method", "equal" if expense.get("split_equally") else "exact"),
            "payers": expense.get("payers") or [
                {"user_id": item["user_id"], "paid_share": item["paid_share"]}
                for item in expense["user_shares"]
                if Decimal(item["paid_share"]) > 0
            ],
            "participants": expense.get("participants") or [
                {"user_id": item["user_id"], "included": True, "split_value": item["owed_share"]}
                for item in expense["user_shares"]
            ],
            "series_id": expense.get("series_id"),
            "series_root_expense_id": expense.get("series_root_expense_id"),
            "parent_expense_id": expense.get("parent_expense_id"),
            "series_paused": bool(expense.get("series_paused")),
            "series_cancelled": bool(expense.get("series_cancelled")),
            "transaction_id": None,
        }

    def _comment_payload(self, comment_id):
        comment = self.state["comments"][comment_id]
        return {
            "id": comment["id"],
            "content": comment["content"],
            "comment_type": "comment",
            "relation_type": "ExpenseComment",
            "relation_id": comment["expense_id"],
            "created_at": comment["created_at"],
            "deleted_at": comment["deleted_at"],
            "user": self._user_base_payload(self._require_user(comment["user_id"])),
        }

    def _notification_payload(self, notification_id):
        notification = next(item for item in self.state["notifications"] if item["id"] == notification_id)
        return {
            "id": notification["id"],
            "content": notification["content"],
            "type": notification["type"],
            "created_at": notification["created_at"],
            "created_by": notification["created_by"],
            "image_shape": "square",
            "image_url": "https://example.local/notifications/%s.png" % notification["id"],
            "source": {
                "id": notification["source_id"],
                "type": notification["source_type"],
                "url": "https://example.local/%s/%s" % (notification["source_type"].lower(), notification["source_id"]),
            },
        }

    def _friend_balances(self, user_id, current_user_id):
        totals = defaultdict(Decimal)
        for expense in self.state["expenses"].values():
            if expense.get("deleted_at"):
                continue
            user_map = {item["user_id"]: item for item in expense["user_shares"]}
            if user_id not in user_map or current_user_id not in user_map:
                continue
            currency = expense["currency_code"]
            totals[currency] += Decimal(user_map[user_id]["owed_share"]) - Decimal(user_map[user_id]["paid_share"])
        for settlement in self.state["settlements"].values():
            if current_user_id not in (settlement["from_user_id"], settlement["to_user_id"]):
                continue
            if user_id not in (settlement["from_user_id"], settlement["to_user_id"]):
                continue
            currency = settlement["currency_code"]
            amount = Decimal(settlement["amount"])
            if settlement["from_user_id"] == user_id and settlement["to_user_id"] == current_user_id:
                totals[currency] -= amount
            elif settlement["to_user_id"] == user_id and settlement["from_user_id"] == current_user_id:
                totals[currency] += amount
        if not totals:
            currency = self.state["currencies"][0]["currency_code"]
            return [{"currency_code": currency, "amount": self._money("0")}]
        return [{"currency_code": code, "amount": self._money(amount)} for code, amount in sorted(totals.items())]

    def _friend_groups(self, user_id, current_user_id):
        groups = []
        for group_id, group in self.state["groups"].items():
            if group.get("deleted") or user_id not in group["member_ids"] or current_user_id not in group["member_ids"]:
                continue
            balances = self._group_member_balances(group_id)
            groups.append({
                "id": group_id,
                "group_id": group_id,
                "balance": balances.get(user_id, [{"currency_code": self.state["currencies"][0]["currency_code"], "amount": self._money("0")}]),
            })
        return groups

    def _group_member_balances(self, group_id):
        totals = defaultdict(lambda: defaultdict(Decimal))
        for expense in self.state["expenses"].values():
            if expense.get("deleted_at") or expense.get("group_id") != group_id:
                continue
            for share in expense["user_shares"]:
                totals[share["user_id"]][expense["currency_code"]] += Decimal(share["paid_share"]) - Decimal(share["owed_share"])
        for settlement in self.state["settlements"].values():
            if settlement.get("group_id") != group_id:
                continue
            amount = Decimal(settlement["amount"])
            currency = settlement["currency_code"]
            totals[settlement["from_user_id"]][currency] += amount
            totals[settlement["to_user_id"]][currency] -= amount
        response = {}
        for member_id in self._require_group(group_id)["member_ids"]:
            member_totals = totals.get(member_id)
            if not member_totals:
                member_totals = {self.state["currencies"][0]["currency_code"]: Decimal("0")}
            response[member_id] = [{"currency_code": code, "amount": self._money(amount)} for code, amount in sorted(member_totals.items())]
        return response

    def _group_repayments(self, group_id):
        balances = self._group_member_balances(group_id)
        creditors = []
        debtors = []
        for member_id, member_balances in balances.items():
            primary = member_balances[0] if member_balances else None
            if not primary:
                continue
            amount = Decimal(primary["amount"])
            if amount > 0:
                creditors.append([member_id, amount, primary["currency_code"]])
            elif amount < 0:
                debtors.append([member_id, -amount, primary["currency_code"]])
        repayments = []
        for debtor_id, remaining, currency_code in debtors:
            while remaining > 0 and creditors:
                creditor_id, available, creditor_currency = creditors[0]
                if creditor_currency != currency_code:
                    creditors.pop(0)
                    continue
                amount = min(remaining, available)
                repayments.append({
                    "from": debtor_id,
                    "to": creditor_id,
                    "amount": self._money(amount),
                    "currency_code": currency_code,
                })
                remaining -= amount
                creditors[0][1] -= amount
                if creditors[0][1] <= 0:
                    creditors.pop(0)
        return repayments

    def _add_notification(self, content, source_type, source_id, current_user_id, visible_to_all=False):
        self.state["notifications"].insert(0, {
            "id": self._next_id("notification"),
            "content": content,
            "type": 0,
            "created_at": self._now(),
            "created_by": current_user_id,
            "source_type": source_type.title(),
            "source_id": source_id,
            "visible_to_all": visible_to_all,
        })

    def register_account(self, first_name, email, password, last_name=None):
        first_name = (first_name or "").strip()
        if not first_name:
            raise ValueError("first_name is required")
        email = self._normalize_email(email)
        if not email:
            raise ValueError("email is required")
        if self._find_user_by_email(email) is not None:
            raise ValueError("An account with that email already exists")
        password_hash = self._hash_password(password)
        user = self._create_user(first_name=first_name, last_name=last_name, email=email)
        self.state["password_hashes"][user["id"]] = password_hash
        self.state["friendships"].setdefault(user["id"], set())
        return self._user_payload(user["id"])

    def authenticate_account(self, email, password):
        email = self._normalize_email(email)
        user = self._find_user_by_email(email)
        if user is None:
            raise ValueError("Invalid email or password")
        password_hash = self.state["password_hashes"].get(user["id"])
        if not password_hash or not self._verify_password(password, password_hash):
            raise ValueError("Invalid email or password")
        return self._user_payload(user["id"])

    def add_friend(self, current_user_id, email=None, user_id=None):
        if user_id is None:
            email = self._normalize_email(email)
            friend = self._find_user_by_email(email)
        else:
            friend = self.state["users"].get(int(user_id))
        if friend is None:
            raise ValueError("No account exists for that friend")
        if friend["id"] == current_user_id:
            raise ValueError("You cannot add yourself as a friend")
        self.state["friendships"].setdefault(current_user_id, set()).add(friend["id"])
        self.state["friendships"].setdefault(friend["id"], set()).add(current_user_id)
        self._add_notification(
            "You are now friends with %s" % friend["first_name"],
            "friend",
            friend["id"],
            current_user_id,
        )
        return self._friend_payload(friend["id"], current_user_id)

    def send_friend_request(self, current_user_id, email=None, user_id=None):
        if user_id is None:
            email = self._normalize_email(email)
            friend = self._find_user_by_email(email)
        else:
            friend = self.state["users"].get(int(user_id))
        if friend is None:
            raise ValueError("No account exists for that friend")
        if friend["id"] == current_user_id:
            raise ValueError("You cannot add yourself as a friend")
        if friend["id"] in self.state["friendships"].get(current_user_id, set()):
            return {"status": "accepted", "friend": self._friend_payload(friend["id"], current_user_id)}
        for request_id, request in self.state["friend_requests"].items():
            if request["status"] != "pending":
                continue
            if request["from_user_id"] == current_user_id and request["to_user_id"] == friend["id"]:
                return self._friend_request_payload(request_id, current_user_id)
            if request["from_user_id"] == friend["id"] and request["to_user_id"] == current_user_id:
                return self.respond_friend_request(current_user_id, request_id, accept=True)
        request_id = self._next_id("friend_request")
        self.state["friend_requests"][request_id] = {
            "id": request_id,
            "from_user_id": current_user_id,
            "to_user_id": friend["id"],
            "status": "pending",
            "created_at": self._now(),
            "responded_at": None,
        }
        self._add_notification(
            "Friend request sent to %s" % friend["first_name"],
            "friend",
            friend["id"],
            current_user_id,
        )
        return self._friend_request_payload(request_id, current_user_id)

    def list_friend_requests(self, current_user_id):
        incoming = []
        outgoing = []
        for request_id, request in sorted(self.state["friend_requests"].items(), reverse=True):
            payload = self._friend_request_payload(request_id, current_user_id)
            if request["to_user_id"] == current_user_id and request["status"] == "pending":
                incoming.append(payload)
            elif request["from_user_id"] == current_user_id and request["status"] == "pending":
                outgoing.append(payload)
        return {"incoming": incoming, "outgoing": outgoing}

    def respond_friend_request(self, current_user_id, request_id, accept=True):
        request = self.state["friend_requests"].get(int(request_id))
        if request is None:
            raise ValueError("Friend request not found")
        if request["to_user_id"] != current_user_id:
            raise ValueError("Only the recipient can respond to this friend request")
        if request["status"] != "pending":
            raise ValueError("This friend request has already been handled")
        request["status"] = "accepted" if accept else "rejected"
        request["responded_at"] = self._now()
        requester = self._require_user(request["from_user_id"])
        if accept:
            self.state["friendships"].setdefault(request["from_user_id"], set()).add(current_user_id)
            self.state["friendships"].setdefault(current_user_id, set()).add(request["from_user_id"])
            self._add_notification(
                "%s accepted your friend request" % self._require_user(current_user_id)["first_name"],
                "friend",
                current_user_id,
                current_user_id,
                visible_to_all=True,
            )
            return {
                "status": "accepted",
                "friend": self._friend_payload(request["from_user_id"], current_user_id),
                "request": self._friend_request_payload(request_id, current_user_id),
            }
        self._add_notification(
            "Friend request from %s declined" % requester["first_name"],
            "friend",
            requester["id"],
            current_user_id,
        )
        return {"status": "rejected", "request": self._friend_request_payload(request_id, current_user_id)}

    def update_account(self, current_user_id, first_name=None, last_name=None, email=None):
        user = self._require_user(current_user_id)
        normalized_email = self._normalize_email(email) if email is not None else None
        if normalized_email and normalized_email != self._normalize_email(user.get("email")):
            existing = self._find_user_by_email(normalized_email)
            if existing and existing["id"] != current_user_id:
                raise ValueError("An account with that email already exists")
        if first_name is not None:
            first_name = first_name.strip()
            if not first_name:
                raise ValueError("first_name is required")
            user["first_name"] = first_name
        if last_name is not None:
            user["last_name"] = last_name.strip() or None
        if email is not None:
            if not normalized_email:
                raise ValueError("email is required")
            user["email"] = normalized_email
        user["updated_at"] = self._now()
        self._add_notification("Profile updated", "user", current_user_id, current_user_id)
        return self._current_user_payload(current_user_id)

    def update_password(self, current_user_id, current_password, new_password):
        password_hash = self.state["password_hashes"].get(current_user_id)
        if not password_hash or not self._verify_password(current_password, password_hash):
            raise ValueError("Current password is incorrect")
        self.state["password_hashes"][current_user_id] = self._hash_password(new_password)
        self._add_notification("Password updated", "user", current_user_id, current_user_id)
        return {"updated": True}

    def update_group(self, current_user_id, group_id, name=None, whiteboard=None):
        group = self._require_group(int(group_id))
        if not self._can_manage_group(group, current_user_id):
            raise ValueError("Only group owners or admins can update this group")
        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("name is required")
            group["name"] = name
        if whiteboard is not None:
            group["whiteboard"] = whiteboard.strip() or None
        group["updated_at"] = self._now()
        self._add_notification("Group '%s' updated" % group["name"], "group", group["id"], current_user_id)
        return self._group_payload(group["id"], current_user_id)

    def add_group_member(self, current_user_id, group_id, user_id):
        self._handle_add_user_to_group({"group_id": group_id, "user_id": user_id}, current_user_id)
        return self._group_payload(int(group_id), current_user_id)

    def remove_group_member(self, current_user_id, group_id, member_user_id):
        group = self._require_group(int(group_id))
        if not self._can_manage_group(group, current_user_id):
            raise ValueError("Only group owners or admins can remove members")
        member_user_id = int(member_user_id)
        if member_user_id == group.get("owner_id"):
            raise ValueError("Transfer ownership before removing the owner")
        if member_user_id not in group["member_ids"]:
            raise ValueError("That user is not in this group")
        group["member_ids"] = [item for item in group["member_ids"] if item != member_user_id]
        group["admin_ids"] = [item for item in group.get("admin_ids", []) if item != member_user_id]
        group["updated_at"] = self._now()
        member = self._require_user(member_user_id)
        self._add_notification("%s removed from %s" % (member["first_name"], group["name"]), "group", group["id"], current_user_id)
        return self._group_payload(group["id"], current_user_id)

    def leave_group(self, current_user_id, group_id):
        group = self._require_group(int(group_id))
        if group["id"] == 0:
            raise ValueError("You cannot leave the non-group expenses bucket")
        if current_user_id not in group["member_ids"]:
            raise ValueError("You are not a member of this group")
        remaining = [item for item in group["member_ids"] if item != current_user_id]
        if not remaining:
            group["deleted"] = True
        else:
            group["member_ids"] = remaining
            group["admin_ids"] = [item for item in group.get("admin_ids", []) if item != current_user_id]
            if group.get("owner_id") == current_user_id:
                next_owner = group["admin_ids"][0] if group["admin_ids"] else remaining[0]
                group["owner_id"] = next_owner
                group["admin_ids"] = [item for item in group["admin_ids"] if item != next_owner]
        group["updated_at"] = self._now()
        self._add_notification("%s left %s" % (self._require_user(current_user_id)["first_name"], group["name"]), "group", group["id"], current_user_id)
        return {"left": True, "group_id": group["id"], "deleted": bool(group.get("deleted"))}

    def set_group_admin(self, current_user_id, group_id, member_user_id, is_admin):
        group = self._require_group(int(group_id))
        if current_user_id != group.get("owner_id"):
            raise ValueError("Only the group owner can manage admins")
        member_user_id = int(member_user_id)
        if member_user_id == group.get("owner_id"):
            raise ValueError("The group owner is already the owner")
        if member_user_id not in group["member_ids"]:
            raise ValueError("That user is not in this group")
        admin_ids = set(group.get("admin_ids") or [])
        if is_admin:
            admin_ids.add(member_user_id)
        else:
            admin_ids.discard(member_user_id)
        group["admin_ids"] = sorted(admin_ids)
        group["updated_at"] = self._now()
        member = self._require_user(member_user_id)
        self._add_notification(
            "%s %s admin access in %s" % (member["first_name"], "received" if is_admin else "lost", group["name"]),
            "group",
            group["id"],
            current_user_id,
        )
        return self._group_payload(group["id"], current_user_id)

    def set_group_archived(self, current_user_id, group_id, archived):
        group = self._require_group(int(group_id))
        if not self._can_manage_group(group, current_user_id):
            raise ValueError("Only group owners or admins can archive this group")
        if group["id"] == 0:
            raise ValueError("You cannot archive the non-group expenses bucket")
        group["archived"] = bool(archived)
        group["updated_at"] = self._now()
        self._add_notification(
            "Group '%s' %s" % (group["name"], "archived" if group["archived"] else "restored"),
            "group",
            group["id"],
            current_user_id,
        )
        return self._group_payload(group["id"], current_user_id)

    def pause_expense_series(self, current_user_id, series_id):
        root = self._require_series_root(series_id, current_user_id)
        root["series_paused"] = True
        root["updated_at"] = self._now()
        self._add_notification("Recurring series '%s' paused" % root["description"], "expense", root["id"], current_user_id)
        return self._expense_payload(root["id"], current_user_id)

    def resume_expense_series(self, current_user_id, series_id):
        root = self._require_series_root(series_id, current_user_id)
        root["series_paused"] = False
        root["updated_at"] = self._now()
        self._add_notification("Recurring series '%s' resumed" % root["description"], "expense", root["id"], current_user_id)
        return self._expense_payload(root["id"], current_user_id)

    def cancel_expense_series(self, current_user_id, series_id):
        root = self._require_series_root(series_id, current_user_id)
        root["series_cancelled"] = True
        root["repeats"] = False
        root["next_repeat"] = None
        root["updated_at"] = self._now()
        self._add_notification("Recurring series '%s' cancelled" % root["description"], "expense", root["id"], current_user_id)
        return self._expense_payload(root["id"], current_user_id)

    def update_expense_series(self, current_user_id, series_id, params):
        root = self._require_series_root(series_id, current_user_id)
        params = dict(params or {})
        params["series_id"] = root["series_id"]
        params["series_root_expense_id"] = root["series_root_expense_id"]
        params["series_paused"] = root.get("series_paused", False)
        params["series_cancelled"] = root.get("series_cancelled", False)
        updated = self._build_expense_record(root["id"], params, current_user_id, existing=root)
        updated["created_at"] = root["created_at"]
        updated["series_id"] = root["series_id"]
        updated["series_root_expense_id"] = root["series_root_expense_id"]
        self.state["expenses"][root["id"]] = updated
        self._add_notification("Recurring series '%s' updated" % updated["description"], "expense", updated["id"], current_user_id)
        return self._expense_payload(updated["id"], current_user_id)

    def record_settlement(self, current_user_id, other_user_id, amount, group_id=None, note=None, date=None, from_user_id=None, to_user_id=None):
        other_user_id = int(other_user_id)
        self._require_user(other_user_id)
        if from_user_id is None or to_user_id is None:
            from_user_id = current_user_id
            to_user_id = other_user_id
        from_user_id = int(from_user_id)
        to_user_id = int(to_user_id)
        self._require_user(from_user_id)
        self._require_user(to_user_id)
        if current_user_id not in (from_user_id, to_user_id):
            raise ValueError("You can only record settlements involving yourself")
        if from_user_id == to_user_id:
            raise ValueError("You cannot settle up with yourself")
        amount = self._money(amount)
        if Decimal(amount) <= 0:
            raise ValueError("amount must be greater than zero")
        settlement_id = self._next_id("settlement")
        record = {
            "id": settlement_id,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "amount": amount,
            "currency_code": self.state["currencies"][0]["currency_code"],
            "group_id": int(group_id) if group_id not in (None, "", 0, "0") else None,
            "note": note.strip() if isinstance(note, str) and note.strip() else None,
            "date": date or self._now(),
            "created_at": self._now(),
            "created_by": current_user_id,
        }
        if record["group_id"] is not None:
            group = self._require_group(record["group_id"])
            if from_user_id not in group["member_ids"] or to_user_id not in group["member_ids"]:
                raise ValueError("Settlements inside a group must involve group members")
        self.state["settlements"][settlement_id] = record
        other_user = self._require_user(other_user_id)
        self._add_notification(
            "Settlement recorded with %s for %s %s" % (
                other_user["first_name"],
                record["currency_code"],
                amount,
            ),
            "expense",
            settlement_id,
            current_user_id,
        )
        return dict(record)

    def _resolve_current_user_id(self, environ):
        raw_user_id = environ.get("HTTP_X_SPLITWISE_USER_ID")
        if raw_user_id:
            try:
                user_id = int(raw_user_id)
            except (TypeError, ValueError):
                user_id = None
            if user_id in self.state["users"]:
                return user_id
        return self.state["current_user_id"]

    def _expense_visible_to_user(self, expense, current_user_id):
        if current_user_id in [item["user_id"] for item in expense["user_shares"]]:
            return True
        group_id = expense.get("group_id")
        if group_id is None:
            return False
        group = self.state["groups"].get(group_id)
        return bool(group and current_user_id in group["member_ids"] and not group.get("deleted"))

    def _normalize_email(self, email):
        return (email or "").strip().lower()

    def _friend_request_payload(self, request_id, current_user_id):
        request = self.state["friend_requests"][request_id]
        other_user_id = request["from_user_id"] if request["to_user_id"] == current_user_id else request["to_user_id"]
        return {
            "id": request["id"],
            "status": request["status"],
            "created_at": request["created_at"],
            "responded_at": request["responded_at"],
            "direction": "incoming" if request["to_user_id"] == current_user_id else "outgoing",
            "user": self._user_payload(other_user_id),
        }

    def _find_user_by_email(self, email):
        if not email:
            return None
        for user in self.state["users"].values():
            if self._normalize_email(user.get("email")) == email:
                return user
        return None

    def _hash_password(self, password):
        password = (password or "").strip()
        if len(password) < 8:
            raise ValueError("password must be at least 8 characters")
        salt = secrets.token_hex(32)
        iterations = 200000
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()
        return "pbkdf2_sha256$%s$%s$%s" % (iterations, salt, digest)

    def _verify_password(self, password, encoded):
        try:
            _, iterations, salt, expected = encoded.split("$", 3)
        except ValueError:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            (password or "").encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
        return hmac.compare_digest(digest, expected)

    def _read_params(self, environ):
        params = {}
        for key, value in parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True).items():
            params[key] = value[-1]

        if environ.get("REQUEST_METHOD", "GET").upper() != "POST":
            return params

        content_type = environ.get("CONTENT_TYPE", "")
        if content_type.startswith("application/json"):
            raw = self._read_body(environ)
            if raw:
                params.update(json.loads(raw.decode("utf-8")))
            return params

        if content_type.startswith("multipart/form-data"):
            raw = self._read_body(environ)
            if not raw:
                return params
            message = BytesParser(policy=default).parsebytes(
                b"Content-Type: " + content_type.encode("utf-8") + b"\r\nMIME-Version: 1.0\r\n\r\n" + raw
            )
            for part in message.iter_parts():
                if part.get_content_disposition() != "form-data":
                    continue
                key = part.get_param("name", header="content-disposition")
                if not key or part.get_filename():
                    continue
                value = part.get_content()
                if isinstance(value, bytes):
                    value = value.decode(part.get_content_charset() or "utf-8")
                params[key] = value
            return params

        raw = self._read_body(environ)
        for key, value in parse_qs(raw.decode("utf-8"), keep_blank_values=True).items():
            params[key] = value[-1]
        return params

    def _read_body(self, environ):
        try:
            environ["wsgi.input"].seek(0)
        except Exception:
            pass
        length = int(environ.get("CONTENT_LENGTH") or 0)
        return environ["wsgi.input"].read(length) if length else b""

    def _require_user(self, user_id):
        return self.state["users"][user_id]

    def _ensure_user(self, user_id, first_name=None, last_name=None, email=None):
        user = self.state["users"].get(user_id)
        if user is None:
            user = {
                "id": user_id,
                "first_name": first_name or "User",
                "last_name": last_name,
                "email": email or "user%s@example.com" % user_id,
                "registration_status": "confirmed",
                "updated_at": self._now(),
            }
            self.state["users"][user_id] = user
        if first_name is not None:
            user["first_name"] = first_name
        if last_name is not None:
            user["last_name"] = last_name
        if email is not None:
            user["email"] = email
        user["updated_at"] = self._now()
        return user

    def _create_user(self, first_name, last_name=None, email=None):
        user_id = self._next_id("user")
        return self._ensure_user(user_id, first_name=first_name, last_name=last_name, email=email)

    def _require_group(self, group_id):
        group = self.state["groups"][group_id]
        if group.get("deleted"):
            raise KeyError(group_id)
        return group

    def _group_role(self, group, user_id):
        if user_id == group.get("owner_id"):
            return "owner"
        if user_id in (group.get("admin_ids") or []):
            return "admin"
        return "member"

    def _can_manage_group(self, group, user_id):
        return user_id == group.get("owner_id") or user_id in (group.get("admin_ids") or [])

    def _require_expense(self, expense_id):
        return self.state["expenses"][expense_id]

    def _user_base_payload(self, user):
        return {
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user.get("last_name"),
            "picture": self._picture_payload(user["id"]),
            "email": user.get("email"),
            "registration_status": user.get("registration_status") or "confirmed",
        }

    def _picture_payload(self, user_id):
        base = "https://example.local/avatars/%s" % user_id
        return {"small": base + "/small.png", "medium": base + "/medium.png", "large": base + "/large.png"}

    def _require_series_root(self, series_id, current_user_id):
        series_id = int(series_id)
        for expense in self.state["expenses"].values():
            if expense.get("series_id") != series_id:
                continue
            if expense.get("series_root_expense_id") != expense["id"]:
                continue
            if not self._expense_visible_to_user(expense, current_user_id):
                raise KeyError(series_id)
            return expense
        raise KeyError(series_id)

    def sync_recurring_expenses(self, current_user_id=None):
        del current_user_id
        now = self._now()
        roots = [
            expense for expense in self.state["expenses"].values()
            if expense.get("repeats")
            and expense.get("series_id")
            and expense.get("series_root_expense_id") == expense["id"]
            and not expense.get("deleted_at")
            and not expense.get("series_paused")
            and not expense.get("series_cancelled")
        ]
        generated = False
        for root in roots:
            next_repeat = root.get("next_repeat")
            loops = 0
            # Cap catch-up generation at 24 instances per request so a corrupted or very old schedule cannot loop forever in one sync.
            while next_repeat and next_repeat <= now and loops < 24:
                if not self._series_instance_exists(root["series_id"], next_repeat):
                    self._spawn_recurring_instance(root, next_repeat)
                    generated = True
                root["next_repeat"] = self._next_repeat_value(next_repeat, root["repeat_interval"], repeats=True)
                root["updated_at"] = self._now()
                next_repeat = root.get("next_repeat")
                loops += 1
        return generated

    def _series_instance_exists(self, series_id, date_value):
        for expense in self.state["expenses"].values():
            if expense.get("deleted_at"):
                continue
            if expense.get("series_id") == series_id and expense.get("date") == date_value and expense.get("series_root_expense_id") != expense["id"]:
                return True
        return False

    def _spawn_recurring_instance(self, root_expense, date_value):
        expense_id = self._next_id("expense")
        instance = {key: value for key, value in root_expense.items() if key not in ("id", "created_at", "updated_at", "date", "next_repeat", "repeats", "parent_expense_id")}
        instance["id"] = expense_id
        instance["date"] = date_value
        instance["created_at"] = self._now()
        instance["updated_at"] = instance["created_at"]
        instance["repeats"] = False
        instance["next_repeat"] = None
        instance["parent_expense_id"] = root_expense["id"]
        instance["series_root_expense_id"] = root_expense["id"]
        instance["creation_method"] = "recurring"
        instance["user_shares"] = [dict(item) for item in root_expense["user_shares"]]
        instance["payers"] = [dict(item) for item in root_expense.get("payers", [])]
        instance["participants"] = [dict(item) for item in root_expense.get("participants", [])]
        self.state["expenses"][expense_id] = instance
        self._add_notification("Recurring expense '%s' created" % root_expense["description"], "expense", expense_id, root_expense["created_by"])
        return instance

    def _next_id(self, key):
        value = self.state["next_ids"][key]
        self.state["next_ids"][key] += 1
        return value

    def _parse_int(self, value, label):
        if value is None or value == "":
            raise ValueError("%s is required" % label)
        return int(value)

    def _parse_bool(self, value, default=False):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("1", "true", "yes", "on")

    def _normalize_repeat_interval(self, value, repeats):
        interval = (value or "").strip().lower()
        if not repeats:
            return "never"
        if interval not in ("daily", "weekly", "monthly", "yearly"):
            return "monthly"
        return interval

    def _next_repeat_value(self, date_value, repeat_interval, existing=None, repeats=False):
        if not repeats or repeat_interval == "never":
            return None
        if existing:
            return existing
        try:
            base = datetime.fromisoformat(str(date_value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if repeat_interval == "daily":
            target = base + timedelta(days=1)
        elif repeat_interval == "weekly":
            target = base + timedelta(days=7)
        elif repeat_interval == "yearly":
            try:
                target = base.replace(year=base.year + 1)
            except ValueError:
                target = base + timedelta(days=365)
        else:
            month = base.month + 1
            year = base.year
            if month > 12:
                month = 1
                year += 1
            day = min(base.day, 28)
            target = base.replace(year=year, month=month, day=day)
        return target.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _money(self, value):
        if isinstance(value, Decimal):
            amount = value
        else:
            amount = Decimal(str(value or "0"))
        amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return format(amount, "f")

    def _now(self):
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _respond(self, start_response, status, payload, content_type):
        if content_type == "json":
            return self._respond_json(start_response, status, payload)
        body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        headers = [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Access-Control-Allow-Headers", "Authorization, Content-Type"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Origin", "*"),
        ]
        start_response(status, headers)
        return [body]

    def _respond_json(self, start_response, status, payload):
        body = json.dumps(payload).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("Access-Control-Allow-Headers", "Authorization, Content-Type"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Origin", "*"),
        ]
        start_response(status, headers)
        return [body]


def _default_state():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    users = {
        1: {"id": 1, "first_name": "Alex", "last_name": "Owner", "email": "alex@example.com", "registration_status": "confirmed", "updated_at": now},
        2: {"id": 2, "first_name": "Sam", "last_name": "Friend", "email": "sam@example.com", "registration_status": "confirmed", "updated_at": now},
        3: {"id": 3, "first_name": "Jamie", "last_name": "Roommate", "email": "jamie@example.com", "registration_status": "confirmed", "updated_at": now},
    }
    state = {
        "current_user_id": 1,
        "users": users,
        "password_hashes": {},
        "friendships": {
            1: {2, 3},
            2: {1},
            3: {1},
        },
        "friend_requests": {},
        "groups": {
            0: {
                "id": 0,
                "name": "Non-group expenses",
                "group_type": None,
                "whiteboard": None,
                "country_code": "US",
                "created_at": now,
                "updated_at": now,
                "simplify_by_default": False,
                "member_ids": [1, 2],
                "owner_id": 1,
                "admin_ids": [],
                "archived": False,
                "deleted": False,
            },
            1: {
                "id": 1,
                "name": "Apartment",
                "group_type": "home",
                "whiteboard": "Utilities and groceries",
                "country_code": "US",
                "created_at": now,
                "updated_at": now,
                "simplify_by_default": True,
                "member_ids": [1, 2, 3],
                "owner_id": 1,
                "admin_ids": [2],
                "archived": False,
                "deleted": False,
            },
        },
        "expenses": {
            1: {
                "id": 1,
                "group_id": 1,
                "friendship_id": None,
                "expense_bundle_id": None,
                "description": "Groceries",
                "repeats": False,
                "repeat_interval": "never",
                "email_reminder": False,
                "email_reminder_in_advance": -1,
                "next_repeat": None,
                "details": "Weekly shop",
                "payment": False,
                "creation_method": None,
                "transaction_method": "offline",
                "transaction_confirmed": False,
                "cost": "36.00",
                "currency_code": "USD",
                "date": now,
                "created_at": now,
                "created_by": 1,
                "updated_at": now,
                "updated_by": 1,
                "deleted_at": None,
                "deleted_by": None,
                "category_id": 18,
                "receipt": {"original": None, "large": None},
                "user_shares": [
                    {"user_id": 1, "paid_share": "36.00", "owed_share": "12.00"},
                    {"user_id": 2, "paid_share": "0.00", "owed_share": "12.00"},
                    {"user_id": 3, "paid_share": "0.00", "owed_share": "12.00"},
                ],
                "split_equally": True,
                "split_method": "equal",
                "payers": [
                    {"user_id": 1, "paid_share": "36.00"},
                ],
                "participants": [
                    {"user_id": 1, "included": True, "split_value": "12.00"},
                    {"user_id": 2, "included": True, "split_value": "12.00"},
                    {"user_id": 3, "included": True, "split_value": "12.00"},
                ],
                "series_id": None,
                "series_root_expense_id": None,
                "parent_expense_id": None,
                "series_paused": False,
                "series_cancelled": False,
            }
        },
        "comments": {
            1: {"id": 1, "expense_id": 1, "content": "Looks good", "created_at": now, "deleted_at": None, "user_id": 2}
        },
        "expense_comments": {1: [1]},
        "notifications": [
            {
                "id": 1,
                "content": "Apartment activity is up to date",
                "type": 0,
                "created_at": now,
                "created_by": 1,
                "source_type": "Group",
                "source_id": 1,
                "visible_to_all": True,
            }
        ],
        "settlements": {},
        "categories": [
            {"id": 18, "name": "General", "subcategories": []},
            {"id": 19, "name": "Food", "subcategories": [{"id": 1901, "name": "Groceries"}]},
        ],
        "currencies": [
            {"currency_code": "USD", "unit": "$"},
            {"currency_code": "EUR", "unit": "€"},
        ],
        "oauth1_request_tokens": {},
        "next_ids": {"user": 4, "group": 2, "expense": 2, "comment": 2, "notification": 2, "friend_request": 1, "settlement": 1, "recurring_series": 1},
    }
    return state


def create_backend_app(initial_state=None):
    return SplitwiseBackendApp(initial_state=initial_state)


def main():
    host = "127.0.0.1"
    port = 8766
    app = create_backend_app()
    with make_server(host, port, app) as server:
        print("Splitwise backend listening on http://%s:%s" % (host, port))
        server.serve_forever()


if __name__ == "__main__":
    main()
