# Roadmap — Market Data Frontend Platform

> **Branch:** `feature/frontend`
> **Phases:** 0–6 (v1 scope)

---

## Status Legend

| Symbol | Status      |
|--------|-------------|
| ✅     | Complete    |
| 🔄     | In progress |
| ⬜     | Pending     |
| ❌     | Blocked     |

---

## v1 — Core Dashboard

| Phase | Milestone                                 | Status | Commit scope                  |
|-------|-------------------------------------------|--------|-------------------------------|
| 0     | Docs scaffold (PRD, DEV_PLAN, QA, arch)   | ✅     | `docs(frontend):`             |
| 1     | Vite project init + toolchain             | ⬜     | `feat(frontend):`             |
| 2     | API client layer (`src/api/`)             | ⬜     | `feat(frontend):`             |
| 3     | Authentication (JWT, protected routes)    | ⬜     | `feat(frontend):`             |
| 4     | Instruments list (table, filters, CRUD)   | ⬜     | `feat(frontend):`             |
| 5     | Price chart (OHLCV candlestick)           | ⬜     | `feat(frontend):`             |
| 6     | Integration & QA (lint, coverage, build)  | ⬜     | `chore(frontend):`            |

---

## Phase Details

### Phase 0 — Docs scaffold ✅

- [x] `docs/PRD.md` — API contract + screen requirements
- [x] `docs/DEV_PLAN.md` — execution plan by phase
- [x] `docs/QA_PROTOCOL.md` — validation checklist
- [x] `docs/architecture.md` — component hierarchy + data flow
- [x] `docs/roadmap.md` — this file

### Phase 1 — Vite project setup ⬜

- [ ] `npm create vite@latest` with `--template react`
- [ ] Install runtime dependencies (TanStack Query, lightweight-charts, react-router-dom)
- [ ] Install dev dependencies (Vitest, RTL, ESLint, Prettier)
- [ ] Configure `vite.config.js` (Vitest + coverage threshold 80%)
- [ ] Configure `.eslintrc.js` and `.prettierrc`
- [ ] Add npm scripts (dev, build, lint, format:check, test)
- [ ] Create `nginx.conf` + `Dockerfile`
- [ ] Create `.env.example`

### Phase 2 — API client layer ⬜

- [ ] `src/api/client.js` — base fetch with auth header + error handling
- [ ] `src/api/auth.js` — login endpoint
- [ ] `src/api/instruments.js` — CRUD endpoints
- [ ] `src/api/prices.js` — OHLCV + latest price endpoints
- [ ] Unit tests for all `src/api/` modules (100% coverage target)

### Phase 3 — Authentication ⬜

- [ ] `src/hooks/useAuth.js` — login mutation, token storage, logout
- [ ] `src/components/LoginForm/` — form + test
- [ ] `src/pages/Login/` — login page
- [ ] `src/components/ProtectedRoute/` — token guard + test
- [ ] `src/main.jsx` — router setup (react-router-dom v6)

### Phase 4 — Instruments list ⬜

- [ ] `src/hooks/useInstruments.js` — TanStack Query list
- [ ] `src/hooks/useInstrumentMutations.js` — create/update/delete
- [ ] `src/components/InstrumentTable/` — table + test
- [ ] `src/components/InstrumentFilters/` — filter bar + test
- [ ] `src/components/InstrumentForm/` — create/edit modal + test
- [ ] `src/components/Pagination/` — skip/limit controls + test
- [ ] `src/pages/Instruments/` — page composition

### Phase 5 — Price chart ⬜

- [ ] `src/hooks/usePrices.js` — TanStack Query OHLCV list
- [ ] `src/hooks/useLatestPrice.js` — TanStack Query latest price
- [ ] `src/components/PriceChart/` — lightweight-charts wrapper + test
- [ ] `src/components/DateRangePicker/` — date inputs + test
- [ ] `src/components/LatestPriceSummary/` — summary card + test
- [ ] `src/pages/PriceView/` — page composition

### Phase 6 — Integration & QA ⬜

- [ ] Run full `QA_PROTOCOL.md` checklist
- [ ] Coverage ≥ 80% globally, 100% on `src/api/`
- [ ] `npm run build` → bundle size < 500 KB gzipped
- [ ] Smoke test against live backend (login → instruments → chart)
- [ ] Dockerfile smoke test (build + serve at port 80)

---

## v2 — Post-v1 (Out of Scope for Now)

| Feature                          | Priority |
|----------------------------------|----------|
| Real-time WebSocket price stream | High     |
| Dark mode                        | Medium   |
| Mobile-responsive layout         | Medium   |
| Ingest trigger from UI           | Low      |
| Grafana iframe embed             | Low      |
| User management (admin panel)    | Low      |
| TypeScript migration             | Low      |
