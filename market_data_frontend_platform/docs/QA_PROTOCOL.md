# QA_PROTOCOL — Market Data Frontend Platform

> **Purpose:** Non-negotiable validation checklist. A feature is not done until all applicable items pass.
> **Stack:** React 18 · Vite 5 · Vitest · ESLint · Prettier

---

## 1. Code Quality

### 1.1 Linting (ESLint)

```bash
npm run lint
```

- [ ] Exit code = 0
- [ ] Zero errors, zero warnings (`--max-warnings 0`)
- [ ] No `console.log` in `src/` (use `// eslint-disable` only for documented exceptions)
- [ ] No unused imports or variables

### 1.2 Formatting (Prettier)

```bash
npm run format:check
```

- [ ] Exit code = 0
- [ ] All files in `src/` conform to `.prettierrc` settings

### 1.3 Build

```bash
npm run build
```

- [ ] Exit code = 0
- [ ] No TypeScript / Vite errors
- [ ] `dist/` directory created with `index.html`, JS bundle, CSS bundle

---

## 2. Testing (Vitest + RTL)

### 2.1 Test suite

```bash
npm test
```

- [ ] All tests pass (exit code = 0)
- [ ] No skipped tests (`it.skip`, `describe.skip`) without documented reason
- [ ] No `console.error` output during test run (React prop-types, missing keys, etc.)

### 2.2 Coverage

```bash
npm test -- --coverage
```

- [ ] **Global coverage ≥ 80%** (lines, branches, functions, statements)
- [ ] `src/api/` coverage = 100% (pure functions, fully testable)
- [ ] Every component in `src/components/` has a `*.test.jsx` file

### 2.3 Test quality checklist (per component/hook)

- [ ] **Render test**: component renders without throwing
- [ ] **Loading state**: skeleton or spinner shown while `isLoading = true`
- [ ] **Error state**: error message shown when `isError = true`
- [ ] **Empty state**: correct message when data is empty array
- [ ] **User interaction**: click / input / submit events produce correct state changes
- [ ] **API calls**: `src/api/` functions called with correct arguments (vi.mock)
- [ ] **No implementation leakage**: tests target user-visible behavior, not internal state

---

## 3. Architecture Invariants

These rules are enforced by code review. No automated gate exists yet — check manually.

- [ ] **No `fetch()` outside `src/api/`** — grep for `fetch(` in `src/components/`, `src/pages/`, `src/hooks/`
- [ ] **No `useEffect` for data fetching** — all server state via TanStack Query
- [ ] **No inline styles for static values** — CSS Modules only; dynamic chart dimensions are the only exception
- [ ] **No hardcoded API URLs** — grep for `localhost` or `http` in `src/` (except `.env.example`)
- [ ] **No TypeScript files** — no `.ts` or `.tsx` in `src/`
- [ ] **No axios** — `package.json` must not contain `axios`
- [ ] **No class components** — grep for `extends Component` or `extends React.Component`
- [ ] **`VITE_` prefix** on all env vars accessed via `import.meta.env`
- [ ] **One component per file** — filename matches default export name

---

## 4. API Contract Compliance

- [ ] All API calls use endpoints documented in `docs/PRD.md §2`
- [ ] No field names hardcoded that differ from backend JSON schema
- [ ] 401 responses handled: clear `localStorage`, redirect to `/login`
- [ ] Non-OK responses surface `detail` field from error body to user
- [ ] `VITE_API_URL` is the only source of the backend base URL

---

## 5. Accessibility (Basic)

- [ ] All form inputs have associated `<label>` elements
- [ ] Buttons have descriptive text or `aria-label`
- [ ] Error messages are associated with their form fields (or displayed near them)
- [ ] Page title updates on route change

---

## 6. Pre-Commit Checklist (from AGENT.md §7)

Run before every commit:

```bash
npm run lint          # 0 ESLint errors, 0 Prettier issues
npm test              # all tests pass
npm run build         # build succeeds
```

- [ ] `npm run lint` → clean
- [ ] `npm test` → all green
- [ ] `npm run build` → dist/ created
- [ ] No `console.log` in `src/` (production code)
- [ ] No `fetch()` outside `src/api/`
- [ ] All new components have at least one test

---

## 7. Definition of Done (Feature Level)

A feature PR is mergeable when:

1. All Phase items in `DEV_PLAN.md` for that phase are complete
2. All items in sections 1–6 of this document pass
3. Code reviewed by at least one reviewer (or self-reviewed against this checklist)
4. `feature/frontend` branch rebased on latest `main`

---

## 8. Severity Levels

| Severity | Description                                      | Blocks merge? |
|----------|--------------------------------------------------|---------------|
| P0       | Build fails / tests fail / coverage < 80%        | Yes           |
| P1       | ESLint error / Prettier error / fetch() in comp  | Yes           |
| P2       | Missing test for a component / missing JSDoc      | Yes           |
| P3       | Warning / style inconsistency                    | No (fix soon) |
