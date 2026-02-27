"""JWT token creation and decoding utilities.

Implements HS256-signed access tokens using PyJWT.
Token lifetime and secret key are read from application settings.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, cast

import jwt

from market_data_backend_platform.core.config import settings

_ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject (typically user email).
        expires_minutes: Token lifetime in minutes.
            Defaults to settings.access_token_expire_minutes.

    Returns:
        Encoded JWT string.
    """
    minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return str(jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM))


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.InvalidTokenError: If token is invalid, expired, or tampered.
    """
    return cast(
        dict[str, Any], jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
    )
