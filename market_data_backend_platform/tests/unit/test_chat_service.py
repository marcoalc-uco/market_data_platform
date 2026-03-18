"""Tests for ChatService orchestration logic.

Unit tests verify that ChatService correctly:
- Fetches instrument metadata and raises NotFoundError if missing
- Retrieves and formats OHLCV price data for the LLM context
- Queries relevant document chunks via RAG
- Assembles the system prompt and conversation messages
- Streams tokens from the Ollama client

All external dependencies (repos, Ollama, DocumentService) are mocked.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from market_data_backend_platform.chat.services.chat_service import (
    ChatService,
    _format_price_table,
)
from market_data_backend_platform.core import NotFoundError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="mock_ollama")
def fixture_mock_ollama():
    """Create a mock OllamaClient."""
    mock = MagicMock()
    return mock


@pytest.fixture(name="mock_price_repo")
def fixture_mock_price_repo():
    """Create a mock MarketPriceRepository."""
    return MagicMock()


@pytest.fixture(name="mock_instrument_repo")
def fixture_mock_instrument_repo():
    """Create a mock InstrumentRepository."""
    return MagicMock()


@pytest.fixture(name="mock_doc_service")
def fixture_mock_doc_service():
    """Create a mock DocumentService."""
    mock = MagicMock()
    mock.query_relevant_chunks = AsyncMock(return_value=[])
    return mock


@pytest.fixture(name="service")
def fixture_service(
    mock_ollama, mock_price_repo, mock_instrument_repo, mock_doc_service
):
    """Create a ChatService with all mocked dependencies."""
    return ChatService(
        ollama_client=mock_ollama,
        chat_model="test-model",
        price_repo=mock_price_repo,
        instrument_repo=mock_instrument_repo,
        document_service=mock_doc_service,
        max_price_rows=10,
        max_doc_chunks=3,
    )


def _make_instrument(name="Apple Inc.", symbol="AAPL"):
    """Create a mock instrument object."""
    inst = MagicMock()
    inst.name = name
    inst.symbol = symbol
    return inst


def _make_price(timestamp_str, open_v, high, low, close, volume):
    """Create a mock price object with OHLCV data."""
    p = MagicMock()
    p.timestamp = datetime.fromisoformat(timestamp_str)
    p.open = Decimal(str(open_v))
    p.high = Decimal(str(high))
    p.low = Decimal(str(low))
    p.close = Decimal(str(close))
    p.volume = volume
    return p


# ---------------------------------------------------------------------------
# _format_price_table
# ---------------------------------------------------------------------------


class TestFormatPriceTable:
    """Tests for the price table formatting helper."""

    def test_empty_list_returns_no_data_message(self):
        """Should return 'No price data available.' for empty list."""
        result = _format_price_table([])
        assert result == "No price data available."

    def test_formats_single_row(self):
        """Should format a single OHLCV row as a table line."""
        prices = [
            _make_price("2025-01-15 10:00:00", 150.0, 155.0, 149.0, 153.0, 1000000)
        ]
        result = _format_price_table(prices)

        assert "Date" in result
        assert "Open" in result
        assert "High" in result
        assert "2025-01-15 10:00" in result
        assert "150.0000" in result
        assert "155.0000" in result
        assert "1000000" in result

    def test_formats_multiple_rows(self):
        """Should format multiple OHLCV rows."""
        prices = [
            _make_price("2025-01-15 10:00:00", 150.0, 155.0, 149.0, 153.0, 1000000),
            _make_price("2025-01-16 10:00:00", 153.0, 158.0, 152.0, 157.0, 1200000),
        ]
        result = _format_price_table(prices)
        lines = result.split("\n")

        # Header + separator + 2 data rows
        assert len(lines) == 4

    def test_table_has_header_and_separator(self):
        """Should include header row and dashed separator."""
        prices = [_make_price("2025-01-15 10:00:00", 100.0, 101.0, 99.0, 100.5, 500)]
        result = _format_price_table(prices)
        lines = result.split("\n")

        assert "Date" in lines[0]
        assert lines[1].startswith("-")


# ---------------------------------------------------------------------------
# ChatService.chat_stream
# ---------------------------------------------------------------------------


class TestChatServiceStream:
    """Tests for ChatService.chat_stream() orchestration."""

    @pytest.mark.asyncio
    async def test_raises_not_found_when_instrument_missing(
        self, service, mock_instrument_repo
    ):
        """Should raise NotFoundError if instrument does not exist."""
        mock_instrument_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Instrument not found"):
            async for _ in service.chat_stream(999, "question", []):
                pass

    @pytest.mark.asyncio
    async def test_fetches_instrument_by_id(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Should call instrument_repo.get_by_id with the given ID."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        async def fake_stream(model, messages):
            yield "ok"

        mock_ollama.chat_stream = fake_stream

        async for _ in service.chat_stream(42, "test", []):
            pass

        mock_instrument_repo.get_by_id.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_fetches_prices_with_limit(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Should fetch prices with max_price_rows as limit."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        async def fake_stream(model, messages):
            yield "ok"

        mock_ollama.chat_stream = fake_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        mock_price_repo.get_by_instrument.assert_called_once_with(1, limit=10)

    @pytest.mark.asyncio
    async def test_queries_document_chunks(
        self,
        service,
        mock_instrument_repo,
        mock_price_repo,
        mock_doc_service,
        mock_ollama,
    ):
        """Should query relevant document chunks via DocumentService."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        async def fake_stream(model, messages):
            yield "ok"

        mock_ollama.chat_stream = fake_stream

        async for _ in service.chat_stream(1, "What is the trend?", []):
            pass

        mock_doc_service.query_relevant_chunks.assert_awaited_once_with(
            1, "What is the trend?", top_k=3
        )

    @pytest.mark.asyncio
    async def test_system_prompt_contains_instrument_info(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """System prompt should include instrument name and symbol."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument(
            "Apple Inc.", "AAPL"
        )
        mock_price_repo.get_by_instrument.return_value = []

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        system_msg = captured_messages[0]
        assert system_msg["role"] == "system"
        assert "Apple Inc." in system_msg["content"]
        assert "AAPL" in system_msg["content"]

    @pytest.mark.asyncio
    async def test_system_prompt_contains_price_data(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """System prompt should include formatted price table."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = [
            _make_price("2025-01-15 10:00:00", 150.0, 155.0, 149.0, 153.0, 1000000),
        ]

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        system_content = captured_messages[0]["content"]
        assert "150.0000" in system_content
        assert "2025-01-15" in system_content

    @pytest.mark.asyncio
    async def test_system_prompt_contains_doc_chunks(
        self,
        service,
        mock_instrument_repo,
        mock_price_repo,
        mock_doc_service,
        mock_ollama,
    ):
        """System prompt should include relevant document chunks."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []
        mock_doc_service.query_relevant_chunks = AsyncMock(
            return_value=["Revenue was $100M", "Q4 earnings increased"]
        )

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        system_content = captured_messages[0]["content"]
        assert "Revenue was $100M" in system_content
        assert "Q4 earnings increased" in system_content
        assert "[Chunk 1]" in system_content
        assert "[Chunk 2]" in system_content

    @pytest.mark.asyncio
    async def test_no_docs_shows_placeholder(
        self,
        service,
        mock_instrument_repo,
        mock_price_repo,
        mock_doc_service,
        mock_ollama,
    ):
        """System prompt should show placeholder when no documents exist."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []
        mock_doc_service.query_relevant_chunks = AsyncMock(return_value=[])

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        system_content = captured_messages[0]["content"]
        assert "No documents uploaded" in system_content

    @pytest.mark.asyncio
    async def test_includes_history_and_user_message(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Messages should include system + history + current user message."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        history = [
            {"role": "user", "content": "Previous Q"},
            {"role": "assistant", "content": "Previous A"},
        ]

        async for _ in service.chat_stream(1, "Current Q", history):
            pass

        # system + 2 history + user message = 4
        assert len(captured_messages) == 4
        assert captured_messages[0]["role"] == "system"
        assert captured_messages[1]["role"] == "user"
        assert captured_messages[1]["content"] == "Previous Q"
        assert captured_messages[2]["role"] == "assistant"
        assert captured_messages[3]["role"] == "user"
        assert captured_messages[3]["content"] == "Current Q"

    @pytest.mark.asyncio
    async def test_uses_configured_model(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Should pass the configured chat_model to Ollama."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        captured_model = []

        async def capture_stream(model, messages):
            captured_model.append(model)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        assert captured_model[0] == "test-model"

    @pytest.mark.asyncio
    async def test_yields_tokens_from_ollama(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Should yield all tokens from the Ollama stream."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        mock_price_repo.get_by_instrument.return_value = []

        async def fake_stream(model, messages):
            for token in ["The ", "trend ", "is ", "bullish."]:
                yield token

        mock_ollama.chat_stream = fake_stream

        tokens = []
        async for token in service.chat_stream(1, "What is the trend?", []):
            tokens.append(token)

        assert tokens == ["The ", "trend ", "is ", "bullish."]

    @pytest.mark.asyncio
    async def test_prices_reversed_for_chronological_order(
        self, service, mock_instrument_repo, mock_price_repo, mock_ollama
    ):
        """Prices from repo (DESC) should be reversed for chronological display."""
        mock_instrument_repo.get_by_id.return_value = _make_instrument()
        # Simulate repo returning DESC order
        mock_price_repo.get_by_instrument.return_value = [
            _make_price("2025-01-16 10:00:00", 153.0, 158.0, 152.0, 157.0, 1200000),
            _make_price("2025-01-15 10:00:00", 150.0, 155.0, 149.0, 153.0, 1000000),
        ]

        captured_messages = []

        async def capture_stream(model, messages):
            captured_messages.extend(messages)
            yield "ok"

        mock_ollama.chat_stream = capture_stream

        async for _ in service.chat_stream(1, "test", []):
            pass

        system_content = captured_messages[0]["content"]
        # 2025-01-15 should appear before 2025-01-16 (chronological)
        pos_15 = system_content.index("2025-01-15")
        pos_16 = system_content.index("2025-01-16")
        assert pos_15 < pos_16
