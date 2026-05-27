"""
Tests for JSON package conversion.
"""

import json
import logging
import tempfile
from pathlib import Path

import pytest
import yaml

from janusz.json_packager import (
    JSONPackageConverter,
    convert_directory,
    inspect_json_package,
    load_json_file,
    load_structured_package,
    load_yaml_file,
    validate_json_file,
    write_json_package,
)


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


def test_write_json_package_creates_parent_and_preserves_unicode(tmp_path):
    """Writing JSON packages should create parents and emit deterministic JSON."""
    data = {"title": "Zażółć", "items": [1, 2]}
    output_path = tmp_path / "nested" / "package.json"

    written = write_json_package(data, output_path)

    assert written == output_path
    text = output_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '"title": "Zażółć"' in text
    assert json.loads(text) == data


def test_load_json_and_yaml_require_object_roots(tmp_path):
    """Structured package loaders should reject non-object roots."""
    json_path = tmp_path / "list.json"
    json_path.write_text("[1, 2, 3]", encoding="utf-8")
    yaml_path = tmp_path / "list.yaml"
    yaml_path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(TypeError, match="object"):
        load_json_file(json_path)
    with pytest.raises(TypeError, match="object"):
        load_yaml_file(yaml_path)


def test_load_structured_package_uses_case_insensitive_suffixes(tmp_path):
    """Structured loading should dispatch JSON/YAML by suffix without data loss."""
    json_path = tmp_path / "PACKAGE.JSON"
    json_path.write_text('{"metadata": {"title": "JSON"}}', encoding="utf-8")
    yaml_path = tmp_path / "PACKAGE.YML"
    yaml_path.write_text("metadata:\n  title: YAML\n", encoding="utf-8")

    assert load_structured_package(json_path) == {"metadata": {"title": "JSON"}}
    assert load_structured_package(yaml_path) == {"metadata": {"title": "YAML"}}


def test_validate_json_file_reports_validity(tmp_path):
    """The public validate helper should return booleans for valid and invalid JSON."""
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text('{"ok": true}', encoding="utf-8")
    invalid_path.write_text('{"ok": }', encoding="utf-8")

    assert validate_json_file(str(valid_path)) is True
    assert validate_json_file(str(invalid_path)) is False


def test_convert_directory_uses_default_new_directory(monkeypatch, tmp_path):
    """Calling convert_directory() without arguments should process ./new."""
    monkeypatch.chdir(tmp_path)
    source_dir = tmp_path / "new"
    source_dir.mkdir()
    (source_dir / "package.yaml").write_text("metadata:\n  title: Default\n", encoding="utf-8")

    convert_directory()

    assert load_json_file(source_dir / "package.json") == {"metadata": {"title": "Default"}}


def test_convert_directory_processes_supported_files_only(monkeypatch, tmp_path, caplog):
    """Directory conversion should skip JSON outputs and report success/failure counts."""
    calls: list[tuple[str, bool, str]] = []

    def fake_convert_file(input_path: str, *, use_ai: bool, ai_model: str) -> bool:
        source = Path(input_path)
        calls.append((source.name, use_ai, ai_model))
        return source.name == "ok.yaml"

    monkeypatch.setattr("janusz.json_packager.convert_file", fake_convert_file)
    (tmp_path / "ok.yaml").write_text("metadata:\n  title: OK\n", encoding="utf-8")
    (tmp_path / "fail.md").write_text("# broken", encoding="utf-8")
    (tmp_path / "existing.json").write_text("{}", encoding="utf-8")

    with caplog.at_level(logging.INFO, logger="janusz.json_packager"):
        convert_directory(str(tmp_path), use_ai=True, ai_model="test/model")

    assert sorted(calls) == [
        ("fail.md", True, "test/model"),
        ("ok.yaml", True, "test/model"),
    ]
    assert "JSON packaging completed: 1 successful, 1 failed" in caplog.text


def test_inspect_json_package_logs_summary(tmp_path, caplog):
    """Package inspection should summarize metadata, content, and analysis."""
    package_path = tmp_path / "inspectable.json"
    write_json_package(
        {
            "metadata": {"title": "Inspectable", "source_type": "markdown"},
            "content": {"sections": [{"title": "One"}, {"title": "Two"}]},
            "analysis": {"keywords": ["agent"], "best_practices": ["test"]},
        },
        package_path,
    )

    with caplog.at_level(logging.INFO, logger="janusz.json_packager"):
        assert inspect_json_package(str(package_path)) is True

    assert "Package title: Inspectable" in caplog.text
    assert "Source type: markdown" in caplog.text
    assert "Sections: 2" in caplog.text
    assert "Keywords: 1" in caplog.text
    assert "Best practices: 1" in caplog.text


def test_inspect_json_package_reports_invalid_package(tmp_path, caplog):
    """Package inspection should fail clearly for malformed package roots."""
    package_path = tmp_path / "invalid.json"
    package_path.write_text("[]", encoding="utf-8")

    with caplog.at_level(logging.ERROR, logger="janusz.json_packager"):
        assert inspect_json_package(str(package_path)) is False

    assert "Package inspection failed" in caplog.text
