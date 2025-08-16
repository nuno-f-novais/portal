
from __future__ import annotations
from typing import List, Dict, Any, Set
from flask import current_app
from flask_login import current_user
from importlib import import_module
from .settings_store import load_settings
from .visibility import resolve_module_policy
from .db import get_user_home_layout

# ---- Icon resolution helpers (restores emoji/class/html support) ----

ICON_EMOJI = {
    "home": "🏠", "dashboard": "📊", "apps": "🧩", "grid": "🔲",
    "settings": "⚙️", "gear": "⚙️", "cog": "⚙️", "cogs": "⚙️", "tools": "🧰", "wrench": "🔧",
    "info": "ℹ️", "help": "❓", "question": "❓", "alert": "⚠️", "warning": "⚠️", "bug": "🐞",
    "search": "🔎", "sync": "🔄", "refresh": "🔄", "reload": "🔁", "update": "♻️",
    "power": "🔌", "start": "▶️", "play": "▶️", "pause": "⏸️", "stop": "⏹️", "restart": "🔁",
    "download": "⬇️", "upload": "⬆️", "link": "🔗", "external": "🔗", "star": "⭐",
    "user": "👤", "users": "👥", "team": "👥", "group": "👥", "profile": "👤", "account": "👤",
    "admin": "🛡️", "security": "🛡️", "shield": "🛡️", "lock": "🔒", "key": "🔑", "auth": "🔐",
    "server": "🗄️", "host": "🗄️", "compute": "🖥️", "node": "🖥️", "vm": "🖥️", "vmmanager": "🖥️",
    "cloud": "☁️", "k8s": "⛵", "kubernetes": "⛵", "docker": "🐳", "container": "📦", "pod": "📦",
    "network": "🌐", "globe": "🌐", "internet": "🌐", "world": "🌍",
    "db": "🛢️", "database": "🛢️", "sql": "🛢️", "storage": "💾", "disk": "💽", "drive": "💾",
    "folder": "📁","sticky-note": "📜", "file": "📄", "files": "📄", "docs": "📄", "document": "📄", "documents": "📄",
    "image": "🖼️", "photo": "📷", "picture": "🖼️", "video": "🎬", "music": "🎵", "audio": "🔊",
    "package": "📦", "box": "📦", "cube": "🧊",
    "logs": "📜", "log": "📜", "book": "📘", "journal": "📓",
    "monitor": "📈", "metrics": "📈", "analytics": "📊", "chart": "📊", "graph": "📈", "stats": "📈",
    "terminal": "⌨️", "console": "⌨️", "shell": "⌨️", "code": "💻", "dev": "💻",
    "puzzle": "🧩", "demo": "🧪", "beaker": "🧪", "flask": "🧪", "lab": "🧪", "test": "🧪",
    "rocket": "🚀", "deploy": "🚀",
    "mail": "✉️", "email": "✉️", "message": "✉️",
    "clock": "⏰",
}

def _bp_key(name: str, bp) -> str:
    return getattr(bp, "__portal_key__", name)

def _get_meta(bp) -> Dict[str, Any]:
    m = getattr(bp, "META", None)
    if isinstance(m, dict):
        return m
    try:
        mod_name = getattr(bp, "import_name", None)
        if mod_name:
            mod = import_module(mod_name)
            m2 = getattr(mod, "META", None)
            if isinstance(m2, dict):
                return m2
    except Exception:
        pass
    return {}

def _user_roles() -> Set[str]:
    roles: Set[str] = set(getattr(current_user, "roles", []) or [])
    legacy = getattr(current_user, "role", None)
    if legacy:
        roles.add(legacy)
    return roles

def _simple_icon_name(s: str) -> str:
    s = (s or "").strip().lower()
    if not s:
        return ""
    # If it's a full class list with spaces/colons/dashes, don't treat as a simple name
    if " " in s in s or ":" in s: # or "-"
        return ""
    return s.replace("_", "")

def _icon_from_meta(meta: Dict[str, Any]) -> Dict[str, str]:
    # 1) Raw HTML wins
    icon_html = meta.get("icon_html")
    if isinstance(icon_html, str) and icon_html.strip():
        return {"icon_html": icon_html, "icon_class": ""}

    # 2) Class or simple name
    icon_class = meta.get("icon_class") or meta.get("icon")
    if isinstance(icon_class, str) and icon_class.strip():
        simple = _simple_icon_name(icon_class)
        if simple:
            emoji = ICON_EMOJI.get(simple)
            if emoji:
                return {"icon_html": emoji, "icon_class": ""}
        # Assume it's a CSS class string
        return {"icon_html": f'<i class="{icon_class}"></i>', "icon_class": icon_class}

    # 3) Fallback
    return {"icon_html": "📦", "icon_class": ""}

# ---- Home modules ----

def build_home_modules() -> List[Dict[str, Any]]:
    app = current_app
    s = load_settings(app)
    configured: Dict[str, Dict[str, Any]] = s.get("modules") or {}
    out: List[Dict[str, Any]] = []

    for name, bp in app.blueprints.items():
        if name in ("static", "auth", "settings", "prefs_api", "profile"):
            continue
        key = _bp_key(name, bp)
        meta = _get_meta(bp)
        if meta.get("internal") or meta.get("system"):
            continue

        pol = resolve_module_policy(meta, key)
        cfg = (configured or {}).get(key) or {}
        if cfg:
            if "enabled" in cfg:        pol["enabled"] = bool(cfg.get("enabled"))
            if any(k in cfg for k in ("show_in_home","show_home","show_on_home")):
                pol["show_in_home"] = bool(cfg["show_in_home"] if "show_in_home" in cfg else (cfg["show_home"] if "show_home" in cfg else cfg.get("show_on_home")))
            if "anonymous" in cfg:      pol["anonymous"] = bool(cfg.get("anonymous"))
            if "roles" in cfg:
                try:
                    pol["roles"] = list(cfg.get("roles") or [])
                except Exception:
                    pol["roles"] = []

        if not pol.get("enabled", True):
            continue
        if not pol.get("show_in_home", True):
            continue
        if not pol.get("anonymous", False) and not getattr(current_user, "is_authenticated", False):
            continue
        req_roles = set(pol.get("roles", []) or [])
        if req_roles and _user_roles().isdisjoint(req_roles):
            continue

        label = meta.get("label") or key.replace("_", " ").title()
        desc = meta.get("description", "")
        icon_data = _icon_from_meta(meta)

        out.append({
            "key": key,
            "label": label,
            "description": desc,
            "icon": meta.get("icon", ""),
            "icon_class": meta.get("icon_class", "") if isinstance(meta.get("icon_class", ""), str) else "",
            "icon_html": icon_data.get("icon_html", ""),
            "href": f"/{key}/",
            "new_tab": False,
            "has_settings": False,
            "settings_href": "",
        })

    # User-preferred order
    try:
        uid = int(getattr(current_user, "id", 0) or 0)
    except Exception:
        uid = 0
    if uid:
        preferred = get_user_home_layout(uid)
        if preferred:
            order = {k: i for i, k in enumerate(preferred)}
            out.sort(key=lambda m: order.get(m.get("key"), 10**9))

    return out

# ---- Navigation ----

def build_nav_items() -> List[Dict[str, Any]]:
    app = current_app
    s = load_settings(app)
    items: List[Dict[str, Any]] = []

    # External quick links (portal icons) — now respect per-icon 'show_in_nav'
    for icon in (s.get("icons") or s.get("portal_icons") or []):
        try:
            enabled = bool(icon.get("enabled", True))
            shownav = bool(icon.get("show_in_nav", True))  # default True for backwards compat
            title = (icon.get("title") or "").strip()
            href = (icon.get("url") or icon.get("href") or "").strip()
            new_tab = bool(icon.get("new_tab", True))
            if not (enabled and shownav and title and href):
                continue
            items.append({"title": title, "href": href, "new_tab": new_tab})
        except Exception:
            continue

    # Registered modules
    configured: Dict[str, Dict[str, Any]] = s.get("modules") or {}
    for name, bp in app.blueprints.items():
        if name in ("static", "auth", "settings", "prefs_api", "profile"):
            continue
        key = _bp_key(name, bp)
        meta = _get_meta(bp)
        if meta.get("internal") or meta.get("system"):
            continue

        pol = resolve_module_policy(meta, key)
        cfg = (configured or {}).get(key) or {}
        if cfg:
            if "enabled" in cfg:        pol["enabled"] = bool(cfg.get("enabled"))
            if any(k in cfg for k in ("show_in_nav","show_nav","show_on_nav")):
                pol["show_in_nav"] = bool(cfg["show_in_nav"] if "show_in_nav" in cfg else (cfg["show_nav"] if "show_nav" in cfg else cfg.get("show_on_nav")))
            if "anonymous" in cfg:      pol["anonymous"] = bool(cfg.get("anonymous"))
            if "roles" in cfg:
                try:
                    pol["roles"] = list(cfg.get("roles") or [])
                except Exception:
                    pol["roles"] = []

        if not pol.get("enabled", True):
            continue
        if not pol.get("show_in_nav", True):
            continue
        if not pol.get("anonymous", False) and not getattr(current_user, "is_authenticated", False):
            continue
        req_roles = set(pol.get("roles", []) or [])
        if req_roles and _user_roles().isdisjoint(req_roles):
            continue

        items.append({"title": meta.get("label") or key.replace("_", " ").title(), "href": f"/{key}/", "new_tab": False})

    return items
