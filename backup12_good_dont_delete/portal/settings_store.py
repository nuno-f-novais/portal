from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple
from .db import get_db, query_one, execute

# Persist portal settings as one JSON blob under key 'portal_settings' in settings table.
# Back-compat: returns BOTH 'portal_icons' and 'icons'. Accepts either on save.

DEFAULTS: Dict[str, Any] = {
    "portal_icons": [],
    "icons": [],
    "modules": {},
}

def _ensure_table() -> None:
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    db.commit()

def _get(key: str) -> str | None:
    _ensure_table()
    row = query_one("SELECT value FROM settings WHERE key = ?", (key,))
    if not row:
        return None
    try:
        return row["value"]
    except Exception:
        try:
            return row[0]  # type: ignore[index]
        except Exception:
            return None

def _set(key: str, value: str) -> None:
    _ensure_table()
    # Try modern upsert; fallback if SQLite too old
    try:
        execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    except Exception:
        db = get_db()
        cur = db.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
        if cur.rowcount == 0:
            db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
        db.commit()

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

def _pick_bool(d: Dict[str, Any], keys: Tuple[str, ...], default: bool) -> bool:
    # Respect explicit False; only use default if key is absent
    for k in keys:
        if k in d:
            return _coerce_bool(d.get(k))
    return default

def load_settings(app) -> Dict[str, Any]:
    raw = _get("portal_settings")
    if not raw:
        return dict(DEFAULTS)

    try:
        data = json.loads(raw) if isinstance(raw, (bytes, bytearray)) else json.loads(str(raw))
    except Exception:
        return dict(DEFAULTS)

    icons_in = (data.get("portal_icons") or data.get("icons") or []) or []
    norm_icons: List[Dict[str, Any]] = []
    for it in icons_in:
        if not isinstance(it, dict):
            continue
        norm_icons.append({
            "title": (it.get("title") or "").strip(),
            "url": (it.get("url") or it.get("href") or "").strip(),
            "icon_class": (it.get("icon_class") or it.get("icon") or "").strip(),
            "enabled": _coerce_bool(it.get("enabled", True)),
            "new_tab": _coerce_bool(it.get("new_tab", True)),
            "show_in_nav": _coerce_bool(it.get("show_in_nav", True)),
        })

    modules_in = data.get("modules") or {}
    if not isinstance(modules_in, dict):
        modules_in = {}
    modules_out: Dict[str, Dict[str, Any]] = {}
    for key, cfg in modules_in.items():
        if not isinstance(cfg, dict):
            continue
        cfg = dict(cfg)
        modules_out[str(key)] = {
            "enabled": _pick_bool(cfg, ("enabled",), True),
            "show_in_nav": _pick_bool(cfg, ("show_in_nav","show_nav","show_on_nav"), True),
            "show_in_home": _pick_bool(cfg, ("show_in_home","show_home","show_on_home"), True),
            "anonymous": _pick_bool(cfg, ("anonymous",), False),
            "roles": _norm_roles(cfg.get("roles")),
        }

    return {"portal_icons": norm_icons, "icons": norm_icons, "modules": modules_out}

def save_settings(app, data: Dict[str, Any]) -> Dict[str, Any]:
    icons_in = (data.get("portal_icons") or data.get("icons") or []) or []
    modules_in = data.get("modules") or {}

    norm_icons: List[Dict[str, Any]] = []
    for it in icons_in:
        if not isinstance(it, dict):
            continue
        title = (it.get("title") or "").strip()
        url = (it.get("url") or it.get("href") or "").strip()
        icon_class = (it.get("icon_class") or it.get("icon") or "").strip()
        if not title and not url:
            continue
        norm_icons.append({
            "title": title,
            "url": url,
            "icon_class": icon_class,
            "enabled": _coerce_bool(it.get("enabled", True)),
            "new_tab": _coerce_bool(it.get("new_tab", True)),
            "show_in_nav": _coerce_bool(it.get("show_in_nav", True)),
        })

    modules_out: Dict[str, Dict[str, Any]] = {}
    if isinstance(modules_in, dict):
        for key, cfg in modules_in.items():
            if not isinstance(cfg, dict):
                continue
            cfg = dict(cfg)
            modules_out[str(key)] = {
                "enabled": _pick_bool(cfg, ("enabled",), True),
                "show_in_nav": _pick_bool(cfg, ("show_in_nav","show_nav","show_on_nav"), True),
                "show_in_home": _pick_bool(cfg, ("show_in_home","show_home","show_on_home"), True),
                "anonymous": _pick_bool(cfg, ("anonymous",), False),
                "roles": _norm_roles(cfg.get("roles")),
            }

    payload = {"portal_icons": norm_icons, "icons": norm_icons, "modules": modules_out}
    _set("portal_settings", json.dumps(payload))
    return payload


# ---------- Generic Key/Value helpers (share the same 'settings' table) ----------

RESERVED_KEYS = {"portal_settings"}

def list_kv() -> list[tuple[str, str]]:
    _ensure_table()
    rows = get_db().execute("SELECT key, value FROM settings WHERE key NOT IN ({}) ORDER BY key".format(
        ",".join("?" for _ in RESERVED_KEYS)), tuple(RESERVED_KEYS)).fetchall()
    out: list[tuple[str, str]] = []
    for r in rows:
        try:
            k = r["key"]
            v = r["value"]
        except Exception:
            k, v = r[0], r[1]
        out.append((str(k), "" if v is None else str(v)))
    return out

def set_kv(key: str, value: str) -> None:
    key = (key or "").strip()
    if not key or key in RESERVED_KEYS:
        return
    _set(key, value or "")

def delete_kv(key: str) -> None:
    key = (key or "").strip()
    if not key or key in RESERVED_KEYS:
        return
    _ensure_table()
    execute("DELETE FROM settings WHERE key = ?", (key,))


def get_kv(key: str, default: str | None = None) -> str | None:
    """Return value for a key from the 'settings' table, or default if missing."""
    try:
        v = _get(key)
    except Exception:
        v = None
    return v if v is not None else default
