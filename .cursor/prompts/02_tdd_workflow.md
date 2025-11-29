# Test-Driven Development (TDD) Template

**Context**: Use this template for implementing new features or fixing bugs using the Red-Green-Refactor cycle.

---

## Phase 1: Red (Write Failing Test)

**Feature/Bug Description**: [DESCRIBE WHAT YOU'RE IMPLEMENTING]

First, write a test case that defines the expected behavior:

**Requirements**:
- Test must fail initially (confirms we're testing the right thing)
- Test must be specific and focused on one behavior
- Include edge cases and error conditions
- Use existing test framework patterns

**Output**:
```python
# tests/test_[feature].py

def test_[specific_behavior]():
    """
    Test that [expected behavior].
    
    Given: [preconditions]
    When: [action]
    Then: [expected result]
    """
    # Arrange
    ...
    
    # Act
    ...
    
    # Assert
    assert [expected_condition]
```

**Verification**: Run `pytest tests/test_[feature].py -v` and confirm test fails.

---

## Phase 2: Green (Minimal Implementation)

Write the **minimum code** necessary to make the test pass:

**Guidelines**:
- Focus only on satisfying the test
- Don't over-engineer or add extra features
- Follow existing code patterns and conventions
- Keep implementation simple

**Verification**: Run tests until all pass.

---

## Phase 3: Refactor (Improve Code Quality)

With tests green, improve the code:

**Consider**:
- Remove duplication (DRY)
- Improve naming and readability
- Extract helper functions if needed
- Ensure proper error handling
- Add docstrings and type hints

**Verification**: Tests must remain green after refactoring.

---

## Iteration Loop

If tests fail during implementation:
1. Read the error message carefully
2. Identify the root cause
3. Fix the specific issue
4. Run tests again
5. Repeat until green

---

## Success Criteria
- [ ] Test written and initially fails (Red)
- [ ] Implementation makes test pass (Green)
- [ ] Code refactored for quality (Refactor)
- [ ] All existing tests still pass
- [ ] Edge cases covered
- [ ] Code follows project conventions

