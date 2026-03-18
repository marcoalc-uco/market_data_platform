"""Ollama HTTP client for chat completions and embeddings.

Communicates with a local Ollama instance for LLM inference
and text embedding generation used in RAG pipelines.

Example::

    client = OllamaClient(base_url="http://localhost:11434")
    async for token in client.chat_stream("qwen2.5-coder:3b", messages):
        print(token, end="")
"""

import json
from collections.abc import AsyncIterator

import httpx

from market_data_backend_platform.core import ExternalAPIError, get_logger

logger = get_logger(__name__)


class OllamaClient:
    """HTTP client for the Ollama REST API.

    Attributes:
        base_url: Ollama server URL (e.g. http://localhost:11434).
    """

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    async def chat_stream(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> AsyncIterator[str]:
        """Stream chat completion tokens from Ollama.

        Args:
            model: Ollama model name (e.g. "qwen2.5-coder:3b").
            messages: List of message dicts with "role" and "content" keys.

        Yields:
            Individual text tokens as they are generated.

        Raises:
            ExternalAPIError: If Ollama is unreachable or returns an error.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }

        # Generous timeouts: connect fast, but allow slow LLM generation on CPU
        timeout = httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=10.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        raise ExternalAPIError(
                            f"Ollama chat error: {response.status_code}",
                            status_code=response.status_code,
                            details={"body": body.decode()},
                        )
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
        except httpx.ConnectError as e:
            logger.error("ollama_connection_error", error=str(e))
            raise ExternalAPIError(
                "Cannot connect to Ollama. Is it running?",
                details={"url": self.base_url, "error": str(e)},
            ) from e
        except httpx.ReadTimeout as e:
            logger.error("ollama_read_timeout", error=repr(e), url=url)
            raise ExternalAPIError(
                "Ollama response timed out. "
                "The model may be loading or the prompt is too large.",
                details={"url": url, "error": repr(e)},
            ) from e
        except httpx.HTTPError as e:
            logger.error("ollama_http_error", error=repr(e), type=type(e).__name__)
            raise ExternalAPIError(
                f"Ollama request failed: {type(e).__name__}: {e}",
                details={"error": repr(e)},
            ) from e

    async def embed(self, model: str, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            model: Ollama embedding model name (e.g. "nomic-embed-text").
            text: Input text to embed.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            ExternalAPIError: If Ollama is unreachable or returns an error.
        """
        url = f"{self.base_url}/api/embed"
        payload = {"model": model, "input": text}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    raise ExternalAPIError(
                        f"Ollama embed error: {response.status_code}",
                        status_code=response.status_code,
                        details={"body": response.text},
                    )
                data = response.json()
                embeddings = data.get("embeddings", [])
                if not embeddings:
                    raise ExternalAPIError(
                        "Ollama returned empty embeddings",
                        details={"response": data},
                    )
                return embeddings[0]  # type: ignore[no-any-return]
        except httpx.ConnectError as e:
            logger.error("ollama_embed_connection_error", error=str(e))
            raise ExternalAPIError(
                "Cannot connect to Ollama for embeddings.",
                details={"url": self.base_url, "error": str(e)},
            ) from e
        except httpx.HTTPError as e:
            logger.error("ollama_embed_http_error", error=str(e))
            raise ExternalAPIError(
                f"Ollama embed request failed: {e}",
                details={"error": str(e)},
            ) from e
