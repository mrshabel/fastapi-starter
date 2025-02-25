from sqlmodel import SQLModel

# all tables created in the application should be imported here to allow alembic to pick it up easily when using revision autogenerate
from .user import User as User
from .item import Item as Item


# Generic message for all API responses
class Message(SQLModel):
    message: str


class SystemHealth(SQLModel):
    status: str = "healthy"
    database: str = "connected"
