"""Simple score-based reranker to save server memory (Render free tier friendly)."""

from typing import List
from backend.config import get_settings
from backend.rag.retriever import RetrievedChunk


class Reranker:
    def __init__(self) -> None:
        self.settings = get_settings()

    def rerank(self, query: str, chunks: List[RetrievedChunk], top_k: int | None = None) -> List[RetrievedChunk]:
        if not chunks:
            return []

        k = top_k or self.settings.RERANK_TOP_K
        # Since we are running on Render Free Tier, we perform score-based reranking
        # which sorts the retrieved chunks based on their retrieval (hybrid) score.
        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks[:k]


_reranker: Reranker | None = None


def get_reranker() -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker
