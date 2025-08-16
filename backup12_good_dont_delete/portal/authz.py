from __future__ import annotations
from typing import List
from flask_login import current_user

def roles_of(user=None) -> List[str]:
    """Return normalized roles list (requires user.roles iterable)."""
    if user is None:
        user = current_user
    r = getattr(user, 'roles', None)
    if not r:
        return []
    if isinstance(r, (list, tuple, set)):
        roles = [str(x).strip().lower() for x in r]
    else:
        roles = []
    seen = set(); out: List[str] = []
    for x in roles:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

def is_admin(user=None) -> bool:
    return 'admin' in roles_of(user)
