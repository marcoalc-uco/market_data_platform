"""Unit tests for password hashing utilities.

TDD: these tests are written before the implementation.
"""

import pytest

from market_data_backend_platform.auth.password import hash_password, verify_password


class TestHashPassword:
    def test_returns_string(self) -> None:
        result = hash_password("mysecret")
        assert isinstance(result, str)

    def test_hash_is_not_plain_text(self) -> None:
        result = hash_password("mysecret")
        assert result != "mysecret"

    def test_same_password_produces_different_hashes(self) -> None:
        hash1 = hash_password("mysecret")
        hash2 = hash_password("mysecret")
        assert hash1 != hash2  # bcrypt uses random salt

    def test_hash_starts_with_bcrypt_prefix(self) -> None:
        result = hash_password("mysecret")
        assert result.startswith("$2b$")


class TestVerifyPassword:
    def test_correct_password_returns_true(self) -> None:
        hashed = hash_password("mysecret")
        assert verify_password("mysecret", hashed) is True

    def test_wrong_password_returns_false(self) -> None:
        hashed = hash_password("mysecret")
        assert verify_password("wrong", hashed) is False

    def test_empty_password_returns_false(self) -> None:
        hashed = hash_password("mysecret")
        assert verify_password("", hashed) is False

    def test_case_sensitive(self) -> None:
        hashed = hash_password("MySecret")
        assert verify_password("mysecret", hashed) is False
