from __future__ import annotations
from typing import Dict, Any, Set
from flask import abort
from flask_login import current_user

# Keep ALL legacy keys so old code never KeyErrors
DEFAULT_POLICY: Dict[str, Any] = {
    "enabled": True,       # legacy flag used by older modules
    "visible": True,       # synonym used elsewhere
    "show_in_nav": True,   # whether to show in top/side nav
    "show_in_home": True,  # whether to show on home grid
    "anonymous": False,    # allow anonymous users?
    "roles": [],           # list[str] of allowed roles; [] => any authed user (if anonymous==False)
}

# accept optional/ignored extra positional args for back-compat (e.g., module key)
def resolve_module_policy(meta: Dict[str, Any] | None, *_unused) -> Dict[str, Any]:
    """Normalize module meta into a full policy dict."""
    policy: Dict[str, Any] = dict(DEFAULT_POLICY)
    if meta:
        pol = meta.get("policy") or {}
        if isinstance(pol, dict):
            policy.update(pol)

    # Normalize synonyms & fill any missing keys
    if "enabled" not in policy:
        policy["enabled"] = bool(policy.get("visible", True))
    if "visible" not in policy:
        policy["visible"] = bool(policy.get("enabled", True))
    if "show_in_nav" not in policy:
        policy["show_in_nav"] = bool(policy.get("visible", True))
    if "show_in_home" not in policy:
        policy["show_in_home"] = bool(policy.get("enabled", policy.get("visible", True)))

    return policy

def apply_visibility(bp, policy: Dict[str, Any] | None) -> None:
    """Attach a before_request guard enforcing policy."""
    # Normalize the dict we were passed (may be just the policy sub-dict)
    pol: Dict[str, Any] = resolve_module_policy({"policy": policy or {}}, None)

    @bp.before_request
    def _guard():
        # Completely hide module if disabled or not visible
        if not pol.get("enabled", True) or not pol.get("visible", True):
            abort(404)

        # Require auth unless anonymous explicitly allowed
        if not pol.get("anonymous", False) and not getattr(current_user, "is_authenticated", False):
            abort(401)

        # Role-based restriction: accept roles list and legacy single 'role'
        roles_required: Set[str] = set(pol.get("roles", []) or [])
        if roles_required:
            user_roles: Set[str] = set(getattr(current_user, "roles", []) or [])
            legacy = getattr(current_user, "role", None)
            if legacy:
                user_roles.add(legacy)
            if user_roles.isdisjoint(roles_required):
                abort(403)

        return None
