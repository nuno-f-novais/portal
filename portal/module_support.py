from __future__ import annotations
from functools import wraps
from flask import abort
from flask_login import current_user

def _is_admin_user() -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    # Direct boolean flag
    if getattr(current_user, "is_admin", False):
        return True
    # String role field (e.g., "admin" or "admin,user")
    role = str(getattr(current_user, "role", "") or "").lower()
    if role == "admin":
        return True
    try:
        parts = [p.strip() for p in role.split(",") if p.strip()]
        if "admin" in parts:
            return True
    except Exception:
        pass
    return False

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _is_admin_user():
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

def register_module_settings(blueprint, *, view_func, endpoint: str = "settings"):
    """Register an admin-only /settings route for a module blueprint.

    Usage inside a module package:
        from ...module_support import register_module_settings

        META = { ..., 'has_settings': True }

        def my_settings(): ...

        register_module_settings(blueprint, view_func=my_settings)
    """
    view = admin_required(view_func)
    blueprint.add_url_rule('/settings', endpoint=endpoint, view_func=view, methods=['GET', 'POST'])
