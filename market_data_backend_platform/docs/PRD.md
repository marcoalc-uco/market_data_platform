# PRD.md - Product Requirements Document

> **Purpose:** Architectural contract defining WHAT to build
> **Location:** `/docs/PRD.md`
> **Status:** Active
> **Version:** 1.0

---

## Document Hierarchy

**In case of conflict, this document takes precedence over:**

- `/AGENT.md` - Technical standards (HOW to write code)
- `/docs/QA_PROTOCOL.md` - Validation checklist
- `/docs/DEV_PLAN.md` - Execution plan

**Golden Rule:** If implementation diverges from this PRD → **STOP** and request clarification.

---

## 1. Executive Summary

### Project Vision

The **Market Data Backend Platform** is an **API-first backend system** designed for financial time-series data ingestion, storage, and analysis.

The platform demonstrates:

- **Backend Engineering** with Python and FastAPI
- **Clean Code** principles (SOLID, DRY, PEP compliance)
- **Test-Driven Development (TDD)** as core methodology
- **DevOps** practices with Docker and CI/CD

### Core Objectives

1. **Ingest** historical market data (stocks, indices, cryptocurrencies)
2. **Normalize** and persist time-series data consistently
3. **Expose** data via REST APIs (API-first design)
4. **Visualize** data and KPIs using Grafana
5. **Execute** reproducibly in local environment using Docker

### Target Users

- Financial analysts requiring historical data access
- Developers building on top of market data APIs
- Data scientists performing quantitative analysis

---

## 2. Technology Stack

| Layer              | Technology                      | Justification                    |
| ------------------ | ------------------------------- | -------------------------------- |
| **API Framework**  | FastAPI                         | Async support, auto OpenAPI docs |
| **Validation**     | Pydantic v2                     | Type-safe schemas                |
| **ORM**            | SQLAlchemy 2.x                  | Mature, flexible ORM             |
| **Migrations**     | Alembic                         | Schema versioning                |
| **Database**       | PostgreSQL / TimescaleDB        | Time-series optimization         |
| **Testing**        | pytest + httpx + testcontainers | TDD support                      |
| **Quality**        | pylint + mypy + pre-commit      | Linting and type checking        |
| **Logging**        | structlog                       | Structured logging               |
| **Visualization**  | Grafana                         | Dashboard and analytics          |
| **Infrastructure** | Docker Compose                  | Local orchestration              |

### Python Version

- **Required:** Python 3.14+
- **Type Hints:** Native types (PEP 585) - `list[str]` not `List[str]`

---

## 3. Domain Model

### 3.1 Core Entities

#### Instrument

Represents a tradable financial instrument.

**Attributes:**

- `id` (int, PK): Auto-increment identifier
- `symbol` (str, unique, indexed): Trading symbol (e.g., "AAPL", "BTC-USD")
- `name` (str): Full name (e.g., "Apple Inc.")
- `asset_type` (enum): `STOCK` | `INDEX` | `CRYPTO`
- `is_active` (bool): Whether to fetch data for this instrument
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Constraints:**

- Symbol must be unique and non-empty
- Asset type required

#### MarketPrice

Represents a single time-series data point for an instrument.

**Attributes:**

- `id` (int, PK): Auto-increment identifier
- `instrument_id` (int, FK → Instrument): Reference to instrument
- `timestamp` (datetime, indexed): Price timestamp (UTC)
- `open` (Decimal): Opening price
- `high` (Decimal): Highest price
- `low` (Decimal): Lowest price
- `close` (Decimal): Closing price
- `volume` (BigInt): Trading volume
- `created_at` (datetime): Insertion timestamp

**Constraints:**

- Unique constraint on `(instrument_id, timestamp)` - prevents duplicates
- All price fields must be non-negative
- Volume must be non-negative

---

## 4. Pydantic Schemas

### 4.1 Instrument Schemas

#### InstrumentBase

```python
class InstrumentBase(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=200)
    asset_type: AssetType
    is_active: bool = True
```

#### InstrumentCreate

```python
class InstrumentCreate(InstrumentBase):
    pass
```

#### InstrumentUpdate

```python
class InstrumentUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
```

#### InstrumentResponse

```python
class InstrumentResponse(InstrumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

### 4.2 MarketPrice Schemas

#### MarketPriceCreate

```python
class MarketPriceCreate(BaseModel):
    instrument_id: int = Field(gt=0)
    timestamp: datetime
    open: Decimal = Field(ge=0)
    high: Decimal = Field(ge=0)
    low: Decimal = Field(ge=0)
    close: Decimal = Field(ge=0)
    volume: int = Field(ge=0)

    @field_validator('high')
    @classmethod
    def validate_high_gte_low(cls, v: Decimal, info: ValidationInfo) -> Decimal:
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('High must be >= Low')
        return v
```

#### MarketPriceResponse

```python
class MarketPriceResponse(MarketPriceCreate):
    id: int
    created_at: datetime
```

---

## 5. API Specification

### 5.1 Versioning

- Base path: `/api/v1`
- All endpoints must be versioned
- Breaking changes require new version number

### 5.2 Health Endpoint

**GET** `/health`

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-13T20:50:00Z"
}
```

### 5.3 Instruments

#### List Instruments

**GET** `/api/v1/instruments`

**Query Parameters:**

- `asset_type` (optional): Filter by asset type
- `is_active` (optional): Filter by active status
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=100, max=1000): Page size

**Response:** `List[InstrumentResponse]`

#### Get Instrument

**GET** `/api/v1/instruments/{id}`

**Response:** `InstrumentResponse`

**Errors:**

- `404` - Instrument not found

#### Create Instrument

**POST** `/api/v1/instruments`

**Body:** `InstrumentCreate`

**Response:** `InstrumentResponse` (201 Created)

**Errors:**

- `400` - Validation error
- `409` - Symbol already exists

#### Update Instrument

**PUT** `/api/v1/instruments/{id}`

**Body:** `InstrumentUpdate`

**Response:** `InstrumentResponse`

**Errors:**

- `404` - Instrument not found
- `400` - Validation error

#### Delete Instrument

**DELETE** `/api/v1/instruments/{id}`

**Response:** `204 No Content`

**Errors:**

- `404` - Instrument not found

### 5.4 Market Prices

#### Get Prices by Instrument

**GET** `/api/v1/prices/{instrument_id}`

**Query Parameters:**

- `start_date` (optional): Filter from date (ISO 8601)
- `end_date` (optional): Filter to date (ISO 8601)
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=100, max=1000): Page size

**Response:** `List[MarketPriceResponse]`

**Errors:**

- `404` - Instrument not found
- `400` - Invalid date format

#### Get Latest Price

**GET** `/api/v1/prices/{instrument_id}/latest`

**Response:** `MarketPriceResponse`

**Errors:**

- `404` - Instrument not found or no prices available

---

## 6. ETL Specification

### 6.1 Data Sources

**Supported:**

- Yahoo Finance API (primary)

**Future extensions:**

- Alpha Vantage
- CoinGecko (crypto)
- Custom CSV import

### 6.2 ETL Flow

```
External API
     │
     ▼
ETL Client (fetch raw data)
     │
     ▼
Transformer (normalize to schema)
     │
     ▼
Validator (Pydantic schema validation)
     │
     ▼
Repository (idempotent insert)
     │
     ▼
Database (PostgreSQL)
```

### 6.3 Idempotency

- Duplicate detection via `(instrument_id, timestamp)` unique constraint
- Re-running ingestion for same period must not create duplicates
- Use `ON CONFLICT DO NOTHING` or equivalent

### 6.4 Scheduling Options

**Option A: Automated Scheduler**

- APScheduler runs ingestion every X minutes
- Starts with FastAPI application
- Configured via environment variables

**Option B: Manual Trigger**

- Endpoint: **POST** `/api/v1/ingest/run`
- Body: `{ "symbol": "AAPL", "period": "1mo" }`
- Response: `{ "fetched": 30, "inserted": 25, "skipped": 5 }`

**Current Implementation:** Option B (manual trigger via endpoint)

---

## 7. Architecture Patterns

### 7.1 SOLID Principles

#### Single Responsibility

- **Routes:** Handle HTTP only, delegate to services
- **Services:** Business logic only
- **Repositories:** Data access only
- **Models:** Data structure only

#### Open/Closed

- Use polymorphism for extensibility (e.g., multiple API clients)
- Avoid massive `if/elif` chains

#### Liskov Substitution

- Subclasses must be substitutable for base classes
- No breaking changes in overrides

#### Interface Segregation

- Use `Protocol` for small, focused interfaces
- Avoid monolithic interfaces

#### Dependency Inversion

- **CRITICAL:** Always inject dependencies via `__init__`
- Never instantiate dependencies inside classes
- Depend on abstractions, not concretions

### 7.2 Repository Pattern

**Interface:**

```python
class Repository(Protocol[T]):
    def get_by_id(self, id: int) -> T | None: ...
    def get_all(self) -> list[T]: ...
    def create(self, entity: T) -> T: ...
    def update(self, entity: T) -> T: ...
    def delete(self, id: int) -> None: ...
```

**Implementation:**

- One repository per model
- Inject `Session` via `__init__`
- Return domain models, not ORM objects (when applicable)

### 7.3 Service Layer

**Responsibilities:**

- Orchestrate multiple repository calls
- Apply business rules
- Handle transactions
- Log operations

**Anti-patterns:**

- Services directly accessing database
- Services containing HTTP logic
- Services with hardcoded dependencies

---

## 8. Configuration Management

### 8.1 Environment Variables

**Required:**

- `DATABASE_URL`: PostgreSQL connection string
- `API_PREFIX`: API base path (default: `/api/v1`)

**Optional:**

- `DEBUG`: Enable debug mode (default: `false`)
- `DB_POOL_SIZE`: Connection pool size (default: 5)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 10)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### 8.2 Configuration Class

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    api_prefix: str = "/api/v1"
    debug: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
```

---

## 9. Testing Requirements

### 9.1 Test Coverage

- **Minimum:** 85% code coverage
- **Target:** 90%+ for business logic
- **Critical paths:** 100% coverage

### 9.2 Test Types

#### Unit Tests

- Test individual functions/methods in isolation
- Use mocks for dependencies
- Fast execution (\<1s per test)

#### Integration Tests

- Test API endpoints with real database (testcontainers)
- Verify repository operations
- Test ETL flow end-to-end

#### E2E Tests

- Test complete system with Docker Compose
- Verify health checks
- Test data flow from API to Grafana

### 9.3 TDD Cycle (Mandatory in Phase 3+)

```
RED: Write failing test
  ↓
GREEN: Minimum code to pass
  ↓
REFACTOR: Improve without breaking
  ↓
REPEAT
```

---

## 10. Logging and Observability

### 10.1 Structured Logging

**Library:** `structlog`

**Levels:**

- `DEBUG`: Development traces
- `INFO`: Normal operations
- `WARNING`: Recoverable issues
- `ERROR`: Operation failures
- `CRITICAL`: System failures

**Format:**

```python
logger.info(
    "user_created",
    user_id=user.id,
    email=user.email,
    timestamp=datetime.utcnow().isoformat()
)
```

### 10.2 Log Requirements

- All HTTP requests logged (middleware)
- All database operations logged (at DEBUG level)
- All ETL operations logged (with metrics)
- All errors logged with `exc_info=True`

### 10.3 Prohibited

- ❌ `print()` statements in production code
- ❌ Generic `except Exception` without re-raise
- ❌ Silenced exceptions

---

## 11. Error Handling

### 11.1 Custom Exceptions

**Base Exception:**

```python
class MarketDataException(Exception):
    """Base exception for all application errors."""
    pass
```

**Domain Exceptions:**

```python
class InstrumentNotFoundError(MarketDataException):
    def __init__(self, instrument_id: int):
        self.instrument_id = instrument_id
        super().__init__(f"Instrument {instrument_id} not found")

class DuplicateSymbolError(MarketDataException):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Symbol {symbol} already exists")
```

### 11.2 HTTP Error Responses

**Format:**

```json
{
  "detail": "Instrument not found",
  "error_code": "INSTRUMENT_NOT_FOUND",
  "timestamp": "2026-02-13T20:50:00Z"
}
```

---

## 12. Database Schema

### 12.1 Tables

#### instruments

| Column     | Type         | Constraints          |
| ---------- | ------------ | -------------------- |
| id         | SERIAL       | PRIMARY KEY          |
| symbol     | VARCHAR(20)  | UNIQUE, NOT NULL     |
| name       | VARCHAR(200) | NOT NULL             |
| asset_type | VARCHAR(10)  | NOT NULL             |
| is_active  | BOOLEAN      | DEFAULT TRUE         |
| created_at | TIMESTAMP    | DEFAULT CURRENT_TIME |
| updated_at | TIMESTAMP    | DEFAULT CURRENT_TIME |

**Indexes:**

- `idx_instruments_symbol` on `symbol`
- `idx_instruments_asset_type` on `asset_type`

#### market_prices

| Column        | Type      | Constraints                    |
| ------------- | --------- | ------------------------------ |
| id            | SERIAL    | PRIMARY KEY                    |
| instrument_id | INTEGER   | NOT NULL, FK → instruments(id) |
| timestamp     | TIMESTAMP | NOT NULL                       |
| open          | DECIMAL   | NOT NULL                       |
| high          | DECIMAL   | NOT NULL                       |
| low           | DECIMAL   | NOT NULL                       |
| close         | DECIMAL   | NOT NULL                       |
| volume        | BIGINT    | NOT NULL                       |
| created_at    | TIMESTAMP | DEFAULT CURRENT_TIME           |

**Constraints:**

- `UNIQUE(instrument_id, timestamp)`

**Indexes:**

- `idx_market_prices_instrument_timestamp` on `(instrument_id, timestamp DESC)`
- `idx_market_prices_timestamp` on `timestamp`

### 12.2 Migrations

- All schema changes via Alembic
- Reversible migrations (up/down)
- Migrations tested before merge

---

## 13. Project Structure (Canonical)

```
market_data_backend_platform/
├── src/
│   └── market_data_backend_platform/
│       ├── __init__.py
│       ├── main.py              # FastAPI entry point
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── health.py
│       │   │   ├── instruments.py
│       │   │   └── prices.py
│       │   └── dependencies.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── logging.py
│       │   └── exceptions.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── instrument.py
│       │   └── market_price.py
│       ├── etl/
│       │   ├── __init__.py
│       │   ├── clients/
│       │   │   ├── __init__.py
│       │   │   └── yahoo.py
│       │   ├── transformers/
│       │   │   ├── __init__.py
│       │   │   └── yahoo_transformer.py
│       │   └── services/
│       │       ├── __init__.py
│       │       └── ingestion.py
│       └── db/
│           ├── __init__.py
│           └── session.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── alembic/
│   ├── versions/
│   └── env.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── PRD.md (this file)
│   ├── DEV_PLAN.md
│   ├── QA_PROTOCOL.md
│   ├── architecture.md
│   └── roadmap.md
├── scripts/
│   ├── validate_against_prd.py
│   └── validate_schemas.py
├── pyproject.toml
├── AGENT.md
├── Makefile
├── .pre-commit-config.yaml
├── .env.example
└── README.md
```

---

## 14. Non-Functional Requirements

### 14.1 Performance

- API response time \<200ms (p95)
- Database queries optimized with proper indexes
- Connection pooling configured

### 14.2 Scalability

- Stateless API (horizontal scaling ready)
- Database connection pool management
- Pagination on all list endpoints

### 14.3 Security

- No hardcoded secrets
- Environment-based configuration
- SQL injection prevention (ORM parameterization)
- Input validation on all endpoints

### 14.4 Maintainability

- Code coverage ≥ 85%
- Type hints on all functions
- Docstrings on all public APIs
- Pre-commit hooks enforced

---

## 15. Validation Commands

### Complete Validation (Pre-Commit)

```bash
pytest --cov=src --cov-fail-under=85 && \
mypy src/ && \
pylint src/ && \
pre-commit run --all-files
```

### Quick Validation (Development)

```bash
pytest -q && mypy src/ --no-error-summary
```

---

## 16. Conflict Resolution

If this PRD conflicts with other documents:

1. **STOP** implementation
2. **DOCUMENT** the conflict
3. **ESCALATE** to user
4. **WAIT** for decision

**Template:**

```
⚠️  PRD CONFLICT DETECTED

PRD.md requires: [X]
[Other document] says: [Y]

RECOMMENDATION: [preferred solution]

Awaiting clarification before proceeding.
```

---

**Version:** 1.0
**Location:** `/docs/PRD.md`
**Related:** `/AGENT.md`, `/docs/QA_PROTOCOL.md`, `/docs/DEV_PLAN.md`
**Last Updated:** 2026-02-13
