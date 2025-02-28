import uuid

from typing import Annotated
from fastapi import APIRouter, Depends
from src.services import UserService
from src.models import user as user_models
from src.api.dependencies import SessionDep, CurrentUser

router = APIRouter(
    prefix="/users",
    tags=["User Endpoints"],
    responses={
        201: {"description": "User created successfully"},
        404: {"description": "User not found"},
    },
)


# annotate dependencies
def get_user_service(session: SessionDep):
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.get(
    "/",
    response_model=user_models.UsersPublicResponse,
)
async def get_users(
    user_service: UserServiceDep,
    skip: int = 0,
    limit: int = 10,
    query: user_models.UserSearch = Depends(),
):
    """
    Get all user records
    """
    data = await user_service.get_all_users(skip=skip, limit=limit, query=query)

    return user_models.UsersPublicResponse(
        **vars(data), message="Users retrieved successfully"
    )


@router.get("/me", response_model=user_models.UserPublicResponse)
async def get_user_me(current_user: CurrentUser, user_service: UserServiceDep):
    """
    Get current user.
    """
    user = await user_service.get_user_by_id(id=current_user.sub)

    return user_models.UserPublicResponse(
        message="Current user details retrieved successfully",
        data=user,
    )


@router.get(
    "/{id}/",
    response_model=user_models.UserPublicResponse,
)
async def get_user(
    id: uuid.UUID,
    user_service: UserServiceDep,
):
    """
    Get a user record
    """
    user = await user_service.get_user_by_id(id=id)

    return user_models.UserPublicResponse(
        message="User retrieved successfully",
        data=user,
    )


@router.patch(
    "/{id}/",
    response_model=user_models.UserPublicResponse,
)
async def update_user(
    id: uuid.UUID,
    data: user_models.UserUpdatePublic,
    user_service: UserServiceDep,
):
    """
    Update a user record
    """
    user = await user_service.update_user_by_id(id=id, data=data)

    return user_models.UserPublicResponse(
        message="User updated successfully",
        data=user,
    )
