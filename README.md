# Janusz

Janusz converts documents and structured data into agent-ready knowledge packages.
The core workflow is:

```text
Documents -> YAML -> JSON -> Codex skill package
```

It is designed for local AI-assisted work: ingest a PDF, Markdown file, text file,
DOCX, HTML, YAML, or JSON document; normalize it into structured data; then turn the
result into a reusable skill folder for an agent.

## Features

- Convert PDF, Markdown, plain text, DOCX, HTML, YAML, and JSON inputs.
- Produce structured YAML with metadata, sections, raw text, keywords, examples, and best practices.
- Produce plain JSON packages with no external format CLI dependency.
- Generate Codex-compatible skill packages with `SKILL.md` and `references/source.json`.
- Lint and score skills for routing metadata, structure, secret leakage, and agent usability.
- Ingest repositories into operations skills with architecture, commands, tests, deployment, and pitfalls.
- Keep a lightweight Janusz memory catalog of useful skill packs and routing triggers.
- Export a machine-readable tool manifest for higher-level orchestrators.
- Serve core Janusz tools, resources, and prompts over a lightweight MCP stdio server.
- Build a local JSONL/SQLite skill registry and package skills into plugin bundles.
- Optional OpenRouter-powered analysis for richer summaries and extraction.
- Schema management, local GUI, RAG experiments, and prompt tooling remain available as optional workflows.

## Installation

Janusz 1.0.0 supports Python 3.10 or newer.

```bash
uv sync
```

For development tools:

```bash
uv sync --group dev --locked
```

For AI-powered commands:

```bash
uv sync --extra ai
export JANUSZ_OPENROUTER_API_KEY=...
```

## Basic Usage

```bash
# Convert documents in new/ to YAML
janusz convert

# Convert one document to YAML
janusz convert --file document.md

# Create JSON packages from documents or YAML files
janusz json
janusz json --file document.yaml
janusz json --file document.md --output document.json

# Validate an existing JSON package
janusz json --validate-only --file document.json

# Inspect a YAML or JSON package
janusz test document.json

# Create a skill package
janusz skill --file document.json --output-dir skills
janusz skill --file document.md --output-dir skills --overwrite

# Lint and score skill packages
janusz skill lint skills/api-documentation
janusz skill score skills/api-documentation --json

# Create a repository operations skill
janusz ingest repo /path/to/repo --output-dir skills

# Seed Janusz memory and export orchestrator context
janusz memory seed
janusz memory list
janusz memory context

# Register Janusz as a local orchestrator tool
janusz tool manifest
janusz tool manifest --output artifacts/janusz_tool_manifest.json

# Build/search a skill registry and bundle plugin packages
janusz registry build --skills-dir skills
janusz registry search "repo test" --min-score 75
janusz package plugin --name repo-tools --skill skills/repo-helper --output-dir dist/repo-tools

# Run the MCP server for MCP-capable orchestrators
janusz mcp serve
```

## Skill Output

`janusz skill` creates a folder like:

```text
skills/
└── api-documentation/
    ├── SKILL.md
    └── references/
        └── source.json
```

`SKILL.md` contains concise trigger metadata and operational guidance. The full
extracted package lives in `references/source.json`, so the agent can load the
detailed source only when it is useful.

## Janusz Memory

`memory/janusz_memory.json` stores curated skill-pack metadata, triggers, source
paths, and Janusz tool contracts. It is intentionally compact: agents should read
the full referenced `SKILL.md` only after the memory entry matches the task.

The current catalog includes Hipson workflow, repo intake, executor, review,
memory, tooling, taxonomy, OpenAI skill-authoring/install docs, Supabase, and
visual asset helper skills.

## Skill Quality

`janusz skill lint` checks `SKILL.md` frontmatter, `name`, `description`, folder
structure, trigger metadata, likely secrets, reference layout, and actionability.
`janusz skill score` returns a compact 0-100 agent-usability score for registry
ranking and packaging gates.

Generated skills include `metadata.triggers` so they can be searched and routed
without loading full reference material first.

## Repository Ingest

`janusz ingest repo` creates a repository operations skill. The generated package
contains:

- `SKILL.md` with workflow guidance for agents.
- `references/repo_inventory.json` for tools and orchestrators.
- `references/repo_inventory.md` for human-readable context.

The inventory covers architecture signals, detected commands, test commands,
deployment/CI files, and common pitfalls such as uncommitted changes or missing
verification signals.

## Registry, MCP, And Plugins

`janusz registry build` writes `registry/skills.jsonl` and `registry/skills.sqlite`
from local skill folders. Search results can be filtered by query, category, and
minimum quality score.

`janusz mcp serve` exposes:

- tools: JSON package generation, skill generation, package inspection, manifest export
- resources: Janusz memory, skill catalog, JSON packages
- prompts: create skill, review skill, convert docs to agent skill

MCP tool paths and package resource listings are confined to the configured
workspace root and hide sensitive files such as `.env`, `.aws`, `.ssh`, `.git`,
token, credential, and private-key JSON paths.

`janusz package plugin` bundles selected skills into a plugin folder with
`.codex-plugin/plugin.json`, copied skill directories, and an optional Janusz tool
manifest.

## Orchestrator Tool Mode

Use `janusz tool manifest` to expose Janusz as a local CLI tool for a larger
orchestrator. See [docs/ORCHESTRATOR_TOOL.md](docs/ORCHESTRATOR_TOOL.md) for the
tool contract and recommended call flow.

## Production 1.0 Surface

Janusz 1.0.0 separates the hardened integration surface from incubating modules:

| Stability | Features |
| --- | --- |
| Stable | Core CLI, document conversion, JSON packaging, skill packaging, skill lint/score, repository ingest, registry JSONL/SQLite, plugin packaging, memory, orchestrator manifest |
| Beta | MCP stdio server with workspace sandboxing and safe path handling |
| Experimental | AI analysis, schema generation, GUI, RAG, prompt tools, AI orchestration |

Experimental modules are import-safe and should fail with actionable messages
when optional dependencies or provider configuration are missing. They are not
part of the hardened 1.0 compatibility contract.

`janusz schema generate-ai` is experimental. It requires
`JANUSZ_OPENROUTER_API_KEY` and the AI extra, for example `janusz[ai]`, and unit
tests use fake analyzers instead of network calls.

The release gate is:

```bash
make check
make release-check
```

See [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) for the 1.0
integration checklist.

## CLI Commands

```bash
janusz convert      # document -> YAML
janusz json         # document/YAML/JSON -> normalized JSON package
janusz skill        # document/YAML/JSON -> Codex skill package
janusz ingest       # repo -> repository operations skill
janusz registry     # build/search local JSONL and SQLite skill registry
janusz package      # bundle skills into plugin packages
janusz mcp          # MCP stdio server
janusz memory       # seed/list/export Janusz skill-pack memory
janusz tool         # export Janusz orchestrator tool manifest
janusz schema       # manage reusable extraction schemas
janusz orchestrate  # recommend schemas and processing plans
janusz rag          # local retrieval experiments
janusz prompt       # prompt optimization and library tools
janusz gui          # launch desktop GUI
janusz test         # inspect YAML/JSON package structure
```

## Make Commands

```bash
make install
make convert
make json
make skill
make test
make lint
make check
make release-check
make wheel-smoke
make mutate-core
```

Use `FILE=...` for file-specific runs:

```bash
make json FILE=examples/inputs/sample_architecture.yaml
make skill FILE=examples/inputs/sample_architecture.yaml
```

## Project Structure

```text
src/janusz/
├── cli.py              # command-line interface
├── converter.py        # document -> YAML structure
├── json_packager.py    # YAML/document/JSON -> JSON package
├── skill_packager.py   # JSON/YAML/document -> Codex skill folder
├── skill_quality.py    # skill linting and agent-usability scoring
├── skill_registry.py   # JSONL/SQLite skill index
├── repo_ingester.py    # repository -> operations skill
├── plugin_packager.py  # skill bundle -> plugin folder
├── mcp_server.py       # MCP stdio server
├── memory.py           # durable skill-pack memory for agents
├── orchestrator_tool.py # machine-readable local tool manifest
├── schemas/            # modular schema management
├── rag/                # retrieval experiments
├── prompts/            # prompt tools
└── gui/                # desktop GUI
```

## Development

```bash
uv sync --group dev --locked
uv run python -m pytest tests --capture=no
uv run ruff check .
uv run ruff format --check .
uv run mypy src/janusz
make check
```

`make check` runs linting, strict type checking for the supported 1.0 surface,
and the automated test suite.

`make release-check` is the production gate. It verifies the lockfile, lint,
formatting, type checking, syntax compilation, 70% coverage, Bandit, `pip-audit`,
package build, wheel install smoke tests, and version metadata.

`make mutate-core` runs mutation testing for production-critical core modules.
It is documented as a manual release hardening gate because it is slower than the
normal pull-request path.

## Environment Variables

- `JANUSZ_OPENROUTER_API_KEY`: optional key for AI analysis, schema generation,
  prompt optimization, and answer generation.
- `JANUSZ_WORKSPACE_ROOT`: optional MCP workspace root. MCP file operations are
  resolved inside this root and deny traversal, symlink escapes, sensitive files,
  and oversized files by default.

## Notes

Janusz stores generated JSON and skill packages as normal local files. Treat source
documents as untrusted data, review generated skills before installing them globally,
and keep private knowledge bases out of version control.
