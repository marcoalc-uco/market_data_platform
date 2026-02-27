# Makefile for Market Data Backend Platform

.PHONY: dev test test-all test-cov test-integration docker-up docker-down freeze db-migrate db-upgrade db-downgrade db-status clean help

# Default target
help:
	@echo Available commands:
	@echo   make dev          - Start development server
	@echo   make test         - Run unit tests
	@echo   make test-all         - Run all tests including integration
	@echo   make test-cov         - Run tests with coverage report
	@echo   make test-integration - Run integration tests with Docker
	@echo   make docker-up        - Start Docker Compose services
	@echo   make docker-down      - Stop Docker Compose services
	@echo   make freeze           - Update requirements.txt from virtual environment
	@echo   make db-migrate   - Generate Alembic migration (requires PostgreSQL)
	@echo   make db-upgrade   - Apply pending migrations
	@echo   make db-downgrade - Revert last migration
	@echo   make clean        - Remove temporary files

# Start development server with hot reload
dev:
	.\.venv\Scripts\uvicorn.exe market_data_backend_platform.main:app --reload --host 0.0.0.0 --port 8000

# Run unit tests (quick feedback during development)
test:
	.\.venv\Scripts\pytest.exe tests/unit/ -q

# Run all tests including integration (when available)
test-all:
	.\.venv\Scripts\pytest.exe tests/ -v

# Run tests with coverage report
test-cov:
	.\.venv\Scripts\pytest.exe --cov=src --cov-report=term-missing --cov-report=html
	cmd /c start .\htmlcov\class_index.html
	@echo Coverage report generated at .\htmlcov\class_index.html

# Run integration tests (requires Docker)
# Uses docker-compose.test.yml to avoid affecting production data
test-integration:
	@echo Starting TEST Docker Compose services...
	docker-compose -f docker-compose.test.yml up -d
	@echo Waiting for TEST services to be ready...
	@timeout /t 10 /nobreak >nul
	@echo Running integration tests...
	.\.venv\Scripts\pytest.exe tests/integration/ -v
	@echo Stopping TEST Docker Compose services...
	docker-compose -f docker-compose.test.yml down -v

# Start Docker Compose services
docker-up:
	docker-compose up -d --build
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo Services started.

# Stop Docker Compose services
docker-down:
	docker-compose down
	@echo Services stopped.

# Freeze dependencies into requirements.txt (guarantees UTF-8 and LF)
freeze:
	.\.venv\Scripts\python.exe -c "import subprocess; out = subprocess.check_output([r'.\.venv\Scripts\pip.exe', 'freeze', '--exclude-editable']); open('requirements.txt', 'wb').write(out.replace(b'\r\n', b'\n'))"

# Generate new Alembic migration (autogenerate from model changes)
# Usage: make db-migrate msg="add user table"
db-migrate:
	.\.venv\Scripts\alembic.exe revision --autogenerate -m "$(msg)"

# Apply all pending migrations
db-upgrade:
	.\.venv\Scripts\alembic.exe upgrade head

# Revert last migration
db-downgrade:
	.\.venv\Scripts\alembic.exe downgrade -1

# Show current migration status
db-status:
	.\.venv\Scripts\alembic.exe current

# Clean temporary files
clean:
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .coverage del .coverage
	@echo Cleaned temporary files
