from fastapi.security import OAuth2PasswordRequestForm
from src.core.exceptions import BadActionError, NotFoundError
from src.repositories import UserRepository
from src.models.user import (
    UserCreate,
    UserUpdate,
    UserLogin,
    TokenPayload,
    UserRegister,
    UserRole,
    UpdatePassword,
)
from src.core.security import (
    create_password_hash,
    verify_password,
    create_access_token,
)
from pydantic import UUID4
from sqlmodel import Session


class AuthService:
    def __init__(self, session: Session) -> None:
        self.user_repository = UserRepository(session=session)

    def signup(self, data: UserRegister):
        """Create a new user account"""
        # check if user exists in system
        existing_user = self.user_repository.get_by_email(email=data.email)
        if existing_user:
            raise BadActionError("User already exists in the system")

        # create password hash
        hashed_password = create_password_hash(password=data.password)
        data.password = hashed_password

        user_data = UserCreate(**vars(data), role=UserRole.USER)
        user = self.user_repository.create(data=user_data)
        return user

    def login(self, data: UserLogin):
        """Login to a user account

        Args:
            data (UserLogin): The user's login data

        Returns:
            tuple[user, access_token, refresh_token]
        """
        user = self.user_repository.get_by_email(email=data.email)
        if not user:
            raise NotFoundError("User does not exist in the system")

        if not verify_password(data.password, user.password):
            raise BadActionError("Incorrect email or password")

        # generate tokens
        token_data = TokenPayload(sub=str(user.id), role=user.role)
        access_token = create_access_token(token_data)
        refresh_token = create_access_token(token_data)
        return user, access_token, refresh_token

    def login_access_token(self, data: OAuth2PasswordRequestForm):
        """Login to a user account for an OAuth access token"""
        user = self.user_repository.get_by_email(email=data.username)
        if not user:
            raise NotFoundError("User does not exist in the system")

        if not verify_password(data.password, user.password):
            raise BadActionError("Incorrect email or password")

        # generate and return tokens
        # generate tokens
        token_data = TokenPayload(sub=str(user.id), role=user.role)
        return create_access_token(token_data)

    def deactivate_account(self, id: UUID4, role: UserRole):
        """Update user details"""
        # prevent superusers from disabling their accounts
        if role == UserRole.SUPERUSER:
            raise PermissionError("Superusers are not allowed to delete themselves")

        user = self.user_repository.update(id=id, data=UserUpdate(is_active=False))
        return user

    def update_password(self, id: UUID4, data: UpdatePassword):
        """Update user account password"""
        user = self.user_repository.get_by_id(id=id)
        if not user:
            raise NotFoundError("Password cannot be updated at this time")

        if not verify_password(data.current_password, user.password):
            raise BadActionError("Incorrect password")

        user.password = create_password_hash(password=data.new_password)
        updated_user = self.user_repository.save(user)

        return updated_user
