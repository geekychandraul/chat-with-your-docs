import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file_metadata import FileMetadata


class FileRepository:
    def __init__(self, db: AsyncSession):
        """Repository for file metadata operations.

        Args:
            db: an AsyncSession used for DB operations.
        """
        self.db = db

    async def get_by_hash(
        self, file_hash: str, user_id: uuid.UUID
    ) -> FileMetadata | None:
        """Lookup FileMetadata by SHA256 hash.

        Args:
            file_hash (str): hex-encoded SHA256 of the file contents.

        Returns:
            Optional[FileMetadata]: the metadata record if found.
        """
        stmt = select(FileMetadata).where(
            FileMetadata.file_hash == file_hash, FileMetadata.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, file: FileMetadata):
        """Save or update a FileMetadata record.

        Args:
            file (FileMetadata): the model instance to persist.

        Returns:
            FileMetadata: refreshed instance with DB-assigned fields.
        """
        self.db.add(file)
        await self.db.commit()
        await self.db.refresh(file)
        return file
