"""Tests for Janusz durable memory."""

import json

from janusz.memory import JanuszMemory, build_default_memory


def test_default_memory_contains_useful_skill_packs():
    """The default catalog should include orchestration and skill-authoring packs."""
    data = build_default_memory()
    names = {item["name"] for item in data["skill_packs"]}

    assert "hipson-workflow" in names
    assert "skill-creator" in names
    assert "skill-installer" in names
    assert "openai-docs" in names


def test_memory_seed_writes_json(temp_dir):
    """Seeding memory should create a durable JSON file."""
    path = temp_dir / "memory" / "janusz_memory.json"
    memory = JanuszMemory(path)

    data = memory.seed()

    assert path.exists()
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted["version"] == data["version"]
    assert persisted["skill_packs"]


def test_export_tool_context_is_compact_and_ordered(temp_dir):
    """The exported context should be usable by an orchestrator."""
    path = temp_dir / "memory.json"
    memory = JanuszMemory(path)
    memory.seed()

    context = memory.export_tool_context()
    priorities = [item["priority"] for item in context["skill_packs"]]

    assert context["tool"] == "janusz"
    assert context["tool_contracts"]
    assert priorities == sorted(priorities, reverse=True)
    assert context["skill_packs"][0]["name"] == "hipson-workflow"
