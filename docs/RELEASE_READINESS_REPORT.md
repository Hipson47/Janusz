# Release Readiness Report

Date: 2026-05-27
Version: 1.0.0

## Status

Janusz is ready as a 1.0.0 core release candidate for the stable CLI, JSON
packaging, skill packaging, lint/score, repo ingest, registry, memory, plugin
packaging, tool manifest, and sandboxed MCP integration surface.

Optional AI skill generation, AI/RAG/GUI/schema/prompt/orchestration modules
remain experimental or beta as documented in `docs/PRODUCTION_READINESS.md`.

## Files Changed

- `.cursorignore`
- `.cursorrules`
- `.gitignore`
- `.pre-commit-config.yaml`
- `AI_ENHANCEMENT_PLAN.md`
- `Makefile`
- `docs/ARCHITECTURE.md`
- `docs/PRODUCTION_READINESS.md`
- `docs/progress.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `README.md`
- `pyproject.toml`
- schema JSON files under `schemas/`
- `src/janusz/cli.py`
- `src/janusz/mcp_server.py`
- `src/janusz/ai/ai_content_analyzer.py`
- `src/janusz/ai/skill_generator.py`
- `src/janusz/ai/skill_prompt.py`
- `tests/test_cli_orchestrator_commands.py`
- `tests/test_mcp_server.py`
- `tests/test_ai_integration.py`
- `tests/test_ai_skill_builder.py`
- `uv.lock`
- `docs/REVIEW_FIX_LEDGER.md`
- `docs/REVIEW_FIX_PROGRESS.md`
- `docs/RELEASE_READINESS_REPORT.md`

## Commands Run

| Command | Result |
| --- | --- |
| `hipson route --task "Fresh full production review/fix loop for Janusz 1.0.0: audit, fix, verify, repeat until no P0/P1"` | Passed; advised verify flow. |
| `uv lock` | Passed; regenerated lock after dependency declaration cleanup. |
| `uv lock --check` | Passed. |
| `uv sync --group dev --locked` | Passed; resolved 202 packages and audited 80 packages. |
| `uv run ruff check .` | Passed. |
| `uv run ruff format --check .` | Passed; 56 files already formatted. |
| `uv run mypy src/janusz` | Passed; no issues in 34 source files. |
| `uv run python -m compileall -q src scripts examples tests` | Passed. |
| `uv run pytest tests -q` | Passed; 89 tests. |
| `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70` | Passed; 72.64% total coverage across 89 tests. |
| `uv run bandit -q -r src/janusz` | Passed. |
| `uv run pip-audit` | Passed; no known vulnerabilities found, local `janusz` skipped because it is not on PyPI. |
| `uv build` | Passed; built sdist and wheel. |
| clean wheel smoke in `/tmp/janusz-wheel-test` | Passed; installed wheel, ran `janusz --help`, `janusz --version`, JSON conversion, skill packaging, tool manifest export, registry build, and registry search. |
| `uv run pre-commit run --all-files` | Passed after hook alignment. |
| `uv run mutmut run --max-children 4` | Completed; 3188 mutants processed, 1233 killed, 1708 survived, 247 no-tests. |
| targeted JSON packager mutation run | Completed; 229 mutants processed, 147 killed, 82 survived. |
| targeted MCP/schema P1 tests | Passed; 4 tests. |
| `uv run pytest tests/test_mcp_server.py tests/test_cli_orchestrator_commands.py -q` | Passed; 25 tests. |
| targeted MCP skills resource tests | First reproduced 2 failures, then passed after the fix. |
| `uv run pytest tests/test_mcp_server.py -q` | Passed; 22 tests after MCP skills resource hardening. |
| `uv run pytest tests/test_ai_skill_builder.py -q` | Passed; 8 tests. |
| `make check` | Passed; lint, format, mypy, and 89-test developer gate completed. |
| `make wheel-smoke` | Passed; clean wheel install, `janusz --version`, JSON conversion, skill packaging, manifest export, registry build, and registry search completed. |
| latest `make release-check` | Passed after MCP skills resource hardening and AI Skill Builder; lock, lint, format, mypy, compile, 89-test coverage gate, Bandit, pip-audit, build, wheel smoke, and version check completed. |

## Security Review

- MCP filesystem access remains root-sandboxed, traversal-safe, sensitive-path
  denied, size-limited, and covered by tests.
- MCP package resource discovery uses the same sensitive-path policy and skips
  sensitive JSON files and symlink escapes.
- MCP package resource discovery skips dangling JSON symlinks and other resolved
  paths that are not files.
- MCP skill resource discovery uses no-follow traversal, filters symlink escapes
  and sensitive skill paths, and returns workspace-relative catalog entries.
- Optional AI client no longer imports `httpx` during core module import.
- Experimental AI Skill Builder validates strict draft JSON, rejects secret-like
  draft output, renders files with deterministic Janusz code, and runs existing
  skill lint/score gates.
- `schema generate-ai` lazily wires the AI analyzer and is covered by offline
  fake-analyzer and missing-configuration tests.
- No hardcoded developer path remained in the fresh sweep.
- No legacy-format references remained after hidden/no-ignore search.
- Bandit and pip-audit passed in the local environment.
- Fresh review after the current RC fixes found no unresolved P0/P1 security issues.

## Remaining P2 Items

- Mutation testing is configured and executable, but the current mutation score
  is below the long-term 80% target. The latest full run killed 1233 of 2941
  tested mutants, with 1708 survivors and 247 no-tests. This should drive future
  test-depth work. A later targeted JSON packager run killed 147 of 229
  JSON-packager mutants.
- Optional AI/RAG/GUI/schema/prompt/orchestration modules are not part of the
  hardened 1.0 stable contract and should receive separate hardening before any
  future stability promotion.
- `janusz skill ai` is experimental and should receive real-provider hardening
  before any future stability promotion.

## Blocked Items

None.

## Release Readiness Decision

READY for a 1.0.0 core release candidate: no unresolved P0/P1 issues were found
in the fresh post-fix review, and the required release gates passed locally.
