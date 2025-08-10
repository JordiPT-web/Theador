from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

from .dependencies import Role, role_required, user_roles
from . import i18n

app = FastAPI(title="Theador")


@app.get("/greeting")
async def greeting(lang: str = Query("en")):
    """Return a greeting message in the requested language."""
    return {"message": i18n.translate("greeting", lang), "dir": i18n.direction(lang)}


@app.get("/admin/ping", dependencies=[Depends(role_required(Role.ADMIN))])
async def admin_ping():
    return {"status": "admin pong"}


class UserRole(BaseModel):
    role: Role


@app.get("/admin/users", dependencies=[Depends(role_required(Role.ADMIN))])
async def list_users():
    return {
        "users": [
            {"username": username, "role": role} for username, role in user_roles.items()
        ]
    }


@app.put("/admin/users/{username}", dependencies=[Depends(role_required(Role.ADMIN))])
async def set_user_role(username: str, user_role: UserRole):
    user_roles[username] = user_role.role
    return {"username": username, "role": user_role.role}


@app.get(
    "/accountant/ping",
    dependencies=[Depends(role_required(Role.ADMIN, Role.ACCOUNTANT))],
)
async def accountant_ping():
    return {"status": "accountant pong"}


@app.get(
    "/client/ping",
    dependencies=[
        Depends(role_required(
            Role.CLIENT, Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER
        ))
    ],
)
async def client_ping():
    return {"status": "client pong"}
