from src.models.user import UserCreate, User, UserUpdate
from sqlmodel import select, func, update, col
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: UserCreate) -> User:
        """Create new user"""
        # create instance of user
        user = User.model_validate(data)
        # flush to db
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def save(self, data: User) -> User:
        """Save an instance user. This method is mostly used when the user instance is first retrieved in previous queries to avoid redundant query on update"""
        # flush to db
        self.session.add(data)
        await self.session.commit()
        await self.session.refresh(data)

        return data

    async def get_by_id(self, id: UUID) -> User | None:
        """Get one user by id"""
        # query = select(User).where(User.id == id)
        user = await self.session.get(User, id)
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get one user by email"""
        query = select(User).where(User.email == email)
        user = await self.session.exec(query)
        return user.first()

    async def get_all(
        self, skip: int, limit: int, filters: list
    ) -> tuple[list[User], int]:
        """Get all paginated user records"""
        count_query = select(func.count()).select_from(User)
        result = await self.session.exec(count_query)
        count = result.one()

        query = select(User).offset(skip).limit(limit)
        # build filter
        for clause in filters:
            query = query.where(clause)

        results = await self.session.exec(query)
        users = results.all()

        return list(users), count

    async def update(self, id: UUID, data: UserUpdate) -> User | None:
        """Update user by id"""
        # remove default field values
        query = (
            update(User)
            .where(col(User.id) == id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(User)
        )

        # flush to db
        result = await self.session.exec(query)  # type: ignore
        # extract returned row from tuple
        user = result.first()[0]
        await self.session.commit()

        return user
