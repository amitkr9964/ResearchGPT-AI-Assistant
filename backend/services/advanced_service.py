"""Advanced AI features: summarization, comparison, quiz, flashcards, etc."""

import json
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Document, DocumentChunk, User
from backend.models.schemas import (
    CompareResponse,
    Flashcard,
    FlashcardsResponse,
    QuizQuestion,
    QuizResponse,
)
from backend.rag.llm import get_llm
from backend.utils.text_cleaner import extract_keywords


class AdvancedService:
    async def summarize(self, db: AsyncSession, user: User, document_id: int) -> str:
        doc = await self._get_document(db, user, document_id)
        if doc.summary:
            return doc.summary

        chunks = await self._get_chunks(db, document_id)
        content = "\n\n".join(c.content for c in chunks[:20])

        prompt = f"""Summarize the following research document titled "{doc.filename}".
Provide a comprehensive academic summary covering:
- Main thesis/objective
- Key findings
- Methodology (if applicable)
- Conclusions
- Important contributions

Document content:
{content[:15000]}

Write a clear, structured summary in Markdown format."""

        summary = await get_llm().generate_raw(prompt)
        doc.summary = summary
        await db.flush()
        return summary

    async def compare(
        self, db: AsyncSession, user: User, doc_id_1: int, doc_id_2: int
    ) -> CompareResponse:
        doc1 = await self._get_document(db, user, doc_id_1)
        doc2 = await self._get_document(db, user, doc_id_2)

        chunks1 = await self._get_chunks(db, doc_id_1)
        chunks2 = await self._get_chunks(db, doc_id_2)

        content1 = "\n".join(c.content for c in chunks1[:15])[:8000]
        content2 = "\n".join(c.content for c in chunks2[:15])[:8000]

        prompt = f"""Compare these two research documents:

DOCUMENT 1: {doc1.filename}
{content1}

DOCUMENT 2: {doc2.filename}
{content2}

Provide a detailed comparison in JSON format:
{{
  "comparison": "Overall comparison narrative",
  "similarities": ["similarity 1", "similarity 2", ...],
  "differences": ["difference 1", "difference 2", ...]
}}

Return ONLY valid JSON."""

        raw = await get_llm().generate_raw(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = json.loads(raw[start:end])
            return CompareResponse(**data)
        except (json.JSONDecodeError, ValueError):
            return CompareResponse(
                comparison=raw,
                similarities=[],
                differences=[],
            )

    async def generate_quiz(
        self, db: AsyncSession, user: User, document_id: int, num_questions: int = 5
    ) -> QuizResponse:
        doc = await self._get_document(db, user, document_id)
        chunks = await self._get_chunks(db, document_id)
        content = "\n".join(c.content for c in chunks[:20])[:12000]

        prompt = f"""Based on the document "{doc.filename}", generate {num_questions} multiple-choice quiz questions.

Content:
{content}

Return JSON array:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "correct option text",
    "explanation": "why this is correct"
  }}
]

Return ONLY valid JSON array."""

        raw = await get_llm().generate_raw(prompt)
        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            data = json.loads(raw[start:end])
            questions = [QuizQuestion(**q) for q in data]
            return QuizResponse(questions=questions)
        except (json.JSONDecodeError, ValueError):
            return QuizResponse(questions=[])

    async def generate_flashcards(
        self, db: AsyncSession, user: User, document_id: int, num_cards: int = 10
    ) -> FlashcardsResponse:
        doc = await self._get_document(db, user, document_id)
        chunks = await self._get_chunks(db, document_id)
        content = "\n".join(c.content for c in chunks[:20])[:12000]

        prompt = f"""Create {num_cards} study flashcards from "{doc.filename}".

Content:
{content}

Return JSON array:
[{{"front": "term/concept", "back": "definition/explanation"}}]

Return ONLY valid JSON array."""

        raw = await get_llm().generate_raw(prompt)
        try:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            data = json.loads(raw[start:end])
            cards = [Flashcard(**c) for c in data]
            return FlashcardsResponse(cards=cards)
        except (json.JSONDecodeError, ValueError):
            return FlashcardsResponse(cards=[])

    async def literature_review(self, db: AsyncSession, user: User, document_ids: List[int]) -> str:
        contents = []
        for doc_id in document_ids:
            doc = await self._get_document(db, user, doc_id)
            chunks = await self._get_chunks(db, doc_id)
            text = "\n".join(c.content for c in chunks[:10])[:5000]
            contents.append(f"## {doc.filename}\n{text}")

        combined = "\n\n".join(contents)

        prompt = f"""Write a comprehensive literature review synthesizing these research documents:

{combined[:20000]}

Structure the review with:
1. Introduction
2. Thematic analysis
3. Key findings across papers
4. Gaps and future directions
5. Conclusion

Use academic Markdown formatting with proper citations referencing document names."""

        return await get_llm().generate_raw(prompt)

    async def extract_entities(self, db: AsyncSession, user: User, document_id: int) -> str:
        doc = await self._get_document(db, user, document_id)
        chunks = await self._get_chunks(db, document_id)
        content = "\n".join(c.content for c in chunks[:15])[:10000]

        prompt = f"""Extract key entities from "{doc.filename}":
- People
- Organizations
- Concepts/Topics
- Methods
- Datasets
- Key terms

Content:
{content}

Return structured Markdown with categorized entity lists."""

        return await get_llm().generate_raw(prompt)

    async def extract_keywords(self, db: AsyncSession, user: User, document_id: int) -> List[str]:
        chunks = await self._get_chunks(db, document_id)
        content = " ".join(c.content for c in chunks)
        return extract_keywords(content, max_keywords=30)

    async def _get_document(self, db: AsyncSession, user: User, doc_id: int) -> Document:
        result = await db.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user.id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    async def _get_chunks(self, db: AsyncSession, document_id: int) -> List[DocumentChunk]:
        result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())
