# Grafana Visualization Guide

## Overview

This guide explains how to use Grafana to visualize market data from the Market Data Backend Platform. The dashboard provides real-time insights into price evolution, trading volumes, and latest market prices grouped by asset type.

---

## Dashboard Access

Once the Docker Compose environment is running:

1. Open your browser and navigate to: `http://localhost:3000`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin` (change this in production!)
3. Navigate to **Dashboards** → **Market Data - Multi-Instrument by Asset Type**

---

## Dashboard Overview

### Main Dashboard: Market Data - Multi-Instrument by Asset Type

The dashboard displays OHLCV candlestick charts and volume bars for one or more instruments, filtered by asset type. It uses two linked dropdown variables:

| Variable        | Label      | Description                                                                                  |
| --------------- | ---------- | -------------------------------------------------------------------------------------------- |
| `${asset_type}` | Asset Type | Selects the instrument type (`crypto`, `index`, `stock`). Populated dynamically from the DB. |
| `${symbol}`     | Symbol     | Multi-select of symbols belonging to the selected asset type.                                |

**Dashboard features:**

- **Candlestick chart** — OHLCV price evolution
- **Volume bar chart** — Trading volume over time
- **Latest prices table** — Most recent OHLCV snapshot per instrument
- **Time range picker** — Adjust the analysis window
- **Auto-cross-filter** — Selecting an asset type refreshes the symbol list automatically

---

## Dashboard Panels

### 1. Price Candlesticks — `${symbol}`

**Type**: Candlestick chart
**Description**: Displays OHLCV candlestick price evolution for the selected symbol(s). Candles are green for up-days and red for down-days.

**SQL Query (from market_data.json):**

```sql
SELECT
  mp.timestamp AS time,
  mp.open,
  mp.high,
  mp.low,
  mp.close,
  i.symbol AS metric
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE
  i.symbol IN ($symbol)
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
ORDER BY mp.timestamp ASC
```

---

### 2. Trading Volume — `${symbol}`

**Type**: Bar chart (time series)
**Description**: Shows trading volume for the selected symbol(s) over the selected time range.

**SQL Query (from market_data.json):**

```sql
SELECT
  mp.timestamp AS time,
  mp.volume AS value,
  i.symbol AS metric
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE
  i.symbol IN ($symbol)
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
ORDER BY mp.timestamp ASC
```

---

### 3. Latest Prices — `${symbol}`

**Type**: Table
**Description**: Displays the most recent OHLCV snapshot for each selected instrument. The `close` column is color-coded. Sorted by timestamp descending.

**Columns:** symbol, name, instrument_type, timestamp, open, high, low, close (€, color-coded), volume

**SQL Query (from market_data.json):**

```sql
SELECT
  i.symbol,
  i.name,
  i.instrument_type,
  mp.timestamp,
  mp.open,
  mp.high,
  mp.low,
  mp.close,
  mp.volume
FROM instruments i
JOIN LATERAL (
  SELECT *
  FROM market_prices
  WHERE instrument_id = i.id
  ORDER BY timestamp DESC
  LIMIT 1
) mp ON true
WHERE i.symbol IN ($symbol)
ORDER BY mp.timestamp DESC
```

---

## Using the Dashboard

### Step 1 — Select Asset Type

1. Use the **Asset Type** dropdown at the top to pick `crypto`, `index`, or `stock`
2. The **Symbol** dropdown will automatically refresh and show only symbols of that type

### Step 2 — Select Symbol(s)

- The **Symbol** dropdown supports **multi-select** — pick one or more instruments to compare
- Selecting **All** shows data for all symbols of the chosen asset type

### Adjusting Time Range

1. Click the **time picker** in the top-right corner
2. Select a preset range (Last 7 days, Last 30 days, etc.) or define a custom range
3. All panels update automatically

### Zooming and Panning

- **Zoom**: Click and drag horizontally on any chart
- **Reset Zoom**: Double-click on the chart
- **Pan**: Hold Shift and drag

---

## Customizing the Dashboard

### Editing Panels

1. Click the panel title → **Edit**
2. Modify the query, visualization settings, or display options
3. Click **Apply** to save changes

### Adding New Panels

1. Click **Add panel** in the dashboard toolbar
2. Select **Add a new panel**
3. Configure the data source (PostgreSQL) and query
4. Choose visualization type and configure display options
5. Click **Apply** to add to dashboard

### Creating New Dashboards

1. Navigate to **Dashboards** → **New Dashboard**
2. Add panels as needed
3. Save with a descriptive name
4. Optionally, export as JSON and save to `docker/grafana/dashboards/` for version control

---

## Dashboard Template Variables

The dashboard uses two linked Grafana query variables:

### `${asset_type}` — Asset Type

Populates the first dropdown dynamically from the DB:

```sql
SELECT DISTINCT instrument_type FROM instruments ORDER BY instrument_type
```

### `${symbol}` — Symbol (multi-select)

Filters symbols based on the selected asset type:

```sql
SELECT symbol FROM instruments WHERE instrument_type = '${asset_type}' ORDER BY symbol
```

All three dashboard panels filter on `i.symbol IN ($symbol)`.

---

## Troubleshooting

### Dashboard Shows "No Data"

**Possible Causes:**

1. No data in database for selected asset type
2. Time range doesn't match available data
3. PostgreSQL datasource not connected

**Solutions:**

1. Check if instruments exist: `docker-compose exec postgres psql -U market_data -d market_data -c "SELECT * FROM instruments;"`
2. Verify data exists: `docker-compose exec postgres psql -U market_data -d market_data -c "SELECT COUNT(*) FROM market_prices;"`
3. Run ETL ingestion: `docker-compose exec api python -m market_data_backend_platform.etl.services.ingestion`
4. Check datasource connection: **Settings** → **Data Sources** → **PostgreSQL** → **Save & Test**

### Datasource Connection Failed

**Error**: "Database connection failed"

**Solutions:**

1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check credentials in `docker/grafana/provisioning/datasources/postgres.yml`
3. Ensure services are on the same Docker network
4. Restart Grafana: `docker-compose restart grafana`

### Dashboard Not Loading

**Solutions:**

1. Check Grafana logs: `docker-compose logs grafana`
2. Verify dashboard JSON is valid
3. Re-provision: `docker-compose restart grafana`

---

## Performance Optimization

### For Large Datasets

1. **Use Time-Based Aggregation**:

   ```sql
   SELECT
     DATE_TRUNC('hour', timestamp) AS time,
     AVG(close) AS value
   FROM market_prices
   GROUP BY time
   ORDER BY time
   ```

2. **Limit Data Points**: Add `LIMIT` clause to queries

3. **Use Indexes**: Ensure composite index exists on `(instrument_id, timestamp)`

4. **Consider TimescaleDB**: For production, migrate to TimescaleDB for better time-series performance

---

## Exporting Dashboards

### Export as JSON

1. Open the dashboard
2. Click **Dashboard settings** (gear icon)
3. Select **JSON Model**
4. Copy JSON and save to `docker/grafana/dashboards/`
5. Commit to Git for version control

### Export as PDF/PNG

1. Open the dashboard
2. Click **Share** → **Export**
3. Select format (PDF, PNG)
4. Configure options and download

---

## Security Considerations

### Production Deployment

1. **Change Default Credentials**:
   - Update `GRAFANA_ADMIN_PASSWORD` in `.env`
   - Use strong passwords

2. **Enable HTTPS**:
   - Configure reverse proxy (nginx, Traefik)
   - Use SSL certificates

3. **Restrict Database Access**:
   - Create read-only PostgreSQL user for Grafana
   - Grant only SELECT permissions

4. **Enable Authentication**:
   - Configure OAuth, LDAP, or SAML
   - Disable anonymous access

---

## Additional Resources

- **Grafana Documentation**: https://grafana.com/docs/
- **PostgreSQL Data Source**: https://grafana.com/docs/grafana/latest/datasources/postgres/
- **Dashboard Best Practices**: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/

---

**Version**: 2.0
**Last Updated**: 2026-02-22
**Related**: [architecture.md](./architecture.md) — [roadmap.md](./roadmap.md)
