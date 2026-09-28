"""Chat endpoints with Socket.IO."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from src.core.db import get_db
from src.core import security
from src.schemas import ChatMessage, ChatResponse, ChatRequest
from src.services.chat import ChatService

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Ask a question and get answer based on RAG."""
    return await ChatService.ask_question(
        db=db,
        user_id=current_user.id,
        question=request.question,
        session_id=request.session_id,
    )


@router.post("/stream")
async def stream_answer(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(security.get_current_user),
):
    """Stream answer tokens in real-time."""
    async def event_stream() -> AsyncGenerator[str, None]:
        async for token in ChatService.stream_answer(
            db=db,
            user_id=current_user.id,
            question=request.question,
            session_id=request.session_id,
        ):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
