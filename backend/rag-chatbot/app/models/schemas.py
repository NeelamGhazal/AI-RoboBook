"""
Pydantic models for request/response validation.
Based on OpenAPI specification in contracts/openapi.yaml.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# Session schemas
class SessionCreate(BaseModel):
    """Request to create a new session."""

    user_id: Optional[str] = Field(None, max_length=255)
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    """Response with session information."""

    session_id: str
    created_at: datetime
    last_activity: datetime


# Citation schema
class Citation(BaseModel):
    """Source citation with confidence score."""

    chunk_id: UUID
    chapter: str
    section: str
    url: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    text_snippet: Optional[str] = Field(None, max_length=200)


# Chat request schemas
class ChatRequest(BaseModel):
    """Request for general Q&A."""

    session_id: str
    question: str = Field(min_length=1, max_length=1000)
    selected_text: Optional[str] = Field(None, max_length=5000)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question is not empty after stripping."""
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


# Chat response schemas
class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    answer: str
    sources: List[dict]
    metadata: dict


class MessageResponse(BaseModel):
    """Message in chat history."""

    role: str
    content: str
    sources: Optional[List[dict]] = None
    created_at: datetime


# History schemas
class HistoryMessage(BaseModel):
    """Message in chat history."""

    message_id: UUID
    role: str
    content: str
    timestamp: datetime
    token_count: int
    selected_text: Optional[str] = None
    citations: Optional[List[Citation]] = None


class ChatHistoryResponse(BaseModel):
    """Response with chat history."""

    session_id: UUID
    messages: List[HistoryMessage]
    total: int
    limit: int
    offset: int


# Error response schema
class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: str
    message: str
    timestamp: datetime
    details: Optional[dict] = None


# Health check schema
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    dependencies: Optional[dict] = None
    version: Optional[str] = None
