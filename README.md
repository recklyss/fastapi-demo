# Todo API

[Learning path here](https://recklyss.github.io/fastapi-demo/learn-fastapi.html)

[![Python](https://img.shields.io/badge/python-3.13+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-latest-009688)](https://fastapi.tiangolo.com/)
[![Snowflake](https://img.shields.io/badge/snowflake-supported-29B5E8)](https://www.snowflake.com/)
[![GitHub](https://img.shields.io/badge/source-recklyss%2Ffastapi--demo-181717?logo=github)](https://github.com/recklyss/fastapi-demo)

A demo project for learning Python and building a production-shaped stack with **FastAPI + SQLAlchemy + Snowflake**, plus a small **Jinja2 web UI**.

- **Live demo:** [https://todo-demo-qnea.onrender.com/login](https://todo-demo-qnea.onrender.com/login)
- **Source:** [github.com/recklyss/fastapi-demo](https://github.com/recklyss/fastapi-demo)

## Features

- **JWT auth** — access + refresh tokens signed with HS256, Argon2 password hashing
- **Refresh-token rotation** — refresh tokens are stored (hashed), rotated on use, and revoked on logout
- **Per-user todos** — users can only read and modify their own todos
- **Jinja frontend** — login / register / todos pages that call the JSON API with a Bearer token in `localStorage`
- **Snowflake backend** — SQLAlchemy models and Alembic migrations targeting Snowflake
- **Config via environment** — `pydantic-settings` with a `.env` file
- **Test suite** — `pytest` + FastAPI `TestClient`; Snowflake tests skip unless credentials are set

## Tech stack

| Layer                 | Tool                                                                 |
|-----------------------|----------------------------------------------------------------------|
| Web framework         | [FastAPI](https://fastapi.tiangolo.com/)                             |
| Templates             | [Jinja2](https://jinja.palletsprojects.com/)                         |
| ORM                   | [SQLAlchemy 2.0](https://www.sqlalchemy.org/)                        |
| Database              | [Snowflake](https://www.snowflake.com/) (via `snowflake-sqlalchemy`) |
| Migrations            | [Alembic](https://alembic.sqlalchemy.org/)                           |
| Validation / settings | [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings`      |
| Passwords             | [pwdlib](https://github.com/frankie567/pwdlib) (Argon2)              |
| Tokens                | [PyJWT](https://pyjwt.readthedocs.io/)                               |
| Package manager       | [uv](https://docs.astral.sh/uv/)                                     |

## Project structure

```
.
├── app/
│   ├── main.py          # FastAPI app factory, lifespan, /health, /static
│   ├── config.py        # settings (pydantic-settings) + Snowflake URL
│   ├── db.py            # engine/session factory + get_db dependency
│   ├── models.py        # SQLAlchemy models: User, Todo, RefreshToken
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # password hashing, JWT, auth dependencies
│   └── routers/
│       ├── pages.py     # HTML pages: /, /login, /register, /app
│       ├── auth.py      # /auth/* endpoints
│       ├── user.py      # /user/me, /user/reset-password
│       └── todos.py     # /todos/* endpoints
├── templates/           # Jinja2 HTML
├── static/              # CSS + client JS
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

Edit `.env` with your Snowflake credentials and a `SECRET_KEY`.
See [Environment variables](#environment-variables) below.

### 3. Run migrations

```bash
uv run alembic upgrade head
```

### 4. Start the server

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

| Surface | URL |
|---------|-----|
| Web UI (login) | http://127.0.0.1:8000/login |
| Todos app | http://127.0.0.1:8000/app |
| Swagger | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

> Prefer `127.0.0.1` over `localhost` on macOS if clients resolve `localhost` to IPv6 (`::1`) while uvicorn listens on IPv4 only.

## Deploy on Render

Create a **Web Service** from this repo ([recklyss/fastapi-demo](https://github.com/recklyss/fastapi-demo)).

| Setting | Value |
|---------|-------|
| Runtime | Python **3.13** |
| Build command | `curl -LsSf https://astral.sh/uv/install.sh \| sh && uv sync --frozen --no-dev` |
| Start command | `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Pre-deploy (optional) | `uv run alembic upgrade head` |

Set the same environment variables as `.env` in the Render dashboard (`SNOWFLAKE_*`, `SECRET_KEY`, token TTLs). Do not commit `.env`.

## Environment variables

| Variable                    | Description                                             | Default           |
|-----------------------------|---------------------------------------------------------|-------------------|
| `SNOWFLAKE_ACCOUNT`         | Snowflake account identifier (e.g. `xy12345.us-east-1`) | —                 |
| `SNOWFLAKE_USER`            | Snowflake user                                          | —                 |
| `SNOWFLAKE_PASSWORD`        | Snowflake password                                      | —                 |
| `SNOWFLAKE_DATABASE`        | Snowflake database                                      | —                 |
| `SNOWFLAKE_SCHEMA`          | Snowflake schema                                        | `PUBLIC`          |
| `SNOWFLAKE_WAREHOUSE`       | Snowflake warehouse                                     | —                 |
| `SNOWFLAKE_ROLE`            | Snowflake role                                          | *(empty)*         |
| `SECRET_KEY`                | JWT signing key (use a long random string, ≥32 bytes)   | —                 |
| `ACCESS_TOKEN_TTL_SECONDS`  | Access token lifetime                                   | `900` (15 min)    |
| `REFRESH_TOKEN_TTL_SECONDS` | Refresh token lifetime                                  | `604800` (7 days) |

## Pages (HTML)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Redirects to `/login` |
| `GET` | `/login` | Sign-in page |
| `GET` | `/register` | Registration page |
| `GET` | `/app` | Todo UI (requires access token in the browser) |

The UI stores JWT tokens in `localStorage` and calls the JSON API below.

## API

Protected routes need `Authorization: Bearer <access_token>`.

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — verifies the DB connection |

### Auth — `/auth`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in (OAuth2 password form) → token pair |
| `POST` | `/auth/refresh` | Rotate a refresh token → new token pair |
| `POST` | `/auth/logout` | Revoke a refresh token |

### User — `/user`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/user/me` | Current authenticated user |
| `PATCH` | `/user/reset-password` | Reset password (`new_password` + `confirm_password`) |

### Todos — `/todos`

| Method | Path | Description |
|--------|------|-------------|
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

Three tables:

- **`users`** — id, username (unique), password hash, optional phone number, created_at
- **`todos`** — id, user_id (FK → users), title, completed, timestamps
- **`refresh_tokens`** — id, user_id (FK → users), jti, token hash, expiry, revocation timestamp

```bash
uv run alembic revision --autogenerate -m "message"   # create a migration
uv run alembic upgrade head                            # apply migrations
uv run alembic downgrade -1                            # roll back one step
```

> Note: Snowflake has no built-in Alembic DDL dialect, so `alembic/env.py` registers a minimal one.

**Immutability:** once a revision file is on `main`, do not edit or delete it — add a new revision. CI enforces this on pull requests (`.github/workflows/alembic-immutable.yaml`). Locally:

```bash
./scripts/check_alembic_immutable.sh origin/main HEAD
```

## Auth design

- Passwords are hashed with **Argon2** (`pwdlib`'s recommended profile).
- Login returns an **access token** (short-lived) and a **refresh token** (long-lived).
- Refresh tokens are stored only as a **SHA-256 hash**, keyed by `jti`.
- Refresh **rotates** the token (old one revoked, new pair issued).
- Logout revokes the presented refresh token.

## Testing

```bash
uv run pytest          # run the full suite
uv run pytest -v       # verbose output
```

Tests that need Snowflake are **skipped** unless `SNOWFLAKE_*` is set. When credentials are present, the suite runs against that Snowflake schema and **deletes all rows** in mapped tables between tests — use a dedicated test schema, not production.

## License

See [LICENSE](LICENSE).
