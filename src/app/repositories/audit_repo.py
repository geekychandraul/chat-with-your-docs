from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        """Repository for audit logging to the database.

        Args:
            db: an AsyncSession used for DB operations.
        """
        self.db = db

    async def log(self, action: str, metadata: dict):
        """Append an audit log entry.

        Args:
            action (str): short action name (e.g. 'INGEST_SUCCESS').
            metadata (dict): JSON-serializable metadata associated with the action.
        """
        self.db.add(AuditLog(action=action, metadatas=metadata))
        await self.db.commit()
