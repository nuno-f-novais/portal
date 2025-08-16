
from __future__ import annotations
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from ..db import get_user_home_layout, save_user_home_layout

blueprint = Blueprint("prefs_api", __name__)

@blueprint.get("/api/home-layout")
@login_required
def get_home_layout():
    try:
        uid = int(getattr(current_user, "id", 0))
    except Exception:
        uid = 0
    # Build default order if none saved
    from ..navdata import build_home_modules
    default_order = [m["key"] for m in build_home_modules()]
    order = get_user_home_layout(uid) if uid else []
    if not order:
        order = default_order
    # Filter to currently valid keys only
    valid = set(default_order)
    order = [k for k in order if k in valid]
    return jsonify({"order": order})

@blueprint.post("/api/home-layout")
@login_required
def save_home_layout():
    data = request.get_json(silent=True) or {}
    order = data.get("order") or []
    if not isinstance(order, list):
        return jsonify({"ok": False, "error": "Invalid payload"}), 400

    # Only allow currently visible home modules
    from ..navdata import build_home_modules
    valid_keys = {m["key"] for m in build_home_modules()}
    cleaned = []
    for k in order:
        if isinstance(k, str) and k in valid_keys and k not in cleaned:
            cleaned.append(k)

    try:
        uid = int(getattr(current_user, "id", 0))
    except Exception:
        uid = 0
    if not uid:
        return jsonify({"ok": False, "error": "Not authenticated"}), 401

    save_user_home_layout(uid, cleaned)
    return jsonify({"ok": True})
