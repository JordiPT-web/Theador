from enum import Enum
from typing import Dict, Tuple

from fastapi import Depends, HTTPException, Header, status


class Role(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    BOOKKEEPER = "bookkeeper"
    CLIENT = "client"


# In-memory store for user roles. Pre-populate an admin user so that
# tests and first-time setup have an administrator available.
user_roles: Dict[str, Role] = {"admin": Role.ADMIN}


async def get_current_user(x_user: str | None = Header(default=None)) -> Tuple[str, Role]:
    """Return the username and role for the current request."""
    if x_user is None or x_user not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown user",
        )
    return x_user, user_roles[x_user]


def role_required(*allowed: Role):
    async def _dep(user: Tuple[str, Role] = Depends(get_current_user)) -> Tuple[str, Role]:
        username, role = user
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return username, role

    return _dep
