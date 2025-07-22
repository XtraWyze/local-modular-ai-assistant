"""Basic in-memory user authentication."""

import json
import os

USERS_FILE = "users.json"

__all__ = ["load_users", "authenticate", "add_user"]

_users = None


def load_users():
    global _users
    if _users is None:
        if os.path.isfile(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                _users = json.load(f)
        else:
            _users = {}
    return _users


def authenticate(username: str, password: str) -> bool:
    users = load_users()
    return users.get(username) == password


def add_user(username: str, password: str):
    users = load_users()
    users[username] = password
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)


def get_description() -> str:
    return "Handles simple username/password authentication for profiles."
