import uuid
from datetime import date, datetime, timezone
from typing import Optional

from app.models import ActivityEvent, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}
_activities: dict[str, list[ActivityEvent]] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Persist a new task and return its full representation.

    Args:
        payload: Validated creation payload with title, status, priority, etc.

    Returns:
        The newly created TaskResponse including generated id and timestamps.
    """
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    """Return every stored task, optionally filtered.

    Args:
        status: If provided, keep only tasks with this status.
        priority: If provided, keep only tasks with this priority.

    Returns:
        A list of TaskResponse objects. When both filters are supplied
        they AND together (a task must match both to be included).
        When neither filter is supplied every task is returned.
    """
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    if overdue is True:
        today = date.today()
        results = [
            t
            for t in results
            if t.due_date is not None
            and t.due_date < today
            and t.status != TaskStatus.DONE
        ]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by its UUID string.

    Args:
        task_id: The UUID string assigned at creation time.

    Returns:
        The matching TaskResponse, or None if no task has that id.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Partially update an existing task.

    Only fields present in *payload* (explicitly set by the caller) are
    applied; omitted fields keep their current values. The ``updated_at``
    timestamp is refreshed automatically on every change.

    Args:
        task_id: UUID string of the task to update.
        payload: Partial update with zero or more fields set.

    Returns:
        The updated TaskResponse, or None if the task_id is unknown.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return task
    updated = task.model_copy(update=update_data)
    updated.updated_at = datetime.now(timezone.utc)
    _tasks[task_id] = updated
    return updated


def add_activity_event(task_id: str, event: ActivityEvent) -> None:
    _activities.setdefault(task_id, []).append(event)


def get_activity(task_id: str) -> list[ActivityEvent]:
    return _activities.get(task_id, [])


def get_all_activity() -> list[ActivityEvent]:
    all_events: list[ActivityEvent] = []
    for events in _activities.values():
        all_events.extend(events)
    all_events.sort(key=lambda e: e.timestamp, reverse=True)
    return all_events


def delete_task(task_id: str) -> bool:
    """Remove a task from the in-memory store.

    Args:
        task_id: UUID string of the task to delete.

    Returns:
        True if the task existed and was removed, False otherwise.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        _activities.pop(task_id, None)
        return True
    return False


def _reset() -> None:
    """Clear all tasks. Intended for test teardown only."""
    _tasks.clear()
    _activities.clear()
