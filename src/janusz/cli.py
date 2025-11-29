#!/usr/bin/env python3
"""
Unified CLI for Janusz - Document-to-TOON Pipeline

Provides command-line interface for converting documents to YAML and YAML to TOON format.
"""

import argparse
import logging
import sys
from pathlib import Path

from .converter import UniversalToYAMLConverter, process_directory as convert_directory
from .toon_adapter import YAMLToTOONConverter, convert_directory as toon_convert_directory, test_toon_conversion
from .json_to_toon import JSONToTOONConverter, convert_directory as json_convert_directory, test_toon_conversion as test_json_toon_conversion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_file_to_yaml(file_path: str) -> bool:
    """Convert a single file to YAML format."""
    try:
        converter = UniversalToYAMLConverter(file_path)
        return converter.convert_to_yaml()
    except ValueError as e:
        logger.error(f"Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def convert_yaml_to_toon(yaml_path: str, validate: bool = True) -> bool:
    """Convert a single YAML file to TOON format."""
    try:
        converter = YAMLToTOONConverter(yaml_path)
        success = converter.convert()
        if success and validate:
            return converter.validate_toon_file()
        return success
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def convert_json_to_toon(json_path: str, validate: bool = True) -> bool:
    """Convert a single JSON file to TOON format."""
    try:
        converter = JSONToTOONConverter(json_path)
        success = converter.convert()
        if success and validate:
            return converter.validate_toon_file()
        return success
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all documents in current directory to YAML
  janusz convert

  # Convert specific file to YAML
  janusz convert --file document.pdf

  # Convert all YAML files to TOON
  janusz toon

  # Convert specific YAML to TOON
  janusz toon --file document.yaml

  # Test TOON conversion with detailed output
  janusz test document.yaml

Supported input formats for convert: PDF, MD, TXT, DOCX, HTML, RTF, EPUB
Supported input formats for toon: YAML
Supported input formats for json: JSON
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert documents to YAML')
    convert_parser.add_argument('--directory', '-d', default='.',
                               help='Directory to process (default: current directory)')
    convert_parser.add_argument('--file', '-f', help='Specific file to convert')

    # Toon command
    toon_parser = subparsers.add_parser('toon', help='Convert YAML files to TOON')
    toon_parser.add_argument('--directory', '-d', default='.',
                            help='Directory to process (default: current directory)')
    toon_parser.add_argument('--file', '-f', help='Specific YAML file to convert')
    toon_parser.add_argument('--no-validate', action='store_true',
                            help='Skip TOON file validation')

    # Json command
    json_parser = subparsers.add_parser('json', help='Convert JSON files to TOON')
    json_parser.add_argument('--directory', '-d', default='.',
                            help='Directory to process (default: current directory)')
    json_parser.add_argument('--file', '-f', help='Specific JSON file to convert')
    json_parser.add_argument('--no-validate', action='store_true',
                            help='Skip TOON file validation')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test TOON conversion with detailed output')
    test_parser.add_argument('file', help='YAML or JSON file to test')

    # Version
    parser.add_argument('--version', action='version', version='Janusz 1.0.0')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'convert':
        if args.file:
            success = convert_file_to_yaml(args.file)
            sys.exit(0 if success else 1)
        else:
            convert_directory(args.directory)

    elif args.command == 'toon':
        validate = not args.no_validate
        if args.file:
            success = convert_yaml_to_toon(args.file, validate=validate)
            sys.exit(0 if success else 1)
        else:
            toon_convert_directory(args.directory, validate=validate)

    elif args.command == 'json':
        validate = not args.no_validate
        if args.file:
            success = convert_json_to_toon(args.file, validate=validate)
            sys.exit(0 if success else 1)
        else:
            json_convert_directory(args.directory, validate=validate)

    elif args.command == 'test':
        # Try to detect file type and use appropriate test function
        file_path = Path(args.file)
        if file_path.suffix.lower() == '.json':
            test_json_toon_conversion(args.file)
        else:
            test_toon_conversion(args.file)

if __name__ == "__main__":
    main()
