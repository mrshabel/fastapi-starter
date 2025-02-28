from fastapi import APIRouter
from src.api.dependencies import SessionDep
from src.models import SystemHealth
from sqlmodel import select

router = APIRouter(prefix="/health-check", tags=["Health Check Endpoint"])


@router.get("/", response_model=SystemHealth)
async def check_health(session: SessionDep):
    """Check application health"""
    # execute test query to db
    result = await session.exec(select(1))
    result.first()

    return SystemHealth(status="healthy", database="connected")
