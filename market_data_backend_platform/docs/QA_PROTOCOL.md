# Backend QA Protocol

## Executable Contracts

**Pre-commit Validations:**

```bash
pytest --cov=src --cov-fail-under=85
mypy src/
ruff check src/
black --check src/
python scripts/validate_schemas.py
```

**Custom Scripts:**

- `scripts/validate_against_prd.py`: Verifies PRD vs code alignment.
- `scripts/validate_schemas.py`: Checks Pydantic against JSON schemas in `/docs/schemas/`.

**Testing Targets:**

- 85% global coverage minimum.
- 100% on critical business logic pathways.
- Integration tests must use testcontainers or `docker-compose.test.yml`.
