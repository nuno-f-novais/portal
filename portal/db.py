from __future__ import annotations
import sqlite3, json, os
from pathlib import Path
from typing import Any, Iterable, Optional
from flask import g

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "portal.db"

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_db() -> sqlite3.Connection:
    conn = getattr(g, "_portal_db", None)
    if conn is None:
        conn = g._portal_db = _connect()
    return conn

def close_db(e: Optional[BaseException] = None):
    conn = getattr(g, "_portal_db", None)
    if conn is not None:
        conn.close()
        g._portal_db = None

def execute(sql: str, params: Iterable[Any] = ()):
    db = get_db()
    cur = db.execute(sql, tuple(params))
    db.commit()
    return cur

def query_all(sql: str, params: Iterable[Any] = ()):
    cur = get_db().execute(sql, tuple(params))
    return cur.fetchall()

def query_one(sql: str, params: Iterable[Any] = ()):
    cur = get_db().execute(sql, tuple(params))
    return cur.fetchone()

def init_schema():
    
    execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        roles_json TEXT
    )""")
    execute("""CREATE TABLE IF NOT EXISTS portal_icons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        icon_class TEXT,
        enabled INTEGER DEFAULT 1,
        show_in_nav INTEGER DEFAULT 0,
        show_in_home INTEGER DEFAULT 0
    )""")
    execute("""CREATE TABLE IF NOT EXISTS module_settings (
        module_key TEXT PRIMARY KEY,
        enabled INTEGER DEFAULT 1,
        show_in_nav INTEGER DEFAULT 0,
        show_in_home INTEGER DEFAULT 0,
        anonymous INTEGER DEFAULT 0,
        roles_json TEXT
    )""")
    execute("""CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    # Per-user saved Home layout
    execute("""CREATE TABLE IF NOT EXISTS user_home_layouts (
        user_id INTEGER PRIMARY KEY,
        layout_json TEXT NOT NULL,
        updated_at TEXT
    )""")


def _meta_get(key: str) -> Optional[str]:
    row = query_one("SELECT value FROM meta WHERE key = ?", (key,))
    return row["value"] if row else None

def _meta_set(key: str, value: str):
    execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

def migrate_from_json_if_needed():
    settings_json = (BASE_DIR / "data" / "settings.json")
    if settings_json.exists() and not _meta_get("settings_imported"):
        try:
            data = json.loads(settings_json.read_text(encoding="utf-8") or "{}")
        except Exception:
            data = {}
        icons = data.get("portal_icons") or []
        modules = data.get("modules") or {}
        execute("DELETE FROM portal_icons")
        execute("DELETE FROM module_settings")
        for it in icons:
            title = (it.get("title") or it.get("label") or "Link")
            url   = (it.get("url") or it.get("href") or "#")
            iconc = (it.get("icon_class") or it.get("icon") or "")
            enabled = 1 if it.get("enabled", True) else 0
            show_nav  = 1 if (it.get("show_in_nav") or it.get("show_on_nav") or it.get("show_nav")) else 0
            show_home = 1 if (it.get("show_in_home") or it.get("show_on_home") or it.get("show_home")) else 0
            execute("INSERT INTO portal_icons(title,url,icon_class,enabled,show_in_nav,show_in_home) VALUES(?,?,?,?,?,?)",
                    (title, url, iconc, enabled, show_nav, show_home))
        for key, cfg in (modules or {}).items():
            enabled = 1 if cfg.get("enabled", True) else 0
            show_nav  = 1 if (cfg.get("show_in_nav") or cfg.get("show_on_nav") or cfg.get("show_nav")) else 0
            show_home = 1 if (cfg.get("show_in_home") or cfg.get("show_on_home") or cfg.get("show_home")) else 0
            anonymous = 1 if cfg.get("anonymous", False) else 0
            roles = cfg.get("roles") or []
            try:
                roles_json = json.dumps(roles)
            except Exception:
                roles_json = "[]"
            execute("INSERT INTO module_settings(module_key,enabled,show_in_nav,show_in_home,anonymous,roles_json) VALUES(?,?,?,?,?,?)",
                    (key, enabled, show_nav, show_home, anonymous, roles_json))
        _meta_set("settings_imported", "1")

    users_json = (BASE_DIR / "data" / "users.json")
    if users_json.exists() and not _meta_get("users_imported"):
        try:
            udata = json.loads(users_json.read_text(encoding="utf-8") or "{}")
        except Exception:
            udata = {}
        row = query_one("SELECT COUNT(*) as c FROM users")
        empty = (row["c"] == 0) if row else True
        if empty:
            for uname, rec in (udata or {}).items():
                username = rec.get("username") or uname
                role = rec.get("role") or "admin"
                pwh = rec.get("password_hash") or ""
                if username and pwh:
                    execute("INSERT INTO users(username,password_hash,roles_json) VALUES(?,?,?)", (username, pwh, json.dumps(["admin"])))
        _meta_set("users_imported", "1")

def _ensure_user_home_table():
    try:
        execute("SELECT 1 FROM user_home_layouts LIMIT 1")
    except Exception:
        try:
            execute("""CREATE TABLE IF NOT EXISTS user_home_layouts (
                user_id INTEGER PRIMARY KEY,
                layout_json TEXT NOT NULL,
                updated_at TEXT
            )""")
        except Exception:
            pass


# --- User Home Layout helpers ---
def get_user_home_layout(user_id: int) -> list[str]:
    row = query_one("SELECT layout_json FROM user_home_layouts WHERE user_id = ?", (user_id,))
    if not row:
        return []
    try:
        data = json.loads(row["layout_json"] or "[]")
        return [str(k) if not isinstance(k, str) else k for k in data]
    except Exception:
        return []

def save_user_home_layout(user_id: int, order: list[str]) -> None:
    js = json.dumps(list(dict.fromkeys(order)))  # de-dup while preserving order
    try:
        execute(
            "INSERT INTO user_home_layouts(user_id, layout_json, updated_at) "
            "VALUES (?, ?, datetime('now')) "
            "ON CONFLICT(user_id) DO UPDATE SET layout_json=excluded.layout_json, updated_at=datetime('now')",
            (user_id, js),
        )
    except Exception:
        # Fallback for SQLite without ON CONFLICT DO UPDATE support
        existing = query_one("SELECT 1 FROM user_home_layouts WHERE user_id = ?", (user_id,))
        if existing:
            execute("UPDATE user_home_layouts SET layout_json = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (js, user_id))
        else:
            execute("INSERT OR REPLACE INTO user_home_layouts(user_id, layout_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (user_id, js))




def ensure_roles_json_column():
    """Add roles_json column to users if missing, and migrate existing 'role' values."""
    try:
        cols = [r["name"] for r in query_all("PRAGMA table_info(users)")]
    except Exception:
        return
    if "roles_json" not in cols:
        # Add new column
        execute("ALTER TABLE users ADD COLUMN roles_json TEXT")
        cols = [r["name"] for r in query_all("PRAGMA table_info(users)")]
    # Migrate existing 'role' into roles_json if role column exists and roles_json rows are null
    if "role" in cols:
        rows = query_all("SELECT id, role, roles_json FROM users")
        for r in rows:
            if r["roles_json"]:
                continue
            role = r["role"]
            try:
                import json as _json
                roles_json = _json.dumps([role] if role else [])
            except Exception:
                roles_json = None
            execute("UPDATE users SET roles_json = ? WHERE id = ?", (roles_json, r["id"]))




def ensure_kv_bootstrap_defaults():
    """Ensure the 'settings' table exists and seed default key/value pairs if missing.
    This is safe to call repeatedly (idempotent). Add new default keys to DEFAULT_KV below.
    """
    # Ensure table
    execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    # Define bootstrap defaults here
    DEFAULT_KV = {
        "homepage_width": "1100px",
        # add future defaults here, e.g. "brand_primary": "#0d6efd"
    }
    for k, v in DEFAULT_KV.items():
        row = query_one("SELECT value FROM settings WHERE key = ?", (k,))
        if not row:
            try:
                # Try modern upsert-do-nothing on conflict
                execute("INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO NOTHING", (k, v))
            except Exception:
                # Fallback: only insert if truly missing
                execute("INSERT INTO settings(key, value) VALUES(?, ?)", (k, v))

def init_app(app):
    # Run schema+migration inside an application context so 'g' is available.
    with app.app_context():
        init_schema()
        ensure_kv_bootstrap_defaults()
        ensure_roles_json_column()
        migrate_from_json_if_needed()
    # Ensure connections are cleaned up after each request
    app.teardown_appcontext(close_db)
