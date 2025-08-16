from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ...auth_store import find_user, verify_password

blueprint = Blueprint("auth", __name__)

@blueprint.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("settings.index") if "settings" in url_for("settings.index") else "/")
    return render_template("auth/login.html", title="Sign in")

@blueprint.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    remember = bool(request.form.get("remember"))
    if not username or not password:
        flash("Missing username or password.", "error")
        return redirect(url_for("auth.login"))
    if not verify_password(username, password):
        flash("Invalid credentials.", "error")
        return redirect(url_for("auth.login"))
    user = find_user(username)
    login_user(user, remember=remember)
    next_url = request.args.get("next") or "/"
    return redirect(next_url)

@blueprint.get("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("auth.login"))
