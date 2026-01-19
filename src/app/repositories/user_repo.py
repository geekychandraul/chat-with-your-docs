from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        """Repository for user operations.

        Args:
            db: an AsyncSession used for DB operations.
        """
        self.db = db

    async def get_user(self, username: str) -> User | None:
        """Get a user by their username.

        Args:
            username: The username of the user.

        Returns:
            The user or None if not found.
        """
        stmt = select(User).where(func.lower(User.username) == username.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        """Create a new user.

        Args:
            user: The user to create.

        Returns:
            The created user.
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
