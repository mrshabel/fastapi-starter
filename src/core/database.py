from sqlmodel import create_engine, select
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.config import AppConfig

# disable strict single thread check
connect_args = {"check_same_thread": False}
engine = AsyncEngine(
    create_engine(
        AppConfig.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=AppConfig.DB_POOL_SIZE,
        max_overflow=10,
        echo=False,
    )
)


# setup sqlite configuration
@event.listens_for(engine.sync_engine, "connect")
def configure_sqlite_connection(conn, record):
    """Configure SQLite connection with improved settings"""
    # enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")

    # WAL for better concurrency support
    conn.execute("PRAGMA journal_mode = WAL;")


async def init_db():
    async with AsyncSession(engine) as session:
        # ensure db is responsive on startup
        await session.exec(select(1))
