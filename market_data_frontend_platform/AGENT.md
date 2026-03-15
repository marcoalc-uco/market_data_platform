# AGENT.md - Frontend Standards

## Operational Preconditions

- **Stack**: JS (ES6+), React 18+, Vite 5, TanStack Query v5, lightweight-charts.
- **Strict Architecture**: NO `fetch()` allowed outside `src/api/`.
- **CSS**: CSS Modules only. No global styles except `index.css` variables/reset.
- **Server State**: Must use TanStack Query. No `useEffect` data fetching.

## Commands

- Dev Server: `npm run dev`
- Build: `npm run build`
- Linter: `npm run lint` (0 errors required)
- Tests: `npm test` --coverage (80% minimum)

## Internal Constraints

- All env vars must have `VITE_` prefix.
- Multi-stage Dockerfile required (builder -> nginx).
- No class components. No `.ts` or `.tsx` files.
