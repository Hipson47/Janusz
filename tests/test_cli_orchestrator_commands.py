"""CLI smoke tests for Janusz memory and tool commands."""

import contextlib
import io
import json
import sys

from janusz import cli

from .test_skill_quality import write_good_skill


def run_cli(args: list[str]) -> tuple[int, str, str]:
    """Run the CLI in-process so coverage includes the argparse command surface."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    original_argv = sys.argv
    sys.argv = ["janusz", *args]
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                cli.main()
                exit_code = 0
            except SystemExit as exc:
                exit_code = int(exc.code) if isinstance(exc.code, int) else 0
    finally:
        sys.argv = original_argv

    return exit_code, stdout.getvalue(), stderr.getvalue()


def test_cli_help_and_version_are_available():
    """The installed command should expose help and version metadata."""
    help_code, help_stdout, _ = run_cli(["--help"])
    version_code, version_stdout, _ = run_cli(["--version"])

    assert help_code == 0
    assert "Document-to-JSON Pipeline" in help_stdout
    assert version_code == 0
    assert "Janusz 1.0.0" in version_stdout


def test_cli_memory_context_outputs_json(temp_dir):
    """The memory context command should print orchestrator-ready JSON."""
    memory_path = temp_dir / "memory.json"
    seed_code, seed_stdout, _ = run_cli(
        [
            "memory",
            "seed",
            "--path",
            str(memory_path),
        ]
    )
    context_code, context_stdout, _ = run_cli(
        [
            "memory",
            "context",
            "--path",
            str(memory_path),
        ]
    )

    context = json.loads(context_stdout)

    assert seed_code == 0
    assert context_code == 0
    assert "Memory ready" in seed_stdout
    assert context["tool"] == "janusz"
    assert context["skill_packs"]


def test_cli_memory_list_outputs_summary(temp_dir):
    """The memory list command should show seeded skill-pack summaries."""
    memory_path = temp_dir / "memory.json"
    run_cli(["memory", "seed", "--path", str(memory_path)])

    exit_code, stdout, _ = run_cli(["memory", "list", "--path", str(memory_path)])

    assert exit_code == 0
    assert "Remembered skill packs:" in stdout
    assert "skill" in stdout.lower()


def test_cli_tool_manifest_outputs_json(temp_dir):
    """The tool manifest command should print a valid local tool contract."""
    memory_path = temp_dir / "memory.json"
    output_path = temp_dir / "manifest.json"

    exit_code, stdout, _ = run_cli(
        [
            "tool",
            "manifest",
            "--memory-path",
            str(memory_path),
            "--output",
            str(output_path),
        ]
    )

    manifest = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert "Tool manifest written" in stdout
    assert manifest["name"] == "janusz"
    assert manifest["commands"]


def test_cli_skill_lint_and_score(temp_dir):
    """The skill lint and score commands should run through argparse."""
    skill_dir = temp_dir / "repo-helper"
    write_good_skill(skill_dir)

    lint_code, lint_stdout, _ = run_cli(["skill", "lint", str(skill_dir), "--json"])
    score_code, score_stdout, _ = run_cli(["skill", "score", str(skill_dir), "--json"])

    assert lint_code == 0
    assert score_code == 0
    assert json.loads(lint_stdout)["valid"] is True
    assert json.loads(score_stdout)["agent_usable"] is True


def test_cli_json_validate_and_convert_paths(temp_dir):
    """JSON validation and conversion should return clear success/failure codes."""
    valid_json = temp_dir / "package.json"
    invalid_json = temp_dir / "invalid.json"
    markdown = temp_dir / "doc.md"
    output_json = temp_dir / "doc.json"
    valid_json.write_text('{"metadata": {"title": "ok"}}\n', encoding="utf-8")
    invalid_json.write_text("{broken", encoding="utf-8")
    markdown.write_text("# Title\n\nUseful content.", encoding="utf-8")

    valid_code, _, _ = run_cli(["json", "--file", str(valid_json), "--validate-only"])
    invalid_code, _, _ = run_cli(["json", "--file", str(invalid_json), "--validate-only"])
    missing_file_code, _, _ = run_cli(["json", "--validate-only"])
    convert_code, _, _ = run_cli(["json", "--file", str(markdown), "--output", str(output_json)])

    assert valid_code == 0
    assert invalid_code == 1
    assert missing_file_code == 1
    assert convert_code == 0
    assert output_json.exists()


def test_cli_convert_and_skill_create_paths(temp_dir):
    """Core conversion and skill creation paths should be covered in-process."""
    markdown = temp_dir / "source.md"
    markdown.write_text("# Agent Notes\n\nUse clear triggers and examples.", encoding="utf-8")
    unsupported = temp_dir / "source.bin"
    unsupported.write_bytes(b"\x00")
    json_output = temp_dir / "source.json"
    skill_output = temp_dir / "skills"

    convert_code, _, _ = run_cli(["convert", "--file", str(markdown)])
    unsupported_code, _, _ = run_cli(["convert", "--file", str(unsupported)])
    json_code, _, _ = run_cli(["json", "--file", str(markdown), "--output", str(json_output)])
    skill_code, skill_stdout, _ = run_cli(
        ["skill", "--file", str(json_output), "--output-dir", str(skill_output)]
    )

    assert convert_code == 0
    assert markdown.with_suffix(".yaml").exists()
    assert unsupported_code == 1
    assert json_code == 0
    assert skill_code == 0
    assert "Created skill package" in skill_stdout
    assert next(skill_output.glob("*/SKILL.md")).exists()


def test_cli_test_command_handles_valid_and_invalid_packages(temp_dir):
    """The package inspection command should return non-zero for malformed input."""
    valid_json = temp_dir / "package.json"
    invalid_json = temp_dir / "invalid.json"
    valid_json.write_text(
        json.dumps({"metadata": {}, "content": {"sections": []}, "analysis": {}}),
        encoding="utf-8",
    )
    invalid_json.write_text("[1, 2, 3]\n", encoding="utf-8")

    valid_code, _, _ = run_cli(["test", str(valid_json)])
    invalid_code, _, _ = run_cli(["test", str(invalid_json)])

    assert valid_code == 0
    assert invalid_code == 1


def test_cli_search_no_results_and_plugin_error_paths(temp_dir):
    """Common negative paths should return cleanly without tracebacks."""
    registry_path = temp_dir / "empty.jsonl"
    registry_path.write_text("", encoding="utf-8")

    search_code, search_stdout, _ = run_cli(
        ["registry", "search", "nothing", "--registry", str(registry_path)]
    )
    plugin_code, _, _ = run_cli(
        [
            "package",
            "plugin",
            "--name",
            "Broken",
            "--skill",
            str(temp_dir / "missing-skill"),
            "--output-dir",
            str(temp_dir / "plugin"),
        ]
    )

    assert search_code == 0
    assert "No matching skills found" in search_stdout
    assert plugin_code == 1


def test_cli_registry_and_package_plugin(temp_dir):
    """The registry and plugin package commands should be usable from CLI."""
    skill_dir = temp_dir / "skills" / "repo-helper"
    skill_dir.parent.mkdir()
    write_good_skill(skill_dir)
    registry_path = temp_dir / "registry.jsonl"
    plugin_path = temp_dir / "plugin"

    build_code, _, _ = run_cli(
        [
            "registry",
            "build",
            "--skills-dir",
            str(skill_dir.parent),
            "--output",
            str(registry_path),
            "--no-sqlite",
        ]
    )
    search_code, search_stdout, _ = run_cli(
        [
            "registry",
            "search",
            "repo",
            "--registry",
            str(registry_path),
            "--json",
        ]
    )
    package_code, _, _ = run_cli(
        [
            "package",
            "plugin",
            "--name",
            "Repo Tools",
            "--skill",
            str(skill_dir),
            "--output-dir",
            str(plugin_path),
        ]
    )

    assert build_code == 0
    assert search_code == 0
    assert package_code == 0
    assert json.loads(search_stdout)[0]["name"] == "repo-helper"
    assert (plugin_path / ".codex-plugin" / "plugin.json").exists()
