# Task Tracker — Architecture

## 1. What the app does

Task Tracker is a learning-project Kanban board: a FastAPI REST backend in `backend/app/` and a single-page vanilla HTML/CSS/JS frontend in `frontend/index.html`. Users create, edit, and drag tasks between To Do / In Progress / Done columns, set priority, assignee, and due date, filter overdue tasks, and view per-task and global activity feeds. Storage is in-memory — all data is lost on backend restart — and there is no authentication or database.

## 2. Data model

Two entities, Pydantic v2 models held in module-level dicts in `storage.py`:

- **Task** — `id` (generated UUID string), `title` (required; stripped; non-blank; ≤200 chars), `description` (default empty), `status` (ToDo | InProgress | Done, default ToDo), `priority` (Low | Medium | High, default Medium), `assignee` (optional), `due_date` (optional date), `created_at` / `updated_at` (UTC datetimes; `updated_at` refreshed on every change).
- **ActivityEvent** — `task_id`, `event_type` (created | status_change), `timestamp` (UTC), `from_status` / `to_status` (set only for status changes). Stored per task id; deleted with the task.

Overdue is computed, never persisted: `due_date < today AND status != Done`, evaluated on the server (`date.today()`) and on the client (zeroed local `Date`).

## 3. Request flow — creating a task

1. "New Task" opens a modal with title, description, status, priority, assignee, and due-date fields. On submit, the frontend trims the title and blocks blank titles client-side.
2. The frontend POSTs JSON to `/tasks` at `http://localhost:8000`.
3. FastAPI validates the body against `TaskCreate` (Pydantic): unknown fields, blank/oversized titles, and invalid enum values → 422.
4. `storage.add_task()` builds a `TaskResponse` with a UUID id and UTC timestamps, applies defaults, and stores it in `_tasks`.
5. A `created` ActivityEvent is appended to `_activities[task_id]`.
6. The 201 `TaskResponse` returns; the frontend closes the modal, reloads the board via GET `/tasks`, and refreshes the global activity sidebar. (Creation is server-first, not optimistic.)

## 4. Key files

- [main.py](backend/app/main.py) — FastAPI app: 8 endpoints, CORS allowlist (localhost:5500, 127.0.0.1:5500), `.env` loading.
- [models.py](backend/app/models.py) — Pydantic v2 models: TaskCreate, TaskUpdate, TaskResponse, ActivityEvent, status/priority enums, title validators, `extra="forbid"`.
- [storage.py](backend/app/storage.py) — in-memory `_tasks`/`_activities` dicts; CRUD, list filters, computed overdue, `_reset()` for tests.
- [business_rules.py](backend/app/business_rules.py) — allowed status transitions; anything else raises 422.
- [index.html](frontend/index.html) — the entire UI and app JS in one static file: board state machine, rendering, modal, drag-and-drop, activity panels (no build step).
- [conftest.py](backend/tests/conftest.py) — autouse storage-reset fixture, TestClient, `created_task` fixture.
- [test_tasks.py](backend/tests/test_tasks.py) — 28 endpoint tests (CRUD, due dates, overdue filter).
- [test_health.py](backend/tests/test_health.py) — 3 health endpoint tests.
- [verify_a.py](backend/scripts/verify_a.py) — 8 standalone model-level validation checks.
- [ci.yml](.github/workflows/ci.yml) — GitHub Actions workflow: `pytest -v` on push/PR, Python 3.11.

## 5. Conventions

- **Validation**: Pydantic v2 with `extra="forbid"` on request/response models. Title must be stripped, non-blank, ≤200 chars. Enums serialize by member name. Status transitions are checked separately in `business_rules`: ToDo→InProgress, InProgress→Done, Done→InProgress, and same→same no-op; everything else → 422 with the allowed list in the detail message.
- **Storage**: no database or persistence — process-memory dicts only (`backend/app/data/` is reserved but empty). Timestamps always UTC. PATCH applies only explicitly-set fields (`exclude_unset`); an empty update returns the task unchanged. Delete removes the task and its activity history. `_reset()` clears both dicts for tests (autouse, before and after each test).
- **Error handling**: 404 for unknown task ids (including activity endpoints), 422 for validation/transition errors, 204 for successful delete. The frontend reads `body.detail` on non-OK responses and falls back to the status text; the board has four CSS states (loading / ready / empty / error) with a Retry button that re-runs the load; a failed drag reverts the card and shows a 5-second toast.
- **Frontend/backend interaction**: plain `fetch()` against a fixed `API_BASE` (`http://localhost:8000`); CORS permits only the port-5500 origins used by the static server (`python3 -m http.server 5500` from `frontend/`). Create/edit/delete are server-first (await, then full reload). Drag-and-drop is optimistic: move the card, PATCH the status, revert + toast on failure. Cards are grouped by status and sorted High→Medium→Low, then by id; user text is escaped before DOM insertion. Activity: per-task feed (loaded when the edit modal opens) plus a global feed, newest first. Note: the backend DELETE endpoint exists, but no frontend control calls it.

## 6. Not visible / assumptions

- Tests were read but not run: the counts (28 + 3 = 31) are verified; "all 31 pass in ~0.10s" is README's claim.
- AGENTS.md states no active CI workflow was confirmed, but [.github/workflows/ci.yml](.github/workflows/ci.yml) defines one (push/PR → pytest). Whether it actually executes in GitHub could not be confirmed from the files.
- `.env` exists but was deliberately not read (secrets policy); only `.env.example` is referenced.
- The frontend CSS body (lines ~120–890) was skimmed, not line-read — styling only, no behavior claims rest on it.
- AGENTS.md also contains Module 5 governance guardrails (read-only inspection, docs-only edits); they are process policy, not architecture, so they are not covered here.
