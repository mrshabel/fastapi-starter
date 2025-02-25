from sqlmodel import Field, SQLModel
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class FilePublic(SQLModel):
    path: str = Field(title="Path", description="The file path")

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )


class FilePublicResponse(SQLModel):
    message: str = Field(title="Message", description="The file path")
    data: FilePublic

    model_config = ConfigDict(  # type: ignore
        alias_generator=to_camel,
        populate_by_name=True,
    )
