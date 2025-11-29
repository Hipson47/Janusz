# Debug Investigation Template

**Context**: Use this template for investigating runtime errors, bugs, and unexpected behavior.

---

## Error Information

**Error Message**:
```
[PASTE THE FULL ERROR MESSAGE/STACK TRACE HERE]
```

**Context**:
- When does this error occur? [DESCRIBE THE SCENARIO]
- Is it reproducible? [YES/NO/SOMETIMES]
- When did it start? [RECENT CHANGE/ALWAYS/UNKNOWN]

**Relevant Code**:
@code:[FILE_PATH]:[LINE_RANGE]

---

## Investigation Steps

### Step 1: Understand the Error
- What type of error is this?
- What is the immediate cause?
- What is the call stack telling us?

### Step 2: Identify the Root Cause
1. Where does the undefined/null/error value originate?
2. What should the correct data structure/state be?
3. What code path leads to this state?

### Step 3: Trace Data Flow
- Follow the data from input to error point
- Identify where expectations diverge from reality
- Check for missing validation or error handling

---

## Hypothesis and Fix

**Hypothesis**: [EXPLAIN WHY THE ERROR IS OCCURRING]

**Proposed Fix**:
```[language]
// Before
[current code that causes the error]

// After
[corrected code that fixes the error]
```

**Why This Fixes It**: [EXPLAIN THE RATIONALE]

---

## Verification Plan

1. **Reproduce**: Confirm the error before fixing
2. **Apply Fix**: Make the minimal change
3. **Verify**: Confirm error no longer occurs
4. **Regression**: Ensure no new issues introduced
5. **Edge Cases**: Test related scenarios

---

## Prevention

To prevent similar issues in the future:
- [ ] Add proper null/undefined checking
- [ ] Add input validation
- [ ] Add error handling
- [ ] Write a regression test
- [ ] Update documentation if API contract was unclear

---

## Success Criteria
- [ ] Error is resolved without side effects
- [ ] Root cause is understood and documented
- [ ] Proper error handling is added
- [ ] Regression test written
- [ ] Edge cases covered

