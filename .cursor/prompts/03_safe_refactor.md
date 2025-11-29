# Safe Refactoring Template

**Context**: Use this template for restructuring code while maintaining functionality and avoiding breaking changes.

---

## Pre-Refactor Checklist

Before starting, ensure:
- [ ] All existing tests pass
- [ ] Feature branch created (not working on main)
- [ ] Backup/checkpoint available
- [ ] Clear understanding of current behavior
- [ ] Success criteria defined

---

## Refactoring Request

**Target Code**: @code:[FILE_PATH]:[LINE_RANGE]

**Objective**: [DESCRIBE THE REFACTORING GOAL]

Examples:
- "Extract validation logic into a separate, testable function"
- "Split this class following single responsibility principle"
- "Remove duplication by creating a shared utility"

---

## Constraints

**CRITICAL**:
- Maintain backward compatibility with existing API
- Do not change external behavior
- Keep changes minimal and focused
- One logical change at a time

**Forbidden**:
- Changing function signatures without updating all callers
- Removing or renaming public interfaces
- Combining refactor with new features
- Modifying files outside the refactoring scope

---

## Implementation Steps

1. **Analyze Dependencies**
   - Identify all callers of the code being refactored
   - Map the dependency graph
   - Note any external contracts

2. **Write Characterization Tests** (if missing)
   - Capture current behavior in tests
   - These tests must pass before and after refactoring

3. **Execute Refactoring**
   - Make one small change at a time
   - Run tests after each change
   - Review diff before applying

4. **Validate**
   - All tests pass
   - No unintended changes
   - Performance not degraded

---

## Output Format

```markdown
## Refactoring Summary

### Changes Made
- [File 1]: [Description of change]
- [File 2]: [Description of change]

### Tests Updated
- [Test file]: [Reason for update]

### API Compatibility
- [x] All public interfaces unchanged
- [x] All callers updated (if signature changed)

### Verification
- [x] All tests pass
- [x] Manual verification of [key behavior]
```

---

## Success Criteria
- [ ] Existing tests continue to pass
- [ ] No breaking changes to public API
- [ ] Code is cleaner/more maintainable
- [ ] Changes are minimal and focused
- [ ] Documentation updated if needed

