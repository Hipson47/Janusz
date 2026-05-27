# Progress

## Goal

Prepare Janusz as a local document-to-JSON-to-skill tool for agent and
orchestrator workflows.

## Completed

- Removed the legacy alternate serialization workflow from the codebase and docs.
- Added JSON package generation as the stable interchange layer.
- Added Codex skill package generation from documents, YAML, or JSON packages.
- Added durable Janusz skill-pack memory in `memory/janusz_memory.json`.
- Added `janusz memory seed`, `janusz memory list`, and `janusz memory context`.
- Added `janusz tool manifest` for machine-readable orchestrator registration.
- Added `janusz skill lint` and `janusz skill score` for skill quality gates.
- Added `janusz ingest repo` for repository operations skill generation.
- Added `janusz registry build/search` with JSONL and SQLite outputs.
- Added `janusz package plugin` for distributing bundled skills and manifests.
- Added `janusz mcp serve` with tools, resources, and prompts over stdio JSON-RPC.
- Added tests for JSON packaging, skill packaging, memory, tool manifests, and CLI smoke coverage.
- Added the 1.0 production quality gate: lint, strict mypy for the supported
  integration surface, and tests through `make check`.
- Hardened release metadata, dependency locking, and low-risk security findings
  for a clean 1.0 build and audit.
- Added the production release gate through `make release-check`, including
  coverage, Bandit, `pip-audit`, package build, and clean wheel smoke testing.

## Verification

- `uv sync --group dev --locked`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src/janusz`
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`
- `make check`
- `make release-check`
- `uv build`
- `uv run bandit -q -r src/janusz`
- `uv run pip-audit`
- `uv run janusz memory seed --path /tmp/janusz_memory_smoke.json --overwrite`
- `uv run janusz memory list --path /tmp/janusz_memory_smoke.json`
- `uv run janusz memory context --path /tmp/janusz_memory_smoke.json`
- `uv run janusz tool manifest --memory-path /tmp/janusz_memory_smoke.json`
- `uv run janusz tool manifest --memory-path /tmp/janusz_memory_smoke.json --output /tmp/janusz_tool_manifest_smoke.json`
- `uv run janusz skill lint <generated-skill>`
- `uv run janusz skill score <generated-skill>`
- `uv run janusz ingest repo <repo> --output-dir <skills>`
- `uv run janusz registry build --skills-dir <skills>`
- `uv run janusz registry search <query>`
- `uv run janusz package plugin --name <name> --skill <skill> --output-dir <plugin>`
- MCP JSON-RPC initialize/tools/resources/prompts unit tests
- `git diff --check`

A repository-wide search for the removed legacy format name returned no matches.

## Remaining Risk

- Optional GUI, RAG, schema, prompt, and experimental orchestration workflows are
  available but remain outside the hardened 1.0 integration contract.
