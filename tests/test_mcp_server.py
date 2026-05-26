"""Tests for the Janusz MCP stdio server core."""

from pathlib import Path

from janusz.mcp_server import JanuszMCPServer


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
