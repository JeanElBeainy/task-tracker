# AGENTS.md

## Project summary

Task Tracker is a learning project Kanban board. Its FastAPI REST backend is in `backend/app/`, and its single page vanilla HTML, CSS, and JavaScript frontend is in `frontend/index.html`. Task and activity storage is in memory, so all data is lost when the backend restarts. No authentication or database implementation is present.

Primary implementation sources are `backend/app/main.py`, `backend/app/models.py`, `backend/app/storage.py`, and `frontend/index.html`.

## Technology and layout

The backend requires Python 3.11 or later and uses FastAPI, Pydantic v2, Uvicorn, python dotenv, pytest, and httpx. See `backend/requirements.txt`. The frontend is static and has no confirmed package manager, bundler, or build step. Tests are in `backend/tests/`, with standalone model validation checks in `backend/scripts/verify_a.py`. A Docker runtime definition is present at `backend/Dockerfile`.

## Confirmed commands

Run backend commands from `backend/`.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000

pytest -v
pytest -v tests/test_tasks.py
pytest --collect-only

python scripts/verify_a.py
```

The frontend calls `http://localhost:8000`. Backend CORS explicitly permits origins on port 5500. To serve the static frontend locally, run this from `frontend/`.

```bash
python3 -m http.server 5500
```

The following Docker commands are supported from `backend/`.

```bash
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
```

No `pyproject.toml`, frontend build command, linter command, formatter command, or active CI workflow is confirmed by the files inspected.

## Visible business rules

Task statuses are `ToDo`, `InProgress`, and `Done`. Priorities are `Low`, `Medium`, and `High`. New tasks default to `ToDo`, `Medium`, an empty description, no assignee, and no due date.

A title is required, stripped of surrounding whitespace, unable to be blank, and limited to 200 characters. Unknown fields are rejected for create and update payloads.

Allowed status changes are `ToDo` to `InProgress`, `InProgress` to `Done`, `Done` to `InProgress`, and a same status no op. Other transitions return HTTP 422.

Updates are partial and omitted fields retain their values. An empty update returns the existing task unchanged. A task is overdue only when its due date is before today and its status is not `Done`; overdue is computed rather than persisted.

Creating a task creates an activity event. Changing status creates an activity event. Deleting a task removes its activity history. The frontend groups tasks by status and displays each group in priority order: High, Medium, then Low.

Sources are `backend/app/models.py`, `backend/app/business_rules.py`, `backend/app/storage.py`, `backend/app/main.py`, and `frontend/index.html`.

## Module 5 operating guardrails

Treat Module 5 as an AI assisted coding governance and grading module, not a feature building module. Default to read only inspection and report evidence before proposing changes. Prefer documentation work and edit files in `docs/` by default.

Do not modify `app/` or `backend/app/` unless the user explicitly approves one specific minimal fix. Keep one bounded task per thread. If a request expands materially, ask the user to open or authorize a separate task.

State the task understood, files to inspect, and required edit permission before acting. Cite actual repository files inspected for every repository specific claim. If a file, command, behavior, or policy is not visible, mark it as not confirmed rather than inferring it.

## Security and governance

Never paste, log, commit, or expose secrets, credentials, tokens, or local `.env` contents. `.env` is ignored. Use `.env.example` only as a safe configuration reference.

Do not run destructive commands or irreversible Git operations without explicit approval and a verified target. Preserve unrelated user changes and do not broaden the requested scope.

Do not claim tests, builds, CI results, security properties, or repository findings that were not actually inspected or run. Do not invent findings for the AI Assisted Coding Module 5 Prompt Library. Record only evidence supplied or inspected in this repository.
