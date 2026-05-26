"""Tests for repository ingestion into skill packages."""

import json

from janusz.repo_ingester import ingest_repo
from janusz.skill_quality import lint_skill


def test_ingest_repo_creates_operations_skill(temp_dir):
    """Repository ingest should produce a usable operations skill."""
    repo = temp_dir / "demo-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo Repo\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (repo / "Makefile").write_text("test:\n\tpytest\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")

    skill_dir = ingest_repo(str(repo), output_dir=str(temp_dir / "skills"))

    assert (skill_dir / "SKILL.md").exists()
    inventory = json.loads(
        (skill_dir / "references" / "repo_inventory.json").read_text(encoding="utf-8")
    )
    assert inventory["metadata"]["name"] == "demo-repo"
    assert inventory["commands"]
    assert lint_skill(skill_dir)["agent_usable"] is True
