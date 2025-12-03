"""
Edge Case Tests for Janusz - Document-to-TOON Pipeline

Tests for edge cases and error conditions.
"""

import tempfile
from pathlib import Path

import pytest

from janusz.converter import UniversalToYAMLConverter


class TestEdgeCases:
    def test_empty_file_conversion(self):
        """Test conversion of empty files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("")  # Empty file
            tmp_path = tmp.name

        try:
            converter = UniversalToYAMLConverter(tmp_path)
            result = converter.convert_to_yaml()
            assert result is False  # Should fail gracefully
        finally:
            Path(tmp_path).unlink()

    def test_corrupted_file_handling(self):
        """Test handling of corrupted files."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as tmp:
            tmp.write(b"corrupted\x00\x01\x02data")  # Invalid PDF data
            tmp_path = tmp.name

        try:
            converter = UniversalToYAMLConverter(tmp_path)
            result = converter.convert_to_yaml()
            # Should either succeed with partial content or fail gracefully
            assert isinstance(result, bool)
        finally:
            Path(tmp_path).unlink()

    def test_unsupported_extension_error(self):
        """Test error handling for unsupported file extensions."""
        with tempfile.NamedTemporaryFile(suffix=".xyz") as tmp:
            with pytest.raises(ValueError, match="Unsupported file format"):
                UniversalToYAMLConverter(tmp.name)
