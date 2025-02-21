from src.models.user import UserCreate, User, UserUpdate
from sqlmodel import select, func, Session, update
from uuid import UUID


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: UserCreate) -> User:
        """Create new user"""
        # create instance of user
        user = User.model_validate(data)
        # flush to db
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def save(self, data: User) -> User:
        """Save an instance user. This method is mostly used when the user instance is first retrieved in previous queries to avoid redundant query on update"""
        # flush to db
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)

        return data

    def get_by_id(self, id: UUID) -> User | None:
        """Get one user by id"""
        # query = select(User).where(User.id == id)
        user = self.session.get(User, id)
        return user

    def get_by_email(self, email: str) -> User | None:
        """Get one user by email"""
        query = select(User).where(User.email == email)
        user = self.session.exec(query).first()
        return user

    def get_all(self, skip: int, limit: int, filters: list) -> tuple[list[User], int]:
        """Get all paginated user records"""
        count_query = select(func.count()).select_from(User)
        count = self.session.exec(count_query).one()

        query = select(User).offset(skip).limit(limit)
        # build filter
        for clause in filters:
            query = query.where(clause)

        users = self.session.exec(query).all()

        return users, count

    def update(self, id: UUID, data: UserUpdate) -> User | None:
        """Update user by id"""
        # remove default field values
        query = (
            update(User)
            .where(User.id == id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(User)
        )

        # flush to db
        result = self.session.exec(query).first()
        # extract returned row from tuple
        user = result[0]
        self.session.commit()

        return user
