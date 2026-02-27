# QA_PROTOCOL.md - Quality Assurance Protocol

> **Purpose:** Executive validation checklist
> **Location:** `/docs/QA_PROTOCOL.md`
> **For:** AI Agent + Developers
> **Use:** Before commit, in Definition of Done, in Code Reviews

---

## Document Hierarchy

**If conflict exists, follow this order:**

1. `/docs/PRD.md` - Architectural contract (WHAT to build)
2. `/AGENT.md` - Technical standards (HOW to write code)
3. `/docs/QA_PROTOCOL.md` - Validation checklist (this document)

**Golden Rule:** If something contradicts PRD → **STOP** and ask user.

---

## 1. Single Source of Truth

- [ ] **PRD Alignment**: All code implements `/docs/PRD.md`
- [ ] **No divergence**: If implementation differs, update PRD FIRST
- [ ] **When in doubt**: STOP and request clarification

**Validation:**

```bash
# Compare implementation vs PRD
python scripts/validate_against_prd.py
```

---

## 2. Schema First

- [ ] **Pydantic Models**: All models use `BaseModel`
- [ ] **Complete type hints**: Every field annotated
- [ ] **Custom validators**: If applicable (corporate email, ranges)
- [ ] **JSON Schemas**: In `/docs/schemas/*.json`

**Correct example:**

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr

    @field_validator('email')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if not v.endswith('@company.com'):
            raise ValueError('Corporate email required')
        return v
```

**Validation:**

```bash
python scripts/validate_schemas.py
```

---

## 3. Test-Driven Development (TDD)

- [ ] **Cycle RED → GREEN → REFACTOR**: Applied
- [ ] **Test first**: Written BEFORE code
- [ ] **Coverage >= 85%**: Configured in `pyproject.toml`
- [ ] **Meaningful tests**: Validate behavior, not just coverage

**Mandatory cycle:**

```
1. RED: Test fails (functionality doesn't exist)
2. GREEN: Minimum code that passes
3. REFACTOR: Improve without breaking tests
```

**Validation:**

```bash
# Tests pass
pytest -v

# Coverage >= 85%
pytest --cov=src --cov-fail-under=85

# View details
pytest --cov=src --cov-report=html
```

---

## 4. No Placeholders

- [ ] **No empty TODOs**: Each TODO has associated issue
- [ ] **No "Implement later"**: Functional code or doesn't exist
- [ ] **No naked pass**: Document why

**Bad:**

```python
def process():
    # TODO: Implement
    pass
```

**Good:**

```python
def process(data: dict) -> Result:
    """Process user data.

    TODO(#123): Add retry for timeouts
    https://github.com/project/issues/123
    """
    return gateway.process(data)
```

---

## 5. SOLID Principles

### S - Single Responsibility

- [ ] Each class/function: **one** responsibility
- [ ] Functions < 20 lines
- [ ] Classes < 200 lines

### O - Open/Closed

- [ ] Extendable without modifying existing
- [ ] Polymorphism instead of massive `if/elif`

### L - Liskov Substitution

- [ ] Subclasses substitute base without breaking

### I - Interface Segregation

- [ ] Specific interfaces (use `Protocol`)

### D - Dependency Inversion

- [ ] **Dependency Injection**: DON'T instantiate inside classes
- [ ] Depend on abstractions, not concretions

**Validation:**

```bash
# Cyclomatic complexity
radon cc src/ -a -nb

# Refactoring hints
pylint src/ --disable=all --enable=R
```

---

## 6. Clean Code

- [ ] **Descriptive names**: NO `x`, `temp`, `data`
- [ ] **Early return**: Avoid deep `if/else`
- [ ] **DRY**: Refactor after 1st repetition
- [ ] **Indentation**: Maximum 3 levels

**Example:**

```python
# ❌ Bad
def proc(d):
    if d:
        r = d.get('n')
        if r:
            return r
    return None

# ✅ Good
def extract_name(data: dict[str, Any]) -> str | None:
    """Extract name from dictionary."""
    if not data:
        return None
    return data.get('name')
```

---

## 7. PEP Compliance

### PEP 8 - Style

- [ ] `black --check src/` passes
- [ ] `ruff check src/` no warnings
- [ ] Lines <= 88 characters

### PEP 257 - Docstrings

- [ ] Google format
- [ ] Public functions documented
- [ ] Include: Args, Returns, Raises, Example (if complex)

### PEP 484 - Type Hints

- [ ] ALL signatures annotated
- [ ] No `Any` (avoid except justified cases)

### PEP 585 - Built-in Generics

- [ ] `list[str]` NOT `List[str]`
- [ ] `int | None` NOT `Optional[int]`

**Validation:**

```bash
black --check src/
ruff check src/
mypy src/ --strict
```

---

## 8. Logging and Errors

### Logging

- [ ] **NO print()**: Forbidden in production
- [ ] **structlog**: Structured logging
- [ ] **Correct levels**: DEBUG/INFO/WARNING/ERROR/CRITICAL

### Exceptions

- [ ] **NO except Exception**: Catch specific
- [ ] **Custom exceptions**: Inherit from project base
- [ ] **Error logging**: With `exc_info=True`

**Example:**

```python
import structlog

logger = structlog.get_logger(__name__)

try:
    result = operation()
except (ValueError, KeyError) as e:
    logger.error("operation_failed", error=str(e), exc_info=True)
    raise
```

---

## 9. Pre-commit Hooks

**Automated hooks** (`.pre-commit-config.yaml`):

- [ ] **black**: Auto-formatting
- [ ] **ruff**: Fast linting
- [ ] **mypy**: Type checking
- [ ] **isort**: Sort imports

**On pre-push** (NOT pre-commit):

- [ ] **pytest**: Full suite + coverage

**Validation:**

```bash
# Run all
pre-commit run --all-files

# Only verify
pre-commit run --all-files --show-diff-on-failure
```

---

## 10. Definition of Done

### Checklist per Feature

**A feature is complete when:**

#### Tests

- [ ] Unit tests pass
- [ ] Feature coverage >= 85%
- [ ] Integration tests pass (if applicable)

#### Quality

- [ ] `mypy src/` no errors
- [ ] `ruff check src/` no warnings
- [ ] `black --check src/` passes

#### Documentation

- [ ] Complete docstrings
- [ ] Comments only where necessary
- [ ] PRD updated if design changed

#### Schemas

- [ ] JSON Schemas updated
- [ ] Schema validation passes

#### Git

- [ ] Descriptive commit: `feat(module): description`
- [ ] Branch updated
- [ ] No merge conflicts

**Complete command:**

```bash
#!/bin/bash
# validate_dod.sh

set -e

echo "Validating Definition of Done..."

# Tests
pytest -v
pytest --cov=src --cov-fail-under=85

# Types
mypy src/

# Quality
ruff check src/
black --check src/

# Schemas
python scripts/validate_schemas.py

# Pre-commit
pre-commit run --all-files

echo "✅ Definition of Done: COMPLETE"
```

---

## 11. Validations by Phase

### Phase 0 - Setup

- [ ] Virtual environment activated
- [ ] Dependencies in `requirements.txt`
- [ ] Pre-commit installed
- [ ] This QA_PROTOCOL.md exists

### Phase 1 - PRD

- [ ] Complete Pydantic models
- [ ] JSON Schemas in `/docs/schemas/`
- [ ] Stack with exact versions
- [ ] Testable User Stories

### Phase 1.5 - Validation

- [ ] No Pydantic ↔ JSON inconsistencies
- [ ] No blockers
- [ ] Warnings documented

### Phase 2 - DEV_PLAN

- [ ] Atomic tasks (1-2h each)
- [ ] Validation commands per phase
- [ ] Clear dependencies

### Phase 3 - Execution

- [ ] TDD applied (RED → GREEN → REFACTOR)
- [ ] Incremental commits
- [ ] Continuous validation

### Phase 4 - Audit

- [ ] 100% PRD features
- [ ] Coverage >= 85%
- [ ] No critical technical debt

---

## 12. Violation Severity

### 🔴 CRITICAL (Blocks merge)

- No tests
- Coverage < 85%
- Mypy errors
- Security (SQL injection, hardcoded secrets)
- PRD functionality NOT implemented

### 🟡 IMPORTANT (Fix < 1 week)

- Ruff/Black warnings
- Evident SOLID violations
- Duplicated code
- Incomplete docstrings

### 🔵 SUGGESTION (Continuous improvement)

- Performance optimizations
- Cosmetic refactoring
- Readability improvements

---

## 13. Reference Commands

```bash
# Complete validation (before PR)
pytest --cov=src --cov-fail-under=85 && \
mypy src/ && \
ruff check src/ && \
black --check src/

# Quick validation (development)
pytest -q && mypy src/ --no-error-summary && ruff check src/ -q

# Auto-formatting
black src/ tests/
isort src/ tests/

# Detailed coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Dead code
vulture src/ --min-confidence 80

# Duplicated code
pylint src/ --disable=all --enable=duplicate-code

# Complexity
radon cc src/ -a -nb
```

---

## 14. Conflict Escalation

If **irreconcilable conflict** found:

1. **STOP** execution
2. **DOCUMENT** conflict
3. **ESCALATE** to user
4. **WAIT** for decision

**Template:**

```
⚠️  CONFLICT DETECTED

PRD.md says: [X]
AGENT.md says: [Y]

OPTION A IMPACT:
- Pro: [benefit]
- Con: [risk]

OPTION B IMPACT:
- Pro: [benefit]
- Con: [risk]

RECOMMENDATION: [preferred option + justification]

Which option to apply?
```

---

## Executive Summary

### Minimum Checklist (Before Commit)

1. ✅ `pytest -v` - Tests pass
2. ✅ `pytest --cov --cov-fail-under=85` - Coverage
3. ✅ `mypy src/` - Types OK
4. ✅ `ruff check src/` - Quality OK
5. ✅ `python scripts/validate_schemas.py` - Schemas OK
6. ✅ `pre-commit run --all-files` - Hooks OK

### Golden Rules

1. **TDD**: Test first, code after
2. **SOLID**: Not optional
3. **Type hints**: In ALL signatures
4. **Docstrings**: In public functions
5. **NO print()**: Use structlog
6. **PRD is law**: If contradicts, escalate

---

**Version:** 3.0 Final (English)
**Location:** `/docs/QA_PROTOCOL.md`
**Related:** `/AGENT.md` (detailed standards)
**Last Updated:** 2025-02-06
