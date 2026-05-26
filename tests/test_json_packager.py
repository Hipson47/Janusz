"""
Tests for JSON package conversion.
"""

import json
import tempfile
from pathlib import Path

import yaml

from janusz.json_packager import JSONPackageConverter, load_structured_package


class TestJSONPackageConverter:
    """Test cases for JSONPackageConverter."""

    def test_json_validation_valid(self):
        """Test validation of valid JSON."""
        test_data = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(test_data, tmp)
            tmp_path = tmp.name

        try:
            converter = JSONPackageConverter(tmp_path)
            assert converter.validate_json() is True
        finally:
            Path(tmp_path).unlink()

    def test_json_validation_invalid(self):
        """Test validation of invalid JSON."""
        invalid_json = '{"key": "value", "missing": }'

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp.write(invalid_json)
            tmp_path = tmp.name

        try:
            converter = JSONPackageConverter(tmp_path)
            assert converter.validate_json() is False
        finally:
            Path(tmp_path).unlink()

    def test_yaml_to_json_package(self):
        """Test YAML to JSON package conversion."""
        test_yaml = {"metadata": {"title": "test"}, "content": {"sections": []}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.dump(test_yaml, tmp)
            tmp_path = Path(tmp.name)

        output_path = tmp_path.with_suffix(".json")

        try:
            converter = JSONPackageConverter(str(tmp_path))
            success = converter.convert()

            assert success
            assert output_path.exists()
            assert load_structured_package(output_path) == test_yaml
        finally:
            tmp_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)

    def test_document_to_json_package(self):
        """Test direct source document packaging."""
        content = "# Test Document\n\nBest Practice: Keep checks reproducible.\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        output_path = tmp_path.with_suffix(".json")

        try:
            converter = JSONPackageConverter(str(tmp_path))
            success = converter.convert()

            assert success
            data = load_structured_package(output_path)
            assert data["metadata"]["title"] == tmp_path.stem
            assert data["metadata"]["source_type"] == "markdown"
            assert data["content"]["raw_text"] == content
        finally:
            tmp_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)
