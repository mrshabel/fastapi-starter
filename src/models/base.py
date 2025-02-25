import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone, date
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class Base(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )
    created_at: datetime = Field(default=datetime.now(tz=timezone.utc), nullable=False)
    updated_at: datetime = Field(default=datetime.now(tz=timezone.utc), nullable=False)


class BaseSearch(SQLModel):
    """A base class to be used for all search queries"""

    id: uuid.UUID | None = Field(
        default=None, title="ID", description="ID of the item record"
    )
    created_at: date | None = Field(
        default=None,
        title="Created At",
        description="The date the record was created",
    )
    updated_at: date | None = Field(
        default=None,
        title="Created At",
        description="The date the record was created",
    )

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )
