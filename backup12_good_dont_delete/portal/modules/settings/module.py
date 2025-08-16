from __future__ import annotations

from typing import Any, Dict, List
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from ...settings_store import load_settings, save_settings, list_kv, set_kv, delete_kv
from ...visibility import apply_visibility, resolve_module_policy

blueprint = Blueprint("settings", __name__)

META: Dict[str, Any] = {
    "label": "Settings",
    "description": "Admin-only: configure navigation and module visibility.",
    "icon": "gear",
    "policy": {
        "enabled": True,
        "show_in_home": False,
        "show_in_nav": False,
        "anonymous": False,
        "roles": ["admin"],
    },
}

def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "t", "yes", "y", "on"}
    return False

def _norm_roles(v: Any) -> List[str]:
    if isinstance(v, str):
        parts = [p.strip() for p in v.replace(',', ' ').split() if p.strip()]
    elif isinstance(v, (list, tuple, set)):
        parts = [str(p).strip() for p in v if str(p).strip()]
    else:
        parts = []
    return parts

@blueprint.route("/")
@login_required
def index():
    s = load_settings(current_app)

    icons_list = (s.get("portal_icons") or s.get("icons") or []) or []
    portal_icons = {}
    for idx, it in enumerate(icons_list):
        key = it.get("key") or it.get("id") or it.get("title") or f"item{idx}"
        portal_icons[str(key)] = it

    modules_rows = []
    for name, bp in current_app.blueprints.items():
        if name in ("static", "auth", "settings", "prefs_api", "profile"):
            continue
        key = getattr(bp, "__portal_key__", name)
        meta = getattr(bp, "META", {}) or {}
        if meta.get("internal") or meta.get("system"):
            continue

        pol = resolve_module_policy(meta, key)
        cfg = (s.get("modules") or {}).get(key) or {}
        if cfg:
            if "enabled" in cfg:       pol["enabled"] = _coerce_bool(cfg.get("enabled"))
            if any(k in cfg for k in ("show_in_nav", "show_nav", "show_on_nav")):
                pol["show_in_nav"] = _coerce_bool(cfg["show_in_nav"] if "show_in_nav" in cfg else (cfg["show_nav"] if "show_nav" in cfg else cfg.get("show_on_nav")))
            if any(k in cfg for k in ("show_in_home", "show_home", "show_on_home")):
                pol["show_in_home"] = _coerce_bool(cfg["show_in_home"] if "show_in_home" in cfg else (cfg["show_home"] if "show_home" in cfg else cfg.get("show_on_home")))
            if "anonymous" in cfg:     pol["anonymous"] = _coerce_bool(cfg.get("anonymous"))
            if "roles" in cfg:         pol["roles"] = _norm_roles(cfg.get("roles"))

        modules_rows.append({
            "key": key,
            "label": meta.get("label") or key,
            "description": meta.get("description", ""),
            "icon": meta.get("icon", ""),
            "enabled": bool(pol.get("enabled", True)),
            "show_in_nav": bool(pol.get("show_in_nav", True)),
            "show_in_home": bool(pol.get("show_in_home", True)),
            "anonymous": bool(pol.get("anonymous", False)),
            "roles": list(pol.get("roles") or []),
        })

    return render_template("settings/index.html", portal_icons=list(portal_icons.values()), modules=modules_rows)

@blueprint.post("/admin/save")
@login_required
def admin_save():
    data = request.get_json(force=True, silent=True) or {}
    icons_in = data.get("icons") or data.get("portal_icons") or []
    modules_in = data.get("modules") or {}

    # Normalize icons
    icons_out = []
    for it in icons_in:
        title = (it.get("title") or "").strip()
        url   = (it.get("url") or it.get("href") or "").strip()
        iconc = (it.get("icon_class") or it.get("icon") or "").strip()
        enabled = _coerce_bool(it.get("enabled", True))
        new_tab = _coerce_bool(it.get("new_tab", True))
        show_in_nav = _coerce_bool(it.get("show_in_nav", True))
        if not (title or url):
            continue
        icons_out.append({"title": title, "url": url, "icon_class": iconc, "enabled": enabled,
                          "new_tab": new_tab, "show_in_nav": show_in_nav,})

    # Normalize modules with presence-based booleans
    def _pick(d, keys, default):
        for k in keys:
            if k in d:
                return _coerce_bool(d.get(k))
        return default

    modules_out = {}
    for key, cfg in (modules_in or {}).items():
        modules_out[key] = {
            "enabled": _pick(cfg, ("enabled",), True),
            "show_in_nav": _pick(cfg, ("show_in_nav","show_nav","show_on_nav"), True),
            "show_in_home": _pick(cfg, ("show_in_home","show_home","show_on_home"), True),
            "anonymous": _pick(cfg, ("anonymous",), False),
            "roles": _norm_roles(cfg.get("roles")),
        }

    s = load_settings(current_app)
    s["portal_icons"] = icons_out
    s["icons"] = icons_out
    s["modules"] = modules_out
    save_settings(current_app, s)
    return jsonify({"ok": True})

apply_visibility(blueprint, META)


@blueprint.get("/admin/kv/list")
@login_required
def kv_list():
    data = [{"key": k, "value": v} for (k, v) in list_kv()]
    return jsonify({"items": data})

@blueprint.post("/admin/kv/save")
@login_required
def kv_save():
    data = request.get_json(force=True, silent=True) or {}
    items = data.get("items") or []
    deleted = set(data.get("deleted") or [])
    for it in items:
        key = (it.get("key") or "").strip()
        if not key or key in deleted:
            continue
        value = it.get("value")
        set_kv(key, "" if value is None else str(value))
    for key in deleted:
        delete_kv(str(key))
    return jsonify({"ok": True})
