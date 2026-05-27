# Architecture Overview

Janusz is a local document normalization and skill packaging tool for AI agent
workflows.

```text
Documents -> YAML -> JSON -> Skill package
```

## Core Components

### Document Conversion

`src/janusz/converter.py` extracts text from PDF, Markdown, text, DOCX, and HTML
sources. It parses headings, raw text, keywords, best practices, examples, and
optional AI analysis into a `DocumentStructure` model, then writes YAML.

### JSON Packaging

`src/janusz/json_packager.py` normalizes supported source documents, YAML files,
and existing JSON files into a plain JSON package. This is the stable interchange
format for downstream agent workflows.

### Skill Packaging

`src/janusz/skill_packager.py` creates a Codex-compatible skill folder:

```text
skill-name/
├── SKILL.md
└── references/
    └── source.json
```

`SKILL.md` stays concise and points to `references/source.json` for detailed
source material.

### Skill Quality

`src/janusz/skill_quality.py` lints and scores skills. It checks required
frontmatter, `name`, `description`, trigger metadata, structure, length, likely
secret leakage, reference layout, and actionability. The score is a 0-100
agent-usability signal used by CLI output, registry indexing, and plugin bundles.

### Repository Ingest

`src/janusz/repo_ingester.py` creates a repository operations skill from a local
project. It scans architecture signals, development commands, tests, deployment
files, CI, language mix, and pitfalls, then writes `SKILL.md`,
`references/repo_inventory.json`, and `references/repo_inventory.md`.

### Registry

`src/janusz/skill_registry.py` builds a local skill index in JSONL and SQLite. It
uses the quality scorer for every skill and supports search by query, trigger,
category, and minimum score.

### Plugin Packaging

`src/janusz/plugin_packager.py` bundles selected skills into a distributable
folder containing `.codex-plugin/plugin.json`, copied skill packages, and an
optional Janusz tool manifest.

### MCP Server

`src/janusz/mcp_server.py` is a lightweight stdio JSON-RPC MCP server. It exposes
Janusz tools, resources, and prompts without adding an external runtime
dependency.

### Janusz Memory

`src/janusz/memory.py` owns durable memory for skill-pack routing. It writes
`memory/janusz_memory.json`, which stores compact metadata about useful local and
system skills, source paths, triggers, tool contracts, and operating rules.

The memory file is designed for progressive disclosure: agents read names,
descriptions, triggers, and paths first, then load the full referenced `SKILL.md`
only when the task matches.

### Orchestrator Tool Manifest

`src/janusz/orchestrator_tool.py` exports Janusz as a local CLI tool contract. The
manifest describes commands, accepted input formats, output formats, memory
location, routing guidance, and safety rules for a higher-level orchestrator.

### CLI

`src/janusz/cli.py` exposes:

- `convert`: document -> YAML
- `json`: document/YAML/JSON -> JSON package
- `skill`: document/YAML/JSON -> skill folder
- `skill lint`: validate metadata, structure, triggers, secrets, and quality
- `skill score`: return agent-usability score
- `ingest repo`: repository -> operations skill package
- `registry`: build/search JSONL and SQLite skill indexes
- `package plugin`: bundle selected skills for distribution
- `mcp`: run the Janusz MCP stdio server
- `memory`: seed/list/export Janusz skill-pack memory
- `tool`: export Janusz orchestrator tool manifest
- `schema`: modular schema management
- `orchestrate`: schema and processing recommendations
- `rag`: retrieval experiments
- `prompt`: prompt optimization and prompt library tools
- `gui`: desktop interface
- `test`: inspect YAML/JSON package structure

Optional AI-heavy commands import their dependencies lazily so the base CLI can
start with only core dependencies installed.

## Data Flow

1. Detect input format from extension.
2. Extract text or load structured YAML/JSON.
3. Build or validate a normalized package object.
4. Write YAML or JSON output.
5. Optionally create a skill package with concise instructions and a JSON reference.
6. Optionally lint/score skills and index them in the registry.
7. Optionally package skills as a plugin or expose Janusz over MCP.
8. Optionally expose memory context or a tool manifest to an orchestrator.

## Quality Gates

- `uv sync --group dev --locked`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src/janusz`
- `uv run pytest tests --cov=janusz --cov-report=term-missing --cov-fail-under=70`
- `make check`
- `make release-check`

The 1.0 production type gate covers the core CLI, conversion, JSON packaging,
skill packaging, quality scoring, repository ingest, registry, plugin packaging,
MCP, memory, and orchestrator manifest modules. Optional GUI, RAG, schema,
prompt, and experimental orchestration modules remain importable but are not part
of the strict 1.0 type contract.

## Safety Notes

- Generated skills should be reviewed before installation.
- Source documents are treated as data, not trusted instructions.
- `make clean` only removes caches and temporary files; it does not delete tracked
  knowledge packages.
