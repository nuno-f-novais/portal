from __future__ import annotations

# Ensure Werkzeug URL helpers exist before importing flask_login
from . import compat  # noqa: F401

import importlib.util, sys, os
from pathlib import Path
from flask import Flask, render_template, jsonify, g
from flask_login import LoginManager
from .settings_store import load_settings

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def discover_modules(app: Flask, *, register: bool = True):
    modules_dir = BASE_DIR / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)
    for child in sorted(modules_dir.iterdir()):
        if not child.is_dir():
            continue
        mod_file = child / "module.py"
        if not mod_file.exists():
            continue
        key = child.name  # URL prefix and settings key
        spec = importlib.util.spec_from_file_location(f"portal.modules.{key}.module", mod_file)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        # Python 3.13: register before exec, for dataclasses/typing safety
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)  # type: ignore
        bp = getattr(mod, "blueprint", None)
        if register and bp and key not in app.blueprints:
            # Attach a stable key so nav/visibility can map to settings.json
            setattr(bp, "__portal_key__", key)
            app.register_blueprint(bp, url_prefix=f"/{key}")

def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))
    from .db import init_app as init_db
    init_db(app)
    # auto_bootstrap_admin: seed default admin if none exists
    try:
        from .auth_store import _ensure_default_admin
        with app.app_context():
            _ensure_default_admin()
    except Exception:
        pass
    app.secret_key = os.environ.get("PORTAL_SECRET", "change-me")

    # Init login manager
    login_manager.init_app(app)

    # ---- Page settings from KV (safe + clamped; supports px and %) ----
    @app.context_processor
    def inject_page_settings():
        try:
            from .settings_store import get_kv
            width = (get_kv("homepage_width", "1100px") or "1100px").strip().lower()
        except Exception:
            width = "1100px"

        # Accept: "1200", "1200px", "90%"
        if width.isdigit():
            width = f"{width}px"

        if width.endswith("px"):
            try:
                n = int(width[:-2])
            except Exception:
                n = 1100
            n = max(960, min(n, 1920))   # clamp 960..1920 px
            width = f"{n}px"

        elif width.endswith("%"):
            try:
                n = int(width[:-1])
            except Exception:
                n = 100
            n = max(60, min(n, 100))     # clamp 60..100 %
            width = f"{n}%"
        else:
            width = "1100px"

        return {"HOMEPAGE_WIDTH": width}

    # Expose KV-driven page settings globally
    @app.context_processor
    def inject_page_settings():
        try:
            from .settings_store import get_kv
            width = get_kv("homepage_width", "1100px")
        except Exception:
            width = "1100px"
        return {"HOMEPAGE_WIDTH": width}

    # User loader
    @login_manager.user_loader
    def load_user(user_id: str):
        from .auth_store import get_user_by_id
        return get_user_by_id(user_id)

    # Register feature modules (includes 'auth' and your existing ones)
    discover_modules(app, register=True)

    # Compute left nav each request
    def _compute_nav():
        try:
            from .navdata import build_nav_items
            g.nav_links =  build_nav_items()
        except Exception:
            g.nav_links = []
    app.before_request(_compute_nav)

    # Register small prefs API blueprint (home layout)
    try:
        from .core.prefs_api import blueprint as prefs_api_bp
        app.register_blueprint(prefs_api_bp)
    except Exception:
        pass

    # Profile page
    try:
        from .core.profile import blueprint as profile_bp
        app.register_blueprint(profile_bp)
    except Exception:
        pass

    # Home route
    @app.route("/")
    def home():
        s = load_settings(app)
        from .navdata import build_home_modules
        return render_template("home.html", portal_items=(s.get("portal_icons") or s.get("icons") or []), home_modules=build_home_modules())

    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    return app