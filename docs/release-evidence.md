# Release Evidence

Evidence for the final submission of the Task Tracker project, branch `final-project` (HEAD `077013b`, 2026-08-21). Every command listed below was actually run in this session, or is cited from an artifact that records it.

## 1. Deliverable checklist

| Deliverable | Where it lives | Status |
|---|---|---|
| CLAUDE.md (corrected project memory) | [`CLAUDE.md`](../CLAUDE.md) | ✅ present |
| AGENTS.md (repo instructions + Module 5 guardrails) | [`AGENTS.md`](../AGENTS.md) | ✅ present |
| CI workflow | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | ✅ present, green runs on GitHub (section 3) |
| Dockerfile + .dockerignore (multi-stage, non-root) | [`backend/Dockerfile`](../backend/Dockerfile), [`backend/.dockerignore`](../backend/.dockerignore) | ✅ present, re-verified this session (section 4) |
| Docstrings + README (verified documentation) | `backend/app/*.py`, [`README.md`](../README.md), [`backend/README.md`](../backend/README.md) | ✅ present; four inaccuracies caught and fixed (see [claim-vs-reality.md](claim-vs-reality.md)) |
| Claim-vs-reality log | [`docs/claim-vs-reality.md`](claim-vs-reality.md) | ✅ present (3 required checks + 1 bonus) |
| AI review log with Useful / Noise / Wrong triage | [`docs/final-ai-review.md`](final-ai-review.md) | ✅ present |
| Technical decision note linked from README | [`docs/decisions/ci-workflow-design.md`](decisions/ci-workflow-design.md) | ✅ present, linked from README Final Project section |
| Security review (grades + reconciliation + top-3) | [`docs/security-review.md`](security-review.md) | ✅ present |
| Governance worksheet (Shared/Received, risk levels) | [`docs/governance-worksheet.md`](governance-worksheet.md) | ✅ present (two open TODO cells flagged in [final-ai-review.md](final-ai-review.md) for the student to answer) |
| Comments feature plan (generic vs repo-grounded) | [`docs/decisions/comments-feature-plan.md`](decisions/comments-feature-plan.md) | ✅ present |
| Architecture docs A/B/C + final comparison | [`docs/architecture-A.md`](architecture-A.md), [`docs/architecture-B.md`](architecture-B.md), [`docs/architecture-C.md`](architecture-C.md), [`docs/architecture.md`](architecture.md) | ✅ present |
| Personal AI playbook + Decision Card | [`docs/ai-playbook.md`](ai-playbook.md) | ✅ present |
| Test & verification record | [`docs/verification.md`](verification.md) | ✅ present |

## 2. Backend verification (run this session, 2026-08-21)

```bash
cd backend
venv/bin/pytest -v
```

Result: **31 passed in ~0.1s** (31/31 green; local Python 3.12.3, pytest 8.3.4).

```bash
cd backend
PYTHONPATH=. venv/bin/python scripts/verify_a.py
```

Result: **8/8 PASS**

Note: running `python scripts/verify_a.py` without `PYTHONPATH=.` fails with
`ModuleNotFoundError: No module named 'app'` — this is why the README/CLAUDE.md/
AGENTS.md commands were corrected in [claim-vs-reality.md](claim-vs-reality.md).

## 3. CI evidence

Workflow: `.github/workflows/ci.yml` — triggers on `push` and `pull_request`,
`ubuntu-latest`, Python 3.11, `pip install -r requirements.txt`, `pytest -v`.
No `continue-on-error`, `|| true`, or `--exit-zero` anywhere in the file
(inspected line by line).

GitHub Actions (checked via the public API
`https://api.github.com/repos/JeanElBeainy/task-tracker/actions/runs?per_page=10`
on 2026-08-21): **10 recorded CI runs, all with conclusion `success`**.

- Latest run: `https://github.com/JeanElBeainy/task-tracker/actions/runs/32243302797`
  — branch `final-project`, commit `077013b` (current HEAD), title
  "Modify ai-playbook to match Module 5 rubrics", success.

Green→red→green: local red-run evidence (two deliberately broken tests and their failing output, then restored green) is recorded in [docs/verification.md](verification.md) (Break Test Evidence). An Actions-hosted red run is not visible in the API history (all 10 recorded runs are green) — see "Still to verify" below.

## 4. Docker evidence (run this session, 2026-08-21)

```bash
cd backend
docker build -t task-tracker:dev .        # succeeded (image 187MB)
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
docker exec tt-dev whoami                 # -> app
docker stop tt-dev                        # container removed (--rm)
```

Observed output:

- `GET /health` → `HTTP/1.1 200 OK`, body
  `{"status":"ok","timestamp":"2026-08-21T08:37:21.796907+00:00"}`
- `docker exec tt-dev whoami` → `app` (non-root user confirmed)
- Image: `task-tracker:dev 187MB`, built from a multi-stage Dockerfile with a
  `python:3.11-slim` runtime base, `USER app` before `CMD`, and
  `uvicorn app.main:app --host 0.0.0.0 --port 8000` without `--reload`.

Session note: the build used the legacy builder (`DOCKER_BUILDKIT=0`) because
the local sandbox blocks BuildKit's `~/.docker` activity file; this changes
only the builder, not the Dockerfile or the produced image.

## 5. Evidence links

- Commands + run outputs: [`docs/release-evidence.md`](release-evidence.md) (this file)
- Test results, verify_a output, manual browser checklist, red-run evidence: [`docs/verification.md`](verification.md)
- Doc inaccuracies caught and fixed: [`docs/claim-vs-reality.md`](claim-vs-reality.md)
- Final AI review + triage: [`docs/final-ai-review.md`](final-ai-review.md)
- Security review: [`docs/security-review.md`](security-review.md)
- Architecture + context-strategy comparison: [`docs/architecture.md`](architecture.md)
- Feature planning: [`docs/decisions/comments-feature-plan.md`](decisions/comments-feature-plan.md)
- CI technical note: [`docs/decisions/ci-workflow-design.md`](decisions/ci-workflow-design.md)
- Governance worksheet: [`docs/governance-worksheet.md`](governance-worksheet.md)
- AI playbook: [`docs/ai-playbook.md`](ai-playbook.md)
- Prompt log: [`docs/prompt-log.md`](prompt-log.md)
- Tool reflection: [`docs/reflection.md`](reflection.md)