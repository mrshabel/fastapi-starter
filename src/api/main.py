from fastapi import APIRouter

# import all routes here
from src.api.routers import health_check, item, user, auth, file, task

api_router = APIRouter(
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized access"},
        403: {"description": "Not enough permissions to perform this request"},
        500: {"description": "Something went wrong"},
        503: {"description": "Service Unavailable"},
    }
)

# register all routes here
api_router.include_router(health_check.router)
api_router.include_router(item.router)
api_router.include_router(user.router)
api_router.include_router(auth.router)
api_router.include_router(file.router)
api_router.include_router(task.router)
