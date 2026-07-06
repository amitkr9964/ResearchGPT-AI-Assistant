"""Search service for semantic, keyword, and hybrid search."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Document, User
from backend.models.schemas import SearchRequest, SearchResponse, SearchResult
from backend.rag.reranker import get_reranker
from backend.rag.retriever import HybridRetriever


class SearchService:
    async def search(
        self,
        db: AsyncSession,
        user: User,
        request: SearchRequest,
    ) -> SearchResponse:
        document_ids = request.document_ids

        if request.tags or request.author or request.filename:
            document_ids = await self._filter_documents(
                db, user, document_ids, request.tags, request.author, request.filename
            )

        retriever = HybridRetriever(user.id)
        chunks = retriever.retrieve(
            request.query,
            top_k=request.top_k,
            document_ids=document_ids,
            search_mode=request.search_mode,
        )

        reranker = get_reranker()
        ranked = reranker.rerank(request.query, chunks, top_k=request.top_k)

        results = [
            SearchResult(
                document_id=c.document_id,
                document_name=c.document_name,
                page_number=c.page_number,
                content=c.content,
                score=round(c.score, 4),
                chunk_index=c.chunk_index,
            )
            for c in ranked
        ]

        return SearchResponse(results=results, total=len(results))

    async def _filter_documents(
        self,
        db: AsyncSession,
        user: User,
        document_ids: Optional[List[int]],
        tags: Optional[List[str]],
        author: Optional[str],
        filename: Optional[str],
    ) -> List[int]:
        query = select(Document.id).where(Document.user_id == user.id)

        if document_ids:
            query = query.where(Document.id.in_(document_ids))
        if author:
            query = query.where(Document.author.ilike(f"%{author}%"))
        if filename:
            query = query.where(Document.filename.ilike(f"%{filename}%"))

        result = await db.execute(query)
        ids = list(result.scalars().all())

        if tags:
            filtered = []
            for doc_id in ids:
                doc_result = await db.execute(select(Document).where(Document.id == doc_id))
                doc = doc_result.scalar_one_or_none()
                if doc and doc.tags:
                    doc_tags = [t.strip().lower() for t in doc.tags.split(",")]
                    if any(t.lower() in doc_tags for t in tags):
                        filtered.append(doc_id)
            return filtered

        return ids
