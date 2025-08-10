import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app


@pytest.mark.anyio
async def test_admin_access():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/admin/ping", headers={"X-Role": "admin"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "admin pong"


@pytest.mark.anyio
async def test_admin_denied_for_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/admin/ping", headers={"X-Role": "client"})
    assert resp.status_code == 403
