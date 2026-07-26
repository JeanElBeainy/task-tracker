# Prompt Log — Mid-Course Project

Selected features: **Due dates + overdue filter**, **Activity log**

> How to use this file: each entry below has a weak version and an improved (fixed) version, ready to run in your editor AI tool. After you actually run the improved prompt, fill in the two blank fields under it — "AI response summary" and "Accepted / edited / rejected" — with what really happened. Don't backfill these from memory later; jot them down right after each run.

---

## Feature 1: Due dates + overdue filter

### Prompt 1.1 — Backend implementation

**Weak version:**
```
Add due dates to my task tracker.
```

**Improved (fixed) version:**
```
In app/main.py, extend the Task Tracker to support due dates.

Context:
- Task model currently has: id, title, description, status, priority, assignee.
- Status values are exactly: ToDo, InProgress, Done.
- This is the Module 2 in-memory FastAPI backend — no database.

Task:
- Add an optional due_date field (Pydantic date type) to the create and update models.
- A task is "overdue" if due_date < today AND status != Done. Compute this at request
  time — do not persist an is_overdue field.
- Add an optional overdue query parameter to GET /tasks. When overdue=true, return
  only tasks meeting the overdue definition above.

Constraints:
- Do not add a stored/persisted overdue boolean field.
- Do not add reminders, notifications, or email/alert logic.
- Preserve existing endpoints and response shapes for fields not related to due dates.
- Return a focused diff, not a full file rewrite.

Output format:
Explain the change in 2-3 bullets, then provide the diff.
```

**AI response summary:**

Change summary

due_date is an optional Pydantic date field on TaskCreate, TaskUpdate, and TaskResponse — defaults to None so existing callers are unaffected.
Overdue is computed at request time — in get_all_tasks, when overdue=true, it filters to tasks where due_date is set, due_date < today, and status != Done. Nothing is persisted.
GET /tasks?overdue=true — the new query parameter pipes through from the route handler to storage, composing with existing status and priority filters.
The diff:


--- a/backend/app/models.py
+++ b/backend/app/models.py
@@ -1,4 +1,4 @@
-from datetime import datetime
+from datetime import date, datetime
 from enum import Enum
 from typing import Optional
 
@@ -25,6 +25,7 @@ class TaskCreate(BaseModel):
     priority: TaskPriority = TaskPriority.MEDIUM
     assignee: Optional[str] = None
+    due_date: Optional[date] = None
 
     @field_validator("title")
@@ -46,6 +47,7 @@ class TaskUpdate(BaseModel):
     assignee: Optional[str] = None
+    due_date: Optional[date] = None
 
     @field_validator("title")
@@ -69,6 +71,7 @@ class TaskResponse(BaseModel):
     assignee: Optional[str]
+    due_date: Optional[date] = None
     created_at: datetime

--- a/backend/app/storage.py
+++ b/backend/app/storage.py
@@ -1,4 +1,4 @@
 import uuid
-from datetime import datetime, timezone
+from datetime import date, datetime, timezone
 from typing import Optional
 
@@ -16,6 +16,7 @@ def add_task(payload: TaskCreate) -> TaskResponse:
         assignee=payload.assignee,
+        due_date=payload.due_date,
         created_at=now,
@@ -27,6 +28,7 @@ def get_all_tasks(
     priority: Optional[TaskPriority] = None,
+    overdue: Optional[bool] = None,
 ) -> list[TaskResponse]:
     results = list(_tasks.values())
@@ -35,6 +37,13 @@ def get_all_tasks(
         results = [t for t in results if t.priority == priority]
+    if overdue is True:
+        today = date.today()
+        results = [
+            t
+            for t in results
+            if t.due_date is not None
+            and t.due_date < today
+            and t.status != TaskStatus.DONE
+        ]
     return results

--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -46,6 +46,7 @@ def list_tasks(
     priority: TaskPriority | None = None,
+    overdue: bool | None = None,
 ) -> list[TaskResponse]:
-    return storage.get_all_tasks(status=status, priority=priority)
+    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue)

**Accepted / edited / rejected:** Accepted, works perfectly.

---

### Prompt 1.2 — Tests

**Weak version:**
```
Write tests for the due date feature.
```

**Improved (fixed) version:**
```
Read the existing tests in tests/test_tasks.py and follow the same fixture/TestClient
pattern to add tests for the due date + overdue filter feature.

Context:
- due_date is optional, ISO format (YYYY-MM-DD).
- Overdue = due_date < today AND status != Done, computed at request time.
- GET /tasks?overdue=true filters to only overdue tasks.

Task: write ONE pytest test per scenario, five total:
1. Valid due_date is accepted and returned on create.
2. Invalid due_date format returns 422.
3. A task with a past due_date and status ToDo is detected as overdue.
4. A task with a past due_date but status Done is NOT detected as overdue.
5. GET /tasks?overdue=true with no overdue tasks returns 200 and [].

Constraints:
- Use the existing fixture style, do not introduce new test utilities.
- Assert both status code and the relevant response field.
- Do not modify app code, only the test file.

Output format:
Return all five test functions in one code block, clearly separated.
```

**AI response summary:**

Now I have full context — the fixture pattern, the client fixture, created_task fixture, and how storage._reset() runs before/after each test. Here are the five tests:


# ---------------------------------------------------------------------------
# POST /tasks — due_date
# ---------------------------------------------------------------------------

def test_create_task_with_valid_due_date_returns_201_with_date(client):
    payload = {
        "title": "Due date task",
        "due_date": "2025-12-31",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == "2025-12-31"


def test_create_task_with_invalid_due_date_format_returns_422(client):
    payload = {
        "title": "Bad date",
        "due_date": "12/31/2025",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks — overdue filter
# ---------------------------------------------------------------------------

def test_list_tasks_overdue_includes_past_due_date_with_status_todo(client):
    client.post("/tasks", json={
        "title": "overdue task",
        "due_date": "2020-01-01",
        "status": "ToDo",
    })
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "overdue task"
    assert data[0]["due_date"] == "2020-01-01"


def test_list_tasks_overdue_excludes_past_due_date_with_status_done(client):
    client.post("/tasks", json={
        "title": "finished late",
        "due_date": "2020-01-01",
        "status": "Done",
    })
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_overdue_with_no_matches_returns_200_and_empty_list(client):
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    assert r.json() == []
What each test covers:

test_create_task_with_valid_due_date_returns_201_with_date — Sends due_date: "2025-12-31" (ISO format) in the POST body, asserts 201 and that the response includes the same due_date string.

test_create_task_with_invalid_due_date_format_returns_422 — Sends due_date: "12/31/2025" (non-ISO format), Pydantic rejects it as not a valid date, asserts 422.

test_list_tasks_overdue_includes_past_due_date_with_status_todo — Creates a task with due_date: "2020-01-01" and status: "ToDo", then queries GET /tasks?overdue=true. The task is in the past and not Done, so it's returned.

test_list_tasks_overdue_excludes_past_due_date_with_status_done — Creates a task with due_date: "2020-01-01" and status: "Done". Even though the due date is in the past, the Done status means it's not overdue, so ?overdue=true returns [].

test_list_tasks_overdue_with_no_matches_returns_200_and_empty_list — Queries GET /tasks?overdue=true on an empty store (no tasks exist), asserts 200 and [].

**Accepted / edited / rejected:** accepted, all tests ran perfectly.

---

### Prompt 1.3 — Frontend integration

**Weak version:**
```
add it to the frontend so that it can work.
```

**Weak version's output:**
Frontend changes (index.html)
3 areas touched, all localized:

Modal form — a new <input type="date" id="field-due-date"> field sits between Assignee and the footer buttons. Both openCreateModal (clears it) and openEditModal (populates from task.due_date) are wired up. handleModalSubmit includes it in the payload as due_date (or null when empty).

Card display — buildCard() now renders a .due-date span in the meta row when task.due_date is set. If the date is in the past and the task isn't Done, it gets the .overdue class — red text, bold weight, and a ⚠ prefix.

CSS — three short rules for .due-date (muted by default), .due-date.overdue (red + bold), and .due-date.overdue::before (the warning icon).

Helper — formatDate(isoDate) converts YYYY-MM-DD to a short locale string (e.g. "Jul 28, 2026") for display.


**Improved (fixed) version:**
```
The changes have been already done, but please check it again and refine if needed:
Extend the existing frontend/index.html to support due dates, without breaking
existing board behavior.

Context:
- Existing behavior to preserve: three status columns, priority sorting, loading/
  empty/ready/error states, drag-and-drop with rollback, create/edit modal with title
  validation and 422 handling.
- Backend now accepts due_date (YYYY-MM-DD, optional) on create/update, and supports
  GET /tasks?overdue=true.

Task:
- Add a due_date input to the create/edit modal.
- Show the due date on each card in a readable format (e.g. "Due Jul 30"); show
  nothing if there is no due date.
- Show a distinct "Overdue" pill on cards where the backend data indicates the task is
  overdue.
- Add a filter toggle that calls GET /tasks?overdue=true and re-renders the board with
  only those results, while keeping all three columns visible.

Constraints:
- Do not change existing class names, IDs, or data-* attributes used elsewhere.
- Do not remove or alter drag-and-drop, modal validation, or the four UI states.
- Return a focused diff.

Output format:
Explain the change in 2-3 bullets, then the diff.
```

**AI response summary:**

Here's a summary of the three refinements made:

Added the missing overdue filter toggle — the original changes had no way to trigger GET /tasks?overdue=true. Added a pill-shaped "Overdue" button next to "+ New Task" that toggles the filter on/off, with active-state styling and a loadTasks() re-fetch.
Replaced the inline overdue style with a distinct "Overdue" pill — the spec calls for a pill/badge, not just red-styled date text. Now buildCard renders a separate .overdue-pill <span> with the text "Overdue" before the date, using the same red-tint pill style as the priority badges.
Dropped the year from formatDate — changed from "Jul 30, 2026" to "Jul 30" to match the "Due Jul 30" example from the spec and keep cards compact.
Here's the full diff of all changes:


--- a/frontend/index.html
+++ b/frontend/index.html
@@ -299,17 +299,14 @@
       white-space: nowrap;
     }
 
-    .due-date.overdue {
-      color: #ad281a;
+    .overdue-pill {
+      display: inline-flex;
+      align-items: center;
+      font-size: 0.6875rem;
       font-weight: 650;
-    }
-
-    .due-date.overdue::before {
-      content: "⚠";
-      font-size: 0.75rem;
+      text-transform: uppercase;
+      letter-spacing: 0.03em;
+      padding: 3px 8px;
+      border-radius: 999px;
+      background: #fdecea;
+      color: #ad281a;
     }
 
     /* ── edit button ────────────────────────────────────────────────── */
@@ -480,6 +477,34 @@
       box-shadow: 0 1px 4px rgba(91,91,214,.2);
     }
 
+    .btn-filter-overdue {
+      display: inline-flex;
+      align-items: center;
+      gap: 6px;
+      padding: 9px 18px;
+      border: 1.5px solid var(--color-border);
+      border-radius: 999px;
+      background: var(--color-surface);
+      color: var(--color-muted);
+      font-size: 0.8125rem;
+      font-weight: 600;
+      cursor: pointer;
+      transition: all 0.2s var(--ease-out);
+      letter-spacing: -0.01em;
+    }
+
+    .btn-filter-overdue:hover {
+      border-color: #e8a59e;
+      color: #ad281a;
+    }
+
+    .btn-filter-overdue.active {
+      background: #fdecea;
+      border-color: #f5c6c2;
+      color: #ad281a;
+    }
+
     /* ------------------------------------------------------------------ */
     /* MODAL                                                               */
     /* ------------------------------------------------------------------ */
@@ -711,6 +736,7 @@
     <p class="subtitle">Manage your work with a simple Kanban board</p>
     <button id="btn-new-task" class="btn-new-task">+ New Task</button>
+    <button id="btn-filter-overdue" class="btn-filter-overdue">Overdue</button>
   </header>
 
   <!-- ================================================================= -->
@@ -821,6 +847,7 @@
 
     let tasks = [];
     let editingTaskId = null;   // null = create mode; set = edit mode
+    let overdueFilterActive = false;
 
     /* ------------------------------------------------------------------ */
     /* HELPERS                                                             */
@@ -847,7 +874,7 @@
     function formatDate(isoDate) {
       if (!isoDate) return "";
       const d = new Date(isoDate + "T00:00:00");
-      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
+      return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
     }
 
     /** Return a stable id-based comparator for tie-breaking. */
@@ -860,8 +887,9 @@
     /* FETCH                                                               */
     /* ------------------------------------------------------------------ */
 
-    async function fetchTasks() {
-      const response = await fetch(`${API_BASE}/tasks`);
+    async function fetchTasks(params = {}) {
+      const url = new URL(`${API_BASE}/tasks`);
+      if (params.overdue) url.searchParams.set("overdue", "true");
+      const response = await fetch(url.toString());
       if (!response.ok) {
         throw new Error(`Fetch failed: ${response.status} ${response.statusText}`);
       }
@@ -1017,13 +1045,15 @@
       if (task.due_date) {
-        const dueEl = document.createElement("span");
-        dueEl.className = "due-date";
         const dueDate = new Date(task.due_date + "T00:00:00");
         const today = new Date();
         today.setHours(0, 0, 0, 0);
         if (dueDate < today && task.status !== "Done") {
-          dueEl.classList.add("overdue");
+          const overduePill = document.createElement("span");
+          overduePill.className = "overdue-pill";
+          overduePill.textContent = "Overdue";
+          metaLeft.appendChild(overduePill);
         }
+        const dueEl = document.createElement("span");
+        dueEl.className = "due-date";
         dueEl.textContent = formatDate(task.due_date);
         metaLeft.appendChild(dueEl);
       }
@@ -1332,7 +1362,9 @@
     async function loadTasks() {
       setBoardState("loading");
       try {
-        await fetchTasks();
+        const params = {};
+        if (overdueFilterActive) params.overdue = true;
+        await fetchTasks(params);
         renderBoard(tasks);
         setBoardState(tasks.length === 0 ? "empty" : "ready");
       } catch (err) {
@@ -1349,6 +1381,13 @@
     // New Task button
     document.getElementById("btn-new-task").addEventListener("click", openCreateModal);
 
+    // Overdue filter toggle
+    document.getElementById("btn-filter-overdue").addEventListener("click", function () {
+      overdueFilterActive = !overdueFilterActive;
+      this.classList.toggle("active", overdueFilterActive);
+      loadTasks();
+    });
+
     // Modal dismissals
Everything preserved: three status columns, priority sorting, loading/empty/ready/error states, drag-and-drop with rollback, modal validation and 422 handling — none of those code paths were touched. All 28 backend tests pass.

**Accepted / edited / rejected:** edited after sending the weak prompt (output is up with the weak prompt).

---

## Feature 2: Activity log

### Prompt 2.1 — Backend implementation

**Weak version:**
```
Add an activity log to my backend.
```

**Improved (fixed) version:**
```
In app/main.py, add an activity log to the Task Tracker.

Context:
- In-memory storage, same pattern as the existing task store.
- Task lifecycle actions: create (POST /tasks), update (PATCH /tasks/{id}, including
  status changes), delete (DELETE /tasks/{id}).

Task:
- Store activity events in a separate in-memory structure, one event per: task
  creation, and status change specifically (not every field edit).
- Each event includes: task id, event type (created | status_change), timestamp, and
  for status_change, the from/to status values.
- Add GET /tasks/{id}/activity returning that task's events oldest-to-newest. Return
  404 if the task id does not exist.
- Deleting a task does not need to retain a queryable activity event — confirm this
  matches the intended behavior before implementing (see note below).

Constraints:
- Do not build a generic event-sourcing system or rebuild task state from events.
- Do not log every field edit — only creation and status transitions.
- Do not add persistence beyond in-memory storage.

Output format:
Explain the change in 2-3 bullets, then provide the diff.
```

**AI response summary:**

Summary

Activity log stores creation + status-change events in a new _activities dict (keyed by task_id) alongside the existing _tasks dict — same in-memory pattern. Non-status field edits and same-status no-ops produce no event.
New GET /tasks/{id}/activity endpoint returns events oldest-to-newest, with a 404 if the task doesn't exist. Each event carries task_id, event_type, timestamp, and (for status changes) from_status / to_status.
Deletion cleans up activity — storage.delete_task drops the task's activity events, so deleted tasks leave no queryable history (matching the ADR decision).

**Accepted / edited / rejected:** accepted

---

### Prompt 2.2 — Tests

**Weak version:**
```
Test the activity log.
```

**Improved (fixed) version:**
```
Read the existing tests in tests/test_tasks.py and follow the same pattern to add
tests for the activity log.

Context:
- Events are created on: task creation (type created), and status change (type
  status_change, with from/to fields).
- GET /tasks/{id}/activity returns events oldest-to-newest, 404 for a missing task.
- A PATCH that does not change status should NOT create a status_change event.

Task: write ONE pytest test per scenario, four total:
1. Creating a task generates exactly one "created" event.
2. Changing status via PATCH generates a status_change event with correct from/to.
3. A PATCH that only changes description (not status) does not add a new event.
4. GET /tasks/{id}/activity for a non-existent task id returns 404.

Constraints:
- Use the existing fixture/TestClient pattern.
- Assert status code and the relevant response body fields, not just "no error".
- Do not modify app code.

Output format:
Return all four test functions in one code block.
```

**AI response summary:**

Here are the four tests, following the existing conventions (top-level functions, client/created_task fixtures, specific JSON field assertions, section comment):


# ---------------------------------------------------------------------------
# GET /tasks/{id}/activity
# ---------------------------------------------------------------------------

def test_create_task_generates_created_event(client):
    """POST /tasks produces exactly one activity event of type 'created'."""
    r = client.post("/tasks", json={"title": "activity test"})
    assert r.status_code == 201
    task_id = r.json()["id"]

    r = client.get(f"/tasks/{task_id}/activity")
    assert r.status_code == 200
    events = r.json()
    assert len(events) == 1
    assert events[0]["event_type"] == "created"
    assert events[0]["task_id"] == task_id
    assert "timestamp" in events[0]
    assert events[0]["from_status"] is None
    assert events[0]["to_status"] is None


def test_status_change_generates_status_change_event(client, created_task):
    """PATCH that changes status logs a status_change event with correct from/to."""
    task_id = created_task["id"]

    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200

    r = client.get(f"/tasks/{task_id}/activity")
    assert r.status_code == 200
    events = r.json()
    assert len(events) == 2
    status_event = events[1]
    assert status_event["event_type"] == "status_change"
    assert status_event["task_id"] == task_id
    assert status_event["from_status"] == "ToDo"
    assert status_event["to_status"] == "InProgress"
    assert "timestamp" in status_event


def test_patch_without_status_change_does_not_add_event(client, created_task):
    """PATCH that only changes description does not create a new activity event."""
    task_id = created_task["id"]

    r = client.patch(f"/tasks/{task_id}", json={"description": "updated description"})
    assert r.status_code == 200

    r = client.get(f"/tasks/{task_id}/activity")
    assert r.status_code == 200
    events = r.json()
    assert len(events) == 1
    assert events[0]["event_type"] == "created"


def test_activity_for_nonexistent_task_returns_404(client):
    """GET /tasks/{id}/activity returns 404 with detail when the task does not exist."""
    r = client.get("/tasks/nonexistent-id/activity")
    assert r.status_code == 404
    assert "detail" in r.json()

**Accepted / edited / rejected:** accepted
---

### Prompt 2.3 — Frontend integration

**Weak version:**
```
Show the activity log in the UI.
```

**Improved (fixed) version:**
```
Extend the existing frontend/index.html to show a task's activity history, without
breaking existing board or modal behavior.

Context:
- Existing behavior to preserve: three columns, priority sorting, four UI states,
  drag-and-drop with rollback, create/edit modal with validation and 422 handling.
- Backend now exposes GET /tasks/{id}/activity, returning a chronological list of
  events with type, timestamp, and from/to status for status_change events.

Task:
- Add a small activity section inside the edit modal (or a lightweight side panel)
  that fetches and displays that task's activity when the modal opens in edit mode.
- Keep it to a simple chronological list — no pagination, no filtering.
- Do not fetch or show activity in create mode, since a new task has no history yet.

Constraints:
- Do not change existing class names, IDs, or data-* attributes.
- Do not remove or alter drag-and-drop, validation, or the four UI states.
- Return a focused diff.

Output format:
Explain the change in 2-3 bullets, then the diff.
```

**AI response summary:**

Summary

CSS-only toggle: The #activity-section block is display: none by default and becomes visible via .visible class — no JS removes it from the DOM. Create mode never shows it because clearActivity() strips the class and empties the list.
Edit-mode fetch: When openEditModal fires, fetchActivity(task.id).then(renderActivity) hits GET /tasks/{id}/activity asynchronously. On success it builds a chronological list of badge + timestamp + (for status changes) from → to detail rows.
No touchpoints broken: The activity section is appended after </form> inside .modal, outside the form. No existing IDs, class names, data attributes, drag handlers, validation logic, or board states are modified. All existing behavior — three columns, priority sort, four UI states, drag-and-drop with rollback, modal validation with 422 handling — is untouched.

**Accepted / edited / rejected:**

edited:
"""Add 1 general activity block that shows all activity done for all tasks"""

output:

Summary

New GET /activity endpoint returns every event from all existing tasks as a flat list, newest-first. Deleted-task events are naturally absent since delete_task removes them from _activities.
Right-side panel in the board — a fixed-width aside.activity-panel sits alongside the three columns with its own header and scrollable list. Each row shows an event badge, timestamp, task title (resolved client-side from the tasks array), and for status changes a from → to detail.
Refreshes on every mutation path — loadTasks() calls fetchGlobalActivity().then(renderGlobalActivity) after board render (covers page load, overdue toggle, create/update via modal), and handleDrop() does the same after a successful status-change PATCH. No fetch happens on create-only modal open (the panel is independent of the modal).