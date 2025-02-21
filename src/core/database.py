from sqlmodel import SQLModel, create_engine
from sqlalchemy import event
from src.core.config import AppConfig
from src.models import *  # noqa

# disable strict single thread check
connect_args = {"check_same_thread": False}
engine = create_engine(
    AppConfig.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=AppConfig.DB_POOL_SIZE,
    max_overflow=10,
    echo=False,
)


# setup sqlite configuration
@event.listens_for(engine, "connect")
def configure_sqlite_connection(conn, record):
    """Configure SQLite connection with improved settings"""
    # enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")

    # WAL for better concurrency support
    conn.execute("PRAGMA journal_mode = WAL;")


def init_db():
    # create tables
    SQLModel.metadata.create_all(engine)
