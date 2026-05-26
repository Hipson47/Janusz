"""CLI smoke tests for Janusz memory and tool commands."""

import json
import subprocess
import sys

from .test_skill_quality import write_good_skill


def test_cli_memory_context_outputs_json(temp_dir):
    """The memory context command should print orchestrator-ready JSON."""
    memory_path = temp_dir / "memory.json"
    seed_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "memory",
            "seed",
            "--path",
            str(memory_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    context_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "memory",
            "context",
            "--path",
            str(memory_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    context = json.loads(context_result.stdout)

    assert "Memory ready" in seed_result.stdout
    assert context["tool"] == "janusz"
    assert context["skill_packs"]


def test_cli_tool_manifest_outputs_json(temp_dir):
    """The tool manifest command should print a valid local tool contract."""
    memory_path = temp_dir / "memory.json"
    output_path = temp_dir / "manifest.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "tool",
            "manifest",
            "--memory-path",
            str(memory_path),
            "--output",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))

    assert "Tool manifest written" in result.stdout
    assert manifest["name"] == "janusz"
    assert manifest["commands"]


def test_cli_skill_lint_and_score(temp_dir):
    """The skill lint and score commands should run through argparse."""
    skill_dir = temp_dir / "repo-helper"
    write_good_skill(skill_dir)

    lint_result = subprocess.run(
        [sys.executable, "-m", "janusz.cli", "skill", "lint", str(skill_dir), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    score_result = subprocess.run(
        [sys.executable, "-m", "janusz.cli", "skill", "score", str(skill_dir), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(lint_result.stdout)["valid"] is True
    assert json.loads(score_result.stdout)["agent_usable"] is True


def test_cli_registry_and_package_plugin(temp_dir):
    """The registry and plugin package commands should be usable from CLI."""
    skill_dir = temp_dir / "skills" / "repo-helper"
    skill_dir.parent.mkdir()
    write_good_skill(skill_dir)
    registry_path = temp_dir / "registry.jsonl"
    plugin_path = temp_dir / "plugin"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "registry",
            "build",
            "--skills-dir",
            str(skill_dir.parent),
            "--output",
            str(registry_path),
            "--no-sqlite",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    search_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "registry",
            "search",
            "repo",
            "--registry",
            str(registry_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "janusz.cli",
            "package",
            "plugin",
            "--name",
            "Repo Tools",
            "--skill",
            str(skill_dir),
            "--output-dir",
            str(plugin_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(search_result.stdout)[0]["name"] == "repo-helper"
    assert (plugin_path / ".codex-plugin" / "plugin.json").exists()
