from __future__ import annotations
from typing import Any
from flask import g

def _compute_nav():
    try:
        from ..navdata import build_nav_items
        g.nav_links = build_nav_items()
    except Exception:
        g.nav_links = []

# The function Flask will register when using:
#   app.before_request(nav_middleware.before_request)
def before_request():
    _compute_nav()

def install(app: Any):
    """Idempotently attach the before_request hook to the app."""
    if getattr(app, "_portal_nav_installed", False):
        return app
    app.before_request(before_request)
    setattr(app, "_portal_nav_installed", True)
    return app

class _NavMiddleware:
    """Callable object AND attribute-based hook for maximum compatibility."""
    def __call__(self, app: Any):
        return install(app)

# Exported symbol used by legacy code:
nav_middleware = _NavMiddleware()
# Also expose the function attribute for: app.before_request(nav_middleware.before_request)
nav_middleware.before_request = before_request  # type: ignore[attr-defined]
