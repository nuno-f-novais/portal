from __future__ import annotations
import os
from ..db import execute, query_one, init_schema, migrate_from_json_if_needed
from ..auth_store import _ensure_default_admin

def _truncate(table: str):
    execute(f"DELETE FROM {table}")

def wipe_and_seed(use_json: bool = True, keep_users: bool = True) -> dict:
    """Dev helper compatible with legacy code.

    - If PORTAL_WIPE=1 (or truthy) in the environment, it **clears** settings tables
      (and optionally users) before seeding.
    - Otherwise, it only ensures schema, runs one-time JSON migration if present,
      and guarantees there's an admin/admin user.

    Args:
        use_json: when wiping, re-import from portal/data/settings.json and users.json if present.
        keep_users: when wiping, keep existing users table content if True.

    Returns:
        Dict with basic counts after the operation.
    """
    init_schema()

    do_wipe = os.environ.get("PORTAL_WIPE", "").strip() not in ("", "0", "false", "False")
    if do_wipe:
        _truncate("portal_icons")
        _truncate("module_settings")
        _truncate("meta")
        if not keep_users:
            _truncate("users")

    if use_json:
        migrate_from_json_if_needed()

    # Always ensure at least one admin user exists
    _ensure_default_admin()

    # Return quick stats
    row_icons = query_one("SELECT COUNT(*) as c FROM portal_icons")
    row_mods  = query_one("SELECT COUNT(*) as c FROM module_settings")
    row_users = query_one("SELECT COUNT(*) as c FROM users")
    return {
        "icons": (row_icons["c"] if row_icons else 0),
        "modules": (row_mods["c"] if row_mods else 0),
        "users": (row_users["c"] if row_users else 0),
        "wiped": bool(do_wipe),
    }
