# Task Tracker

A Kanban board for managing tasks. Create, edit, and drag and drop tasks, and track activity. Built with a FastAPI backend and a vanilla HTML/CSS/JS frontend.

## Features

* **Three column Kanban board:** To Do, In Progress, Done
* **Drag and drop:** move tasks between columns with visual feedback and rollback on error
* **Due dates:** set optional due dates. Overdue tasks get a red pill and a dedicated filter toggle
* **Activity log:** per task history for creation and status changes, plus a global activity sidebar
* **Priority badges:** Low, Medium, High on color coded cards
* **In memory storage:** no database setup required. Data resets on server restart

## Project Structure

```
task-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + 8 endpoints
│   │   ├── models.py         # Pydantic v2 models (TaskCreate, TaskUpdate, TaskResponse, ActivityEvent)
│   │   ├── storage.py        # In memory task + activity store
│   │   ├── business_rules.py # Status transition validation
│   │   └── data/             # Reserved for file persistence
│   ├── tests/
│   │   ├── conftest.py       # Fixtures (TestClient, storage reset, created_task)
│   │   ├── test_health.py    # 3 tests
│   │   └── test_tasks.py     # 28 tests (CRUD, due dates, overdue filter)
│   ├── scripts/
│   │   └── verify_a.py       # 8 model level validation checks
│   └── requirements.txt
├── frontend/
│   └── index.html            # Single page Kanban board (no build step)
└── docs/
    ├── mini-adr.md           # Architecture decisions (due dates, activity log)
    ├── user-stories.md       # Feature user stories with acceptance criteria
    ├── verification.md       # Baseline check, test results, manual browser checklist
    ├── prompt-log.md         # AI prompts used with before/after comparisons
    └── reflection.md         # Reflection on the development process
```

## Prerequisites

* **Python 3.11+**
* A modern web browser

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

# Copy the environment file, optional, defaults work out of the box
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API runs at **http://localhost:8000**. While the server is running, browse the interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Frontend

Open [frontend/index.html](frontend/index.html) directly in your browser. The frontend expects the backend to be running on port 8000, so start the backend first.

The frontend is a single static HTML file with no build step, no bundler, and no framework. Open it with `file://` or serve it with any HTTP server (e.g. `python3 -m http.server 5500` from the `frontend/` directory, which matches the CORS allowlist on the backend).

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

All 31 tests pass (`pytest -v`: 31 passed in about 0.1 seconds, checked August 21, 2026). The `verify_a.py` script runs 8 model level validation checks:

```bash
PYTHONPATH=. python scripts/verify_a.py
```

---

## API Overview

| Method | Endpoint                 | Description                                      |
|--------|--------------------------|--------------------------------------------------|
| GET    | `/health`                | Health check (`{status, timestamp}`)             |
| POST   | `/tasks`                 | Create a new task (returns 201)                  |
| GET    | `/tasks`                 | List tasks; optional `?status=`, `?priority=`, `?overdue=true` |
| GET    | `/tasks/{id}`            | Get a single task (404 if missing)               |
| PATCH  | `/tasks/{id}`            | Partial update with any subset of fields (404/422) |
| DELETE | `/tasks/{id}`            | Delete a task and its activity history (204/404) |
| GET    | `/tasks/{id}/activity`   | Per-task activity, oldest first (404 if missing) |
| GET    | `/activity`              | Global activity feed, newest first               |

### Task fields

| Field         | Type                  | Required | Default    |
|---------------|-----------------------|----------|------------|
| `title`       | string (1 to 200 chars) | yes    | none       |
| `description` | string                | no       | `""`       |
| `status`      | `ToDo` \| `InProgress` \| `Done` | no | `ToDo` |
| `priority`    | `Low` \| `Medium` \| `High` | no | `Medium` |
| `assignee`    | string or null        | no       | `null`     |
| `due_date`    | date (`YYYY-MM-DD`) or null | no | `null` |

### Business rules

* **Status transitions:** ToDo to InProgress, InProgress to Done, Done to InProgress. Skipping a column (ToDo to Done) returns 422.
* **Overdue:** computed at request time. A task is overdue when `due_date < today` and `status != Done`. No persisted `is_overdue` field.

The full interactive API reference with request/response schemas is at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

---

## Final Project

Branch reviewed: final-project

This section is the course closeout. It lists the commands that work in this repo, the evidence for each module, and how AI was used along the way.

### What this submission demonstrates
* The Task Tracker app still runs inside the course scope.
* CI runs the pytest suite on push and pull request.
* The Docker image builds and runs, and /health returns 200.
* AI review, security, and ownership evidence lives in docs/.

### Commands

Run backend commands from `backend/`, frontend commands from `frontend/`.

```bash
# Run the backend tests (31 tests)
cd backend
source venv/bin/activate
pytest -v

# Run the model level validation checks (8 checks)
PYTHONPATH=. python scripts/verify_a.py

# Run the API
uvicorn app.main:app --reload --port 8000
```

```bash
# Serve the static board, no build step
cd frontend
python3 -m http.server 5500
```

```bash
# Docker: build, run, verify, stop
cd backend
docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health    # expect 200 {"status":"ok", ...}
docker exec tt-dev whoami               # expect: app (not root)
docker stop tt-dev
```

### Evidence links

| Artifact | File |
|---|---|
| Release evidence (commands actually run, CI, Docker) | [docs/release-evidence.md](docs/release-evidence.md) |
| Claim vs reality log (doc inaccuracies caught and fixed) | [docs/claim-vs-reality.md](docs/claim-vs-reality.md) |
| Final AI review (Useful / Noise / Wrong triage) | [docs/final-ai-review.md](docs/final-ai-review.md) |
| Test results, verify_a output, browser checklist, red run evidence | [docs/verification.md](docs/verification.md) |
| Security review (grades, reconciliation, top three backlog) | [docs/security-review.md](docs/security-review.md) |
| Architecture and context strategy comparison (A/B/C) | [docs/architecture.md](docs/architecture.md) |
| Comments feature plan (generic vs repo grounded) | [docs/decisions/comments-feature-plan.md](docs/decisions/comments-feature-plan.md) |
| CI technical note | [docs/decisions/ci-workflow-design.md](docs/decisions/ci-workflow-design.md) |
| Governance worksheet (what was shared with AI + risk levels) | [docs/governance-worksheet.md](docs/governance-worksheet.md) |
| Personal AI playbook + Decision Card | [docs/ai-playbook.md](docs/ai-playbook.md) |
| Prompt log (weak to improved prompts, accepted/edited/rejected) | [docs/prompt-log.md](docs/prompt-log.md) |
| Tool fit reflection | [docs/reflection.md](docs/reflection.md) |
| CI workflow | [.github/workflows/ci.yml](.github/workflows/ci.yml) |

### AI use summary

* What AI built: the Kanban board, the due dates and overdue filter feature, and the activity log were built with AI help. Every prompt is logged with a weak version, an improved version, and an accepted, edited, or rejected note in [docs/prompt-log.md](docs/prompt-log.md).
* Which tools: feature work started in Cursor, then moved to DeepSeek running through Claude Code in VSCode (see [docs/reflection.md](docs/reflection.md)). Module 5 review, planning, governance, and context experiments were done in Codex App with a read first, docs first posture (see [AGENTS.md](AGENTS.md)).
* How AI output was graded, not accepted: security findings were graded Valid, False Positive, or Noise ([docs/security-review.md](docs/security-review.md)). Review comments were triaged as Useful, Noise, or Wrong ([docs/final-ai-review.md](docs/final-ai-review.md)). Plan sections were labeled Right, Missing, or Needs Resequencing ([docs/decisions/comments-feature-plan.md](docs/decisions/comments-feature-plan.md)). Four documentation claims were caught not matching the code and were fixed ([docs/claim-vs-reality.md](docs/claim-vs-reality.md)).
* Governance: everything shared with AI was classified Low risk, since this is a public course repo with synthetic data and no secrets ([docs/governance-worksheet.md](docs/governance-worksheet.md)). The .env file and secrets were never shared.
* Rules I keep: the playbook in [docs/ai-playbook.md](docs/ai-playbook.md). Never paste secrets or API keys into an AI tool. Read and verify everything before committing. Review the first outputs closely, because that is where corrections are still cheap.
