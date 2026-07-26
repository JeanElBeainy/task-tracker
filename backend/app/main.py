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
    """Basic liveness check for the API."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
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
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.get("/tasks/{task_id}/activity", response_model=list[ActivityEvent], tags=["tasks"])
def get_task_activity(task_id: str) -> list[ActivityEvent]:
    if storage.get_task_by_id(task_id) is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return storage.get_activity(task_id)


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
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
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
