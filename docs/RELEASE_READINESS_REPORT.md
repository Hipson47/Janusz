# Release Readiness Report

Date: 2026-05-27
Version: 1.0.0

## Status

Janusz is ready as a 1.0.0 core release candidate for the stable CLI, JSON
packaging, skill packaging, lint/score, repo ingest, registry, memory, plugin
packaging, tool manifest, and sandboxed MCP integration surface.

Optional AI/RAG/GUI/schema/prompt/orchestration modules remain experimental or
beta as documented in `docs/PRODUCTION_READINESS.md`.

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
- `tests/test_cli_orchestrator_commands.py`
- `tests/test_mcp_server.py`
- `tests/test_ai_integration.py`
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
| `uv run ruff format --check .` | Passed; 53 files already formatted. |
| `uv run mypy src/janusz` | Passed; no issues in 32 source files. |
| `uv run python -m compileall -q src scripts examples tests` | Passed. |
| `uv run pytest tests -q` | Passed; 64 tests. |
| `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70` | Passed; 71.49% total coverage. |
| `uv run bandit -q -r src/janusz` | Passed. |
| `uv run pip-audit` | Passed; no known vulnerabilities found, local `janusz` skipped because it is not on PyPI. |
| `uv build` | Passed; built sdist and wheel. |
| clean wheel smoke in `/tmp/janusz-wheel-test` | Passed; installed wheel, ran `janusz --help`, `janusz --version`, JSON conversion, and skill packaging. |
| `uv run pre-commit run --all-files` | Passed after hook alignment. |
| `uv run mutmut run` | Completed; 3138 mutants processed, 1178 killed, 1713 survived, 247 no-tests. |
| targeted MCP/schema P1 tests | Passed; 4 tests. |
| `uv run pytest tests/test_mcp_server.py tests/test_cli_orchestrator_commands.py -q` | Passed; 25 tests. |
| `make check` | Passed; lint, format, mypy, and 64-test developer gate completed. |
| `make wheel-smoke` | Passed; clean wheel install, `janusz --version`, JSON conversion, and skill packaging completed. |
| `make release-check` | Passed; lock, lint, format, mypy, compile, coverage, Bandit, pip-audit, build, wheel smoke, and version check completed. |

## Security Review

- MCP filesystem access remains root-sandboxed, traversal-safe, sensitive-path
  denied, size-limited, and covered by tests.
- MCP package resource discovery uses the same sensitive-path policy and skips
  sensitive JSON files and symlink escapes.
- Optional AI client no longer imports `httpx` during core module import.
- `schema generate-ai` lazily wires the AI analyzer and is covered by offline
  fake-analyzer and missing-configuration tests.
- No hardcoded developer path remained in the fresh sweep.
- No legacy-format references remained after hidden/no-ignore search.
- Bandit and pip-audit passed in the local environment.
- Fresh review after the current RC fixes found no unresolved P0/P1 security issues.

## Remaining P2 Items

- Mutation testing is configured and executable, but the current mutation score
  is below the long-term 80% target. This should drive future test-depth work.
- Optional AI/RAG/GUI/schema/prompt/orchestration modules are not part of the
  hardened 1.0 stable contract and should receive separate hardening before any
  future stability promotion.

## Blocked Items

None.

## Release Readiness Decision

READY for a 1.0.0 core release candidate: no unresolved P0/P1 issues were found
in the fresh post-fix review, and the required release gates passed locally.
