from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.core.db.database import Base


class DocumentChunk(Base):
    __tablename__ = "chunks"

    file_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("files.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    chroma_id: Mapped[str] = mapped_column(String)
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default_factory=uuid7
    )
