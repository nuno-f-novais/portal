
from __future__ import annotations
from flask import Blueprint, render_template
from flask_login import login_required, current_user

blueprint = Blueprint("profile", __name__)

@blueprint.get("/profile")
@login_required
def profile_page():
    role_str = (getattr(current_user, "role", "") or "")
    roles_list = getattr(current_user, "roles", None)
    if isinstance(roles_list, str):
        roles_list = [p.strip() for p in roles_list.split(",") if p.strip()]
    elif not isinstance(roles_list, (list, tuple, set)):
        roles_list = []
    is_admin_flag = bool(getattr(current_user, "is_admin", False))
    is_admin_str = "admin" in (role_str or "").lower()
    is_admin_list = "admin" in [str(x).lower() for x in roles_list]
    is_admin_effective = is_admin_flag or is_admin_str or is_admin_list

    user_info = {
        "id": getattr(current_user, "id", None),
        "username": getattr(current_user, "username", None) or getattr(current_user, "name", None),
        "email": getattr(current_user, "email", None),
        "role": role_str,
        "roles": roles_list,
        "is_authenticated": getattr(current_user, "is_authenticated", False),
        "is_admin": is_admin_flag,
        "admin_via_role_string": is_admin_str,
        "admin_via_roles_list": is_admin_list,
        "admin_effective": is_admin_effective,
    }
    return render_template("profile.html", title="Your Profile", user_info=user_info)
