# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Task Tracker is a Kanban board with a FastAPI backend and a vanilla HTML/CSS/JS frontend. It uses in-memory storage (no database), so all data resets on server restart.

## Commands

All commands run from the `backend/` directory with the virtual environment active:

```bash
cd backend && source venv/bin/activate

# Run the server (auto-reload on changes)
uvicorn app.main:app --reload --port 8000

# Run all 31 tests (~0.10s)
pytest -v

# Run a single test file
pytest -v tests/test_tasks.py

# Run a single test by name
pytest -v -k "test_create_task_valid"

# Collect test names only (no execution)
pytest --collect-only

# Run 8 model-level validation checks (no pytest needed)
python tests/verify_a.py
```

The frontend has no build step — open [frontend/index.html](frontend/index.html) in a browser (served from port 5500 to match the CORS allowlist, e.g. `cd frontend && python3 -m http.server 5500`). The backend must be running on port 8000 first.

## Architecture

```
frontend/index.html          # Single-page Kanban board (~1700 lines, all inline)
backend/
  app/main.py                # FastAPI app: 8 endpoints, CORS middleware
  app/models.py              # Pydantic v2 models (TaskCreate, TaskUpdate, TaskResponse, ActivityEvent)
  app/storage.py             # In-memory store: _tasks and _activities dicts
  app/business_rules.py      # Status transition validator
  tests/conftest.py          # Fixtures: storage reset, TestClient, created_task
  tests/test_health.py       # 3 health endpoint tests
  tests/test_tasks.py        # 28 CRUD + due-date + overdue-filter tests
  tests/verify_a.py          # 8 standalone model-level Pydantic checks
```

### Key design decisions

- **Overdue is computed, not persisted.** A task is overdue when `due_date < today AND status != Done`. This is calculated in `storage.get_all_tasks()` and in the frontend card builder — there's no stored `is_overdue` field.
- **Activity events fire on creation and status change only.** No events for title/description/priority changes. Events are stored in `_activities: dict[str, list[ActivityEvent]]` keyed by task ID. Deleting a task removes its activity history.
- **Status transitions are constrained.** Valid: `ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`, and same→same (no-op). `ToDo→Done` (skipping InProgress) returns 422. Enforced in `business_rules.validate_status_transition()`.
- **Pydantic v2 with `extra="forbid"`** on TaskCreate and TaskUpdate — unknown fields return 422. Title validators strip whitespace, reject blank, reject >200 chars.
- **Frontend uses optimistic updates.** Drag-and-drop moves the card immediately, then PATCHes the server. On failure, the card snaps back and a toast error appears. The same pattern applies to the modal save flow.

### Test patterns

- **`storage._reset()`** is called before and after each test via the `_reset_storage` autouse fixture in [conftest.py](backend/tests/conftest.py). This guarantees test isolation.
- The `created_task` fixture POSTs a task with `{"title": "fixture task"}` and returns its JSON, so tests don't repeat setup.
- `verify_a.py` is a standalone script that catches Pydantic validation edge cases (whitespace title, `extra="forbid"`, enum rejection) — it's a quick smoke test before running the full suite.

### Frontend state machine

The board element has four CSS state classes: `state-loading`, `state-ready`, `state-empty`, `state-error`. The `setBoardState()` function in [index.html](frontend/index.html) manages these. The error state shows a "Retry" button that re-calls `loadTasks()`.

### Drag-and-drop flow

1. `dragstart` → record `draggedTaskId` and source status, add `.dragging` class
2. `dragover`/`dragenter`/`dragleave` → show/hide `.drag-over` highlight on target column
3. `drop` → extract target status, optimistically update the task's status in local state, re-render, PATCH to server
4. On PATCH failure → revert local state, re-render, show toast error for 5 seconds

### Dates and timezones

- `due_date` is a `datetime.date` (Pydantic `date` type), serialized as `YYYY-MM-DD`.
- The overdue check uses `date.today()` on the server and `new Date()` with zeroed time on the frontend — both assume local timezone. This is fine for single-machine dev but would need timezone handling at scale.
