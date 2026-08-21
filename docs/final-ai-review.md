# Final AI Review and Ownership Evidence

This file follows the template from the final project brief. It records how AI output was reviewed, graded, corrected, or rejected for this submission. Branch: final-project. Date: August 21, 2026.

## AGENTS.md guardrails

* Repo specific stack and commands included: yes (AGENTS.md, Confirmed commands section)
* Docs first and read first guardrail included: yes (AGENTS.md, Module 5 operating guardrails)
* Unexpected app and frontend edits rule included: yes (AGENTS.md says do not modify app/, backend/app/, or frontend/ unless the user approves one specific minimal fix)

## AI code review mini log

The AI reviewed the final submission diff. Every comment below was checked against the actual files before grading.

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| README points to tests/verify_a.py, but the file lives in scripts/ | Useful | The path is wrong and the old command fails | Fixed the README. See docs/claim-vs-reality.md row 1 |
| CLAUDE.md points to tests/verify_a.py in two places | Useful | Same wrong path | Fixed CLAUDE.md. See docs/claim-vs-reality.md row 2 |
| backend/README.md says no ci.yml exists | Useful | The workflow file exists and has 10 green runs | Rewrote that section. See docs/claim-vs-reality.md row 3 |
| The governance worksheet still has TODO cells | Useful | Two cells are unanswered in a final artifact | Answer them before submitting. AI must not invent this |
| backend/.env exists on disk | Noise | It is git ignored and not tracked, so there is no risk | Skip. No change needed |
| POST /tasks may return 200 instead of 201 | Wrong | backend/app/main.py line 49 returns 201. The README was right | No fix. The comment was rejected |
| frontend/index.html may not be 1700 lines | Wrong | wc -l shows 1703 lines. The claim was right | No fix. The comment was rejected |

## AI security mini review

These findings come from docs/security-review.md. Each one has file evidence.

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| No authentication on any task endpoint | backend/app/main.py has no auth imports or access checks | Valid | Real risk outside the course, but it is a documented scope decision | Keep as a known limit. Do not add auth in this project |
| Description and assignee have no length limit | backend/app/models.py lines 36 and 39, in memory storage | Noise | True, but it is generic hardening advice with no action in course scope | No action |
| Dependencies are pinned without hashes | backend/requirements.txt | Noise | Standard supply chain advice, no real impact in this scope | No action |

## Manual security check

I checked backend/.env myself. Git ignores it (backend/.gitignore line 8) and it is not tracked, so no secret can be committed by accident. I also read the CORS settings in backend/app/main.py and confirmed only http://localhost:5500 and http://127.0.0.1:5500 are allowed. I found no new issue.

## One AI output I rejected or corrected

The AI review suggested the README could be wrong about the response codes for POST and DELETE. I opened backend/app/main.py and found line 49 returns 201 and line 172 returns 204, so the README was correct. I rejected that comment and made no change. Earlier, AI generated docs placed verify_a.py in tests/ and claimed no CI file exists. I corrected both claims in the README, CLAUDE.md, AGENTS.md, and backend/README.md, and recorded them in docs/claim-vs-reality.md.

## Three AI usage rules

1. Never paste: secrets, API keys, .env files, tokens, real customer data, or production logs into an AI tool.
2. Always verify: run the tests, read the diff, and compare each claim against the real file or a live run before accepting it.
3. Record AI contributions by: keeping a prompt log with the weak version, the improved version, and an accepted, edited, or rejected note. See docs/prompt-log.md.

## Ownership statement

I can explain the main parts of this repo, including the status rules in backend/app/business_rules.py, the storage in backend/app/storage.py, and the board logic in frontend/index.html. I ran the test suite and the Docker checks myself, and I checked every claim in the evidence docs against the actual files. I graded AI output as Useful, Noise, or Wrong instead of accepting it, and I fixed or rejected anything I could not support with evidence. For these reasons I am comfortable submitting this repository as my own work.
