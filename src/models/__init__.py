from .user import User
from .item import Item
from sqlmodel import SQLModel


# Generic message for all API responses
class Message(SQLModel):
    message: str


class SystemHealth(SQLModel):
    status: str = "healthy"
    database: str = "connected"
