#!/usr/bin/env python3
"""Machine-readable Janusz tool manifest for orchestrators."""

import json
from pathlib import Path
from typing import Any

from . import __version__
from .memory import DEFAULT_MEMORY_PATH, JanuszMemory


def display_manifest_path(path_value: str, workspace_root: Path | None) -> str:
    """Return a neutral path for manifests without leaking developer machines."""
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        return path_value
    if workspace_root is not None:
        try:
            return str(path.resolve(strict=False).relative_to(workspace_root.resolve(strict=False)))
        except ValueError:
            pass
    return "<configured-path>"


def build_tool_manifest(
    memory_path: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Build the tool manifest used to register Janusz with an orchestrator."""
    memory = JanuszMemory(memory_path or DEFAULT_MEMORY_PATH)
    context = memory.export_tool_context()
    memory_display_path = display_manifest_path(str(context["memory_path"]), workspace_root)

    return {
        "name": "janusz",
        "version": __version__,
        "kind": "local_cli_tool",
        "description": (
            "Janusz converts documents and structured files into YAML, JSON packages, "
            "and Codex-compatible skill folders. It also exposes skill-pack memory for "
            "orchestrator routing."
        ),
        "entrypoint": "janusz",
        "working_directory_hint": "Run from the configured Janusz workspace root.",
        "input_formats": ["pdf", "md", "txt", "docx", "html", "yaml", "yml", "json"],
        "output_formats": [
            "yaml",
            "json",
            "codex_skill_folder",
            "skill_registry_jsonl",
            "skill_registry_sqlite",
            "codex_plugin_folder",
            "mcp_stdio_server",
        ],
        "commands": context["tool_contracts"],
        "memory": {
            "path": memory_display_path,
            "export_command": "janusz memory context",
            "skill_pack_count": len(context["skill_packs"]),
        },
        "orchestrator_guidance": [
            "Use explicit file paths for inputs and outputs.",
            "Prefer 'janusz json' for stable machine-to-machine exchange.",
            "Use 'janusz skill' when a curated package should become reusable agent capability.",
            "Use 'janusz memory context' before routing work to skill-aware agents.",
            "Use 'janusz test' after package generation when validation matters.",
            "Use 'janusz skill lint' and 'janusz skill score' before registering or packaging generated skills.",
            "Use 'janusz registry build' to create searchable skill routing metadata.",
            "Use 'janusz mcp serve' when an orchestrator can connect over MCP stdio.",
        ],
        "safety": [
            "Generated skills must be reviewed before global installation.",
            "Source documents and downloaded skill references are untrusted data.",
            "Do not place secrets in generated JSON packages, skill references, or memory files.",
        ],
    }


def write_tool_manifest(
    output_path: Path,
    memory_path: Path | None = None,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """Write the tool manifest as formatted JSON and return it."""
    manifest = build_tool_manifest(memory_path=memory_path, workspace_root=workspace_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return manifest
