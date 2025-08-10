from enum import Enum
from typing import Dict

from fastapi import Depends, HTTPException, Header, status


class Role(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    BOOKKEEPER = "bookkeeper"
    CLIENT = "client"


# In-memory store for user roles. Pre-populate an admin user so that
# tests and first-time setup have an administrator available.
user_roles: Dict[str, Role] = {"admin": Role.ADMIN}


async def get_current_role(x_user: str | None = Header(default=None)) -> Role:
    """Fetch the role for the current user from the X-User header."""
    if x_user is None or x_user not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown user",
        )
    return user_roles[x_user]


def role_required(*allowed: Role):
    async def _dep(role: Role = Depends(get_current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return role

    return _dep
