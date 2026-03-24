import json
import logging
import os
from threading import Lock
from urllib.parse import quote

import requests

LOGGER = logging.getLogger(__name__)

DEFAULT_PERSISTENCE_DIR = os.path.expanduser("~/.local/state/splitwise-clone-1")
DEFAULT_PERSISTENCE_KEY_PREFIX = "splitwise-clone-1"


class PersistenceStore(object):
    def __init__(self, environment=None):
        self.environment = environment or os.environ
        self.storage_dir = self.environment.get("SPLITWISE_PERSISTENCE_DIR", DEFAULT_PERSISTENCE_DIR)
        self.key_prefix = self.environment.get("SPLITWISE_PERSISTENCE_KEY_PREFIX", DEFAULT_PERSISTENCE_KEY_PREFIX)
        self.kv_url = (self.environment.get("KV_REST_API_URL") or "").rstrip("/")
        self.kv_token = self.environment.get("KV_REST_API_TOKEN") or ""
        self._lock = Lock()

    def load_state(self):
        data = self._load_payload("state")
        if not data:
            return None
        return self._normalize_state(data)

    def save_state(self, state):
        return self._save_payload("state", self._serialize_state(state))

    def load_sessions(self):
        data = self._load_payload("sessions")
        if not data:
            return {}
        if not isinstance(data, dict):
            return {}
        return {str(key): value for key, value in data.items() if isinstance(value, dict)}

    def save_sessions(self, sessions):
        return self._save_payload("sessions", dict(sessions))

    def _load_payload(self, name):
        if self.kv_url and self.kv_token:
            payload = self._load_from_kv(name)
            if payload is not None:
                return payload
        return self._load_from_file(name)

    def _save_payload(self, name, payload):
        saved = False
        if self.kv_url and self.kv_token:
            saved = self._save_to_kv(name, payload)
        file_saved = self._save_to_file(name, payload)
        return saved or file_saved

    def _file_path(self, name):
        return os.path.join(self.storage_dir, "%s.json" % name)

    def _kv_key(self, name):
        return "%s:%s" % (self.key_prefix, name)

    def _load_from_file(self, name):
        path = self._file_path(name)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as handle:
                return json.load(handle)
        except (OSError, ValueError, TypeError):
            LOGGER.exception("Unable to load persisted %s from %s", name, path)
            return None

    def _save_to_file(self, name, payload):
        path = self._file_path(name)
        directory = os.path.dirname(path)
        try:
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            temp_path = path + ".tmp"
            with self._lock:
                with open(temp_path, "w") as handle:
                    json.dump(payload, handle, sort_keys=True)
                os.replace(temp_path, path)
            return True
        except OSError:
            LOGGER.exception("Unable to save persisted %s to %s", name, path)
            return False

    def _load_from_kv(self, name):
        try:
            response = requests.get(
                "%s/get/%s" % (self.kv_url, quote(self._kv_key(name), safe="")),
                headers={"Authorization": "Bearer %s" % self.kv_token},
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json().get("result")
            if payload in (None, ""):
                return None
            if isinstance(payload, str):
                return json.loads(payload)
            return payload
        except (requests.RequestException, ValueError, TypeError):
            LOGGER.exception("Unable to load persisted %s from KV", name)
            return None

    def _save_to_kv(self, name, payload):
        try:
            response = requests.post(
                "%s/set/%s" % (self.kv_url, quote(self._kv_key(name), safe="")),
                headers={
                    "Authorization": "Bearer %s" % self.kv_token,
                    "Content-Type": "application/json",
                },
                json={"value": json.dumps(payload, sort_keys=True)},
                timeout=5,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            LOGGER.exception("Unable to save persisted %s to KV", name)
            return False

    def _serialize_state(self, state):
        return {
            "current_user_id": state.get("current_user_id"),
            "users": self._int_keyed_dict(state.get("users", {})),
            "password_hashes": self._int_keyed_dict(state.get("password_hashes", {})),
            "friendships": {
                str(key): sorted(value)
                for key, value in state.get("friendships", {}).items()
            },
            "friend_requests": self._int_keyed_dict(state.get("friend_requests", {})),
            "groups": self._int_keyed_dict(state.get("groups", {})),
            "expenses": self._int_keyed_dict(state.get("expenses", {})),
            "comments": self._int_keyed_dict(state.get("comments", {})),
            "expense_comments": {
                str(key): list(value)
                for key, value in state.get("expense_comments", {}).items()
            },
            "notifications": list(state.get("notifications", [])),
            "settlements": self._int_keyed_dict(state.get("settlements", {})),
            "categories": list(state.get("categories", [])),
            "currencies": list(state.get("currencies", [])),
            "oauth1_request_tokens": dict(state.get("oauth1_request_tokens", {})),
            "next_ids": dict(state.get("next_ids", {})),
        }

    def _normalize_state(self, raw_state):
        state = {
            "current_user_id": raw_state.get("current_user_id", 1),
            "users": self._restore_int_keyed_dict(raw_state.get("users", {})),
            "password_hashes": self._restore_int_keyed_dict(raw_state.get("password_hashes", {})),
            "friendships": {
                int(key): set(value if value is not None else [])
                for key, value in raw_state.get("friendships", {}).items()
            },
            "friend_requests": self._restore_int_keyed_dict(raw_state.get("friend_requests", {})),
            "groups": self._restore_int_keyed_dict(raw_state.get("groups", {})),
            "expenses": self._restore_int_keyed_dict(raw_state.get("expenses", {})),
            "comments": self._restore_int_keyed_dict(raw_state.get("comments", {})),
            "expense_comments": {
                int(key): [int(item) for item in (value if value is not None else [])]
                for key, value in raw_state.get("expense_comments", {}).items()
            },
            "notifications": list(raw_state.get("notifications", [])),
            "settlements": self._restore_int_keyed_dict(raw_state.get("settlements", {})),
            "categories": list(raw_state.get("categories", [])),
            "currencies": list(raw_state.get("currencies", [])),
            "oauth1_request_tokens": dict(raw_state.get("oauth1_request_tokens", {})),
            "next_ids": dict(raw_state.get("next_ids", {})),
        }
        state["friendships"].setdefault(int(state.get("current_user_id", 1)), set())
        state["next_ids"].setdefault("recurring_series", 1)
        return state

    def _int_keyed_dict(self, value):
        return {str(key): item for key, item in value.items()}

    def _restore_int_keyed_dict(self, value):
        return {int(key): item for key, item in value.items()}
