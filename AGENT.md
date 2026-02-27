# AGENT.md - AI Agent Instructions

> **Operational Context:** Act as a Senior Full-Stack Software Architect. You are working in a **monorepo** containing a Python/FastAPI backend and a JavaScript/React frontend. Your absolute priority is consistency between services, code robustness, and clear separation of concerns. Reject quick solutions if they compromise technical debt.

> **Location:** This file is at the **monorepo root** and is **tool-agnostic** (works with Claude Code, Antigravity, Aider, Cursor, etc.)

> **Scope:** This file governs **monorepo-level decisions** (orchestration, docker-compose, cross-service contracts). Each service has its own AGENT.md for service-specific standards.

---

## 0. Document Hierarchy and References

### Monorepo Document Map

```
market_data_platform/
├── AGENT.md                        ← THIS FILE (monorepo root — orchestration)
├── docker-compose.yml              ← Full stack orchestration
├── docker-compose.dev.yml          ← Development overrides
├── .env.example                    ← Shared environment template
│
├── backend/
│   ├── AGENT.md                    ← Backend-specific standards (Python/FastAPI)
│   └── docs/
│       ├── PRD.md                  ← Backend product requirements
│       ├── DEV_PLAN.md             ← Backend execution plan
│       ├── QA_PROTOCOL.md          ← Backend validation checklist
│       └── architecture.md         ← Backend architecture
│
├── frontend/
│   ├── AGENT.md                    ← Frontend-specific standards (React/JS)
│   └── docs/
│       ├── PRD.md                  ← Frontend product requirements
│       ├── DEV_PLAN.md             ← Frontend execution plan
│       └── architecture.md         ← Frontend architecture
│
└── docs/
    └── architecture.md             ← Full system architecture (this level)
```

### Reading Order (In Case of Conflict)

**Read documents in this priority order:**

1. **`/AGENT.md`** (this file) — Monorepo orchestration standards
   - Defines: Cross-service conventions, docker-compose, API contracts
   - Action if contradicts service AGENT.md: **STOP** and request user clarification

2. **`/backend/AGENT.md`** — Backend-specific standards
   - Defines: Python/FastAPI code standards (SOLID, TDD, PEPs)
   - Applies in: All backend work

3. **`/frontend/AGENT.md`** — Frontend-specific standards
   - Defines: React/JS code standards (components, hooks, testing)
   - Applies in: All frontend work

4. **`/backend/docs/PRD.md`** and **`/frontend/docs/PRD.md`** — Product contracts
   - Define: WHAT each service builds
   - Action if contradicts: **STOP** and request user clarification

### Rule: Which AGENT.md Applies?

| Task                                | Read                       |
| ----------------------------------- | -------------------------- |
| Modify `docker-compose.yml`         | `/AGENT.md` (this file)    |
| Add backend endpoint                | `/backend/AGENT.md`        |
| Add frontend component              | `/frontend/AGENT.md`       |
| Change API contract (shared schema) | `/AGENT.md` + both service |
| Add environment variable            | `/AGENT.md` (this file)    |
| CI/CD pipeline changes              | `/AGENT.md` (this file)    |

---

## 1. Monorepo Structure

### Canonical Directory Layout

```
market_data_platform/
├── backend/                        ← Python/FastAPI service (complete project)
│   ├── src/
│   ├── tests/
│   ├── alembic/
│   ├── docker/
│   │   └── Dockerfile              ← Backend image
│   ├── pyproject.toml
│   ├── Makefile
│   ├── AGENT.md
│   └── .env.example
│
├── frontend/                       ← React/Vite/JS service
│   ├── src/
│   │   ├── api/                    ← HTTP client layer (fetch against FastAPI)
│   │   ├── components/             ← Reusable UI components
│   │   ├── pages/                  ← Route-level components
│   │   ├── hooks/                  ← Custom React hooks
│   │   └── main.jsx                ← Entry point
│   ├── public/
│   ├── Dockerfile                  ← Frontend image (Nginx)
│   ├── package.json
│   ├── vite.config.js
│   ├── .eslintrc.js
│   ├── AGENT.md
│   └── .env.example
│
├── docker/
│   └── nginx/
│       └── nginx.conf              ← Reverse proxy config (optional)
│
├── docs/
│   └── architecture.md             ← Full system architecture
│
├── docker-compose.yml              ← Production-like orchestration
├── docker-compose.dev.yml          ← Development overrides
├── .env.example                    ← Root env template
├── .gitignore                      ← Monorepo-wide ignores
├── Makefile                        ← Root automation commands
├── AGENT.md                        ← This file
└── README.md                       ← Monorepo entry point
```

### MANDATORY: What Lives at Root vs Service Level

**Root level:** Only orchestration artifacts — `docker-compose.yml`, root `Makefile`, root `.env`, root `AGENT.md`, root `README.md`, root `.gitignore`.

**Service level:** Everything else — source code, tests, dependencies, service-specific docs, service-specific Dockerfile.

**FORBIDDEN:**

- ❌ Source code at monorepo root
- ❌ `pyproject.toml` or `package.json` at root
- ❌ Service-specific config at root level
- ❌ Mixing backend and frontend dependencies

---

## 2. Environment Variables

### Strategy: Layered Configuration

Variables are scoped to where they are consumed:

```
/(.env)                             ← Shared infra (DB credentials, ports)
/backend/(.env)                     ← Backend-only (SECRET_KEY, JWT config)
/frontend/(.env)                    ← Frontend-only (VITE_API_URL)
```

### Root `.env.example` Template

```env
# ── Infrastructure (shared) ──────────────────────────────────
POSTGRES_USER=market_data
POSTGRES_PASSWORD=market_data_pass
POSTGRES_DB=market_data

# ── Backend ──────────────────────────────────────────────────
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD_HASH=$$2b$$12$$...your-hash-here...
SECRET_KEY=your-openssl-rand-hex-32-value

# ── Frontend ─────────────────────────────────────────────────
VITE_API_URL=http://localhost:8000
```

### Rules

1. **NEVER commit `.env`** — only `.env.example` goes to Git
2. **VITE\_ prefix is mandatory** for all frontend env vars (Vite security requirement)
3. **Backend vars** are not accessible from frontend — by design
4. **Escape `$` with `$$`** in values used by Docker Compose

---

## 3. Docker Compose Orchestration

### File Strategy — Three Scopes, Never Mixed

```
market_data_platform/
├── docker-compose.yml              ← ROOT: full stack (prod-like, all services)
├── docker-compose.dev.yml          ← ROOT: hot reload overrides (dev only)
│
├── backend/
│   ├── docker-compose.yml          ← BACKEND: standalone backend + postgres + grafana
│   └── docker-compose.test.yml     ← BACKEND: isolated integration tests
│
└── frontend/
    └── (no docker-compose — managed from root)
```

**Purpose of each file:**

| File                               | Purpose                                          | Usage                             |
| ---------------------------------- | ------------------------------------------------ | --------------------------------- |
| `/docker-compose.yml`              | Full stack demo/dev — all services together      | `make up`                         |
| `/docker-compose.dev.yml`          | Hot reload overrides on top of root compose      | `make up-dev`                     |
| `/backend/docker-compose.yml`      | Backend standalone — works without frontend      | `cd backend && docker-compose up` |
| `/backend/docker-compose.test.yml` | Integration tests — isolated ports, no scheduler | `make backend-test-integration`   |

**RULE: Files are independent, never cross-reference each other.**
The root compose does NOT import or depend on `backend/docker-compose.yml`.
Both define their own services independently.

---

### Services Architecture

```
┌─────────────────────────────────────────────────┐
│                   Browser                        │
└──────────────────────┬──────────────────────────┘
                       │ :5173 (dev) / :80 (prod)
              ┌────────▼────────┐
              │    frontend     │  React → Nginx
              └────────┬────────┘
                       │ HTTP :8000
              ┌────────▼────────┐
              │      api        │  FastAPI → Uvicorn
              └────────┬────────┘
                       │ :5432
              ┌────────▼────────┐
              │    postgres     │  PostgreSQL 16
              └─────────────────┘
                       │ direct read
              ┌────────▼────────┐
              │    grafana      │  Dashboards :3000
              └─────────────────┘

── Integration tests (isolated) ──────────────────
              ┌────────────────┐
              │  postgres_test │  :5433 (different port)
              └───────┬────────┘
              ┌────────▼────────┐
              │    api_test     │  :8001, scheduler OFF
              └─────────────────┘
```

---

### `/docker-compose.yml` (Root — Full Stack)

```yaml
# docker-compose.yml (monorepo root)
# Purpose: Full stack orchestration — all services together
# Usage: docker-compose up -d

services:
  postgres:
    image: postgres:16
    container_name: market_data_postgres
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-market_data}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-market_data_pass}
      POSTGRES_DB: ${POSTGRES_DB:-market_data}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-market_data}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - platform

  api:
    build:
      context: ./backend
      dockerfile: docker/Dockerfile
    container_name: market_data_api
    restart: always
    # NOTE: env_file intentionally omitted.
    # ADMIN_PASSWORD_HASH and SECRET_KEY contain '$' characters that
    # docker-compose interpolates as variable references, corrupting values.
    # Pass sensitive vars explicitly via environment: block.
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-market_data}:${POSTGRES_PASSWORD:-market_data_pass}@postgres:5432/${POSTGRES_DB:-market_data}
      API_PREFIX: /api/v1
      DEBUG: ${DEBUG:-false}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      INGESTION_INTERVAL_MINUTES: ${INGESTION_INTERVAL_MINUTES:-5}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      ADMIN_EMAIL: ${ADMIN_EMAIL:-admin@market.com}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - platform
    volumes:
      - ./backend/alembic:/app/alembic
      - ./backend/alembic.ini:/app/alembic.ini

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production # Multi-stage: use nginx stage
    container_name: market_data_frontend
    restart: always
    environment:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    ports:
      - "80:80"
    depends_on:
      api:
        condition: service_healthy
    networks:
      - platform

  grafana:
    image: grafana/grafana:11.0.0
    container_name: market_data_grafana
    restart: always
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:-admin}
      GF_SERVER_ROOT_URL: http://localhost:3000
      GF_AUTH_ANONYMOUS_ENABLED: "false"
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - grafana_data:/var/lib/grafana
      - ./backend/docker/grafana/provisioning:/etc/grafana/provisioning
      - ./backend/docker/grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - platform

volumes:
  postgres_data:
    driver: local
  grafana_data:
    driver: local

networks:
  platform:
    driver: bridge
```

---

### `/docker-compose.dev.yml` (Root — Dev Overrides)

```yaml
# docker-compose.dev.yml (monorepo root)
# Purpose: Hot reload for backend and frontend during development
# Usage: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

services:
  api:
    command: uvicorn market_data_backend_platform.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./backend/src:/app/src # Hot reload — backend source
      - ./backend/alembic:/app/alembic
      - ./backend/alembic.ini:/app/alembic.ini

  frontend:
    build:
      context: ./frontend
      target: development # Multi-stage: use Vite dev server stage
    ports:
      - "5173:5173" # Vite default port
    volumes:
      - ./frontend/src:/app/src # Hot reload — frontend source
      - /app/node_modules # Preserve node_modules inside container
```

---

### Critical Rules for docker-compose

1. **`env_file` is FORBIDDEN for secrets** — `ADMIN_PASSWORD_HASH` and `SECRET_KEY` contain `$` that Docker Compose interpolates, corrupting the values. Always pass via `environment:` block explicitly.
2. **`docker-compose.yml` (root) must work standalone** — no dependency on any backend compose file.
3. **healthcheck mandatory** for postgres and api — downstream services depend on them.
4. **Never hardcode credentials** — always `${VAR:-default}` pattern.
5. **Build context points to service root** — `./backend`, `./frontend`.
6. **Source volumes only in dev override** — never in production compose.
7. **Integration tests use backend compose** — never triggered from root compose.

---

## 4. API Contract — Frontend ↔ Backend

### Source of Truth: OpenAPI Spec

The backend auto-generates the OpenAPI spec at `http://localhost:8000/openapi.json`. This is the **single source of truth** for the API contract.

**MANDATORY workflow when changing the API:**

```
1. Modify backend endpoint (FastAPI)
2. Verify spec at /openapi.json reflects change
3. Update frontend API client accordingly
4. Test integration end-to-end
5. Commit both changes in the same commit
```

**FORBIDDEN:**

- ❌ Frontend calling endpoints not defined in OpenAPI spec
- ❌ Backend changing response shape without updating frontend client
- ❌ Hardcoding API URLs in frontend components (use `src/api/` layer)

### Frontend API Layer Convention

All HTTP calls must go through `frontend/src/api/`:

```
frontend/src/api/
├── client.js           ← Base fetch client (auth headers, base URL)
├── instruments.js      ← Instrument endpoints
├── prices.js           ← Price endpoints
└── auth.js             ← Authentication (JWT login, token storage)
```

**NEVER** call `fetch()` directly from components or pages.

---

## 5. Git Conventions

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat | fix | docs | style | refactor | test | chore | ci
Scope: backend | frontend | docker | docs | root
```

**Examples:**

```bash
feat(frontend): add candlestick chart component for OHLCV data
feat(backend): add pagination to /api/v1/prices endpoint
fix(docker): correct healthcheck command for api service
chore(root): update .gitignore with frontend node_modules
ci(root): add frontend lint step to GitHub Actions
docs(frontend): add component architecture diagram
```

### Branch Strategy

```
main          ← Stable, deployable
develop       ← Integration branch
feature/      ← New features (feature/frontend-auth)
fix/          ← Bug fixes (fix/docker-healthcheck)
```

### `.gitignore` at Monorepo Root

```gitignore
# Python (backend)
backend/.venv
backend/__pycache__/
backend/*.egg-info
backend/.pytest_cache
backend/.mypy_cache
backend/.ruff_cache
backend/htmlcov/
backend/.coverage

# JavaScript (frontend)
frontend/node_modules/
frontend/dist/
frontend/.vite/

# Environment
.env
backend/.env
frontend/.env

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

---

## 6. Root Makefile

### Mandatory Commands

```makefile
# Makefile (monorepo root)

# ── Full Stack ────────────────────────────────────────────────
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

# ── Backend ───────────────────────────────────────────────────
backend-test: ## Run backend unit tests
	cd backend && make test

backend-test-integration: ## Run backend integration tests (isolated docker)
	cd backend && docker-compose -f docker-compose.test.yml up --abort-on-container-exit
	cd backend && docker-compose -f docker-compose.test.yml down -v

backend-lint: ## Run backend linting
	cd backend && make lint

backend-migrate: ## Run database migrations
	cd backend && make db-upgrade

# ── Frontend ──────────────────────────────────────────────────
frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Start frontend dev server (standalone)
	cd frontend && npm run dev

frontend-build: ## Build frontend for production
	cd frontend && npm run build

frontend-lint: ## Run frontend linting
	cd frontend && npm run lint

frontend-test: ## Run frontend tests
	cd frontend && npm test

# ── Quality Gates ─────────────────────────────────────────────
check-all:    ## Run all quality checks (backend + frontend)
	cd backend && make lint && make test
	cd frontend && npm run lint && npm test

check-all-integration: ## Run all checks including integration tests
	cd backend && make lint && make test
	cd backend && docker-compose -f docker-compose.test.yml up --abort-on-container-exit
	cd backend && docker-compose -f docker-compose.test.yml down -v
	cd frontend && npm run lint && npm test

# ── Help ──────────────────────────────────────────────────────
help:         ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: up up-dev down down-clean logs logs-api logs-frontend \
        backend-test backend-test-integration backend-lint backend-migrate \
        frontend-install frontend-dev frontend-build frontend-lint frontend-test \
        check-all check-all-integration help
```

---

## 7. Frontend Service Standards (Summary)

> Full detail in `/frontend/AGENT.md`. This section defines monorepo-level constraints only.

### Stack (Non-negotiable)

| Layer         | Technology         | Purpose                           |
| ------------- | ------------------ | --------------------------------- |
| Framework     | React 18+          | UI component model                |
| Build tool    | Vite               | Dev server + production build     |
| Language      | JavaScript (ES6+)  | No TypeScript (for now)           |
| Styling       | CSS Modules        | Scoped styles per component       |
| HTTP Client   | fetch (native)     | No axios unless justified         |
| Data fetching | TanStack Query     | Server state + caching            |
| Charts        | lightweight-charts | OHLCV candlestick (TradingView)   |
| Linting       | ESLint + Prettier  | Code quality (equivalent to ruff) |
| Testing       | Vitest + RTL       | Unit + component tests            |
| Container     | Nginx (Alpine)     | Serves static build in prod       |

### Frontend Dockerfile (Multi-stage)

```dockerfile
# frontend/Dockerfile

# ── Stage 1: Build ─────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci                          # Clean install (reproducible)
COPY . .
RUN npm run build                   # Output: /app/dist

# ── Stage 2: Production (Nginx) ────────────────────────────
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# ── Stage 3: Development (Vite dev server) ─────────────────
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

---

## 8. Integration Testing Strategy

### Cross-Service Tests

Integration tests that span backend + frontend live at the **monorepo root**, not inside either service:

```
tests/                              ← Monorepo-level integration tests
└── e2e/                            ← End-to-end (Playwright or Cypress)
    ├── auth.spec.js                ← Login flow: browser → frontend → backend → DB
    ├── instruments.spec.js         ← Instrument CRUD via UI
    └── prices.spec.js              ← Price chart renders with real data
```

Unit and integration tests for each service stay inside their own directory:

```
backend/tests/          ← pytest (unit + backend integration)
frontend/src/**/*.test.js ← Vitest (unit + component tests)
tests/e2e/              ← Playwright (full stack, optional phase)
```

---

## 9. CI/CD Pipeline (GitHub Actions)

### Workflow Strategy

```yaml
# .github/workflows/ci.yml

name: CI

on: [push, pull_request]

jobs:
  backend:
    name: Backend Quality
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - run: pip install -r requirements.txt
      - run: ruff check src/
      - run: mypy src/
      - run: pytest --cov=src --cov-fail-under=85

  frontend:
    name: Frontend Quality
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm test

  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - uses: actions/checkout@v4
      - run: docker-compose build
```

### Quality Gates (Non-negotiable)

- **Backend:** `pytest --cov-fail-under=85` must pass
- **Frontend:** `npm run lint` must pass with 0 errors
- **Docker:** Both images must build successfully
- **Merge to main:** All 3 jobs must be green

---

## 10. Conflict Handling

If a user instruction **contradicts** this AGENT.md:

### Warning Template

```
⚠️  WARNING: Technical Risk Detected

The proposed solution violates [PRINCIPLE X] because [REASON].

RISKS:
- Short-term: [Immediate consequence]
- Long-term: [Technical debt]

RECOMMENDED ALTERNATIVE:
[Propose solution following AGENT.md]

Do you want to proceed with original solution (NOT recommended)
or apply the alternative?
```

### If User Insists

Document in the relevant file:

```js
// TODO(TECH_DEBT): Violation of [PRINCIPLE] - [REASON]
// Decision: User insisted for [REASON]
// Date: YYYY-MM-DD
// Impact: [CONSEQUENCES]
// Plan: Refactor in [DATE/SPRINT]
```

---

## 11. Executive Summary

### Golden Rules (Monorepo Level)

1. **Root is orchestration only** — no source code at root
2. **One `.env` per scope** — root, backend, frontend each have their own
3. **API contract is sacred** — OpenAPI spec is the single source of truth
4. **Frontend never calls fetch directly** — always through `src/api/` layer
5. **Commit scope is mandatory** — `feat(frontend):`, `fix(backend):`, etc.
6. **Both services must pass CI** before merging to main
7. **docker-compose up** must work with a single command from root
8. **healthcheck** mandatory for all services with dependencies
9. **Multi-stage Dockerfile** mandatory for frontend (builder + nginx)
10. **Warn user** if any cross-service contract is violated

### Priority Hierarchy

```
1st Security       (JWT, env vars never committed, CORS configured)
2nd Correctness    (API contract respected, data flows end-to-end)
3rd Testability    (backend ≥85%, frontend components tested)
4th Maintainability (SOLID backend, component separation frontend)
5th Performance    (optimize only if needed)
```

---

## 12. Quick References

### Monorepo Commands

```bash
# Start everything
make up

# Development with hot reload
make up-dev

# Run all quality checks (unit only)
make check-all

# Run all quality checks including integration tests
make check-all-integration

# Backend only
make backend-test                  # Unit tests
make backend-test-integration      # Integration tests (docker isolated)
make backend-lint
make backend-migrate

# Frontend only
make frontend-install
make frontend-dev
make frontend-test
make frontend-lint

# Docker
make down
make down-clean
make logs
```

### Service URLs

| Service     | URL                        | Notes                        |
| ----------- | -------------------------- | ---------------------------- |
| Frontend    | http://localhost:5173      | Dev (Vite)                   |
| Frontend    | http://localhost:80        | Prod (Nginx)                 |
| Backend API | http://localhost:8000      | FastAPI                      |
| API Docs    | http://localhost:8000/docs | Swagger UI                   |
| Grafana     | http://localhost:3000      | admin/admin                  |
| PostgreSQL  | localhost:5432             | market_data/market_data_pass |

### Key Files

- **`/docker-compose.yml`** — Full stack orchestration
- **`/docker-compose.dev.yml`** — Development overrides
- **`/.env.example`** — Environment template
- **`/Makefile`** — Root automation
- **`/backend/AGENT.md`** — Backend standards (Python/FastAPI)
- **`/frontend/AGENT.md`** — Frontend standards (React/JS)

---

**Version:** 1.1
**Location:** Monorepo root (`/AGENT.md`)
**Scope:** Tool-agnostic (Claude Code, Antigravity, Aider, Cursor)
**Services:** backend (Python/FastAPI) + frontend (React/Vite/JS)
**Last Updated:** 2026-02-27
