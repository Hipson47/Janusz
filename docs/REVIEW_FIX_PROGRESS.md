# Review/Fix Progress

Date: 2026-05-27

## Loop 1: Baseline Review and Fix Batch

Completed a repository-wide production review focused on packaging, dependency
model, CI/release gates, optional-module imports, pre-commit consistency,
mutation-test readiness, hidden stale format references, and documentation
accuracy.

Fixed:

- removed the duplicate `dev` package extra and regenerated `uv.lock`;
- made optional AI `httpx` import lazy and actionable;
- aligned pre-commit `mypy` with the same command used by local release gates;
- repaired mutmut configuration for current mutmut behavior;
- removed hidden legacy-format references;
- updated stale quality-gate documentation;
- accepted final-newline fixes from pre-commit.

Verification run in this loop:

- `uv lock --check`: passed
- `uv sync --group dev --locked`: passed
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run mypy src/janusz`: passed
- `uv run python -m compileall -q src scripts examples tests`: passed
- `uv run pytest tests -q`: passed, 60 tests
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`: passed, 70.87%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed, no known vulnerabilities found; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- clean wheel smoke: passed
- `uv run pre-commit run --all-files`: passed after hook fix
- `uv run mutmut run`: completed with substantial remaining survivors tracked as P2
- `make release-check`: passed

## Loop 2: Fresh Review

Performed a fresh post-fix review instead of only rechecking the original issue
list.

Fresh searches performed:

- hardcoded paths and developer usernames;
- hidden/no-ignore legacy-format search;
- TODO/FIXME/HACK/dummy/mock/placeholder/nosec/type-ignore/skip/xfail/broad exception sweep;
- optional dependency import sweep;
- CI, Makefile, and documentation command consistency sweep.

Result:

- zero unresolved P0/P1 findings;
- remaining mutation score/test-depth gap documented as P2;
- release-check and pre-commit gates passed after the fix batch.

## Loop 3: Current RC P1 Fixes

Reproduced and fixed two current release-candidate blockers:

- `janusz://packages` disclosed sensitive JSON paths such as cloud credentials,
  environment JSON, token JSON, and symlink escapes;
- `janusz schema generate-ai` did not inject an AI analyzer into `SchemaManager`
  and returned misleading API-key guidance.

Added offline tests for both fixes. Targeted verification passed:

- `uv run pytest tests/test_mcp_server.py::test_mcp_package_discovery_hides_sensitive_json_paths tests/test_mcp_server.py::test_mcp_package_discovery_skips_symlink_escape tests/test_cli_orchestrator_commands.py::test_cli_schema_generate_ai_uses_lazy_analyzer tests/test_cli_orchestrator_commands.py::test_cli_schema_generate_ai_missing_key_is_actionable -q`: passed, 4 tests
- `uv run pytest tests/test_mcp_server.py tests/test_cli_orchestrator_commands.py -q`: passed, 25 tests
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed after formatting the new CLI test
- `uv run mypy src/janusz`: passed
- `uv run pytest tests -q`: passed, 64 tests
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`: passed, 71.49%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed, no known vulnerabilities found; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- `make wheel-smoke`: passed
- `make check`: passed
- `make release-check`: passed

## Loop 4: Fresh Review After Current RC Fixes

Performed a fresh review after the MCP and schema fixes. Searches covered:

- hardcoded absolute paths;
- sensitive markers and placeholder values;
- optional dependency import leaks in core paths;
- suppressions such as `nosec`, `noqa`, `skip`, and `xfail`;
- production, beta, and experimental documentation claims;
- Makefile, CI, and release gate drift.

Result:

- zero unresolved P0/P1 findings;
- MCP package discovery no longer discloses sensitive JSON paths;
- `schema generate-ai` is accurately wired and remains documented as experimental;
- optional AI/RAG/GUI modules remain outside the hardened stable 1.0 contract.
