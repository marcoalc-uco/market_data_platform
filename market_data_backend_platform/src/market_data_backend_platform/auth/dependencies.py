"""FastAPI authentication dependencies.

Provides the ``get_current_user`` dependency that validates the Bearer JWT
token from the Authorization header and returns the subject (email).
Use ``CurrentUserDep`` as a type alias in route signatures for convenience.
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from market_data_backend_platform.auth.token import decode_access_token

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(token: Annotated[str, Depends(_oauth2_scheme)]) -> str:
    """Decode JWT and return the subject (email).

    Args:
        token: Bearer token from Authorization header.

    Returns:
        Subject (email) from the token payload.

    Raises:
        HTTPException: 401 if token is missing, invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
        return subject
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc


CurrentUserDep = Annotated[str, Depends(get_current_user)]
