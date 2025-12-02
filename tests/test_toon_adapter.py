"""
Tests for the YAMLToTOONConverter class.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml
from janusz.toon_adapter import YAMLToTOONConverter


class TestYAMLToTOONConverter:
    """Test cases for YAMLToTOONConverter."""

    def test_yaml_to_json_conversion(self):
        """Test YAML to JSON conversion."""
        test_yaml = {"metadata": {"title": "test"}, "content": {"sections": []}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.dump(test_yaml, tmp)
            tmp_path = tmp.name

        try:
            converter = YAMLToTOONConverter(tmp_path)
            success = converter.yaml_to_json()

            assert success
            assert converter.json_temp_path.exists()

            # Verify JSON content
            with open(converter.json_temp_path) as f:
                json_data = json.load(f)

            assert json_data == test_yaml

        finally:
            Path(tmp_path).unlink()
            if converter.json_temp_path.exists():
                converter.json_temp_path.unlink()

    @patch("janusz.toon_adapter.ensure_toon_available")
    @patch("subprocess.run")
    def test_json_to_toon_success(self, mock_run, mock_validate):
        """Test successful JSON to TOON conversion."""
        mock_validate.return_value = "/usr/bin/toon"
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            converter = YAMLToTOONConverter("dummy.yaml")
            converter.json_temp_path = Path(tmp_path)

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

        converter = YAMLToTOONConverter("dummy.yaml")
        success = converter.json_to_toon()

        assert not success

    @patch("subprocess.run")
    def test_json_to_toon_cli_error(self, mock_run):
        """Test handling of TOON CLI errors."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "toon", stderr="Error: invalid format")

        converter = YAMLToTOONConverter("dummy.yaml")
        success = converter.json_to_toon()

        assert not success

    @patch("subprocess.run")
    def test_get_token_stats(self, mock_run):
        """Test token statistics retrieval."""
        mock_json_result = MagicMock(stdout="JSON: 100 tokens", stderr="", returncode=0)
        mock_toon_result = MagicMock(stdout="TOON: 50 tokens", stderr="", returncode=0)

        mock_run.side_effects = [mock_json_result, mock_toon_result]

        converter = YAMLToTOONConverter("dummy.yaml")
        stats = converter.get_token_stats()

        assert stats is not None
        assert "json_stats" in stats
        assert "toon_stats" in stats

    @patch("subprocess.run")
    def test_get_token_stats_error(self, mock_run):
        """Test token stats error handling."""
        mock_run.side_effect = Exception("Stats command failed")

        converter = YAMLToTOONConverter("dummy.yaml")
        stats = converter.get_token_stats()

        assert stats is None

    @patch("subprocess.run")
    def test_validate_toon_file_success(self, mock_run):
        """Test successful TOON file validation."""
        mock_run.return_value = MagicMock(stdout='{"valid": "json"}', stderr="", returncode=0)

        converter = YAMLToTOONConverter("dummy.yaml")
        success = converter.validate_toon_file()

        assert success

    @patch("subprocess.run")
    def test_validate_toon_file_invalid_json(self, mock_run):
        """Test TOON validation with invalid JSON output."""
        mock_run.return_value = MagicMock(stdout="invalid json", stderr="", returncode=0)

        converter = YAMLToTOONConverter("dummy.yaml")
        success = converter.validate_toon_file()

        assert not success

    @patch("subprocess.run")
    def test_validate_toon_file_decode_error(self, mock_run):
        """Test TOON validation decode error."""
        mock_run.side_effect = Exception("Decode failed")

        converter = YAMLToTOONConverter("dummy.yaml")
        success = converter.validate_toon_file()

        assert not success

    def test_full_conversion_pipeline(self):
        """Test the complete conversion pipeline."""
        test_yaml = {"metadata": {"title": "test"}, "content": {"sections": []}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            yaml.dump(test_yaml, tmp)
            tmp_path = tmp.name

        try:
            converter = YAMLToTOONConverter(tmp_path)

            # Mock the external TOON CLI calls
            with patch("janusz.toon_adapter.ensure_toon_available") as mock_validate, \
                 patch("subprocess.run") as mock_run:
                mock_validate.return_value = "/usr/bin/toon"
                mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

                converter.convert()

                # Should have made multiple subprocess calls (validation + encode + validate)
                assert mock_run.call_count >= 3

                # Temporary JSON file should be cleaned up
                assert not converter.json_temp_path.exists()

        finally:
            Path(tmp_path).unlink()
            if hasattr(converter, "toon_path") and converter.toon_path.exists():
                converter.toon_path.unlink()
