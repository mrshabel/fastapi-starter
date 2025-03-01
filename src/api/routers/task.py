from fastapi import APIRouter
from pydantic import EmailStr
from celery.result import AsyncResult
from src.models import TaskSubmission, TaskResult
from src.tasks import basic as basic_tasks, email as email_tasks

router = APIRouter(
    prefix="/tasks",
    tags=["Long-running Task Endpoints"],
    responses={
        404: {"description": "Task not found"},
    },
)


@router.post(
    "/add",
    response_model=TaskSubmission,
)
async def trigger_add(
    x: int,
    y: int,
):
    """
    Trigger a long-running addition operation
    """
    task = basic_tasks.add_task.delay(x, y)

    return TaskSubmission(task_id=task.id)


@router.post(
    "/email",
    response_model=TaskSubmission,
)
async def trigger_email(recipient: EmailStr):
    """
    Trigger a test email sender
    """
    subject = "Test Email"
    content = """
        Hey there, we are testing our services
    """
    task = email_tasks.send_email_task.delay(
        recipient=recipient, subject=subject, content=content
    )

    return TaskSubmission(task_id=task.id)


@router.get(
    "/status/{id}",
    response_model=TaskResult,
)
async def check_status(id: str):
    """
    Check status of a background running task
    """
    result = AsyncResult(id=id)

    return TaskResult(task_id=id, task_result=result.result, task_status=result.status)
