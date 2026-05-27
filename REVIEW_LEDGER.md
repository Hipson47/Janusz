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

## Loop 5: JSON Packager Mutation Coverage

- Date: 2026-05-27
- Review findings:
  - P2: mutation results showed weak direct tests around JSON packager helpers,
    especially `validate_json_file`, `convert_directory`, and
    `inspect_json_package`.
- Commands run:
  - `uv run pytest tests/test_json_packager.py -q`: passed, 12 tests.
  - `uv run mutmut run --max-children 4 'janusz.json_packager.*'`: completed
    targeted JSON packager mutation testing, 229 mutants processed, 147 killed,
    82 survived.
  - `uv run ruff check tests/test_json_packager.py`: passed.
  - `uv run ruff format --check tests/test_json_packager.py`: passed.
  - `uv run mypy src/janusz`: passed.
  - `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`:
    passed, 78 tests, 72.41% coverage.
  - `uv run pytest tests -q`: passed, 78 tests.
  - `make check`: passed, 78 tests.
  - `make release-check`: passed, including lock check, lint, format, mypy,
    compileall, coverage, `pip-audit`, build, and expanded wheel smoke.
  - `uv run pre-commit run --all-files`: passed.
  - `git diff --check`: passed.
- Results:
  - JSON packager coverage increased to 92%.
  - Public helper and directory conversion behavior now has direct tests.
- Fixes applied:
  - no runtime code change; test-only reliability improvement.
- Remaining issues:
  - P2 mutation score/test-depth debt remains open for `skill_quality`,
    `skill_registry`, and remaining non-equivalent `json_packager` survivors.

## Fresh Review After Loop 5

- Date: 2026-05-27
- Searches:
  - changed files for hardcoded paths, placeholders, suppressions, skipped-test
    markers, and secret-like strings.
- Result:
  - no unresolved P0/P1 findings;
  - matches were existing review-ledger search descriptions only.

## Loop 6: MCP Skills Resource Hardening and Experimental AI Skill Builder

- Date: 2026-05-27
- Review findings:
  - P1: `janusz://skills` could disclose skill names from a root `skills`
    symlink resolving outside the configured workspace.
  - P1: `janusz://skills` did not apply the shared sensitive path policy and
    could list skill directories below sensitive paths such as `.ssh` or names
    containing `token`.
  - P3: Janusz lacked an AI Skill Builder that kept model output constrained to
    a structured draft and Janusz-owned deterministic rendering.
- Commands run:
  - `uv run pytest tests/test_mcp_server.py::test_mcp_skills_resource_ignores_root_symlink_escape tests/test_mcp_server.py::test_mcp_skills_resource_ignores_nested_symlink_escape tests/test_mcp_server.py::test_mcp_skills_resource_hides_sensitive_skill_paths -q`:
    reproduced 2 failures before the MCP fix and passed after the fix.
  - `uv run pytest tests/test_ai_skill_builder.py -q`: passed, 8 tests.
  - `uv run pytest tests/test_mcp_server.py -q`: passed, 22 tests.
  - `uv run pytest tests/test_ai_skill_builder.py tests/test_mcp_server.py -q`:
    passed, 30 tests.
  - `uv run ruff check` on changed Python files: passed.
  - `uv run ruff format --check` on changed Python files: passed.
  - `uv run mypy src/janusz`: passed after type cleanup, 34 source files.
  - `uv sync --group dev --locked`: passed, resolved 202 packages and audited
    80 packages.
  - `make release-check`: passed; lock check, lint, format, mypy, compileall,
    89 tests, 72.64% coverage, Bandit, `pip-audit`, package build, wheel smoke,
    and version check all completed.
  - `make check`: passed; lint, format, mypy, and 89 tests completed.
  - `git diff --check`: passed.
  - `uv run pre-commit run --all-files`: passed.
- Results:
  - MCP skill resources now return only workspace-relative safe skill paths.
  - `janusz skill ai` exists as an experimental optional command.
  - AI output is strict JSON/Pydantic validated, secret-checked, rendered by
    Janusz deterministic code, and linted/scored before success.
- Fixes applied:
  - added `find_skill_catalog()` with no-follow workspace traversal, workspace
    containment, and sensitive path policy for MCP skills resources;
  - added `src/janusz/ai/skill_prompt.py` and
    `src/janusz/ai/skill_generator.py`;
  - wired `janusz skill ai` into the CLI;
  - added offline AI Skill Builder tests and MCP skills resource security tests.
- Remaining issues:
  - AI Skill Builder remains experimental and needs separate real-provider
    hardening before stability promotion.

## Fresh Review After Loop 6

- Date: 2026-05-27
- Searches:
  - hardcoded absolute paths and developer usernames;
  - sensitive markers and placeholder values;
  - broad suppressions and skipped-test markers;
  - optional dependency import leaks from core paths;
  - production, beta, and experimental documentation claims;
  - AI prompt source-data boundaries;
  - MCP resource listing and path discovery code.
- Result:
  - no unresolved P0/P1 findings;
  - matches were expected test fixtures, security policy constants, documented
    experimental-module limitations, `/tmp` wheel-smoke paths, or optional
    module imports that remain lazy/isolated from the stable core CLI.
