# Elder Company — Backend API

FastAPI backend: REST API, models, middleware, and utilities.

Business logic lives in **`../services/`** at the repo root. Tests live in **`../tests/`**.

## Quick start

```bash
cd backend
pip install -r requirements.txt

# From repo root — local data directory (gitignored)
cd ..
./scripts/setup_local_dirs.sh
cp backend/env.example do-not-upload/env/.env

cd backend
uvicorn main:app --reload
```

API: `http://localhost:8000`

Local secrets, database, logs, and uploads live in **`../do-not-upload/`** (never committed).

## Layout

```
backend/
├── api/              # Route handlers
├── config/           # Settings and database
├── middleware/       # Auth, rate limit, errors
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── storage/          # File storage helpers
├── utils/            # Shared utilities
└── main.py           # App entrypoint

../services/          # Business logic (repo root)
../tests/             # Pytest suite (repo root)
../scripts/           # Migration, stress test, checks
```

## Tests

Run from the **repository root**:

```bash
pytest tests/integration/test_internal_api.py -v
./scripts/check_folder_limits.sh
```

See [tests/README.md](../tests/README.md) and [docs/testing/TESTING.md](../docs/testing/TESTING.md).

## Docs

- [DOCS_INDEX.md](../DOCS_INDEX.md)
- [docs/api/](../docs/api/)
- [docs/architecture/](../docs/architecture/)

---

**Last updated**: 2026-07-04
