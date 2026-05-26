# Janusz Orchestrator Tool

Janusz can be registered as a local CLI tool for an orchestrator. Its stable job is
to turn source knowledge into durable agent material:

```text
Documents -> YAML -> JSON -> Codex skill package
```

## Tool Manifest

Export the machine-readable contract:

```bash
janusz tool manifest
janusz tool manifest --output artifacts/janusz_tool_manifest.json
```

The manifest describes accepted inputs, generated outputs, command contracts,
memory location, and safety rules. Orchestrators should read it before invoking
Janusz in an automated workflow.

## Memory Context

Janusz keeps a lightweight skill-pack memory in:

```text
memory/janusz_memory.json
```

Seed or refresh it:

```bash
janusz memory seed
janusz memory seed --overwrite
```

Export compact context for another agent:

```bash
janusz memory context
```

The memory stores skill-pack metadata, routing triggers, local source paths, and
tool contracts. It intentionally does not inline full skill instructions; agents
should load the referenced `SKILL.md` only after the metadata matches the task.

## Recommended Orchestrator Flow

1. Call `janusz tool manifest` during tool registration.
2. Call `janusz memory context` before task routing.
3. Use `janusz json --file <input> --output <output.json>` for machine-readable knowledge.
4. Use `janusz skill --file <input> --output-dir <skills_dir>` for reusable agent skills.
5. Use `janusz skill lint <skill_dir>` and `janusz skill score <skill_dir>` before routing.
6. Use `janusz registry build --skills-dir <skills_dir>` to create searchable skill metadata.
7. Use `janusz test <package>` after generation when package validation matters.

## MCP Mode

Run:

```bash
janusz mcp serve
```

The MCP server exposes:

- tools: `janusz_json`, `janusz_skill`, `janusz_test`, `janusz_manifest`
- resources: `janusz://memory`, `janusz://skills`, `janusz://packages`
- prompts: `create_skill`, `review_skill`, `convert_docs_to_agent_skill`

The server uses stdio JSON-RPC and keeps normal command output out of stdout so
an MCP host can parse responses reliably.

## Registry And Plugins

Build a registry:

```bash
janusz registry build --skills-dir skills
janusz registry search "repo test" --min-score 75
```

Bundle skills:

```bash
janusz package plugin --name repo-tools --skill skills/repo-helper --output-dir dist/repo-tools
```

The plugin output includes `.codex-plugin/plugin.json`, selected skill folders,
and a Janusz tool manifest unless `--no-manifest` is used.

## Safety

- Treat source documents and generated references as untrusted data.
- Review generated skills before global installation.
- Keep secrets out of JSON packages, `references/source.json`, and memory files.
- Prefer explicit input and output paths in orchestrated runs.

## Skill Research Notes

The memory catalog is based on locally available skills plus the public Codex
skills model:

- Codex skills are `SKILL.md` directories with optional `scripts/`, `references/`,
  `assets/`, and `agents/` folders.
- Skill routing depends on concise names, descriptions, triggers, and task scope.
- The public `openai/skills` catalog is useful for future expansion through
  `skill-installer`; Janusz stores that catalog as a source hint, not as trusted
  executable content.
