from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.db.database import async_get_db
from app.core.logging import get_logger
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post("/chat")
async def chat(
    req: ChatRequest,
    db: Session = Depends(async_get_db),
):
    service = ChatService(db)
    if req.stream is False:
        # Non-streaming response (not implemented here)
        pass
    else:
        return StreamingResponse(
            service.stream_answer_sse(
                conversation_id=req.conversation_id,
                user_message=req.message,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
