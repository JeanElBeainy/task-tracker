# Release Evidence

Evidence for the final submission of the Task Tracker project. Branch: final-project. Date: August 21, 2026. Every command below was actually run, or comes from an artifact that records it.

## Baseline

* Branch: final-project (HEAD de24b70)
* Date: August 21, 2026
* Local app run command: cd backend, then venv/bin/uvicorn app.main:app --reload --port 8000
* /health result: HTTP/1.1 200 OK with body {"status":"ok","timestamp":"2026-08-21T10:08:54.313237+00:00"} (local run, August 21, 2026)
* Frontend check: the static page serves from frontend/ with python3 -m http.server 5500, and index.html returns HTTP 200. The manual browser checklist in docs/verification.md records the board and the create and edit flow.
* Test command: cd backend, then venv/bin/pytest -v
* Test result: 31 passed in about 0.1 seconds

## 1. Deliverable checklist

| Deliverable | Where it lives | Status |
|---|---|---|
| CLAUDE.md (corrected project memory) | [`CLAUDE.md`](../CLAUDE.md) | present |
| AGENTS.md (repo instructions and Module 5 guardrails) | [`AGENTS.md`](../AGENTS.md) | present |
| CI workflow | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | present, green runs on GitHub (section 3) |
| Dockerfile and .dockerignore (builder stage, slim runtime, app user) | [`backend/Dockerfile`](../backend/Dockerfile), [`backend/.dockerignore`](../backend/.dockerignore) | present, rechecked this session (section 4) |
| Docstrings and README (verified documentation) | `backend/app/*.py`, [`README.md`](../README.md), [`backend/README.md`](../backend/README.md) | present; four inaccuracies caught and fixed (section 5) |
| Claim vs reality log | [`docs/claim-vs-reality.md`](claim-vs-reality.md) | present (3 required checks and 1 bonus) |
| AI review log with Useful / Noise / Wrong triage | [`docs/final-ai-review.md`](final-ai-review.md) | present |
| Technical decision note linked from README | [`docs/decisions/ci-workflow-design.md`](decisions/ci-workflow-design.md) | present, linked from README Final Project section |
| Security review (grades, reconciliation, top three backlog) | [`docs/security-review.md`](security-review.md) | present |
| Governance worksheet (Shared and Received tables, risk levels) | [`docs/governance-worksheet.md`](governance-worksheet.md) | present (two open TODO cells flagged in final-ai-review.md for the student to answer) |
| Comments feature plan (generic vs repo grounded) | [`docs/decisions/comments-feature-plan.md`](decisions/comments-feature-plan.md) | present |
| Architecture docs A/B/C and final comparison | [`docs/architecture-A.md`](architecture-A.md), [`docs/architecture-B.md`](architecture-B.md), [`docs/architecture-C.md`](architecture-C.md), [`docs/architecture.md`](architecture.md) | present |
| Personal AI playbook and Decision Card | [`docs/ai-playbook.md`](ai-playbook.md) | present |
| Test and verification record | [`docs/verification.md`](verification.md) | present |

## 2. Backend verification (run August 21, 2026)

```bash
cd backend
venv/bin/pytest -v
```

Result: 31 passed in about 0.1 seconds (31 of 31 green, local Python 3.12.3, pytest 8.3.4).

```bash
cd backend
PYTHONPATH=. venv/bin/python scripts/verify_a.py
```

Result: 8 of 8 checks PASS, ending with the line "--- Part A verifications complete ---".

Note: running `python scripts/verify_a.py` without `PYTHONPATH=.` fails with `ModuleNotFoundError: No module named 'app'`, because the script imports `app.models`. This is why the README, CLAUDE.md, and AGENTS.md commands were corrected. See the claim vs reality log in section 5.

## 3. CI evidence

* Workflow file: `.github/workflows/ci.yml`
* Triggers: push and pull_request
* Setup: ubuntu-latest, Python 3.11, pip install -r requirements.txt
* Test command used by CI: pytest -v
* Shortcut check: no continue-on-error, no `|| true`, no `--exit-zero`, pytest is not skipped. The file was inspected line by line.
* Latest run: https://github.com/JeanElBeainy/task-tracker/actions/runs/32243302797 (run 32243302797, branch final-project, commit 077013b, title "Modify ai-playbook to match Module 5 rubrics", conclusion success)
* GitHub API check on August 21, 2026: 10 recorded runs, all with conclusion success

Green to red to green: the local red run evidence from Module 4 is in docs/verification.md (two deliberately broken tests and their failing output, then restored green). An Actions hosted red run is not visible in the API history, and the final project brief says that evidence is optional.

## 4. Docker evidence (run August 21, 2026)

```bash
cd backend
docker build -t task-tracker:dev .        # succeeded, image 187MB
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
docker exec tt-dev whoami                 # returns app
docker stop tt-dev                        # container removed with --rm
```

Observed output:

* GET /health returns HTTP/1.1 200 OK with body {"status":"ok","timestamp":"2026-08-21T08:37:21.796907+00:00"}
* docker exec tt-dev whoami returns app, so the container runs as the app user, not root
* Image task-tracker:dev is 187MB, built from a Dockerfile with a builder stage and a slim python:3.11-slim runtime stage
* Runtime command: uvicorn app.main:app --host 0.0.0.0 --port 8000 with no reload flag
* No baked secrets check: .dockerignore excludes .env, .git, venv folders, caches, and tests. I inspected the file and the image.

Session note: the build used the legacy builder (DOCKER_BUILDKIT=0) because the local sandbox blocks BuildKit activity files. The builder choice does not change the Dockerfile or the image.

## 5. Documentation claim vs reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README placed verify_a.py in tests/ and told readers to run python tests/verify_a.py | backend/scripts/verify_a.py exists. The old command fails with ModuleNotFoundError | Claim wrong | README now shows scripts/ and the command PYTHONPATH=. python scripts/verify_a.py |
| CLAUDE.md used the same wrong path in two places | Same file and run evidence | Claim wrong | CLAUDE.md corrected in both places |
| backend/README.md said no ci.yml exists | .github/workflows/ci.yml exists and has 10 green runs on GitHub | Claim wrong | Section 7 rewritten with the real workflow summary |
| AGENTS.md listed python scripts/verify_a.py as a confirmed command | Direct run fails. The run with PYTHONPATH=. passes 8 of 8 checks | Claim wrong | AGENTS.md command corrected |

The same log with full evidence details is in docs/claim-vs-reality.md.

## 6. Evidence links

* Commands and run outputs: docs/release-evidence.md (this file)
* Test results, verify_a output, manual browser checklist, red run evidence: docs/verification.md
* Doc inaccuracies caught and fixed: docs/claim-vs-reality.md
* Final AI review and triage: docs/final-ai-review.md
* Security review: docs/security-review.md
* Architecture and context strategy comparison: docs/architecture.md
* Feature planning: docs/decisions/comments-feature-plan.md
* CI technical note: docs/decisions/ci-workflow-design.md
* Governance worksheet: docs/governance-worksheet.md
* AI playbook: docs/ai-playbook.md
* Prompt log: docs/prompt-log.md
* Tool reflection: docs/reflection.md
