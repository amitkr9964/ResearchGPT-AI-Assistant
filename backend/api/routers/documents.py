"""Document management API routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import DocumentRename, DocumentResponse, DocumentUpdate
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])
doc_service = DocumentService()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    author: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await doc_service.upload_document(db, current_user, file, author, tags)
    return DocumentService.to_response(doc)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    docs = await doc_service.get_documents(db, current_user, search)
    return [DocumentService.to_response(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await doc_service.get_document(db, current_user, doc_id)
    return DocumentService.to_response(doc)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await doc_service.delete_document(db, current_user, doc_id)


@router.patch("/{doc_id}/rename", response_model=DocumentResponse)
async def rename_document(
    doc_id: int,
    data: DocumentRename,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await doc_service.rename_document(db, current_user, doc_id, data.filename)
    return DocumentService.to_response(doc)


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await doc_service.update_document(db, current_user, doc_id, data)
    return DocumentService.to_response(doc)
