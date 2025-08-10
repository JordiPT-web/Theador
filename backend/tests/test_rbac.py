import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.mark.anyio
async def test_admin_access():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/admin/ping", headers={"X-User": "admin"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "admin pong"


@pytest.mark.anyio
async def test_admin_denied_for_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        await ac.put(
            "/admin/users/bob",
            json={"role": "client"},
            headers={"X-User": "admin"},
        )
        resp = await ac.get("/admin/ping", headers={"X-User": "bob"})
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_role_assignment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        await ac.put(
            "/admin/users/carla",
            json={"role": "accountant"},
            headers={"X-User": "admin"},
        )
        resp = await ac.get("/accountant/ping", headers={"X-User": "carla"})
        assert resp.status_code == 200
        users_resp = await ac.get("/admin/users", headers={"X-User": "admin"})
        assert {"username": "carla", "role": "accountant"} in users_resp.json()[
            "users"
        ]
