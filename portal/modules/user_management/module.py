from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.security import generate_password_hash
import json

# Import DB helpers from portal.db, regardless of module loading context
try:
    from ...db import query_all, query_one, execute
except Exception:
    from portal.db import query_all, query_one, execute  # type: ignore

bp = Blueprint("user_management", __name__, url_prefix="/users")

@bp.route("/")
@login_required
def index():
    rows = query_all("SELECT id, username, roles_json FROM users ORDER BY id ASC")
    users = []
    for r in rows:
        try:
            roles = json.loads(r["roles_json"]) if 'roles_json' in r.keys() and r["roles_json"] else ([r['role']] if 'role' in r.keys() and r['role'] else [])
            if not isinstance(roles, list):
                roles = []
        except Exception:
            roles = []
        users.append({"id": r["id"], "username": r["username"], "roles": roles})
    return render_template("user_management/index.html", users=users, title="Users")

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        roles = [x.strip() for x in (request.form.get("roles", "") or "").split(",") if x.strip()]
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("user_management.new"))
        pwh = generate_password_hash(password)
        try:
            execute("INSERT INTO users(username,password_hash,roles_json) VALUES(?,?,?)",
                    (username, pwh, json.dumps(roles)))
            flash("User created.", "success")
        except Exception as e:
            flash(f"Could not create user: {e}", "error")
            return redirect(url_for("user_management.new"))
        return redirect(url_for("user_management.index"))
    return render_template("user_management/new.html", title="New User")

@bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit(user_id: int):
    row = query_one("SELECT id,username,roles_json FROM users WHERE id = ?", (user_id,))
    if not row:
        flash("User not found.", "error")
        return redirect(url_for("user_management.index"))
    # Parse roles
    try:
        roles = json.loads(row['roles_json']) if row['roles_json'] else []
        if not isinstance(roles, list):
            roles = []
    except Exception:
        roles = []
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        roles_in = [x.strip() for x in (request.form.get("roles", "") or "").split(",") if x.strip()]
        pwd = request.form.get("password", "").strip()
        if new_username:
            execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
        execute("UPDATE users SET roles_json = ? WHERE id = ?", (json.dumps(roles_in), user_id))
        if pwd:
            pwh = generate_password_hash(pwd)
            execute("UPDATE users SET password_hash = ? WHERE id = ?", (pwh, user_id))
        flash("User updated.", "success")
        return redirect(url_for("user_management.index"))
    roles_str = ", ".join(roles or [])
    return render_template("user_management/edit.html", user={"id": row["id"], "username": row["username"]}, roles_str=roles_str, title="Edit User")

@bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
def delete(user_id: int):
    execute("DELETE FROM users WHERE id = ?", (user_id,))
    flash("User deleted.", "info")
    return redirect(url_for("user_management.index"))

def get_module():
    return {
        "name": "User Management",
        "blueprint": bp,
        "icon": "users",
        "category": "Admin",
        "visible": True,
        "route": "/users"
    }


# Expose blueprint for module discovery
blueprint = bp
