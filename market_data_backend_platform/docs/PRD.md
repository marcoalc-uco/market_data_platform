# Backend PRD

## Features & Contracts

1. **Instruments API**
   - Endpoints: `GET /api/v1/instruments`, `GET .../{id}`, `POST /api/v1/instruments`, `PUT .../{id}`, `DELETE .../{id}`.
   - Model: `symbol` (unique), `name`, `asset_type` (STOCK, INDEX, CRYPTO), `is_active`.
2. **Market Prices API**
   - Endpoints: `GET /api/v1/prices/{instrument_id}`, `GET .../latest`
   - Model: `timestamp`, `open`, `high`, `low`, `close`, `volume`. Constraint: `high >= low`.
3. **Ingestion ETL**
   - Flow: Yahoo Finance -> normalized -> saved.
   - Endpoint: `POST /api/v1/ingest/run` handling manual triggers with idempotent logic (ON CONFLICT DO NOTHING).

## Out of Scope

- Automated APScheduler scheduling (currently manual trigger only).
- Real-time WebSocket streaming.
- Alternative data sources (Alpha Vantage, CoinGecko).
