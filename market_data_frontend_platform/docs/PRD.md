# PRD — Market Data Frontend Platform

> **Scope:** React/Vite frontend that consumes the `market_data_backend_platform` REST API.
> **Version:** 1.0
> **Stack:** React 18 · Vite 5 · JavaScript (ES6+) · TanStack Query v5 · lightweight-charts · CSS Modules

---

## 1. Overview

The frontend is a Single-Page Application (SPA) that provides a dashboard for viewing and managing market instruments and their OHLCV price history. It connects exclusively to the FastAPI backend via REST/JSON.

---

## 2. Backend API Contract (Source of Truth)

The OpenAPI spec at `GET /openapi.json` is the authoritative contract.
Frontend code MUST NOT hardcode field names or paths that differ from the spec.

### 2.1 Authentication

| Method | Path                    | Description         | Auth Required |
|--------|-------------------------|---------------------|---------------|
| POST   | `/api/v1/auth/login`    | Obtain JWT token    | No            |

**Request body:**
```json
{ "username": "string", "password": "string" }
```
**Response:**
```json
{ "access_token": "string", "token_type": "bearer" }
```
Token is stored in `localStorage` as `access_token`.

### 2.2 Instruments

| Method | Path                          | Description               | Auth Required |
|--------|-------------------------------|---------------------------|---------------|
| GET    | `/api/v1/instruments`         | List instruments          | Yes           |
| GET    | `/api/v1/instruments/{id}`    | Get single instrument     | Yes           |
| POST   | `/api/v1/instruments`         | Create instrument (201)   | Yes           |
| PUT    | `/api/v1/instruments/{id}`    | Update instrument         | Yes           |
| DELETE | `/api/v1/instruments/{id}`    | Delete instrument (204)   | Yes           |

**Query params (list):** `asset_type`, `is_active`, `skip`, `limit`

**Instrument schema:**
```json
{
  "id": "integer",
  "symbol": "string",
  "name": "string",
  "asset_type": "string",
  "is_active": "boolean"
}
```

### 2.3 Prices

| Method | Path                                        | Description               | Auth Required |
|--------|---------------------------------------------|---------------------------|---------------|
| GET    | `/api/v1/prices/{instrument_id}`            | List OHLCV prices         | Yes           |
| GET    | `/api/v1/prices/{instrument_id}/latest`     | Latest price record       | Yes           |

**Query params (list):** `start_date`, `end_date`, `skip`, `limit`

**Price schema (OHLCV):**
```json
{
  "id": "integer",
  "instrument_id": "integer",
  "timestamp": "string (ISO 8601)",
  "open": "number",
  "high": "number",
  "low": "number",
  "close": "number",
  "volume": "number"
}
```

### 2.4 Health

| Method | Path      | Description              | Auth Required |
|--------|-----------|--------------------------|---------------|
| GET    | `/health` | Backend health check     | No            |

---

## 3. Screens

### Screen 1 — Login (`/login`)

**Purpose:** Authenticate the user and obtain a JWT token.

**Requirements:**
- Form: `username` (text input) + `password` (password input) + Submit button
- On success: store `access_token` in `localStorage`, redirect to `/instruments`
- On error: display `detail` field from error response (e.g., "Invalid credentials")
- If a token already exists and is valid: redirect directly to `/instruments`
- No "Remember me" toggle in v1

### Screen 2 — Instruments List (`/instruments`)

**Purpose:** View, filter, and navigate to instruments.

**Requirements:**
- Table/list of instruments: `symbol`, `name`, `asset_type`, `is_active`
- Filter bar: `asset_type` (select) + `is_active` (toggle/checkbox)
- Click on instrument row → navigate to `/instruments/{id}/prices`
- "Add instrument" button → opens creation form (modal or inline)
- Creation form fields: `symbol`, `name`, `asset_type`, `is_active` (boolean)
- Edit / delete actions per row
- Pagination: `skip` + `limit` (default limit = 20)
- Loading skeleton while fetching
- Empty state message when list is empty
- Error state with retry option

### Screen 3 — Price Chart (`/instruments/{id}/prices`)

**Purpose:** Display OHLCV candlestick chart for a single instrument.

**Requirements:**
- Instrument header: `symbol` + `name` + `asset_type` badge
- Date range picker: `start_date` / `end_date` (ISO 8601 strings sent to API)
- Candlestick chart via `lightweight-charts`:
  - X-axis: timestamp
  - Candlesticks: open, high, low, close
  - Volume bars overlay (optional v1 scope)
- "Latest price" summary: close, timestamp, volume
- Loading state during fetch
- Error state with retry
- Back button → `/instruments`

---

## 4. Non-Functional Requirements

| Requirement        | Target                                              |
|--------------------|-----------------------------------------------------|
| Test coverage      | ≥ 80% (Vitest)                                      |
| Build              | `npm run build` must produce zero errors            |
| Linting            | `npm run lint` → 0 ESLint errors, 0 Prettier issues |
| Bundle size        | < 500 KB gzipped (initial load)                     |
| API error handling | ALL errors surfaced to user; no silent swallows     |
| Token expiry       | Redirect to `/login` on 401 response                |
| Env config         | All API base URL via `VITE_API_URL`; no hardcoding  |

---

## 5. Out of Scope (v1)

- Real-time WebSocket price streaming
- User registration / password reset
- Dark mode
- Mobile-specific layout (responsive is nice-to-have, not required)
- Instrument data ingestion trigger from UI
- Grafana embedding

---

## 6. Acceptance Criteria (Definition of Done)

A feature is done when:

1. `npm run lint` passes with 0 errors
2. `npm run build` succeeds
3. `npm test` passes with coverage ≥ 80%
4. All screens render correctly with mocked API responses
5. All screens handle loading, error, and empty states
6. No `fetch()` calls outside `src/api/`
7. No `console.log` in production code
8. Component has JSDoc on public props
