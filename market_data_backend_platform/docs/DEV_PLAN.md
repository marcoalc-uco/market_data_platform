# DEV_PLAN.md - Development Execution Plan

> **Purpose:** Phase-by-phase execution roadmap
> **Location:** `/docs/DEV_PLAN.md`
> **Status:** Active
> **Version:** 1.0

---

## Document Hierarchy

**This plan implements:**

- `/docs/PRD.md` - Product requirements (architectural contract)

**Following standards from:**

- `/AGENT.md` - Technical standards
- `/docs/QA_PROTOCOL.md` - Validation checklist

**Golden Rule:** If execution diverges from PRD → **STOP** and escalate.

---

## 1. Overview

This plan decomposes the roadmap into **atomic, testable tasks** following **Test-Driven Development (TDD)** methodology.

### TDD Cycle (Mandatory)

```
RED: Write FAILING test
  ↓
GREEN: Minimum code to PASS
  ↓
REFACTOR: Improve without breaking
  ↓
COMMIT & VERIFY
```

### Validation Per Phase

Each phase must pass:

- ✅ `pytest -v` - All tests pass
- ✅ `pytest --cov=src --cov-fail-under=85` - Coverage ≥ 85%
- ✅ `mypy src/` - No type errors
- ✅ `pylint src/` - No critical warnings
- ✅ `pre-commit run --all-files` - Hooks pass

---

## 2. Phase Status

| Phase | Name                     | Status         |
| ----- | ------------------------ | -------------- |
| 0     | Design and Architecture  | ✅ Complete    |
| 1     | Project Setup            | ✅ Complete    |
| 2     | Backend Base (FastAPI)   | ✅ Complete    |
| 3     | Modeling and Persistence | ✅ Complete    |
| 4     | Data Ingestion (ETL)     | ✅ Complete    |
| 5     | REST API Queries         | ✅ Complete    |
| 6     | Grafana Visualization    | 🟡 In Progress |
| 7     | Dockerization            | ⚪ Pending     |
| 8     | CI/CD and Documentation  | ⚪ Pending     |

---

## 3. Phase 0 — Design and Architecture

**Objective:** Define the system before implementation.

### Tasks

- [x] Define domain model (Instrument, MarketPrice)
- [x] Select technology stack
- [x] Design data flow (ETL pipeline)
- [x] Document architecture principles (SOLID, DRY, PEP)
- [x] Create repository structure

### Deliverables

- [x] `docs/architecture.md`
- [x] `docs/roadmap.md`
- [x] `AGENT.md` (technical standards)
- [x] `docs/QA_PROTOCOL.md`
- [x] `docs/PRD.md` (this phase)

### Verification

```bash
# Verify documentation exists
ls docs/architecture.md docs/roadmap.md docs/PRD.md docs/QA_PROTOCOL.md
```

---

## 4. Phase 1 — Project Setup

**Objective:** Professional development environment.

### Tasks

- [x] Initialize Git repository
- [x] Configure `pyproject.toml`
  - [x] Project metadata
  - [x] mypy configuration
  - [x] black configuration
  - [x] isort configuration
- [x] Configure quality tools
  - [x] pylint (`.pylintrc`)
  - [x] mypy (in `pyproject.toml`)
  - [x] pytest
- [x] Configure pre-commit hooks (`.pre-commit-config.yaml`)
- [x] Create `Makefile` for automation
- [x] Create directory structure (`src/`, `tests/`, `alembic/`)
- [x] Create `.env.example`

### Deliverables

- [x] Working Python project with quality pipeline
- [x] Executable test suite (even if empty)
- [x] Virtual environment (`.venv/`)

### Verification

```bash
# Verify tools are configured
mypy --version
pylint --version
pytest --version
pre-commit --version

# Run quality checks
pre-commit run --all-files
pytest --collect-only
```

---

## 5. Phase 2 — Backend Base (FastAPI)

**Objective:** Minimal FastAPI application with TDD.

### Tasks

- [x] **RED:** Write test for `/health` endpoint
- [x] **GREEN:** Create FastAPI app with `/health`
- [x] Configure `pydantic-settings` for config
- [x] Configure structured logging (`structlog`)
- [x] Create modular structure (`api/`, `core/`)
- [x] Centralized error handling
- [x] **REFACTOR:** Apply SOLID principles

### Deliverables

- [x] FastAPI app with `/health` endpoint
- [x] Passing unit tests
- [x] Code coverage established

### Verification

```bash
# Run tests
pytest tests/unit/test_health.py -v

# Start server
uvicorn market_data_backend_platform.main:app --reload

# Test endpoint
curl http://localhost:8000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-13T20:50:00Z"
}
```

---

## 6. Phase 3 — Modeling and Persistence

**Objective:** Define domain with TDD.

### Tasks

- [x] **RED:** Write tests for Instrument model
- [x] **GREEN:** Create SQLAlchemy `Instrument` model
- [x] **RED:** Write tests for MarketPrice model
- [x] **GREEN:** Create SQLAlchemy `MarketPrice` model
- [x] Create Pydantic schemas (separate from models)
- [x] Implement Repository pattern
  - [x] `InstrumentRepository`
  - [x] `MarketPriceRepository`
- [x] Configure Alembic
- [x] Create initial migration
- [x] **REFACTOR:** Dependency Injection, Open/Closed

### Deliverables

- [x] Versioned database schema
- [x] Tested repositories
- [x] Reproducible migrations

### Verification

```bash
# Run model tests
pytest tests/unit/test_models.py -v

# Run repository tests
pytest tests/unit/test_repositories.py -v

# Apply migrations
alembic upgrade head

# Verify schema
psql -U postgres -d market_data -c "\dt"
```

**Expected Tables:**

- `instruments`
- `market_prices`
- `alembic_version`

---

## 7. Phase 4 — Data Ingestion (ETL)

**Objective:** Populate system with real data.

### Tasks

- [x] **RED:** Write tests for Yahoo Finance client
- [x] **GREEN:** Implement `YahooFinanceClient`
- [x] **RED:** Write tests for data transformer
- [x] **GREEN:** Implement `YahooTransformer`
- [x] **RED:** Write tests for ingestion service
- [x] **GREEN:** Implement `IngestionService`
- [x] Implement idempotent insertion (ON CONFLICT DO NOTHING)
- [x] Add structured logging for ETL operations
- [x] Create manual ingestion endpoint (Option B)
- [x] **REFACTOR:** Interface Segregation, DRY

### Deliverables

- [x] Functional and tested ETL pipeline
- [x] Historical data in database

### Verification

```bash
# Run ETL tests
pytest tests/unit/test_etl.py -v

# Manual ingestion via endpoint
curl -X POST http://localhost:8000/api/v1/ingest/run \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "period": "1mo"}'

# Verify data
psql -U postgres -d market_data -c \
  "SELECT COUNT(*) FROM market_prices WHERE instrument_id = 1;"
```

**Expected:** At least 20+ price records for AAPL.

---

## 8. Phase 5 — REST API Queries

**Objective:** Expose data as service.

### Tasks

- [x] **RED:** Write tests for `/api/v1/instruments` endpoints
- [x] **GREEN:** Implement instruments CRUD endpoints
  - [x] List instruments (GET)
  - [x] Get instrument by ID (GET)
  - [x] Create instrument (POST)
  - [x] Update instrument (PUT)
  - [x] Delete instrument (DELETE)
- [x] **RED:** Write tests for `/api/v1/prices` endpoints
- [x] **GREEN:** Implement price query endpoints
  - [x] Get prices by instrument
  - [x] Get latest price
- [x] Add input validation (query params)
- [x] Implement pagination
- [x] Consistent error handling (HTTP status codes)
- [x] **REFACTOR:** Remove code duplication

### Deliverables

- [x] Complete REST API
- [x] Auto-generated OpenAPI docs
- [x] Clear data contracts

### Verification

```bash
# Run API tests
pytest tests/integration/test_api.py -v

# Test instruments endpoint
curl http://localhost:8000/api/v1/instruments

# Test prices endpoint
curl "http://localhost:8000/api/v1/prices/1?limit=10"

# View OpenAPI docs
open http://localhost:8000/docs
```

**Expected:** Swagger UI with all endpoints documented.

---

## 9. Phase 6 — Grafana Visualization

**Objective:** Analytics and observability.

**Status:** 🟡 In Progress

### Tasks

- [ ] Configure PostgreSQL datasource in Grafana
- [ ] Create dashboard: Time-series evolution
- [ ] Create dashboard: Comparative analysis
- [ ] Create dashboard: Basic KPIs
- [ ] Export dashboards as JSON (version control)
- [ ] Document dashboard setup in README

### Deliverables

- [ ] Functional dashboards
- [ ] Exportable configuration
- [ ] Screenshots in `docs/`

### Verification

```bash
# Start Grafana (via Docker Compose)
docker-compose up -d grafana

# Access Grafana
open http://localhost:3000

# Login: admin / admin

# Verify datasource connection
# Navigate to: Configuration > Data sources > PostgreSQL
# Click "Test" button
```

**Expected:** "Data source is working" message.

**Manual Testing:**

1. Create new dashboard
2. Add panel with PostgreSQL query:
   ```sql
   SELECT timestamp, close
   FROM market_prices
   WHERE instrument_id = 1
   ORDER BY timestamp
   ```
3. Verify chart renders correctly

---

## 10. Phase 7 — Dockerization

**Objective:** Reproducible local environment.

**Status:** ⚪ Pending

### Tasks

- [ ] **RED:** Write integration tests with testcontainers
- [ ] **GREEN:** Create multi-stage `Dockerfile` for backend
- [ ] Create `docker-compose.yml`
  - [ ] FastAPI service
  - [ ] PostgreSQL / TimescaleDB service
  - [ ] Grafana service
- [ ] Configure health checks
- [ ] Centralize environment variables
- [ ] Create startup scripts
- [ ] **REFACTOR:** Optimize image size

### Deliverables

- [ ] `docker/Dockerfile`
- [ ] `docker/docker-compose.yml`
- [ ] One-command system startup

### Verification

```bash
# Build and start all services
docker-compose up --build

# Verify all services healthy
docker-compose ps

# Test API from container
curl http://localhost:8000/health

# Test database connectivity
docker exec -it postgres psql -U postgres -d market_data -c "SELECT 1;"

# Access Grafana
open http://localhost:3000
```

**Expected:** All services running and accessible.

---

## 11. Phase 8 — CI/CD and Documentation

**Objective:** Publishable project.

**Status:** ⚪ Pending

### Tasks

- [ ] Configure GitHub Actions
  - [ ] Lint + Type check workflow
  - [ ] Test + Coverage workflow
  - [ ] Build Docker image workflow
- [ ] Create professional `README.md`
- [ ] Update `docs/` with:
  - [ ] API documentation
  - [ ] Deployment guide
  - [ ] Architecture diagrams (Mermaid)
- [ ] Add quality badges to README
- [ ] Create `CONTRIBUTING.md`

### Deliverables

- [ ] Functional CI/CD pipeline
- [ ] Production-ready documentation
- [ ] Professional repository

### Verification

```bash
# Manually run GitHub Actions locally (using act)
act -l

# Verify README has badges
cat README.md | grep "badge"

# Verify docs are complete
ls docs/
```

**Expected Files:**

- `docs/PRD.md`
- `docs/DEV_PLAN.md`
- `docs/QA_PROTOCOL.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/API.md`

**GitHub Actions Expected:**

- ✅ All workflows passing
- ✅ Coverage report uploaded
- ✅ Docker image built successfully

---

## 12. Definition of Done (Per Phase)

### Code Quality

- [ ] All tests pass (`pytest -v`)
- [ ] Coverage ≥ 85% (`pytest --cov --cov-fail-under=85`)
- [ ] No mypy errors (`mypy src/`)
- [ ] No pylint critical warnings (`pylint src/`)
- [ ] Code formatted (`black --check src/`)

### Documentation

- [ ] Complete docstrings (public functions)
- [ ] Comments only where necessary
- [ ] PRD updated if design changed

### Git

- [ ] Descriptive commit message (`feat(module): description`)
- [ ] Branch up to date with main
- [ ] No merge conflicts

### Validation Script

```bash
#!/bin/bash
# validate_phase.sh

set -e

echo "🔍 Validating Phase Completion..."

# Tests
echo "Running tests..."
pytest -v
pytest --cov=src --cov-fail-under=85

# Type checking
echo "Type checking..."
mypy src/

# Linting
echo "Linting..."
pylint src/

# Formatting
echo "Checking formatting..."
black --check src/

# Pre-commit hooks
echo "Running pre-commit..."
pre-commit run --all-files

echo "✅ Phase validation COMPLETE"
```

---

## 13. Task Breakdown (Atomic)

### Example: Phase 3, Task: Create Instrument Model

**Time Estimate:** 1-2 hours

**Subtasks:**

1. **RED** - Write failing test in `tests/unit/test_models.py`
   ```python
   def test_instrument_creation():
       instrument = Instrument(symbol="AAPL", name="Apple Inc.", asset_type="STOCK")
       assert instrument.symbol == "AAPL"
   ```
2. **GREEN** - Create model in `src/models/instrument.py`
3. **GREEN** - Run test, verify it passes
4. **REFACTOR** - Add docstrings, type hints
5. **VERIFY** - Run `mypy`, `pylint`, `black`
6. **COMMIT** - `git commit -m "feat(models): add Instrument model"`

---

## 14. Dependency Graph

```
Phase 0 (Design)
    ↓
Phase 1 (Setup)
    ↓
Phase 2 (FastAPI Base)
    ↓
Phase 3 (Models) ──────────┐
    ↓                      ↓
Phase 4 (ETL)          Phase 5 (REST API)
    ↓                      ↓
    └──────────┬───────────┘
               ↓
         Phase 6 (Grafana)
               ↓
         Phase 7 (Docker)
               ↓
         Phase 8 (CI/CD)
```

---

## 15. Current Focus (Phase 6)

**Next Immediate Tasks:**

### Task 6.1: Configure Grafana Datasource

**Steps:**

1. Ensure PostgreSQL is accessible (port 5432)
2. Start Grafana container
3. Login to Grafana (admin/admin)
4. Add PostgreSQL datasource:
   - Host: `postgres:5432` (if using Docker network)
   - Database: `market_data`
   - User: `postgres`
   - SSL Mode: `disable` (local only)
5. Test connection
6. Save configuration

**Verification:**

```bash
# Test datasource via Grafana API
curl -u admin:admin http://localhost:3000/api/datasources
```

### Task 6.2: Create Time-Series Dashboard

**Steps:**

1. Create new dashboard
2. Add panel with query:
   ```sql
   SELECT
     timestamp AS time,
     close AS value,
     symbol AS metric
   FROM market_prices
   JOIN instruments ON market_prices.instrument_id = instruments.id
   WHERE $__timeFilter(timestamp)
   ORDER BY timestamp
   ```
3. Configure panel:
   - Visualization: Time series
   - Legend: Show
   - Axes: Auto
4. Save dashboard
5. Export as JSON to `docs/grafana/dashboards/`

**Verification:**

- Chart displays historical prices
- Time range picker works
- Legend shows instrument symbols

---

## 16. Risk Mitigation

### Technical Debt Tracking

- Document all `# TODO` with issue numbers
- Tag all `# pylint: disable` with justification
- Review all `except Exception` (should be specific)

### Rollback Strategy

- All migrations reversible (`alembic downgrade`)
- Feature flags for experimental features
- Git tags on stable releases

---

## 17. Reference Commands

### Development Workflow

```bash
# Activate virtual environment
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn market_data_backend_platform.main:app --reload

# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Type check
mypy src/

# Lint
pylint src/

# Format
black src/ tests/
isort src/ tests/

# Pre-commit
pre-commit run --all-files

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

---

**Version:** 1.0
**Location:** `/docs/DEV_PLAN.md`
**Related:** `/docs/PRD.md`, `/AGENT.md`, `/docs/QA_PROTOCOL.md`
**Last Updated:** 2026-02-13
