
from __future__ import annotations
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from ...module_support import register_module_settings
from ...db import _meta_get, _meta_set

blueprint = Blueprint("some_module", __name__)

META = {
    "label": "Some Module",
    "description": "Example module that includes its own settings page.",
    "icon": "puzzle",
    "visibility": {"enabled": True, "show_in_home": True, "show_in_nav": False, "anonymous": False},
    "has_settings": True,
}

SETTINGS_KEY = "some_module.settings"  # stored in meta table as JSON string (here we keep it simple)

def get_settings() -> dict:
    import json
    raw = _meta_get(SETTINGS_KEY) or "{}"
    try:
        data = json.loads(raw)
    except Exception:
        data = {}
    # defaults
    data.setdefault("message", "Hello from Some Module!")
    return data

def save_settings(data: dict) -> None:
    import json
    _meta_set(SETTINGS_KEY, json.dumps(data))

@blueprint.route("/")
@login_required
def index():
    s = get_settings()
    return render_template("index.html", title="Some Module", settings=s)

def settings_view():
    s = get_settings()
    if request.method == "POST":
        message = (request.form.get("message") or "").strip() or "Hello from Some Module!"
        s["message"] = message
        save_settings(s)
        flash("Settings saved", "success")
        return redirect(url_for("some_module.settings"))
    return render_template("settings.html", title="Some Module Settings", settings=s)

# Register /some_module/settings (admin-only via helper)
register_module_settings(blueprint, view_func=settings_view)
