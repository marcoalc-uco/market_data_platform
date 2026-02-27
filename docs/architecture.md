# System Architecture — Market Data Platform

> **Scope:** Full-system view (monorepo root).
> Service-level architecture is documented in each service's own `docs/architecture.md`.

---

## Services Overview

```
┌─────────────────────────────────────────────┐
│                   Browser                    │
└──────────────────────┬──────────────────────┘
                       │ :5173 (prod → Nginx :80)
              ┌────────▼────────┐
              │    frontend     │  React 18 + Vite → Nginx (Alpine)
              │  market_data_   │  CSS Modules · TanStack Query
              │  frontend_      │  lightweight-charts (OHLCV)
              │  platform/      │
              └────────┬────────┘
                       │ HTTP :8000  (VITE_API_URL)
              ┌────────▼────────┐
              │      api        │  FastAPI + Uvicorn (Python 3.14)
              │  market_data_   │  JWT Auth · Alembic · APScheduler
              │  backend_       │  ETL: Yahoo Finance → PostgreSQL
              │  platform/      │
              └────────┬────────┘
                       │ :5432
              ┌────────▼────────┐
              │    postgres     │  PostgreSQL 16
              │                 │  TimescaleDB-ready schema
              └────────┬────────┘
                       │ direct read
              ┌────────▼────────┐
              │    grafana      │  Grafana 11 — Dashboards :3000
              └─────────────────┘
```

---

## Directory Structure

```
market_data_platform/                ← Monorepo root
├── market_data_backend_platform/    ← Python/FastAPI service
├── market_data_frontend_platform/   ← React/Vite/JS service
├── docs/                            ← This file (full-system view)
├── tests/e2e/                       ← Playwright end-to-end tests
├── docker-compose.yml               ← Production-like orchestration
├── docker-compose.dev.yml           ← Development hot-reload overrides
├── .env.example                     ← Shared environment template
├── Makefile                         ← Root automation (delegates to services)
└── AGENT.md                         ← AI agent monorepo standards
```

---

## API Contract

- **Source of truth:** `http://localhost:8000/openapi.json`
- **Swagger UI:** `http://localhost:8000/docs`
- Frontend communicates **exclusively** through `market_data_frontend_platform/src/api/`

## Service URLs

| Service     | URL                        | Notes            |
| ----------- | -------------------------- | ---------------- |
| Frontend    | http://localhost:5173      | Dev (Vite)       |
| Frontend    | http://localhost:80        | Prod (Nginx)     |
| Backend API | http://localhost:8000      | FastAPI          |
| API Docs    | http://localhost:8000/docs | Swagger UI       |
| Grafana     | http://localhost:3000      | admin/admin      |
| PostgreSQL  | localhost:5432             | market_data DB   |
