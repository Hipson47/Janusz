# Release Readiness Report

## Release decision

READY for a Janusz 1.0.0 core CLI release candidate.

The latest local release gate passed, and the latest fresh review found no
unresolved P0/P1 issues. Publishing remains forbidden for autonomous agents and
requires human approval.

## Stable surface

- Core CLI
- Document conversion
- JSON packaging
- Skill package generation
- Skill lint/score
- Repository ingest
- Registry and memory
- Plugin packaging
- Wheel installation and release gates

## Beta surface

- MCP stdio server with workspace root enforcement, sensitive path denial,
  symlink escape handling, size limits, and resource listing filtering.

## Experimental surface

- AI/schema generation
- RAG
- GUI
- Prompt/orchestration modules

## Validation gates

Latest known results:

- `uv lock --check`: passed
- `uv sync --group dev --locked`: passed
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run mypy src/janusz`: passed
- `uv run python -m compileall -q src scripts examples tests`: passed
- `uv run pytest tests -q`: passed, 64 tests
- coverage gate: passed, 71.49%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- `make wheel-smoke`: passed
- `make check`: passed
- `make release-check`: passed
- `uv run pre-commit run --all-files`: passed

## Security status

MCP tool and resource paths are root-sandboxed. Sensitive directories and files
are denied or hidden by default. Latest security scans passed locally.

## Packaging status

The wheel builds and installs into a clean virtual environment. Smoke testing
exercises `janusz --version`, document-to-JSON conversion, and skill package
generation.

## Known limitations

- Mutation score is below the long-term 80% target.
- Optional AI/RAG/GUI/prompt/orchestration modules remain experimental.
- `pip-audit` cannot audit the local unpublished `janusz` package record because
  it is not available on PyPI.

## Blocking issues

None.
