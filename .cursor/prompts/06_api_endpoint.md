# API Endpoint Development Template

**Context**: Use this template for creating new REST API endpoints with proper validation, error handling, and documentation.

---

## Endpoint Specification

**Resource**: [RESOURCE_NAME]
**HTTP Method**: [GET / POST / PUT / PATCH / DELETE]
**Endpoint Path**: [/api/v1/...]

**Description**: [WHAT THIS ENDPOINT DOES]

---

## Request/Response Schema

**Request Body** (if applicable):
```json
{
  "field1": "string (required) - description",
  "field2": "integer (optional) - description"
}
```

**Success Response** (200/201):
```json
{
  "data": {
    "id": "string",
    "...": "..."
  },
  "message": "string"
}
```

**Error Response** (4xx/5xx):
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

---

## Implementation Checklist

### Request Handling
- [ ] Input validation using Pydantic/validation schemas
- [ ] Type checking on all parameters
- [ ] Required vs optional fields clearly defined
- [ ] Default values for optional fields

### Authentication & Authorization
- [ ] Authentication middleware applied
- [ ] Authorization checks (roles/permissions)
- [ ] Rate limiting if needed

### Business Logic
- [ ] Core functionality implemented in service layer
- [ ] Database operations handled properly
- [ ] Transaction management for multi-step operations

### Error Handling
- [ ] Proper HTTP status codes for each error type
- [ ] Structured error responses
- [ ] No sensitive data in error messages
- [ ] Logging of errors server-side

### Documentation
- [ ] OpenAPI/Swagger docstring
- [ ] Request/response examples
- [ ] Error codes documented

---

## Code Structure

```python
# schemas/[resource].py
class [Resource]Request(BaseModel):
    """Request schema with validation."""
    field1: str = Field(..., description="...")
    field2: Optional[int] = Field(None, description="...")

class [Resource]Response(BaseModel):
    """Response schema."""
    id: str
    ...

# routes/[resource].py
@router.[method]("/path")
async def endpoint_name(
    request: [Resource]Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> [Resource]Response:
    """
    Endpoint description for OpenAPI docs.
    
    - **param1**: Description
    - **returns**: Description
    """
    # Implementation
    ...
```

---

## Testing Requirements

- [ ] Unit tests for business logic
- [ ] Integration tests for endpoint
- [ ] Test cases for:
  - [ ] Valid request → success response
  - [ ] Invalid request → validation error (400)
  - [ ] Unauthenticated → 401
  - [ ] Unauthorized → 403
  - [ ] Resource not found → 404
  - [ ] Server error handling → 500

---

## Success Criteria
- [ ] Endpoint follows REST conventions
- [ ] All validation in place
- [ ] Proper error handling
- [ ] Authentication/authorization working
- [ ] Tests passing
- [ ] API documentation generated

