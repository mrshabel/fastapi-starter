from collections.abc import AsyncGenerator
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.database import engine
from src.core.exceptions import (
    PermissionDeniedError,
)
from src.core.security import decode_token
from src.models.user import TokenPayload, UserRole
from src.core.config import AppConfig
from src.services import LocalStorageService, S3StorageService


# database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get the db session"""
    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
    async with Session.begin() as session:  # type: ignore
        try:
            yield session
        except Exception:
            # rollback transaction
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_db)]


# token dependency
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login/access-token")

TokenDep = Annotated[str, Depends(reusable_oauth2)]


# user dependency
def get_current_user(token: TokenDep) -> TokenPayload:
    try:
        data = decode_token(token=token)
    except (jwt.exceptions.InvalidTokenError, ValidationError):
        raise PermissionDeniedError("Could not validate credentials")

    if not data:
        raise PermissionDeniedError("Invalid or expired token")

    # user = session.get(User, token_data.sub)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return data


CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> TokenPayload:
    if not current_user.role == UserRole.SUPERUSER:
        raise PermissionDeniedError("The user doesn't have enough privileges")

    return current_user


# storage dependencies
def get_storage_service() -> LocalStorageService | S3StorageService:
    """Returns an instance of the underlying storage client"""
    if AppConfig.IS_DEVELOPMENT:
        return LocalStorageService()
    else:
        return S3StorageService()


StorageServiceDep = Annotated[
    LocalStorageService | S3StorageService, Depends(get_storage_service)
]
