from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db import query_one, execute

@dataclass
class AuthUser(UserMixin):
    id: str
    username: str
    roles: list[str]

    @property
    def is_admin(self) -> bool:
        return 'admin' in (self.roles or [])

def _ensure_default_admin() -> None:
    """Ensure there is at least one admin user in the DB."""
    row = query_one("SELECT COUNT(*) as c FROM users")
    if not row or int(row["c"]) == 0:
        execute(
            "INSERT INTO users(username,password_hash,roles_json) VALUES(?,?,?)",
            ("admin", generate_password_hash("admin123"), json.dumps(["admin"]))
        )

def _parse_roles_from_row(row, have_roles_json: bool) -> list[str]:
    roles: list[str] = []
    if not row:
        return roles
    try:
        if have_roles_json:
            val = row["roles_json"]
            roles = json.loads(val) if val else []
            if not isinstance(roles, list):
                roles = []
        else:
            role = row["role"]
            if role:
                roles = [str(role).strip()]
    except Exception:
        roles = []
    return roles

def find_user(username: str) -> Optional[AuthUser]:
    _ensure_default_admin()
    # Prefer new schema; fall back to legacy single 'role' column
    try:
        row = query_one("SELECT id,username,roles_json FROM users WHERE username = ?", (username,))
        have_roles_json = True
    except Exception:
        row = query_one("SELECT id,username,role FROM users WHERE username = ?", (username,))
        have_roles_json = False
    if not row:
        return None
    roles = _parse_roles_from_row(row, have_roles_json)
    return AuthUser(id=str(row["id"]), username=row["username"], roles=roles)

def get_user_by_id(user_id: str) -> Optional[AuthUser]:
    if user_id is None:
        return None
    try:
        row = query_one("SELECT id,username,roles_json FROM users WHERE id = ?", (user_id,))
        have_roles_json = True
    except Exception:
        row = query_one("SELECT id,username,role FROM users WHERE id = ?", (user_id,))
        have_roles_json = False
    if not row:
        return None
    roles = _parse_roles_from_row(row, have_roles_json)
    return AuthUser(id=str(row["id"]), username=row["username"], roles=roles)

def verify_password(username: str, password: str) -> bool:
    _ensure_default_admin()
    row = query_one("SELECT password_hash FROM users WHERE username = ?", (username,))
    if not row:
        return False
    return check_password_hash(row["password_hash"], password)
