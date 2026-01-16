import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid6 import uuid7

from app.core.db.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default_factory=lambda: datetime.now(UTC),
    )
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid7,
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    conversation_id: Mapped[uuid_pkg.UUID] = mapped_column(
        ForeignKey("conversations.uuid"), index=True, default=None
    )
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        UUID(as_uuid=True), default_factory=uuid7, unique=True, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default_factory=lambda: datetime.now(UTC),
    )
