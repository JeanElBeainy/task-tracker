# User Stories — Mid-Course Project

Selected features: **Due dates + overdue filter**, **Activity log**

---

## Feature 1: Due dates + overdue filter

### US-1.1: Set a due date on a task
As a team member, I want to set an optional due date when creating or editing a task, so that I can track when work needs to be finished.

**Acceptance criteria**
- `due_date` is optional; a task can be created/updated without one.
- Valid format is an ISO date (`YYYY-MM-DD`).
- Invalid date format returns `422` with a clear error message.
- `due_date` persists correctly after creation and is unaffected by unrelated updates (e.g. changing `status` does not clear `due_date`).

### US-1.2: See overdue tasks flagged on the board
As a team member, I want tasks past their due date to be visually flagged as overdue, so I don't miss urgent work.

**Acceptance criteria**
- A task is "overdue" only if `due_date < today` **and** `status != Done`.
- Overdue tasks show a distinct "Overdue" pill on their card.
- A `Done` task is never shown as overdue, regardless of its due date.

**AI assumption corrected:**
the first draft defined overdue purely as `due_date < today`, which would mark completed tasks overdue forever. Corrected to exclude `Done` tasks.

### US-1.3 — Filter the board to overdue tasks only
As a team member, I want to filter tasks to show only overdue ones, so I can prioritize urgent work first.

**Acceptance criteria**
- `GET /tasks?overdue=true` returns only tasks meeting the overdue definition above.
- If no tasks are overdue, the endpoint returns `200` with `[]`, not `404`.
- The filter can combine with existing status/priority query params (if already supported).

### US-1.4 — Update or clear a task's due date
As a team member, I want to change or remove a task's due date after creation, so I can adjust deadlines as priorities shift.

**Acceptance criteria**
- `PATCH /tasks/{id}` accepts `due_date` (including explicitly setting it to `null`).
- Clearing `due_date` removes the task from "overdue" status.
- An invalid date on update returns `422` and does not modify the stored task.

### US-1.5 — View the due date clearly on a card
As a team member, I want to see a task's due date on its card in a readable format, so I can plan without opening each task individually.

**Acceptance criteria**
- Due date renders as a readable label (e.g. "Due Jul 30"), not a raw ISO string.
- Tasks with no due date show no date label — never "null" or "None" in the UI.

---

## Feature 2: Activity log

### US-2.1 — Record task creation
As a team member, I want an activity event recorded whenever a task is created, so there's a history of when work started.

**Acceptance criteria**
- `POST /tasks` generates one activity event: type `created`, task id, timestamp.
- The event is retrievable via the activity endpoint (see US-2.3).

### US-2.2 — Record status changes with from/to values
As a team member, I want an activity event recorded when a task's status changes, so I can see how it progressed through the board.

**Acceptance criteria**
- `PATCH /tasks/{id}` that changes `status` creates one event of type `status_change` with `from` and `to` values.
- `PATCH` requests that do **not** change `status` (e.g. only editing description) do **not** create a status-change event.

### US-2.3 — View a task's activity history
As a team member, I want to view the activity history for a specific task, so I can understand what happened to it over time.

**Acceptance criteria**
- `GET /tasks/{id}/activity` returns events in chronological order (oldest → newest).
- Each event includes type, timestamp, and relevant detail (e.g. from/to status).
- Requesting activity for a non-existent task returns `404`.

### US-2.4 — Deletion and the activity log
As a team member, I want deletion behavior to be predictable and documented, so I know whether a deleted task's history is preserved.

**Acceptance criteria**
- `DELETE /tasks/{id}` removes the task.
- Decision (documented in the ADR): deleting a task does **not** retain a queryable activity event, since the task record itself no longer exists to query against.
- This behavior is explicit and tested, not incidental.

### US-2.5 — Keep the activity view simple
As a team member, I want the activity panel to be compact and readable, so it doesn't clutter the board or the modal.

**Acceptance criteria**
- Activity appears as a small section in the edit modal or a lightweight side panel.
- No pagination or advanced filtering required; a simple chronological list is enough for this project's scope.