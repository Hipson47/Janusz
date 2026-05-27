# Changelog

## 1.0.0 - Production hardening candidate

- Standardized Python support on 3.10+ and aligned local, CI, and release installs
  on `uv sync --group dev --locked`.
- Switched repository formatting policy to Ruff format and expanded lint/format
  checks to the full repository.
- Added `make release-check` with lockfile, lint, format, mypy, compile, coverage,
  Bandit, `pip-audit`, build, wheel smoke, and version checks.
- Hardened MCP filesystem handling with workspace roots, path normalization,
  traversal and symlink denial, sensitive-file denial, size limits, and sanitized
  errors.
- Hardened MCP JSON package discovery so `janusz://packages` does not disclose
  sensitive JSON paths or symlink escapes outside the workspace root.
- Hardened MCP skill catalog discovery so `janusz://skills` does not disclose
  skill metadata from symlink escapes or sensitive skill paths.
- Made MCP JSON package discovery deterministic and pruned ignored or sensitive
  directories before traversal.
- Strengthened MCP package discovery tests for limits, resource defaults,
  ignored directories, non-JSON files, and dangling JSON symlinks.
- Expanded JSON packager tests for structured loading, deterministic writes,
  directory conversion, validation helpers, and package inspection.
- Added experimental `janusz skill ai`, which validates AI skill drafts, rejects
  secret-like draft output, renders packages deterministically, and runs
  lint/score gates.
- Fixed `janusz schema generate-ai` analyzer wiring and added offline tests for
  successful fake generation and missing provider configuration.
- Expanded clean-wheel smoke coverage to exercise tool manifest export and
  registry build/search from the installed artifact.
- Removed hardcoded local developer paths from the orchestrator manifest and
  memory catalog.
- Repaired the RAG example and documented RAG, GUI, AI, prompt, schema, and AI
  orchestration modules as experimental unless separately hardened.
- Added direct CLI, MCP, NLP fallback, path-sandbox, and portability tests.
- Added `SECURITY.md`, release hardening notes, production readiness guidance, and
  mutation testing configuration for core modules.
