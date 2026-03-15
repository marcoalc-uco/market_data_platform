# Architecture — Market Data Frontend Platform

> **Stack:** React 18 · Vite 5 · JavaScript ES6+ · TanStack Query v5 · CSS Modules
> **Pattern:** Component composition · Custom hooks · API layer isolation

---

## 1. Directory Structure

```
market_data_frontend_platform/
├── src/
│   ├── api/                        ← HTTP layer (ONLY place with fetch calls)
│   │   ├── client.js               ← Base fetch client (auth headers, error handling)
│   │   ├── auth.js                 ← POST /api/v1/auth/login
│   │   ├── instruments.js          ← GET/POST/PUT/DELETE /api/v1/instruments
│   │   └── prices.js               ← GET /api/v1/prices/{id}
│   │
│   ├── hooks/                      ← Custom React hooks (data + UI logic)
│   │   ├── useAuth.js              ← Login mutation, token, logout
│   │   ├── useInstruments.js       ← TanStack Query: list instruments
│   │   ├── useInstrumentMutations.js  ← create / update / delete
│   │   ├── usePrices.js            ← TanStack Query: OHLCV list
│   │   └── useLatestPrice.js       ← TanStack Query: latest price
│   │
│   ├── components/                 ← Stateless, reusable UI components
│   │   ├── LoginForm/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── LoginForm.module.css
│   │   │   └── LoginForm.test.jsx
│   │   ├── InstrumentTable/
│   │   │   ├── InstrumentTable.jsx
│   │   │   ├── InstrumentTable.module.css
│   │   │   └── InstrumentTable.test.jsx
│   │   ├── InstrumentFilters/
│   │   │   ├── InstrumentFilters.jsx
│   │   │   ├── InstrumentFilters.module.css
│   │   │   └── InstrumentFilters.test.jsx
│   │   ├── InstrumentForm/
│   │   │   ├── InstrumentForm.jsx
│   │   │   ├── InstrumentForm.module.css
│   │   │   └── InstrumentForm.test.jsx
│   │   ├── PriceChart/
│   │   │   ├── PriceChart.jsx
│   │   │   ├── PriceChart.module.css
│   │   │   └── PriceChart.test.jsx
│   │   ├── DateRangePicker/
│   │   │   ├── DateRangePicker.jsx
│   │   │   ├── DateRangePicker.module.css
│   │   │   └── DateRangePicker.test.jsx
│   │   ├── LatestPriceSummary/
│   │   │   ├── LatestPriceSummary.jsx
│   │   │   ├── LatestPriceSummary.module.css
│   │   │   └── LatestPriceSummary.test.jsx
│   │   ├── Pagination/
│   │   │   ├── Pagination.jsx
│   │   │   ├── Pagination.module.css
│   │   │   └── Pagination.test.jsx
│   │   └── ProtectedRoute/
│   │       ├── ProtectedRoute.jsx
│   │       └── ProtectedRoute.test.jsx
│   │
│   ├── pages/                      ← Route-level components (compose components)
│   │   ├── Login/
│   │   │   ├── Login.jsx
│   │   │   └── Login.module.css
│   │   ├── Instruments/
│   │   │   ├── Instruments.jsx
│   │   │   └── Instruments.module.css
│   │   └── PriceView/
│   │       ├── PriceView.jsx
│   │       └── PriceView.module.css
│   │
│   ├── App.jsx                     ← Root component (Router, QueryClientProvider)
│   ├── App.module.css              ← Root-level layout styles
│   └── main.jsx                    ← Entry: React root mount
│
├── tests/                          ← Test utilities and setup
├── docs/                           ← PRD, QA protocol, architecture
├── Dockerfile                      ← Multi-stage: builder + production (Nginx) + development
├── nginx.conf                      ← SPA fallback: all routes → index.html
├── package.json
├── vite.config.js
├── .eslintrc.js
├── .prettierrc
├── .env.example
└── AGENT.md
```

---

## 2. Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Browser                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Pages (Route Components)              │   │
│  │   Login   │   Instruments   │   PriceView                │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │ compose                                    │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │                  Components (Reusable UI)                  │   │
│  │  LoginForm │ InstrumentTable │ PriceChart │ DatePicker …  │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │ use                                        │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │              Custom Hooks (Data + UI Logic)                │   │
│  │  useAuth │ useInstruments │ usePrices │ useLatestPrice …  │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │ call                                       │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │              TanStack Query v5 (Cache Layer)               │   │
│  │         staleTime · background refetch · mutations         │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │ invoke                                     │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │              src/api/ (HTTP Layer — ONLY fetch here)       │   │
│  │  client.js │ auth.js │ instruments.js │ prices.js          │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │ HTTP/JSON                                  │
└─────────────────────┼───────────────────────────────────────────┘
                      │
              ┌───────▼────────┐
              │  FastAPI (8000) │
              │  /api/v1/*      │
              └────────────────┘
```

---

## 3. Data Flow

### 3.1 Authentication flow

```
User fills LoginForm
  → LoginForm calls useAuth.login(credentials)
    → useAuth calls api/auth.login(credentials)
      → POST /api/v1/auth/login
        ← { access_token, token_type }
      → localStorage.setItem('access_token', token)
      → navigate('/instruments')
```

### 3.2 Protected route flow

```
Browser navigates to /instruments
  → ProtectedRoute checks localStorage.getItem('access_token')
    ├── token exists → render Instruments page
    └── no token → navigate('/login')
```

### 3.3 401 intercept flow

```
Any API call
  → client.js attaches Authorization header
    ← HTTP 401
      → client.js throws Error('HTTP 401')
        → TanStack Query sets isError=true
          → component renders error state
            → user clicks "Log out" / "Retry login"
              → navigate('/login')
```

### 3.4 Instruments list flow

```
Instruments page mounts
  → useInstruments({ asset_type, is_active, skip, limit })
    → TanStack Query checks cache (queryKey = ['instruments', filters])
      ├── cache hit + fresh → return cached data
      └── cache miss / stale → call api/instruments.getInstruments(params)
            → GET /api/v1/instruments?...
              ← [{ id, symbol, name, asset_type, is_active }, ...]
            → update cache
  → InstrumentTable renders rows
```

### 3.5 Price chart flow

```
PriceView mounts with instrumentId from URL params
  → usePrices(instrumentId, { start_date, end_date })
    → GET /api/v1/prices/{instrumentId}?start_date=&end_date=
      ← [{ timestamp, open, high, low, close, volume }, ...]
  → PriceChart receives data prop
    → lightweight-charts series.setData(data)
```

---

## 4. State Management

| State type            | Managed by                    | Location              |
|-----------------------|-------------------------------|-----------------------|
| Server state (remote) | TanStack Query                | hooks/                |
| Authentication token  | localStorage + useAuth        | hooks/useAuth.js      |
| Filter/UI state       | React `useState` in page      | pages/                |
| Chart lifecycle       | `useRef` + `useEffect`        | PriceChart component  |
| Form state            | React `useState` in form      | components/           |

---

## 5. Routing

```
/                    → redirect to /instruments
/login               → Login page (public)
/instruments         → Instruments list (protected)
/instruments/:id/prices  → PriceView (protected)
*                    → redirect to /instruments
```

**Router:** `react-router-dom` v6 (declarative `<Routes>/<Route>`)
**Guard:** `<ProtectedRoute>` wrapper checks token presence

---

## 6. Environment

| Variable         | Used in              | Default (dev)            |
|-----------------|----------------------|--------------------------|
| `VITE_API_URL`  | `src/api/client.js`  | `http://localhost:8000`  |

Injected at build time by Vite. Never call `process.env` — always `import.meta.env.VITE_*`.

---

## 7. Production Deployment

```
Docker multi-stage build:
  Stage 1 (builder):  node:20-alpine → npm ci → npm run build → /app/dist
  Stage 2 (prod):     nginx:alpine   → COPY dist → port 80

nginx.conf:
  - SPA fallback: try_files $uri /index.html
  - Upstream proxy for /api/* → http://api:8000 (optional; usually handled by docker network)
```

In docker-compose.yml:
- `frontend` container → port `80:80`
- `api` container → port `8000:8000`
- Both on `platform` bridge network
