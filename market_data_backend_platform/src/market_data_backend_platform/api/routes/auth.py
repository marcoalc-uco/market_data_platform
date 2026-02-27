"""Authentication routes.

Provides the OAuth2 password flow login endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from market_data_backend_platform.auth.password import verify_password
from market_data_backend_platform.auth.token import create_access_token
from market_data_backend_platform.core.config import settings
from market_data_backend_platform.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter()


class TokenResponse(BaseModel):
    """OAuth2 token response schema.

    Attributes:
        access_token: Signed JWT string.
        token_type: Always "bearer".
    """

    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    """Authenticate user and return a JWT access token.

    Uses OAuth2 password flow — credentials sent as form data
    (username / password fields). Logs success and failure events
    via structlog; passwords and tokens are never logged.

    Args:
        request: FastAPI request object, used to capture client IP.
        form: OAuth2 form with username and password fields.

    Returns:
        TokenResponse with signed JWT and token type.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    # If behind a reverse proxy, client.host is the proxy IP.
    # X-Forwarded-For would be needed for the real IP in that case.
    client_ip: str = request.client.host if request.client else "unknown"

    admin_email = settings.admin_email
    if form.username != admin_email or not verify_password(
        form.password, settings.admin_password_hash
    ):
        log.warning(
            "auth.login_failed",
            username=form.username,  # email only — never password
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=admin_email)
    log.info(
        "auth.login_success",
        username=admin_email,  # email only — never token value
        client_ip=client_ip,
    )
    return TokenResponse(access_token=token)
