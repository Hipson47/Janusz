#!/usr/bin/env python3
"""
Unified CLI for Janusz - Document-to-TOON Pipeline

Provides command-line interface for converting documents to YAML and YAML to TOON format.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from .converter import UniversalToYAMLConverter
from .converter import process_directory as convert_directory
from .schemas.schema_manager import SchemaManager
from .orchestrator.ai_orchestrator import AIOrchestrator
from .json_to_toon import JSONToTOONConverter, convert_directory_json_only, convert_json_only
from .json_to_toon import convert_directory as json_convert_directory
from .json_to_toon import test_toon_conversion as test_json_toon_conversion
from .toon_adapter import YAMLToTOONConverter, test_toon_conversion
from .toon_adapter import convert_directory as toon_convert_directory
from .toon_cli import ToonCliError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def convert_file_to_yaml(file_path: str, use_ai: bool = False, ai_model: str = "anthropic/claude-3-haiku") -> bool:
    """Convert a single file to YAML format."""
    try:
        converter = UniversalToYAMLConverter(file_path, use_ai=use_ai, ai_model=ai_model)
        return converter.convert_to_yaml()
    except ValueError as e:
        # Invalid file format or unsupported extension
        logger.error(f"Invalid file format: {e}")
        return False
    except PermissionError as e:
        # File permission issues
        logger.error(f"Permission denied accessing file '{file_path}': {e}")
        return False
    except OSError as e:
        # File system errors (file not found, disk full, etc.)
        logger.error(f"File system error processing '{file_path}': {e}")
        return False
    except Exception as e:
        # Unexpected errors - log with full traceback for debugging
        logger.error(f"Unexpected error converting '{file_path}': {e}", exc_info=True)
        return False


def convert_yaml_to_toon(yaml_path: str, validate: bool = True) -> bool:
    """Convert a single YAML file to TOON format."""
    try:
        converter = YAMLToTOONConverter(yaml_path)
        success = converter.convert()
        if success and validate:
            return converter.validate_toon_file()
        return success
    except ToonCliError as e:
        # TOON CLI validation or execution errors
        logger.error(f"TOON CLI error for YAML '{yaml_path}': {e}")
        return False
    except subprocess.TimeoutExpired as e:
        # TOON CLI timeout errors
        logger.error(f"TOON CLI timeout for YAML '{yaml_path}': {e}")
        return False
    except ValueError as e:
        # Invalid YAML file or path issues
        logger.error(f"Invalid YAML file '{yaml_path}': {e}")
        return False
    except PermissionError as e:
        # File permission issues
        logger.error(f"Permission denied accessing YAML file '{yaml_path}': {e}")
        return False
    except OSError as e:
        # File system errors
        logger.error(f"File system error processing YAML '{yaml_path}': {e}")
        return False
    except Exception as e:
        # Unexpected errors - log with full traceback for debugging
        logger.error(f"Unexpected error converting YAML '{yaml_path}': {e}", exc_info=True)
        return False


def convert_json_to_toon(json_path: str, validate: bool = True) -> bool:
    """Convert a single JSON file to TOON format."""
    try:
        converter = JSONToTOONConverter(json_path)
        success = converter.convert()
        if success and validate:
            return converter.validate_toon_file()
        return success
    except ToonCliError as e:
        # TOON CLI validation or execution errors
        logger.error(f"TOON CLI error for JSON '{json_path}': {e}")
        return False
    except subprocess.TimeoutExpired as e:
        # TOON CLI timeout errors
        logger.error(f"TOON CLI timeout for JSON '{json_path}': {e}")
        return False
    except ValueError as e:
        # Invalid JSON file or path issues
        logger.error(f"Invalid JSON file '{json_path}': {e}")
        return False
    except PermissionError as e:
        # File permission issues
        logger.error(f"Permission denied accessing JSON file '{json_path}': {e}")
        return False
    except OSError as e:
        # File system errors
        logger.error(f"File system error processing JSON '{json_path}': {e}")
        return False
    except Exception as e:
        # Unexpected errors - log with full traceback for debugging
        logger.error(f"Unexpected error converting JSON '{json_path}': {e}", exc_info=True)
        return False


def convert_file_to_json(json_path: str) -> bool:
    """Validate a single JSON file (no TOON conversion)."""
    try:
        return convert_json_only(json_path)
    except ValueError as e:
        # Invalid JSON file or parsing errors
        logger.error(f"Invalid JSON file '{json_path}': {e}")
        return False
    except PermissionError as e:
        # File permission issues
        logger.error(f"Permission denied accessing JSON file '{json_path}': {e}")
        return False
    except OSError as e:
        # File system errors
        logger.error(f"File system error processing JSON '{json_path}': {e}")
        return False
    except Exception as e:
        # Unexpected errors - log with full traceback for debugging
        logger.error(f"Unexpected error validating JSON '{json_path}': {e}", exc_info=True)
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all documents in 'new' directory to YAML (default behavior)
  janusz convert

  # Convert specific file to YAML
  janusz convert --file document.pdf

  # Convert all YAML files in 'new' directory to TOON (default behavior)
  janusz toon

  # Convert specific YAML to TOON
  janusz toon --file document.yaml

  # Test TOON conversion with detailed output
  janusz test document.yaml

Supported input formats for convert: PDF, MD, TXT, DOCX, HTML
Supported input formats for toon: YAML
Supported input formats for json: JSON
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert documents to YAML")
    convert_parser.add_argument(
        "--directory", "-d", default="new", help="Directory to process (default: new)"
    )
    convert_parser.add_argument("--file", "-f", help="Specific file to convert")
    convert_parser.add_argument(
        "--use-ai", action="store_true",
        help="Enable AI-powered analysis (requires JANUSZ_OPENROUTER_API_KEY)"
    )
    convert_parser.add_argument(
        "--ai-model", default="anthropic/claude-3-haiku",
        help="AI model to use for analysis (default: anthropic/claude-3-haiku)"
    )

    # Toon command
    toon_parser = subparsers.add_parser("toon", help="Convert YAML files to TOON")
    toon_parser.add_argument(
        "--directory", "-d", default="new", help="Directory to process (default: new)"
    )
    toon_parser.add_argument("--file", "-f", help="Specific YAML file to convert")
    toon_parser.add_argument("--no-validate", action="store_true", help="Skip TOON file validation")

    # Json command
    json_parser = subparsers.add_parser("json", help="Convert JSON files to TOON or validate JSON files")
    json_parser.add_argument(
        "--directory", "-d", default="new", help="Directory to process (default: new)"
    )
    json_parser.add_argument("--file", "-f", help="Specific JSON file to convert")
    json_parser.add_argument("--no-validate", action="store_true", help="Skip TOON file validation")
    json_parser.add_argument("--no-toon", action="store_true", help="Only validate JSON files, don't convert to TOON")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch the graphical user interface")

    # Schema commands
    schema_parser = subparsers.add_parser("schema", help="Manage modular schemas")
    schema_subparsers = schema_parser.add_subparsers(dest="schema_command", help="Schema operations")

    # Schema list
    schema_list_parser = schema_subparsers.add_parser("list", help="List available schemas")
    schema_list_parser.add_argument("--category", help="Filter by category")
    schema_list_parser.add_argument("--tag", action="append", help="Filter by tags")

    # Schema create
    schema_create_parser = schema_subparsers.add_parser("create", help="Create schema from document")
    schema_create_parser.add_argument("file", help="Source document file")
    schema_create_parser.add_argument("--name", required=True, help="Schema name")
    schema_create_parser.add_argument("--description", required=True, help="Schema description")
    schema_create_parser.add_argument("--category", default="technical",
                                    choices=["technical", "business", "educational", "process", "reference", "tutorial"],
                                    help="Schema category")

    # Schema generate AI
    schema_ai_parser = schema_subparsers.add_parser("generate-ai", help="Generate schema using AI")
    schema_ai_parser.add_argument("--prompt", required=True, help="Natural language prompt")
    schema_ai_parser.add_argument("--category", default="technical",
                                choices=["technical", "business", "educational", "process", "reference", "tutorial"],
                                help="Schema category")

    # Orchestrator command
    orchestrator_parser = subparsers.add_parser("orchestrate", help="Use AI orchestrator for intelligent processing")
    orchestrator_parser.add_argument("request", help="Natural language processing request")
    orchestrator_parser.add_argument("--file", help="Document file to analyze")
    orchestrator_parser.add_argument("--use-ai", action="store_true", help="Enable AI analysis")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test TOON conversion with detailed output")
    test_parser.add_argument("file", help="YAML or JSON file to test")

    # Version
    parser.add_argument("--version", action="version", version="Janusz 1.0.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "convert":
        if args.file:
            success = convert_file_to_yaml(args.file, use_ai=getattr(args, 'use_ai', False), ai_model=getattr(args, 'ai_model', 'anthropic/claude-3-haiku'))
            sys.exit(0 if success else 1)
        else:
            convert_directory(args.directory, use_ai=getattr(args, 'use_ai', False), ai_model=getattr(args, 'ai_model', 'anthropic/claude-3-haiku'))

    elif args.command == "toon":
        validate = not args.no_validate
        if args.file:
            success = convert_yaml_to_toon(args.file, validate=validate)
            sys.exit(0 if success else 1)
        else:
            toon_convert_directory(args.directory, validate=validate)

    elif args.command == "json":
        if hasattr(args, 'no_toon') and args.no_toon:
            # Only validate JSON files, don't convert to TOON
            if args.file:
                success = convert_file_to_json(args.file)
                sys.exit(0 if success else 1)
            else:
                convert_directory_json_only(args.directory)
        else:
            # Convert JSON to TOON
            validate = not args.no_validate
            if args.file:
                success = convert_json_to_toon(args.file, validate=validate)
                sys.exit(0 if success else 1)
            else:
                json_convert_directory(args.directory, validate=validate)

    elif args.command == "gui":
        try:
            from .gui.main_app import main as gui_main
            gui_main()
        except ImportError as e:
            logger.error(f"GUI components not available: {e}")
            logger.error("Make sure tkinter is installed: pip install tk")
            sys.exit(1)

    elif args.command == "schema":
        schema_manager = SchemaManager()

        if args.schema_command == "list":
            schemas = schema_manager.list_schemas(
                category=getattr(args, 'category', None),
                tags=getattr(args, 'tag', None)
            )

            if not schemas:
                print("No schemas found.")
            else:
                print(f"Found {len(schemas)} schemas:")
                for schema in schemas:
                    print(f"  • {schema.id}: {schema.name}")
                    print(f"    Category: {schema.category}")
                    print(f"    Usage: {schema.usage_count} times")
                    print(f"    Tags: {', '.join(schema.tags)}")
                    print()

        elif args.schema_command == "create":
            # Convert file to document structure first
            converter = UniversalToYAMLConverter(args.file)
            doc_structure = converter.parse_text_structure(converter.extract_text_from_file())

            schema = schema_manager.create_schema_from_document(
                doc_structure,
                args.name,
                args.description,
                args.category
            )

            print(f"✅ Created schema: {schema.name} ({schema.id})")

        elif args.schema_command == "generate-ai":
            # Check if AI is available
            try:
                from janusz.ai.ai_content_analyzer import AIContentAnalyzer
                ai_analyzer = AIContentAnalyzer()
                schema = schema_manager.generate_ai_schema(args.prompt, args.category)
                print(f"🤖 Generated AI schema: {schema.name} ({schema.id})")
            except Exception as e:
                logger.error(f"AI schema generation failed: {e}")
                logger.error("Make sure JANUSZ_OPENROUTER_API_KEY is set")
                sys.exit(1)

    elif args.command == "orchestrate":
        try:
            from janusz.ai.ai_content_analyzer import AIContentAnalyzer
            ai_analyzer = AIContentAnalyzer() if getattr(args, 'use_ai', False) else None
        except Exception:
            ai_analyzer = None
            if getattr(args, 'use_ai', False):
                logger.warning("AI requested but not available")

        orchestrator = AIOrchestrator(ai_analyzer=ai_analyzer)

        # Load document if provided
        document = None
        if getattr(args, 'file', None):
            converter = UniversalToYAMLConverter(args.file)
            document = converter.parse_text_structure(converter.extract_text_from_file())

        response = orchestrator.process_document_request(args.request, document)

        print("🎯 Orchestrator Response:")
        print(f"Recommended schemas: {', '.join(response.recommended_schemas) or 'None'}")
        print(f"Confidence: {response.confidence_score:.1%}")
        print(f"Reasoning: {response.reasoning}")

        if response.alternative_options:
            print("\nAlternatives:")
            for alt in response.alternative_options:
                print(f"  • {alt.get('reason', alt)}")

        if response.processing_plan:
            print("\nProcessing plan:")
            for key, value in response.processing_plan.items():
                print(f"  • {key}: {value}")

        if response.estimated_time:
            print(f"\nEstimated time: {response.estimated_time} seconds")

    elif args.command == "test":
        # Try to detect file type and use appropriate test function
        file_path = Path(args.file)
        if file_path.suffix.lower() == ".json":
            test_json_toon_conversion(args.file)
        else:
            test_toon_conversion(args.file)


if __name__ == "__main__":
    main()
