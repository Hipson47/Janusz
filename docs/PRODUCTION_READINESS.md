# Production Readiness

Janusz 1.0.0 is prepared as a local tool for agent and orchestrator workflows.
The supported production surface is focused on turning documents and repositories
into reusable agent skill assets, then exposing those assets through CLI, MCP,
registry, memory, and plugin packaging.

The supported runtime is Python 3.10 or newer.

## Supported 1.0 Surface

- `janusz convert`: document to YAML structure.
- `janusz json`: document, YAML, or JSON to normalized JSON package.
- `janusz skill`: package source material as Codex-compatible skills.
- `janusz skill lint`: validate skill metadata, triggers, structure, secrets, and quality.
- `janusz skill score`: score whether a skill is agent-usable.
- `janusz ingest repo`: create repository operations skill packs.
- `janusz registry build/search`: maintain local JSONL and SQLite skill indexes.
- `janusz package plugin`: bundle skills and manifests into distributable plugin folders.
- `janusz mcp serve`: expose tools, resources, and prompts over stdio JSON-RPC.
- `janusz memory`: seed and export Janusz skill-pack memory.
- `janusz tool manifest`: expose Janusz as a machine-readable local tool.

## Integration Checklist

Run these gates before wiring Janusz into an orchestrator:

```bash
uv sync --extra dev
make check
uv build
uv run bandit -q -r src/janusz
uv run pip-audit
uv run janusz --help
uv run janusz tool manifest
```

For MCP clients, start:

```bash
uv run janusz mcp serve
```

For local skill discovery, seed memory and build the registry:

```bash
uv run janusz memory seed
uv run janusz registry build --skills-dir skills
```

## Compatibility Contract

The stable integration contract for 1.0.0 is the CLI command set, generated JSON
package shape, generated skill folder shape, registry entries, MCP method names,
and orchestrator tool manifest.

Optional GUI, RAG, schema, prompt, and experimental orchestration workflows remain
available for local use, but they are not part of the hardened 1.0 integration
contract. Treat them as incubating modules until they receive their own release
gate and compatibility notes.

## Release Gate

The production release gate is:

```bash
make check
uv build
git diff --check
uv run bandit -q -r src/janusz
uv run pip-audit
```

`make check` runs linting, strict type checking for the supported 1.0 surface,
and automated tests.
