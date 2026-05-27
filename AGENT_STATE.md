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

Autonomous loop 6 completed on 2026-05-27:

- fixed P1 `janusz://skills` resource sandboxing so skill listings cannot
  disclose root symlink escapes, nested symlink escapes, or sensitive skill
  paths, and so MCP skill catalog discovery does not follow directory symlinks;
- added experimental `janusz skill ai` as a draft-only AI Skill Builder;
- added strict `AISkillDraft` validation, injection-resistant prompt assembly,
  lazy OpenRouter provider wiring, secret-like draft rejection, deterministic
  rendering, and skill lint/score gates;
- added offline tests for MCP skill resource security and AI Skill Builder
  success/failure paths;
- ran the full release gate, developer gate, pre-commit hooks, diff hygiene, and
  fresh repository searches with no unresolved P0/P1 findings.

Autonomous loop 5 completed on 2026-05-27:

- continued `BL-P2-002` with JSON packager mutation/test-depth work;
- added JSON packager tests for deterministic writes, object-root validation,
  suffix dispatch, validation helpers, directory conversion, and inspection
  summaries/errors;
- ran targeted JSON packager mutation testing: 229 mutants processed, 147
  killed, 82 survived;
- verified targeted tests, coverage, mypy, `make check`, pre-commit, and diff
  hygiene, fresh review search, plus the full `make release-check`.

Autonomous loop 4 completed on 2026-05-27:

- selected `BL-P2-002` as the next reliability task;
- ran a full mutation baseline;
- added MCP package discovery tests for limits, bounded resource output,
  non-JSON traversal, ignored directory pruning, and dangling JSON symlinks;
- fixed package discovery so dangling JSON symlinks and other non-file resolved
  paths are not reported as packages;
- verified MCP tests, coverage, mypy, Bandit, `make check`, `make release-check`,
  fresh review searches, and diff hygiene.

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

- `uv run pytest tests/test_mcp_server.py::test_mcp_skills_resource_ignores_root_symlink_escape tests/test_mcp_server.py::test_mcp_skills_resource_ignores_nested_symlink_escape tests/test_mcp_server.py::test_mcp_skills_resource_hides_sensitive_skill_paths -q`:
  first reproduced 2 failures, then passed after the fix
- `uv run pytest tests/test_ai_skill_builder.py -q`: passed, 8 tests
- `uv run pytest tests/test_mcp_server.py -q`: passed, 22 tests
- `uv run pytest tests/test_ai_skill_builder.py tests/test_mcp_server.py -q`:
  passed, 30 tests
- `uv run ruff check src/janusz/ai/skill_generator.py src/janusz/ai/skill_prompt.py src/janusz/cli.py src/janusz/mcp_server.py tests/test_ai_skill_builder.py tests/test_mcp_server.py`:
  passed
- `uv run ruff format --check src/janusz/ai/skill_generator.py src/janusz/ai/skill_prompt.py src/janusz/cli.py src/janusz/mcp_server.py tests/test_ai_skill_builder.py tests/test_mcp_server.py`:
  passed
- `uv run mypy src/janusz`: passed after type cleanup, 34 source files
- `uv sync --group dev --locked`: passed, resolved 202 packages and audited 80
  packages
- `make release-check`: passed, including lock check, lint, format, mypy,
  compileall, 89 tests with 72.64% coverage, Bandit, `pip-audit`, build,
  wheel smoke, and version check
- `make check`: passed, lint, format, mypy, and 89 tests
- `git diff --check`: passed
- `uv run pre-commit run --all-files`: passed
- fresh repository searches for hardcoded paths, sensitive markers,
  placeholders, suppressions, optional dependency leaks, documentation
  overclaims, AI prompt boundaries, and MCP raw path discovery: no unresolved
  P0/P1 findings
- `uv run pytest tests/test_json_packager.py -q`: passed, 12 tests
- `uv run mutmut run --max-children 4 'janusz.json_packager.*'`: completed
  targeted JSON packager mutation testing, 229 mutants processed, 147 killed,
  82 survived
- `uv run ruff check tests/test_json_packager.py`: passed
- `uv run ruff format --check tests/test_json_packager.py`: passed
- `uv run mypy src/janusz`: passed
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`:
  passed, 78 tests, 72.41% coverage
- `uv run pytest tests -q`: passed, 78 tests
- `make check`: passed, 78 tests
- `make release-check`: passed after loop 5, including lock check, lint,
  format, mypy, compileall, coverage, `pip-audit`, build, and expanded
  `make wheel-smoke`
- `uv run pre-commit run --all-files`: passed
- `git diff --check`: passed
- `uv run mutmut run --max-children 4`: completed, 3188 mutants processed,
  1233 killed, 1708 survived, 247 no-tests
- targeted `mutmut` run for `find_json_packages`: killed several MCP discovery
  mutants; default-limit and equivalent negative-limit mutants still survived
- `uv run ruff check src/janusz/mcp_server.py tests/test_mcp_server.py`: passed
- `uv run ruff format src/janusz/mcp_server.py tests/test_mcp_server.py`:
  formatted `tests/test_mcp_server.py`
- `uv run ruff format --check src/janusz/mcp_server.py tests/test_mcp_server.py`:
  passed
- `uv run pytest tests/test_mcp_server.py -q`: passed, 19 tests
- `uv run mypy src/janusz`: passed
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`:
  passed, 70 tests, 71.65% coverage
- `uv run bandit -q -r src/janusz`: passed
- `git diff --check`: passed
- `make check`: passed, 70 tests
- loop 4 `make release-check`: passed, including lock check, lint, format,
  mypy, compileall, coverage, `pip-audit`, build, and expanded
  `make wheel-smoke`
- `uv lock --check`: passed
- `uv sync --group dev --locked`: passed
- `uv run ruff check .`: passed
- `uv run ruff format --check .`: passed
- `uv run python -m compileall -q src scripts examples tests`: passed
- `uv run pytest tests -q`: passed, 78 tests
- `uv run pip-audit`: passed; local `janusz` skipped because it is not on PyPI
- `uv build`: passed
- `make wheel-smoke`: passed, including manifest export and registry build/search
- `uv run pre-commit run --all-files`: passed
- fresh repository searches: no unresolved P0/P1 findings

## Known blockers

None.

## Next recommended task

Commit loop 6 if the working tree still contains the verified diff, then
continue `BL-P2-002` with `skill_quality` or `skill_registry`, then return to
remaining non-equivalent `json_packager` and MCP survivors.

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
