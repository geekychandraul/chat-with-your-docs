from sqlalchemy.ext.asyncio import AsyncSession


class ChunkRepository:
    def __init__(self, db: AsyncSession):
        """Repository for DocumentChunk persistence.

        Args:
            db: an AsyncSession used for DB operations.
        """
        self.db = db

    async def save_all(self, chunks):
        """Persist multiple chunk records in a single transaction.

        Args:
            chunks (List[DocumentChunk]): list of chunk model instances.
        """
        self.db.add_all(chunks)
        await self.db.commit()
