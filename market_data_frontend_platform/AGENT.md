# AGENT.md - AI Agent Instructions (Frontend)

> **Operational Context:** Act as a Senior Frontend Engineer specialized in React. Your absolute priority is component composability, clear data-flow, and testability. Reject quick solutions if they compromise technical debt.

> **Location:** This file is at `market_data_frontend_platform/` root and is **tool-agnostic** (works with Claude Code, Antigravity, Aider, Cursor, etc.)

> **Scope:** Frontend-specific standards. For monorepo orchestration see `/AGENT.md`.

---

## 0. Document Hierarchy

**Read in this order:**

1. **`/AGENT.md`** (monorepo root) — Cross-service conventions, API contract, docker-compose
2. **`/market_data_frontend_platform/AGENT.md`** (this file) — Frontend code standards
3. **`/market_data_frontend_platform/docs/PRD.md`** — What to build (features, screens)
4. **`/market_data_frontend_platform/docs/DEV_PLAN.md`** — Execution plan by phases

**Rule:** If this file contradicts the monorepo `/AGENT.md`, **STOP** and request clarification.

---

## 1. Stack (Non-Negotiable)

| Layer         | Technology          | Purpose                              |
| ------------- | ------------------- | ------------------------------------ |
| Framework     | React 18+           | UI component model (hooks-first)     |
| Build tool    | Vite 5+             | Dev server + production build        |
| Language      | JavaScript (ES6+)   | No TypeScript (for now)              |
| Styling       | CSS Modules         | Scoped styles per component          |
| HTTP Client   | fetch (native)      | No axios unless explicitly justified |
| Server state  | TanStack Query v5   | Cache + background refetch           |
| Charts        | lightweight-charts  | OHLCV candlestick (TradingView lib)  |
| Linting       | ESLint + Prettier   | Code quality (equivalent to ruff)    |
| Testing       | Vitest + RTL        | Unit + component tests               |
| Container     | Nginx (Alpine)      | Serves static build in prod          |

---

## 2. Directory Structure (Canonical)

```
market_data_frontend_platform/
├── src/
│   ├── api/                    ← HTTP client layer (ONLY place with fetch calls)
│   │   ├── client.js           ← Base fetch client (auth headers, base URL, error handling)
│   │   ├── instruments.js      ← Instrument endpoints
│   │   ├── prices.js           ← Price / OHLCV endpoints
│   │   └── auth.js             ← JWT login, token storage
│   │
│   ├── components/             ← Reusable, stateless UI components
│   │   └── <ComponentName>/
│   │       ├── ComponentName.jsx
│   │       └── ComponentName.module.css
│   │
│   ├── pages/                  ← Route-level components (compose components)
│   │   └── <PageName>/
│   │       ├── PageName.jsx
│   │       └── PageName.module.css
│   │
│   ├── hooks/                  ← Custom React hooks (data fetching, UI logic)
│   │   └── use<HookName>.js
│   │
│   ├── assets/                 ← Static images, fonts, icons
│   ├── test/
│   │   ├── setup.js            ← Vitest global setup (@testing-library/jest-dom)
│   │   └── testUtils.jsx       ← renderWithProviders (QueryClient + MemoryRouter)
│   └── main.jsx                ← Entry point (React root, router)
│
├── tests/                      ← All tests (mirrors src/ structure, like backend)
│   └── unit/
│       ├── api/                ← Tests for src/api/
│       ├── components/         ← Tests for src/components/
│       └── hooks/              ← Tests for src/hooks/
│
├── public/                     ← Static files served as-is
├── Dockerfile                  ← Multi-stage: builder (Vite) + production (Nginx) + development
├── nginx.conf                  ← Nginx config for SPA (all routes → index.html)
├── package.json
├── vite.config.js
├── .eslintrc.cjs               ← ESLint config (CommonJS, required for ESLint 8 + type:module)
├── .prettierrc
├── .env.example                ← VITE_API_URL only
└── AGENT.md                    ← This file
```

---

## 3. API Layer — Golden Rule

**NEVER** call `fetch()` directly from components, pages, or hooks.

**ALL** HTTP calls go through `src/api/`:

```javascript
// ✅ CORRECT — in a hook or component
import { getInstruments } from '../api/instruments'

// ❌ FORBIDDEN — direct fetch in component
const res = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/instruments`)
```

### `src/api/client.js` — Base client pattern

```javascript
// src/api/client.js
const BASE_URL = import.meta.env.VITE_API_URL

async function request(path, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  }
  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail ?? `HTTP ${response.status}`)
  }
  return response.json()
}

export const apiClient = { request }
```

### API module pattern

```javascript
// src/api/instruments.js
import { apiClient } from './client'

export const getInstruments = () =>
  apiClient.request('/api/v1/instruments')

export const createInstrument = (data) =>
  apiClient.request('/api/v1/instruments', { method: 'POST', body: JSON.stringify(data) })
```

---

## 4. Code Standards

### A. Component Conventions

- **One component per file**, named identically to the file: `PriceChart.jsx` → `export default PriceChart`
- **Functional components only** — no class components
- **Props destructured** in function signature
- **JSDoc** for public components:

```javascript
/**
 * Candlestick chart for OHLCV price data.
 *
 * @param {Object} props
 * @param {string} props.symbol - Instrument symbol (e.g. "AAPL")
 * @param {Array}  props.data   - Array of { time, open, high, low, close, volume }
 */
export default function PriceChart({ symbol, data }) { ... }
```

### B. Custom Hooks

- Prefix: `use` (e.g., `useInstruments`, `usePrices`)
- Return consistent shape: `{ data, isLoading, error }`
- Use **TanStack Query** for all server state:

```javascript
// src/hooks/useInstruments.js
import { useQuery } from '@tanstack/react-query'
import { getInstruments } from '../api/instruments'

export function useInstruments() {
  return useQuery({
    queryKey: ['instruments'],
    queryFn: getInstruments,
    staleTime: 5 * 60 * 1000, // 5 min
  })
}
```

### C. CSS Modules

```javascript
// ComponentName.jsx
import styles from './ComponentName.module.css'

export default function ComponentName() {
  return <div className={styles.container}>...</div>
}
```

- **No inline styles** except for dynamic values (chart dimensions)
- **No global CSS** except `src/index.css` for CSS variables and resets

### D. Environment Variables

- **ALL** env vars must start with `VITE_` (Vite security requirement)
- Access via `import.meta.env.VITE_*` (never `process.env`)
- Only `VITE_API_URL` is needed for the API client

---

## 5. Test-Driven Development (TDD)

### Mandatory cycle (matching backend §6)

```
RED:    Write FAILING test with Vitest + RTL
  ↓
GREEN:  Minimum component/hook code that passes
  ↓
REFACTOR: Improve without breaking tests
  ↓
REPEAT
```

### Test structure

```javascript
// src/components/PriceChart/PriceChart.test.jsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import PriceChart from './PriceChart'

describe('PriceChart', () => {
  it('renders chart container with symbol label', () => {
    render(<PriceChart symbol="AAPL" data={[]} />)
    expect(screen.getByText('AAPL')).toBeInTheDocument()
  })
})
```

### Minimum coverage

- **Target:** 80% (Vitest coverage)
- **Configured in:** `vite.config.js`

---

## 6. Dockerfile (Multi-stage)

```dockerfile
# market_data_frontend_platform/Dockerfile

# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build                    # Output: /app/dist

# ── Stage 2: Production (Nginx) ─────────────────────────────────────────────
FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# ── Stage 3: Development (Vite dev server) ──────────────────────────────────
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

---

## 7. Pre-Commit Checklist

- [ ] `npm run lint` → 0 ESLint errors, 0 Prettier issues
- [ ] `npm test` → all tests pass
- [ ] `npm run build` → build succeeds (no TypeScript/Vite errors)
- [ ] No `console.log` in production code (use structured logging if needed)
- [ ] No `fetch()` outside `src/api/`
- [ ] All new components have at least one test

---

## 8. Critical Restrictions (Guardrails)

1. **❌ No TypeScript** — keep JS (ES6+) for now; do not add `.ts`/`.tsx` files
2. **❌ No axios** — use native `fetch` through `src/api/client.js`
3. **❌ No class components** — functional components + hooks only
4. **❌ No `useEffect` for data fetching** — use TanStack Query
5. **❌ No inline styles** for static values — use CSS Modules
6. **❌ No hardcoded API URLs** in components — always `VITE_API_URL` via `src/api/`
7. **❌ No direct `fetch()` in components** — always through `src/api/` layer

---

## 9. Conflict Handling

If a user instruction contradicts this AGENT.md, use the warning template:

```
⚠️  WARNING: Technical Risk Detected

The proposed solution violates [PRINCIPLE X] because [REASON].

RISKS:
- Short-term: [Immediate consequence]
- Long-term: [Technical debt]

RECOMMENDED ALTERNATIVE:
[Propose solution following AGENT.md]

Do you want to proceed with original solution (NOT recommended)
or apply the alternative?
```

---

## 10. Executive Summary — Golden Rules

1. **NEVER `fetch()` in components** — always through `src/api/`
2. **TanStack Query for ALL server state** — no manual `useEffect` fetching
3. **CSS Modules for ALL styles** — no inline, no global (except reset)
4. **TDD** — test first, component after
5. **Coverage ≥ 80%** — non-negotiable
6. **`VITE_` prefix mandatory** for all env vars
7. **Functional components only** — no class components
8. **JSDoc** on all public components and hooks
9. **`npm run build` must pass** before any commit
10. **Warn user** if any frontend best practice is violated

---

**Version:** 1.0
**Location:** `market_data_frontend_platform/AGENT.md`
**Scope:** Tool-agnostic (Claude Code, Antigravity, Aider, Cursor)
**Stack:** React 18+ / Vite / JavaScript (ES6+)
**Last Updated:** 2026-02-27
