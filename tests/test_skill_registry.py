"""Tests for the local skill registry."""

from pathlib import Path

from janusz.skill_registry import build_registry, search_registry

from .test_skill_quality import write_good_skill


def test_build_registry_writes_jsonl_and_sqlite(temp_dir):
    """Registry build should create both JSONL and SQLite outputs."""
    skill_dir = temp_dir / "skills" / "repo-helper"
    skill_dir.parent.mkdir()
    write_good_skill(skill_dir)
    jsonl_path = temp_dir / "registry" / "skills.jsonl"
    sqlite_path = temp_dir / "registry" / "skills.sqlite"

    entries = build_registry(
        [str(skill_dir.parent)], output_jsonl=jsonl_path, sqlite_path=sqlite_path
    )

    assert len(entries) == 1
    assert jsonl_path.exists()
    assert sqlite_path.exists()


def test_search_registry_filters_by_query_category_and_score(temp_dir):
    """Registry search should use triggers, category, and quality score."""
    skill_dir = temp_dir / "skills" / "repo-helper"
    skill_dir.parent.mkdir()
    write_good_skill(skill_dir)
    jsonl_path = temp_dir / "skills.jsonl"
    build_registry([str(skill_dir.parent)], output_jsonl=jsonl_path, sqlite_path=None)

    results = search_registry(
        "test workflow",
        registry_path=Path(jsonl_path),
        category="repo_operations",
        min_score=80,
    )

    assert len(results) == 1
    assert results[0]["name"] == "repo-helper"
