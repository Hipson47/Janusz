#!/usr/bin/env python3
"""Check Janusz release version metadata and optional tag consistency."""

import argparse
import re
import sys
from pathlib import Path


def read_project_version(pyproject_path: Path) -> str:
    """Read the project version from pyproject.toml without extra dependencies."""
    match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        pyproject_path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError("Could not find project.version in pyproject.toml")
    return match.group(1)


def normalize_tag(tag: str) -> str:
    """Convert vX.Y.Z tags to X.Y.Z."""
    return tag[1:] if tag.startswith("v") else tag


def main() -> int:
    """Run the version check."""
    parser = argparse.ArgumentParser(description="Check Janusz release version metadata.")
    parser.add_argument("--tag", help="Optional release tag, for example v1.0.0.")
    args = parser.parse_args()

    version = read_project_version(Path("pyproject.toml"))
    print(f"pyproject version: {version}")

    if args.tag:
        tag_version = normalize_tag(args.tag)
        if tag_version != version:
            print(f"Version mismatch: tag {args.tag!r} does not match {version!r}", file=sys.stderr)
            return 1
        print(f"tag version matches: {args.tag}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
