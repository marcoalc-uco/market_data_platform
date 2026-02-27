"""Integration test fixtures.

Provides fixtures for Docker-based integration testing.
Uses subprocess to control docker-compose services.
"""

import subprocess
import time
from typing import Generator

import httpx
import psycopg2
import pytest


@pytest.fixture(scope="session")
def docker_compose_up() -> Generator[None, None, None]:
    """Start Docker Compose services for integration tests.

    This fixture:
    1. Uses docker-compose.test.yml (separate from production)
    2. Stops and removes any existing TEST containers/volumes (clean slate)
    3. Starts all TEST services
    4. Waits for services to be healthy
    5. Yields control to tests
    6. Optionally tears down TEST services after all tests complete

    NOTE: This uses separate containers/volumes/ports from production:
    - postgres_test (port 5433) instead of postgres (port 5432)
    - api_test (port 8001) instead of api (port 8000)
    - Volume: postgres_test_data instead of postgres_data
    """
    # Clean up any existing TEST containers and volumes for fresh start
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
        check=False,  # Don't fail if nothing to stop
        capture_output=True,
    )

    # Start TEST services with fresh volumes — always rebuild the API image
    # so that code changes are picked up without manual docker rmi.
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d", "--build"],
        check=True,
        capture_output=True,
    )

    # Wait for services to be healthy
    max_retries = 30
    for i in range(max_retries):
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Simple check: if output contains "Up", services are running
            if "Up" in result.stdout:
                time.sleep(5)  # Extra wait for health checks
                break
        except subprocess.CalledProcessError:
            pass

        time.sleep(1)

        if i == max_retries - 1:
            raise RuntimeError("Docker services failed to start")

    yield

    # Teardown: stop TEST services and remove volumes
    # This cleans up test data but does NOT affect production
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
        check=False,  # Don't fail if already down
        capture_output=True,
    )


@pytest.fixture(scope="session")
def api_client(docker_compose_up: None) -> Generator[httpx.Client, None, None]:
    """HTTP client for the containerized TEST API.

    Waits for the API to be ready, obtains a JWT token via the login
    endpoint, and yields a client with the Authorization header pre-set
    so that all requests to protected routes are authenticated.

    Args:
        docker_compose_up: Ensures Docker TEST services are running.

    Yields:
        Configured httpx.Client pointing to the TEST API (port 8001)
        with a Bearer token in the default headers.
    """
    base_url = "http://localhost:8001"

    # Wait for API to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = httpx.get(f"{base_url}/health", timeout=2.0)
            if response.status_code == 200:
                break
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        time.sleep(1)

        if i == max_retries - 1:
            raise RuntimeError("API failed to become ready")

    # Obtain a JWT token once for the entire test session
    token_response = httpx.post(
        f"{base_url}/api/v1/auth/token",
        data={"username": "admin@market.com", "password": "adminpassword"},
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    with httpx.Client(
        base_url=base_url,
        timeout=10.0,
        headers={"Authorization": f"Bearer {access_token}"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
def db_connection(
    docker_compose_up: None,
) -> Generator[psycopg2.extensions.connection, None, None]:
    """Direct PostgreSQL connection for TEST data verification.

    Args:
        docker_compose_up: Ensures Docker TEST services are running

    Yields:
        psycopg2 connection to the containerized TEST database (port 5433)
    """
    # Wait for TEST PostgreSQL to be ready
    max_retries = 30
    conn = None

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5433,
                user="market_data",
                password="market_data_pass",
                database="market_data",
            )
            break
        except psycopg2.OperationalError:
            time.sleep(1)

            if i == max_retries - 1:
                raise RuntimeError("TEST PostgreSQL failed to become ready")

    if conn is None:
        raise RuntimeError("Failed to establish database connection")

    yield conn

    conn.close()
