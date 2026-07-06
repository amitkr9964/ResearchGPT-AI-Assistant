"""Google Gemini LLM integration with streaming support."""

import json
from typing import AsyncGenerator, List, Optional

import google.generativeai as genai

from backend.config import get_settings
from backend.models.schemas import Citation
from backend.rag.retriever import RetrievedChunk
from backend.utils.logger import logger

SYSTEM_PROMPT = """You are ResearchGPT, an AI research assistant. You answer questions ONLY using the provided context from uploaded documents.

RULES:
1. Answer ONLY from the retrieved context below. Never use outside knowledge.
2. If the answer is not in the context, respond exactly: "I could not find this information in your uploaded documents."
3. Never hallucinate or invent information.
4. Always cite sources using [Source N] notation where N corresponds to the source number.
5. Format responses in clear Markdown with proper headings, lists, code blocks, tables, and math when appropriate.
6. Be precise, academic, and thorough.

CONTEXT:
{context}

CONVERSATION HISTORY:
{history}
"""


class GeminiLLM:
    def __init__(self) -> None:
        settings = get_settings()
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.settings = settings

    def _build_context(self, chunks: List[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context found."

        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Source {i}] Document: {chunk.document_name} | Page: {chunk.page_number}\n"
                f"Content: {chunk.content}\n"
                f"Relevance Score: {chunk.score:.2f}"
            )
        return "\n\n".join(parts)

    def _build_citations(self, chunks: List[RetrievedChunk]) -> List[Citation]:
        citations = []
        for chunk in chunks:
            # If the score is outside [-1, 1], it is a raw logit from a cross-encoder model.
            # We map raw logits to [0, 100]% using the sigmoid function.
            if chunk.score < -1.0 or chunk.score > 1.0:
                import math
                try:
                    confidence = (1.0 / (1.0 + math.exp(-chunk.score))) * 100.0
                except OverflowError:
                    confidence = 0.0 if chunk.score < 0 else 100.0
            else:
                # Cosine similarity is in [-1, 1], map it to [0, 100]%
                confidence = max(0.0, chunk.score) * 100.0

            citations.append(
                Citation(
                    document_name=chunk.document_name,
                    document_id=chunk.document_id,
                    page_number=chunk.page_number,
                    paragraph=chunk.content[:500] + ("..." if len(chunk.content) > 500 else ""),
                    confidence_score=round(min(confidence, 100), 1),
                )
            )
        return citations

    async def generate(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        history: Optional[List[dict]] = None,
    ) -> tuple[str, List[Citation]]:
        context = self._build_context(chunks)
        history_text = ""
        if history:
            for msg in history[-6:]:
                history_text += f"{msg['role'].upper()}: {msg['content']}\n"

        prompt = SYSTEM_PROMPT.format(context=context, history=history_text or "None")
        full_prompt = f"{prompt}\n\nUSER QUESTION: {query}\n\nANSWER:"

        try:
            response = await self.model.generate_content_async(full_prompt)
            answer = response.text if response.text else "I could not find this information in your uploaded documents."
        except Exception as e:
            logger.error("Gemini generation failed: %s", e)
            answer = "I encountered an error generating a response. Please try again."

        citations = self._build_citations(chunks)
        return answer, citations

    async def generate_stream(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        history: Optional[List[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        context = self._build_context(chunks)
        history_text = ""
        if history:
            for msg in history[-6:]:
                history_text += f"{msg['role'].upper()}: {msg['content']}\n"

        prompt = SYSTEM_PROMPT.format(context=context, history=history_text or "None")
        full_prompt = f"{prompt}\n\nUSER QUESTION: {query}\n\nANSWER:"

        try:
            response = await self.model.generate_content_async(full_prompt, stream=True)
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error("Gemini streaming failed: %s", e)
            yield "I encountered an error generating a response. Please try again."

    async def generate_raw(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text or ""
        except Exception as e:
            logger.error("Gemini raw generation failed: %s", e)
            return ""


_llm: GeminiLLM | None = None


def get_llm() -> GeminiLLM:
    global _llm
    if _llm is None:
        _llm = GeminiLLM()
    return _llm
