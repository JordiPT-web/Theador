import pytest
from httpx import ASGITransport, AsyncClient

from backend.app import main as main_app
from backend.app.dependencies import Role, user_roles


@pytest.mark.anyio
async def test_client_note_and_summary():
    user_roles.clear()
    user_roles["admin"] = Role.ADMIN
    main_app.clients.clear()
    main_app.client_notes.clear()
    main_app.client_transactions.clear()
    main_app.next_client_id = 1
    main_app.next_transaction_id = 1

    transport = ASGITransport(app=main_app.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        await ac.put(
            "/admin/users/bk",
            json={"role": "bookkeeper"},
            headers={"X-User": "admin"},
        )
        await ac.put(
            "/admin/users/ac",
            json={"role": "accountant"},
            headers={"X-User": "admin"},
        )
        resp = await ac.post(
            "/clients",
            json={
                "username": "cl",
                "name": "Client One",
                "bookkeeper": "bk",
                "accountant": "ac",
            },
            headers={"X-User": "bk"},
        )
        client_id = resp.json()["id"]

        await ac.post(
            f"/clients/{client_id}/transactions",
            json={"type": "income", "amount": 1000, "category": "sales"},
            headers={"X-User": "cl"},
        )
        await ac.post(
            f"/clients/{client_id}/transactions",
            json={"type": "expense", "amount": 300, "category": "salary"},
            headers={"X-User": "bk"},
        )
        await ac.post(
            f"/clients/{client_id}/transactions",
            json={"type": "expense", "amount": 200, "category": "office"},
            headers={"X-User": "bk"},
        )

        await ac.post(
            f"/clients/{client_id}/notes",
            json={"text": "please review"},
            headers={"X-User": "bk"},
        )

        notes_resp = await ac.get(
            f"/clients/{client_id}/notes", headers={"X-User": "cl"}
        )
        assert notes_resp.status_code == 200
        assert notes_resp.json()["notes"][0]["text"] == "please review"

        summary_resp = await ac.get(
            f"/clients/{client_id}/summary", headers={"X-User": "cl"}
        )
        data = summary_resp.json()
        assert data["total_income"] == 1000
        assert data["total_expenses"] == 500
        assert data["salary_expenses"] == 300
        assert data["other_expenses"] == 200


@pytest.mark.anyio
async def test_bookkeeper_access_control():
    user_roles.clear()
    user_roles["admin"] = Role.ADMIN
    main_app.clients.clear()
    main_app.client_notes.clear()
    main_app.client_transactions.clear()
    main_app.next_client_id = 1
    main_app.next_transaction_id = 1

    transport = ASGITransport(app=main_app.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        await ac.put(
            "/admin/users/bk1",
            json={"role": "bookkeeper"},
            headers={"X-User": "admin"},
        )
        await ac.put(
            "/admin/users/bk2",
            json={"role": "bookkeeper"},
            headers={"X-User": "admin"},
        )
        resp = await ac.post(
            "/clients",
            json={"username": "c1", "name": "Client1", "bookkeeper": "bk1"},
            headers={"X-User": "bk1"},
        )
        client_id = resp.json()["id"]

        resp_forbidden = await ac.get(
            f"/clients/{client_id}", headers={"X-User": "bk2"}
        )
        assert resp_forbidden.status_code == 403
