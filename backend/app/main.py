from fastapi import Depends, FastAPI, Query

from .dependencies import Role, role_required
from . import i18n

app = FastAPI(title="Theador")


@app.get("/greeting")
async def greeting(lang: str = Query("en")):
    """Return a greeting message in the requested language."""
    return {"message": i18n.translate("greeting", lang), "dir": i18n.direction(lang)}


@app.get("/admin/ping", dependencies=[Depends(role_required(Role.ADMIN))])
async def admin_ping():
    return {"status": "admin pong"}


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
