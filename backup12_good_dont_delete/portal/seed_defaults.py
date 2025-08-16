import json
from .db import query_one, execute

def bootstrap_defaults():
    row = query_one("SELECT COUNT(*) as c FROM users")
    if row and int(row["c"]) == 0:
        username = "admin"
        password_hash = "$pbkdf2-sha256$placeholder"  # will be overwritten by auth module if used elsewhere
        try:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash("admin123")
        except Exception:
            pass
        execute("INSERT INTO users(username,password_hash,roles_json) VALUES(?,?,?)",
                (username, password_hash, json.dumps(["admin"])))
        print("Seeded default admin: admin / admin123")
