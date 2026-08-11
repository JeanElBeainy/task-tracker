# Mini-ADR: Mid-Course Project

**Features:** Due dates + overdue filter, Activity log
**Status:** Draft, pending your review before implementation

---

## 1. Due dates + overdue filter

### Decision
- Add `due_date: date | None` to the task model (Pydantic `date` type, not a raw string), validated on both create and update.
- **Overdue is computed at request time, not stored.** A task is overdue if `due_date < today` and `status != Done`. This is calculated wherever it's needed (card rendering data, `GET /tasks?overdue=true`) rather than persisted as a field.
- Add `overdue` as an optional query parameter on `GET /tasks`.

### Why
- Computing on read means the value can never go stale — no risk of a task staying flagged "overdue" after its status changes to `Done`, since there's no cached boolean to forget to update.
- Keeps the storage model minimal, consistent with the in-memory, no database approach from Module 2.

### Alternatives considered
- **Persist an `is_overdue` boolean, recalculated on every write.** Rejected, because it introduces a value that can silently drift out of sync with "today" if the field isn't touched (e.g. a task just sitting untouched past its due date would show a stale `false` until the next write). Compute-on-read avoids this entirely.
- **AI suggested adding reminder/notification support for overdue tasks** (e.g. a flagged "notify assignee" hook). Rejected as out of scope, because Module 1/2/3 exclude notifications.

---

## 2. Activity log

### Decision
- Store activity events in a single in-memory list (or dict keyed by `task_id`), matching the existing in-memory storage pattern rather than adding a new storage paradigm.
- Generate an event on: task **creation**, and **status change** specifically (not every field edit).
- `GET /tasks/{id}/activity` returns events for one task, 404 if the task doesn't exist.
- **Deletion does not retain a queryable event.** When a task is deleted, its activity history goes with it. *(Flagged in user-stories.md as a real decision worth reconsidering — see below.)*

### Why
- Logging only creation + status change keeps the log meaningful and readable, per the brief's own guidance ("keep it simple and readable"), rather than turning it into a full field-level audit trail.
- Reusing the existing in-memory storage pattern avoids introducing a second storage mechanism this late in the course sequence.

### Alternatives considered
- **AI suggested a full event-sourcing design** (rebuild task state by replaying events rather than storing current state directly). Rejected, because this is a learning project CRUD backend, not an event-sourced system; it would require rewriting the existing task model from Modules 1–2 for no benefit at this scope.
- **AI suggested logging every field change with before/after diffs** (title, description, assignee, priority). Rejected — noisy, and not requested by the feature's "good tests to include" list, which only asks for create/update/delete event coverage at the status level.
- **Global activity log independent of task existence**, so deleted tasks' history survives. Considered but not chosen by default.

---

## Risks if this project grew beyond a learning exercise
- In-memory storage means both due dates and activity history are lost on server restart.
- No pagination on the activity endpoint; would need it if task histories grew large.
- Overdue computation assumes server and client agree on "today": it's fine for a single local deployment, would need timezone handling for a real multi-user product.