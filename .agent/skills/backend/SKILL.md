---
name: backend
description: "Backend development specialist for Python + FastAPI. Use when implementing API endpoints, database models, business logic, authentication, or any backend Python code. Enforces type safety, Pydantic models, pytest testing, and secure coding practices."
---

# Backend Development Skill

You are a backend development expert specializing in Python with FastAPI and uv.

## When to use this skill

- Implementing new API endpoints or modifying existing ones
- Creating or updating Pydantic models
- Writing database queries or ORM code
- Adding authentication or authorization logic
- Writing backend tests with pytest
- Working in the `backend/` directory

## Do not use this skill when

- The task is purely frontend (React/TypeScript) — use the `frontend` skill instead
- The task is infrastructure/deployment — use the `terraform` skill instead

## Core Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Package manager**: `uv` (never `pip`)
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Linting/Formatting**: ruff
- **Target directory**: `backend/`

## Instructions

### 1. API Endpoint Design

Follow REST conventions:
- `GET /resources` — list (with pagination)
- `POST /resources` — create
- `GET /resources/{id}` — get by ID
- `PUT /resources/{id}` — full update
- `PATCH /resources/{id}` — partial update
- `DELETE /resources/{id}` — delete

Version all APIs: `/api/v1/`.

Always use proper HTTP status codes:
- `200 OK`, `201 Created`, `204 No Content`
- `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`
- `422 Unprocessable Entity` (Pydantic validation errors)
- `500 Internal Server Error` (never expose details to client)

### 2. Pydantic Models (Multi-Model Pattern)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ResourceBase(BaseModel):
    """Shared fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ResourceCreate(ResourceBase):
    """Request body for creation."""
    pass

class ResourceUpdate(BaseModel):
    """Request body for update (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class ResourceResponse(ResourceBase):
    """API response."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ResourceInDB(ResourceResponse):
    """Database document."""
    doc_type: str = "resource"
```

### 3. Type Hints & Docstrings

Every function must have:
- Complete type annotations on all parameters and return values
- Google Style docstring

```python
def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Retrieve a user by their ID.

    Args:
        db: Database session.
        user_id: The UUID of the user.

    Returns:
        The User object if found, None otherwise.

    Raises:
        DatabaseError: If there's a database connectivity issue.
    """
    return db.query(User).filter(User.id == user_id).first()
```

### 4. Testing Requirements

Before writing tests, present a **Test Perspectives Table** (see user_rules.md).

Use Given/When/Then comments:

```python
def test_create_user_success(client: TestClient, db: Session) -> None:
    """Test successful user creation."""
    # Given: valid user data
    payload = {"name": "Alice", "email": "alice@example.com"}

    # When: POST /api/v1/users is called
    response = client.post("/api/v1/users", json=payload)

    # Then: returns 201 with user data
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
```

### 5. Security Practices

- Validate ALL inputs with Pydantic
- Use parameterized queries (never string interpolation in SQL)
- Hash passwords with `bcrypt` or `argon2`
- Return minimal error details to clients
- Use dependency injection for authentication
- Log security events (auth failures, suspicious inputs)

### 6. Commands

```bash
uv run pytest                              # all tests
uv run pytest tests/unit/                  # unit tests
uv run pytest tests/integration/           # integration tests
uv run pytest --cov=src --cov-report=html  # with coverage
uv run ruff check .                        # lint
uv run ruff format .                       # format
uv add <package>                           # add dependency
uv add --dev <package>                     # add dev dependency
```

## Output Format

1. Implement the requested code with full type hints and docstrings
2. Create or update Pydantic models as needed
3. Write tests following the test perspectives table format
4. Run linting and tests to verify
5. Report what was implemented and any remaining issues
