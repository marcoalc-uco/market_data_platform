# 📈 Market Data Backend Platform

> A production-grade FastAPI backend for financial market data — built with clean architecture, TDD, and full Docker support.

[![CI](https://github.com/marcoalc-uco/market_data_backend_platform/actions/workflows/ci.yml/badge.svg)](https://github.com/marcoalc-uco/market_data_backend_platform/actions/workflows/ci.yml)

---

## What is this?

A backend platform that automatically ingests historical market data (stocks, indices, cryptocurrencies) from external APIs, stores it in PostgreSQL, and exposes it through a REST API — with Grafana dashboards for visualization out of the box.

**Key highlights:**

- 🔐 **JWT Authentication** — Secure API access with bcrypt-hashed credentials
- 📈 **ETL Pipeline** — Automated market data ingestion via APScheduler + Yahoo Finance
- 🗄️ **PostgreSQL** — Time-series optimized schema with Alembic migrations
- 📊 **Grafana** — Pre-configured dashboards, ready to explore
- 🐳 **One-command Docker setup** — API + DB + Grafana with `docker-compose up`
- ✅ **Full test suite** — Unit and integration tests with ≥85% coverage

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/) 2.0+

### 1. Clone and configure

```bash
git clone https://github.com/marcoalc-uco/market_data_backend_platform.git
cd market_data_backend_platform
cp .env.example .env
```

### 2. Generate your admin password hash

The API uses bcrypt-hashed passwords. Generate one for your admin user:

```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"
```

Paste the output into your `.env` file, escaping `$` with `$$` for Docker Compose:

```env
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD_HASH=$$2b$$12$$...your-hash-here...

# Also set a proper secret key:
SECRET_KEY=your-openssl-rand-hex-32-value
```

> **Tip:** Generate a strong `SECRET_KEY` with: `openssl rand -hex 32`

### 3. Start everything

```bash
docker-compose up -d
```

Services will be available at:

| Service        | URL                          | Credentials                    |
| -------------- | ---------------------------- | ------------------------------ |
| **API Docs**   | http://localhost:8000/docs   | —                              |
| **API Health** | http://localhost:8000/health | —                              |
| **Grafana**    | http://localhost:3000        | admin / admin                  |
| **PostgreSQL** | localhost:5432               | market_data / market_data_pass |

---

## Using the API

### Interactive API Docs (recommended)

The easiest way to explore and test the API is via the built-in **Swagger UI** at http://localhost:8000/docs.

To authenticate inside Swagger:

1. Click **POST /api/v1/auth/token** → **Try it out**
2. Fill in `username` (your `ADMIN_EMAIL`) and `password`, then **Execute**
3. Copy the `access_token` from the response
4. Click the **🔒 Authorize** button at the top of the page
5. Paste the token as `Bearer <token>` and click **Authorize**

All protected endpoints in Swagger will now use your token automatically.

> **Tip:** There's also a ReDoc UI at http://localhost:8000/redoc for a cleaner read-only reference.

### Via cURL (advanced)

```bash
# Step 1: Authenticate
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@yourdomain.com&password=your_password"

# Step 2: Use the token
curl http://localhost:8000/api/v1/instruments \
  -H "Authorization: Bearer <your_token>"

# Get OHLCV prices for an instrument
curl "http://localhost:8000/api/v1/prices/1?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer <token>"
```

### Grafana Dashboards

1. Open http://localhost:3000 → login with `admin/admin`
2. Go to **Dashboards → Market Data - Multi-Instrument by Asset Type**
3. Pick an asset type (STOCK, INDEX, CRYPTO) from the dropdown
4. Adjust the time range as needed

---

## Development

### Local setup (without Docker)

**Requirements:** Python 3.14+, PostgreSQL 16+

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local DB credentials

# Run migrations
alembic upgrade head

# Start dev server (with hot reload)
make dev
```

### Running tests

```bash
make test          # Unit tests only (fast)
make test-all      # All tests including integration
make test-cov      # Coverage report (opens browser)
```

### Code quality

All quality checks run automatically via pre-commit hooks on every commit:

```bash
pre-commit install   # One-time setup
git commit ...       # hooks run: black, isort, pylint, mypy, pytest
```

---

## Project Structure

```
market_data_backend_platform/
├── src/market_data_backend_platform/
│   ├── api/routes/          # FastAPI endpoints (auth, instruments, prices, health)
│   ├── auth/                # JWT tokens, bcrypt hashing, auth dependencies
│   ├── core/                # Config (pydantic-settings), logging, exceptions
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas (request/response DTOs)
│   ├── repositories/        # Data access layer (Repository pattern)
│   ├── services/            # Business logic
│   ├── etl/                 # Data ingestion (clients, transformers, scheduler)
│   ├── db/                  # Database session factory
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/                # Fast tests, no external dependencies
│   └── integration/         # Tests with real PostgreSQL (via Docker)
├── alembic/                 # Database migrations
├── docker/                  # Dockerfile + Grafana provisioning
├── docs/                    # Architecture and roadmap
├── .github/workflows/       # GitHub Actions CI pipeline
├── docker-compose.yml       # Full stack: API + PostgreSQL + Grafana
└── Makefile                 # Common dev commands
```

---

## Docker Commands

```bash
make docker-up       # Build and start all services
make docker-down     # Stop all services
make docker-down -v  # Stop and delete volumes (fresh start)

# View logs
docker-compose logs -f api

# Access PostgreSQL
docker-compose exec postgres psql -U market_data -d market_data

# Rebuild after code changes
docker-compose build api && docker-compose up -d api
```

---

## Database Migrations

```bash
make db-migrate msg="describe your change"   # Generate new migration
make db-upgrade                              # Apply pending migrations
make db-downgrade                            # Revert last migration
make db-status                               # Show current version
```

---

## Tech Stack

| Layer         | Technology     | Purpose                       |
| ------------- | -------------- | ----------------------------- |
| API           | FastAPI 0.115+ | Async web framework           |
| Auth          | PyJWT + bcrypt | JWT tokens & password hashing |
| Validation    | Pydantic 2.x   | Type-safe schemas & settings  |
| ORM           | SQLAlchemy 2.x | Database abstraction          |
| Migrations    | Alembic        | Schema versioning             |
| Database      | PostgreSQL 16  | Time-series data storage      |
| Scheduler     | APScheduler    | Automated data ingestion      |
| Visualization | Grafana 11+    | Dashboards                    |
| Logging       | structlog      | Structured JSON logs          |
| Testing       | pytest + httpx | Unit and integration tests    |
| Containers    | Docker Compose | Local orchestration           |
| CI            | GitHub Actions | Automated quality pipeline    |

---

## Documentation

| Document                             | Description                                            |
| ------------------------------------ | ------------------------------------------------------ |
| [Architecture](docs/architecture.md) | Component design, data flows, DB schema, API endpoints |
| [Roadmap](docs/roadmap.md)           | Development phases and progress                        |
| [Grafana Guide](docs/GRAFANA.md)     | Dashboard setup and customization                      |

---

## Troubleshooting

**Port already in use (5432, 8000, 3000)**
Stop conflicting services, or change the port mapping in `docker-compose.yml`.

**`market_data_api` not starting**

```bash
docker-compose logs api   # Check for migration errors or missing env vars
```

**Grafana dashboard is empty**
The scheduler runs ingestion automatically. For an immediate run:

```bash
docker-compose exec api python -m market_data_backend_platform.etl.services.ingestion
```

Then check Grafana datasource: **Settings → Data Sources → Test**.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

_Last updated: 2026-02-22_
