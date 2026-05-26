"""
Tests for Codex skill package generation.
"""

import json

from janusz.skill_packager import create_skill_package, slugify


def test_slugify_creates_skill_name():
    """Skill names should be lowercase and filesystem-safe."""
    assert slugify("API Documentation Guide!") == "api-documentation-guide"


def test_create_skill_package_from_json(temp_dir):
    """Create a minimal skill folder from a JSON package."""
    source = temp_dir / "api.json"
    source.write_text(
        json.dumps(
            {
                "metadata": {
                    "title": "API Documentation",
                    "source": "api.md",
                    "source_type": "markdown",
                },
                "content": {
                    "sections": [
                        {
                            "title": "Overview",
                            "content": ["Use explicit endpoint contracts."],
                        }
                    ],
                    "raw_text": "Use explicit endpoint contracts.",
                },
                "analysis": {
                    "keywords": [{"text": "API", "confidence_level": "high"}],
                    "best_practices": [
                        {
                            "text": "Document request and response examples.",
                            "confidence_level": "high",
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )

    skill_dir = create_skill_package(str(source), output_dir=str(temp_dir / "skills"))

    skill_md = skill_dir / "SKILL.md"
    reference = skill_dir / "references" / "source.json"

    assert skill_md.exists()
    assert reference.exists()
    assert "name: api-documentation" in skill_md.read_text(encoding="utf-8")
    assert (
        json.loads(reference.read_text(encoding="utf-8"))["metadata"]["title"]
        == "API Documentation"
    )
