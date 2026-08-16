# Task Tracker — Architecture

## 1. What the app does

From the files I read, Task Tracker is a REST API — a FastAPI app titled "Task Tracker API", self-described as "Module 4 Task Tracker REST API", version 0.1.0 — for managing tasks with three statuses (ToDo, InProgress, Done), three priorities (Low, Medium, High), an optional assignee and due date, filtered listing (status/priority/overdue), per-task and global activity feeds, and a health check. Storage is in-process memory. The app metadata mentions no UI; the CORS allowlist implies a browser frontend is expected on port 5500, but the UI itself is not visible from the files I read.

## 2. Data model

Entities (Pydantic models in `models.py`, held in `storage.py` dicts):

- **Task** (`TaskResponse`) — `id` (string, generated UUID), `title` (required, 1–200 chars), `description` (default empty), `status`, `priority`, `assignee` (optional), `due_date` (optional date), `created_at` / `updated_at` (UTC datetimes).
- **TaskCreate** — creation payload: title validator (strips, rejects blank or >200 chars), `status` default ToDo, `priority` default Medium, `description` default empty, `assignee`/`due_date` optional. Unknown fields rejected (`extra="forbid"`).
- **TaskUpdate** — every field optional; only provided fields are applied; same title rule; unknown fields rejected.
- **ActivityEvent** — `task_id`, `event_type` (`created` | `status_change`), `timestamp` (UTC), `from_status` / `to_status` (optional — populated only on status-change events, per `main.py`).

Stored as `_tasks: dict` keyed by task id and `_activities: dict` of event lists keyed by task id. **Overdue is derived, not stored**: `due_date < today AND status != Done`, computed during list filtering.

## 3. Request flow — creating a task

1. A POST arrives at `/tasks` with a JSON body. (What the user or UI does before this is not visible from the files I read.)
2. FastAPI parses the body into `TaskCreate`: title is stripped and validated (non-blank, ≤200), unknown fields are rejected, defaults are applied (ToDo, Medium, empty description).
3. `add_task()` generates a UUID id and a single UTC `now` for `created_at`/`updated_at`, builds the `TaskResponse`, and stores it in `_tasks`.
4. A `created` ActivityEvent (timestamped with the task's `created_at`) is appended to `_activities[id]`.
5. HTTP 201 returns the full `TaskResponse`. (The client's reaction to the 201 is not visible from the files I read.)

## 4. Key files

- [main.py](backend/app/main.py) *(read)* — FastAPI app: 8 endpoints, CORS middleware for port-5500 origins, health check, task CRUD, activity endpoints.
- [models.py](backend/app/models.py) *(read)* — Pydantic models: TaskCreate, TaskUpdate, TaskResponse, ActivityEvent, status/priority enums, title validators, `extra="forbid"`.
- [storage.py](backend/app/storage.py) *(read)* — in-memory `_tasks`/`_activities` dicts, list filters incl. computed overdue, partial updates, `_reset()` for tests.
- `business_rules.py` *(not read; existence evidenced by main.py's import)* — supplies `validate_status_transition`, called on PATCH status changes; its rule set is not visible from the files I read.
- `.env` *(not read; loading referenced by `load_dotenv()` and its comment in main.py)* — environment variables read at startup; contents not visible.
- A test suite *(not read; referenced by `_reset()`'s "Intended for test teardown only" docstring)* — location, size, and contents not visible.
- FastAPI / Pydantic *(third-party, imported)* — framework layers; no other repository files are visible from the files I read.

## 5. Conventions

- **Validation**: Pydantic models with `extra="forbid"` on all four request/response models; a field validator strips titles and rejects blank or >200 chars; enums constrain `status` and `priority` to their three members each; creation defaults are ToDo / Medium / empty description. (How Pydantic validation failures are turned into HTTP responses is framework behavior and not visible from the files I read.)
- **Storage**: plain module-level dicts only — no database, file I/O, or persistence code appears in these files; nothing in them persists or reloads data across process restarts. Ids are UUID4 strings generated in `add_task`; timestamps are always UTC (`datetime.now(timezone.utc)`); `updated_at` is refreshed whenever an update is applied; an empty PATCH body returns the task unchanged; deleting a task also removes its activity list.
- **Error handling**: endpoints raise `HTTPException` 404 with a detail string for unknown task ids (including the activity endpoint); invalid status transitions produce 422 (raised inside `business_rules`, whose details are not visible); success codes are 201 (create), 200 (list/get/patch/health), 204 (delete). Deletion failure and not-found responses use the same 404 pattern.
- **Frontend/backend interaction**: not visible from the files I read. The only visible facts are that the API is HTTP/JSON (FastAPI response models) and CORS allowlists `http://localhost:5500` and `http://127.0.0.1:5500` with all methods/headers — indicating an expected browser frontend served from port 5500. How that frontend calls these endpoints, or whether it exists beyond this expectation, is not visible.

## 6. Not visible / assumptions

- The frontend in its entirety — UI, drag-and-drop, rendering, error states, activity display: not visible from the files I read.
- The allowed status-transition set — only that invalid ones raise 422 (per main.py docstrings); the rules themselves are in `business_rules.py`, not read.
- Tests — referenced by the `_reset()` docstring only; count, coverage, and framework not visible.
- Whether data survives restart — the three files show only in-memory dicts; nothing confirms or denies an external store elsewhere.
- `.env` contents, dependency versions beyond the imports visible (`fastapi`, `pydantic`, `dotenv`), deployment, and CI setup.
- Minor inconsistency visible in the files read: `get_all_tasks()` implements and is called with an `overdue` filter, but its docstring documents only the `status`/`priority` filters.
