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
