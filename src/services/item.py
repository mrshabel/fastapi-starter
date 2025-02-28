from src.core.exceptions import NotFoundError
from src.repositories import ItemRepository
from src.models.item import ItemCreate, ItemUpdate, Item, ItemsPublic
from src.utils.database import build_query_filter
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession


class ItemService:
    def __init__(self, session: AsyncSession) -> None:
        self.item_repository = ItemRepository(session=session)

    async def create_item(self, data: ItemCreate):
        return await self.item_repository.create(data=data)

    async def get_item_by_id(self, id: UUID4):
        """Get item by id"""
        item = await self.item_repository.get_by_id(id=id)
        if not item:
            raise NotFoundError("Item not found")
        return item

    async def get_all_items(self, skip: int, limit: int, query):
        """Get all items"""
        # build filters. exclude unset and none fields
        filters = build_query_filter(
            model=Item,
            query=query.model_dump(exclude_unset=True, exclude_none=True),
        )
        items, count = await self.item_repository.get_all(
            skip=skip, limit=limit, filters=filters
        )

        return ItemsPublic(data=items, count=count)

    async def update_item_by_id(self, id: UUID4, data: ItemUpdate):
        """Update item details"""
        item = await self.item_repository.update(id=id, data=data)
        if not item:
            raise NotFoundError("Item to be updated not found")
        return item

    async def delete_item_by_id(self, id: UUID4):
        """Delete item details"""
        item = await self.item_repository.delete(id=id)
        if not item:
            raise NotFoundError("Item to be deleted not found")
        return item
