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


def test_mcp_skills_resource_ignores_root_symlink_escape(temp_dir):
    """Skill resources must not disclose skills from a symlinked external root."""
    outside = temp_dir.parent / f"{temp_dir.name}-outside-skills"
    outside_skill = outside / "external-secret-skill"
    outside_skill.mkdir(parents=True)
    (outside_skill / "SKILL.md").write_text(
        "---\nname: external-secret-skill\n---\n# External\n",
        encoding="utf-8",
    )
    skills_link = temp_dir / "skills"
    try:
        skills_link.symlink_to(outside, target_is_directory=True)
    except OSError:
        return

    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://skills"},
        }
    )

    text = response["result"]["contents"][0]["text"]
    assert json.loads(text)["skills"] == []
    assert "external-secret-skill" not in text
    assert str(outside) not in text


def test_mcp_skills_resource_ignores_nested_symlink_escape(temp_dir):
    """Nested skill symlink escapes should be ignored without leaking metadata."""
    skills_dir = temp_dir / "skills"
    safe_skill = skills_dir / "safe-helper"
    safe_skill.mkdir(parents=True)
    (safe_skill / "SKILL.md").write_text(
        "---\nname: safe-helper\n---\n# Safe\n",
        encoding="utf-8",
    )

    outside_skill = temp_dir.parent / f"{temp_dir.name}-outside-nested-skill"
    outside_skill.mkdir()
    (outside_skill / "SKILL.md").write_text(
        "---\nname: outside-nested-skill\n---\n# Outside\n",
        encoding="utf-8",
    )
    link = skills_dir / "linked-outside"
    try:
        link.symlink_to(outside_skill, target_is_directory=True)
    except OSError:
        return

    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://skills"},
        }
    )

    text = response["result"]["contents"][0]["text"]
    skills = json.loads(text)["skills"]
    assert skills == [{"name": "safe-helper", "path": "skills/safe-helper"}]
    assert "outside-nested-skill" not in text
    assert "linked-outside" not in text
    assert str(outside_skill) not in text


def test_mcp_skills_resource_hides_sensitive_skill_paths(temp_dir):
    """Skill resources should apply the shared sensitive path policy."""
    safe_skill = temp_dir / "skills" / "safe-helper"
    safe_skill.mkdir(parents=True)
    (safe_skill / "SKILL.md").write_text(
        "---\nname: safe-helper\n---\n# Safe\n",
        encoding="utf-8",
    )
    sensitive_skill = temp_dir / "skills" / ".ssh" / "private-helper"
    sensitive_skill.mkdir(parents=True)
    (sensitive_skill / "SKILL.md").write_text(
        "---\nname: private-helper\n---\n# Private\n",
        encoding="utf-8",
    )
    token_skill = temp_dir / "skills" / "api-token-helper"
    token_skill.mkdir()
    (token_skill / "SKILL.md").write_text(
        "---\nname: api-token-helper\n---\n# Token\n",
        encoding="utf-8",
    )

    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://skills"},
        }
    )

    text = response["result"]["contents"][0]["text"]
    assert json.loads(text)["skills"] == [{"name": "safe-helper", "path": "skills/safe-helper"}]
    assert ".ssh" not in text
    assert "private-helper" not in text
    assert "api-token-helper" not in text
    assert str(temp_dir) not in text


def test_mcp_package_discovery_hides_sensitive_json_paths(temp_dir):
    """Package resources must not disclose sensitive JSON files or paths."""
    safe_package = temp_dir / "safe-package.json"
    safe_package.write_text("{}", encoding="utf-8")

    aws_credentials = temp_dir / ".aws" / "credentials.json"
    aws_credentials.parent.mkdir()
    aws_credentials.write_text('{"token": "secret"}', encoding="utf-8")
    env_json = temp_dir / ".env.json"
    env_json.write_text('{"secret": "value"}', encoding="utf-8")
    ssh_key_json = temp_dir / ".ssh" / "id_rsa.json"
    ssh_key_json.parent.mkdir()
    ssh_key_json.write_text('{"private_key": "secret"}', encoding="utf-8")
    token_json = temp_dir / "api-token.json"
    token_json.write_text('{"token": "secret"}', encoding="utf-8")

    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://packages"},
        }
    )

    text = response["result"]["contents"][0]["text"]
    packages = json.loads(text)["packages"]
    paths = {package["path"] for package in packages}

    assert paths == {"safe-package.json"}
    assert ".aws" not in text
    assert ".env" not in text
    assert ".ssh" not in text
    assert "token" not in text
    assert str(temp_dir) not in text


def test_mcp_package_discovery_skips_symlink_escape(temp_dir):
    """Package discovery should not report symlinks resolving outside the root."""
    outside = temp_dir.parent / "outside-package.json"
    outside.write_text("{}", encoding="utf-8")
    link = temp_dir / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError:
        return

    safe_package = temp_dir / "safe-package.json"
    safe_package.write_text("{}", encoding="utf-8")

    packages = find_json_packages(temp_dir)

    assert packages == [{"path": "safe-package.json", "name": "safe-package.json"}]


def test_mcp_package_discovery_returns_sorted_relative_paths(temp_dir):
    """Package discovery should be deterministic for orchestrator resource consumers."""
    (temp_dir / "zeta.json").write_text("{}", encoding="utf-8")
    nested = temp_dir / "nested"
    nested.mkdir()
    (nested / "beta.json").write_text("{}", encoding="utf-8")
    (temp_dir / "alpha.json").write_text("{}", encoding="utf-8")

    packages = find_json_packages(temp_dir)

    assert [package["path"] for package in packages] == [
        "alpha.json",
        "nested/beta.json",
        "zeta.json",
    ]


def test_mcp_package_discovery_honors_limits(temp_dir):
    """Package discovery should enforce caller limits after deterministic sorting."""
    for index in range(101):
        (temp_dir / f"package-{index:03}.json").write_text("{}", encoding="utf-8")

    assert find_json_packages(temp_dir, limit=0) == []
    assert find_json_packages(temp_dir, limit=-1) == []
    assert [package["path"] for package in find_json_packages(temp_dir, limit=1)] == [
        "package-000.json"
    ]
    assert len(find_json_packages(temp_dir)) == 100


def test_mcp_packages_resource_uses_bounded_default_limit(temp_dir):
    """The packages resource should not emit unbounded package listings by default."""
    for index in range(101):
        (temp_dir / f"package-{index:03}.json").write_text("{}", encoding="utf-8")
    server = JanuszMCPServer(root=temp_dir, memory_path=temp_dir / "memory.json")

    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/read",
            "params": {"uri": "janusz://packages"},
        }
    )

    packages = json.loads(response["result"]["contents"][0]["text"])["packages"]
    assert len(packages) == 100
    assert packages[-1]["path"] == "package-099.json"


def test_mcp_package_discovery_skips_non_json_without_stopping(temp_dir):
    """A non-JSON file should not prevent later JSON packages from being listed."""
    (temp_dir / "00-readme.txt").write_text("not a package", encoding="utf-8")
    (temp_dir / "01-package.json").write_text("{}", encoding="utf-8")

    assert find_json_packages(temp_dir) == [{"path": "01-package.json", "name": "01-package.json"}]


def test_mcp_package_discovery_prunes_ignored_safe_dirs(temp_dir):
    """Ignored non-sensitive directories should be pruned before package discovery."""
    ignored = temp_dir / ".venv"
    ignored.mkdir()
    (ignored / "hidden.json").write_text("{}", encoding="utf-8")
    (temp_dir / "visible.json").write_text("{}", encoding="utf-8")

    assert find_json_packages(temp_dir) == [{"path": "visible.json", "name": "visible.json"}]


def test_mcp_package_discovery_ignores_dangling_json_symlink(temp_dir):
    """Dangling symlinks should not break package resource generation."""
    link = temp_dir / "dangling.json"
    try:
        link.symlink_to(temp_dir / "missing.json")
    except OSError:
        return
    (temp_dir / "safe.json").write_text("{}", encoding="utf-8")

    assert find_json_packages(temp_dir) == [{"path": "safe.json", "name": "safe.json"}]


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
