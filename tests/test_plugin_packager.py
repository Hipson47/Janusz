"""Tests for plugin package creation."""

import json

from janusz.plugin_packager import package_plugin

from .test_skill_quality import write_good_skill


def test_package_plugin_bundles_skills_and_manifest(temp_dir):
    """Plugin packaging should create .codex-plugin metadata and copy skills."""
    skill_dir = temp_dir / "repo-helper"
    write_good_skill(skill_dir)
    output_dir = temp_dir / "dist" / "repo-tools"

    plugin_path = package_plugin(
        [str(skill_dir)],
        output_dir=str(output_dir),
        name="Repo Tools",
    )

    plugin_json = json.loads(
        (plugin_path / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )

    assert plugin_json["name"] == "repo-tools"
    assert plugin_json["skills"][0]["name"] == "repo-helper"
    assert (plugin_path / "skills" / "repo-helper" / "SKILL.md").exists()
    assert (plugin_path / "manifest" / "janusz_tool_manifest.json").exists()
