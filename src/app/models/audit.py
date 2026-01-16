import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import JSON, TIMESTAMP, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid6 import uuid7

from app.core.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String)
    metadatas: Mapped[dict] = mapped_column(JSON)
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        UUID(as_uuid=True), default_factory=uuid7, unique=True, primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default_factory=lambda: datetime.now(UTC),
    )
