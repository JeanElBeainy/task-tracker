# Task Tracker — Architecture

## 1. What the app does

Task Tracker is a single-user Kanban board: a FastAPI REST API with a single-file vanilla HTML/CSS/JS frontend. Users create, edit, and delete tasks, drag them between To Do / In Progress / Done columns, set priority, assignee, and due date, filter overdue tasks, and view per-task and global activity feeds. All data lives in backend process memory and resets on server restart — there is no database.

## 2. Data model

Two entities, both Pydantic v2 models stored in in-memory dicts:

- **Task** — `id` (UUID string), `title` (required, 1–200 chars, stripped), `description` (default empty), `status` (ToDo | InProgress | Done, default ToDo), `priority` (Low | Medium | High, default Medium), `assignee` (optional), `due_date` (optional date, YYYY-MM-DD), `created_at` / `updated_at` (UTC datetimes, refreshed on every write).
- **ActivityEvent** — `task_id`, `event_type` (created | status_change), `timestamp` (UTC), `from_status` / `to_status` (populated only for status changes). Events are keyed by task id; deleting a task removes its history.

**Overdue is derived, not persisted**: `due_date < today AND status != Done`, computed at read time on both server and client.

## 3. Request flow — creating a task

1. User opens the "New Task" modal, fills fields, submits; the frontend trims the title and blocks blank titles client-side.
2. Frontend POSTs JSON to `/tasks` at `http://localhost:8000`.
3. FastAPI validates the body against `TaskCreate` (unknown fields and invalid titles → 422).
4. `storage.add_task()` generates a UUID and UTC timestamps, stores the `TaskResponse`.
5. A `created` activity event is appended for the task.
6. The 201 response returns; the frontend closes the modal and reloads the full board (GET `/tasks`), which also refreshes the global activity sidebar.

## 4. Key files

- [main.py](backend/app/main.py) — FastAPI app: 8 endpoints, CORS allowlist for port 5500, .env loading.
- [models.py](backend/app/models.py) — Pydantic v2 schemas (TaskCreate, TaskUpdate, TaskResponse, ActivityEvent), status/priority enums, title validators, `extra="forbid"`.
- [storage.py](backend/app/storage.py) — in-memory `_tasks`/`_activities` dicts, CRUD, list filters incl. computed overdue, `_reset()` for tests.
- [business_rules.py](backend/app/business_rules.py) — status transition allowlist; anything else raises 422.
- [index.html](frontend/index.html) — the entire UI and app JS in one file: state, render, modal, drag-and-drop, activity, board state machine (no build step).
- [conftest.py](backend/tests/conftest.py) — fixtures: TestClient, autouse storage reset, `created_task`.
- [test_tasks.py](backend/tests/test_tasks.py) — 28 task endpoint tests (CRUD, due dates, overdue filter).
- [test_health.py](backend/tests/test_health.py) — 3 health endpoint tests.
- [verify_a.py](backend/scripts/verify_a.py) — 8 standalone model-level validation checks.
- [README.md](README.md) — run instructions, API endpoint table, business rules summary.

## 5. Conventions

- **Validation**: Pydantic v2 with `extra="forbid"` on all request/response models; title validator strips then rejects blank or >200 chars; enums serialize by member name. Status transitions are validated separately in `business_rules` — same→same is allowed, ToDo→Done is rejected with a 422 listing the allowed transitions.
- **Storage**: module-level dicts, no persistence layer (`data/` is reserved, empty); timestamps always UTC; `updated_at` refreshes on any PATCH; delete removes the task and its activity.
- **Error handling**: 404 for unknown task ids, 422 for validation/transition errors, `HTTPException` with detail strings. The frontend reads `body.detail` on non-OK responses and falls back to the status text; the board has a 4-state machine (loading / ready / empty / error) with a Retry button that re-runs the load.
- **Frontend/backend interaction**: plain `fetch()` against a fixed `API_BASE`; CORS allowlists localhost:5500 only. Create/edit/delete are server-first (await request, then reload the board). Drag-and-drop is **optimistic**: the card moves immediately, PATCHes the server, and reverts with a 5-second error toast on failure. All user-provided text is HTML-escaped before insertion.

## 6. Not visible / assumptions

- Test counts and pass claims (31 tests, ~0.10s) come from README — I did not run pytest or read the test files.
- README points to `tests/verify_a.py` but the file actually lives at `backend/scripts/verify_a.py` (stale path).
- `Dockerfile`, `.github/workflows/ci.yml`, and `.env` exist but were not inspected; they are out of scope here.
- The per-task activity panel's exact trigger (assumed: loads when the edit modal opens) was not fully traced.
