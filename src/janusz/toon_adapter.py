#!/usr/bin/env python3
"""
YAML to TOON Converter for AI Agent Knowledge Bases

This module converts YAML files to TOON (Token-Oriented Object Notation) format
for efficient AI agent prompting and knowledge base storage.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class YAMLToTOONConverter:
    """Converts YAML files to TOON format for AI agent knowledge bases."""

    def __init__(self, yaml_path: str):
        self.yaml_path = Path(yaml_path)
        self.toon_path = self.yaml_path.with_suffix(".toon")
        self.json_temp_path = self.yaml_path.with_suffix(".temp.json")

    def yaml_to_json(self) -> bool:
        """Convert YAML to JSON intermediate format."""
        try:
            logger.info(f"Converting {self.yaml_path} to JSON")
            with open(self.yaml_path, encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            with open(self.json_temp_path, "w", encoding="utf-8") as f:
                json.dump(yaml_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error converting YAML to JSON: {e}")
            return False

    def json_to_toon(self) -> bool:
        """Convert JSON to TOON format using TOON CLI."""
        try:
            logger.info(f"Converting {self.json_temp_path} to TOON")

            # Run TOON CLI to encode JSON to TOON
            subprocess.run(
                ["toon", "--encode", str(self.json_temp_path), "-o", str(self.toon_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info("TOON conversion completed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"TOON CLI error: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("TOON CLI not found. Make sure it's installed globally.")
            return False

    def get_token_stats(self) -> Optional[Dict[str, Any]]:
        """Get token statistics comparison between JSON and TOON."""
        try:
            # Get stats for JSON
            json_result = subprocess.run(
                ["toon", "--stats", str(self.json_temp_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            # Get stats for TOON
            toon_result = subprocess.run(
                ["toon", "--stats", str(self.toon_path)], capture_output=True, text=True, check=True
            )

            return {
                "json_stats": json_result.stdout.strip(),
                "toon_stats": toon_result.stdout.strip(),
            }
        except Exception as e:
            logger.warning(f"Could not get token stats: {e}")
            return None

    def convert(self) -> bool:
        """Main conversion method."""
        try:
            # Step 1: YAML -> JSON
            if not self.yaml_to_json():
                return False

            # Step 2: JSON -> TOON
            if not self.json_to_toon():
                return False

            # Step 3: Get token statistics
            stats = self.get_token_stats()
            if stats:
                logger.info(f"Token stats - JSON: {stats['json_stats']}")
                logger.info(f"Token stats - TOON: {stats['toon_stats']}")

            # Step 4: Clean up temporary JSON file
            if self.json_temp_path.exists():
                self.json_temp_path.unlink()

            logger.info(f"Successfully converted {self.yaml_path} to {self.toon_path}")
            return True

        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            return False

    def validate_toon_file(self) -> bool:
        """Validate that the TOON file can be decoded back to JSON."""
        try:
            # Try to decode TOON back to JSON
            result = subprocess.run(
                ["toon", "--decode", str(self.toon_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the JSON to ensure it's valid
            decoded_data = json.loads(result.stdout)
            logger.info(
                f"TOON file validation successful - decoded {len(str(decoded_data))} characters"
            )
            return True

        except Exception as e:
            logger.error(f"TOON file validation failed: {e}")
            return False


def convert_directory(directory: str = "new", validate: bool = True) -> None:
    """Convert all YAML files in a directory to TOON format."""
    dir_path = Path(directory)
    dir_path.mkdir(exist_ok=True)  # Create directory if it doesn't exist

    yaml_files = list(dir_path.glob("**/*.yaml"))

    if not yaml_files:
        logger.info(f"No YAML files found in {directory}")
        return

    logger.info(f"Found {len(yaml_files)} YAML files")

    successful = 0
    failed = 0

    for yaml_file in yaml_files:
        logger.info(f"Processing: {yaml_file}")
        converter = YAMLToTOONConverter(str(yaml_file))

        if converter.convert():
            if validate and converter.validate_toon_file():
                logger.info(f"✓ Successfully converted and validated: {yaml_file.name}")
                successful += 1
            else:
                logger.info(f"✓ Successfully converted: {yaml_file.name}")
                successful += 1
        else:
            logger.error(f"✗ Failed to convert: {yaml_file.name}")
            failed += 1

    logger.info(f"Conversion completed: {successful} successful, {failed} failed")


def test_toon_conversion(yaml_file: str) -> None:
    """Test TOON conversion on a single file with detailed output."""
    logger.info(f"Testing TOON conversion on: {yaml_file}")

    converter = YAMLToTOONConverter(yaml_file)

    # Show original file size
    original_size = os.path.getsize(yaml_file)
    logger.info(f"Original YAML file size: {original_size} bytes")

    # Convert
    if converter.convert():
        # Show TOON file size
        if converter.toon_path.exists():
            toon_size = os.path.getsize(converter.toon_path)
            compression_ratio = (1 - toon_size / original_size) * 100
            logger.info(f"TOON file size: {toon_size} bytes")
            logger.info(f"Compression: {compression_ratio:.1f}%")

        # Validate
        if converter.validate_toon_file():
            logger.info("✓ TOON file validation successful")

            # Show first few lines of TOON file
            with open(converter.toon_path, encoding="utf-8") as f:
                lines = f.readlines()[:10]
                logger.info("First 10 lines of TOON file:")
                for i, line in enumerate(lines, 1):
                    logger.info(f"  {i:2d}: {line.rstrip()}")

        else:
            logger.error("✗ TOON file validation failed")
    else:
        logger.error("✗ Conversion failed")
