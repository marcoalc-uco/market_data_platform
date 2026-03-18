"""Dependency injection factories for the chat module.

Provides FastAPI Depends-compatible factories for OllamaClient,
ChromaDB, DocumentService, and ChatService. These are separated
from the core api/dependencies.py to avoid circular imports.
"""

from typing import Annotated, Any

from fastapi import Depends, Request

from market_data_backend_platform.api.dependencies import (
    InstrumentRepoDep,
    MarketPriceRepoDep,
    SettingsDep,
)
from market_data_backend_platform.chat.clients.ollama import OllamaClient
from market_data_backend_platform.chat.services.chat_service import ChatService
from market_data_backend_platform.chat.services.document_service import DocumentService


def get_ollama_client(settings: SettingsDep) -> OllamaClient:
    """Create OllamaClient configured from application settings.

    Args:
        settings: Application settings with Ollama base URL.

    Returns:
        OllamaClient instance.
    """
    return OllamaClient(base_url=settings.ollama_base_url)


OllamaClientDep = Annotated[OllamaClient, Depends(get_ollama_client)]


def get_chromadb_client(request: Request) -> Any:
    """Retrieve the ChromaDB client initialized during app lifespan.

    Args:
        request: Current HTTP request (provides access to app.state).

    Returns:
        ChromaDB PersistentClient instance.
    """
    return request.app.state.chromadb_client


ChromaDBClientDep = Annotated[Any, Depends(get_chromadb_client)]


def get_document_service(
    ollama_client: OllamaClientDep,
    chromadb_client: ChromaDBClientDep,
    settings: SettingsDep,
) -> DocumentService:
    """Create DocumentService with injected dependencies.

    Args:
        ollama_client: OllamaClient for embedding generation.
        chromadb_client: ChromaDB client for vector storage.
        settings: Application settings.

    Returns:
        DocumentService instance.
    """
    return DocumentService(
        ollama_client=ollama_client,
        embedding_model=settings.ollama_embedding_model,
        chromadb_client=chromadb_client,
    )


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


def get_chat_service(
    ollama_client: OllamaClientDep,
    price_repo: MarketPriceRepoDep,
    instrument_repo: InstrumentRepoDep,
    document_service: DocumentServiceDep,
    settings: SettingsDep,
) -> ChatService:
    """Create ChatService with all RAG dependencies.

    Args:
        ollama_client: OllamaClient for LLM inference.
        price_repo: Repository for OHLCV price data.
        instrument_repo: Repository for instrument metadata.
        document_service: Service for RAG document retrieval.
        settings: Application settings.

    Returns:
        ChatService instance.
    """
    return ChatService(
        ollama_client=ollama_client,
        chat_model=settings.ollama_chat_model,
        price_repo=price_repo,
        instrument_repo=instrument_repo,
        document_service=document_service,
        max_price_rows=settings.chat_max_price_rows,
        max_doc_chunks=settings.chat_max_doc_chunks,
    )


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
