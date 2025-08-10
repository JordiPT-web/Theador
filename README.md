# Theador

Prototype for an AI-powered accounting platform. This repository currently
contains a minimal FastAPI backend demonstrating role based access control and
basic internationalization with Hebrew RTL support.

The application now includes an admin panel for managing user permissions.
Users are identified via the `X-User` header. Administrators can assign roles
with `PUT /admin/users/{username}` and list current assignments using
`GET /admin/users`. Supported roles include `admin`, `accountant`,
`bookkeeper` (tax consultants/account managers) and `client`.

The backend also provides in-memory endpoints for managing clients:

- `POST /clients` – create a client and assign a bookkeeper/accountant.
- `GET /clients` and `GET /clients/{id}` – list accessible clients and view
  details.
- `POST /clients/{id}/notes` / `GET /clients/{id}/notes` – bookkeepers or
  accountants can leave notes for a client to read.
- `POST /clients/{id}/transactions` – record income or expenses.
- `GET /clients/{id}/summary` – view totals, a simple tax estimate and an
  expense breakdown (salary vs. other).

## Development

```bash
pip install -r backend/requirements.txt
pytest
```

## Running the server

```bash
uvicorn backend.app.main:app --reload
```
