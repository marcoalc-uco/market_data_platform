# AGENT.md - Backend Standards

## Operational Preconditions

- **Stack**: Python 3.14+, FastAPI, SQLAlchemy 2.x, Pydantic v2
- Dependency management: always freeze into `requirements.txt`.
- Activate venv before installing: `.venv/bin/activate`

## Conventions

- **Solid Architecture**: Inject dependencies via `__init__`.
- **Validation**: Pydantic for all models and inputs.
- **Logging**: Use `structlog`. No `print()`.
- **Typing**: PEP 585 built-in generics (`list[str]`), NO `typing` module imports unless strictly required.
- **Data models**: Custom `MarketDataException` base class.

## Forbidden Actions

- No magic numbers.
- No hardcoded strings.
- No `except Exception: pass`.
- No commented-out bare code.
