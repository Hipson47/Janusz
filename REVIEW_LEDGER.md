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

## Loop 4: MCP Mutation Coverage and Dangling Symlink Handling

- Date: 2026-05-27
- Review findings:
  - P2: mutation testing showed surviving MCP package discovery mutants around
    limits, traversal, ignored directories, and non-file JSON paths.
  - P2: a new dangling JSON symlink test exposed that package discovery could
    report a non-existent symlink target as a package entry.
- Commands run:
  - `uv run mutmut run --max-children 4`: completed, 3188 mutants processed,
    1233 killed, 1708 survived, 247 no-tests.
  - targeted `mutmut` run for selected `find_json_packages` mutants: several
    traversal/limit mutants killed; default-limit and equivalent negative-limit
    mutants still survived.
  - `uv run ruff check src/janusz/mcp_server.py tests/test_mcp_server.py`:
    passed.
  - `uv run ruff format --check src/janusz/mcp_server.py tests/test_mcp_server.py`:
    passed after formatting the new tests.
  - `uv run pytest tests/test_mcp_server.py -q`: passed, 19 tests.
  - `uv run mypy src/janusz`: passed.
  - `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`:
    passed, 70 tests, 71.65% coverage.
  - `uv run bandit -q -r src/janusz`: passed.
  - `git diff --check`: passed.
  - `make check`: passed, 70 tests.
  - `make release-check`: passed, including lock check, lint, format, mypy,
    compileall, coverage, `pip-audit`, build, and expanded wheel smoke.
- Results:
  - MCP package discovery now has tests for explicit limits, default resource
    bounds, non-JSON file traversal, ignored directory pruning, and dangling
    JSON symlink handling.
  - Global mutation score remains below the long-term 80% target, so
    `BL-P2-002` remains open.
- Fixes applied:
  - `find_json_packages()` now skips resolved paths that are not files.
- Remaining issues:
  - P2 mutation score/test-depth debt in `json_packager`, `skill_quality`, and
    remaining core modules.

## Fresh Review After Loop 4

- Date: 2026-05-27
- Searches:
  - hardcoded absolute paths and developer usernames;
  - sensitive markers and placeholder values;
  - broad suppressions and skipped-test markers;
  - optional dependency import references;
  - production/beta/experimental documentation claims.
- Result:
  - no unresolved P0/P1 findings;
  - matches were expected policy markers, tests, documented experimental RAG/GUI
    placeholders, or lazy optional imports.
