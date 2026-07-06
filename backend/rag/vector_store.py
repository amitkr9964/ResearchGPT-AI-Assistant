"""FAISS vector store with per-user index management."""

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np

from backend.config import get_settings
from backend.rag.embeddings import get_embedding_service
from backend.utils.logger import logger


@dataclass
class VectorRecord:
    faiss_index: int
    document_id: int
    chunk_index: int
    page_number: int
    content: str
    filename: str
    user_id: int


class FAISSVectorStore:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        settings = get_settings()
        self.index_path = settings.FAISS_DIR / f"user_{user_id}.index"
        self.meta_path = settings.FAISS_DIR / f"user_{user_id}.meta"
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[VectorRecord] = []
        self._load()

    def _load(self) -> None:
        if self.index_path.exists() and self.meta_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                
                # Recreate the index if dimensions changed (e.g. switching embedding models)
                if self.index.d != self.dimension:
                    logger.warning("FAISS index dimension mismatch (stored: %d, current: %d). Recreating index.", self.index.d, self.dimension)
                    self.index = faiss.IndexFlatIP(self.dimension)
                    self.metadata = []
                else:
                    logger.info("Loaded FAISS index for user %s with %d vectors", self.user_id, len(self.metadata))
            except Exception as e:
                logger.error("Failed to load FAISS index: %s. Creating new index.", e)
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = []
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def _save(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_vectors(
        self,
        embeddings: np.ndarray,
        records: List[VectorRecord],
    ) -> None:
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)

        faiss.normalize_L2(embeddings)
        start_idx = self.index.ntotal
        self.index.add(embeddings)

        for i, record in enumerate(records):
            record.faiss_index = start_idx + i
            self.metadata.append(record)

        self._save()
        logger.info("Added %d vectors for user %s", len(records), self.user_id)

    def remove_document(self, document_id: int) -> None:
        remaining = [m for m in self.metadata if m.document_id != document_id]
        if len(remaining) == len(self.metadata):
            return

        self.metadata = remaining
        self._rebuild_index()
        self._save()

    def _rebuild_index(self) -> None:
        if not self.metadata:
            self.index = faiss.IndexFlatIP(self.dimension)
            return

        embedding_service = get_embedding_service()
        texts = [m.content for m in self.metadata]
        embeddings = embedding_service.embed_texts(texts)
        faiss.normalize_L2(embeddings)

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        for i, record in enumerate(self.metadata):
            record.faiss_index = i

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        document_ids: Optional[List[int]] = None,
    ) -> List[Tuple[VectorRecord, float]]:
        if self.index is None or self.index.ntotal == 0:
            return []

        query = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query)

        k = min(top_k * 3, self.index.ntotal)
        scores, indices = self.index.search(query, k)

        results: List[Tuple[VectorRecord, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            record = self.metadata[idx]
            if document_ids and record.document_id not in document_ids:
                continue
            results.append((record, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


_store_cache: Dict[int, FAISSVectorStore] = {}


def get_vector_store(user_id: int) -> FAISSVectorStore:
    if user_id not in _store_cache:
        _store_cache[user_id] = FAISSVectorStore(user_id)
    return _store_cache[user_id]


def invalidate_store(user_id: int) -> None:
    _store_cache.pop(user_id, None)
