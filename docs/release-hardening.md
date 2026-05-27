# Release Hardening Notes

## Baseline Reproduction

Captured on 2026-05-27 from the WSL workspace checkout.

- `uv lock --check`: passed.
- `uv sync --group dev --locked`: completed, but installed only the small dependency
  group and removed release tools such as `ruff`, `mypy`, `pytest`, and `bandit`.
- `make check`: failed because `ruff` was not installed after the locked dev-group sync.
- `uv run ruff check .`: failed because `ruff` was not installed.
- `uv run ruff format --check .`: failed because `ruff` was not installed.
- `uv run mypy src/janusz`: failed because `mypy` was not installed.
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`:
  failed because `pytest` was not installed.
- `uv run bandit -q -r src/janusz`: failed because `bandit` was not installed.
- `uv run python -m compileall -q src scripts examples tests`: failed on
  `examples/rag_demo.py` with an unterminated string literal.
- `uv run pip-audit`: passed with no known vulnerabilities in the current environment.
- `uv build`: passed.

## Fix Order

1. Make `uv sync --group dev --locked` the single developer and CI install path.
2. Use Ruff as the single formatter and apply checks to the whole repository.
3. Repair executable examples and remove root-level scratch tests.
4. Add a production `make release-check` that matches CI and release workflows.
5. Harden MCP filesystem access and remove local developer path leaks.
6. Document stable, beta, and experimental surfaces honestly.
7. Add release security, wheel smoke, coverage, and mutation-testing policy gates.

## Completed Hardening

- Replaced the inconsistent dev install path with `uv sync --group dev --locked`
  across docs, Makefile, CI, and release workflows.
- Updated Python/tooling targets to Python 3.10+ and CI to 3.10, 3.11, 3.12,
  and 3.13.
- Standardized on Ruff format and removed Black from the active gate.
- Repaired the RAG example and removed obsolete root scratch tests.
- Added direct tests for CLI, MCP sandboxing, MCP resources/prompts, portability,
  NLP fallback behavior, and production package paths.
- Hardened MCP path handling with workspace roots, path normalization, sensitive
  file denial, size limits, and sanitized errors.
- Removed developer-specific absolute path leakage from memory and orchestrator
  manifests.
- Added release workflow gates for tag/version consistency, release-check, wheel
  smoke testing, Bandit, blocking dependency audit, and trusted PyPI publishing
  through the `pypi` environment.
