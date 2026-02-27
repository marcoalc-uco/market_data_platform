"""Health check endpoint.

Provides a simple health check for:
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Monitoring systems (Grafana, DataDog)

The endpoint responds with service status and version.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from market_data_backend_platform.api import SettingsDep

# Create router for health endpoints
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response model for health check endpoint.

    Attributes:
        status: Service status ("healthy" or "unhealthy")
        version: Current application version from settings
    """

    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Check if the service is healthy.

    Args:
        settings: Application settings (injected by FastAPI).

    Returns:
        HealthResponse: JSON with status and version

    Example response:
        {"status": "healthy", "version": "0.1.0"}
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
    )
