# Review/Fix Ledger

Date: 2026-05-27

## Resolved P1 Issues

| ID | Severity | Finding | Evidence | Fix | Verification |
| --- | --- | --- | --- | --- | --- |
| RF-001 | P1 | Dev dependencies were declared twice: as a package extra and as a uv dependency group. This made the contributor/release model ambiguous. | `pyproject.toml` exposed `[project.optional-dependencies].dev` while docs, CI, and Makefile used `uv sync --group dev --locked`. | Removed the package `dev` extra and regenerated `uv.lock`, leaving dev tools in `[dependency-groups].dev`. | `uv lock --check`, `uv sync --group dev --locked`, and `make release-check` passed. |
| RF-002 | P1 | Optional AI code imported `httpx` at module import time, so a clean core wheel could fail if optional AI dependencies were absent. | `src/janusz/ai/ai_content_analyzer.py` had a top-level `import httpx`. | Moved `httpx` behind `load_httpx()` and raise an actionable `RuntimeError` only when AI client construction needs it. | `tests/test_ai_integration.py`, clean wheel install smoke, and direct wheel import smoke passed. |
| RF-003 | P1 | Pre-commit `mypy` hook did not match the local release gate and failed in its isolated environment. | `uv run pre-commit run --all-files` first failed with duplicate module handling, then missing runtime dependencies in the hook env. | Replaced the mirrored hook with a local `uv run mypy src/janusz` hook and `pass_filenames: false`, matching the project gate. | `uv run pre-commit run --all-files` passed. |
| RF-004 | P1 | Hidden ignore files still referenced the removed legacy format. | Hidden/no-ignore search found stale references in `.cursorignore` and `.gitignore`. | Removed the remaining legacy-format entries. | Follow-up hidden/no-ignore search returned no stale format matches. |
| RF-010 | P1 | `janusz://packages` disclosed sensitive JSON paths. | Reproduction showed `.aws/credentials.json`, `.env.json`, and token/private-key JSON paths in the resource output. | Shared the MCP sensitive-path policy with package discovery, added root containment checks, skipped symlink escapes, and returned only safe relative paths. | `tests/test_mcp_server.py::test_mcp_package_discovery_hides_sensitive_json_paths` and `tests/test_mcp_server.py::test_mcp_package_discovery_skips_symlink_escape` passed. |
| RF-011 | P1 | `janusz schema generate-ai` was exposed but constructed `SchemaManager` without an AI analyzer and returned misleading configuration guidance. | Reproduction with `JANUSZ_OPENROUTER_API_KEY=test-key` failed with `AI analyzer not available for schema generation`. | Constructed `AIContentAnalyzer` lazily only for `generate-ai`, injected it into `SchemaManager`, and printed actionable missing-provider/configuration errors. | Offline fake-analyzer success and missing-key CLI tests passed. |

## Resolved P2 Issues

| ID | Severity | Finding | Fix | Verification |
| --- | --- | --- | --- | --- |
| RF-005 | P2 | `Makefile` wheel-smoke had a stray tab indentation line that made the recipe harder to audit. | Normalized the recipe line. | `make release-check` passed and executed wheel smoke. |
| RF-006 | P2 | Architecture/progress docs listed older partial quality commands instead of the production gate. | Updated docs to reference `uv sync --group dev --locked`, whole-repo Ruff, coverage, and `make release-check`. | Documentation review and `pre-commit` passed. |
| RF-007 | P2 | Mutmut configuration was stale: the configured `runner` key was not honored by current mutmut and the sandbox missed local package modules. | Replaced it with `pytest_add_cli_args_test_selection` and `also_copy = ["src/janusz"]`. | `uv run mutmut run` completed. Result: 3138 mutants processed, 1178 killed, 1713 survived, 247 no-tests. |
| RF-008 | P2 | Mutation-test artifacts could appear as untracked files. | Added `.mutmut-cache/` and `mutants/` to `.gitignore`. | `git status --short` no longer showed mutation artifacts after cleanup. |
| RF-009 | P2 | Several files were missing final newlines according to pre-commit. | Accepted `end-of-file-fixer` changes. | `uv run pre-commit run --all-files` passed. |

## Remaining P2 Items

- Mutation score is below the long-term 80% target. This is test-depth debt, not a current P0/P1 release blocker because release-check, coverage, packaging, security, and wheel smoke gates pass.

## Fresh Review Result

Fresh review searches found no unresolved P0/P1 issues:

- No hardcoded local developer paths beyond tests that assert those paths are not leaked.
- No remaining legacy-format references with hidden/no-ignore search.
- No direct top-level imports of optional AI/RAG/GUI/provider dependencies from core paths.
- MCP package discovery hides sensitive JSON paths and symlink escapes.
- `schema generate-ai` is wired or fails actionably without network-dependent unit tests.
- CI and release workflows use `uv sync --group dev --locked` and release workflow runs `make release-check` before publishing.
