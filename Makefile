# Makefile — market_data_platform (monorepo root)
# Delegates to service-level Makefiles. Requires GNU Make.

.PHONY: up up-dev down down-clean logs logs-api logs-frontend \
        backend-test backend-test-integration backend-test-all backend-test-cov \
        backend-lint backend-migrate backend-upgrade \
        frontend-install frontend-dev frontend-build frontend-lint frontend-test \
        check-all check-all-integration help

# ── Full Stack ────────────────────────────────────────────────────────────────
up:           ## Start all services (production-like)
	docker-compose up -d

up-dev:       ## Start all services with hot reload
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

down:         ## Stop all services
	docker-compose down

down-clean:   ## Stop and remove volumes (fresh start)
	docker-compose down -v

logs:         ## Follow logs for all services
	docker-compose logs -f

logs-api:     ## Follow backend logs only
	docker-compose logs -f api

logs-frontend: ## Follow frontend logs only
	docker-compose logs -f frontend

# ── Backend ───────────────────────────────────────────────────────────────────
backend-test: ## Run backend unit tests
	cd market_data_backend_platform && make test

backend-test-integration: ## Run backend integration tests (isolated docker)
	cd market_data_backend_platform && docker-compose -f docker-compose.test.yml up --abort-on-container-exit
	cd market_data_backend_platform && docker-compose -f docker-compose.test.yml down -v

backend-test-all: ## Run all backend tests (unit + integration)
	cd market_data_backend_platform && make test-all

backend-test-cov: ## Run backend tests with coverage report
	cd market_data_backend_platform && make test-cov

backend-lint: ## Run backend linting (ruff + mypy)
	cd market_data_backend_platform && make lint

backend-migrate: ## Generate new Alembic migration (msg="description")
	cd market_data_backend_platform && make db-migrate msg="$(msg)"

backend-upgrade: ## Apply pending Alembic migrations
	cd market_data_backend_platform && make db-upgrade

# ── Frontend ──────────────────────────────────────────────────────────────────
frontend-install: ## Install frontend dependencies
	cd market_data_frontend_platform && npm install

frontend-dev: ## Start frontend dev server (standalone)
	cd market_data_frontend_platform && npm run dev

frontend-build: ## Build frontend for production
	cd market_data_frontend_platform && npm run build

frontend-lint: ## Run frontend linting (ESLint + Prettier)
	cd market_data_frontend_platform && npm run lint

frontend-test: ## Run frontend tests (Vitest)
	cd market_data_frontend_platform && npm test

# ── Quality Gates ─────────────────────────────────────────────────────────────
check-all:    ## Run all quality checks (backend + frontend)
	cd market_data_backend_platform && make test
	cd market_data_frontend_platform && npm run lint && npm test

check-all-integration: ## Run all checks including integration tests
	cd market_data_backend_platform && make lint && make test
	cd market_data_backend_platform && docker-compose -f docker-compose.test.yml up --abort-on-container-exit
	cd market_data_backend_platform && docker-compose -f docker-compose.test.yml down -v
	cd market_data_frontend_platform && npm run lint && npm test

# ── Help ──────────────────────────────────────────────────────────────────────
help:         ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
