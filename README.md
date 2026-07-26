# Task Tracker

A Kanban board for managing tasks — create, edit, drag-and-drop, and track activity. Built with a FastAPI backend and a vanilla HTML/CSS/JS frontend.

## Features

- **Three-column Kanban board** — To Do, In Progress, Done
- **Drag-and-drop** — move tasks between columns with visual feedback and rollback on error
- **Due dates** — set optional due dates; overdue tasks get a red pill and a dedicated filter toggle
- **Activity log** — per-task history (creation and status changes) plus a global activity sidebar
- **Priority badges** — Low, Medium, High with color-coded cards
- **In-memory storage** — no database setup required; data is reset on server restart

## Project Structure

```
task-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + 8 endpoints
│   │   ├── models.py         # Pydantic v2 models (TaskCreate, TaskUpdate, TaskResponse, ActivityEvent)
│   │   ├── storage.py        # In-memory task + activity store
│   │   ├── business_rules.py # Status transition validation
│   │   └── data/             # Reserved for file persistence
│   ├── tests/
│   │   ├── conftest.py       # Fixtures (TestClient, storage reset, created_task)
│   │   ├── test_health.py    # 3 tests
│   │   ├── test_tasks.py     # 28 tests (CRUD, due dates, overdue filter)
│   │   └── verify_a.py       # 8 model-level validation checks
│   └── requirements.txt
├── frontend/
│   └── index.html            # Single-page Kanban board (no build step)
└── docs/
    ├── mini-adr.md           # Architecture decisions (due dates, activity log)
    ├── user-stories.md       # Feature user stories with acceptance criteria
    ├── verification.md       # Baseline check, test results, manual browser checklist
    ├── prompt-log.md         # AI prompts used with before/after comparisons
    └── reflection.md         # Reflection on the development process
```

## Prerequisites

- **Python 3.11+**
- A modern web browser

---

## Running the Project

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional — defaults work out of the box)
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API runs at **http://localhost:8000**. While the server is running, browse the interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend

Open [frontend/index.html](frontend/index.html) directly in your browser. The frontend expects the backend to be running on port 8000, so start the backend first.

The frontend is a single static HTML file — no build step, no bundler, no framework. Open it with `file://` or serve it with any HTTP server (e.g. `python3 -m http.server 5500` from the `frontend/` directory, which matches the CORS allowlist on the backend).

### 3. Running Tests

```bash
cd backend

# Activate the virtual environment first if not already active
source venv/bin/activate

# Run all 31 tests
pytest -v

# Run a specific test file
pytest -v tests/test_tasks.py

# Collect test names only (no execution)
pytest --collect-only
```

All 31 tests pass in ~0.10s. The `verify_a.py` script can also be run directly for 8 model-level validation checks:

```bash
python tests/verify_a.py
```

---

## API Overview

| Method | Endpoint                 | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| GET    | `/health`                | Health check (`{status, timestamp}`)             |
| POST   | `/tasks`                 | Create a new task (returns 201)                  |
| GET    | `/tasks`                 | List tasks; optional `?status=`, `?priority=`, `?overdue=true` |
| GET    | `/tasks/{id}`            | Get a single task (404 if missing)               |
| PATCH  | `/tasks/{id}`            | Partial update — any subset of fields (404/422)  |
| DELETE | `/tasks/{id}`            | Delete a task and its activity history (204/404) |
| GET    | `/tasks/{id}/activity`   | Per-task activity, oldest first (404 if missing) |
| GET    | `/activity`              | Global activity feed, newest first               |

### Task fields

| Field         | Type                  | Required | Default    |
|---------------|-----------------------|----------|------------|
| `title`       | string (1–200 chars)  | yes      | —          |
| `description` | string                | no       | `""`       |
| `status`      | `ToDo` \| `InProgress` \| `Done` | no | `ToDo` |
| `priority`    | `Low` \| `Medium` \| `High` | no | `Medium` |
| `assignee`    | string or null        | no       | `null`     |
| `due_date`    | date (`YYYY-MM-DD`) or null | no | `null` |

### Business rules

- **Status transitions**: ToDo → InProgress, InProgress → Done, Done → InProgress. Skipping a column (ToDo → Done) returns 422.
- **Overdue**: computed at request time — a task is overdue when `due_date < today` **and** `status != Done`. No persisted `is_overdue` field.

The full interactive API reference with request/response schemas is at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.
