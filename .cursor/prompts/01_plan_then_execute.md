# Plan-Then-Execute Workflow Template

**Context**: Use this template for complex multi-step tasks requiring careful planning before implementation.

---

## Phase 1: Planning

**Task**: [DESCRIBE THE FEATURE OR CHANGE]

Before writing any code, analyze this request and create a detailed execution plan:

1. **Understand Requirements**
   - What is the core objective?
   - What are the success criteria?
   - What constraints apply?

2. **Analyze Codebase**
   - Which files will be affected?
   - What dependencies exist?
   - Are there existing patterns to follow?

3. **Create Execution Plan**
   - List all steps as a numbered checklist
   - Reference specific files or functions for each step
   - Identify potential risks or blockers

**Output Format**:
```markdown
## Execution Plan

### Objective
[Clear statement of what we're building]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Steps
1. [ ] Step 1 - @file:path/to/file.py
2. [ ] Step 2 - @file:path/to/other.py
...

### Risks
- Risk 1: [Description] → Mitigation: [Plan]
```

---

## Phase 2: Execution

**Do not proceed until the plan is approved.**

Execute the plan step by step:
- Complete one step at a time
- Verify each step before proceeding
- Run tests after each significant change
- Update the checklist as steps complete

---

## Phase 3: Verification

After all steps are complete:
1. Run the full test suite
2. Review all diffs for unintended changes
3. Validate against success criteria
4. Document any deviations from plan

---

## Success Criteria
- All planned steps completed
- Tests pass
- No unintended side effects
- Code follows project conventions

