from typing import Any
from enum import StrEnum
from sqlmodel import SQLModel
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict

# all tables created in the application should be imported here to allow alembic to pick it up easily when using revision autogenerate
from .user import User as User
from .item import Item as Item


# Generic message for all API responses
class Message(SQLModel):
    message: str


class SystemHealth(SQLModel):
    status: str = "healthy"
    database: str = "connected"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILED = "FAILURE"


class TaskSubmission(SQLModel):
    task_id: str

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class TaskResult(TaskSubmission):
    task_result: Any
    task_status: str
