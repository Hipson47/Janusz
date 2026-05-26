#!/usr/bin/env python3
"""Machine-readable Janusz tool manifest for orchestrators."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from . import __version__
from .memory import DEFAULT_MEMORY_PATH, JanuszMemory


def build_tool_manifest(memory_path: Optional[Path] = None) -> Dict[str, Any]:
    """Build the tool manifest used to register Janusz with an orchestrator."""
    memory = JanuszMemory(memory_path or DEFAULT_MEMORY_PATH)
    context = memory.export_tool_context()

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
        "working_directory_hint": "/home/hipson47/code/Janusz",
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
            "path": context["memory_path"],
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


def write_tool_manifest(output_path: Path, memory_path: Optional[Path] = None) -> Dict[str, Any]:
    """Write the tool manifest as formatted JSON and return it."""
    manifest = build_tool_manifest(memory_path=memory_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return manifest
