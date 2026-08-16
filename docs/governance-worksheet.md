# Module 5 Governance Worksheet

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Task tracker code (Modules 2-5) | Low | The code is a course toy project hosted publicly (github.com/JeanElBeainy/task-tracker is readable without login), uses in-memory storage only, and a scan of all tracked files found no secrets, API keys, or credentials, so it meets every Low criterion. | Keep sharing the code, but only paste repository files and never the local .env or .claude/settings.json; re-run a secret scan of any code bundle before pasting it. | None |
| Test output and stack traces (Modules 2-4) | Low | The output I inspected (docs/verification.md) contains only synthetic fixture data with no PII or secrets, and stack traces at worst expose local absolute paths with your username, which is minor and easily removed. | Paste failures as a one line summary or a redacted excerpt, replacing absolute paths and usernames with placeholders before sharing. | TODO |
| Frontend code (Module 3) | Low | The single static frontend file (frontend/index.html) was verified to contain no embedded secrets and communicates only with localhost:8000, and it is part of the same public course repository. | Share the same file with local paths and personal annotations stripped, pasting only the state that matches the public repo. | None |
| Dockerfile and CI yaml (Module 4) | Low | Both files were verified: the Dockerfile runs as a non-root user with no secrets in ENV and the workflow contains no tokens, consistent with the public course repo. | Keep pasting template config, but never paste a workflow or Dockerfile holding a real credential; use GitHub Actions secrets and placeholders such as <TOKEN> in anything you share. | None |
| Any real external data used by mistake | TODO | The row is still open, so nothing can be graded until you say whether it happened and what the data was; credentials, personal data, or regulated data would be High while non-sensitive sample data would be Low or Medium. | Never paste real external data; if a real value is ever needed for debugging, replace it with a synthetic placeholder or an anonymized sample first. | TODO |I am doing a Module 5 governance retrospective on what I shared with AI coding tools during this course.
Risk rubric:
- Low: public code, course toy project code, no sensitive data, no proprietary logic.
- Medium: private but non-sensitive code, internal implementation details, or non-public repo context with no secrets and no PII.
- High: credentials, tokens, secrets, production config, real customer/user data, regulated data, or code I am not authorized to share.
Task:
For each row in my "What I Shared" table, classify the risk as Low, Medium, or High. Add a one-sentence reason and a safer future
AI-Assisted Coding - Module 5 Prompt Library
version of what I could paste instead.
Constraints:
- If a row is ambiguous, say what information is missing instead of guessing.
- Do not minimize risk because the project is small.
- Do not invent rows I did not provide.
Output format:
Return a table with columns:
Item shared | Risk | Reason | Safer future version | Ambiguity to resolve
What I Shared:
check 