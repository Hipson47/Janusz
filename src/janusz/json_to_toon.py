#!/usr/bin/env python3
"""
JSON to TOON Converter for AI Agent Knowledge Bases

This module converts JSON files directly to TOON (Token-Oriented Object Notation) format
for efficient AI agent prompting and knowledge base storage.
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONToTOONConverter:
    """Converts JSON files to TOON format for AI agent knowledge bases."""

    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.toon_path = self.json_path.with_suffix('.toon')

    def validate_json(self) -> bool:
        """Validate that the JSON file is well-formed."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.json_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error reading JSON file {self.json_path}: {e}")
            return False

    def json_to_toon(self) -> bool:
        """Convert JSON to TOON format using TOON CLI."""
        try:
            logger.info(f"Converting {self.json_path} to TOON")

            # Run TOON CLI to encode JSON to TOON
            result = subprocess.run(
                ['toon', '--encode', str(self.json_path), '-o', str(self.toon_path)],
                capture_output=True,
                text=True,
                check=True
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
                ['toon', '--stats', str(self.json_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Get stats for TOON
            toon_result = subprocess.run(
                ['toon', '--stats', str(self.toon_path)],
                capture_output=True,
                text=True,
                check=True
            )

            return {
                'json_stats': json_result.stdout.strip(),
                'toon_stats': toon_result.stdout.strip()
            }
        except Exception as e:
            logger.warning(f"Could not get token stats: {e}")
            return None

    def convert(self) -> bool:
        """Main conversion method."""
        try:
            # Step 1: Validate JSON
            if not self.validate_json():
                return False

            # Step 2: JSON -> TOON
            if not self.json_to_toon():
                return False

            # Step 3: Get token statistics
            stats = self.get_token_stats()
            if stats:
                logger.info(f"Token stats - JSON: {stats['json_stats']}")
                logger.info(f"Token stats - TOON: {stats['toon_stats']}")

            logger.info(f"Successfully converted {self.json_path} to {self.toon_path}")
            return True

        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            return False

    def validate_toon_file(self) -> bool:
        """Validate that the TOON file can be decoded back to JSON."""
        try:
            # Try to decode TOON back to JSON
            result = subprocess.run(
                ['toon', '--decode', str(self.toon_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the JSON to ensure it's valid
            decoded_data = json.loads(result.stdout)
            logger.info(f"TOON file validation successful - decoded {len(str(decoded_data))} characters")
            return True

        except Exception as e:
            logger.error(f"TOON file validation failed: {e}")
            return False

def convert_directory(directory: str = ".", validate: bool = True) -> None:
    """Convert all JSON files in a directory to TOON format."""
    json_files = list(Path(directory).glob("**/*.json"))

    if not json_files:
        logger.info(f"No JSON files found in {directory}")
        return

    logger.info(f"Found {len(json_files)} JSON files")

    successful = 0
    failed = 0

    for json_file in json_files:
        logger.info(f"Processing: {json_file}")
        converter = JSONToTOONConverter(json_file)

        if converter.convert():
            if validate and converter.validate_toon_file():
                logger.info(f"✓ Successfully converted and validated: {json_file.name}")
                successful += 1
            else:
                logger.info(f"✓ Successfully converted: {json_file.name}")
                successful += 1
        else:
            logger.error(f"✗ Failed to convert: {json_file.name}")
            failed += 1

    logger.info(f"Conversion completed: {successful} successful, {failed} failed")

def test_toon_conversion(json_file: str) -> None:
    """Test TOON conversion on a single JSON file with detailed output."""
    logger.info(f"Testing TOON conversion on: {json_file}")

    converter = JSONToTOONConverter(json_file)

    # Show original file size
    original_size = Path(json_file).stat().st_size
    logger.info(f"Original JSON file size: {original_size} bytes")

    # Convert
    if converter.convert():
        # Show TOON file size
        if converter.toon_path.exists():
            toon_size = converter.toon_path.stat().st_size
            compression_ratio = (1 - toon_size / original_size) * 100
            logger.info(f"TOON file size: {toon_size} bytes")
            logger.info(f"Compression: {compression_ratio:.1f}%")

        # Validate
        if converter.validate_toon_file():
            logger.info("✓ TOON file validation successful")

            # Show first few lines of TOON file
            with open(converter.toon_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]
                logger.info("First 10 lines of TOON file:")
                for i, line in enumerate(lines, 1):
                    logger.info(f"  {i:2d}: {line.rstrip()}")

        else:
            logger.error("✗ TOON file validation failed")
    else:
        logger.error("✗ Conversion failed")
