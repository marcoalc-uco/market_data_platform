"""Chat orchestration service.

Assembles RAG context (OHLCV prices + document chunks) and streams
LLM responses from Ollama for a given instrument.

Example::

    service = ChatService(
        ollama, "qwen2.5-coder:3b", price_repo, instrument_repo, doc_service
    )
    async for token in service.chat_stream(1, "What is the trend?", []):
        print(token, end="")
"""

from collections.abc import AsyncIterator

from market_data_backend_platform.chat.clients.ollama import OllamaClient
from market_data_backend_platform.chat.services.document_service import DocumentService
from market_data_backend_platform.core import NotFoundError, get_logger
from market_data_backend_platform.repositories.instrument import InstrumentRepository
from market_data_backend_platform.repositories.market_price import MarketPriceRepository

logger = get_logger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are a financial data assistant for {name} ({symbol}).
You have access to recent price data and user-uploaded documents.
Use this information to answer questions accurately.
If the data does not contain the answer, say so clearly.

## Recent Price Data ({symbol})
{price_table}

## Relevant Document Context
{doc_context}"""


def _format_price_table(prices: list) -> str:
    """Format OHLCV price records as a text table for the LLM context."""
    if not prices:
        return "No price data available."

    lines = [
        "Date                | Open       | High       | "
        "Low        | Close      | Volume"
    ]
    lines.append("-" * 90)
    for p in prices:
        lines.append(
            f"{p.timestamp.strftime('%Y-%m-%d %H:%M')} | "
            f"{float(p.open):>10.4f} | "
            f"{float(p.high):>10.4f} | "
            f"{float(p.low):>10.4f} | "
            f"{float(p.close):>10.4f} | "
            f"{int(p.volume):>10}"
        )
    return "\n".join(lines)


class ChatService:
    """Orchestrates RAG-augmented chat with Ollama.

    Attributes:
        ollama_client: Client for LLM inference.
        chat_model: Ollama model name for chat.
        price_repo: Repository for fetching OHLCV data.
        instrument_repo: Repository for fetching instrument metadata.
        document_service: Service for querying RAG document chunks.
        max_price_rows: Maximum OHLCV rows to include in context.
        max_doc_chunks: Maximum document chunks to retrieve.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        ollama_client: OllamaClient,
        chat_model: str,
        price_repo: MarketPriceRepository,
        instrument_repo: InstrumentRepository,
        document_service: DocumentService,
        max_price_rows: int = 60,
        max_doc_chunks: int = 5,
    ) -> None:
        self.ollama_client = ollama_client
        self.chat_model = chat_model
        self.price_repo = price_repo
        self.instrument_repo = instrument_repo
        self.document_service = document_service
        self.max_price_rows = max_price_rows
        self.max_doc_chunks = max_doc_chunks

    async def chat_stream(
        self,
        instrument_id: int,
        user_message: str,
        history: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        """Stream a chat response with RAG context.

        Args:
            instrument_id: ID of the instrument being discussed.
            user_message: The user's current question.
            history: Previous conversation messages.

        Yields:
            Individual tokens from the LLM response.

        Raises:
            NotFoundError: If the instrument does not exist.
        """
        # Fetch instrument metadata
        instrument = self.instrument_repo.get_by_id(instrument_id)
        if not instrument:
            raise NotFoundError(
                "Instrument not found",
                details={"instrument_id": instrument_id},
            )

        # Fetch recent OHLCV data (returned DESC, reverse for chronological)
        prices = self.price_repo.get_by_instrument(
            instrument_id, limit=self.max_price_rows
        )
        prices.reverse()
        price_table = _format_price_table(prices)

        # Retrieve relevant document chunks via RAG
        doc_chunks = await self.document_service.query_relevant_chunks(
            instrument_id, user_message, top_k=self.max_doc_chunks
        )
        doc_context = (
            "\n\n".join(
                f"[Chunk {i + 1}]\n{chunk}" for i, chunk in enumerate(doc_chunks)
            )
            if doc_chunks
            else "No documents uploaded for this instrument."
        )

        # Build system prompt
        system_content = SYSTEM_PROMPT_TEMPLATE.format(
            name=instrument.name,
            symbol=instrument.symbol,
            price_table=price_table,
            doc_context=doc_context,
        )

        # Assemble messages for Ollama
        messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        logger.info(
            "chat_request",
            instrument_id=instrument_id,
            model=self.chat_model,
            history_len=len(history),
            price_rows=len(prices),
            doc_chunks=len(doc_chunks),
        )

        async for token in self.ollama_client.chat_stream(self.chat_model, messages):
            yield token
