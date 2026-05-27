# Backlog

## Open Items

### BL-P2-002: Raise Mutation Score for Core Modules

- Severity: P2
- Area: reliability and test quality
- Evidence: `uv run mutmut run` completed with 3138 mutants processed, 1178
  killed, 1713 survived, and 247 no-tests.
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
