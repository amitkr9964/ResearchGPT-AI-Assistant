"""Hybrid retrieval combining semantic and keyword search."""

import re
from dataclasses import dataclass
from typing import List, Optional

from backend.config import get_settings
from backend.rag.embeddings import get_embedding_service
from backend.rag.vector_store import VectorRecord, get_vector_store
from backend.utils.logger import logger


@dataclass
class RetrievedChunk:
    document_id: int
    document_name: str
    page_number: int
    content: str
    chunk_index: int
    score: float
    search_type: str


class HybridRetriever:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store(user_id)
        self.settings = get_settings()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        document_ids: Optional[List[int]] = None,
        search_mode: str = "hybrid",
    ) -> List[RetrievedChunk]:
        k = top_k or self.settings.TOP_K

        if search_mode == "keyword":
            return self._keyword_search(query, k, document_ids)
        elif search_mode == "semantic":
            return self._semantic_search(query, k, document_ids)
        else:
            semantic = self._semantic_search(query, k, document_ids)
            keyword = self._keyword_search(query, k, document_ids)
            return self._merge_results(semantic, keyword, k)

    def _semantic_search(
        self,
        query: str,
        top_k: int,
        document_ids: Optional[List[int]],
    ) -> List[RetrievedChunk]:
        query_embedding = self.embedding_service.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k=top_k, document_ids=document_ids)

        chunks: List[RetrievedChunk] = []
        for record, score in results:
            chunks.append(
                RetrievedChunk(
                    document_id=record.document_id,
                    document_name=record.filename,
                    page_number=record.page_number,
                    content=record.content,
                    chunk_index=record.chunk_index,
                    score=score,
                    search_type="semantic",
                )
            )
        return chunks

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        document_ids: Optional[List[int]],
    ) -> List[RetrievedChunk]:
        query_terms = set(re.findall(r"\b\w+\b", query.lower()))
        if not query_terms:
            return []

        scored: List[tuple[VectorRecord, float]] = []
        for record in self.vector_store.metadata:
            if document_ids and record.document_id not in document_ids:
                continue
            text_terms = set(re.findall(r"\b\w+\b", record.content.lower()))
            overlap = len(query_terms & text_terms)
            if overlap > 0:
                score = overlap / len(query_terms)
                scored.append((record, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        chunks: List[RetrievedChunk] = []
        for record, score in scored[:top_k]:
            chunks.append(
                RetrievedChunk(
                    document_id=record.document_id,
                    document_name=record.filename,
                    page_number=record.page_number,
                    content=record.content,
                    chunk_index=record.chunk_index,
                    score=score,
                    search_type="keyword",
                )
            )
        return chunks

    def _merge_results(
        self,
        semantic: List[RetrievedChunk],
        keyword: List[RetrievedChunk],
        top_k: int,
    ) -> List[RetrievedChunk]:
        seen: dict[tuple[int, int], RetrievedChunk] = {}

        for chunk in semantic:
            key = (chunk.document_id, chunk.chunk_index)
            if key not in seen or chunk.score > seen[key].score:
                seen[key] = chunk

        for chunk in keyword:
            key = (chunk.document_id, chunk.chunk_index)
            if key in seen:
                seen[key].score = (seen[key].score + chunk.score) / 2
            else:
                seen[key] = chunk

        merged = sorted(seen.values(), key=lambda x: x.score, reverse=True)
        return merged[:top_k]
