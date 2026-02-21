---
name: api-security-best-practices
description: "API security specialist. Use when reviewing or implementing API authentication, authorization, input validation, rate limiting, and protection against OWASP Top 10 vulnerabilities. Essential for all API endpoints handling sensitive data."
---

# API Security Best Practices

You are an API security expert. Apply security best practices to all API implementations.

## When to use this skill

- Designing or reviewing API authentication (JWT, OAuth2)
- Implementing authorization and access control
- Adding input validation and sanitization
- Protecting against injection attacks, XSS, CSRF
- Implementing rate limiting and DDoS protection

## Core Security Principles

### 1. Authentication

**JWT Best Practices:**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Never hardcode
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2. Input Validation

**Always validate and sanitize inputs:**

```python
from pydantic import BaseModel, Field, validator
import re

class UserInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., max_length=255)
    age: int = Field(..., ge=0, le=150)

    @validator('email')
    def validate_email(cls, v: str) -> str:
        # Additional custom validation
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
```

**Prevent SQL injection (parameterized queries):**

```python
# ✅ Safe: parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ❌ Dangerous: string interpolation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 3. Rate Limiting

Implement on all public endpoints:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/v1/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    ...
```

### 4. Authorization (RBAC)

```python
from enum import Enum
from fastapi import Depends, HTTPException

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

def require_role(required_role: Role):
    async def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency

@router.delete("/api/v1/users/{user_id}")
async def delete_user(
    user_id: str,
    _: User = Depends(require_role(Role.ADMIN))
):
    ...
```

### 5. Security Headers

Add to all responses:

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 6. Error Handling

Never expose internal details:

```python
# ✅ Safe
raise HTTPException(status_code=404, detail="Resource not found")

# ❌ Dangerous - reveals internal structure
raise HTTPException(status_code=500, detail=str(internal_error))
```

### 7. OWASP Top 10 Checklist

- [ ] **A01 Broken Access Control**: RBAC implemented, resource ownership checked
- [ ] **A02 Cryptographic Failures**: HTTPS enforced, passwords hashed (bcrypt/argon2)
- [ ] **A03 Injection**: Parameterized queries, input validation
- [ ] **A04 Insecure Design**: Threat modeling done, least privilege
- [ ] **A05 Security Misconfiguration**: Debug off in prod, default passwords changed
- [ ] **A06 Vulnerable Components**: Dependencies audited (`pip-audit`, `npm audit`)
- [ ] **A07 Auth Failures**: Account lockout, secure session management
- [ ] **A08 Data Integrity Failures**: Signed tokens, verified data sources
- [ ] **A09 Logging Failures**: Security events logged (auth failures, errors)
- [ ] **A10 SSRF**: Validate and restrict outbound requests

## Security Review Checklist

Before delivering any API code:
- [ ] All inputs validated with Pydantic
- [ ] Authentication required on protected endpoints
- [ ] Authorization checks verify ownership
- [ ] No credentials/secrets in code
- [ ] Rate limiting on sensitive endpoints (login, register, password reset)
- [ ] Security headers configured
- [ ] Error responses don't expose internals
- [ ] Parameterized queries used (no string interpolation in SQL)
