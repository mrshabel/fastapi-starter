from src.models.item import ItemCreate, Item, ItemUpdate
from sqlmodel import select, func, Session, delete, update, col
from uuid import UUID


class ItemRepository:
    """A CRUD base repository for all interactions with the database.
    The same code can be replicated for other entities depending on the system's business rules
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, data: ItemCreate) -> Item:
        """Create new item"""
        # create instance of item
        item = Item.model_validate(data)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_by_id(self, id: UUID) -> Item | None:
        """Get one item by id"""
        # query = select(Item).where(Item.id == id)
        item = self.session.get(Item, id)
        return item

    def get_all(self, skip: int, limit: int, filters: list) -> tuple[list[Item], int]:
        """Get all paginated item records"""
        count_query = select(func.count()).select_from(Item)
        count = self.session.exec(count_query).one()

        query = select(Item).offset(skip).limit(limit)
        # build filter
        for clause in filters:
            query = query.where(clause)

        items = self.session.exec(query).all()

        return list(items), count

    def update(self, id: UUID, data: ItemUpdate) -> Item | None:
        """Update item by id"""
        # remove unset fields
        query = (
            update(Item)
            .where(col(Item.id) == id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Item)
        )

        # flush to db
        result = self.session.exec(query).first()  # type: ignore
        # extract returned row from tuple
        item = result[0]
        self.session.commit()

        return item

    def delete(self, id: UUID) -> bool:
        """Delete item by id"""
        query = delete(Item).where(col(Item.id) == id).returning(Item.id)  # type: ignore

        # flush to db
        # return only number of affected rows
        result = self.session.exec(query).first()
        self.session.commit()

        return result is not None
