#!/usr/bin/env python3
"""Package Janusz skills into a distributable Codex plugin bundle."""

import json
import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .orchestrator_tool import build_tool_manifest
from .skill_packager import slugify
from .skill_quality import parse_skill_document, score_skill


class PluginPackageError(Exception):
    """Raised when a plugin package cannot be created."""


def package_plugin(
    skill_paths: Sequence[str],
    output_dir: str,
    name: str,
    version: str = "0.1.0",
    description: str | None = None,
    overwrite: bool = False,
    include_manifest: bool = True,
) -> Path:
    """Create a plugin bundle containing one or more skills."""
    if not skill_paths:
        raise PluginPackageError("At least one --skill path is required")

    plugin_root = Path(output_dir)
    if plugin_root.exists():
        if not overwrite:
            raise FileExistsError(f"Plugin output already exists: {plugin_root}")
        shutil.rmtree(plugin_root)

    plugin_root.mkdir(parents=True, exist_ok=True)
    skills_root = plugin_root / "skills"
    metadata_root = plugin_root / ".codex-plugin"
    manifest_root = plugin_root / "manifest"
    skills_root.mkdir()
    metadata_root.mkdir()
    manifest_root.mkdir()

    bundled_skills = []
    for skill_path in skill_paths:
        document = parse_skill_document(skill_path)
        skill_name = str(document.frontmatter.get("name") or document.root.name)
        destination = skills_root / slugify(skill_name)
        shutil.copytree(
            document.root,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        score = score_skill(destination)
        bundled_skills.append(
            {
                "name": skill_name,
                "path": str(destination.relative_to(plugin_root)),
                "quality_score": score["score"],
                "agent_usable": score["agent_usable"],
            }
        )

    manifest_files: list[str] = []
    if include_manifest:
        manifest_path = manifest_root / "janusz_tool_manifest.json"
        manifest_path.write_text(
            json.dumps(build_tool_manifest(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        manifest_files.append(str(manifest_path.relative_to(plugin_root)))

    plugin_json = build_plugin_manifest(
        name=name,
        version=version,
        description=description,
        skills=bundled_skills,
        manifest_files=manifest_files,
    )
    (metadata_root / "plugin.json").write_text(
        json.dumps(plugin_json, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return plugin_root


def build_plugin_manifest(
    name: str,
    version: str,
    description: str | None,
    skills: Sequence[dict[str, Any]],
    manifest_files: Sequence[str],
) -> dict[str, Any]:
    """Build the plugin manifest stored in .codex-plugin/plugin.json."""
    slug = slugify(name)
    return {
        "schema_version": "1.0",
        "name": slug,
        "display_name": name,
        "version": version,
        "description": description
        or "Janusz-generated plugin bundle with agent skills and tool metadata.",
        "generated_by": "janusz",
        "skills": list(skills),
        "manifests": list(manifest_files),
    }
