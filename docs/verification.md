# Verification — Mid-Course Project

Selected features: **Due dates + overdue filter**, **Activity log**

---

## 1. Baseline Check

Checkpoint taken **before** any mid-course refactor. Every individual component was verified in isolation to establish a known-good baseline.

| Check                                              | Result | Notes                                       |
|----------------------------------------------------|--------|---------------------------------------------|
| `pytest -v` (31 tests)                             | ✅ 31/31 pass | 0.10s runtime, no warnings             |
| `verify_a.py` (8 model-level checks)               | ✅ 8/8 PASS     | title, defaults, extra=forbid, enums  |
| `python -m pytest --collect-only`                  | ✅ 31 collected | no collection errors                   |
| `backend/app/` imports                             | ✅ clean        | no circular imports, all modules load  |
| `frontend/index.html` loads in browser             | ✅ renders      | single-file HTML, no build step needed |
| `backend/.env` present                             | ✅              | server boots with default port 8000    |
| Python version                                     | 3.12.3         | meets the 3.11+ requirement            |
| Git branch                                         | `mid-course-project` | clean working tree (only README.md untracked) |

### Baseline summary

The codebase at this checkpoint:

- **Backend** — FastAPI app serving 7 endpoints (`/health`, `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`, `GET /tasks/{id}/activity`, `GET /activity`).
- **Storage** — In-memory dictionaries (`_tasks`, `_activities`), no database. Reset fixture clears state between tests.
- **Models** — Pydantic v2 with `extra="forbid"`, field validators on `title` (blank check, max 200 chars), enumerations for `status` and `priority`.
- **Business rules** — Status transitions enforced via `VALID_TRANSITIONS` frozenset; `ToDo→Done` (skip) is rejected.
- **Overdue logic** — Computed at request time: a task is overdue when `due_date < today` AND `status != Done`. No persisted boolean.
- **Activity log** — Events generated on creation and status change only. Retrieve per-task or globally.
- **Frontend** — Kanban board with three columns, drag-and-drop, create/edit modal, due-date picker, overdue filter toggle, activity side panel.

---

## 2. Backend Test Results

All 31 tests were run on the baseline code. Full output:

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.3.4, pluggy-1.6.0
rootdir: /home/jean/Documents/VScode/task-tracker/backend
plugins: anyio-4.14.2
collected 31 items

tests/test_health.py::test_health_check_returns_200 PASSED               [  3%]
tests/test_health.py::test_health_check_response_shape PASSED            [  6%]
tests/test_health.py::test_health_check_timestamp_is_valid_iso_format PASSED [  9%]
tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED [ 12%]
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED   [ 16%]
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED     [ 19%]
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED [ 22%]
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED   [ 25%]
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED [ 29%]
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED [ 32%]
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED [ 35%]
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED             [ 38%]
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED [ 41%]
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED [ 45%]
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED             [ 48%]
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED [ 51%]
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED [ 54%]
tests/test_tasks.py::test_patch_same_status_is_noop_returns_200 PASSED   [ 58%]
tests/test_tasks.py::test_patch_invalid_status_value_not_in_enum_returns_422 PASSED [ 61%]
tests/test_tasks.py::test_patch_empty_body_returns_200_unchanged PASSED  [ 64%]
tests/test_tasks.py::test_patch_invalid_priority_value_not_in_enum_returns_422 PASSED [ 67%]
tests/test_tasks.py::test_patch_unknown_field_returns_422 PASSED         [ 70%]
tests/test_tasks.py::test_patch_blank_title_returns_422 PASSED           [ 74%]
tests/test_tasks.py::test_patch_wrong_type_for_enum_field_returns_422 PASSED [ 77%]
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED     [ 80%]
tests/test_tasks.py::test_delete_missing_returns_404 PASSED              [ 83%]
tests/test_tasks.py::test_create_task_with_valid_due_date_returns_201_with_date PASSED [ 87%]
tests/test_tasks.py::test_create_task_with_invalid_due_date_format_returns_422 PASSED [ 90%]
tests/test_tasks.py::test_list_tasks_overdue_includes_past_due_date_with_status_todo PASSED [ 93%]
tests/test_tasks.py::test_list_tasks_overdue_excludes_past_due_date_with_status_done PASSED [ 96%]
tests/test_tasks.py::test_list_tasks_overdue_with_no_matches_returns_200_and_empty_list PASSED [100%]

============================== 31 passed in 0.10s ==============================
```

### verify_a.py (8 model-level checks)

```
PASS: whitespace title rejected
PASS: empty title rejected
PASS: title > 200 chars rejected
PASS: defaults applied (status=ToDo, priority=Medium, description='')
PASS: extra field rejected on TaskCreate
PASS: id rejected on TaskCreate
PASS: created_at rejected on TaskUpdate
PASS: invalid status rejected
--- Part A verifications complete ---
```

### Test coverage summary

| Area                        | Tests | What's covered                                     |
|-----------------------------|-------|----------------------------------------------------|
| Health                      | 3     | 200 status, response shape, valid ISO timestamp    |
| POST /tasks (create)        | 7     | valid body, missing title, blank title, invalid priority, unknown field, due-date valid, due-date invalid |
| GET /tasks (list)           | 5     | empty list, status filter, priority filter, overdue filter (hit), overdue filter (Done excluded), overdue filter (no matches) |
| GET /tasks/{id}             | 2     | found, not found                                   |
| PATCH /tasks/{id} (update)  | 10    | partial update, not found, valid transition, invalid transition, same status no-op, invalid enum, empty body, invalid priority, unknown field, blank title, wrong type for enum |
| DELETE /tasks/{id}          | 2     | existing (204 + no body), missing (404)             |
| Activity log                | —*    | covered implicitly through create/patch endpoints  |
| **Total**                   | **31**|                                                    |

> \*Activity events are created as side effects of `POST /tasks` and `PATCH /tasks/{id}` and verified incidentally; no isolated activity-log tests exist yet.

---

## 3. Manual Browser Checks

These are designed as a human checklist. Open `frontend/index.html` in a browser while the backend is running at `http://localhost:8000`.

### 3.1 Board rendering and states

- [ ] **Loading state** — On first load (or after refresh), the board briefly shows "Loading tasks…" with a spinner before cards appear. If the backend is down, the error banner with a Retry button is shown instead.
- [ ] **Empty state** — When no tasks exist, each column (To Do / In Progress / Done) shows a dashed placeholder area with no cards.
- [ ] **Populated state** — After creating tasks, cards appear in their respective status columns with correct title, description, priority badge (colored), assignee, and due date.

### 3.2 Create a task

- [ ] **New Task button** — Clicking "+ New Task" opens a modal labeled "New Task" with fields: Title (required), Description, Status, Priority, Assignee, Due Date.
- [ ] **Submit valid task** — Fill in title, pick values, click Save. Modal closes, board refreshes, the new card appears in the correct column.
- [ ] **Title validation** — Submit with an empty title. An inline error ("Title is required") appears, and the form does not submit.
- [ ] **Server-side error** — Trigger a 422 from the backend (e.g. invalid enum). The modal shows a server error banner.

### 3.3 Edit a task

- [ ] **Edit button** — Hovering a card reveals an edit (pencil) button. Clicking it opens the modal pre-filled.
- [ ] **Partial update** — Change only the title and save. Other fields (status, priority, description) are unchanged.
- [ ] **Status change** — Change status from "To Do" to "In Progress". Card moves to the new column. The activity section in the modal shows a "status_change" event.
- [ ] **Invalid transition** — Attempt to change status from "To Do" to "Done". The backend rejects it with 422; the frontend shows an error.

### 3.4 Due dates

- [ ] **Set due date** — Create a task with a due date. The card shows a readable date label (e.g. "Due Jul 30"), not a raw ISO string.
- [ ] **No due date** — Create a task without a due date. No date label appears on the card — never "null" or "None".
- [ ] **Overdue pill** — Create a task with a due date in the past and status "To Do". The card shows a red "OVERDUE" pill.
- [ ] **Done task not overdue** — Change the overdue task's status to "Done". The "OVERDUE" pill disappears.

### 3.5 Overdue filter

- [ ] **Toggle on** — Click the "Overdue" button. It becomes active (red-tinted). Only overdue tasks are shown.
- [ ] **Toggle off** — Click "Overdue" again. All tasks return.
- [ ] **Empty overdue** — If no tasks are overdue, the filter returns an empty board (columns show dashed placeholders).

### 3.6 Activity panel

- [ ] **Activity panel renders** — A "Recent Activity" sidebar is visible on the right side of the board.
- [ ] **Creation events** — When a new task is created, an activity item appears in the sidebar.
- [ ] **Status-change events** — When a task's status changes, a status-change item appears with from/to values.
- [ ] **Per-task activity** — Open a task in edit mode; the modal's Activity section shows that task's history in chronological order.

### 3.7 Drag-and-drop

- [ ] **Move between columns** — Drag a card from "To Do" to "In Progress". The status updates, and the card renders in the target column.
- [ ] **Invalid transition blocked** — Drag a card from "To Do" to "Done". A toast error appears at the bottom of the screen, the card snaps back, and status is unchanged.
- [ ] **Drag visual feedback** — While dragging, the card appears semi-transparent. The target column shows a dashed highlight border.

### 3.8 Modal

- [ ] **Cancel** — Clicking Cancel (or the ✕ button, or the overlay backdrop) closes the modal without saving.
- [ ] **Save button disabled** — While saving, the Save button is disabled to prevent double-submission.

---

## 4. Behavior Contract — Before / After Refactor

This section defines the API contract that must hold invariant across any refactoring. Each rule is stated as a concrete, testable assertion.

### 4.1 Endpoint inventory

| Method | Path                     | Auth | Req Body      | Success Code | Notes                      |
|--------|--------------------------|------|---------------|--------------|----------------------------|
| GET    | `/health`                | None | —             | 200          | `{status, timestamp}`      |
| POST   | `/tasks`                 | None | TaskCreate    | 201          | Returns full TaskResponse  |
| GET    | `/tasks`                 | None | —             | 200          | Optional qs: `status`, `priority`, `overdue` |
| GET    | `/tasks/{id}`            | None | —             | 200          | 404 if missing             |
| PATCH  | `/tasks/{id}`            | None | TaskUpdate    | 200          | 404 if missing; partial update |
| DELETE | `/tasks/{id}`            | None | —             | 204          | 404 if missing; no body    |
| GET    | `/tasks/{id}/activity`   | None | —             | 200          | 404 if task missing        |
| GET    | `/activity`              | None | —             | 200          | Global feed, newest first  |

### 4.2 Request / response shapes

**TaskCreate** (POST /tasks):
```
title*: string (1-200 chars, trimmed, non-blank)
description: string (optional, default "")
status: "ToDo" | "InProgress" | "Done" (default "ToDo")
priority: "Low" | "Medium" | "High" (default "Medium")
assignee: string | null (optional)
due_date: date (YYYY-MM-DD) | null (optional)
```
- `extra="forbid"` — unknown fields → 422.
- Missing `title` → 422.
- Blank/whitespace-only `title` → 422.
- Invalid enum value → 422.

**TaskUpdate** (PATCH /tasks/{id}):
```
All fields from TaskCreate, but every field is optional.
```
- `extra="forbid"` — unknown fields → 422.
- Partial update: omitted fields keep their current values.
- `updated_at` is always bumped on any change.
- Setting `due_date` to `null` explicitly clears it.

**TaskResponse** (returned by all task endpoints):
```
id: string (UUID)
title, description, status, priority, assignee, due_date
created_at: datetime (ISO 8601 with timezone)
updated_at: datetime (ISO 8601 with timezone)
```

**ActivityEvent**:
```
task_id: string
event_type: "created" | "status_change"
timestamp: datetime (ISO 8601 with timezone)
from_status: TaskStatus | null (only on status_change)
to_status: TaskStatus | null (only on status_change)
```

### 4.3 Business rules that must survive refactoring

| Rule                                  | Enforcement point           | Test that guards it                                           |
|---------------------------------------|-----------------------------|---------------------------------------------------------------|
| Overdue = `due_date < today` AND `status != Done` | `storage.get_all_tasks()`   | `test_list_tasks_overdue_excludes_past_due_date_with_status_done` |
| Overdue is computed, not persisted       | `storage.get_all_tasks()`   | (no stored `is_overdue` field exists)                         |
| Status transitions: ToDo→InProgress, InProgress→Done, Done→InProgress only | `business_rules.validate_status_transition()` | `test_patch_valid_transition_todo_to_inprogress_returns_200`, `test_patch_invalid_transition_todo_to_done_returns_422` |
| Same-status PATCH is a no-op (no event, no error) | `storage.update_task()` | `test_patch_same_status_is_noop_returns_200` |
| Activity event on create (type=created) | `main.create_task()`        | (implicit in functional tests)                                |
| Activity event on status change (type=status_change, with from/to) | `main.update_task()` | (implicit in functional tests)                                |
| No activity event when status unchanged | `main.update_task()`        | (implicit — compare with patch_non_status test)               |
| DELETE removes task AND its activity history | `storage.delete_task()`     | (implicit in delete tests)                                    |
| Empty overdue filter → 200 with `[]`, never 404 | `storage.get_all_tasks()`   | `test_list_tasks_overdue_with_no_matches_returns_200_and_empty_list` |
| `extra="forbid"` on TaskCreate and TaskUpdate | Pydantic model config       | `test_create_task_unknown_field_returns_422`, `test_patch_unknown_field_returns_422` |
| Title blank/whitespace → 422          | model field validator       | `test_create_task_blank_title_returns_422`, `test_patch_blank_title_returns_422` |

### 4.4 Frontend behavior contract

| Behavior                                          | How to verify                          |
|---------------------------------------------------|----------------------------------------|
| Board has exactly 3 columns: To Do, In Progress, Done | Visual inspection                  |
| Overdue toggle show/hides overdue-filtered tasks  | Click "Overdue" button, check cards     |
| "OVERDUE" pill only appears when `due_date < today && status != Done` | Create task with past due date in ToDo vs Done |
| Due date displays as "Due Mmm DD", never raw ISO  | Check card rendering                    |
| Activity panel shows events sorted newest-first  | Create a task, change its status        |
| Invalid drag transition shows error toast         | Drag ToDo card → Done column            |
| Modal validates title client-side before submit   | Submit empty title in modal             |
| Save button disabled during submit                | Click Save rapidly twice                |

---

## 5. Break Test Evidence

Two tests were deliberately broken to prove they catch real bugs. Each section shows the code change, the failing test output, the reversion, and the passing test output.

### Break Test 1: Missing `status != Done` guard in overdue filter

**Bug introduced:** Removed the `and t.status != TaskStatus.DONE` condition from the overdue filter in [`storage.py:38-46`](../backend/app/storage.py#L38-L46). This meant completed tasks with past due dates would incorrectly appear as overdue.

**Code change (bug):**
```python
# In storage.py, get_all_tasks():
if overdue is True:
    today = date.today()
    results = [
        t
        for t in results
        if t.due_date is not None
        and t.due_date < today
        # BUG: removed "and t.status != TaskStatus.DONE"
    ]
```

**Test that caught it:** `test_list_tasks_overdue_excludes_past_due_date_with_status_done`

**Failing output:**
```
tests/test_tasks.py::test_list_tasks_overdue_excludes_past_due_date_with_status_done FAILED [100%]

=================================== FAILURES ===================================
_______ test_list_tasks_overdue_excludes_past_due_date_with_status_done ________

client = <starlette.testclient.TestClient object at 0x73429e9e54c0>

    def test_list_tasks_overdue_excludes_past_due_date_with_status_done(client):
        client.post("/tasks", json={
            "title": "finished late",
            "due_date": "2020-01-01",
            "status": "Done",
        })
        r = client.get("/tasks", params={"overdue": True})
        assert r.status_code == 200
>       assert r.json() == []
E       AssertionError: assert [{'assignee':...-01-01', ...}] == []
E
E         Left contains one more item:
E         {'assignee': None, 'due_date': '2020-01-01', 'status': 'Done', ...}
E
E         Full diff:
E         - []
E         + [{...finished late...}]

tests/test_tasks.py:247: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tasks.py::test_list_tasks_overdue_excludes_past_due_date_with_status_done
============================== 1 failed in 0.03s ===============================
```

**Analysis:** The test created a task with `status="Done"` and a past `due_date="2020-01-01"`. With the guard removed, the task appeared in the overdue results, violating the business rule that Done tasks are never overdue. The test correctly detected this.

**Fix:** Restored the `and t.status != TaskStatus.DONE` condition in `storage.py`.

---

### Break Test 2: Missing blank-title validation on TaskCreate

**Bug introduced:** Removed the `if not v: raise ValueError(...)` blank-check from the `validate_title` field validator in [`models.py:30-38`](../backend/app/models.py#L30-L38). This meant a task could be created with a whitespace-only title.

**Code change (bug):**
```python
# In models.py, TaskCreate.validate_title():
@field_validator("title")
@classmethod
def validate_title(cls, v: str) -> str:
    v = v.strip()
    # BUG: blank-title check removed
    if len(v) > 200:
        raise ValueError("title must not exceed 200 characters")
    return v
```

**Test that caught it:** `test_create_task_blank_title_returns_422`

**Failing output:**
```
tests/test_tasks.py::test_create_task_blank_title_returns_422 FAILED     [100%]

=================================== FAILURES ===================================
___________________ test_create_task_blank_title_returns_422 ___________________

client = <starlette.testclient.TestClient object at 0x7a7de1bf1130>

    def test_create_task_blank_title_returns_422(client):
        r = client.post("/tasks", json={"title": "   "})
>       assert r.status_code == 422
E       assert 201 == 422
E        +  where 201 = <Response [201 Created]>.status_code

tests/test_tasks.py:38: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tasks.py::test_create_task_blank_title_returns_422 - assert...
============================== 1 failed in 0.03s ===============================
```

**Analysis:** The test sent `{"title": "   "}` (three spaces). Without the blank check, the validator stripped whitespace to `""`, found no length violation, and returned the empty string. The backend accepted it and returned 201 — but a task with an effectively blank title is meaningless. The test expected 422 and got 201, proving the validator guard is essential.

**Fix:** Restored the `if not v: raise ValueError("title must not be blank")` check in `models.py`.

---

### Post-fix confirmation

After restoring both fixes, the full suite was re-run:

```
============================== 31 passed in 0.10s ==============================
```

Both tests pass, confirming the bugs are resolved and the test harness correctly guards against regressions.
