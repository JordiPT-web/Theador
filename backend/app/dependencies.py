from enum import Enum
from fastapi import Depends, HTTPException, status, Header


class Role(str, Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    BOOKKEEPER = "bookkeeper"
    CLIENT = "client"


async def get_current_role(x_role: str | None = Header(default=None)) -> Role:
    """Fetch the role from the X-Role header."""
    if x_role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing role")
    try:
        return Role(x_role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown role") from exc


def role_required(*allowed: Role):
    async def _dep(role: Role = Depends(get_current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return role

    return _dep
