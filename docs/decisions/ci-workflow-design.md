# Technical Decision Note: CI Workflow Design

## 1. Context

The Task Tracker is a Module 4 learning project, a FastAPI REST API with in-memory storage and a simple frontend. It has no authentication, no database, and no deployment infrastructure.

The backend test suite consists of 22 pytest tests (`backend/tests/`) covering health checks, full CRUD, status-transition validation, and input rejection. Tests use `fastapi.testclient.TestClient` and `httpx`, and are fully isolated through `conftest.py` that resets in-memory storage before and after each test.

No CI workflow exists yet. Every test run is manual (`pytest -v` from `backend/`). A Docker multi-stage build is already defined but is not done automatically.

## 2. Decision

We will add a single GitHub Actions workflow at `.github/workflows/ci.yml` that:

- Triggers on `push` and `pull_request` targeting the `main` branch. Pull requests trigger on `opened`, `synchronize`, and `reopened` events only.

- Runs one job: `test` on `ubuntu-latest`, using Python 3.12.

- Steps:
  1. Checkout the repository.
  2. Set up Python 3.12 (via `actions/setup-python@v5`).
  3. Install dependencies from `backend/requirements.txt` (`pip install -r backend/requirements.txt`).
  4. Run `pytest -v` from the repository root, targeting `backend/tests/`.

- Does not build the Docker image, run linting, or measure coverage in this initial version.

The workflow is intentionally minimal, because it gates only on tests passing. Additional quality checks (linting, coverage, Docker build verification) can be added in follow-up PRs once the basic gate is in place.

## 3. Alternatives Considered

### A. Docker-based CI (build image, run tests inside container)

Run `docker build -t task-tracker .` and then `docker run task-tracker pytest -v`.

### B. Matrix build across Python versions (3.12)

Test against multiple Python versions to catch version-specific regressions. Rejected because the project pins `python:3.11-slim` in the Dockerfile and does not claim support for other versions. A single-version job matches the stated prerequisites.

### C. Include linting and coverage from day one

Add `ruff` (or `flake8`) and `pytest-cov` to the initial workflow. Rejected to keep the first CI addition scoped to the single highest-value check: do tests pass? Linting and coverage can be separate decisions.

### D. Pre-commit hooks instead of CI

Enforce tests via `pre-commit` hooks run locally. Rejected because pre-commit hooks are client-side only. They don't protect the `main` branch from a contributor who skips hooks or from direct pushes.

## 4. Trade-offs

- Speed vs completeness: A test-only workflow runs in under 30 seconds. Adding Docker build and coverage would add 1–2 minutes per run but catch more issues. For this kind of solo learning project, it matters more to have speed in such projects, so it is preferred to keep the program as is to reduce complexity. Complexity will add up as we progress with the skills learned along the way.

- No Docker build in CI: The Dockerfile is untested in automation. A future PR that breaks the build will not be caught until someone tries to build locally.

- Single Python version: We won't detect regressions on Python 3.12+ unless someone manually tests. For a learning project, this is kept as is.

- No caching of pip dependencies: Each run re-downloads packages.

I would do this differently by adding a Docker test stage if this was a team project with multiple contributors, since the cost of those additions is low and the protection they provide scales with contributor count.

## 5. Consequences

- Every push and PR to `main` will run tests automatically. A red checkmark becomes the signal that something broke.

- PRs cannot be merged (if branch protection is enabled on `main`) without passing tests. This is the single biggest quality gain.

- Contributors no longer need to remember to run `pytest` locally, CI catches it. Local test runs remain useful for fast iteration.

- The workflow file becomes the documented, executable spec** for how to run tests in this project. The `README.md` Section 7 currently documents the intent; the CI file makes it real.

- No new dependencies are introduced. The CI uses only GitHub Actions built-in runners and `actions/setup-python`, which is the de-facto standard action.

- The `.dockerignore` excludes `tests/`, which is correct for the runtime image but means tests cannot run inside the Docker container without modifying the ignore rules or the Dockerfile. This is noted but not addressed in this decision.

## 6. Open Questions

- Should we add a trigger so the workflow can be run manually from the GitHub Actions UI?

- Should the workflow's failing behaviour be explicitly configured? When a second job is added, should a failure cancel the test run or keep going?

- Should we enforce a minimum threshold of test count or coverage, or is the presence of any passing test run sufficient as a gate?

- The `requirements.txt` includes `httpx==0.28.1`, but this is a test-only dependency. Should it be split into another file for development environement (just like .env and .env.example) to`requirements-dev.txt` to keep the CI install surface minimal, or is the single-file approach simpler to maintain?