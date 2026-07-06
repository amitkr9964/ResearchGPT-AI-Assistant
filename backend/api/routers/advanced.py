"""Advanced AI features API routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import (
    CompareRequest,
    CompareResponse,
    FlashcardsRequest,
    FlashcardsResponse,
    LiteratureReviewRequest,
    QuizRequest,
    QuizResponse,
    SummaryResponse,
)
from backend.services.advanced_service import AdvancedService

router = APIRouter(tags=["Advanced AI"])
advanced_service = AdvancedService()


@router.get("/summary/{doc_id}", response_model=SummaryResponse)
async def get_summary(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await advanced_service.summarize(db, current_user, doc_id)
    return SummaryResponse(document_id=doc_id, summary=summary)


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await advanced_service.compare(
        db, current_user, request.document_id_1, request.document_id_2
    )


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await advanced_service.generate_quiz(
        db, current_user, request.document_id, request.num_questions
    )


@router.post("/flashcards", response_model=FlashcardsResponse)
async def generate_flashcards(
    request: FlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await advanced_service.generate_flashcards(
        db, current_user, request.document_id, request.num_cards
    )


@router.post("/literature-review")
async def literature_review(
    request: LiteratureReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    review = await advanced_service.literature_review(db, current_user, request.document_ids)
    return {"review": review}


@router.get("/entities/{doc_id}")
async def extract_entities(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    entities = await advanced_service.extract_entities(db, current_user, doc_id)
    return {"entities": entities}


@router.get("/keywords/{doc_id}")
async def extract_keywords(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    keywords = await advanced_service.extract_keywords(db, current_user, doc_id)
    return {"keywords": keywords}
