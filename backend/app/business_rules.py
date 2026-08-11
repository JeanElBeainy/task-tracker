from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    (TaskStatus.TODO, TaskStatus.TODO),
    (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
    (TaskStatus.DONE, TaskStatus.DONE),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Raise 422 if moving from *current* to *new* is not allowed.

    The allowed transitions are:
    - ToDo → InProgress
    - InProgress → Done
    - Done → InProgress
    - Any status → itself (no-op, permitted)

    Args:
        current: The task's current status before the update.
        new: The status the caller wants to apply.

    Raises:
        HTTPException: 422 with a list of valid transitions when the
            requested transition is forbidden.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )