from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    """Workflow states a task can occupy.

    Values are serialized as their enum member names (e.g. "ToDo").
    """

    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    """Priority levels for triage and ordering.

    Values are serialized as their enum member names (e.g. "High").
    """

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    """Payload accepted by POST /tasks."""

    model_config = ConfigDict(extra="forbid")

    title: str  # validated by validate_title
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Strip and validate the task title.

        Args:
            v: Raw title string from the request body.

        Returns:
            The stripped title if valid.
        """
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        if len(v) > 200:
            raise ValueError("title must not exceed 200 characters")
        return v


class TaskUpdate(BaseModel):
    """Payload accepted by PATCH /tasks/{task_id}. Every field is optional."""

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip and validate the task title when provided.

        Args:
            v: Raw title string from the request body, or None if omitted.

        Returns:
            The stripped title if provided and valid, None otherwise.
        """
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("title must not be blank")
            if len(v) > 200:
                raise ValueError("title must not exceed 200 characters")
        return v


class TaskResponse(BaseModel):
    """Schema returned by all task endpoints."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class ActivityEventType(str, Enum):
    CREATED = "created"
    STATUS_CHANGE = "status_change"


class ActivityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    event_type: ActivityEventType
    timestamp: datetime
    from_status: Optional[TaskStatus] = None
    to_status: Optional[TaskStatus] = None
