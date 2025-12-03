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
from .json_to_toon import (
    JSONToTOONConverter,
    convert_directory_json_only,
    convert_json_only,
)
from .json_to_toon import (
    convert_directory as json_convert_directory,
)
from .json_to_toon import (
    test_toon_conversion as test_json_toon_conversion,
)
from .orchestrator.ai_orchestrator import AIOrchestrator
from .prompts import PromptLibrary, PromptOptimizer, PromptTester
from .rag.rag_system import RAGSystem
from .schemas.schema_manager import SchemaManager
from .toon_adapter import (
    YAMLToTOONConverter,
    test_toon_conversion,
)
from .toon_adapter import (
    convert_directory as toon_convert_directory,
)
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
    subparsers.add_parser("gui", help="Launch the graphical user interface")

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

    # RAG commands
    rag_parser = subparsers.add_parser("rag", help="RAG (Retrieval-Augmented Generation) operations")
    rag_subparsers = rag_parser.add_subparsers(dest="rag_command", help="RAG operations")

    # RAG index
    rag_index_parser = rag_subparsers.add_parser("index", help="Index documents for RAG")
    rag_index_parser.add_argument("--directory", "-d", default="new", help="Directory to index")
    rag_index_parser.add_argument("--file", "-f", help="Specific file to index")

    # RAG query
    rag_query_parser = rag_subparsers.add_parser("query", help="Query the RAG system")
    rag_query_parser.add_argument("question", help="Question to ask")
    rag_query_parser.add_argument("--max-results", "-n", type=int, default=5, help="Maximum results")

    # RAG stats
    rag_subparsers.add_parser("stats", help="Show RAG system statistics")

    # RAG clear
    rag_subparsers.add_parser("clear", help="Clear RAG index")

    # Prompt commands
    prompt_parser = subparsers.add_parser("prompt", help="Prompt optimization and management tools")
    prompt_subparsers = prompt_parser.add_subparsers(dest="prompt_command", help="Prompt operations")

    # Prompt optimize
    optimize_parser = prompt_subparsers.add_parser("optimize", help="Optimize a prompt for better performance")
    optimize_parser.add_argument("text", help="Prompt text to optimize")
    optimize_parser.add_argument("--goal", "-g", choices=["clarity", "efficiency", "specificity", "creativity", "conciseness", "comprehensiveness"],
                               default="clarity", help="Optimization goal")
    optimize_parser.add_argument("--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use")
    optimize_parser.add_argument("--output", "-o", help="Save optimized prompt to file")

    # Prompt test
    test_parser = prompt_subparsers.add_parser("test", help="Test prompt performance against test cases")
    test_parser.add_argument("prompt", help="Prompt to test")
    test_parser.add_argument("--test-cases", "-t", required=True, help="JSON file with test cases")
    test_parser.add_argument("--output", "-o", help="Save test results to file")
    test_parser.add_argument("--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use")

    # Prompt benchmark
    benchmark_parser = prompt_subparsers.add_parser("benchmark", help="Benchmark multiple prompts")
    benchmark_parser.add_argument("--prompts", "-p", required=True, help="JSON file with prompts to benchmark")
    benchmark_parser.add_argument("--test-cases", "-t", required=True, help="JSON file with test cases")
    benchmark_parser.add_argument("--output", "-o", help="Save benchmark results to file")
    benchmark_parser.add_argument("--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use")

    # Prompt library commands
    library_parser = prompt_subparsers.add_parser("library", help="Manage prompt library")
    library_subparsers = library_parser.add_subparsers(dest="library_command", help="Library operations")

    # Library list
    library_subparsers.add_parser("list", help="List available prompt templates")

    # Library search
    search_parser = library_subparsers.add_parser("search", help="Search prompt templates")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum results")

    # Library export
    export_parser = library_subparsers.add_parser("export", help="Export prompt library")
    export_parser.add_argument("output", help="Output file path")

    # Library import
    import_parser = library_subparsers.add_parser("import", help="Import prompt library")
    import_parser.add_argument("input", help="Input file path")
    import_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing templates")

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

    elif args.command == "rag":
        try:
            rag_system = RAGSystem()
        except Exception as e:
            logger.error(f"RAG system initialization failed: {e}")
            sys.exit(1)

        if args.rag_command == "index":
            if args.file:
                # Index single file
                try:
                    converter = UniversalToYAMLConverter(args.file)
                    doc_structure = converter.parse_text_structure(converter.extract_text_from_file())
                    doc_id = rag_system.add_document(doc_structure)
                    print(f"✅ Indexed document: {args.file} (ID: {doc_id})")
                except Exception as e:
                    logger.error(f"Failed to index {args.file}: {e}")
                    sys.exit(1)
            else:
                # Index directory (simplified version)
                print("Directory indexing not yet implemented. Use individual files.")

        elif args.rag_command == "query":
            response = rag_system.query(args.question, max_results=args.max_results)
            print(f"🤖 Answer: {response.answer}")
            print(f"📊 Confidence: {response.confidence_score:.1%}")
            print(f"📚 Sources: {len(response.sources)}")

        elif args.rag_command == "stats":
            stats = rag_system.get_statistics()
            print("📊 RAG System Statistics:")
            for key, value in stats.items():
                print(f"  • {key}: {value}")

        elif args.rag_command == "clear":
            confirm = input("Are you sure you want to clear the RAG index? (y/N): ")
            if confirm.lower() == 'y':
                rag_system.clear_index()
                print("✅ RAG index cleared")
            else:
                print("Operation cancelled")

    elif args.command == "prompt":
        # Initialize prompt tools
        try:
            optimizer = PromptOptimizer(model=getattr(args, 'model', 'anthropic/claude-3-haiku'))
            tester = PromptTester(model=getattr(args, 'model', 'anthropic/claude-3-haiku'))
            library = PromptLibrary()
        except Exception as e:
            logger.error(f"Failed to initialize prompt tools: {e}")
            sys.exit(1)

        if args.prompt_command == "optimize":
            import asyncio
            import json

            # Prepare optimization request
            request_data = {
                "text": args.text,
                "optimization_goal": getattr(args, 'goal', 'clarity')
            }

            # Create optimization request
            from .models import PromptOptimizationRequest
            request = PromptOptimizationRequest(**request_data)

            try:
                print(f"🎯 Optimizing prompt for {request.optimization_goal}...")
                result = asyncio.run(optimizer.optimize_prompt(request))

                print("✅ Optimization completed!")
                print(f"📈 Improvement score: {result.improvement_score:.1%}")
                print("\n📝 Optimized prompt:")
                print(result.optimized_prompt)
                print("\n💡 Suggestions:")
                for suggestion in result.suggestions:
                    print(f"  • {suggestion}")

                # Save to file if requested
                if getattr(args, 'output', None):
                    output_data = result.model_dump()
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt optimization failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "test":
            import asyncio
            import json

            try:
                # Load test cases
                with open(args.test_cases, encoding='utf-8') as f:
                    test_data = json.load(f)

                test_cases = test_data.get('test_cases', [])

                print(f"🧪 Testing prompt against {len(test_cases)} test cases...")
                results = asyncio.run(tester.test_prompt(args.prompt, test_cases))

                # Calculate summary stats
                scores = [r.quality_score for r in results]
                avg_score = sum(scores) / len(scores) if scores else 0

                print("✅ Testing completed!")
                print(f"📊 Average quality score: {avg_score:.1%}")
                print(f"📈 Test results: {len([r for r in results if r.quality_score >= 0.7])}/{len(results)} passed (≥70%)")

                # Save results if requested
                if getattr(args, 'output', None):
                    tester.save_test_results(results, args.output)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt testing failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "benchmark":
            import asyncio
            import json

            try:
                # Load prompts and test cases
                with open(args.prompts, encoding='utf-8') as f:
                    prompts_data = json.load(f)

                with open(args.test_cases, encoding='utf-8') as f:
                    test_data = json.load(f)

                prompts = prompts_data.get('prompts', {})
                test_cases = test_data.get('test_cases', [])

                print(f"🏁 Benchmarking {len(prompts)} prompts against {len(test_cases)} test cases...")
                results = asyncio.run(tester.benchmark_prompts(prompts, test_cases))

                # Sort by performance
                results.sort(key=lambda x: x.average_score, reverse=True)

                print("✅ Benchmarking completed!")
                print("\n📊 Results Summary:")
                for i, result in enumerate(results[:5], 1):  # Top 5
                    print(f"{i}. {result.prompt_id}: {result.average_score:.1%} (±{result.metrics.get('std_dev', 0):.1%})")

                # Save results if requested
                if getattr(args, 'output', None):
                    tester.save_benchmark_results(results, args.output)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt benchmarking failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "library":
            if args.library_command == "list":
                templates = library.list_templates()
                if not templates:
                    print("📚 No templates in library. Use 'janusz prompt library import' to add some.")
                else:
                    print(f"📚 Found {len(templates)} templates:")
                    for template in templates:
                        print(f"  • {template.name} ({template.id}) - {template.category}")

            elif args.library_command == "search":
                results = library.search_templates(args.query, limit=getattr(args, 'limit', 10))
                if not results:
                    print(f"🔍 No templates found for query: '{args.query}'")
                else:
                    print(f"🔍 Found {len(results)} templates matching '{args.query}':")
                    for template in results:
                        print(f"  • {template.name} ({template.id})")
                        print(f"    {template.description[:100]}{'...' if len(template.description) > 100 else ''}")

            elif args.library_command == "export":
                library.export_library(args.output)
                print(f"📤 Library exported to: {args.output}")

            elif args.library_command == "import":
                count = library.import_library(args.input, overwrite=getattr(args, 'overwrite', False))
                print(f"📥 Imported {count} templates from: {args.input}")

            else:
                print("Unknown library command. Use 'janusz prompt library --help' for available options.")

    elif args.command == "test":
        # Try to detect file type and use appropriate test function
        file_path = Path(args.file)
        if file_path.suffix.lower() == ".json":
            test_json_toon_conversion(args.file)
        else:
            test_toon_conversion(args.file)


if __name__ == "__main__":
    main()
