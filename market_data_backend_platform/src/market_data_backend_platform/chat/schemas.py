"""Pydantic schemas for the chat API endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message in the conversation history."""

    role: Literal["user", "assistant"]
    content: str


class ChatMessageRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document for RAG context."""

    filename: str
    chunks_stored: int
    instrument_id: int


class DocumentInfo(BaseModel):
    """Metadata about an uploaded document."""

    filename: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Response listing all uploaded documents for an instrument."""

    instrument_id: int
    documents: list[DocumentInfo]
