import httpx
import urllib.parse
from fastapi.logger import logger
from fastapi.security import OAuth2PasswordRequestForm
from src.core.exceptions import (
    BadActionError,
    NotFoundError,
    InternalServerError,
    AuthenticationError,
)
from src.core.config import AppConfig
from src.repositories import UserRepository
from src.models.user import (
    UserCreate,
    UserUpdate,
    UserLogin,
    TokenPayload,
    UserRegister,
    UserRole,
    UpdatePassword,
    User,
    OAuthProvider,
    GoogleTokenRequest,
    GoogleTokenResponse,
)
from src.core.security import (
    create_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_external_oauth_url,
    decode_google_token,
    update_client_state,
    check_client_state,
)
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session=session)

    async def signup(self, data: UserRegister):
        """Create a new user account"""
        # check if user exists in system
        existing_user = await self.user_repository.get_by_email(email=data.email)
        if existing_user:
            raise BadActionError("User already exists in the system")

        # create password hash
        hashed_password = create_password_hash(password=data.password)
        data.password = hashed_password

        user_data = UserCreate(**vars(data), role=UserRole.USER)
        user = await self.user_repository.create(data=user_data)
        return user

    async def login(self, data: UserLogin):
        """Login to a user account

        Args:
            data (UserLogin): The user's login data

        Returns:
            tuple[user, access_token, refresh_token]
        """
        user = await self.user_repository.get_by_email(email=data.email)
        if not user:
            raise NotFoundError("User does not exist in the system")

        if not verify_password(data.password, user.password):
            raise BadActionError("Incorrect email or password")

        # generate tokens
        token_data = TokenPayload(sub=user.id, role=user.role)
        access_token = create_access_token(token_data)
        refresh_token = create_access_token(token_data)
        return user, access_token, refresh_token

    async def login_access_token(self, data: OAuth2PasswordRequestForm):
        """Login to a user account for an OAuth access token"""
        user = await self.user_repository.get_by_email(email=data.username)
        if not user:
            raise NotFoundError("User does not exist in the system")

        if not verify_password(data.password, user.password):
            raise BadActionError("Incorrect email or password")

        # generate and return tokens
        # generate tokens
        token_data = TokenPayload(sub=user.id, role=user.role)
        return create_access_token(token_data)

    async def refresh_session(self, refresh_token: str) -> str:
        """validate refresh token and generate new access token"""
        data = decode_refresh_token(token=refresh_token)
        if not data:
            raise BadActionError("Invalid refresh token")

        access_token = create_access_token(data)
        return access_token

    async def deactivate_account(self, id: UUID4, role: UserRole):
        """Update user details"""
        # prevent superusers from disabling their accounts
        if role == UserRole.SUPERUSER:
            raise PermissionError("Superusers are not allowed to delete themselves")

        user = await self.user_repository.update(
            id=id, data=UserUpdate(is_active=False)
        )
        return user

    async def update_password(self, id: UUID4, data: UpdatePassword):
        """Update user account password"""
        user = await self.user_repository.get_by_id(id=id)
        if not user:
            raise NotFoundError("Password cannot be updated at this time")

        if not verify_password(data.current_password, user.password):
            raise BadActionError("Incorrect password")

        user.password = create_password_hash(password=data.new_password)
        updated_user = self.user_repository.save(user)

        return updated_user

    async def get_oauth_url(self, client_origin: str, provider: OAuthProvider):
        # compose url and state from client origin
        # write state to an external structure
        state = update_client_state(client_origin=client_origin)
        # compose redirect uri
        redirect_uri = f"{client_origin}/auth/{provider}/callback.html"
        return get_external_oauth_url(
            redirect_uri=redirect_uri, state=state, provider=provider
        )

    async def handle_oauth(
        self, code: str, provider: OAuthProvider, client_origin: str, state: str
    ) -> tuple[User, str, str]:
        """
        Handle OAuth flow by exchanging code for necessary tokens and user details

        Parameters:
            code (str): the code received from oauth server
            provider (OAuthProvider): the oauth provider
            state (str): the state token used in initiating the oauth flow

        Returns:
            tuple[user, access_token, refresh_token]
        """

        # get user account details
        user_data: UserCreate
        try:
            match provider:
                case OAuthProvider.GOOGLE:
                    try:
                        token = await self._get_google_token(
                            code=code, client_origin=client_origin, state=state
                        )
                    except BaseException:
                        logger.error(
                            "Failed to retrieve google access token", exc_info=True
                        )
                        raise

                    user = await self._get_google_user(token)
                    # check if user email is verified
                    if not user.email_verified:
                        raise BadActionError("Email not verified")

                    user_data = UserCreate(
                        email=user.email,
                        # compose fullname
                        full_name=f"{user.given_name} {user.family_name}",
                        password=AppConfig.OAUTH_DEFAULT_PASSWORD,
                        role=UserRole.USER,
                    )
                case _:
                    raise InternalServerError("OAuth Provider not supported")
        except BaseException:
            logger.error("Failed to retrieve user details", exc_info=True)
            raise BadActionError("Failed to retrieve user details")

        # check if user already exists in system
        user = await self.user_repository.get_by_email(email=user_data.email)
        if not user:
            user = await self.user_repository.create(user_data)

        # create tokens
        token_data = TokenPayload(sub=user.id, role=user.role)

        access_token = create_access_token(token_data)
        refresh_token, _ = create_refresh_token(token_data)
        return user, access_token, refresh_token

    async def _get_google_token(
        self, code: str, client_origin: str, state: str, provider=OAuthProvider.GOOGLE
    ):
        """Request for google oauth token with code received on callback endpoint"""
        # raise exception if state does not exist or has expired
        if not check_client_state(state=state):
            raise BadActionError("Invalid OAuth state")

        # compose redirect uri
        redirect_uri = f"{client_origin}/auth/{provider}/callback.html"
        # compose url-encoded data
        data = urllib.parse.urlencode(
            GoogleTokenRequest(
                code=code,
                client_id=AppConfig.GOOGLE_CLIENT_ID,
                client_secret=AppConfig.GOOGLE_CLIENT_SECRET,
                redirect_uri=redirect_uri,
                state=state,
                scope=AppConfig.GOOGLE_OAUTH_SCOPES,
            ).model_dump()
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient(timeout=120) as client:
            res = await client.post(
                url=AppConfig.GOOGLE_OAUTH_TOKEN_URL, content=data, headers=headers
            )

        if res.status_code != 200:
            # raise exception
            raise InternalServerError("Failed to retrieve google access token")

        data = res.json()

        return GoogleTokenResponse(**data)

    async def _get_google_user(self, token: GoogleTokenResponse):
        # decode and retrieve user details
        data = decode_google_token(token.id_token)

        # raise exception if token is malformed or expired
        if not data:
            raise AuthenticationError("Expired Token")

        # return user details from token
        return data
