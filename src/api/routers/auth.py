from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from src.services import AuthService
from src.models import user as user_models, Message
from src.api.dependencies import SessionDep, CurrentUser
from src.core.exceptions import PermissionDeniedError
from src.tasks import email as email_tasks

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
async def signup(
    data: user_models.UserRegister,
    auth_service: AuthServiceDep,
):
    """
    Create new user account
    """
    user = await auth_service.signup(data)

    # deliver email in background
    recipient = user.email
    subject = "Account Signup"
    content = f"""
    Hello {user.full_name if user.full_name else "there"},
    Welcome to Shabel's world.
    Made with love
    """
    email_tasks.send_email_task.delay(
        recipient=recipient, subject=subject, content=content
    )
    return user_models.UserPublicResponse(
        message="Signup completed successfully", data=user
    )


@router.post("/login", response_model=user_models.UserPublicResponse)
async def login(data: user_models.UserLogin, auth_service: AuthServiceDep):
    """
    Login to a user account
    """
    user, access_token, refresh_token = await auth_service.login(data)

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
    access_token = await auth_service.login_access_token(data)

    return user_models.Token(access_token=access_token)


@router.patch("/me/deactivate", response_model=Message)
async def deactivate_account(current_user: CurrentUser, auth_service: AuthServiceDep):
    """
    Delete own user
    """
    # disable superuser from deactivating account
    if current_user.role == user_models.UserRole.SUPERUSER:
        raise PermissionDeniedError(
            "Superusers are not allowed to deactivate their accounts"
        )

    await auth_service.deactivate_account(id=current_user.sub, role=current_user.role)

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
    await auth_service.update_password(id=current_user.sub, data=data)

    return Message(message="Password updated successfully")


@router.post("/refresh", response_model=user_models.TokenRefreshResponse)
async def refresh_client_token(
    refresh_token: str,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    """
    Refresh user access token
    """
    access_token = await auth_service.refresh_session(refresh_token)

    return user_models.TokenRefreshResponse(
        message="Token refresh successful",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/{provider}/init", response_model=user_models.OAuthInitResponse)
async def initiate_oauth_flow(
    provider: user_models.OAuthProvider,
    auth_service: AuthServiceDep,
    origin: Annotated[str, Header()],
):
    """
    Initiate OAuth flow with appropriate providers
    """
    url = await auth_service.get_oauth_url(client_origin=origin, provider=provider)

    # return url to redirect client to oauth server init page
    return user_models.OAuthInitResponse(url=url)


@router.get("/{provider}/callback", response_model=user_models.UserLoginResponse)
async def handle_oauth_callback(
    provider: user_models.OAuthProvider,
    code: str,
    state: str,
    auth_service: AuthServiceDep,
    origin: Annotated[str, Header()],
):
    """
    Process callback from client and login user
    """
    user, access_token, refresh_token = await auth_service.handle_oauth(
        code=code, provider=provider, client_origin=origin, state=state
    )

    return user_models.UserLoginResponse(
        message="Login successfully",
        data=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )
