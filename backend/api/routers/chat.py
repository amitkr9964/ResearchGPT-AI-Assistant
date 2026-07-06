"""Chat API routes with streaming support."""

import json
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationUpdate,
)
from backend.services.chat_service import ChatService

router = APIRouter(tags=["Chat"])
chat_service = ChatService()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if request.stream:
        return StreamingResponse(
            chat_service.chat_stream(db, current_user, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    conversation, answer, citations = await chat_service.chat(db, current_user, request)
    return ChatResponse(
        conversation_id=conversation.id,
        message=answer,
        citations=citations,
    )


@router.get("/history", response_model=List[ConversationResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversations = await chat_service.get_history(db, current_user)
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            is_favorite=c.is_favorite,
            created_at=c.created_at,
            updated_at=c.updated_at,
            messages=[],
        )
        for c in conversations
    ]


@router.get("/history/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await chat_service.get_conversation(db, current_user, conv_id)
    return ChatService.conversation_to_response(conv)


@router.patch("/history/{conv_id}", response_model=ConversationResponse)
async def update_conversation(
    conv_id: int,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await chat_service.get_conversation(db, current_user, conv_id)
    if data.title is not None:
        conv.title = data.title
    if data.is_favorite is not None:
        conv.is_favorite = data.is_favorite
    await db.flush()
    return ChatService.conversation_to_response(conv)


@router.delete("/history/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.delete_conversation(db, current_user, conv_id)


@router.delete("/history", status_code=204)
async def delete_all_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.delete_all_history(db, current_user)
