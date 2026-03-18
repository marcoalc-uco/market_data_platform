"""Document ingestion and retrieval service for RAG.

Handles file parsing (PDF, .md, .txt), text chunking,
embedding generation via Ollama, and ChromaDB storage/retrieval.

Example::

    service = DocumentService(ollama_client, "nomic-embed-text", chromadb_client)
    chunks = await service.ingest_document(1, "report.pdf", pdf_bytes)
    results = await service.query_relevant_chunks(1, "What is the revenue?", top_k=5)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from chromadb.errors import NotFoundError as ChromaNotFoundError

from market_data_backend_platform.chat.clients.ollama import OllamaClient
from market_data_backend_platform.core import get_logger

if TYPE_CHECKING:
    import chromadb

logger = get_logger(__name__)

# Supported file extensions for document upload
ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


def _extract_text(filename: str, content: bytes) -> str:
    """Extract plain text from a file based on its extension.

    Args:
        filename: Original filename with extension.
        content: Raw file bytes.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If file type is not supported.
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    if lower.endswith((".md", ".txt")):
        return content.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: Input text to chunk.
        chunk_size: Target size per chunk in characters.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


class DocumentService:
    """Manages document ingestion and retrieval for RAG.

    Attributes:
        ollama_client: Client for generating embeddings.
        embedding_model: Ollama model name for embeddings.
        chromadb_client: ChromaDB persistent client instance.
    """

    def __init__(
        self,
        ollama_client: OllamaClient,
        embedding_model: str,
        chromadb_client: Any,
    ) -> None:
        self.ollama_client = ollama_client
        self.embedding_model = embedding_model
        self.chromadb_client = chromadb_client

    def _collection_name(self, instrument_id: int) -> str:
        return f"instrument_{instrument_id}_docs"

    async def ingest_document(
        self,
        instrument_id: int,
        filename: str,
        content: bytes,
    ) -> int:
        """Parse, chunk, embed, and store a document in ChromaDB.

        Args:
            instrument_id: ID of the instrument this document relates to.
            filename: Original filename (used for metadata and text extraction).
            content: Raw file bytes.

        Returns:
            Number of chunks stored.
        """
        text = _extract_text(filename, content)
        if not text.strip():
            logger.warning("empty_document", filename=filename)
            return 0

        chunks = _chunk_text(text)
        logger.info(
            "document_chunked",
            filename=filename,
            instrument_id=instrument_id,
            chunk_count=len(chunks),
        )

        collection = self.chromadb_client.get_or_create_collection(
            name=self._collection_name(instrument_id),
        )

        # Generate embeddings and store in ChromaDB
        for i, chunk in enumerate(chunks):
            embedding = await self.ollama_client.embed(self.embedding_model, chunk)
            doc_id = f"{filename}__chunk_{i}"
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"filename": filename, "chunk_index": i}],
            )

        logger.info(
            "document_ingested",
            filename=filename,
            instrument_id=instrument_id,
            chunks_stored=len(chunks),
        )
        return len(chunks)

    async def query_relevant_chunks(
        self,
        instrument_id: int,
        query: str,
        top_k: int = 5,
    ) -> list[str]:
        """Retrieve the most relevant document chunks for a query.

        Args:
            instrument_id: ID of the instrument to search documents for.
            query: User query to find relevant context.
            top_k: Maximum number of chunks to return.

        Returns:
            List of relevant text chunks, ordered by similarity.
        """
        collection_name = self._collection_name(instrument_id)

        try:
            collection = self.chromadb_client.get_collection(name=collection_name)
        except (ValueError, ChromaNotFoundError):
            # No documents uploaded yet for this instrument
            return []

        query_embedding = await self.ollama_client.embed(self.embedding_model, query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
        )

        return cast(list[str], results.get("documents", [[]])[0])

    def list_documents(self, instrument_id: int) -> list[dict[str, int | str]]:
        """List all uploaded documents and their chunk counts.

        Args:
            instrument_id: ID of the instrument.

        Returns:
            List of dicts with 'filename' and 'chunk_count' keys.
        """
        collection_name = self._collection_name(instrument_id)

        try:
            collection = self.chromadb_client.get_collection(name=collection_name)
        except (ValueError, ChromaNotFoundError):
            return []

        all_metadata = collection.get(include=["metadatas"])
        metadatas = all_metadata.get("metadatas", [])

        # Count chunks per filename
        file_chunks: dict[str, int] = {}
        for meta in metadatas:
            fname = meta.get("filename", "unknown")
            file_chunks[fname] = file_chunks.get(fname, 0) + 1

        return [
            {"filename": fname, "chunk_count": count}
            for fname, count in file_chunks.items()
        ]
