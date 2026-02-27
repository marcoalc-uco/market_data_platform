"""FastAPI application entry point.

This is the main module that creates and configures the FastAPI application.
It registers routers, middleware, and exception handlers.

Run with:
    uvicorn market_data_backend_platform.main:app --reload
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from market_data_backend_platform.api.routes import auth, health, instruments, prices
from market_data_backend_platform.auth.dependencies import get_current_user
from market_data_backend_platform.core import (
    MarketDataError,
    get_logger,
    settings,
    setup_logging,
)
from market_data_backend_platform.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Runs setup on startup and cleanup on shutdown.

    Yields:
        None: Control is yielded while application is running.
    """
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    logger.info(
        "application_started",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Start scheduler if enabled
    if settings.scheduler_enabled:
        start_scheduler(settings.ingestion_interval_minutes)
        logger.info(
            "scheduler_enabled",
            interval_minutes=settings.ingestion_interval_minutes,
        )

    yield  # Application runs here

    # Shutdown
    if settings.scheduler_enabled:
        shutdown_scheduler()
    logger.info("application_stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for financial market data ingestion and visualization",
    lifespan=lifespan,
)


# Configure CORS middleware
# Allows frontend applications to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
# Health endpoint at /health (public)
app.include_router(health.router)
# Auth endpoints at /api/v1/auth (public)
app.include_router(
    auth.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["auth"],
)
# Instruments CRUD at /api/v1/instruments (protected)
app.include_router(
    instruments.router,
    prefix=f"{settings.api_prefix}/instruments",
    tags=["instruments"],
    dependencies=[Depends(get_current_user)],
)
# Prices query at /api/v1/prices (protected)
app.include_router(
    prices.router,
    prefix=f"{settings.api_prefix}/prices",
    tags=["prices"],
    dependencies=[Depends(get_current_user)],
)


# Global exception handler for MarketDataError
@app.exception_handler(MarketDataError)
async def market_data_error_handler(
    request: Request,
    exc: MarketDataError,
) -> JSONResponse:
    """Handle all MarketDataError exceptions.

    Logs the error with structured context and returns
    a JSON response to the client.

    Args:
        request: The incoming HTTP request.
        exc: The MarketDataError exception that was raised.

    Returns:
        JSONResponse with error details and appropriate status code.
    """
    logger = get_logger(__name__)

    # Log the error with all context
    logger.error(
        exc.message,
        exception_type=type(exc).__name__,
        path=str(request.url.path),
        method=request.method,
        **exc.details,
    )

    # Determine HTTP status code based on exception type
    # Import here to avoid circular imports
    from market_data_backend_platform.core import NotFoundError, ValidationError

    if isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, ValidationError):
        status_code = 422
    else:
        status_code = 500

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.message,
            "type": type(exc).__name__,
            "details": exc.details,
        },
    )
