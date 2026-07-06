"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


# Auth
class UserSignup(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    dark_mode: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    dark_mode: Optional[bool] = None


# Documents
class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    page_count: int
    chunk_count: int
    author: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentRename(BaseModel):
    filename: str = Field(min_length=1, max_length=500)


class DocumentUpdate(BaseModel):
    author: Optional[str] = None
    tags: Optional[str] = None


# Citations
class Citation(BaseModel):
    document_name: str
    document_id: int
    page_number: int
    paragraph: str
    confidence_score: float


# Chat
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    document_ids: Optional[List[int]] = None
    search_mode: str = "hybrid"  # semantic, keyword, hybrid
    stream: bool = True


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    citations: List[Citation]
    sources: List[Dict[str, Any]] = []


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: int
    title: str
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_favorite: Optional[bool] = None


# Search
class SearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    filename: Optional[str] = None
    search_mode: str = "hybrid"
    top_k: int = 10


class SearchResult(BaseModel):
    document_id: int
    document_name: str
    page_number: int
    content: str
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int


# Advanced AI
class CompareRequest(BaseModel):
    document_id_1: int
    document_id_2: int


class QuizRequest(BaseModel):
    document_id: int
    num_questions: int = 5


class FlashcardsRequest(BaseModel):
    document_id: int
    num_cards: int = 10


class SummaryResponse(BaseModel):
    document_id: int
    summary: str


class CompareResponse(BaseModel):
    comparison: str
    similarities: List[str]
    differences: List[str]


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class Flashcard(BaseModel):
    front: str
    back: str


class FlashcardsResponse(BaseModel):
    cards: List[Flashcard]


class LiteratureReviewRequest(BaseModel):
    document_ids: List[int]


class ExportRequest(BaseModel):
    conversation_id: int
    format: str = "markdown"  # markdown, pdf, docx


# Generic
class ErrorResponse(BaseModel):
    detail: str
