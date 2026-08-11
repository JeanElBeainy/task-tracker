from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.business_rules import validate_status_transition
from app.models import ActivityEvent, ActivityEventType, TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app import storage

# Load variables from .env (e.g. PORT, APP_ENV) into the environment
load_dotenv()

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Basic liveness check for the API.

    Returns:
        A dict with ``status`` ("ok") and a UTC ``timestamp``.

    Example:
        GET /health → 200

        {"status": "ok", "timestamp": "2026-08-11T12:34:56.789Z"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload: TaskCreate body with at minimum a non-blank title.

    Returns:
        The created TaskResponse, including a generated UUID id and
        UTC created_at / updated_at timestamps.

    Example:
        POST /tasks
        {"title": "Buy groceries", "priority": "High"}
        → 201
    """
    task = storage.add_task(payload)
    storage.add_activity_event(task.id, ActivityEvent(
        task_id=task.id,
        event_type=ActivityEventType.CREATED,
        timestamp=task.created_at,
    ))
    return task


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """List tasks, with optional status, priority, and overdue filters.

    Args:
        status: If provided, return only tasks matching this status.
        priority: If provided, return only tasks matching this priority.
        overdue: If provided, return only tasks that are overdue.

    Returns:
        A (possibly empty) list of TaskResponse objects.

    Example:
        GET /tasks?status=ToDo&priority=High → 200
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by its id.

    Args:
        task_id: UUID string of the task to fetch.

    Returns:
        The matching TaskResponse.

    Raises:
        HTTPException: 404 if no task with the given id exists.

    Example:
        GET /tasks/550e8400-e29b-41d4-a716-446655440000 → 200
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.get("/tasks/{task_id}/activity", response_model=list[ActivityEvent], tags=["tasks"])
def get_task_activity(task_id: str) -> list[ActivityEvent]:
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return storage.get_activity(task_id)


@app.get("/activity", response_model=list[ActivityEvent], tags=["tasks"])
def get_global_activity() -> list[ActivityEvent]:
    return storage.get_all_activity()


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update an existing task.

    Only the fields present in the request body are changed; omitted
    fields keep their current values. If ``status`` is included the
    transition is validated against the allowed set (see
    :func:`app.business_rules.validate_status_transition`).

    Args:
        task_id: UUID string of the task to update.
        payload: TaskUpdate body with the fields to change.

    Returns:
        The updated TaskResponse with a refreshed updated_at timestamp.

    Raises:
        HTTPException: 404 if the task does not exist.
        HTTPException: 422 if the requested status transition is invalid.

    Example:
        PATCH /tasks/550e8400... {"status": "Done"} → 200
    """
    existing = storage.get_task_by_id(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    if payload.status is not None:
        validate_status_transition(existing.status, payload.status)
    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    if payload.status is not None and payload.status != existing.status:
        storage.add_activity_event(task_id, ActivityEvent(
            task_id=task_id,
            event_type=ActivityEventType.STATUS_CHANGE,
            timestamp=datetime.now(timezone.utc),
            from_status=existing.status,
            to_status=payload.status,
        ))
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by its id.

    Args:
        task_id: UUID string of the task to delete.

    Returns:
        None (responds with 204 No Content on success).

    Raises:
        HTTPException: 404 if the task does not exist.

    Example:
        DELETE /tasks/550e8400-e29b-41d4-a716-446655440000 → 204
    """
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
