"""Unit tests for JWT token utilities.

TDD: these tests are written before the implementation.
"""

import time

import pytest

from market_data_backend_platform.auth.token import (
    create_access_token,
    decode_access_token,
)


class TestCreateAccessToken:
    def test_returns_string(self) -> None:
        token = create_access_token(subject="user@example.com")
        assert isinstance(token, str)

    def test_token_has_three_parts(self) -> None:
        token = create_access_token(subject="user@example.com")
        parts = token.split(".")
        assert len(parts) == 3  # header.payload.signature

    def test_different_subjects_produce_different_tokens(self) -> None:
        token1 = create_access_token(subject="user1@example.com")
        token2 = create_access_token(subject="user2@example.com")
        assert token1 != token2


class TestDecodeAccessToken:
    def test_decode_returns_subject(self) -> None:
        token = create_access_token(subject="user@example.com")
        payload = decode_access_token(token)
        assert payload["sub"] == "user@example.com"

    def test_decode_invalid_token_raises(self) -> None:
        with pytest.raises(Exception):
            decode_access_token("invalid.token.here")

    def test_decode_tampered_token_raises(self) -> None:
        token = create_access_token(subject="user@example.com")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(Exception):
            decode_access_token(tampered)

    def test_expired_token_raises(self) -> None:
        token = create_access_token(subject="user@example.com", expires_minutes=-1)
        with pytest.raises(Exception):
            decode_access_token(token)

    def test_token_contains_expiry(self) -> None:
        token = create_access_token(subject="user@example.com")
        payload = decode_access_token(token)
        assert "exp" in payload
