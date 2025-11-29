# Function Refactoring Template

**Context**: Use this template for extracting, restructuring, or optimizing function-level code.

**Task**: Refactor this function to extract the validation logic into a separate, testable function.

**Requirements**:
- Create a new function `validateUserInput(data)` that:
  - Takes user input data as parameter
  - Returns validation result object with {isValid: boolean, errors: string[]}
  - Handles all edge cases from the original function
- Maintain backward compatibility with existing API
- Follow single responsibility principle

**Code Reference**:
@code:src/utils/validation.js:15-25

**Success Criteria**:
- All existing tests pass
- New validation function is independently testable
- No breaking changes to public API
- Improved code readability and maintainability
