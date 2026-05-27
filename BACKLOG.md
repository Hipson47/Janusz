# Backlog

## Open Items

### BL-P2-002: Raise Mutation Score for Core Modules

- Severity: P2
- Area: reliability and test quality
- Evidence: latest full `uv run mutmut run --max-children 4` completed with
  3188 mutants processed, 1233 killed, 1708 survived, and 247 no-tests. Loop 4
  added MCP package discovery tests and fixed a dangling JSON symlink listing
  edge case, but the global mutation score remains below the long-term 80%
  target.
- Affected files:
  - `tests/test_json_packager.py`
  - `tests/test_skill_packager.py`
  - `tests/test_skill_quality.py`
  - `tests/test_skill_registry.py`
  - `tests/test_memory.py`
  - `tests/test_mcp_server.py`
- Acceptance criteria:
  - add meaningful non-tautological tests that kill high-value surviving mutants;
  - update mutation testing notes with the new result;
  - do not lower coverage or release gates.
- Validation commands:
  - targeted tests for changed modules
  - `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`
  - `uv run mutmut run`
- Status: open

#### Latest Loop 4 Progress

- Added tests for MCP package discovery limits, the bounded `janusz://packages`
  resource default, non-JSON file traversal, ignored directory pruning, and
  dangling JSON symlinks.
- Fixed package discovery to skip resolved paths that are not files.
- Targeted MCP tests, coverage gate, mypy, Bandit, and `make check` passed.
- Keep this item open and continue with high-value surviving mutants in
  `json_packager`, `skill_quality`, and remaining MCP edge cases.

### BL-P3-001: RAG Persistence Hardening Plan

- Severity: P3
- Area: RAG hardening
- Evidence: RAG remains experimental and has known persistence/provider
  limitations.
- Affected files:
  - `src/janusz/rag/`
  - `docs/PRODUCTION_READINESS.md`
- Acceptance criteria:
  - write an implementation spec before code changes;
  - define provider and persistence contracts;
  - keep unit tests offline with fakes.
- Validation commands:
  - docs/spec review
  - targeted tests if implementation begins
- Status: open

## Completed Items

### BL-P2-001: Deterministic MCP Package Discovery and Traversal Pruning

- Severity: P2
- Area: MCP maturity / security hardening
- Status: completed
- Resolution: Replaced recursive glob package discovery with deterministic
  `os.walk` traversal, sorted resource output, and directory pruning for ignored
  or sensitive paths before descent.

### BL-P2-003: Expand Clean-Wheel Smoke Coverage

- Severity: P2
- Area: packaging reliability
- Status: completed
- Resolution: Wheel smoke now exercises help/version, JSON conversion, skill
  packaging, tool manifest export, registry build, and registry search from the
  installed wheel.

### BL-P1-001: MCP Packages Sensitive Path Disclosure

- Severity: P1
- Area: MCP security
- Status: completed
- Resolution: Shared MCP sensitive path policy with JSON package discovery and
  added tests for sensitive JSON paths and symlink escapes.

### BL-P1-002: Schema Generate-AI Analyzer Wiring

- Severity: P1
- Area: CLI schema/AI integration
- Status: completed
- Resolution: Lazily wired `AIContentAnalyzer` into `SchemaManager` for
  `schema generate-ai` and added offline fake-analyzer and missing-key tests.
