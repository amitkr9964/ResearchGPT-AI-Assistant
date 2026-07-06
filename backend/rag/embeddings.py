"""Google Gemini API embedding service."""

from typing import List
import numpy as np
import google.generativeai as genai
from backend.config import get_settings
from backend.utils.logger import logger


class EmbeddingService:
    _instance: "EmbeddingService | None" = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        settings = get_settings()
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32)
        settings = get_settings()
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        try:
            # Batch call to Gemini embedding service
            response = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=texts,
                task_type="retrieval_document",
            )
            embeddings = response.get("embedding", [])
            return np.array(embeddings, dtype=np.float32)
        except Exception as e:
            logger.error("Failed to generate embeddings via Gemini: %s", e)
            # Return dummy vectors if API fails
            return np.zeros((len(texts), settings.EMBEDDING_DIMENSION), dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        settings = get_settings()
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        try:
            response = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query",
            )
            embedding = response.get("embedding", [])
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error("Failed to generate query embedding via Gemini: %s", e)
            return np.zeros(settings.EMBEDDING_DIMENSION, dtype=np.float32)

    @property
    def dimension(self) -> int:
        return get_settings().EMBEDDING_DIMENSION


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
