"""Search API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import SearchRequest, SearchResponse
from backend.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])
search_service = SearchService()


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await search_service.search(db, current_user, request)
