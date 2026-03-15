# Frontend QA Protocol

## Test Commands & Coverage

```bash
npm run format:check
npm run lint -- --max-warnings 0
npm test -- --coverage
npm run build
```

## Validation Targets

- **Coverage**: 80% global minimum.
- **API Tests**: 100% coverage on `src/api/` (mocking fetch).
- **Component Tests**: Must cover render, loading state, error state, empty state, user interactions.

## Checkpoints

- Verify no `fetch` or `localhost` strings in `src/components/`, `src/pages/`, `src/hooks/`.
- Catch all 401s globally via api client.
