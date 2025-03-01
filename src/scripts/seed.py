import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.logger import logger
from src.core.config import AppConfig
from src.models.user import UserCreate, User, UserRole
from src.core.security import create_password_hash
from src.core.database import engine


async def seed_data():
    """Ensure that the app superuser and other relevant data is seeded into the database"""
    async with AsyncSession(engine) as session:
        try:
            existing_superuser = await session.exec(
                select(User).where(User.email == AppConfig.SUPERUSER_EMAIL)
            )
            if not existing_superuser.first():
                user = User.model_validate(
                    UserCreate(
                        email=AppConfig.SUPERUSER_EMAIL,
                        password=create_password_hash(AppConfig.SUPERUSER_PASSWORD),
                        role=UserRole.SUPERUSER,
                    )
                )
                # flush to db
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info("Seeding complete")
        except Exception:
            # rollback transaction
            await session.rollback()
            logger.error("Failed to seed data")


if __name__ == "__main__":
    asyncio.run(seed_data())
