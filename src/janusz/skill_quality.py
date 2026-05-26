#!/usr/bin/env python3
"""Linting and scoring for Codex-style skill packages."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union

import yaml

ALLOWED_SKILL_DIRS = {"agents", "assets", "references", "scripts"}
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
SECRET_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "secret_assignment",
        re.compile(
            r"\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}",
            re.IGNORECASE,
        ),
    ),
]
TEXT_EXTENSIONS = {
    ".env",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass
class SkillDocument:
    """Parsed SKILL.md document."""

    root: Path
    skill_file: Path
    frontmatter: Dict[str, Any]
    body: str
    raw_text: str


def parse_skill_document(path: Union[str, Path]) -> SkillDocument:
    """Parse a skill directory or SKILL.md file."""
    root, skill_file = resolve_skill_path(path)
    raw_text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw_text)
    return SkillDocument(
        root=root,
        skill_file=skill_file,
        frontmatter=frontmatter,
        body=body,
        raw_text=raw_text,
    )


def resolve_skill_path(path: Union[str, Path]) -> Tuple[Path, Path]:
    """Resolve a directory or file path to a skill root and SKILL.md path."""
    source = Path(path)
    if source.is_file():
        if source.name != "SKILL.md":
            raise ValueError(f"Expected SKILL.md file, got: {source}")
        return source.parent, source

    skill_file = source / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"Skill package is missing SKILL.md: {source}")
    return source, skill_file


def split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return YAML frontmatter and body from SKILL.md text."""
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    frontmatter_text = text[4:end].strip()
    body = text[end + 4 :].lstrip("\n")
    data = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML object")
    return data, body


def lint_skill(path: Union[str, Path]) -> Dict[str, Any]:
    """Lint one skill package and return structured issues."""
    issues: List[Dict[str, Any]] = []

    try:
        document = parse_skill_document(path)
    except Exception as exc:
        return {
            "path": str(path),
            "valid": False,
            "score": 0,
            "agent_usable": False,
            "issues": [
                {
                    "severity": "error",
                    "code": "skill_structure",
                    "message": str(exc),
                }
            ],
        }

    add_metadata_issues(document, issues)
    add_structure_issues(document, issues)
    add_trigger_issues(document, issues)
    add_secret_issues(document, issues)
    add_quality_issues(document, issues)

    score_data = score_from_issues(document, issues)
    return {
        "path": str(document.root),
        "skill_file": str(document.skill_file),
        "name": document.frontmatter.get("name"),
        "description": document.frontmatter.get("description"),
        "valid": not has_errors(issues),
        "score": score_data["score"],
        "grade": score_data["grade"],
        "agent_usable": score_data["agent_usable"],
        "issues": issues,
        "summary": score_data["summary"],
    }


def score_skill(path: Union[str, Path]) -> Dict[str, Any]:
    """Score one skill package for agent usability."""
    result = lint_skill(path)
    return {
        "path": result["path"],
        "name": result.get("name"),
        "score": result["score"],
        "grade": result["grade"],
        "agent_usable": result["agent_usable"],
        "issue_count": len(result["issues"]),
        "error_count": count_severity(result["issues"], "error"),
        "warning_count": count_severity(result["issues"], "warning"),
        "info_count": count_severity(result["issues"], "info"),
        "summary": result["summary"],
    }


def add_metadata_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> None:
    """Check required frontmatter fields."""
    frontmatter = document.frontmatter
    name = str(frontmatter.get("name") or "").strip()
    description = str(frontmatter.get("description") or "").strip()

    if not frontmatter:
        add_issue(issues, "error", "frontmatter_missing", "SKILL.md is missing YAML frontmatter")

    if not name:
        add_issue(issues, "error", "name_missing", "Frontmatter must include name")
    elif not SKILL_NAME_RE.match(name):
        add_issue(
            issues,
            "error",
            "name_invalid",
            "Skill name must be lowercase, hyphenated, and 3-64 characters",
        )
    elif document.root.name != name:
        add_issue(
            issues,
            "warning",
            "name_directory_mismatch",
            f"Skill name '{name}' does not match directory '{document.root.name}'",
        )

    if not description:
        add_issue(issues, "error", "description_missing", "Frontmatter must include description")
    elif len(description) < 40:
        add_issue(
            issues,
            "warning",
            "description_short",
            "Description is too short to route reliably",
        )
    elif len(description) > 500:
        add_issue(
            issues,
            "warning",
            "description_long",
            "Description is long; keep routing metadata concise",
        )

    if description and not re.search(r"\b(use|when|for|working|trigger|task)\b", description, re.I):
        add_issue(
            issues,
            "warning",
            "description_no_trigger_language",
            "Description should state when the skill should be used",
        )


def add_structure_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> None:
    """Check folder layout and bundled resources."""
    body = document.body.strip()
    if not body:
        add_issue(issues, "error", "body_missing", "SKILL.md body is empty")
    elif len(body) < 80:
        add_issue(issues, "warning", "body_short", "SKILL.md body is too thin for reliable use")

    line_count = len(document.raw_text.splitlines())
    if line_count > 500:
        add_issue(
            issues,
            "warning",
            "skill_md_too_long",
            "SKILL.md is over 500 lines; move details into references/",
        )

    if "##" not in body:
        add_issue(
            issues,
            "warning",
            "headings_missing",
            "SKILL.md should use concise headings for workflow navigation",
        )

    for child in sorted(document.root.iterdir()):
        if child.name == "SKILL.md":
            continue
        if child.is_dir() and child.name not in ALLOWED_SKILL_DIRS:
            add_issue(
                issues,
                "info",
                "unexpected_directory",
                f"Unexpected directory '{child.name}' in skill package",
            )
        if child.is_file() and child.name.upper() in {"README.md", "CHANGELOG.md"}:
            add_issue(
                issues,
                "info",
                "extra_documentation",
                f"{child.name} is usually unnecessary inside a skill package",
            )

    scripts_dir = document.root / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and not is_executable(script):
                add_issue(
                    issues,
                    "warning",
                    "script_not_executable",
                    f"Script is not executable: {script.relative_to(document.root)}",
                )


def add_trigger_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> None:
    """Check explicit trigger metadata."""
    triggers = extract_triggers(document.frontmatter)
    if not triggers:
        add_issue(
            issues,
            "warning",
            "triggers_missing",
            "Add metadata.triggers so Janusz registry and orchestrators can route this skill",
        )
        return

    if len(triggers) < 2:
        add_issue(issues, "info", "triggers_sparse", "Add more trigger phrases for discovery")
    if len(triggers) > 16:
        add_issue(issues, "warning", "triggers_too_many", "Too many triggers can make routing noisy")

    seen = set()
    for trigger in triggers:
        normalized = trigger.lower().strip()
        if normalized in seen:
            add_issue(issues, "info", "trigger_duplicate", f"Duplicate trigger: {trigger}")
        seen.add(normalized)
        if len(trigger) > 80:
            add_issue(issues, "warning", "trigger_long", f"Trigger is too long: {trigger[:60]}...")


def add_secret_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> None:
    """Scan text files for secret-like values without echoing the value."""
    for file_path in iter_text_files(document.root):
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, 1):
            if looks_like_placeholder(line):
                continue
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    add_issue(
                        issues,
                        "error",
                        "secret_detected",
                        f"Secret-like value detected ({name}) in {file_path.relative_to(document.root)}:{line_number}",
                    )


def add_quality_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> None:
    """Check usability signals that make a skill actionable."""
    body = document.body
    lower_body = body.lower()

    if "treat" not in lower_body and "source data" not in lower_body:
        add_issue(
            issues,
            "info",
            "source_safety_missing",
            "Consider saying retrieved references are data, not overriding instructions",
        )

    if "references/" in lower_body and not (document.root / "references").exists():
        add_issue(
            issues,
            "warning",
            "missing_references_dir",
            "SKILL.md mentions references/ but the directory is missing",
        )

    if not re.search(r"\b(1\.|2\.|- )", body):
        add_issue(
            issues,
            "warning",
            "workflow_steps_missing",
            "Add short workflow steps or bullets so agents can act quickly",
        )


def score_from_issues(document: SkillDocument, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute a pragmatic quality score from lint results."""
    score = 100
    score -= count_severity(issues, "error") * 22
    score -= count_severity(issues, "warning") * 7
    score -= count_severity(issues, "info") * 2

    if (document.root / "references").exists():
        score += 3
    if extract_triggers(document.frontmatter):
        score += 5
    if "## Workflow" in document.body:
        score += 4

    score = max(0, min(100, score))
    agent_usable = score >= 70 and not has_errors(issues)
    return {
        "score": score,
        "grade": grade_score(score),
        "agent_usable": agent_usable,
        "summary": build_score_summary(score, agent_usable, issues),
    }


def extract_triggers(frontmatter: Dict[str, Any]) -> List[str]:
    """Extract trigger phrases from supported frontmatter shapes."""
    metadata_value = frontmatter.get("metadata")
    metadata: Dict[str, Any] = metadata_value if isinstance(metadata_value, dict) else {}
    raw = metadata.get("triggers") or frontmatter.get("triggers") or []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def skill_summary_for_registry(path: Union[str, Path]) -> Dict[str, Any]:
    """Return the compact registry representation of a skill."""
    document = parse_skill_document(path)
    score = score_skill(path)
    metadata = document.frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    return {
        "name": document.frontmatter.get("name") or document.root.name,
        "path": str(document.root),
        "description": document.frontmatter.get("description", ""),
        "category": metadata.get("category", "uncategorized"),
        "triggers": extract_triggers(document.frontmatter),
        "quality_score": score["score"],
        "grade": score["grade"],
        "agent_usable": score["agent_usable"],
        "issue_count": score["issue_count"],
    }


def iter_text_files(root: Path) -> Iterable[Path]:
    """Yield reasonably small text files inside a skill package."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        if path.stat().st_size > 1_000_000:
            continue
        if path.name == ".env" or path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def looks_like_placeholder(line: str) -> bool:
    """Return True for obvious placeholder examples."""
    lowered = line.lower()
    return any(
        marker in lowered
        for marker in ["example", "placeholder", "your_", "<token>", "<api", "replace_me"]
    )


def is_executable(path: Path) -> bool:
    """Return whether a file has any executable bit."""
    return bool(path.stat().st_mode & 0o111)


def add_issue(
    issues: List[Dict[str, Any]], severity: str, code: str, message: str
) -> None:
    """Append one lint issue."""
    issues.append({"severity": severity, "code": code, "message": message})


def has_errors(issues: List[Dict[str, Any]]) -> bool:
    """Return True when any lint issue is an error."""
    return any(issue["severity"] == "error" for issue in issues)


def count_severity(issues: List[Dict[str, Any]], severity: str) -> int:
    """Count issues by severity."""
    return sum(1 for issue in issues if issue["severity"] == severity)


def grade_score(score: int) -> str:
    """Convert a numeric score to a compact grade."""
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "needs-work"
    return "poor"


def build_score_summary(score: int, agent_usable: bool, issues: List[Dict[str, Any]]) -> str:
    """Build a one-line score summary."""
    if agent_usable:
        return f"Agent-usable skill package ({score}/100)"
    if has_errors(issues):
        return f"Not agent-usable until errors are fixed ({score}/100)"
    return f"Usable with reservations; improve warnings and routing metadata ({score}/100)"


def format_lint_result(result: Dict[str, Any]) -> str:
    """Render a human-readable lint result."""
    lines = [
        f"Skill: {result.get('name') or result['path']}",
        f"Score: {result['score']}/100 ({result['grade']})",
        f"Agent usable: {str(result['agent_usable']).lower()}",
    ]

    issues = result["issues"]
    if not issues:
        lines.append("Issues: none")
    else:
        lines.append(f"Issues: {len(issues)}")
        for issue in issues:
            lines.append(f"- [{issue['severity']}] {issue['code']}: {issue['message']}")

    return "\n".join(lines)


def dumps_result(data: Dict[str, Any]) -> str:
    """Render structured data as deterministic JSON."""
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
