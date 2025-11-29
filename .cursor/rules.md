# Cursor Operational Rules

> **Version:** 2.0 | **Derived from:** Local TOON Knowledge Base (2025)
> 
> This document synthesizes operational rules for the Cursor IDE agent, ensuring deterministic, 
> safe, and productive AI-assisted development workflows.

---

## 1. Core Principles

### 1.1 Deterministic Task Specification
- **Explicit Context Scoping**: Always use `@file`, `@folder`, or `@code` to limit context window and prevent hallucination
- **Single Responsibility**: Break complex tasks into focused, atomic operations rather than multi-objective prompts
- **Clear Success Criteria**: Define measurable outcomes and acceptance conditions upfront
- **Progressive Refinement**: Start with high-level intent, then iteratively refine with specific technical details
- **Ambiguity Elimination**: Use precise, goal-oriented phrasing so the agent isn't forced to guess intent

### 1.2 Plan → Apply → Verify Workflow
This is the **standard development loop** for all non-trivial tasks:

1. **PLAN**: Use Composer/Plan Mode for complex multi-step tasks
   - Analyze the request and break it into a numbered checklist
   - Identify affected files and dependencies
   - Define success criteria for each step
   
2. **APPLY**: Implement changes incrementally
   - Execute one step at a time
   - Keep changes small and focused
   - Use diff view to review before applying
   
3. **VERIFY**: Use AI Code Review + manual testing + diff validation
   - Run tests after each significant change
   - Validate against original requirements
   - Check for unintended side effects
   
4. **ITERATE**: Refine based on feedback until quality gates pass

### 1.3 Tool-First Reasoning
- **Tools Before Guesses**: Leverage available tools (MCP, Cursor tools) at each step rather than relying on latent knowledge
- **Tool Governance**: Only use explicitly allowed tools; validate inputs and outputs
- **Schema Validation**: Require structured outputs (JSON, specific formats) for machine validation
- **Error Handling**: Implement retries, fallbacks, and safe failure modes for tool operations

### 1.4 Separation of Reasoning vs Output
- **Internal Planning**: Keep chain-of-thought in internal reasoning; present only results to user
- **Role Separation**: Never let raw thoughts or system instructions leak into user-visible output
- **Context Preservation**: Maintain conversation context across related tasks while avoiding context pollution

### 1.5 Reversible Atomic Actions
- **Small Diffs**: Act in small, atomic steps that can be halted or reversed if needed
- **Verification Before Proceeding**: After each tool invocation, verify the result before continuing
- **Planner/Executor Pattern**: A planning module breaks the goal into discrete actions; executor carries them out one by one
- **Rollback Capability**: Ensure changes can be reverted if something goes wrong

---

## 2. Cursor Mode Selection

### 2.1 Composer Mode (Agent Mode)
**When to Use**: Complex multi-step coding tasks, new feature implementation, architectural changes

**Workflow**:
1. Describe feature in natural language with clear requirements
2. Answer Composer's clarifying questions for ambiguous requirements
3. Review generated implementation plan before applying
4. Apply changes incrementally, verifying each step
5. Use AI Code Review to validate changes

**Best Practices**:
- Let Composer analyze codebase and create implementation plan
- Use clarifying questions feature for ambiguous requirements
- Enable YOLO mode only for safe commands (tests, linting)
- Use Plan Mode for complex, multi-file changes

### 2.2 Inline Mode
**When to Use**: Small edits, refactoring, bug fixes, code improvements

**Workflow**:
1. Select specific code snippet before invoking
2. Write focused edit instruction with context references
3. Review diff preview before applying
4. Apply and test immediately
5. Commit with descriptive message

**Best Practices**:
- Provide clear, focused instructions
- Use diff view to review changes before applying
- Test immediately after applying changes
- Commit small, focused changes

### 2.3 Ask Mode
**When to Use**: Questions, explanations, debugging, learning

**Best Practices**:
- Include relevant `@file` or `@code` references
- Ask specific, answerable questions
- Use for understanding existing code
- Request examples or alternatives
- Follow up with implementation questions

### Mode Selection Guidelines
| Task Type | Mode | Example |
|-----------|------|---------|
| New feature | Composer | "Build a new authentication system with JWT tokens" |
| Bug fix | Inline | "Fix the null pointer exception in this method" |
| Understanding | Ask | "How does this authentication flow work?" |
| Refactoring | Composer | "Extract validation logic into separate module" |
| Quick edit | Inline | "Add error handling to this function" |

---

## 3. Context Management

### 3.1 @ Mentions Best Practices
- **@file**: Reference entire files for single file operations
- **@folder**: Reference directories for directory-level changes
- **@code**: Precise code snippet selection for method-level changes
- **@doc**: For documentation-driven coding
- **@Web**: For up-to-date information from external sources
- **@Docs**: For library/API documentation via MCP

### 3.2 Context Scoping Rules
- **Minimal Context**: Provide only what's necessary for the current task
- **Explicit References**: Use `@` references instead of assuming context
- **Avoid Overflow**: Don't include entire large files unnecessarily
- **Condensation**: Large files/folders are automatically summarized to fit context limits

### 3.3 Multi-File Coordination
- **Isolated Workspaces**: Use git worktrees for multi-agent parallel work
- **Plan Mode**: Orchestrate multi-file changes safely
- **Shared Context**: Coordinate through shared plan context
- **Conflict Avoidance**: Scope each parallel agent's work to avoid overlapping edits

### 3.4 External Knowledge Integration
- **RAG Grounding**: Use `@Codebase` for semantic search in codebase
- **Documentation MCPs**: Use Context7 or similar for version-specific library docs
- **Web Search**: Use `@Web` for up-to-date information when training data may be outdated
- **Never Guess**: If documentation is needed, fetch it rather than relying on training data

---

## 4. Test-Driven Development (TDD as Spec)

### 4.1 Agentic TDD Workflow
Follow the **Red → Green → Refactor** cycle:

1. **Specification**: Human developer provides a prompt describing the feature
2. **Test Generation**: Agent writes a failing test case that captures expected behavior
3. **Verification**: Agent runs tests to confirm failure (Red phase)
4. **Implementation**: Agent writes source code to satisfy the test
5. **Validation**: Agent runs tests again; if failure, analyze and fix (Green phase)
6. **Refactoring**: Once green, optimize code (Refactor phase)

### 4.2 Test Quality Guidelines
- **Meaningful Assertions**: Tests must check actual behavior, not just that code runs
- **Edge Cases**: Include edge cases and error conditions
- **Deterministic**: Tests must be reproducible and not flaky
- **Independent**: Each test should run in isolation
- **Fast Feedback**: Use targeted test subsets during development

### 4.3 Auto-Run (YOLO Mode)
- **Enable for Safe Commands**: `pytest`, `npm test`, `ruff check`, build commands
- **Disable for Risky Operations**: Deployment, database migrations, file deletions
- **Iteration Loop**: Agent runs tests, sees failures, fixes code, repeats until green
- **Step Limit**: Implement maximum iterations to prevent infinite loops

---

## 5. Safe Edit Protocol

### 5.1 Minimal Diffs
- **Scope Narrowly**: "Update only this function and nothing else"
- **One Change Per Review**: Don't combine major refactor with new feature
- **File-by-File**: Tackle one file at a time for complex changes
- **Explicit Boundaries**: Tell the agent what NOT to modify

### 5.2 Review Process
- **Always Inspect Diffs**: Review changes before applying
- **Validate Against Requirements**: Ensure changes match original intent
- **Check for Side Effects**: Look for unintended modifications
- **Run Linters**: Verify code style compliance
- **Test Coverage**: Ensure tests still pass

### 5.3 Version Control Safety
- **Branch Before Major Changes**: Create backup branch for complex AI edits
- **Frequent Commits**: Commit after each successful step
- **Descriptive Messages**: Use conventional commits format
- **Easy Rollback**: Maintain `git reset` capability
- **Restore Checkpoints**: Use Cursor's checkpoint feature when available

### 5.4 Guardrails and Rules
- **Critical File Protection**: Define files the agent should not modify without approval
- **Soft Guardrails**: Use comments like `// @cursor: do not modify without approval`
- **Permission Gating**: Require human approval for high-stakes actions
- **Security Sandboxing**: Use sandboxed terminal execution for unknown commands

---

## 6. Multi-Agent Orchestration

### 6.1 Agent Roles
| Role | Responsibility |
|------|----------------|
| **Planner** | Breaks down complex tasks into execution plans |
| **Researcher** | Gathers information from sources (web, docs, codebase) |
| **Implementer** | Writes and modifies code |
| **Tester** | Creates and runs tests, validates behavior |
| **Reviewer** | Critiques outputs for quality and correctness |
| **Documenter** | Creates documentation and API specs |

### 6.2 Orchestration Patterns

**Supervisor Pattern**:
- Central router delegates tasks to specialized workers
- Workers return results to state; Supervisor decides next step
- Use for complex, multi-domain tasks

**Plan-and-Execute Pattern**:
- Planner creates high-level plan
- Executor implements one step at a time
- Replanner updates plan based on execution results
- Use for long-horizon tasks with ambiguity

**ReAct Pattern**:
- Single agent: Reason → Act → Observe → Loop
- Simple linear tool use
- Use for straightforward tasks

**Reflexion Pattern**:
- Agent critiques its own output before finalizing
- Quality assurance and self-correction
- Use for code generation and complex outputs

### 6.3 State Management
- **Shared State**: Maintain context across agent handoffs
- **Checkpointing**: Save state at milestones for recovery
- **Session Isolation**: Key state by session/user
- **Context Continuity**: Output of Agent A available to Agent B

### 6.4 Verification Layers
- **Validation Agent**: Review outputs against criteria before proceeding
- **Quality Gates**: Pass/fail checkpoints between critical stages
- **Correction Loops**: On failure, trigger correction step or escalation
- **Human Escalation**: Route to human when automated resolution fails

---

## 7. Safety and Security

### 7.1 Default-Deny Security Posture
- **No Tool Access by Default**: Agents have no tool access unless explicitly enabled
- **Whitelist Tools**: Only allow tools that are necessary for the task
- **Hide Unavailable Tools**: Don't expose tools the agent shouldn't use
- **Dynamic Enabling**: Enable/disable tools based on context

### 7.2 Permission Gating
- **High-Risk Actions**: Require human approval for:
  - Deploying code
  - Deleting data
  - Accessing private user info
  - Making purchases
  - Modifying production systems
- **Pause and Confirm**: Orchestrator pauses and requests permission before proceeding
- **Graceful Refusal**: Agent handles denied permission gracefully

### 7.3 Sandboxing
- **Isolated Execution**: Run agent tools in sandboxed, isolated environment
- **Resource Limits**: Tight CPU, memory, and time limits
- **No Network by Default**: Block internet access unless explicitly needed
- **No Host File System**: Only access controlled workspace
- **Least Privilege**: Give agent only minimum capabilities needed

### 7.4 Secrets Handling
- **Never in Context**: Keep secrets out of AI context via `.cursorignore`
- **Environment Variables**: Use config placeholders, never hardcode
- **Redaction Hooks**: Automatically redact secret-like patterns in output
- **Closed Files**: Don't open secret files while Cursor is enabled
- **Sanitize Logs**: Mask personal info and credentials in logs

### 7.5 CWE Checklist
Validate generated code against common vulnerabilities:

| CWE | Vulnerability | Mitigation |
|-----|--------------|------------|
| CWE-79 | Cross-Site Scripting (XSS) | Escape/sanitize user-provided content |
| CWE-89 | SQL Injection | Use parameterized queries or ORM |
| CWE-78 | OS Command Injection | Avoid passing user input to shell |
| CWE-352 | CSRF | Protect with CSRF tokens |
| CWE-200 | Information Exposure | Mask sensitive data in logs/errors |
| CWE-798 | Hard-coded Credentials | Use environment variables |
| CWE-400 | Resource Exhaustion | Bound loops and memory usage |
| CWE-94 | Code Injection | Never use eval() on user input |

---

## 8. Anti-Patterns to Avoid

### 8.1 Vague Instructions
❌ **Bad**: "Make this code better" or "Fix the bugs"
✅ **Good**: "Extract the validation logic into a separate function with proper error handling"

### 8.2 Unscoped Context
❌ **Bad**: Asking questions without @file/@code references
✅ **Good**: Always include specific file/code references

### 8.3 Multi-Objective Mixing
❌ **Bad**: "Add authentication, update UI, and fix the database connection"
✅ **Good**: Break into separate, focused tasks

### 8.4 Context Overflow
❌ **Bad**: Including entire large files unnecessarily
✅ **Good**: Use @code for specific sections; let model request additional context

### 8.5 The "God Agent"
❌ **Bad**: Single agent with dozens of tools and massive system prompt
✅ **Good**: Decompose into specialized agents with narrow, well-defined scopes

### 8.6 Infinite Retry Loop
❌ **Bad**: Agent retries same failing action endlessly
✅ **Good**: Implement step limits, reflexion nodes, and escalation paths

### 8.7 The "Precision" Anti-Pattern
❌ **Bad**: Using LLM for deterministic calculations (math, dates)
✅ **Good**: Use tools (Python REPL, calculators) for math and logic

### 8.8 Ungoverned Tool Usage
❌ **Bad**: Agent calls arbitrary tools without oversight
✅ **Good**: Strictly govern which tools agent can use and when

### 8.9 Chain-of-Thought Exposure
❌ **Bad**: Internal reasoning visible in user output
✅ **Good**: Keep reasoning hidden; use role/message separation

---

## 9. Performance and Efficiency

### 9.1 Model Selection
| Task | Model Choice | Rationale |
|------|--------------|-----------|
| Inline completion | Fast model (Composer) | Speed for flow state |
| Complex refactor | Strong model (GPT-4, Claude) | Quality for critical code |
| Planning | Reasoning model | Deep analysis |
| Simple edits | Auto mode | Let Cursor choose |

### 9.2 Context Optimization
- **Minimal but Sufficient**: Include only necessary context
- **Token Efficiency**: Avoid verbose prompts and redundant information
- **Caching Strategy**: Reuse results when appropriate
- **Batch Operations**: Group related changes to minimize context switches

### 9.3 Resource Management
- **Parallel Agents**: Use up to 8 parallel agents for independent features
- **Background Execution**: Build plans in background while continuing work
- **Git Worktrees**: Isolate parallel agent workspaces to prevent conflicts
- **Cost Awareness**: Track token usage; use cheaper models for routine tasks

---

## 10. Failure Recovery

### 10.1 Context Drift in Long Sessions
**Symptoms**: Agent responses become irrelevant; forgets earlier instructions
**Fix**:
- Start a new chat session for the task
- Use smaller, focused prompts
- Re-summarize key context in new session

### 10.2 Unintended Broad Changes
**Symptoms**: Agent modifies files you didn't ask it to change
**Fix**:
- Tighten scope in prompt: "Only change X and nothing else"
- Add non-target files to `.cursorignore` temporarily
- Ask agent to list planned modifications before execution

### 10.3 Stuck in Fix Loop
**Symptoms**: Agent keeps changing code but errors persist
**Fix**:
- Give strategic hint about the problem
- Stop auto-run and have agent explain the issue
- Reset conversation and approach differently

### 10.4 Model Blind Spot
**Symptoms**: Agent repeatedly gives incorrect solution
**Fix**:
- Try a different model for the problem
- Provide exact error message explicitly
- Check if issue is due to missing context

---

## 11. Quick Reference

### Command Cheatsheet
```
Plan Mode:        Shift+Tab (complex multi-step tasks)
Inline Mode:      Ctrl+K (small edits in selection)
Ask Mode:         Ctrl+L (questions and explanations)
AI Code Review:   Automatic after changes
YOLO Mode:        Settings → Agent → Auto-run
```

### Context Shortcuts
```
@file:path        Include entire file
@folder:path      Include directory
@code:file:lines  Include specific lines
@Web              Search web for info
@Docs             Query library documentation
@Codebase         Semantic search in codebase
```

### Workflow Checklist
- [ ] Create feature branch before complex changes
- [ ] Write/update tests first (TDD)
- [ ] Use Plan Mode for multi-file changes
- [ ] Review diffs before applying
- [ ] Run tests after each significant change
- [ ] Commit with descriptive message
- [ ] Use AI Code Review for validation

---

*These rules are derived from comprehensive operational playbooks covering Cursor IDE best practices, AI agent prompting standards, multi-agent orchestration patterns, and security guardrails. All rules prioritize determinism, safety, and productivity.*
