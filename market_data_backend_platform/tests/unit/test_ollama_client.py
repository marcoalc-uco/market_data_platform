"""Tests for OllamaClient HTTP interactions.

Unit tests use mocked httpx responses to test the Ollama client
without requiring a running Ollama instance.

Covers:
    - chat_stream: successful streaming, HTTP errors, connection errors
    - embed: successful embedding, HTTP errors, empty response, connection errors
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from market_data_backend_platform.chat.clients.ollama import OllamaClient
from market_data_backend_platform.core import ExternalAPIError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="client")
def fixture_client():
    """Create an OllamaClient pointed at a fake base URL."""
    return OllamaClient(base_url="http://test-ollama:11434")


# ---------------------------------------------------------------------------
# chat_stream
# ---------------------------------------------------------------------------


class TestChatStream:
    """Tests for OllamaClient.chat_stream()."""

    @pytest.mark.asyncio
    async def test_yields_content_tokens(self, client):
        """Should yield each content token from the streamed response."""
        lines = [
            json.dumps({"message": {"content": "Hello"}, "done": False}),
            json.dumps({"message": {"content": " world"}, "done": False}),
            json.dumps({"message": {"content": "!"}, "done": True}),
        ]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.aiter_lines = lambda: _async_iter(lines)

        # Patch httpx.AsyncClient to return our mock stream
        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(return_value=mock_stream_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            tokens = []
            async for token in client.chat_stream(
                "test-model", [{"role": "user", "content": "Hi"}]
            ):
                tokens.append(token)

        assert tokens == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_skips_empty_content(self, client):
        """Should skip lines with empty content."""
        lines = [
            json.dumps({"message": {"content": ""}, "done": False}),
            json.dumps({"message": {"content": "data"}, "done": False}),
            json.dumps({"message": {}, "done": True}),
        ]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.aiter_lines = lambda: _async_iter(lines)

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(return_value=mock_stream_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            tokens = []
            async for token in client.chat_stream("m", []):
                tokens.append(token)

        assert tokens == ["data"]

    @pytest.mark.asyncio
    async def test_skips_empty_lines(self, client):
        """Should skip blank lines in the stream."""
        lines = [
            "",
            json.dumps({"message": {"content": "ok"}, "done": True}),
        ]

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.aiter_lines = lambda: _async_iter(lines)

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(return_value=mock_stream_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            tokens = []
            async for token in client.chat_stream("m", []):
                tokens.append(token)

        assert tokens == ["ok"]

    @pytest.mark.asyncio
    async def test_raises_on_non_200_status(self, client):
        """Should raise ExternalAPIError on non-200 response."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.aread = AsyncMock(return_value=b"Internal Server Error")

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(return_value=mock_stream_ctx)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="Ollama chat error: 500"):
                async for _ in client.chat_stream("m", []):
                    pass

    @pytest.mark.asyncio
    async def test_raises_on_connect_error(self, client):
        """Should raise ExternalAPIError when Ollama is unreachable."""
        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="Cannot connect to Ollama"):
                async for _ in client.chat_stream("m", []):
                    pass

    @pytest.mark.asyncio
    async def test_raises_on_read_timeout(self, client):
        """Should raise ExternalAPIError with timeout message on ReadTimeout."""
        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(
            side_effect=httpx.ReadTimeout("Read timed out")
        )

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="timed out"):
                async for _ in client.chat_stream("m", []):
                    pass

    @pytest.mark.asyncio
    async def test_raises_on_generic_http_error(self, client):
        """Should raise ExternalAPIError on generic HTTP errors."""
        mock_http_client = AsyncMock()
        mock_http_client.stream = MagicMock(
            side_effect=httpx.DecodingError("Decoding failed")
        )

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="Ollama request failed"):
                async for _ in client.chat_stream("m", []):
                    pass

    def test_url_construction(self, client):
        """Should build correct Ollama chat URL."""
        assert client.base_url == "http://test-ollama:11434"

    def test_trailing_slash_stripped(self):
        """Should strip trailing slash from base URL."""
        c = OllamaClient(base_url="http://localhost:11434/")
        assert c.base_url == "http://localhost:11434"


# ---------------------------------------------------------------------------
# embed
# ---------------------------------------------------------------------------


class TestEmbed:
    """Tests for OllamaClient.embed()."""

    @pytest.mark.asyncio
    async def test_returns_embedding_vector(self, client):
        """Should return the first embedding from Ollama response."""
        expected = [0.1, 0.2, 0.3, 0.4]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embeddings": [expected]}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            result = await client.embed("nomic-embed-text", "test text")

        assert result == expected

    @pytest.mark.asyncio
    async def test_sends_correct_payload(self, client):
        """Should send model and input text to Ollama embed endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embeddings": [[0.1]]}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            await client.embed("nomic-embed-text", "hello world")

        mock_http_client.post.assert_awaited_once_with(
            "http://test-ollama:11434/api/embed",
            json={"model": "nomic-embed-text", "input": "hello world"},
        )

    @pytest.mark.asyncio
    async def test_raises_on_non_200(self, client):
        """Should raise ExternalAPIError on non-200 response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="Ollama embed error: 400"):
                await client.embed("m", "text")

    @pytest.mark.asyncio
    async def test_raises_on_empty_embeddings(self, client):
        """Should raise ExternalAPIError when Ollama returns no embeddings."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"embeddings": []}

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="empty embeddings"):
                await client.embed("m", "text")

    @pytest.mark.asyncio
    async def test_raises_on_connect_error(self, client):
        """Should raise ExternalAPIError when Ollama is unreachable."""
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(
                ExternalAPIError, match="Cannot connect to Ollama for embeddings"
            ):
                await client.embed("m", "text")

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self, client):
        """Should raise ExternalAPIError on generic HTTP errors."""
        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(
            side_effect=httpx.ReadTimeout("Read timed out")
        )

        mock_client_ctx = AsyncMock()
        mock_client_ctx.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client_ctx):
            with pytest.raises(ExternalAPIError, match="Ollama embed request failed"):
                await client.embed("m", "text")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _async_iter(items):
    """Convert a list to an async iterator."""
    for item in items:
        yield item
