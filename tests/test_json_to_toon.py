"""
Tests for the JSONToTOONConverter class.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from janusz.json_to_toon import JSONToTOONConverter


class TestJSONToTOONConverter:
    """Test cases for JSONToTOONConverter."""

    def test_json_validation_valid(self):
        """Test validation of valid JSON."""
        test_data = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(test_data, tmp)
            tmp_path = tmp.name

        try:
            converter = JSONToTOONConverter(tmp_path)
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
            converter = JSONToTOONConverter(tmp_path)
            assert converter.validate_json() is False
        finally:
            Path(tmp_path).unlink()

    def test_json_validation_file_not_found(self):
        """Test validation when file doesn't exist."""
        converter = JSONToTOONConverter("nonexistent.json")
        assert converter.validate_json() is False

    @patch("janusz.json_to_toon.ensure_toon_available")
    @patch("subprocess.run")
    def test_json_to_toon_success(self, mock_run, mock_validate):
        """Test successful JSON to TOON conversion."""
        mock_validate.return_value = "/usr/bin/toon"
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            converter = JSONToTOONConverter(tmp_path)
            success = converter.json_to_toon()
            assert success

            # Verify subprocess was called correctly
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert "toon" in args[0]
            assert "--encode" in args[0]

        finally:
            Path(tmp_path).unlink()

    @patch("subprocess.run")
    def test_json_to_toon_cli_not_found(self, mock_run):
        """Test handling of missing TOON CLI."""
        mock_run.side_effect = FileNotFoundError("toon command not found")

        converter = JSONToTOONConverter("dummy.json")
        success = converter.json_to_toon()

        assert not success

    @patch("subprocess.run")
    def test_json_to_toon_cli_error(self, mock_run):
        """Test handling of TOON CLI errors."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "toon", stderr="Error: invalid format")

        converter = JSONToTOONConverter("dummy.json")
        success = converter.json_to_toon()

        assert not success

    @patch("subprocess.run")
    def test_get_token_stats(self, mock_run):
        """Test token statistics retrieval."""
        mock_json_result = MagicMock(stdout="JSON: 100 tokens", stderr="", returncode=0)
        mock_toon_result = MagicMock(stdout="TOON: 50 tokens", stderr="", returncode=0)

        mock_run.side_effects = [mock_json_result, mock_toon_result]

        converter = JSONToTOONConverter("dummy.json")
        stats = converter.get_token_stats()

        assert stats is not None
        assert "json_stats" in stats
        assert "toon_stats" in stats

    @patch("subprocess.run")
    def test_get_token_stats_error(self, mock_run):
        """Test token stats error handling."""
        mock_run.side_effect = Exception("Stats command failed")

        converter = JSONToTOONConverter("dummy.json")
        stats = converter.get_token_stats()

        assert stats is None

    @patch("subprocess.run")
    def test_validate_toon_file_success(self, mock_run):
        """Test successful TOON file validation."""
        mock_run.return_value = MagicMock(stdout='{"valid": "json"}', stderr="", returncode=0)

        converter = JSONToTOONConverter("dummy.json")
        success = converter.validate_toon_file()

        assert success

    @patch("subprocess.run")
    def test_validate_toon_file_invalid_json(self, mock_run):
        """Test TOON validation with invalid JSON output."""
        mock_run.return_value = MagicMock(stdout="invalid json", stderr="", returncode=0)

        converter = JSONToTOONConverter("dummy.json")
        success = converter.validate_toon_file()

        assert not success

    @patch("subprocess.run")
    def test_validate_toon_file_decode_error(self, mock_run):
        """Test TOON validation decode error."""
        mock_run.side_effect = Exception("Decode failed")

        converter = JSONToTOONConverter("dummy.json")
        success = converter.validate_toon_file()

        assert not success

    def test_full_conversion_pipeline(self):
        """Test the complete conversion pipeline."""
        test_data = {"metadata": {"title": "test"}, "content": {"sections": []}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(test_data, tmp)
            tmp_path = tmp.name

        try:
            converter = JSONToTOONConverter(tmp_path)

            # Mock the external TOON CLI calls
            with patch("janusz.json_to_toon.ensure_toon_available") as mock_validate, \
                 patch("subprocess.run") as mock_run:
                mock_validate.return_value = "/usr/bin/toon"
                mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

                converter.convert()

                # Should have made multiple subprocess calls (validation + encode + validate)
                assert mock_run.call_count >= 3

        finally:
            Path(tmp_path).unlink()
            if hasattr(converter, "toon_path") and converter.toon_path.exists():
                converter.toon_path.unlink()
