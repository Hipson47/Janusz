# Review Ledger

## Loop 1: Current RC Hardening

- Date: 2026-05-27
- Review findings:
  - P1: `janusz://packages` disclosed sensitive JSON paths.
  - P1: `janusz schema generate-ai` was exposed but did not inject an AI
    analyzer into `SchemaManager`.
- Commands run:
  - targeted failing reproductions for both P1 issues;
  - targeted tests after fixes;
  - `uv lock --check`;
  - `uv sync --group dev --locked`;
  - `uv run ruff check .`;
  - `uv run ruff format --check .`;
  - `uv run mypy src/janusz`;
  - `uv run python -m compileall -q src scripts examples tests`;
  - `uv run pytest tests -q`;
  - `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`;
  - `uv run bandit -q -r src/janusz`;
  - `uv run pip-audit`;
  - `uv build`;
  - `make wheel-smoke`;
  - `make check`;
  - `uv run pre-commit run --all-files`;
  - `make release-check`.
- Results:
  - 64 tests passed;
  - coverage gate passed at 71.49%;
  - Bandit passed;
  - pip-audit found no known vulnerabilities and skipped local `janusz` because
    it is not on PyPI;
  - clean wheel smoke passed;
  - final release-check passed.
- Fixes applied:
  - MCP package discovery now applies root containment and sensitive-path policy;
  - `schema generate-ai` lazily creates and injects an AI analyzer;
  - docs and release readiness reports updated.
- Remaining issues:
  - P2 mutation score/test-depth debt;
  - P2 deterministic MCP discovery and traversal pruning;
  - P2 expanded clean-wheel smoke coverage.

## Fresh Review After Loop 1

- Date: 2026-05-27
- Searches:
  - hardcoded absolute paths;
  - sensitive markers;
  - placeholders and dummy/mock claims;
  - suppressions;
  - optional dependency import leaks;
  - production/beta/experimental docs claims;
  - Makefile/CI/release command drift.
- Result:
  - no unresolved P0/P1 findings.

## Loop 2: Deterministic MCP Package Discovery

- Date: 2026-05-27
- Review findings:
  - P2: MCP package discovery hid sensitive paths but returned filesystem-order
    results and did not prune ignored/sensitive directories before descent.
- Commands run:
  - `uv run pytest tests/test_mcp_server.py::test_mcp_package_discovery_returns_sorted_relative_paths -q`: failed before fix as expected;
  - `uv run pytest tests/test_mcp_server.py::test_mcp_package_discovery_returns_sorted_relative_paths tests/test_mcp_server.py::test_mcp_package_discovery_hides_sensitive_json_paths tests/test_mcp_server.py::test_mcp_package_discovery_skips_symlink_escape -q`: passed after fix;
  - `uv run pytest tests/test_mcp_server.py -q`: passed, 14 tests;
  - `uv run ruff check src/janusz/mcp_server.py tests/test_mcp_server.py`: passed;
  - `uv run ruff format --check src/janusz/mcp_server.py tests/test_mcp_server.py`: passed;
  - `uv run mypy src/janusz`: passed;
  - `make check`: passed, 65 tests.
- Results:
  - deterministic package path ordering is covered;
  - sensitive and symlink escape package discovery tests remain green.
- Fixes applied:
  - `find_json_packages()` now uses sorted `os.walk` traversal;
  - ignored and sensitive directories are pruned before descent;
  - returned package list is globally sorted before limit application.
- Remaining issues:
  - P2 mutation score/test-depth debt;
  - P2 expanded clean-wheel smoke coverage.

## Loop 3: Expanded Clean-Wheel Smoke Coverage

- Date: 2026-05-27
- Review findings:
  - P2: clean-wheel smoke covered help/version, JSON conversion, and skill
    packaging, but not tool manifest or registry integration.
- Commands run:
  - `make wheel-smoke`: passed after adding manifest and registry smoke steps.
  - `make release-check`: passed after the expanded wheel smoke target.
  - `uv run pre-commit run --all-files`: passed.
- Results:
  - the installed wheel now exports `manifest.json`;
  - the installed wheel builds `registry.jsonl`;
  - the installed wheel searches that registry for the generated smoke skill.
- Fixes applied:
  - extended `Makefile` `wheel-smoke` target.
- Remaining issues:
  - P2 mutation score/test-depth debt.
