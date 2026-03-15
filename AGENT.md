# AGENT.md - Monorepo Orchestration

## Operational Preconditions

- **Backend Stack**: Python 3.14+, FastAPI, PostgreSQL
- **Frontend Stack**: JS/React 18+, Vite 5
- **Monorepo rule**: No source code at root. Root is for orchestration.

## Commands (Makefile)

- `make up`: Start prod-like full stack
- `make up-dev`: Start with hot reload (`docker-compose.dev.yml`)
- `make down-clean`: Stop & rm volumes
- `make check-all`: Run backend tests & frontend lint/test
- `make check-all-integration`: Includes docker isolated integration tests

## Environment Constraints

- Use single layer configuration (shared infra `.env`, backend-only `.env`, frontend-only with `VITE_` prefix)
- Never use `env_file` for secrets in `docker-compose.yml` (escaping bug); use `environment:` explicitly.

## Project Conventions

- **Commit format**: `<type>(<scope>): <msg>` (Scopes: backend, frontend, docker, docs, root)
- OpenAPI spec (`/openapi.json`) is the single source of truth for frontend API client.
