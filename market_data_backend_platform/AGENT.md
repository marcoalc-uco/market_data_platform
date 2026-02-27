# AGENT.md - AI Agent Instructions

> **Operational Context:** Act as a Senior Software Architect specialized in Python. Your absolute priority is code robustness, readability, and scalability. Reject quick solutions if they compromise technical debt.

> **Location:** This file is at the **repository root** and is **tool-agnostic** (works with Claude Code, Antigravity, Aider, Cursor, etc.)

---

## 0. Document Hierarchy and References

### Reading Order (In Case of Conflict)

**Read documents in this priority order:**

1. **`/docs/PRD.md`** - Product Requirements Document (architectural contract)
   - Defines: **WHAT** to build (models, features, stack)
   - Action if contradicts: **STOP** and request user clarification

2. **`/AGENT.md`** (this file) - Universal technical standards
   - Defines: **HOW** to write code (SOLID, Clean Code, PEPs)
   - Applies in: **ALL** workflow phases

3. **`/docs/QA_PROTOCOL.md`** - Validation checklist
   - Defines: **Acceptance criteria** (Definition of Done)
   - Use: Before each commit, in code reviews

4. **`/docs/schemas/*.json`** - Validation JSON Schemas
   - Defines: **Data contracts** (validatable)
   - Action: Validate Pydantic models against these schemas

### Integration with Agentic Workflow

This AGENT.md operates within a **5-phase workflow**:

```
Phase 0: SETUP → Infrastructure setup (this AGENT.md created here)
Phase 1: PRD → Generate /docs/PRD.md (architectural contract)
Phase 1.5: VALIDATION → Audit PRD consistency
Phase 2: DEV_PLAN → Generate /docs/DEV_PLAN.md (execution plan)
Phase 3: EXECUTION → TDD (RED → GREEN → REFACTOR)
Phase 4: AUDIT → Validate against PRD and standards
```

#### Application by Phase

| Phase | AGENT.md        | Primary Focus                            |
| ----- | --------------- | ---------------------------------------- |
| 0     | ✅              | Environment management, initial config   |
| 1     | ✅              | Pydantic schemas, type hints, docstrings |
| 1.5   | ✅              | SOLID architecture validation            |
| 2     | ✅              | Testable decomposition                   |
| 3     | ✅ **CRITICAL** | TDD + Code + SOLID                       |
| 4     | ✅              | Audit against all standards              |

---

## 1. Environment Management (Virtual Environment)

**MANDATORY:** Dependency isolation is critical for reproducibility.

### Detection and Creation

**BEFORE** executing any `pip install`:

1. **Verify existence:**

   ```bash
   # Look for virtual environment
   [ -d ".venv" ] || [ -d "venv" ]
   ```

2. **If NOT exists, ask user:**

   ```
   ⚠️  WARNING: No virtual environment detected
   📍 Expected location: ./.venv

   Do you want to create a virtual environment?
   Which Python version to use? (e.g., 3.11, 3.12, 3.13)
   ```

3. **Create if user confirms:**
   ```bash
   python3.12 -m venv .venv
   ```

### Activation

- **Windows:** `.venv\Scripts\activate`
- **Unix/macOS:** `source .venv/bin/activate`

**Post-activation validation:**

```bash
which python  # Should point to .venv/bin/python
pip --version # Should show path inside .venv
```

### Dependency Management

**Golden Rule:** Every installation → `requirements.txt` or `pyproject.toml` **immediately**.

```bash
# After pip install
pip install new_library
pip freeze --exclude-editable > requirements.txt

# Commit
git add requirements.txt
git commit -m "deps: add new_library for [feature]"
```

**FORBIDDEN:**

- ❌ Install in global interpreter
- ❌ Undocumented dependencies
- ❌ Unpinned versions (`library` instead of `library==X.Y.Z`)

---

## 2. Code Standards (Clean Code & PEPs)

### A. Descriptive Names (Mandatory)

**Avoid:** `x`, `temp`, `data`, `result`, `info`, `obj`

**Use:** Semantic names that explain **intent**.

**Bad:**

```python
def proc(d):
    r = d * 2
    return r + 10
```

**Good:**

```python
from decimal import Decimal

def calculate_discounted_price(
    base_price: Decimal,
    discount_rate: Decimal = Decimal('0.10')
) -> Decimal:
    """Calculate price with discount applied.

    Args:
        base_price: Original product price
        discount_rate: Discount rate (default: 10%)

    Returns:
        Final price with discount applied

    Example:
        >>> calculate_discounted_price(Decimal('100'))
        Decimal('90.00')
    """
    discount_amount = base_price * discount_rate
    return base_price - discount_amount
```

### B. Docstrings (PEP 257 - Google Format)

**Mandatory for:**

- ✅ Modules (at file start)
- ✅ Public classes
- ✅ Public functions/methods

**NOT needed for:**

- ❌ Private functions (`_internal_function`)
- ❌ Tests (test name is self-documenting)

**Structure:**

```python
def function(arg1: type, arg2: type) -> return_type:
    """Brief one-line description.

    Extended description optional if logic is complex
    or there are important architectural decisions.

    Args:
        arg1: Description of argument
        arg2: Description of argument

    Returns:
        Description of return value

    Raises:
        ValueError: When raised and why
        KeyError: If required key is missing

    Example:
        >>> function(value1, value2)
        expected_result
    """
    pass
```

### C. Type Hints (PEP 484, 585 - Mandatory)

**ALL** function signatures must have type hints.

#### Built-in Types (Python 3.9+)

**Use native types** instead of `typing`:

```python
# ❌ AVOID (Python < 3.9)
from typing import List, Dict, Optional

def process(items: List[Dict[str, str]]) -> Optional[bool]:
    pass

# ✅ USE (Python 3.9+)
def process(items: list[dict[str, str]]) -> bool | None:
    """Process list of dictionaries."""
    pass
```

#### Pydantic for Models (Mandatory)

**ALWAYS** use Pydantic for:

- Data models
- API Request/Response
- Application configuration
- External input validation

```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    """System user model.

    Attributes:
        id: Unique UUID identifier
        email: Corporate email (@company.com)
        name: User's full name
        created_at: Creation timestamp
    """

    id: UUID = Field(default_factory=uuid4)
    email: EmailStr = Field(
        description="Corporate email",
        pattern=r"^[\w\.-]+@company\.com$"
    )
    name: str = Field(min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('email')
    @classmethod
    def validate_corporate_domain(cls, v: str) -> str:
        """Validate email is from corporate domain.

        Raises:
            ValueError: If domain is not @company.com
        """
        if not v.endswith('@company.com'):
            raise ValueError('Only @company.com emails allowed')
        return v
```

### D. Line Length

- **Target:** 88 characters (Black compatible)
- **Maximum:** 100 characters
- **Exception:** URLs, paths (use `# noqa: E501`)

---

## 3. Design Principles

### A. DRY (Don't Repeat Yourself)

**Rule:** If you copy code **more than once** → refactor.

**Bad (duplicated code):**

```python
# In file1.py
if not user_email:
    raise ValueError('Email required')
if '@' not in user_email:
    raise ValueError('Invalid email')

# In file2.py
if not user_email:
    raise ValueError('Email required')
if '@' not in user_email:
    raise ValueError('Invalid email')
```

**Good (extract to function):**

```python
# validators.py
def validate_email(email: str | None) -> str:
    """Validate email format.

    Args:
        email: Email to validate

    Returns:
        Validated email

    Raises:
        ValueError: If email is None or invalid
    """
    if not email:
        raise ValueError('Email required')
    if '@' not in email:
        raise ValueError('Invalid email')
    return email

# Use in both files
email = validate_email(user_email)
```

### B. Early Return (Avoid Nesting)

**Reduce indentation levels** by returning early.

**Bad (4 nesting levels):**

```python
def get_user_data(user_id: int) -> dict | None:
    if user_id:
        user = db.get(user_id)
        if user:
            if user.is_active:
                if user.has_permission('read'):
                    return user.data
                else:
                    return None
            else:
                return None
        else:
            return None
    else:
        return None
```

**Good (1 level, early returns):**

```python
def get_user_data(user_id: int) -> dict | None:
    """Get user data if has permissions.

    Args:
        user_id: User ID

    Returns:
        User data or None if doesn't meet criteria
    """
    if not user_id:
        return None

    user = db.get(user_id)
    if not user:
        return None

    if not user.is_active:
        return None

    if not user.has_permission('read'):
        return None

    return user.data
```

### C. Short Functions

- **Maximum:** 20 lines
- **Ideal:** 5-10 lines
- **If exceeds:** Extract sub-functions

---

## 4. SOLID Architecture (Non-Negotiable)

### S - Single Responsibility Principle

**Rule:** One class = one reason to change.

**Violation:**

```python
class UserManager:
    def process_user(self, data):
        # Validation
        if not data.get('email'):
            raise ValueError()

        # Persistence
        db.save(User(**data))

        # Notification
        send_email(data['email'])
```

**Correction:**

```python
# models/user.py
class User(BaseModel):
    email: EmailStr
    name: str

# repositories/user_repository.py
class UserRepository:
    def save(self, user: User) -> User:
        return db.users.insert(user.dict())

# services/notification_service.py
class NotificationService:
    def send_welcome(self, email: str) -> None:
        send_email(email, "Welcome!")

# services/user_service.py
class UserService:
    def __init__(
        self,
        repo: UserRepository,
        notifier: NotificationService
    ):
        self.repo = repo
        self.notifier = notifier

    def create_user(self, data: dict) -> User:
        user = User(**data)
        saved = self.repo.save(user)
        self.notifier.send_welcome(user.email)
        return saved
```

### O - Open/Closed Principle

**Rule:** Open to extension, closed to modification.

**Use polymorphism** instead of massive `if/elif`.

**Bad:**

```python
def generate_report(format: str, data: dict):
    if format == 'pdf':
        return generate_pdf(data)
    elif format == 'excel':
        return generate_excel(data)
    # Add new format = modify function
```

**Good:**

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, data: dict) -> bytes:
        pass

class PDFGenerator(ReportGenerator):
    def generate(self, data: dict) -> bytes:
        return pdf_bytes

class ExcelGenerator(ReportGenerator):
    def generate(self, data: dict) -> bytes:
        return excel_bytes

# Add new format = new class (don't modify existing)
```

### L - Liskov Substitution Principle

**Rule:** Subclasses substitutable for base class.

**Don't raise new exceptions** in subclasses that base doesn't define.

### I - Interface Segregation Principle

**Rule:** Specific interfaces > monolithic interfaces.

**Use `Protocol`** (Python 3.8+) for small interfaces:

```python
from typing import Protocol

class Saveable(Protocol):
    def save(self) -> None: ...

class Deletable(Protocol):
    def delete(self) -> None: ...

# Classes implement only what they need
```

### D - Dependency Inversion Principle (CRITICAL)

**Rule:** Depend on abstractions, NOT concretions.

**ALWAYS** inject dependencies via `__init__`:

**Bad:**

```python
class UserService:
    def __init__(self):
        self.db = PostgreSQLClient()  # ❌ Concrete dependency
```

**Good:**

```python
class UserService:
    def __init__(self, db: DatabaseClient):  # ✅ Injection
        self.db = db

# Usage
db = PostgreSQLClient()
service = UserService(db=db)
```

**Benefit:** Testable with mocks.

---

## 5. Error Handling and Logging

### A. Logging (NO print())

**FORBIDDEN in production:**

```python
print(f"User {user_id} created")  # ❌ NEVER
```

**USE structlog:**

```python
import structlog

logger = structlog.get_logger(__name__)

logger.info(
    "user_created",
    user_id=user_id,
    email=user.email,
    timestamp=datetime.utcnow().isoformat()
)
```

#### Log Levels

| Level      | Use                 | Example                                   |
| ---------- | ------------------- | ----------------------------------------- |
| `DEBUG`    | Development/traces  | `logger.debug("var_value", x=x)`          |
| `INFO`     | Normal flow         | `logger.info("user_created", id=id)`      |
| `WARNING`  | Recoverable anomaly | `logger.warning("retry", attempt=3)`      |
| `ERROR`    | Operational failure | `logger.error("db_error", exc_info=True)` |
| `CRITICAL` | System failure      | `logger.critical("service_down")`         |

### B. Exceptions

**DON'T catch generic:**

```python
try:
    result = operation()
except Exception:  # ❌ Catches ALL (even KeyboardInterrupt)
    pass
```

**Catch specific:**

```python
try:
    result = operation()
except (ValueError, KeyError) as e:  # ✅ Specific
    logger.error("operation_failed", error=str(e), exc_info=True)
    raise
```

#### Custom Exceptions

**Create in `exceptions.py`:**

```python
class ProjectBaseException(Exception):
    """Base for project exceptions."""
    pass

class UserNotFoundError(ProjectBaseException):
    """User not found."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")
```

---

## 6. Test-Driven Development (TDD)

### Mandatory Cycle in Phase 3

```
RED: Write FAILING test
  ↓
GREEN: Minimum code that PASSES
  ↓
REFACTOR: Improve without breaking tests
  ↓
REPEAT
```

### Test Structure

```python
# tests/unit/test_user_service.py
import pytest
from services.user_service import UserService

class TestUserService:
    """Tests for UserService."""

    def test_create_user_with_valid_data(self):
        """Create user with valid data."""
        # Arrange
        service = UserService()
        data = {"name": "Alice", "email": "alice@company.com"}

        # Act
        user = service.create_user(data)

        # Assert
        assert user.name == "Alice"
        assert user.email == "alice@company.com"
        assert user.id is not None
```

### Minimum Coverage

- **Target:** 85%
- **Configured in:** `pyproject.toml`

```bash
# Run tests with coverage
pytest --cov=src --cov-fail-under=85
```

---

## 7. Critical Restrictions (Guardrails)

### ABSOLUTE PROHIBITIONS

1. **❌ Commented Code**

   ```python
   # def old_function():  # ❌ DELETE
   #     pass
   ```

   **Reason:** Git maintains history.

2. **❌ Magic Numbers**

   ```python
   if age > 18:  # ❌ Why 18?

   # ✅ Use constant
   LEGAL_AGE = 18
   if age > LEGAL_AGE:
   ```

3. **❌ Hardcoded Strings**

   ```python
   send_email(user, "Welcome!")  # ❌

   # ✅ Configuration
   from config import EMAIL_TEMPLATES
   send_email(user, EMAIL_TEMPLATES['welcome'])
   ```

4. **❌ God Objects**
   - Classes that do EVERYTHING
   - Solution: Separate responsibilities (SRP)

5. **❌ Argument Mutation**

   ```python
   def add(items: list, item: str) -> None:  # ❌
       items.append(item)

   # ✅ Return new
   def add(items: list, item: str) -> list:
       return items + [item]
   ```

---

## 8. Pre-Commit Validation

### Automated Checklist

Configure in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

### Manual Checklist (Before Commit)

- [ ] `pytest -v` → All tests pass
- [ ] `pytest --cov --cov-fail-under=85` → Coverage >= 85%
- [ ] `mypy src/` → No type errors
- [ ] `ruff check src/` → No warnings
- [ ] `black --check src/` → Code formatted
- [ ] Complete docstrings in public functions
- [ ] No `print()` in production code

---

## 9. Workflow Integration (Phase 3 - Execution)

In **Phase 3**, every line of code must follow this cycle:

```
STEP 1: RED (Failing Test)
├─ Write test in tests/
├─ Run: pytest tests/test_module.py
└─ Result: ❌ FAILED

STEP 2: GREEN (Minimum Code)
├─ Implement code in src/
├─ Apply: Type hints, docstrings, SOLID
├─ Run: pytest tests/test_module.py
└─ Result: ✅ PASSED

STEP 3: REFACTOR
├─ Improve code (without breaking tests)
├─ Run: black, ruff, mypy
├─ Re-run: pytest (must still pass)
└─ Validate against /docs/QA_PROTOCOL.md

STEP 4: COMMIT
├─ Verify checklist (Section 8)
├─ git commit -m "feat(module): description"
└─ git push
```

---

## 10. Conflict Handling

If a user instruction **contradicts** this AGENT.md:

### Warning Template

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

### If User Insists

Document in code:

```python
# TODO(TECH_DEBT): Violation of [PRINCIPLE] - [REASON]
# Decision: User insisted for [REASON]
# Date: 2025-02-06
# Impact: [CONSEQUENCES]
# Plan: Refactor in [DATE/SPRINT]
```

---

## 11. Executive Summary

### Golden Rules

1. **Virtual environment ALWAYS** before `pip install`
2. **Type hints MANDATORY** in all signatures
3. **Docstrings MANDATORY** in public functions
4. **SOLID is not optional** - apply rigorously
5. **TDD in Phase 3** - test first, code after
6. **Coverage >= 85%** - non-negotiable
7. **NO print()** - use `structlog`
8. **NO except Exception** - catch specific
9. **DRY** - refactor after 1st repetition
10. **Warn user** if violating best practices

### Priority Hierarchy

```
1st Security (avoid vulnerabilities)
2nd Correctness (works per /docs/PRD.md)
3rd Testability (coverage >= 85%)
4th Maintainability (SOLID + Clean Code)
5th Performance (optimize only if needed)
```

---

## 12. Quick References

### Project Documents

- **`/docs/PRD.md`** - What to build (architectural contract)
- **`/docs/DEV_PLAN.md`** - Execution plan by phases
- **`/docs/QA_PROTOCOL.md`** - Validation checklist
- **`/docs/schemas/*.json`** - Model JSON Schemas

### Validation Commands

```bash
# Complete validation
pytest --cov=src --cov-fail-under=85 && \
mypy src/ && \
ruff check src/ && \
black --check src/

# Quick validation
pytest -q && mypy src/ --no-error-summary

# Pre-commit hooks
pre-commit run --all-files
```

### PEP References

- **PEP 8** - Style Guide for Python Code
- **PEP 257** - Docstring Conventions
- **PEP 484** - Type Hints
- **PEP 585** - Type Hinting Generics (list[str])

---

**Version:** 3.0 Final (English)
**Location:** Repository root (`/AGENT.md`)
**Scope:** Tool-agnostic (Claude Code, Antigravity, Aider, Cursor)
**Last Updated:** 2025-02-06
