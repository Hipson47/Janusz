# Cursor Operational Rules and Templates

> **Derived from:** Local TOON Knowledge Base (2025)
> **Version:** 2.1

This directory contains operational rules and reusable prompt templates for effective Cursor IDE usage, synthesized from comprehensive knowledge base analysis.

---

## 📁 Directory Structure

```
project-root/
├── .cursorrules                    # ← GLOBAL RULES (auto-loaded every conversation)
└── .cursor/
    ├── README.md                   # This file
    ├── rules.md                    # Detailed reference documentation
    ├── rules/                      # ← CONTEXTUAL RULES (.mdc format)
    │   ├── python-development.mdc  # Applied to *.py files
    │   ├── fastapi-endpoints.mdc   # Applied to routes/api files
    │   ├── testing.mdc             # Applied to test files
    │   ├── security.mdc            # ALWAYS applied (alwaysApply: true)
    │   └── agent-orchestration.mdc # Applied to agent/workflow files
    └── prompts/                    # Reusable prompt templates
        ├── 01_plan_then_execute.md
        ├── 02_tdd_workflow.md
        ├── 03_safe_refactor.md
        ├── 04_debug_investigate.md
        ├── 05_code_review.md
        ├── 06_api_endpoint.md
        └── 07_multi_agent_orchestrator.md
```

---

## 🔑 How Cursor Loads Rules

### File Format Comparison

| Format | Location | Auto-loaded? | When Applied |
|--------|----------|--------------|--------------|
| `.cursorrules` | Project root | ✅ **ALWAYS** | Every conversation |
| `.mdc` | `.cursor/rules/` | ✅ Contextual | When `globs` match or `alwaysApply: true` |
| `.md` | Anywhere | ❌ Manual | Only when @file referenced |

### `.cursorrules` (Global Contract)
The `.cursorrules` file in the project root is your **primary contract** with Cursor. It's automatically injected into EVERY conversation - no manual reference needed.

### `.mdc` Files (Contextual Rules)
MDC (Markdown Component) files in `.cursor/rules/` have YAML frontmatter:

```yaml
---
description: When this rule applies
globs: ["**/*.py"]        # File patterns to match
alwaysApply: false        # Or true for security rules
---

# Rule content here...
```

- `globs`: Rule applies when you're working on matching files
- `alwaysApply: true`: Rule ALWAYS applies (use for security)

### `.md` Files (Documentation)
Regular Markdown files are NOT auto-loaded. They serve as:
- Reference documentation for humans
- Templates to copy/paste into prompts
- Detailed explanations beyond terse rules

---

## 🚀 Quick Start

### 1. Understand the Core Workflow

The fundamental workflow for all non-trivial tasks is **Plan → Apply → Verify**:

1. **PLAN**: Use Composer/Plan Mode (Shift+Tab) to break down complex tasks
2. **APPLY**: Implement changes incrementally with diff review
3. **VERIFY**: Run tests and AI Code Review to validate
4. **ITERATE**: Refine until quality gates pass

### 2. Choose the Right Mode

| Task Type | Mode | Shortcut |
|-----------|------|----------|
| Complex multi-step | Composer | Shift+Tab |
| Small focused edit | Inline | Ctrl+K |
| Questions/learning | Ask | Ctrl+L |

### 3. Use Context References

Always scope your context with `@` mentions:
- `@file:path` - Include entire file
- `@folder:path` - Include directory
- `@code:file:lines` - Specific code section
- `@Web` - Search web for info
- `@Docs` - Query library docs

---

## 📋 Template Usage Guide

### Plan-Then-Execute (`01_plan_then_execute.md`)
**When**: Complex features, architectural changes, multi-file edits
**How**: Copy template, fill in task description, follow phases

### TDD Workflow (`02_tdd_workflow.md`)
**When**: New features, bug fixes, any code changes
**How**: Follow Red-Green-Refactor cycle

### Safe Refactor (`03_safe_refactor.md`)
**When**: Restructuring code without changing behavior
**How**: Use pre-refactor checklist, maintain backward compatibility

### Debug Investigation (`04_debug_investigate.md`)
**When**: Runtime errors, bugs, unexpected behavior
**How**: Provide error trace, follow systematic investigation

### Code Review (`05_code_review.md`)
**When**: Before merging, security audit, quality check
**How**: Run through checklist, document findings

### API Endpoint (`06_api_endpoint.md`)
**When**: Creating new REST endpoints
**How**: Fill in specification, follow implementation checklist

### Multi-Agent Orchestrator (`07_multi_agent_orchestrator.md`)
**When**: Complex tasks requiring multiple specialized agents
**How**: Define agents, set up workflow, coordinate handoffs

---

## 🔒 Security Guidelines

### Protected Knowledge Base

The folder `baza wiedzy 28.11/` contains private knowledge and is:
- ✅ Listed in `.gitignore` (never committed)
- ✅ Listed in `.cursorignore` (never indexed by Cursor)
- ❌ Must never be referenced in public documentation
- ❌ Must never have contents copied verbatim

### Secrets Handling

- Use `.cursorignore` to exclude sensitive files from AI context
- Never hardcode credentials - use environment variables
- Close secret files while working with Cursor
- Review AI-generated code for accidental secret exposure

---

## 🎯 Key Principles

### 1. Deterministic Prompting
- Be explicit with context (`@file`, `@code`)
- Single responsibility per prompt
- Clear success criteria
- Avoid vague instructions

### 2. Test-Driven Development
- Write tests first (Red)
- Minimal implementation (Green)
- Refactor with safety net (Refactor)

### 3. Safe Edits
- Small, focused diffs
- Always review before applying
- Feature branch for complex changes
- Frequent commits for rollback capability

### 4. Tool-First Reasoning
- Use tools before relying on model knowledge
- Validate outputs with schemas
- Handle errors gracefully

---

## 🔄 Mode Selection Guidelines

```
Composer Mode (Complex Tasks)
└── "Build a new authentication system with JWT tokens"
└── "Refactor the database layer to use async patterns"
└── "Implement the full user registration flow"

Inline Mode (Quick Edits)
└── "Fix the null pointer exception in this method"
└── "Add error handling to this function"
└── "Rename this variable for clarity"

Ask Mode (Questions)
└── "How does this authentication flow work?"
└── "What's the purpose of this class?"
└── "Explain the difference between X and Y"
```

---

## ⚠️ Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Vague instructions | Unpredictable results | Be explicit and specific |
| Unscoped context | Hallucinations | Always use `@` references |
| Multi-objective prompts | Incomplete results | One task at a time |
| Skipping tests | Hidden bugs | Always verify with tests |
| Large diffs | Review fatigue | Small, incremental changes |

---

## 📖 Additional Resources

- **rules.md**: Complete operational rules reference
- **prompts/**: Full template library
- **Cursor Docs**: https://cursor.com/docs

---

*These rules ensure deterministic, safe, and productive AI-assisted development.*
