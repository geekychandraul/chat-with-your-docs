import uuid
import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db.database import Base


class FileMetadata(Base):
    __tablename__ = "files"
    _table_args__ = (
        UniqueConstraint("file_hash", "user_id", name="uq_file_hash_user_id"),
    )

    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_hash: Mapped[str] = mapped_column(String, nullable=False)
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default_factory=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(String, default="uploaded")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default_factory=lambda: datetime.now(UTC),
    )
    user_id: Mapped[uuid_pkg.UUID] = mapped_column(
        ForeignKey("user.uuid"), default=None, nullable=True
    )
