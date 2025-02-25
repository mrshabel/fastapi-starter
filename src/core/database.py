from sqlmodel import create_engine, Session, select
from sqlalchemy import event
from src.core.config import AppConfig
from src.models import *  # noqa
from src.models.user import UserCreate, User, UserRole
from src.core.security import create_password_hash

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
    # TODO: move to a startup script
    # ensure app super user exists on app startup
    with Session(engine) as session:
        try:
            existing_superuser = session.exec(
                select(User).where(User.email == AppConfig.SUPERUSER_EMAIL)
            ).first()
            if not existing_superuser:
                user = User.model_validate(
                    UserCreate(
                        email=AppConfig.SUPERUSER_EMAIL,
                        password=create_password_hash(AppConfig.SUPERUSER_PASSWORD),
                        role=UserRole.SUPERUSER,
                    )
                )
                # flush to db
                session.add(user)
                session.commit()
                session.refresh(user)
        except Exception:
            # rollback transaction
            session.rollback()
            raise
