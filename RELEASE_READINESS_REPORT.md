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
- `uv run pytest tests -q`: passed, 78 tests
- `uv run pytest tests/test_mcp_server.py -q`: passed, 19 tests
- latest coverage gate: passed, 78 tests, 72.41%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- `make wheel-smoke`: passed, including manifest export and registry build/search
- `make check`: passed
- latest `make check` after JSON packager mutation coverage improvements:
  passed, 78 tests
- latest `make release-check` after JSON packager mutation coverage
  improvements: passed
- `uv run pre-commit run --all-files`: passed
- `uv run mutmut run --max-children 4`: completed, 3188 mutants processed,
  1233 killed, 1708 survived, 247 no-tests
- targeted JSON packager mutation run: completed, 229 mutants processed, 147
  killed, 82 survived

## Security status

MCP tool and resource paths are root-sandboxed. Sensitive directories and files
are denied or hidden by default. JSON package resource discovery is deterministic
and prunes ignored or sensitive directories before traversal. Package discovery
also skips dangling JSON symlinks and other resolved paths that are not files.
Latest security scans passed locally.

## Packaging status

The wheel builds and installs into a clean virtual environment. Smoke testing
exercises `janusz --help`, `janusz --version`, document-to-JSON conversion, skill
package generation, tool manifest export, registry build, and registry search.

## Known limitations

- Mutation score is below the long-term 80% target; latest full run killed 1233
  of 2941 tested mutants, with 1708 survivors and 247 no-tests.
- Optional AI/RAG/GUI/prompt/orchestration modules remain experimental.
- `pip-audit` cannot audit the local unpublished `janusz` package record because
  it is not available on PyPI.

## Blocking issues

None.
