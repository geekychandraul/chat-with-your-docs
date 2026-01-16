import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, Conversation


class ChatRepository:
    def __init__(self, db: AsyncSession):
        """Repository for chat-related persistence operations.

        Args:
            db: an AsyncSession used for DB operations.
        """
        self.db = db

    async def create_conversation(self) -> uuid.UUID:
        """Create and persist a new Conversation record.

        Returns:
            uuid.UUID: the UUID of the created conversation.
        """
        convo = Conversation()
        self.db.add(convo)
        await self.db.commit()
        return convo.uuid

    async def get_conversation(self, conversation_id):
        """Retrieve conversations matching the provided UUID.

        Args:
            conversation_id: the UUID of the conversation to look up.

        Returns:
            List[Conversation]: matching conversation records (possibly empty).
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.uuid == conversation_id)
        )
        return result.scalars().all()

    async def save(self, message: ChatMessage):
        """Persist a ChatMessage to the database.

        Args:
            message (ChatMessage): the message instance to persist.
        """
        self.db.add(message)
        await self.db.commit()

    async def get_history(self, conversation_id):
        """Retrieve chronological chat history for a conversation.

        Args:
            conversation_id: UUID of the conversation.

        Returns:
            List[ChatMessage]: ordered list of messages.
        """
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return result.scalars().all()
