"""Tests for Janusz orchestrator tool manifest."""

import json

from janusz.orchestrator_tool import build_tool_manifest


def test_tool_manifest_is_json_serializable():
    """Orchestrators should be able to read the manifest as plain JSON."""
    manifest = build_tool_manifest()

    encoded = json.dumps(manifest)

    assert "janusz" in encoded
    assert manifest["kind"] == "local_cli_tool"


def test_tool_manifest_contains_expected_commands():
    """The manifest should expose the stable Janusz automation surface."""
    manifest = build_tool_manifest()
    command_names = {item["name"] for item in manifest["commands"]}

    assert "create_json_package" in command_names
    assert "create_skill_package" in command_names
    assert "export_memory_context" in command_names
    assert "export_tool_manifest" in command_names


def test_tool_manifest_uses_current_formats():
    """The orchestrator surface should advertise the current interchange formats."""
    manifest = build_tool_manifest()

    assert "json" in manifest["output_formats"]
    assert "codex_skill_folder" in manifest["output_formats"]


def test_tool_manifest_does_not_leak_local_developer_paths():
    """Generated manifests should be portable across checkout directories."""
    manifest = build_tool_manifest()
    encoded = json.dumps(manifest)
    developer_marker = "hipson" + "47"

    assert "/home/" not in encoded
    assert developer_marker not in encoded
    assert "working_directory_hint" in manifest
