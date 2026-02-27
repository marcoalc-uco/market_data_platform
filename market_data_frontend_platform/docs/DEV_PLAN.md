# DEV_PLAN — Market Data Frontend Platform

> **Branch:** `feature/frontend`
> **Methodology:** TDD — RED → GREEN → REFACTOR
> **Commit convention:** `<type>(frontend): <description>`

---

## Phase Map

| Phase | Name                  | Status      |
|-------|-----------------------|-------------|
| 0     | Docs scaffold         | ✅ Complete  |
| 1     | Vite project setup    | ⬜ Pending   |
| 2     | API client layer      | ⬜ Pending   |
| 3     | Authentication        | ⬜ Pending   |
| 4     | Instruments list      | ⬜ Pending   |
| 5     | Price chart           | ⬜ Pending   |
| 6     | Integration & QA      | ⬜ Pending   |

---

## Phase 0 — Docs Scaffold ✅

**Goal:** Establish all planning documents before any code.

**Deliverables:**
- `docs/PRD.md` — product requirements + API contract
- `docs/DEV_PLAN.md` — this file
- `docs/QA_PROTOCOL.md` — validation checklist
- `docs/architecture.md` — component hierarchy + data flow
- `docs/roadmap.md` — milestones

**Commit:** `docs(frontend): add docs scaffold (PRD, DEV_PLAN, QA_PROTOCOL, architecture, roadmap)`

---

## Phase 1 — Vite Project Setup

**Goal:** Initialize the project, install all dependencies, verify toolchain.

**Steps:**

1. `npm create vite@latest . -- --template react` (inside `market_data_frontend_platform/`)
2. Install runtime dependencies:
   ```bash
   npm install @tanstack/react-query lightweight-charts react-router-dom
   ```
3. Install dev dependencies:
   ```bash
   npm install -D vitest @testing-library/react @testing-library/jest-dom \
     @testing-library/user-event jsdom \
     eslint eslint-plugin-react eslint-plugin-react-hooks \
     prettier @vitejs/plugin-react
   ```
4. Configure `vite.config.js`:
   - `@vitejs/plugin-react` plugin
   - Vitest `test` block: `environment: 'jsdom'`, `coverage.threshold: 80`
5. Create `.eslintrc.js` (extends `eslint:recommended` + `plugin:react/recommended`)
6. Create `.prettierrc` (singleQuote, semi: false, printWidth: 100)
7. Add npm scripts to `package.json`:
   ```json
   {
     "dev": "vite",
     "build": "vite build",
     "lint": "eslint src --ext .js,.jsx --max-warnings 0",
     "format:check": "prettier --check src",
     "format": "prettier --write src",
     "test": "vitest run --coverage",
     "test:watch": "vitest"
   }
   ```
8. Create `.env.example` with `VITE_API_URL=http://localhost:8000`
9. Create `nginx.conf` (SPA fallback: all routes → `index.html`)
10. Create `Dockerfile` (multi-stage: builder + production + development)

**Verification gate:**
- `npm run lint` → 0 errors
- `npm run build` → succeeds
- `npm test` → passes (no src files yet = 0 tests, coverage skip)

**Commit:** `feat(frontend): initialize Vite project with toolchain`

---

## Phase 2 — API Client Layer

**Goal:** Implement `src/api/` — the ONLY place `fetch()` is allowed.

**TDD cycle for each module:**

### 2.1 `src/api/client.js`

- Reads `VITE_API_URL` from `import.meta.env`
- Attaches `Authorization: Bearer <token>` header if token exists in `localStorage`
- Throws `Error(detail)` on non-OK responses
- Test: mock `fetch`, verify headers and error throwing

### 2.2 `src/api/auth.js`

```javascript
export const login = (credentials) =>
  apiClient.request('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(credentials) })
```

### 2.3 `src/api/instruments.js`

```javascript
export const getInstruments = (params) => apiClient.request('/api/v1/instruments?' + new URLSearchParams(params))
export const getInstrument = (id) => apiClient.request(`/api/v1/instruments/${id}`)
export const createInstrument = (data) => apiClient.request('/api/v1/instruments', { method: 'POST', body: JSON.stringify(data) })
export const updateInstrument = (id, data) => apiClient.request(`/api/v1/instruments/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteInstrument = (id) => apiClient.request(`/api/v1/instruments/${id}`, { method: 'DELETE' })
```

### 2.4 `src/api/prices.js`

```javascript
export const getPrices = (instrumentId, params) => apiClient.request(`/api/v1/prices/${instrumentId}?` + new URLSearchParams(params))
export const getLatestPrice = (instrumentId) => apiClient.request(`/api/v1/prices/${instrumentId}/latest`)
```

**Verification gate:**
- All `src/api/` modules have unit tests
- `npm test` coverage ≥ 80% on `src/api/`

**Commit:** `feat(frontend): add API client layer (client, auth, instruments, prices)`

---

## Phase 3 — Authentication

**Goal:** Login screen + protected routing + token lifecycle.

**Components/hooks to build (TDD):**

| File | Purpose |
|------|---------|
| `src/hooks/useAuth.js` | Login mutation, token storage, logout |
| `src/components/LoginForm/LoginForm.jsx` | Username + password form |
| `src/pages/Login/Login.jsx` | Login page |
| `src/components/ProtectedRoute/ProtectedRoute.jsx` | Redirects to `/login` if no token |
| `src/main.jsx` | Router setup (react-router-dom v6) |

**Routes:**
```
/login             → Login page (public)
/instruments       → Instruments list (protected)
/instruments/:id/prices → Price chart (protected)
*                  → redirect to /instruments
```

**Token expiry handling:**
- `src/api/client.js` intercepts 401 → clears `localStorage` → throws error
- `useAuth` listens for auth errors → redirects to `/login`

**Verification gate:**
- `npm test` — LoginForm renders, form validation, login error display all tested
- `npm run build` succeeds

**Commit:** `feat(frontend): add authentication (login form, JWT, protected routes)`

---

## Phase 4 — Instruments List

**Goal:** Screen 2 of PRD — list, filter, create, edit, delete instruments.

**Components/hooks to build (TDD):**

| File | Purpose |
|------|---------|
| `src/hooks/useInstruments.js` | TanStack Query wrapper for GET list |
| `src/hooks/useInstrumentMutations.js` | create / update / delete mutations |
| `src/components/InstrumentTable/InstrumentTable.jsx` | Table with symbol, name, type, status |
| `src/components/InstrumentFilters/InstrumentFilters.jsx` | asset_type select + is_active toggle |
| `src/components/InstrumentForm/InstrumentForm.jsx` | Create / edit form (modal) |
| `src/components/Pagination/Pagination.jsx` | skip/limit controls |
| `src/pages/Instruments/Instruments.jsx` | Composes all above |

**States required per component:**
- Loading skeleton (use `isLoading` from TanStack Query)
- Error state with "Retry" button (use `isError` + `refetch`)
- Empty state message when `data.length === 0`

**Verification gate:**
- All components have test files covering render, loading, error, empty states
- Coverage ≥ 80%
- `npm run lint` → 0 errors

**Commit:** `feat(frontend): add instruments list page (table, filters, CRUD)`

---

## Phase 5 — Price Chart

**Goal:** Screen 3 of PRD — OHLCV candlestick chart for a single instrument.

**Components/hooks to build (TDD):**

| File | Purpose |
|------|---------|
| `src/hooks/usePrices.js` | TanStack Query for GET prices list |
| `src/hooks/useLatestPrice.js` | TanStack Query for GET latest price |
| `src/components/PriceChart/PriceChart.jsx` | lightweight-charts candlestick wrapper |
| `src/components/DateRangePicker/DateRangePicker.jsx` | start_date / end_date inputs |
| `src/components/LatestPriceSummary/LatestPriceSummary.jsx` | close, timestamp, volume |
| `src/pages/PriceView/PriceView.jsx` | Composes chart + pickers + summary |

**Chart integration notes:**
- `lightweight-charts` requires a DOM element ref — use `useRef` + `useEffect` for chart lifecycle only (not data fetching)
- Data from TanStack Query feeds the chart series; on data change call `series.setData()`
- Mock `lightweight-charts` in tests (it requires a real DOM with canvas)

**Verification gate:**
- PriceChart unit test mocks `lightweight-charts` and verifies container renders
- Date picker inputs update query params
- Coverage ≥ 80%

**Commit:** `feat(frontend): add price chart page (OHLCV candlestick, date range picker)`

---

## Phase 6 — Integration & QA

**Goal:** End-to-end validation, polish, and production readiness.

**Steps:**

1. Run full QA checklist from `docs/QA_PROTOCOL.md`
2. Verify `npm run build` output (bundle size, no console errors)
3. Smoke test against live backend: login → instruments list → price chart
4. Fix any remaining lint / coverage gaps
5. Verify Dockerfile builds and serves app at port 80
6. Review `AGENT.md` checklist (§7)

**Commit:** `chore(frontend): QA pass — lint clean, coverage ≥ 80%, build verified`

---

## Commit Log Template

```
feat(frontend): <description>       # new feature
fix(frontend): <description>        # bug fix
test(frontend): <description>       # tests only
chore(frontend): <description>      # tooling, config
docs(frontend): <description>       # documentation
refactor(frontend): <description>   # refactor, no behavior change
style(frontend): <description>      # formatting only
```
