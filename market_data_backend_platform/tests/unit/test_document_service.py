"""Tests for DocumentService — RAG document ingestion and retrieval.

Unit tests verify:
- Text extraction from .txt, .md, and .pdf files
- Text chunking with overlap
- Document ingestion pipeline (parse → chunk → embed → store)
- Relevant chunk retrieval from ChromaDB
- Document listing with chunk counts
- Edge cases (empty docs, missing collections, unsupported types)

All external dependencies (Ollama, ChromaDB) are mocked.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chromadb.errors import NotFoundError as ChromaNotFoundError

from market_data_backend_platform.chat.services.document_service import (
    ALLOWED_EXTENSIONS,
    DocumentService,
    _chunk_text,
    _extract_text,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="mock_ollama")
def fixture_mock_ollama():
    """Create a mock OllamaClient with embed support."""
    mock = MagicMock()
    mock.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])
    return mock


@pytest.fixture(name="mock_chromadb")
def fixture_mock_chromadb():
    """Create a mock ChromaDB client."""
    return MagicMock()


@pytest.fixture(name="service")
def fixture_service(mock_ollama, mock_chromadb):
    """Create a DocumentService with mocked dependencies."""
    return DocumentService(
        ollama_client=mock_ollama,
        embedding_model="nomic-embed-text",
        chromadb_client=mock_chromadb,
    )


# ---------------------------------------------------------------------------
# ALLOWED_EXTENSIONS
# ---------------------------------------------------------------------------


class TestAllowedExtensions:
    """Verify the set of supported file extensions."""

    def test_pdf_allowed(self):
        assert ".pdf" in ALLOWED_EXTENSIONS

    def test_md_allowed(self):
        assert ".md" in ALLOWED_EXTENSIONS

    def test_txt_allowed(self):
        assert ".txt" in ALLOWED_EXTENSIONS

    def test_only_three_extensions(self):
        assert len(ALLOWED_EXTENSIONS) == 3


# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------


class TestExtractText:
    """Tests for the _extract_text helper."""

    def test_extracts_txt(self):
        """Should decode UTF-8 bytes for .txt files."""
        content = "Hello, world!".encode("utf-8")
        result = _extract_text("notes.txt", content)
        assert result == "Hello, world!"

    def test_extracts_md(self):
        """Should decode UTF-8 bytes for .md files."""
        content = "# Title\n\nSome content".encode("utf-8")
        result = _extract_text("README.md", content)
        assert "# Title" in result
        assert "Some content" in result

    def test_extracts_txt_case_insensitive(self):
        """Should handle uppercase extensions."""
        content = "data".encode("utf-8")
        result = _extract_text("DATA.TXT", content)
        assert result == "data"

    def test_extracts_md_case_insensitive(self):
        """Should handle uppercase .MD extension."""
        content = "# Title".encode("utf-8")
        result = _extract_text("FILE.MD", content)
        assert result == "# Title"

    def test_handles_non_utf8_gracefully(self):
        """Should replace invalid UTF-8 bytes instead of crashing."""
        content = b"\xff\xfe Hello"
        result = _extract_text("data.txt", content)
        assert "Hello" in result

    def test_pdf_extraction(self):
        """Should extract text from PDF bytes using PyMuPDF."""
        # Create a minimal PDF using fitz
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF content")
        pdf_bytes = doc.tobytes()
        doc.close()

        result = _extract_text("report.pdf", pdf_bytes)
        assert "Test PDF content" in result

    def test_unsupported_extension_raises(self):
        """Should raise ValueError for unsupported file types."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            _extract_text("image.png", b"data")


# ---------------------------------------------------------------------------
# _chunk_text
# ---------------------------------------------------------------------------


class TestChunkText:
    """Tests for the _chunk_text helper."""

    def test_short_text_single_chunk(self):
        """Text shorter than chunk_size should produce one chunk."""
        result = _chunk_text("Short text", chunk_size=500)
        assert len(result) == 1
        assert result[0] == "Short text"

    def test_long_text_multiple_chunks(self):
        """Long text should be split into multiple overlapping chunks."""
        text = "A" * 1000
        result = _chunk_text(text, chunk_size=500, overlap=50)
        assert len(result) > 1

    def test_overlap_creates_shared_content(self):
        """Adjacent chunks should share overlapping characters."""
        text = "0123456789" * 20  # 200 chars
        result = _chunk_text(text, chunk_size=100, overlap=20)

        # End of first chunk should overlap with start of second
        if len(result) >= 2:
            tail_of_first = result[0][-20:]
            head_of_second = result[1][:20]
            assert tail_of_first == head_of_second

    def test_empty_text_returns_empty_list(self):
        """Empty text should produce no chunks."""
        result = _chunk_text("")
        assert result == []

    def test_whitespace_only_chunks_are_skipped(self):
        """Chunks that are only whitespace should be excluded."""
        text = "Hello" + " " * 600 + "World"
        result = _chunk_text(text, chunk_size=500, overlap=50)
        for chunk in result:
            assert chunk.strip() != ""

    def test_default_parameters(self):
        """Should work with default chunk_size=500 and overlap=50."""
        text = "x" * 1200
        result = _chunk_text(text)
        assert len(result) >= 2


# ---------------------------------------------------------------------------
# DocumentService.ingest_document
# ---------------------------------------------------------------------------


class TestIngestDocument:
    """Tests for DocumentService.ingest_document()."""

    @pytest.mark.asyncio
    async def test_ingests_txt_and_returns_chunk_count(self, service, mock_chromadb, mock_ollama):
        """Should parse, chunk, embed, and store a text file."""
        mock_collection = MagicMock()
        mock_chromadb.get_or_create_collection.return_value = mock_collection

        content = ("Some analysis text. " * 30).encode("utf-8")  # ~600 chars

        result = await service.ingest_document(1, "notes.txt", content)

        assert result > 0
        assert mock_collection.upsert.call_count == result
        assert mock_ollama.embed.await_count == result

    @pytest.mark.asyncio
    async def test_stores_with_correct_metadata(self, service, mock_chromadb, mock_ollama):
        """Each chunk should be stored with filename and chunk_index metadata."""
        mock_collection = MagicMock()
        mock_chromadb.get_or_create_collection.return_value = mock_collection

        content = b"Short document content"

        await service.ingest_document(5, "report.txt", content)

        # Verify the upsert was called with correct args
        call_args = mock_collection.upsert.call_args
        assert call_args is not None
        kwargs = call_args[1] if call_args[1] else {}
        # If called with positional args, check those
        if not kwargs:
            kwargs_from_call = call_args.kwargs
        else:
            kwargs_from_call = kwargs

        assert kwargs_from_call["metadatas"][0]["filename"] == "report.txt"
        assert kwargs_from_call["metadatas"][0]["chunk_index"] == 0

    @pytest.mark.asyncio
    async def test_uses_correct_collection_name(self, service, mock_chromadb, mock_ollama):
        """Collection name should follow instrument_{id}_docs pattern."""
        mock_collection = MagicMock()
        mock_chromadb.get_or_create_collection.return_value = mock_collection

        await service.ingest_document(42, "notes.txt", b"some text")

        mock_chromadb.get_or_create_collection.assert_called_once_with(
            name="instrument_42_docs"
        )

    @pytest.mark.asyncio
    async def test_generates_embeddings_with_correct_model(self, service, mock_chromadb, mock_ollama):
        """Should use the configured embedding model for all chunks."""
        mock_chromadb.get_or_create_collection.return_value = MagicMock()

        await service.ingest_document(1, "notes.txt", b"text content")

        for call in mock_ollama.embed.await_args_list:
            assert call[0][0] == "nomic-embed-text"

    @pytest.mark.asyncio
    async def test_empty_document_returns_zero(self, service):
        """Should return 0 chunks for empty/whitespace-only files."""
        result = await service.ingest_document(1, "empty.txt", b"   \n  \t  ")
        assert result == 0

    @pytest.mark.asyncio
    async def test_doc_id_format(self, service, mock_chromadb, mock_ollama):
        """Document IDs should follow filename__chunk_N pattern."""
        mock_collection = MagicMock()
        mock_chromadb.get_or_create_collection.return_value = mock_collection

        await service.ingest_document(1, "report.txt", b"content")

        call_args = mock_collection.upsert.call_args
        kwargs_from_call = call_args.kwargs if call_args.kwargs else call_args[1]
        assert kwargs_from_call["ids"][0] == "report.txt__chunk_0"


# ---------------------------------------------------------------------------
# DocumentService.query_relevant_chunks
# ---------------------------------------------------------------------------


class TestQueryRelevantChunks:
    """Tests for DocumentService.query_relevant_chunks()."""

    @pytest.mark.asyncio
    async def test_returns_relevant_documents(self, service, mock_chromadb, mock_ollama):
        """Should return documents from ChromaDB query."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [["Revenue was $100M", "Q4 increased"]]
        }
        mock_chromadb.get_collection.return_value = mock_collection
        mock_ollama.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

        result = await service.query_relevant_chunks(1, "What is the revenue?", top_k=5)

        assert result == ["Revenue was $100M", "Q4 increased"]

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_collection_value_error(self, service, mock_chromadb):
        """Should return empty list if collection raises ValueError."""
        mock_chromadb.get_collection.side_effect = ValueError("Collection not found")

        result = await service.query_relevant_chunks(1, "query")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_collection_chroma_error(self, service, mock_chromadb):
        """Should return empty list if collection raises ChromaDB NotFoundError."""
        mock_chromadb.get_collection.side_effect = ChromaNotFoundError(
            "Collection [instrument_1_docs] does not exist"
        )

        result = await service.query_relevant_chunks(1, "query")
        assert result == []

    @pytest.mark.asyncio
    async def test_queries_with_embedding(self, service, mock_chromadb, mock_ollama):
        """Should embed the query and pass to ChromaDB."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_collection.query.return_value = {"documents": [[]]}
        mock_chromadb.get_collection.return_value = mock_collection
        mock_ollama.embed = AsyncMock(return_value=[0.5, 0.6, 0.7])

        await service.query_relevant_chunks(1, "test query", top_k=3)

        mock_ollama.embed.assert_awaited_once_with("nomic-embed-text", "test query")
        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.5, 0.6, 0.7]],
            n_results=3,
        )

    @pytest.mark.asyncio
    async def test_limits_results_to_collection_count(self, service, mock_chromadb, mock_ollama):
        """Should request min(top_k, collection.count()) results."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 2  # Only 2 docs
        mock_collection.query.return_value = {"documents": [["a", "b"]]}
        mock_chromadb.get_collection.return_value = mock_collection
        mock_ollama.embed = AsyncMock(return_value=[0.1])

        await service.query_relevant_chunks(1, "query", top_k=10)

        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1]],
            n_results=2,  # min(10, 2)
        )

    @pytest.mark.asyncio
    async def test_uses_correct_collection_name(self, service, mock_chromadb, mock_ollama):
        """Should look up the instrument-specific collection."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 1
        mock_collection.query.return_value = {"documents": [["data"]]}
        mock_chromadb.get_collection.return_value = mock_collection
        mock_ollama.embed = AsyncMock(return_value=[0.1])

        await service.query_relevant_chunks(42, "query")

        mock_chromadb.get_collection.assert_called_once_with(name="instrument_42_docs")


# ---------------------------------------------------------------------------
# DocumentService.list_documents
# ---------------------------------------------------------------------------


class TestListDocuments:
    """Tests for DocumentService.list_documents()."""

    def test_returns_empty_when_no_collection_value_error(self, service, mock_chromadb):
        """Should return empty list when collection raises ValueError."""
        mock_chromadb.get_collection.side_effect = ValueError("Not found")

        result = service.list_documents(1)
        assert result == []

    def test_returns_empty_when_no_collection_chroma_error(self, service, mock_chromadb):
        """Should return empty list when collection raises ChromaDB NotFoundError."""
        mock_chromadb.get_collection.side_effect = ChromaNotFoundError(
            "Collection [instrument_1_docs] does not exist"
        )

        result = service.list_documents(1)
        assert result == []

    def test_returns_documents_with_chunk_counts(self, service, mock_chromadb):
        """Should aggregate chunk counts per filename."""
        mock_collection = MagicMock()
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "report.pdf", "chunk_index": 0},
                {"filename": "report.pdf", "chunk_index": 1},
                {"filename": "report.pdf", "chunk_index": 2},
                {"filename": "notes.txt", "chunk_index": 0},
            ]
        }
        mock_chromadb.get_collection.return_value = mock_collection

        result = service.list_documents(1)

        assert len(result) == 2
        # Find report.pdf
        report = next(d for d in result if d["filename"] == "report.pdf")
        notes = next(d for d in result if d["filename"] == "notes.txt")
        assert report["chunk_count"] == 3
        assert notes["chunk_count"] == 1

    def test_handles_empty_metadatas(self, service, mock_chromadb):
        """Should return empty list when collection has no documents."""
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"metadatas": []}
        mock_chromadb.get_collection.return_value = mock_collection

        result = service.list_documents(1)
        assert result == []

    def test_uses_correct_collection_name(self, service, mock_chromadb):
        """Should look up instrument-specific collection."""
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"metadatas": []}
        mock_chromadb.get_collection.return_value = mock_collection

        service.list_documents(99)

        mock_chromadb.get_collection.assert_called_once_with(name="instrument_99_docs")

    def test_collection_name_format(self, service):
        """Collection name should follow instrument_{id}_docs pattern."""
        assert service._collection_name(1) == "instrument_1_docs"
        assert service._collection_name(42) == "instrument_42_docs"
