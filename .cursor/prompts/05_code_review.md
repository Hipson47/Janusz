# Code Review Template

**Context**: Use this template to review code for security vulnerabilities, best practices, and quality issues.

---

## Code Under Review

@file:[FILE_PATH]

or

@code:[FILE_PATH]:[LINE_RANGE]

---

## Review Checklist

### Security (CWE Compliance)
- [ ] **Input Validation**: All external inputs validated for type, format, length
- [ ] **Output Encoding**: User content escaped before rendering (XSS prevention)
- [ ] **SQL Injection**: Parameterized queries or ORM used for database access
- [ ] **Command Injection**: No user input passed to shell commands
- [ ] **Secrets**: No hard-coded credentials, API keys, or secrets
- [ ] **Error Handling**: Internal errors don't leak sensitive information
- [ ] **Authentication**: Auth checks on all protected endpoints
- [ ] **Authorization**: Permission checks before sensitive operations

### Code Quality
- [ ] **Single Responsibility**: Functions/classes have one clear purpose
- [ ] **DRY**: No unnecessary code duplication
- [ ] **Naming**: Variables and functions have descriptive names
- [ ] **Comments**: Complex logic is documented
- [ ] **Type Safety**: Type hints used where applicable
- [ ] **Error Handling**: Errors handled gracefully, not silently ignored

### Performance
- [ ] **Efficiency**: No O(n²) operations that could be O(n)
- [ ] **Resource Management**: Resources (files, connections) properly closed
- [ ] **Caching**: Expensive operations cached where appropriate
- [ ] **Async**: I/O operations are non-blocking where needed

### Testing
- [ ] **Coverage**: Key functionality has test coverage
- [ ] **Edge Cases**: Tests cover boundary conditions
- [ ] **Error Paths**: Error handling is tested

---

## Review Output Format

```markdown
## Code Review Report

### Summary
[OVERALL ASSESSMENT: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]

### Security Issues
| Severity | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| HIGH/MED/LOW | Description | file:line | Fix suggestion |

### Quality Issues
| Priority | Issue | Location | Recommendation |
|----------|-------|----------|----------------|
| P1/P2/P3 | Description | file:line | Fix suggestion |

### Positive Observations
- [What's done well]

### Suggestions for Improvement
- [Optional enhancements]
```

---

## Success Criteria
- [ ] All security issues identified and actionable
- [ ] Code quality issues prioritized
- [ ] Recommendations are specific and actionable
- [ ] Review is constructive, not just critical

