# Production Readiness

Janusz 1.0.0 is prepared as a local tool for agent and orchestrator workflows.
The supported production surface is focused on turning documents and repositories
into reusable agent skill assets, then exposing those assets through CLI, MCP,
registry, memory, and plugin packaging.

The supported runtime is Python 3.10 or newer.

## Feature Stability

| Stability | Commands and modules | Contract |
| --- | --- | --- |
| Stable | `convert`, `json`, `skill`, `skill lint`, `skill score`, `ingest repo`, `registry`, `package plugin`, `memory`, `tool manifest` | Production 1.0 integration surface |
| Beta | `mcp serve` | Workspace-sandboxed stdio MCP server; safe for local orchestrator integration after host-level review |
| Experimental | `rag`, `gui`, `schema`, `prompt`, `orchestrate`, `ai` provider helpers | Import-safe incubating modules; not part of the 1.0 compatibility guarantee |

## Integration Checklist

Run these gates before wiring Janusz into an orchestrator:

```bash
uv sync --group dev --locked
make check
make release-check
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

RAG currently requires optional dependencies and a real embedding/provider
configuration. Dummy embeddings and synthetic answer generation are not presented
as production behavior.

## MCP Security Model

`janusz mcp serve` resolves all tool input and output paths under a configured
workspace root. The root defaults to the current working directory and can be set
with `--root` or `JANUSZ_WORKSPACE_ROOT`.

The MCP layer:

- normalizes paths with `Path.resolve()`;
- rejects path traversal, absolute paths outside the root, and symlink escapes;
- denies sensitive paths such as `.env`, `.ssh`, `.git`, private keys, token files,
  and common cloud credential files;
- enforces a default 10 MiB input size limit;
- returns sanitized user-facing errors that do not expose host-specific absolute paths.

## Release Gate

The production release gate is:

```bash
uv sync --group dev --locked
make release-check
```

`make check` runs the normal developer gate: Ruff lint, Ruff format check, strict
typing for the supported 1.0 surface, and the unit test suite.

`make release-check` runs the full production gate: lockfile check, lint, format,
mypy, syntax compilation, coverage with a 70% threshold, Bandit, blocking
`pip-audit` with retry behavior, package build, wheel install smoke test, and
version metadata validation.

Release tags must be `vX.Y.Z` and match `project.version` in `pyproject.toml`.
The GitHub release workflow builds and tests the artifact before publishing it
through a `pypi` environment. Maintainers should configure required reviewers for
that environment in GitHub repository settings.

## Mutation Testing

`make mutate-core` runs `mutmut` against production-critical core modules:
converter, JSON packaging, skill packaging, skill quality, registry, memory,
plugin packaging, repository ingest, MCP, and orchestrator tool manifest.

The target mutation score for a production release is 80% on those core modules.
Mutation testing is slower than the normal PR gate, so it is a documented manual
release hardening gate unless CI runtime budget allows it to run on scheduled or
release-candidate workflows.
