# Agent State

## Current status

Janusz is on branch `codex/autonomous-maintainer-loop`. The stable core CLI is a
1.0.0 release candidate: local release gates pass, clean wheel smoke passes, and
the latest fresh review found no unresolved P0/P1 issues.

Stable surface:

- core CLI;
- document conversion;
- JSON packaging;
- skill generation;
- skill lint/score;
- repository ingest;
- registry and memory;
- plugin packaging;
- orchestrator manifest.

Beta surface:

- MCP stdio server, with workspace-root path handling and resource-listing
  sensitive path filtering.

Experimental surface:

- AI/schema generation;
- RAG;
- GUI;
- prompt/orchestration modules.

## Last completed loop

Autonomous loop 3 completed on 2026-05-27:

- selected `BL-P2-003` as the next safe packaging-confidence task;
- expanded `make wheel-smoke` to exercise `janusz tool manifest`;
- expanded `make wheel-smoke` to build and search a JSONL skill registry from
  the installed wheel;
- verified `make wheel-smoke`.

Autonomous loop 2 completed on 2026-05-27:

- selected `BL-P2-001` as the highest-value safe task after P0/P1 were clean;
- added a test proving package discovery output must be deterministic;
- changed MCP JSON package discovery to use sorted `os.walk` traversal with
  pruning for ignored and sensitive directories before descent;
- verified `tests/test_mcp_server.py`, `mypy`, and `make check`.

Autonomous loop 1 completed on 2026-05-27:

Current RC hardening loop completed on 2026-05-27:

- fixed MCP `janusz://packages` sensitive JSON path disclosure;
- fixed `janusz schema generate-ai` analyzer wiring and actionable errors;
- added offline tests for both fixes;
- updated README, SECURITY, CHANGELOG, production readiness docs, and review
  ledgers;
- ran final `make release-check` successfully.

## Commands last run

- `uv lock --check`: passed
- `uv sync --group dev --locked`: passed
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run mypy src/janusz`: passed
- `uv run python -m compileall -q src scripts examples tests`: passed
- `uv run pytest tests -q`: passed, 64 tests
- `uv run pytest tests/test_mcp_server.py -q`: passed, 14 tests
- `make check`: passed, 65 tests after deterministic MCP discovery test
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`: passed, 71.49%
- `uv run bandit -q -r src/janusz`: passed
- `uv run pip-audit`: passed; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- `make wheel-smoke`: passed, including manifest export and registry build/search
- `make check`: passed
- `uv run pre-commit run --all-files`: passed
- `make release-check`: passed
- fresh repository searches: no unresolved P0/P1 findings

## Known blockers

None.

## Next recommended task

Pick `BL-P2-002`: raise mutation score for core modules by adding meaningful
tests around high-value survivors. Start with `json_packager`, `skill_quality`,
or MCP paths where surviving mutants map to stable behavior.

## Assumptions

- The project continues to use `uv sync --group dev --locked` as the contributor
  and CI dependency path.
- Optional AI/RAG/GUI/prompt/orchestration modules stay outside the stable 1.0
  compatibility contract until separately hardened.
- Publishing, pushing, and deployment require explicit human approval.

## How to resume

1. Confirm repo root with `pwd` and inspect `git status --short`.
2. Read `AGENT_STATE.md`, `BACKLOG.md`, `REVIEW_LEDGER.md`, `DECISIONS.md`, and
   `RELEASE_READINESS_REPORT.md`.
3. If the working tree contains a verified coherent diff, commit it locally.
4. Select the highest-priority open backlog item and run the test-first
   maintain-improve-verify loop.
