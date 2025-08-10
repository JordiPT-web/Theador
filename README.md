# Theador

Prototype for an AI-powered accounting platform. This repository currently
contains a minimal FastAPI backend demonstrating role based access control and
basic internationalization with Hebrew RTL support.

## Development

```bash
pip install -r backend/requirements.txt
pytest
```

## Running the server

```bash
uvicorn backend.app.main:app --reload
```
