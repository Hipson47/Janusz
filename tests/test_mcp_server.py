"""Tests for the Janusz MCP stdio server core."""

import json
from pathlib import Path

from janusz.mcp_server import JanuszMCPServer, find_json_packages


def test_mcp_initialize_and_tool_list():
    """The MCP server should advertise tools during initialization."""
    server = JanuszMCPServer(root=Path("."))

    initialize = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    tools = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

    assert initialize["result"]["serverInfo"]["name"] == "janusz"
    tool_names = {tool["name"] for tool in tools["result"]["tools"]}
    assert {"janusz_json", "janusz_skill", "janusz_test", "janusz_manifest"} <= tool_names


def test_mcp_resources_and_prompts_are_available(temp_dir):
    """The MCP server should expose memory, skill catalog, packages, and prompts."""
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    resources = server.handle({"jsonrpc": "2.0", "id": 1, "method": "resources/list"})
    prompts = server.handle({"jsonrpc": "2.0", "id": 2, "method": "prompts/list"})

    resource_uris = {resource["uri"] for resource in resources["result"]["resources"]}
    prompt_names = {prompt["name"] for prompt in prompts["result"]["prompts"]}

    assert {"janusz://memory", "janusz://skills", "janusz://packages"} <= resource_uris
    assert {"create_skill", "review_skill", "convert_docs_to_agent_skill"} <= prompt_names


def test_mcp_manifest_tool_returns_text_result(temp_dir):
    """The manifest tool should return MCP text content."""
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "janusz_manifest", "arguments": {}},
        }
    )

    text = response["result"]["content"][0]["text"]
    assert '"name": "janusz"' in text


def test_mcp_jsonrpc_utility_paths(temp_dir):
    """Basic JSON-RPC utility methods should return sanitized structured responses."""
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    parse_error = server.handle_json("{broken")
    initialized = server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    ping = server.handle({"jsonrpc": "2.0", "id": 1, "method": "ping"})
    unknown = server.handle({"jsonrpc": "2.0", "id": 2, "method": "unknown/method"})

    assert parse_error is not None
    assert parse_error["error"]["code"] == -32700
    assert initialized is None
    assert ping["result"] == {}
    assert unknown["error"]["code"] == -32601


def test_mcp_prompt_templates_and_unknown_prompt(temp_dir):
    """Prompt resources should be accessible and unknown prompt names should be safe errors."""
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    create_prompt = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/get",
            "params": {"name": "create_skill", "arguments": {"source_path": "docs"}},
        }
    )
    review_prompt = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "prompts/get",
            "params": {"name": "review_skill", "arguments": {"skill_path": "skills/a"}},
        }
    )
    convert_prompt = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "prompts/get",
            "params": {"name": "convert_docs_to_agent_skill", "arguments": {}},
        }
    )
    unknown_prompt = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "prompts/get",
            "params": {"name": "missing"},
        }
    )

    assert (
        "Create a concise Codex skill" in create_prompt["result"]["messages"][0]["content"]["text"]
    )
    assert "Review `skills/a`" in review_prompt["result"]["messages"][0]["content"]["text"]
    assert "convert `<docs_path>`" in convert_prompt["result"]["messages"][0]["content"]["text"]
    assert unknown_prompt["error"]["code"] == -32603


def test_mcp_resource_reads_and_package_discovery(temp_dir):
    """Resources should serialize workspace-relative data."""
    skills_dir = temp_dir / "skills" / "helper"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("---\nname: helper\n---\n", encoding="utf-8")
    package = temp_dir / "package.json"
    package.write_text("{}", encoding="utf-8")
    ignored = temp_dir / ".git" / "config.json"
    ignored.parent.mkdir()
    ignored.write_text("{}", encoding="utf-8")
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    memory = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://memory"},
        }
    )
    skills = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": "janusz://skills"},
        }
    )
    packages = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/read",
            "params": {"uri": "janusz://packages"},
        }
    )
    unknown = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {"uri": "janusz://missing"},
        }
    )

    assert "skill_packs" in memory["result"]["contents"][0]["text"]
    assert "skills/helper" in skills["result"]["contents"][0]["text"]
    assert find_json_packages(temp_dir) == [{"path": "package.json", "name": "package.json"}]
    assert "package.json" in packages["result"]["contents"][0]["text"]
    assert unknown["error"]["code"] == -32603


def test_mcp_rejects_path_traversal_without_leaking_root(temp_dir):
    """Tool calls should not access files outside the configured workspace."""
    outside = temp_dir.parent / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "janusz_test", "arguments": {"path": "../outside.json"}},
        }
    )

    message = response["error"]["message"]
    assert "outside the configured workspace root" in message
    assert str(temp_dir) not in message


def test_mcp_rejects_sensitive_files(temp_dir):
    """Sensitive files should be denied even when they are inside the workspace."""
    secret = temp_dir / ".env"
    secret.write_text("TOKEN=secret", encoding="utf-8")
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "janusz_test", "arguments": {"path": ".env"}},
        }
    )

    assert "Sensitive files" in response["error"]["message"]


def test_mcp_rejects_symlink_escape(temp_dir):
    """Symlinks that resolve outside the workspace should be rejected."""
    outside = temp_dir.parent / "outside-package.json"
    outside.write_text("{}", encoding="utf-8")
    link = temp_dir / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError:
        return

    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "janusz_test", "arguments": {"path": "linked.json"}},
        }
    )

    assert "outside the configured workspace root" in response["error"]["message"]


def test_mcp_rejects_oversized_files(temp_dir):
    """MCP input files should have a configurable size limit."""
    package = temp_dir / "large.json"
    package.write_text("{}\n", encoding="utf-8")
    server = JanuszMCPServer(
        root=temp_dir,
        memory_path=temp_dir / "memory.json",
        max_file_bytes=1,
    )

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "janusz_test", "arguments": {"path": "large.json"}},
        }
    )

    assert "size limit" in response["error"]["message"]


def test_mcp_json_tool_uses_workspace_relative_output(temp_dir):
    """Successful MCP tool results should not leak absolute local paths."""
    source = temp_dir / "source.json"
    source.write_text(json.dumps({"name": "demo", "items": [1, 2]}), encoding="utf-8")
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "janusz_json",
                "arguments": {"input_path": "source.json", "output_path": "out/package.json"},
            },
        }
    )

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["ok"] is True
    assert payload["input_path"] == "source.json"
    assert payload["output_path"] == "out/package.json"
