# portal/core/__init__.py
"""Compatibility shims for legacy imports under portal.core."""
from .nav_middleware import nav_middleware  # noqa: F401

# Keep bootstrap available if present
try:
    from .bootstrap import wipe_and_seed  # noqa: F401
except Exception:
    pass
