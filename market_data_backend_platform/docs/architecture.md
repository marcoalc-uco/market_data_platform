# System Architecture — Market Data Backend Platform

> **Purpose:** Technical architecture and component design
> **Location:** `/docs/architecture.md`

---

## Overview

The **Market Data Backend Platform** is an **API-first backend system** designed for financial time-series data.

**Core Architecture Principles:**

- **Separation of Concerns:** Ingestion, persistence, API, and visualization are isolated
- **Extensibility:** New data sources can be added without modifying core logic
- **Testability:** Repository pattern enables easy mocking
- **Reproducibility:** Docker-based local execution

---

## Technology Stack

| Layer              | Technology               | Version    | Purpose                    |
| ------------------ | ------------------------ | ---------- | -------------------------- |
| **API Framework**  | FastAPI                  | 0.115+     | Async web framework        |
| **Validation**     | Pydantic                 | 2.x        | Type-safe schemas          |
| **ORM**            | SQLAlchemy               | 2.x        | Database abstraction       |
| **Migrations**     | Alembic                  | 1.x        | Schema versioning          |
| **Database**       | PostgreSQL / TimescaleDB | 16+ / 2.x  | Time-series storage        |
| **Testing**        | pytest + httpx           | 8.x / 0.27 | Unit and integration tests |
| **Quality**        | pylint + mypy + black    | Latest     | Linting and formatting     |
| **Logging**        | structlog                | Latest     | Structured logging         |
| **Visualization**  | Grafana                  | 11+        | Dashboards                 |
| **Infrastructure** | Docker Compose           | 2.x        | Local orchestration        |
| **Scheduler**      | APScheduler              | 3.x        | Automated data ingestion   |

### Python Version

- **Required:** Python 3.14+
- **Type System:** Native generics (PEP 585)

---

## System Architecture

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   External APIs                         │
│              (Yahoo Finance, Alpha Vantage)             │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     ▼
             ┌───────────────┐
             │  ETL Clients  │ ← Fetch raw data
             └───────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Transformers   │ ← Normalize to schema
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │  Repositories  │ ← Idempotent insert
            └────────┬───────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  PostgreSQL/TimescaleDB │ ← Single source of truth
        └─────┬──────────────┬───┘
              │              │
              ▼              ▼
      ┌────────────┐   ┌──────────┐
      │  FastAPI   │   │ Grafana  │
      │  REST API  │   │Dashboard │
      └────────────┘   └──────────┘
```

---

## Project Structure

```
market_data_backend_platform/
├── src/
│   └── market_data_backend_platform/
│       ├── __init__.py
│       ├── main.py                    # FastAPI application entry point
│       │
│       ├── api/                       # HTTP Layer
│       │   ├── routes/
│       │   │   ├── auth.py            # Authentication endpoints (JWT login)
│       │   │   ├── health.py          # Health check endpoint
│       │   │   ├── instruments.py     # Instrument CRUD
│       │   │   └── prices.py          # Price queries
│       │   └── dependencies.py        # FastAPI dependency injection
│       │
│       ├── core/                      # Application Core
│       │   ├── config.py              # Pydantic settings
│       │   ├── logging.py             # Structured logging config
│       │   └── exceptions.py          # Custom exceptions
│       │
│       ├── models/                    # SQLAlchemy ORM Models
│       │   ├── instrument.py          # Instrument entity
│       │   └── market_price.py        # MarketPrice entity
│       │
│       ├── schemas/                   # Pydantic Schemas (DTOs)
│       │   ├── instrument.py          # Instrument schemas
│       │   └── market_price.py        # MarketPrice schemas
│       │
│       ├── repositories/              # Data Access Layer
│       │   ├── base.py                # Base repository pattern
│       │   ├── instrument.py          # Instrument repository
│       │   └── market_price.py        # MarketPrice repository
│       │
│       ├── services/                  # Business Logic Layer
│       │   ├── instrument.py          # Instrument service
│       │   └── market_price.py        # MarketPrice service
│       │
│       ├── etl/                       # Data Ingestion
│       │   ├── clients/               # External API clients
│       │   │   └── yahoo.py           # Yahoo Finance client
│       │   ├── transformers/          # Data normalizers
│       │   │   └── yahoo_transformer.py
│       │   └── services/
│       │       └── ingestion.py       # Ingestion orchestrator
│       │
│       ├── scheduler/                 # Automated Jobs
│       │   └── __init__.py            # APScheduler configuration
│       │
│       ├── auth/                      # Authentication & Security
│       │   ├── password.py            # bcrypt hashing & verification
│       │   ├── token.py               # JWT creation & decoding
│       │   └── dependencies.py        # get_current_user dependency
│       │
│       └── db/                        # Database Layer
│           └── session.py             # Session factory
│
├── tests/
│   ├── conftest.py                    # Pytest fixtures
│   ├── unit/                          # Unit tests
│   └── integration/                   # Integration tests
│
├── alembic/                           # Database Migrations
│   ├── versions/                      # Migration scripts
│   └── env.py                         # Alembic config
│
├── docker/
│   ├── Dockerfile                     # Backend image
│   └── docker-compose.yml             # Multi-service orchestration
│
├── docs/
│   ├── PRD.md                         # Product requirements
│   ├── DEV_PLAN.md                    # Execution plan
│   ├── QA_PROTOCOL.md                 # Quality checklist
│   ├── architecture.md (this file)    # System architecture
│   └── roadmap.md                     # Development roadmap
│
├── scripts/
│   ├── validate_against_prd.py        # PRD compliance check
│   └── validate_schemas.py            # Schema validation
│
├── pyproject.toml                     # Project configuration
├── AGENT.md                           # AI agent coding standards
├── Makefile                           # Automation commands
├── .pre-commit-config.yaml            # Git hooks
├── .env.example                       # Environment template
└── README.md                          # Project overview
```

---

## Core Components

### 1. FastAPI Application (`main.py`)

**Responsibilities:**

- Application initialization and configuration
- Middleware registration (CORS, logging, error handling)
- Route registration
- Lifespan events (startup/shutdown)

**Key Features:**

- Auto-generated OpenAPI documentation (`/docs`)
- Async request handling
- Dependency injection via `Depends()`

---

### 2. Repository Pattern (`repositories/`)

**Purpose:** Abstract data access from business logic

**Interface:**

```python
class Repository(Protocol[T]):
    def get_by_id(self, id: int) -> T | None: ...
    def get_all(self) -> list[T]: ...
    def create(self, entity: T) -> T: ...
    def update(self, entity: T) -> T: ...
    def delete(self, id: int) -> None: ...
```

**Implementations:**

- `InstrumentRepository` - Instrument CRUD operations
- `MarketPriceRepository` - Price CRUD operations with bulk insert

**Benefits:**

- Testability: Easy to mock in unit tests
- Flexibility: Swap implementations without changing services
- Separation: Database logic isolated from business logic

---

### 3. Service Layer (`services/`)

**Purpose:** Orchestrate business operations

**Responsibilities:**

- Coordinate multiple repository calls
- Apply business rules
- Handle transactions
- Emit structured logs

**Example Flow:**

```python
# services/instrument.py
class InstrumentService:
    def __init__(self, repository: InstrumentRepository):
        self.repository = repository

    def activate_instrument(self, instrument_id: int) -> Instrument:
        instrument = self.repository.get_by_id(instrument_id)
        if not instrument:
            raise InstrumentNotFoundError(instrument_id)

        instrument.is_active = True
        return self.repository.update(instrument)
```

---

### 4. ETL Pipeline (`etl/`)

**Architecture:**

```
External API → Client → Transformer → Repository → Database
```

**Components:**

#### ETL Clients (`etl/clients/`)

- Fetch raw data from external APIs
- Handle authentication, rate limiting, retries
- Return raw response data

#### Transformers (`etl/transformers/`)

- Normalize external data to internal schemas
- Apply data quality rules
- Convert to Pydantic schemas for validation

#### Ingestion Service (`etl/services/ingestion.py`)

- Orchestrate fetch → transform → load
- Implement idempotent insertion (ON CONFLICT DO NOTHING)
- Log metrics (fetched, inserted, skipped)

**Idempotency:**

- Unique constraint: `(instrument_id, timestamp)`
- Re-running ingestion doesn't create duplicates

---

### 5. Database Layer

#### PostgreSQL/TimescaleDB

**Role:** Single source of truth for all market data

**Features:**

- **Hypertables:** Optimized time-series partitioning (TimescaleDB)
- **Referential Integrity:** Foreign keys enforced
- **Indexes:** Composite indexes on `(instrument_id, timestamp)`

#### Alembic Migrations

**Workflow:**

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add volume column"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Best Practices:**

- All schema changes via migrations (never manual SQL)
- Migrations are reversible (up/down functions)
- Test migrations in development before production

---

### 6. REST API (`api/routes/`)

**Versioning:** `/api/v1/*`

**Endpoints:**

| Method | Endpoint                                | Purpose                      |
| ------ | --------------------------------------- | ---------------------------- |
| GET    | `/health`                               | Health check                 |
| POST   | `/api/v1/auth/token`                    | Login — get JWT access token |
| GET    | `/api/v1/instruments`                   | List instruments             |
| GET    | `/api/v1/instruments/{id}`              | Get instrument by ID         |
| POST   | `/api/v1/instruments`                   | Create instrument            |
| PUT    | `/api/v1/instruments/{id}`              | Update instrument            |
| DELETE | `/api/v1/instruments/{id}`              | Delete instrument            |
| GET    | `/api/v1/prices/{instrument_id}`        | Get prices for instrument    |
| GET    | `/api/v1/prices/{instrument_id}/latest` | Get latest price             |

**Features:**

- Automatic request/response validation (Pydantic)
- Pagination on list endpoints (`skip`, `limit`)
- OpenAPI documentation at `/docs`

---

### 7. Scheduler (`scheduler/`)

**Purpose:** Automated periodic data ingestion

**Implementation:** APScheduler

**Configuration:**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
    ingest_all_active,
    trigger="interval",
    minutes=30,
    id="ingest_market_data"
)
```

**Lifecycle:**

- Starts with FastAPI application (lifespan event)
- Runs in background (non-blocking)
- Graceful shutdown on application stop

---

### 8. Grafana Visualization

**Architecture:**

- **Direct Database Connection:** Grafana → PostgreSQL
- **No Business Logic:** Read-only queries
- **Dashboard as Code:** JSON configuration versioned in Git

**Data Flow:**

```
PostgreSQL ← Grafana datasource
     ↓
  SQL Query (time-series aggregation)
     ↓
  Dashboard Panel (graph, table, gauge)
```

---

## Data Flow

### Ingestion Flow (ETL)

```
1. APScheduler triggers job every 30 minutes
       ↓
2. IngestionService.ingest_all_active()
       ↓
3. For each active instrument:
       ↓
   a. YahooFinanceClient.get_historical_prices()
       ↓
   b. YahooTransformer.transform_batch()
       ↓
   c. MarketPriceRepository.bulk_create_new()
       ↓
   d. PostgreSQL INSERT (ON CONFLICT DO NOTHING)
       ↓
4. Log metrics: fetched, inserted, skipped
```

### Query Flow (API)

```
1. HTTP GET /api/v1/prices/{instrument_id}
       ↓
2. FastAPI router (prices.py)
       ↓
3. Dependency injection: get_session()
       ↓
4. MarketPriceRepository.get_by_instrument()
       ↓
5. PostgreSQL SELECT with filters
       ↓
6. Pydantic serialization
       ↓
7. JSON response
```

---

## Database Schema

### Tables

#### instruments

```sql
CREATE TABLE instruments (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    asset_type VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instruments_symbol ON instruments(symbol);
CREATE INDEX idx_instruments_asset_type ON instruments(asset_type);
```

#### market_prices

```sql
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL NOT NULL,
    high DECIMAL NOT NULL,
    low DECIMAL NOT NULL,
    close DECIMAL NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_instrument_timestamp UNIQUE (instrument_id, timestamp)
);

CREATE INDEX idx_market_prices_instrument_timestamp
    ON market_prices(instrument_id, timestamp DESC);
CREATE INDEX idx_market_prices_timestamp ON market_prices(timestamp);
```

### TimescaleDB Optimization (Optional)

```sql
-- Convert to hypertable for time-series optimization
SELECT create_hypertable('market_prices', 'timestamp');

-- Automatic data retention (e.g., keep 2 years)
SELECT add_retention_policy('market_prices', INTERVAL '2 years');
```

---

## Configuration Management

### Environment Variables

**Required:**

- `DATABASE_URL` - PostgreSQL connection string
- `API_PREFIX` - API base path (default: `/api/v1`)

**Optional:**

- `DEBUG` - Enable debug mode (default: `false`)
- `DB_POOL_SIZE` - Connection pool size (default: `5`)
- `DB_MAX_OVERFLOW` - Max overflow connections (default: `10`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `YAHOO_API_KEY` - Yahoo Finance API key (if required)

### Settings Class

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Loaded from .env or environment
```

---

## Deployment Architecture

### Local Development (Docker Compose)

```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./docker
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/market_data

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
```

**Start Command:**

```bash
docker-compose up -d
```

**Access:**

- API: `http://localhost:8000/docs`
- Grafana: `http://localhost:3000`
- PostgreSQL: `localhost:5432`

---

## Extension Points

### Adding New Data Sources

1. Create client in `etl/clients/new_source.py`
2. Implement transformer in `etl/transformers/new_source_transformer.py`
3. Update `IngestionService` to use new client
4. No changes to repository or database schema needed

### Adding New Instruments

1. Insert via API: `POST /api/v1/instruments`
2. Set `is_active=true` to enable automatic ingestion
3. Scheduler will pick up on next run

### Custom Aggregations

1. Create view in PostgreSQL:
   ```sql
   CREATE VIEW daily_returns AS
   SELECT instrument_id, timestamp,
          (close - LAG(close) OVER (PARTITION BY instrument_id ORDER BY timestamp)) / LAG(close) AS return
   FROM market_prices;
   ```
2. Query from Grafana or API

---

## Performance Considerations

### Database Indexing

- **Composite index** on `(instrument_id, timestamp DESC)` for time-series queries
- **Partial index** on `is_active` instruments for scheduler efficiency

### Connection Pooling

```python
engine = create_engine(
    database_url,
    pool_size=5,        # Normal connections
    max_overflow=10,    # Burst capacity
    pool_pre_ping=True  # Health check before use
)
```

### Pagination

All list endpoints support:

- `skip` - Offset for pagination
- `limit` - Page size (max 1000)

---

## Security

### Secrets Management

- **Never commit:** `.env` files
- **Always commit:** `.env.example` (template)
- **Production:** Use secret managers (AWS Secrets Manager, HashiCorp Vault)

### SQL Injection Prevention

- **ORM Parameterization:** SQLAlchemy escapes all inputs
- **No raw SQL:** Except in reviewed migrations

### API Security (JWT Authentication)

- **Login endpoint:** `POST /api/v1/auth/token` — returns a signed JWT access token
- **Password storage:** bcrypt hashing (never stored in plain text)
- **Token validation:** HS256-signed JWT verified on every protected request via `get_current_user` dependency
- Input validation via Pydantic
- CORS configuration for production
- Rate limiting (future enhancement)

---

## Monitoring and Observability

### Structured Logging

All logs are JSON-formatted:

```json
{
  "event": "ingestion_complete",
  "symbol": "AAPL",
  "fetched": 30,
  "inserted": 25,
  "skipped": 5,
  "timestamp": "2026-02-13T20:00:00Z"
}
```

### Health Checks

- **Application:** `GET /health`
- **Database:** Connection pool monitoring
- **Docker:** Container health checks

---

**Version:** 3.0
**Location:** `/docs/architecture.md`
**Last Updated:** 2026-02-22
