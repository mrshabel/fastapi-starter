import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict
from typing import TYPE_CHECKING
from src.models.base import Base, BaseSearch
from enum import StrEnum
from datetime import datetime

# this will escape runtime typechecking that results in circular imports.
# it will be used to import and declare stringified type annotations only
if TYPE_CHECKING:
    from src.models.item import Item


class UserRole(StrEnum):
    SUPERUSER = "superuser"
    USER = "user"


class OAuthProvider(StrEnum):
    """Supported OAuth Providers"""

    GOOGLE = "google"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(
        title="Email",
        description="Email Address of the user",
        unique=True,
        index=True,
        max_length=255,
    )
    is_active: bool = Field(
        title="Is Active",
        description="Whether or not the user account is active",
        default=True,
    )
    role: str = Field(title="Role", description="Role of the user", max_length=255)
    full_name: str | None = Field(
        title="Full Name",
        description="The user's fullname",
        max_length=255,
        default=None,
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


# Database model, database table inferred from class name
class User(Base, UserBase, table=True):
    __tablename__ = "users"  # type: ignore

    password: str

    # relationship
    items: list["Item"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(
        title="Password",
        description="Password of the user account",
        min_length=8,
    )


class UserRegister(SQLModel):
    email: EmailStr = Field(
        title="Email", description="Email Address of the user", max_length=255
    )
    password: str = Field(
        title="Password",
        description="Password of the user account",
        min_length=8,
    )
    full_name: str | None = Field(
        title="Full Name",
        description="The user's fullname",
        default=None,
        max_length=255,
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserSearch(BaseSearch):
    email: EmailStr | None = Field(
        title="Email",
        description="Email Address of the user",
        default=None,
    )
    is_active: bool | None = Field(
        title="Is Active",
        description="Whether or not the user account is active",
        default=None,
    )
    role: str | None = Field(title="Role", description="Role of the user", default=None)
    full_name: str | None = Field(
        title="Full Name", description="The user's fullname", default=None
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


# internal model update
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(
        title="Email", description="Email Address of the user", default=None
    )
    password: str | None = Field(
        title="Password", description="The user's password", min_length=8, default=None
    )
    full_name: str | None = Field(
        title="Full Name", description="The user's fullname", default=None
    )
    is_active: bool | None = Field(
        title="Is Active",
        description="Whether or not the user account is active",
        default=None,
    )
    role: str | None = Field(title="Role", description="Role of the user", default=None)

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(
        title="Full Name", description="The user's fullname", default=None
    )
    email: EmailStr | None = Field(
        title="Email", description="Email Address of the user", default=None
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserUpdatePublic(SQLModel):
    full_name: str | None = Field(
        title="Full Name", description="The user's fullname", default=None
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class UserLogin(SQLModel):
    email: EmailStr = Field(title="Email", description="Email Address of the user")
    password: str = Field(title="Password", description="The user's password")


class UpdatePassword(SQLModel):
    current_password: str = Field(
        title="Current Password",
        description="Current Password of the user account",
        min_length=8,
        max_length=40,
    )
    new_password: str = Field(
        title="New Password",
        description="New Password of the user account",
        min_length=8,
        max_length=40,
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID = Field(title="ID", description="ID of the user record")
    created_at: datetime = Field(
        title="created_at", description="The date and time the user record was created"
    )
    updated_at: datetime = Field(
        title="updated_at", description="The date and time the user record was updated"
    )


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# response models
class UserPublicResponse(SQLModel):
    message: str
    data: UserPublic


class UsersPublicResponse(UsersPublic):
    message: str


class OAuthInitResponse(SQLModel):
    url: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserLoginResponse(Token):
    message: str
    data: UserPublic
    refresh_token: str


class TokenRefreshResponse(Token):
    message: str
    refresh_token: str


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: uuid.UUID
    role: str


class NewPassword(SQLModel):
    token: str = Field(
        title="Token", description="Verification token to complete password change"
    )
    new_password: str = Field(
        title="New Password",
        description="New Password of the user account",
        min_length=8,
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class GoogleTokenRequest(SQLModel):
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str
    scope: str
    state: str
    grant_type: str = "authorization_code"


class GoogleTokenResponse(SQLModel):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str
    id_token: str


class GoogleOAuthTokenPayload(SQLModel):
    email: str
    email_verified: bool
    at_hash: str  # access token hash
    name: str
    picture: str
    given_name: str  # first name
    family_name: str  # last name
