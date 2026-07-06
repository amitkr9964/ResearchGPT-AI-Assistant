"""Chat and conversation management service."""

import json
from typing import AsyncGenerator, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database.models import Conversation, Message, User
from backend.models.schemas import ChatRequest, Citation, ConversationResponse, MessageResponse
from backend.rag.llm import get_llm
from backend.rag.reranker import get_reranker
from backend.rag.retriever import HybridRetriever
from backend.utils.logger import logger


class ChatService:
    async def chat(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
    ) -> tuple[Conversation, str, List[Citation]]:
        conversation = await self._get_or_create_conversation(db, user, request.conversation_id, request.message)

        user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
        db.add(user_msg)

        history = await self._get_history(db, conversation.id)
        chunks = await self._retrieve(user.id, request.message, request.document_ids, request.search_mode)
        llm = get_llm()
        answer, citations = await llm.generate(request.message, chunks, history)

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            citations=json.dumps([c.model_dump() for c in citations]),
        )
        db.add(assistant_msg)

        if conversation.title == "New Chat":
            conversation.title = request.message[:80] + ("..." if len(request.message) > 80 else "")

        await db.flush()
        await db.refresh(conversation)
        return conversation, answer, citations

    async def chat_stream(
        self,
        db: AsyncSession,
        user: User,
        request: ChatRequest,
    ) -> AsyncGenerator[str, None]:
        conversation = await self._get_or_create_conversation(db, user, request.conversation_id, request.message)

        user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
        db.add(user_msg)
        await db.flush()

        history = await self._get_history(db, conversation.id)
        chunks = await self._retrieve(user.id, request.message, request.document_ids, request.search_mode)
        citations = get_llm()._build_citations(chunks)

        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conversation.id, 'citations': [c.model_dump() for c in citations]})}\n\n"

        full_answer = ""
        llm = get_llm()
        async for token in llm.generate_stream(request.message, chunks, history):
            full_answer += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_answer,
            citations=json.dumps([c.model_dump() for c in citations]),
        )
        db.add(assistant_msg)

        if conversation.title == "New Chat":
            conversation.title = request.message[:80] + ("..." if len(request.message) > 80 else "")

        await db.flush()
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    async def _retrieve(
        self,
        user_id: int,
        query: str,
        document_ids: Optional[List[int]],
        search_mode: str,
    ):
        retriever = HybridRetriever(user_id)
        chunks = retriever.retrieve(query, document_ids=document_ids, search_mode=search_mode)
        reranker = get_reranker()
        return reranker.rerank(query, chunks)

    async def _get_or_create_conversation(
        self,
        db: AsyncSession,
        user: User,
        conversation_id: Optional[int],
        message: str,
    ) -> Conversation:
        if conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user.id,
                )
            )
            conv = result.scalar_one_or_none()
            if conv:
                return conv

        conv = Conversation(user_id=user.id, title="New Chat")
        db.add(conv)
        await db.flush()
        return conv

    async def _get_history(self, db: AsyncSession, conversation_id: int) -> List[dict]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages[:-1]]

    async def get_history(self, db: AsyncSession, user: User) -> List[Conversation]:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .order_by(Conversation.updated_at.desc())
            .limit(50)
        )
        return list(result.scalars().all())

    async def get_conversation(self, db: AsyncSession, user: User, conv_id: int) -> Conversation:
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conv_id, Conversation.user_id == user.id)
        )
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conv

    async def delete_conversation(self, db: AsyncSession, user: User, conv_id: int) -> None:
        conv = await self.get_conversation(db, user, conv_id)
        await db.delete(conv)

    async def delete_all_history(self, db: AsyncSession, user: User) -> None:
        result = await db.execute(select(Conversation).where(Conversation.user_id == user.id))
        for conv in result.scalars().all():
            await db.delete(conv)

    @staticmethod
    def conversation_to_response(conv: Conversation) -> ConversationResponse:
        messages = []
        for m in conv.messages:
            citations = None
            if m.citations:
                try:
                    citations = [Citation(**c) for c in json.loads(m.citations)]
                except (json.JSONDecodeError, TypeError):
                    pass
            messages.append(
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    citations=citations,
                    created_at=m.created_at,
                )
            )
        return ConversationResponse(
            id=conv.id,
            title=conv.title,
            is_favorite=conv.is_favorite,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=messages,
        )
