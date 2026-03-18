"""Chat API endpoints with Ollama LLM and RAG support.

Provides streaming chat completions, document upload for RAG context,
and document listing for a given instrument.

Endpoints:
    POST /{instrument_id}           - Stream chat response (SSE)
    POST /{instrument_id}/documents - Upload a document for RAG
    GET  /{instrument_id}/documents - List uploaded documents
"""

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from market_data_backend_platform.chat.dependencies import (
    ChatServiceDep,
    DocumentServiceDep,
)
from market_data_backend_platform.chat.schemas import (
    ChatMessageRequest,
    DocumentInfo,
    DocumentListResponse,
    DocumentUploadResponse,
)
from market_data_backend_platform.chat.services.document_service import (
    ALLOWED_EXTENSIONS,
)
from market_data_backend_platform.core import ValidationError, get_logger

logger = get_logger(__name__)

router = APIRouter()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/{instrument_id}")
async def chat(
    instrument_id: int,
    body: ChatMessageRequest,
    chat_service: ChatServiceDep,
) -> StreamingResponse:
    """Stream a chat response about the given instrument.

    Uses RAG to augment the LLM context with OHLCV prices
    and user-uploaded documents.

    Args:
        instrument_id: ID of the instrument to discuss.
        body: Chat message and conversation history.
        chat_service: Injected ChatService with RAG dependencies.

    Returns:
        SSE stream of token events.
    """
    history = [{"role": m.role, "content": m.content} for m in body.history]

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for token in chat_service.chat_stream(
                instrument_id, body.message, history
            ):
                yield f"data: {json.dumps(token)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("chat_stream_error", error=str(e))
            yield f"data: {json.dumps(f'Error: {e}')}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{instrument_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    instrument_id: int,
    file: UploadFile,
    doc_service: DocumentServiceDep,
) -> DocumentUploadResponse:
    """Upload a document for RAG context.

    Supported file types: .pdf, .md, .txt
    Maximum file size: 10 MB

    Args:
        instrument_id: ID of the instrument this document relates to.
        file: The uploaded file.
        doc_service: Injected DocumentService.

    Returns:
        Upload result with filename and chunk count.
    """
    # Validate file extension
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed: {allowed}",
            details={"filename": filename, "allowed": list(ALLOWED_EXTENSIONS)},
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File too large ({len(content)} bytes). Maximum: {MAX_UPLOAD_SIZE} bytes.",
            details={"filename": filename, "size": len(content)},
        )

    chunks_stored = await doc_service.ingest_document(instrument_id, filename, content)

    return DocumentUploadResponse(
        filename=filename,
        chunks_stored=chunks_stored,
        instrument_id=instrument_id,
    )


@router.get("/{instrument_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    instrument_id: int,
    doc_service: DocumentServiceDep,
) -> DocumentListResponse:
    """List all uploaded documents for an instrument.

    Args:
        instrument_id: ID of the instrument.
        doc_service: Injected DocumentService.

    Returns:
        List of documents with their chunk counts.
    """
    docs = doc_service.list_documents(instrument_id)

    return DocumentListResponse(
        instrument_id=instrument_id,
        documents=[
            DocumentInfo(
                filename=str(d["filename"]),
                chunk_count=int(d["chunk_count"]),
            )
            for d in docs
        ],
    )
