from src.core.exceptions import NotFoundError
from src.repositories import UserRepository
from src.models.user import (
    UserUpdate,
    UserUpdatePublic,
    User,
    UsersPublic,
)
from src.utils.database import build_query_filter
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session=session)

    async def create_user(self):
        raise NotImplementedError(
            "This handler has not been implemented yet. Use the Auth Handler instead"
        )

    async def get_user_by_id(self, id: UUID4):
        """Get user by id"""
        user = await self.user_repository.get_by_id(id=id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_all_users(self, skip: int, limit: int, query):
        """Get all users"""
        # build filters. exclude unset and none fields
        filters = build_query_filter(
            model=User,
            query=query.model_dump(exclude_unset=True, exclude_none=True),
        )
        users, count = await self.user_repository.get_all(
            skip=skip, limit=limit, filters=filters
        )

        return UsersPublic(data=users, count=count)

    async def update_user_by_id(self, id: UUID4, data: UserUpdatePublic):
        """Update user details"""
        user = await self.user_repository.update(
            id=id, data=UserUpdate(**data.model_dump(exclude_unset=True))
        )
        if not user:
            raise NotFoundError("User to be updated not found")
        return user
