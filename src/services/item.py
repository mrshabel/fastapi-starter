from src.core.exceptions import NotFoundError
from src.repositories import ItemRepository
from src.models.item import ItemCreate, ItemUpdate, Item, ItemsPublic
from src.utils.database import build_query_filter
from pydantic import UUID4
from sqlmodel import Session


class ItemService:
    def __init__(self, session: Session) -> None:
        self.item_repository = ItemRepository(session=session)

    def create_item(self, data: ItemCreate):
        return self.item_repository.create(data=data)

    def get_item_by_id(self, id: UUID4):
        """Get item by id"""
        item = self.item_repository.get_by_id(id=id)
        if not item:
            raise NotFoundError("Item not found")
        return item

    def get_all_items(self, skip: int, limit: int, query):
        """Get all items"""
        # build filters. exclude unset and none fields
        filters = build_query_filter(
            model=Item,
            query=query.model_dump(exclude_unset=True, exclude_none=True),
        )
        items, count = self.item_repository.get_all(
            skip=skip, limit=limit, filters=filters
        )

        return ItemsPublic(data=items, count=count)

    def update_item_by_id(self, id: UUID4, data: ItemUpdate):
        """Update item details"""
        item = self.item_repository.update(id=id, data=data)
        if not item:
            raise NotFoundError("Item to be updated not found")
        return item

    def delete_item_by_id(self, id: UUID4):
        """Delete item details"""
        item = self.item_repository.delete(id=id)
        if not item:
            raise NotFoundError("Item to be deleted not found")
        return item
