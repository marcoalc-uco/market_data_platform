# Backend DEV_PLAN

## Active Tasks

- **[IN PROGRESS] Phase 6 — Grafana Visualization**
  - Configure PostgreSQL datasource via Grafana container.
  - Query test: `SELECT timestamp, close FROM market_prices WHERE instrument_id = 1`.
  - Export dashboards to `docs/grafana/dashboards/`.

## Next Immediate Action Items

1. Start Grafana: `docker-compose up -d grafana`.
2. Connect Grafana to `postgres:5432` with user `postgres`, db `market_data`.
3. Create generic Time-Series evolution dashboard.
4. Export Grafana configuration JSON to version control.

## Blockers

- Pending validation of Grafana PostgreSQL read connectivity from compose network.
