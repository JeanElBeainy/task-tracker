# Final AI Review

Final review of the submission diff on branch `final-project` before release, run on 2026-08-21 (Module 4 Part 4.5 prompts R1/R2: review a real diff, then triage every comment as Useful, Noise, or Wrong). The review covered the pending documentation changes plus the release state of the repo. Every comment below was verified against the cited files before it was triaged.

## 1. AI review comments

| ID | File / location | Severity | Category | Issue | Evidence from the diff or repo |
|----|-----------------|----------|----------|-------|--------------------------------|
| R-01 | `README.md` (project tree, Running Tests) | medium | docs | Tree lists `verify_a.py` under `backend/tests/` and the command `python tests/verify_a.py` points at a nonexistent path. | `backend/scripts/verify_a.py` is the real file; `backend/tests/` contains only the pytest files. Running the old command fails with `ModuleNotFoundError: No module named 'app'`. |
| R-02 | `CLAUDE.md` (Commands, Architecture) | medium | docs | Same wrong path: `python tests/verify_a.py` and `tests/verify_a.py` in the architecture block. | Verified against `backend/scripts/verify_a.py` and the session run output. |
| R-03 | `backend/README.md` section 7 | medium | docs | Claims "No `.github/workflows/ci.yml` was found in the repository" — the workflow exists and has been running. | `.github/workflows/ci.yml` (push + pull_request, Python 3.11, `pytest -v`, no false-green flags); GitHub API shows 10 runs, all `success`. |
| R-04 | `AGENTS.md` (Confirmed commands) | medium | docs | Two issues: the confirmed command `python scripts/verify_a.py` fails as written (import path), and the file states no active CI workflow is confirmed even though `ci.yml` exists. | Direct run → `ModuleNotFoundError`; `PYTHONPATH=. python scripts/verify_a.py` → 8/8 PASS. `ci.yml` inspected line by line. |
| R-05 | `docs/governance-worksheet.md` (What I Shared table) | low | docs | Two cells are still `TODO` in a final artifact: the "Any real external data used by mistake" row and one ambiguity cell. | Read the worksheet: `TODO` appears in the row and its "Ambiguity to resolve" cell. The answer must come from the student's history, not from AI. |
| R-06 | `backend/.env` (untracked) | low | security | Local `.env` exists next to the app — check whether it can be committed. | `git ls-files` shows only `backend/.env.example` is tracked; `backend/.gitignore` line 8 ignores `.env`. Safe, nothing to change. |
| R-07 | `backend/Dockerfile` (EXPOSE 8000) | low | Docker | `EXPOSE` does not publish the port — it is informational only. | Dockerfile comment already says "informational — does not publish"; `docker run -p 8000:8000` does the publishing. Nothing to change. |
| R-08 | `README.md` API overview, POST/DELETE status codes | — | docs | Suspicion: does POST `/tasks` really return 201 and DELETE 204 as the README claims? | Verified in `backend/app/main.py`: line 49 `status_code=status.HTTP_201_CREATED`, line 172 `status_code=status.HTTP_204_NO_CONTENT`. The README claims are correct. |
| R-09 | `CLAUDE.md` "~1700 lines" for `frontend/index.html` | — | docs | Suspicion: the line-count estimate may be stale. | `wc -l frontend/index.html` → 1703 lines. The claim is correct. |

## 2. Triage

| Comment | Bucket | Evidence found (where I checked) | Action |
|---------|--------|----------------------------------|--------|
| R-01 | **Useful** | `backend/scripts/verify_a.py` exists; old command actually fails (run this session). | Fixed: README tree + command corrected to `PYTHONPATH=. python scripts/verify_a.py`. Logged in [claim-vs-reality.md](claim-vs-reality.md) row 1. |
| R-02 | **Useful** | Same failure reproduced; CLAUDE.md paths wrong in two places. | Fixed: both CLAUDE.md locations corrected. Logged in [claim-vs-reality.md](claim-vs-reality.md) row 2. |
| R-03 | **Useful** | `ci.yml` read line by line; GitHub API fetched (10 runs, all success). | Fixed: `backend/README.md` section 7 rewritten with the real workflow and run link. Logged in [claim-vs-reality.md](claim-vs-reality.md) row 3. |
| R-04 | **Useful** | Command failure and CI file both verified. | Fixed: AGENTS.md command corrected and the CI sentence replaced. Logged in [claim-vs-reality.md](claim-vs-reality.md) rows 3–4. |
| R-05 | **Useful** | `TODO` cells visible in the worksheet. | Student action before submission: answer the "real external data" row (e.g. "None — only synthetic course data was shared" if that is true). Not something AI may invent — also flagged in [release-evidence.md](release-evidence.md) section 6. |
| R-06 | **Noise** | `.env` is git-ignored (`.gitignore:8`) and untracked; only `.env.example` is committed. | Skip — already safe; keep the ignore rule. |
| R-07 | **Noise** | Dockerfile comment already documents the same fact. | Skip — cosmetic, no action. |
| R-08 | **Wrong** | `main.py:49` and `main.py:172` confirm 201 and 204. | No fix — the docs were right; the comment misread the risk. |
| R-09 | **Wrong** | `wc -l frontend/index.html` = 1703. | No fix — the estimate was accurate. |

Summary: 5 Useful (4 fixed in this session, 1 needs my answer), 2 Noise (skipped with reasons), 2 Wrong (verified against code and rejected; no imaginary fixes were made).

## 3. What AI caught vs. what I had already caught

Two of the Useful items were already visible in my own earlier review work: docs/architecture-A.md had flagged the README's stale verify_a.py path (line 48), and docs/decisions/comments-feature-plan.md had noted that README and CLAUDE.md were stale while AGENTS.md was correct (line 13). The AI review added the two I had not recorded: the backend/README.md "no ci.yml" claim (which contradicted the workflow that has been running for weeks) and the fact that the AGENTS.md verify_a.py command itself fails without PYTHONPATH=.

## 4. My personal AI-review rule

I will use an AI review for broad first-pass coverage of a diff, but I will only act on a comment after I have verified it myself against the cited file or a real run, because this review's two wrong comments both looked plausible until I checked the code.