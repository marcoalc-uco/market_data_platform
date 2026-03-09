# Frontend PRD

## Scoped Features

1. **Login Screen (`/login`)**
   - LocalStorage token handling (`access_token`).
   - Redirect to `/instruments` on success or if valid token present.
2. **Instruments List (`/instruments`)**
   - Paginated table (default limit=20), filtering (`asset_type`, `is_active`).
   - Full CRUD UI with modal forms.
3. **Price Chart (`/instruments/{id}/prices`)**
   - OHLCV candlestick via `lightweight-charts`.
   - Date range picker. Latest price summary.

## Out of Scope

- Real-time WebSockets. User registration. Dark mode. Mobile-first layout. Grafana embedding.

## Acceptance Criteria

- `npm run build` zero errors.
- Bundle < 500 KB gzipped.
- Automatic redirect to `/login` on HTTP 401.
