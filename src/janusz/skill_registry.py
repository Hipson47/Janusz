#!/usr/bin/env python3
"""Local JSONL/SQLite registry for Janusz skill packages."""

import json
import sqlite3
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .skill_quality import skill_summary_for_registry

DEFAULT_REGISTRY_JSONL = Path("registry/skills.jsonl")
DEFAULT_REGISTRY_SQLITE = Path("registry/skills.sqlite")


def discover_skill_dirs(roots: Sequence[str]) -> list[Path]:
    """Discover skill directories under one or more roots."""
    seen = set()
    skills: list[Path] = []

    for root_value in roots:
        root = Path(root_value).expanduser()
        if not root.exists():
            continue
        candidates: Iterable[Path]
        if root.is_file() and root.name == "SKILL.md":
            candidates = [root]
        elif (root / "SKILL.md").exists():
            candidates = [root / "SKILL.md"]
        else:
            candidates = root.rglob("SKILL.md")

        for skill_file in candidates:
            skill_dir = skill_file.parent
            if any(
                part in {".git", ".venv", "__pycache__", "node_modules"} for part in skill_dir.parts
            ):
                continue
            resolved = str(skill_dir.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            skills.append(skill_dir)

    return sorted(skills)


def build_registry(
    roots: Sequence[str],
    output_jsonl: Path = DEFAULT_REGISTRY_JSONL,
    sqlite_path: Path | None = DEFAULT_REGISTRY_SQLITE,
) -> list[dict[str, Any]]:
    """Build a local skill registry from skill directories."""
    entries: list[dict[str, Any]] = []
    indexed_at = utc_now()

    for skill_dir in discover_skill_dirs(roots):
        try:
            entry = skill_summary_for_registry(skill_dir)
        except Exception as exc:
            entry = {
                "name": skill_dir.name,
                "path": str(skill_dir),
                "description": "",
                "category": "invalid",
                "triggers": [],
                "quality_score": 0,
                "grade": "poor",
                "agent_usable": False,
                "issue_count": 1,
                "error": str(exc),
            }
        entry["indexed_at"] = indexed_at
        entries.append(entry)

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(entries, output_jsonl)

    if sqlite_path is not None:
        write_sqlite(entries, sqlite_path)

    return entries


def write_jsonl(entries: Sequence[dict[str, Any]], output_path: Path) -> None:
    """Write registry entries to JSONL."""
    with open(output_path, "w", encoding="utf-8") as file:
        for entry in entries:
            json.dump(entry, file, ensure_ascii=False, sort_keys=True)
            file.write("\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load registry entries from JSONL."""
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.strip():
                data = json.loads(line)
                if isinstance(data, dict):
                    entries.append(data)
    return entries


def write_sqlite(entries: Sequence[dict[str, Any]], sqlite_path: Path) -> None:
    """Write registry entries to SQLite."""
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS skills (
                name TEXT NOT NULL,
                path TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                triggers_json TEXT NOT NULL,
                quality_score INTEGER NOT NULL,
                grade TEXT NOT NULL,
                agent_usable INTEGER NOT NULL,
                issue_count INTEGER NOT NULL,
                indexed_at TEXT NOT NULL
            )
            """
        )
        connection.execute("DELETE FROM skills")
        connection.executemany(
            """
            INSERT INTO skills (
                name, path, description, category, triggers_json, quality_score,
                grade, agent_usable, issue_count, indexed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    entry.get("name", ""),
                    entry.get("path", ""),
                    entry.get("description", ""),
                    entry.get("category", "uncategorized"),
                    json.dumps(entry.get("triggers", []), ensure_ascii=False),
                    int(entry.get("quality_score", 0)),
                    entry.get("grade", "poor"),
                    1 if entry.get("agent_usable") else 0,
                    int(entry.get("issue_count", 0)),
                    entry.get("indexed_at", utc_now()),
                )
                for entry in entries
            ],
        )
        connection.commit()
    finally:
        connection.close()


def search_registry(
    query: str = "",
    registry_path: Path = DEFAULT_REGISTRY_JSONL,
    category: str | None = None,
    min_score: int = 0,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search a JSONL registry by query, trigger, category, and score."""
    query_terms = [term.lower() for term in query.split() if term.strip()]
    results = []

    for entry in load_jsonl(registry_path):
        if category and entry.get("category") != category:
            continue
        if int(entry.get("quality_score", 0)) < min_score:
            continue
        haystack = build_search_text(entry)
        if query_terms and not all(term in haystack for term in query_terms):
            continue
        results.append(entry)

    results.sort(key=lambda item: int(item.get("quality_score", 0)), reverse=True)
    return results[:limit]


def build_search_text(entry: dict[str, Any]) -> str:
    """Build lowercase search text for one registry entry."""
    parts = [
        entry.get("name", ""),
        entry.get("description", ""),
        entry.get("category", ""),
        " ".join(str(trigger) for trigger in entry.get("triggers", [])),
    ]
    return " ".join(parts).lower()


def utc_now() -> str:
    """Return an ISO timestamp without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
