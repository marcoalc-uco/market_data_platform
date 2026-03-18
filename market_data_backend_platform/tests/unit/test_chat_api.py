"""Tests for Chat API endpoints.

This module contains TDD tests for the chat API layer (Phase 2).
Tests cover:
- POST /api/v1/chat/{instrument_id} (SSE streaming chat)
- POST /api/v1/chat/{instrument_id}/documents (document upload)
- GET  /api/v1/chat/{instrument_id}/documents (list documents)
- JWT protection on all endpoints
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from market_data_backend_platform.api.dependencies import get_db_session
from market_data_backend_platform.auth.dependencies import get_current_user
from market_data_backend_platform.chat.dependencies import (
    get_chat_service,
    get_document_service,
)
from market_data_backend_platform.chat.services.chat_service import ChatService
from market_data_backend_platform.chat.services.document_service import DocumentService
from market_data_backend_platform.main import app
from market_data_backend_platform.models import Base

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="engine")
def fixture_engine():
    """Create test database engine (SQLite in-memory)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create test database session."""
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(name="mock_chat_service")
def fixture_mock_chat_service():
    """Create a mock ChatService."""
    mock = MagicMock(spec=ChatService)
    return mock


@pytest.fixture(name="mock_doc_service")
def fixture_mock_doc_service():
    """Create a mock DocumentService."""
    mock = MagicMock(spec=DocumentService)
    return mock


@pytest.fixture(name="client")
def fixture_client(
    session: Session,
    mock_chat_service: MagicMock,
    mock_doc_service: MagicMock,
):
    """Create test client with overridden dependencies."""

    def override_get_db_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = lambda: "test@market.com"
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    app.dependency_overrides[get_document_service] = lambda: mock_doc_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="unauth_client")
def fixture_unauth_client(session: Session):
    """Create test client WITHOUT auth override (for JWT protection tests)."""

    def override_get_db_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    # Do NOT override get_current_user - requests should be rejected
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# JWT Protection Tests
# ---------------------------------------------------------------------------


class TestChatAuthProtection:
    """All chat endpoints require JWT authentication."""

    def test_chat_requires_auth(self, unauth_client: TestClient):
        """POST /chat/{id} without token returns 401."""
        response = unauth_client.post(
            "/api/v1/chat/1",
            json={"message": "Hello"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_requires_auth(self, unauth_client: TestClient):
        """POST /chat/{id}/documents without token returns 401."""
        response = unauth_client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("test.txt", b"content", "text/plain")},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_documents_requires_auth(self, unauth_client: TestClient):
        """GET /chat/{id}/documents without token returns 401."""
        response = unauth_client.get("/api/v1/chat/1/documents")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# POST /api/v1/chat/{instrument_id} - Streaming Chat
# ---------------------------------------------------------------------------


class TestChatStream:
    """Tests for the SSE streaming chat endpoint."""

    def test_chat_returns_sse_stream(
        self,
        client: TestClient,
        mock_chat_service: MagicMock,
    ):
        """Should return streaming response with SSE events."""

        async def fake_stream(instrument_id, message, history):
            for token in ["Hello", " world", "!"]:
                yield token

        mock_chat_service.chat_stream = fake_stream

        response = client.post(
            "/api/v1/chat/1",
            json={"message": "What is the trend?"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"].startswith("text/event-stream")
        assert response.headers["cache-control"] == "no-cache"

        # Parse SSE events
        events = [
            line
            for line in response.text.strip().split("\n")
            if line.startswith("data: ")
        ]
        # Should have 3 token events + 1 [DONE]
        assert len(events) == 4
        assert json.loads(events[0].removeprefix("data: ")) == "Hello"
        assert json.loads(events[1].removeprefix("data: ")) == " world"
        assert json.loads(events[2].removeprefix("data: ")) == "!"
        assert events[3] == "data: [DONE]"

    def test_chat_with_history(
        self,
        client: TestClient,
        mock_chat_service: MagicMock,
    ):
        """Should pass conversation history to the service."""
        received_args = {}

        async def capture_stream(instrument_id, message, history):
            received_args["instrument_id"] = instrument_id
            received_args["message"] = message
            received_args["history"] = history
            yield "ok"

        mock_chat_service.chat_stream = capture_stream

        response = client.post(
            "/api/v1/chat/42",
            json={
                "message": "Follow-up question",
                "history": [
                    {"role": "user", "content": "Previous question"},
                    {"role": "assistant", "content": "Previous answer"},
                ],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert received_args["instrument_id"] == 42
        assert received_args["message"] == "Follow-up question"
        assert len(received_args["history"]) == 2
        assert received_args["history"][0]["role"] == "user"

    def test_chat_handles_stream_error(
        self,
        client: TestClient,
        mock_chat_service: MagicMock,
    ):
        """Should return error event when stream raises exception."""

        async def error_stream(instrument_id, message, history):
            raise RuntimeError("Ollama is down")
            yield  # make it an async generator  # noqa: RUF027

        mock_chat_service.chat_stream = error_stream

        response = client.post(
            "/api/v1/chat/1",
            json={"message": "Will fail"},
        )

        assert response.status_code == status.HTTP_200_OK  # SSE always 200
        events = [
            line
            for line in response.text.strip().split("\n")
            if line.startswith("data: ")
        ]
        # Should have error event + DONE
        assert any("Error:" in e for e in events)
        assert events[-1] == "data: [DONE]"

    def test_chat_empty_message_rejected(self, client: TestClient):
        """Should return 422 when message is empty."""
        response = client.post(
            "/api/v1/chat/1",
            json={"message": ""},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_message_too_long_rejected(self, client: TestClient):
        """Should return 422 when message exceeds max length."""
        response = client.post(
            "/api/v1/chat/1",
            json={"message": "x" * 2001},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# POST /api/v1/chat/{instrument_id}/documents - Upload
# ---------------------------------------------------------------------------


class TestDocumentUpload:
    """Tests for the document upload endpoint."""

    def test_upload_text_file(
        self,
        client: TestClient,
        mock_doc_service: MagicMock,
    ):
        """Should upload .txt file and return chunk count."""
        mock_doc_service.ingest_document = AsyncMock(return_value=3)

        response = client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("notes.txt", b"Some text content", "text/plain")},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["filename"] == "notes.txt"
        assert data["chunks_stored"] == 3
        assert data["instrument_id"] == 1

        mock_doc_service.ingest_document.assert_awaited_once_with(
            1, "notes.txt", b"Some text content"
        )

    def test_upload_markdown_file(
        self,
        client: TestClient,
        mock_doc_service: MagicMock,
    ):
        """Should accept .md files."""
        mock_doc_service.ingest_document = AsyncMock(return_value=5)

        response = client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("README.md", b"# Title\nContent", "text/markdown")},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chunks_stored"] == 5

    def test_upload_pdf_file(
        self,
        client: TestClient,
        mock_doc_service: MagicMock,
    ):
        """Should accept .pdf files."""
        mock_doc_service.ingest_document = AsyncMock(return_value=10)

        response = client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("report.pdf", b"fake-pdf-bytes", "application/pdf")},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["chunks_stored"] == 10

    def test_upload_unsupported_extension_rejected(
        self,
        client: TestClient,
    ):
        """Should return 422 for unsupported file types."""
        response = client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("image.png", b"png-data", "image/png")},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upload_too_large_rejected(
        self,
        client: TestClient,
    ):
        """Should return 422 when file exceeds 10 MB."""
        big_content = b"x" * (10 * 1024 * 1024 + 1)

        response = client.post(
            "/api/v1/chat/1/documents",
            files={"file": ("big.txt", big_content, "text/plain")},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# GET /api/v1/chat/{instrument_id}/documents - List
# ---------------------------------------------------------------------------


class TestListDocuments:
    """Tests for the document listing endpoint."""

    def test_list_documents_empty(
        self,
        client: TestClient,
        mock_doc_service: MagicMock,
    ):
        """Should return empty list when no documents uploaded."""
        mock_doc_service.list_documents.return_value = []

        response = client.get("/api/v1/chat/1/documents")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["instrument_id"] == 1
        assert data["documents"] == []

    def test_list_documents_with_results(
        self,
        client: TestClient,
        mock_doc_service: MagicMock,
    ):
        """Should return uploaded documents with chunk counts."""
        mock_doc_service.list_documents.return_value = [
            {"filename": "report.pdf", "chunk_count": 12},
            {"filename": "notes.txt", "chunk_count": 3},
        ]

        response = client.get("/api/v1/chat/42/documents")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["instrument_id"] == 42
        assert len(data["documents"]) == 2
        assert data["documents"][0]["filename"] == "report.pdf"
        assert data["documents"][0]["chunk_count"] == 12
        assert data["documents"][1]["filename"] == "notes.txt"


# ---------------------------------------------------------------------------
# Router Registration Tests
# ---------------------------------------------------------------------------


class TestChatRouterRegistration:
    """Tests that the chat router is properly registered in the app."""

    def test_chat_routes_registered(self):
        """All 3 chat routes should be registered in the app."""
        routes = [r.path for r in app.routes if hasattr(r, "path")]

        assert "/api/v1/chat/{instrument_id}" in routes
        assert "/api/v1/chat/{instrument_id}/documents" in routes

    def test_chat_routes_have_chat_tag(self):
        """Chat routes should be tagged with 'chat'."""
        for route in app.routes:
            if hasattr(route, "path") and "/api/v1/chat/" in route.path:
                assert "chat" in getattr(route, "tags", [])
