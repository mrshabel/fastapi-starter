from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.services import AuthService
from src.models import user as user_models, Message
from src.api.dependencies import SessionDep, CurrentUser

router = APIRouter(
    prefix="/auth",
    tags=["Auth Endpoints"],
    responses={
        201: {"description": "User signup successfully"},
        404: {"description": "User not found"},
    },
)


# annotate dependencies
def get_auth_service(session: SessionDep):
    return AuthService(session=session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/signup", response_model=user_models.UserPublicResponse, status_code=201)
async def signup(data: user_models.UserRegister, auth_service: AuthServiceDep):
    """
    Create new user account
    """
    user = auth_service.signup(data)

    # TODO: deliver email in background
    return user_models.UserPublicResponse(
        message="Signup completed successfully", data=user
    )


@router.post("/login", response_model=user_models.UserPublicResponse)
async def login(data: user_models.UserLogin, auth_service: AuthServiceDep):
    """
    Login to a user account
    """
    user, access_token, refresh_token = auth_service.login(data)

    return user_models.UserLoginResponse(
        message="Login successfully",
        data=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login/access-token")
async def login_access_token(
    auth_service: AuthServiceDep,
    data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login to a user account for an oauth access token
    """
    access_token = auth_service.login_access_token(data)

    return user_models.Token(access_token=access_token)


@router.patch("/me/deactivate", response_model=Message)
async def deactivate_account(current_user: CurrentUser, auth_service: AuthServiceDep):
    """
    Delete own user
    """
    auth_service.deactivate_account(id=current_user.sub, role=current_user.role)

    return Message(message="Account deactivated successfully")


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    data: user_models.UpdatePassword,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    """
    Update user's own password
    """
    auth_service.update_password(id=current_user.sub, data=data)

    return Message(message="Password updated successfully")
