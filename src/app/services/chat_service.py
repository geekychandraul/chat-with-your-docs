import uuid

from fastapi.exceptions import HTTPException

from app.core.logging import get_logger
from app.models.chat import ChatMessage
from app.repositories.audit_repo import AuditRepository
from app.repositories.chat_repo import ChatRepository, Conversation
from app.services.retrieval_service import RetrievalService
from app.utils.chains import build_streaming_chain
from app.utils.history import format_history

logger = get_logger(__name__)


class ChatService:
    """Service that handles chat operations and streaming responses.

    Methods:
        - stream_answer_sse: stream assistant tokens via Server-Sent Events.
    """

    def __init__(self, db):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.audit_repo = AuditRepository(db)
        self.retrieval = RetrievalService()
        self.chain = build_streaming_chain()

    async def validate_or_create_conversation_id(
        self, conversation_id, user_id: uuid.UUID
    ):
        # Create conversation if not exists
        if not conversation_id:
            logger.info("No conversation ID provided; creating a new one.")
            conversation = Conversation(user_id=user_id)
            conversation_id = await self.chat_repo.create_conversation(conversation)
        elif conversation_id and not await self.chat_repo.get_conversation(
            conversation_id
        ):
            logger.error("Conversation_id not found. Raising HTTP 404.")
            raise HTTPException(
                status_code=404, detail="Conversation ID does not exist."
            )
        return conversation_id

    async def stream_answer_sse(
        self, conversation_id, user_message: str, user_id: uuid.UUID
    ):
        """Stream an answer back to the client using Server-Sent Events (SSE).

        Args:
            conversation_id: optional conversation UUID; a new conversation
                will be created if not provided.
            user_message (str): the user's chat message.

        Yields:
            SSE formatted event strings (conversation id, token events, done).
        """
        yield ("event: conversation\n" f"data: {conversation_id}\n\n")

        # Load history from DB
        past_messages = await self.chat_repo.get_history(conversation_id)
        history_text = format_history(past_messages)

        # Retrieve context
        docs = self.retrieval.retrieve(user_message, user_id)
        print("Retrieved %d documents for context.", len(docs), docs[:2])

        # Persist user message
        await self.chat_repo.save(
            ChatMessage(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
            )
        )

        full_answer = []

        # Stream response
        async for token in self.chain.astream(
            {
                "input": user_message,
                "context": docs,
                "history": history_text,
            }
        ):
            full_answer.append(token)
            logger.debug("Streaming token: %s", token)
            yield f"event: token\ndata:{token}\n\n"

        # Persist assistant message
        final_answer = "".join(full_answer)

        await self.chat_repo.save(
            ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=final_answer,
            )
        )

        await self.audit_repo.log(
            "CHAT_STREAM_COMPLETED",
            {"conversation_id": str(conversation_id)},
            user_id=user_id,
        )

        yield "event: done\ndata: [DONE]\n\n"


# Str1ngst!
