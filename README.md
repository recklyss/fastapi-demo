# Todo API

![Python](https://img.shields.io/badge/python-3.13+-blue)
![FastAPI](https://img.shields.io/badge/fastapi-latest-009688)
![Snowflake](https://img.shields.io/badge/snowflake-supported-29B5E8)

A demo project for learning Python and building a production-shaped API with
**FastAPI + SQLAlchemy + Snowflake**. It implements a small todo list backend
with JWT authentication, refresh-token rotation, and per-user data isolation.

## Features

- **JWT auth** — access + refresh tokens signed with HS256, Argon2 password hashing
- **Refresh-token rotation** — refresh tokens are stored (hashed), rotated on use, and revoked on logout
- **Per-user todos** — users can only read and modify their own todos
- **Snowflake backend** — SQLAlchemy models and Alembic migrations targeting Snowflake
- **Config via environment** — `pydantic-settings` with a `.env` file
- **Full test suite** — `pytest` + FastAPI `TestClient`, with Snowflake tests auto-skipping when no credentials are set

## Tech stack

| Layer | Tool |
| --- | --- |
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| Database | [Snowflake](https://www.snowflake.com/) (via `snowflake-sqlalchemy`) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Validation / settings | [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings` |
| Passwords | [pwdlib](https://github.com/frankie567/pwdlib) (Argon2) |
| Tokens | [PyJWT](https://pyjwt.readthedocs.io/) |
| Package manager | [uv](https://docs.astral.sh/uv/) |

## Project structure

```
.
├── app/
│   ├── main.py          # FastAPI app factory, lifespan, /health
│   ├── config.py        # settings (pydantic-settings) + Snowflake URL
│   ├── db.py            # engine/session factory and UnitOfWork
│   ├── models.py        # SQLAlchemy models: User, Todo, RefreshToken
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # password hashing, JWT, auth dependencies
│   └── routers/
│       ├── auth.py      # /auth/* endpoints
│       └── todos.py     # /todos/* endpoints
├── alembic/             # database migrations
├── tests/               # pytest suite
├── docs/                # project docs
├── pyproject.toml
├── uv.lock
└── .env.example         # template for required environment variables
```

## Getting started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) installed
- A Snowflake account (warehouse + role with table-create privileges)

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Then edit `.env` and fill in your Snowflake credentials and a `SECRET_KEY`.
See [Environment variables](#environment-variables) below.

### 3. Run migrations

```bash
uv run alembic upgrade head
```

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload
```

The API is now available at <http://127.0.0.1:8000>, with interactive docs at
<http://127.0.0.1:8000/docs> (Swagger UI) and <http://127.0.0.1:8000/redoc>.

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier (e.g. `xy12345.us-east-1`) | — |
| `SNOWFLAKE_USER` | Snowflake user | — |
| `SNOWFLAKE_PASSWORD` | Snowflake password | — |
| `SNOWFLAKE_DATABASE` | Snowflake database | — |
| `SNOWFLAKE_SCHEMA` | Snowflake schema | `PUBLIC` |
| `SNOWFLAKE_WAREHOUSE` | Snowflake warehouse | — |
| `SNOWFLAKE_ROLE` | Snowflake role | *(empty)* |
| `SECRET_KEY` | JWT signing key (use a long random string, ≥32 bytes) | — |
| `ACCESS_TOKEN_TTL_SECONDS` | Access token lifetime | `900` (15 min) |
| `REFRESH_TOKEN_TTL_SECONDS` | Refresh token lifetime | `604800` (7 days) |

## API

All `/todos` endpoints (and `GET /auth/me`) require an `Authorization: Bearer <access_token>` header.

### Health

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check — verifies the DB connection |

### Auth — `/auth`

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in (OAuth2 password form) → token pair |
| `POST` | `/auth/refresh` | Rotate a refresh token → new token pair |
| `POST` | `/auth/logout` | Revoke a refresh token |
| `GET` | `/auth/me` | Get the current user |

### Todos — `/todos`

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/todos` | List the current user's todos |
| `POST` | `/todos` | Create a todo |
| `GET` | `/todos/{id}` | Get one todo |
| `PATCH` | `/todos/{id}` | Update a todo (title and/or completed) |
| `DELETE` | `/todos/{id}` | Delete a todo |

### Example flow

```bash
# 1. Register and log in
curl -X POST http://127.0.0.1:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "secret"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -d 'username=alice&password=secret'

# 2. Use the access token from the login response
curl http://127.0.0.1:8000/todos \
  -H 'Authorization: Bearer <access_token>'

# 3. Create a todo
curl -X POST http://127.0.0.1:8000/todos \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"title": "learn FastAPI"}'
```

## Database

The data model has three tables:

- **`users`** — id, username (unique), password hash, created_at
- **`todos`** — id, user_id (FK → users, cascade delete), title, completed, timestamps
- **`refresh_tokens`** — id, user_id (FK → users), jti, token hash, expiry, revocation timestamp

Migrations live in `alembic/`. Useful commands:

```bash
uv run alembic revision --autogenerate -m "message"   # create a migration
uv run alembic upgrade head                            # apply migrations
uv run alembic downgrade -1                            # roll back one step
```

> Note: Snowflake has no built-in Alembic DDL dialect, so `alembic/env.py` registers a minimal one.

## Auth design

- Passwords are hashed with **Argon2** (`pwdlib`'s recommended profile).
- On login, the server issues an **access token** (short-lived) and a **refresh token** (long-lived).
- Refresh tokens are never stored in the clear: only a **SHA-256 hash** is persisted, keyed by `jti`.
- Refreshing **rotates** the refresh token (the old one is revoked and a new pair is issued), which limits replay.
- Logging out revokes the presented refresh token.

## Testing

```bash
uv run pytest          # run the full suite
uv run pytest -v       # verbose output
```

The tests use FastAPI's `TestClient` and a `UnitOfWork`-backed app. Tests that need a
real Snowflake database are **skipped automatically** unless the `SNOWFLAKE_*`
environment variables are set (see `.env.example`); when they are, the suite runs
against Snowflake and truncates tables between tests.

## License

See [LICENSE](LICENSE).
