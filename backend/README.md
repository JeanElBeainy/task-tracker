# Task Tracker — Module 4

Full-stack task-tracking application with a FastAPI REST API and a vanilla
HTML/CSS/JS Kanban board. This is a learning project — it runs entirely
in-process with **in-memory storage** and no authentication, database, or
production hardening.

## 1. Project overview

- **Backend:** FastAPI (Python 3.11+) — REST API for CRUD task management plus
  a `/health` liveness endpoint.
- **Frontend:** A single-page Kanban board (`frontend/index.html`) that
  communicates with the API via `fetch()`.
- **Storage:** In-memory Python `dict` (lost on restart).
- **Business logic:** Status-transition validation (e.g. ToDo → InProgress is
  allowed; ToDo → Done is rejected).

## 2. Prerequisites

- Python 3.11 or later (`python3 --version`)
- pip (bundled with Python 3.11+)
- (optional) Docker — for containerised runs

## 3. Local setup

From the repository root, `cd` into the backend directory first:

```bash
cd backend
```

**Create and activate a virtual environment:**

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Set up environment variables:**

Linux / macOS:
```bash
cp .env.example .env
```

Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

The defaults in `.env.example` (`PORT=8000`, `APP_ENV=development`) work out
of the box — no changes needed.

## 4. Run the app locally

Make sure you are in `backend/` with the virtual environment active:

```bash
uvicorn app.main:app --reload --port 8000
```

| Option     | Purpose                                  |
|------------|------------------------------------------|
| `--reload` | Auto-restart on code changes (dev only). |
| `--port`   | Port to bind to (defaults to 8000).      |

**Endpoints:**

| Method   | Path             | Description        |
|----------|------------------|--------------------|
| `GET`    | `/health`        | Liveness check     |
| `POST`   | `/tasks`         | Create a task      |
| `GET`    | `/tasks`         | List tasks         |
| `GET`    | `/tasks/{id}`    | Get a single task  |
| `PATCH`  | `/tasks/{id}`    | Partial update     |
| `DELETE` | `/tasks/{id}`    | Delete a task      |

Interactive docs: open <http://localhost:8000/docs> while the server is
running.

## 5. Run tests

```bash
pytest -v
```

Tests cover:
- Health-check endpoint (status code, response shape, ISO 8601 timestamp).
- Full CRUD cycle for `/tasks` — create, list (with filters by status &
  priority), get-by-id, patch (partial updates, status transitions, validation
  errors), and delete.

The `conftest.py` fixture resets in-memory storage before and after every test
so tests are fully isolated.

## 6. Run with Docker

Build the image from the `backend/` directory:

```bash
docker build -t task-tracker .
```

Run the container:

```bash
docker run -p 8000:8000 task-tracker
```

The API is available at <http://localhost:8000>. The `Dockerfile` is a
multi-stage build — dependencies are installed in a `builder` stage, then only
the virtual environment and application code are copied into the slim runtime
image, which runs as a non-root `app` user.

## 7. CI workflow summary [VERIFY]

No `.github/workflows/ci.yml` was found in the repository. [VERIFY] When a CI
workflow is added, it should:

- Trigger on pushes and pull requests to `main`.
- Install Python 3.11, restore dependencies from `requirements.txt`, and run
  `pytest -v` inside `backend/`.

## 8. Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, endpoints
│   │   ├── models.py            # Pydantic schemas & enums
│   │   ├── storage.py           # In-memory task store
│   │   ├── business_rules.py    # Status-transition validator
│   │   └── data/                # Reserved directory (.gitkeep)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Fixtures & storage reset
│   │   ├── test_health.py       # /health endpoint tests
│   │   └── test_tasks.py        # CRUD + validation tests
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── scripts/
│       └── verify_a.py          # Manual Pydantic validation spot-check
└── frontend/
    └── index.html               # Kanban board SPA
```

## 9. Project conventions & current limitations

- **In-memory storage:** Tasks are stored in a Python `dict` on the API
  process. Restarting the server wipes all data.
- **No authentication / authorisation:** The API is wide-open — CORS allows
  `localhost:5500` and `127.0.0.1:5500` only, but no auth mechanism exists.
- **No database:** No PostgreSQL, SQLite, or file persistence is wired up.
  The `app/data/` directory is reserved for future use.
- **Status transitions:** Enforced by `business_rules.py` — only
  ToDo→InProgress, InProgress→Done, Done→InProgress, and same→same are
  permitted. [VERIFY] A comment in the code questions whether same→same should
  be valid.
- **No production server:** `uvicorn` is run without a process manager
  (gunicorn). The Docker image omits `--reload` but is still a single-worker
  deployment.
- **Frontend served separately:** The Kanban board in `frontend/index.html` is
  designed to be opened directly (or via a static server on port 5500), not
  served by FastAPI.

## 10. Further reading

No `docs/decisions/` directory exists yet. If architectural decision records
(ADRs) are added later, link them here.
