"""
Tests for the UniversalToYAMLConverter class.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from janusz.converter import UniversalToYAMLConverter


class TestUniversalToYAMLConverter:
    """Test cases for UniversalToYAMLConverter."""

    def test_supported_extensions(self):
        """Test that supported extensions are properly defined."""
        expected_extensions = {".pdf", ".md", ".txt", ".docx", ".html", ".rtf", ".epub"}
        assert UniversalToYAMLConverter.SUPPORTED_EXTENSIONS == expected_extensions

    def test_detect_file_type(self):
        """Test file type detection based on extension."""
        test_cases = [
            ("document.pdf", "pdf"),
            ("readme.md", "markdown"),
            ("notes.txt", "text"),
            ("report.docx", "docx"),
            ("page.html", "html"),
            ("unknown.xyz", "unknown"),
        ]

        for filename, expected_type in test_cases:
            converter = UniversalToYAMLConverter.__new__(UniversalToYAMLConverter)
            converter.extension = Path(filename).suffix.lower()
            assert converter.detect_file_type() == expected_type

    def test_unsupported_extension_raises_error(self):
        """Test that unsupported file extensions raise ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".xyz") as tmp:
            with pytest.raises(ValueError, match="Unsupported file format"):
                UniversalToYAMLConverter(tmp.name)

    def test_extract_text_from_txt(self):
        """Test text extraction from plain text files."""
        test_content = "This is a test document.\nWith multiple lines."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name

        try:
            converter = UniversalToYAMLConverter(tmp_path)
            extracted = converter.extract_text_from_txt()
            assert extracted == test_content
        finally:
            Path(tmp_path).unlink()

    def test_extract_text_from_markdown(self):
        """Test text extraction from Markdown files."""
        test_content = "# Header\n\nThis is **bold** text."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name

        try:
            converter = UniversalToYAMLConverter(tmp_path)
            extracted = converter.extract_text_from_markdown()
            assert extracted == test_content
        finally:
            Path(tmp_path).unlink()

    def test_parse_text_structure(self):
        """Test text structure parsing."""
        test_text = """# Introduction

This is the introduction section.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

        converter = UniversalToYAMLConverter.__new__(UniversalToYAMLConverter)
        converter.filename = "test"
        converter.file_path = Path("test.txt")
        converter.detect_file_type = lambda: "text"

        structure = converter.parse_text_structure(test_text)

        assert structure["metadata"]["title"] == "test"
        assert structure["metadata"]["source_type"] == "text"
        assert structure["content"]["raw_text"] == test_text
        assert len(structure["content"]["sections"]) > 0

    def test_extract_key_concepts(self):
        """Test key concepts extraction."""
        test_text = """This document discusses Machine Learning and Artificial Intelligence.
Best Practice: Always validate your data.
Example: Use cross-validation for model evaluation.
"""

        converter = UniversalToYAMLConverter.__new__(UniversalToYAMLConverter)
        concepts = converter.extract_key_concepts(test_text)

        assert "keywords" in concepts
        assert "best_practices" in concepts
        assert "examples" in concepts
        assert len(concepts["keywords"]) > 0
        assert len(concepts["best_practices"]) > 0
        assert len(concepts["examples"]) > 0

    def test_yaml_conversion_integration(self):
        """Test full YAML conversion pipeline."""
        test_content = """# Test Document

This is a test document for conversion.

Best Practice: Test your code thoroughly.
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name

        try:
            converter = UniversalToYAMLConverter(tmp_path)
            success = converter.convert_to_yaml()

            assert success
            assert converter.yaml_path.exists()

            # Verify YAML content
            with open(converter.yaml_path) as f:
                yaml_data = yaml.safe_load(f)

            assert "metadata" in yaml_data
            assert "content" in yaml_data
            assert "analysis" in yaml_data
            assert yaml_data["metadata"]["title"] == Path(tmp_path).stem

        finally:
            Path(tmp_path).unlink()
            if converter.yaml_path.exists():
                converter.yaml_path.unlink()
