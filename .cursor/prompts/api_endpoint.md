# API Endpoint Development Template

**Context**: Use this template for creating new REST API endpoints with proper validation and error handling.

**Task**: Create a new REST API endpoint for [RESOURCE_NAME].

**Requirements**:
- HTTP Method: [GET/POST/PUT/DELETE]
- Endpoint Path: [API_PATH]
- Input validation using existing validation schemas
- Error handling with proper HTTP status codes
- Authentication middleware integration
- Database operations (if applicable)
- Response formatting and documentation

**Code References**:
Use existing patterns from @file:src/routes/auth.js
Reference validation schemas in @folder:src/schemas
Follow middleware patterns in @folder:src/middleware

**Implementation Checklist**:
- [ ] Route definition with proper HTTP method
- [ ] Input validation middleware
- [ ] Authentication/authorization checks
- [ ] Business logic implementation
- [ ] Database operations (CRUD)
- [ ] Error handling and status codes
- [ ] Response formatting
- [ ] Unit tests
- [ ] API documentation

**Security Considerations**:
- Input sanitization and validation
- Rate limiting
- Authentication requirements
- Authorization checks
- CORS configuration
- Data exposure prevention

**Testing Requirements**:
- Unit tests for business logic
- Integration tests for API endpoints
- Error case coverage
- Authentication/authorization testing
- Performance validation

**Success Criteria**:
- All tests pass
- API documentation updated
- Security review completed
- Performance requirements met
- Backward compatibility maintained
