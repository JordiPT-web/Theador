from datetime import date, datetime
from typing import Dict, List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel

from .dependencies import Role, role_required, user_roles
from . import i18n

app = FastAPI(title="Theador")


class Client(BaseModel):
    id: int
    username: str
    name: str
    bookkeeper: str | None = None
    accountant: str | None = None


class ClientCreate(BaseModel):
    username: str
    name: str
    bookkeeper: str | None = None
    accountant: str | None = None


class Note(BaseModel):
    author: str
    text: str
    timestamp: datetime


class NoteCreate(BaseModel):
    text: str


class Transaction(BaseModel):
    id: int
    type: Literal["income", "expense"]
    amount: float
    category: str
    date: date


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: float
    category: str
    date: Optional[date] = None


clients: Dict[int, Client] = {}
client_notes: Dict[int, List[Note]] = {}
client_transactions: Dict[int, List[Transaction]] = {}
next_client_id = 1
next_transaction_id = 1


def get_client_or_404(client_id: int) -> Client:
    client = clients.get(client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


def ensure_client_access(client: Client, username: str, role: Role) -> None:
    if role == Role.ADMIN:
        return
    if role == Role.CLIENT and client.username == username:
        return
    if role == Role.BOOKKEEPER and client.bookkeeper == username:
        return
    if role == Role.ACCOUNTANT and client.accountant == username:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


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


@app.post(
    "/clients",
)
async def create_client(
    client_in: ClientCreate,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER)
    ),
):
    global next_client_id
    username, _role = user
    client_id = next_client_id
    next_client_id += 1
    client = Client(id=client_id, **client_in.dict())
    clients[client_id] = client
    user_roles.setdefault(client_in.username, Role.CLIENT)
    return client


@app.get("/clients")
async def list_clients(
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    )
):
    username, role = user
    result = []
    for c in clients.values():
        if role == Role.ADMIN:
            result.append(c)
        elif role == Role.ACCOUNTANT and c.accountant == username:
            result.append(c)
        elif role == Role.BOOKKEEPER and c.bookkeeper == username:
            result.append(c)
        elif role == Role.CLIENT and c.username == username:
            result.append(c)
    return {"clients": result}


@app.get("/clients/{client_id}")
async def get_client(
    client_id: int,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    ),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    return client


@app.post("/clients/{client_id}/notes")
async def add_note(
    client_id: int,
    note: NoteCreate,
    user: tuple[str, Role] = Depends(role_required(Role.ACCOUNTANT, Role.BOOKKEEPER)),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    note_obj = Note(author=username, text=note.text, timestamp=datetime.utcnow())
    client_notes.setdefault(client_id, []).append(note_obj)
    return note_obj


@app.get("/clients/{client_id}/notes")
async def list_notes(
    client_id: int,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    ),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    return {"notes": client_notes.get(client_id, [])}


@app.post("/clients/{client_id}/transactions")
async def add_transaction(
    client_id: int,
    tx: TransactionCreate,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    ),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    global next_transaction_id
    transaction = Transaction(
        id=next_transaction_id,
        date=tx.date or date.today(),
        **tx.dict(exclude={"date"}),
    )
    next_transaction_id += 1
    client_transactions.setdefault(client_id, []).append(transaction)
    return transaction


@app.get("/clients/{client_id}/transactions")
async def list_transactions(
    client_id: int,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    ),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    return {"transactions": client_transactions.get(client_id, [])}


@app.get("/clients/{client_id}/summary")
async def client_summary(
    client_id: int,
    user: tuple[str, Role] = Depends(
        role_required(Role.ADMIN, Role.ACCOUNTANT, Role.BOOKKEEPER, Role.CLIENT)
    ),
):
    username, role = user
    client = get_client_or_404(client_id)
    ensure_client_access(client, username, role)
    txs = client_transactions.get(client_id, [])
    total_income = sum(t.amount for t in txs if t.type == "income")
    total_expenses = sum(t.amount for t in txs if t.type == "expense")
    salary_expenses = sum(
        t.amount for t in txs if t.type == "expense" and t.category == "salary"
    )
    other_expenses = total_expenses - salary_expenses
    income_tax = total_income * 0.2
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "income_tax": income_tax,
        "salary_expenses": salary_expenses,
        "other_expenses": other_expenses,
    }
