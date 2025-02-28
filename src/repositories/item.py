from src.models.item import ItemCreate, Item, ItemUpdate
from sqlmodel import select, func, delete, update, col
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID


class ItemRepository:
    """A CRUD base repository for all interactions with the database.
    The same code can be replicated for other entities depending on the system's business rules
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: ItemCreate) -> Item:
        """Create new item"""
        # create instance of item
        item = Item.model_validate(data)

        self.session.add(item)
        await self.session.commit()
        # await self.session.refresh(item)
        return item

    async def get_by_id(self, id: UUID) -> Item | None:
        """Get one item by id"""
        # query = select(Item).where(Item.id == id)
        item = await self.session.get(Item, id)
        return item

    async def get_all(
        self, skip: int, limit: int, filters: list
    ) -> tuple[list[Item], int]:
        """Get all paginated item records"""
        count_query = select(func.count()).select_from(Item)
        result = await self.session.exec(count_query)
        count = result.one()

        query = select(Item).offset(skip).limit(limit)
        # build filter
        for clause in filters:
            query = query.where(clause)

        results = await self.session.exec(query)
        items = results.all()

        return list(items), count

    async def update(self, id: UUID, data: ItemUpdate) -> Item | None:
        """Update item by id"""
        # remove unset fields
        query = (
            update(Item)
            .where(col(Item.id) == id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(Item)
        )

        # flush to db
        result = await self.session.exec(query)  # type: ignore
        # extract returned row from tuple
        item = result.first()[0]
        await self.session.commit()

        return item

    async def delete(self, id: UUID) -> bool:
        """Delete item by id"""
        query = delete(Item).where(col(Item.id) == id).returning(Item.id)  # type: ignore

        # flush to db
        # return only number of affected rows
        result = self.session.exec(query)
        await self.session.commit()

        item = result.first()
        return item is not None
