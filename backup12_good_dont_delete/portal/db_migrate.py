from __future__ import annotations

def ensure_users_roles_column():
    """Ensure the users table has a 'roles' TEXT column and migrate data.

    - Adds roles TEXT column if missing.
    - If legacy 'role' column exists, copies its values into 'roles' (CSV).
    - Idempotent; safe to call on every startup.
    """
    try:
        from .db import get_db
        db = get_db()
        cur = db.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        if 'roles' not in cols:
            db.execute("ALTER TABLE users ADD COLUMN roles TEXT DEFAULT ''")
            db.commit()
            cur = db.execute("PRAGMA table_info(users)")
            cols = [r[1] for r in cur.fetchall()]
        if 'role' in cols:
            db.execute("UPDATE users SET roles = COALESCE(role, roles) WHERE (roles IS NULL OR roles = '') AND role IS NOT NULL")
            db.commit()
    except Exception:
        # Never block app start on migration; prefer empty roles
        pass
