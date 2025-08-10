import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app


@pytest.mark.anyio
async def test_hebrew_direction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/greeting", params={"lang": "he"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "שלום"
    assert data["dir"] == "rtl"
