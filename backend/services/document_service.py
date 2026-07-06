"""Document upload, processing, and management service."""

import shutil
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.database.models import Document, DocumentChunk, User
from backend.models.schemas import DocumentResponse, DocumentUpdate
from backend.rag.chunker import SemanticChunker
from backend.rag.embeddings import get_embedding_service
from backend.rag.vector_store import VectorRecord, get_vector_store, invalidate_store
from backend.utils.document_parser import DocumentParser
from backend.utils.logger import logger


class DocumentService:
    def __init__(self) -> None:
        self.parser = DocumentParser()
        self.chunker = SemanticChunker()
        self.embedding_service = get_embedding_service()
        self.settings = get_settings()

    async def upload_document(
        self,
        db: AsyncSession,
        user: User,
        file: UploadFile,
        author: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Document:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in self.settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {suffix} not supported. Allowed: {self.settings.ALLOWED_EXTENSIONS}",
            )

        content = await file.read()
        max_size = self.settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {self.settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        unique_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = self.settings.UPLOAD_DIR / str(user.id) / unique_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

        doc = Document(
            user_id=user.id,
            filename=file.filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_type=suffix,
            file_size=len(content),
            author=author,
            tags=tags,
            status="processing",
        )
        db.add(doc)
        await db.flush()

        try:
            await self._process_document(db, doc)
            doc.status = "ready"
            await db.flush()
        except Exception as e:
            logger.error("Document processing failed:", exc_info=True)
            doc.status = "error"
            await db.flush()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {str(e)}",
            )

        await db.refresh(doc)
        return doc

    async def _process_document(self, db: AsyncSession, doc: Document) -> None:
        parsed = self.parser.parse(Path(doc.file_path))
        doc.page_count = parsed.page_count

        if parsed.metadata.get("author") and not doc.author:
            doc.author = parsed.metadata["author"]

        chunks = self.chunker.chunk_document(parsed, doc.id, doc.filename)
        if not chunks:
            raise ValueError("No text content extracted from document")

        texts = [c.content for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        db_chunks: List[DocumentChunk] = []
        vector_records: List[VectorRecord] = []

        for chunk, embedding_idx in zip(chunks, range(len(chunks))):
            db_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                page_number=chunk.page_number,
            )
            db_chunks.append(db_chunk)

            vector_records.append(
                VectorRecord(
                    faiss_index=0,
                    document_id=doc.id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    filename=doc.filename,
                    user_id=doc.user_id,
                )
            )

        db.add_all(db_chunks)
        doc.chunk_count = len(db_chunks)

        vector_store = get_vector_store(doc.user_id)
        vector_store.add_vectors(embeddings, vector_records)

    async def get_documents(
        self,
        db: AsyncSession,
        user: User,
        search: Optional[str] = None,
    ) -> List[Document]:
        query = select(Document).where(Document.user_id == user.id)
        if search:
            query = query.where(
                or_(
                    Document.filename.ilike(f"%{search}%"),
                    Document.author.ilike(f"%{search}%"),
                    Document.tags.ilike(f"%{search}%"),
                )
            )
        query = query.order_by(Document.updated_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_document(self, db: AsyncSession, user: User, doc_id: int) -> Document:
        result = await db.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user.id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return doc

    async def delete_document(self, db: AsyncSession, user: User, doc_id: int) -> None:
        doc = await self.get_document(db, user, doc_id)

        file_path = Path(doc.file_path)
        if file_path.exists():
            file_path.unlink()

        vector_store = get_vector_store(user.id)
        vector_store.remove_document(doc.id)
        invalidate_store(user.id)

        await db.delete(doc)

    async def rename_document(self, db: AsyncSession, user: User, doc_id: int, new_name: str) -> Document:
        doc = await self.get_document(db, user, doc_id)
        doc.filename = new_name
        await db.flush()
        await db.refresh(doc)
        return doc

    async def update_document(
        self, db: AsyncSession, user: User, doc_id: int, data: DocumentUpdate
    ) -> Document:
        doc = await self.get_document(db, user, doc_id)
        if data.author is not None:
            doc.author = data.author
        if data.tags is not None:
            doc.tags = data.tags
        await db.flush()
        await db.refresh(doc)
        return doc

    @staticmethod
    def to_response(doc: Document) -> DocumentResponse:
        return DocumentResponse.model_validate(doc)
