import uuid

from sqlmodel import Field, Relationship, SQLModel
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict
from datetime import datetime

# import related entities
from src.models.user import User
from src.models.base import Base, BaseSearch


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(
        title="Title", description="The title of the item", min_length=1, max_length=255
    )
    description: str | None = Field(
        title="Description",
        description="The description of the item",
        default=None,
        max_length=255,
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


# Database model, database table inferred from class name
class Item(Base, ItemBase, table=True):
    __tablename__ = "items"  # type: ignore

    user_id: uuid.UUID = Field(
        foreign_key="users.id", nullable=False, ondelete="CASCADE"
    )

    # declare relationship
    user: User = Relationship(back_populates="items")


# Properties to receive on item creation
class ItemCreate(ItemBase):
    user_id: uuid.UUID = Field(title="ID", description="ID of the user record")


class ItemCreateMe(ItemBase):
    pass


# Properties to receive on item update
class ItemSearch(BaseSearch):
    title: str | None = Field(
        default=None,
        title="Title",
        description="The title of the item",
        min_length=1,
        max_length=255,
    )
    description: str | None = Field(
        title="Description",
        description="The description of the item",
        default=None,
        max_length=255,
    )


class ItemUpdate(ItemBase):
    title: str | None = Field(
        default=None,
        title="Title",
        description="The title of the item",
        min_length=1,
        max_length=255,
    )


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID = Field(title="ID", description="ID of the item record")
    user_id: uuid.UUID = Field(title="ID", description="ID of the user record")
    created_at: datetime = Field(
        title="created_at", description="The date and time the item was created"
    )
    updated_at: datetime = Field(
        title="updated_at", description="The date and time the item was updated"
    )


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class ItemPublicResponse(SQLModel):
    message: str
    data: ItemPublic


class ItemsPublicResponse(ItemsPublic):
    message: str
