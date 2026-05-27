#!/usr/bin/env python3
"""Unified CLI for Janusz document, JSON, and skill packaging workflows."""

import argparse
import json as json_module
import logging
import sys
from pathlib import Path
from typing import Any, cast

from .converter import UniversalToYAMLConverter
from .converter import process_directory as convert_directory
from .json_packager import (
    convert_directory as json_convert_directory,
)
from .json_packager import (
    convert_file as convert_json_package,
)
from .json_packager import (
    inspect_json_package,
    validate_json_file,
)
from .mcp_server import serve_stdio
from .memory import DEFAULT_MEMORY_PATH, JanuszMemory
from .orchestrator_tool import build_tool_manifest, write_tool_manifest
from .plugin_packager import package_plugin
from .repo_ingester import ingest_repo
from .skill_packager import create_skill_package, create_skill_packages_from_directory
from .skill_quality import dumps_result, format_lint_result, lint_skill, score_skill
from .skill_registry import (
    DEFAULT_REGISTRY_JSONL,
    DEFAULT_REGISTRY_SQLITE,
    build_registry,
    search_registry,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def convert_file_to_yaml(
    file_path: str, use_ai: bool = False, ai_model: str = "anthropic/claude-3-haiku"
) -> bool:
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


def convert_file_to_json(
    file_path: str,
    output_path: str | None = None,
    use_ai: bool = False,
    ai_model: str = "anthropic/claude-3-haiku",
) -> bool:
    """Convert a supported input file to a JSON package."""
    try:
        return convert_json_package(
            file_path,
            output_path=output_path,
            use_ai=use_ai,
            ai_model=ai_model,
        )
    except ValueError as e:
        # Invalid JSON file or parsing errors
        logger.error(f"Invalid file '{file_path}': {e}")
        return False
    except PermissionError as e:
        # File permission issues
        logger.error(f"Permission denied accessing file '{file_path}': {e}")
        return False
    except OSError as e:
        # File system errors
        logger.error(f"File system error processing '{file_path}': {e}")
        return False
    except Exception as e:
        # Unexpected errors - log with full traceback for debugging
        logger.error(f"Unexpected error creating JSON package '{file_path}': {e}", exc_info=True)
        return False


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Janusz - Document-to-JSON Pipeline for AI Agent Knowledge Bases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all documents in 'new' directory to YAML (default behavior)
  janusz convert

  # Convert specific file to YAML
  janusz convert --file document.pdf

  # Create JSON packages
  janusz json
  janusz json --file document.yaml
  janusz json --file document.pdf --output document.json

  # Create a Codex skill package
  janusz skill --file document.json --output-dir skills

  # Seed memory and expose Janusz as an orchestrator tool
  janusz memory seed
  janusz memory context
  janusz tool manifest

  # Improve, index, and distribute skills
  janusz skill lint skills/my-skill
  janusz skill score skills/my-skill
  janusz ingest repo .
  janusz registry build --skills-dir skills
  janusz package plugin --name my-plugin --skill skills/my-skill --output-dir dist/my-plugin

  # Inspect a YAML or JSON package
  janusz test document.json

Supported input formats for convert: PDF, MD, TXT, DOCX, HTML
Supported input formats for json: PDF, MD, TXT, DOCX, HTML, YAML, JSON
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
        "--use-ai",
        action="store_true",
        help="Enable AI-powered analysis (requires JANUSZ_OPENROUTER_API_KEY)",
    )
    convert_parser.add_argument(
        "--ai-model",
        default="anthropic/claude-3-haiku",
        help="AI model to use for analysis (default: anthropic/claude-3-haiku)",
    )

    # Json command
    json_parser = subparsers.add_parser("json", help="Create or validate JSON packages")
    json_parser.add_argument(
        "--directory", "-d", default="new", help="Directory to process (default: new)"
    )
    json_parser.add_argument("--file", "-f", help="Specific file to package")
    json_parser.add_argument("--output", "-o", help="Output JSON file for --file")
    json_parser.add_argument(
        "--validate-only", action="store_true", help="Validate an existing JSON package"
    )
    json_parser.add_argument(
        "--use-ai", action="store_true", help="Enable AI-powered analysis for source documents"
    )
    json_parser.add_argument(
        "--ai-model",
        default="anthropic/claude-3-haiku",
        help="AI model to use for analysis (default: anthropic/claude-3-haiku)",
    )

    # Skill command
    skill_parser = subparsers.add_parser("skill", help="Create Codex skill packages from sources")
    skill_parser.add_argument("--directory", "-d", default="new", help="Directory to process")
    skill_parser.add_argument("--file", "-f", help="Specific file to turn into a skill")
    skill_parser.add_argument(
        "--output-dir", "-o", default="skills", help="Directory for skill packages"
    )
    skill_parser.add_argument("--name", help="Skill name for single-file packaging")
    skill_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing skill package"
    )
    skill_parser.add_argument(
        "--use-ai", action="store_true", help="Enable AI-powered analysis for source documents"
    )
    skill_parser.add_argument(
        "--ai-model",
        default="anthropic/claude-3-haiku",
        help="AI model to use for analysis (default: anthropic/claude-3-haiku)",
    )
    skill_subparsers = skill_parser.add_subparsers(
        dest="skill_command", help="Skill quality operations"
    )

    skill_lint_parser = skill_subparsers.add_parser("lint", help="Lint a Codex skill package")
    skill_lint_parser.add_argument("path", help="Skill directory or SKILL.md path")
    skill_lint_parser.add_argument("--json", action="store_true", help="Print JSON result")

    skill_score_parser = skill_subparsers.add_parser(
        "score", help="Score skill usability for agents"
    )
    skill_score_parser.add_argument("path", help="Skill directory or SKILL.md path")
    skill_score_parser.add_argument("--json", action="store_true", help="Print JSON result")

    # Memory command
    memory_parser = subparsers.add_parser(
        "memory", help="Manage Janusz skill-pack memory for agents"
    )
    memory_subparsers = memory_parser.add_subparsers(
        dest="memory_command", required=True, help="Memory operations"
    )

    memory_seed_parser = memory_subparsers.add_parser(
        "seed", help="Create or refresh the Janusz memory file"
    )
    memory_seed_parser.add_argument(
        "--path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )
    memory_seed_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing memory data"
    )

    memory_list_parser = memory_subparsers.add_parser("list", help="List remembered skill packs")
    memory_list_parser.add_argument(
        "--path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )

    memory_context_parser = memory_subparsers.add_parser(
        "context", help="Print compact JSON context for an orchestrator"
    )
    memory_context_parser.add_argument(
        "--path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )

    # Tool manifest command
    tool_parser = subparsers.add_parser(
        "tool", help="Expose Janusz as a machine-readable orchestrator tool"
    )
    tool_subparsers = tool_parser.add_subparsers(
        dest="tool_command", required=True, help="Tool metadata operations"
    )
    tool_manifest_parser = tool_subparsers.add_parser(
        "manifest", help="Print or write the Janusz tool manifest"
    )
    tool_manifest_parser.add_argument("--output", "-o", help="Output manifest JSON path")
    tool_manifest_parser.add_argument(
        "--memory-path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest", help="Ingest sources into agent-ready knowledge packages"
    )
    ingest_subparsers = ingest_parser.add_subparsers(
        dest="ingest_command", required=True, help="Ingest operations"
    )
    ingest_repo_parser = ingest_subparsers.add_parser(
        "repo", help="Create a repository operations skill package"
    )
    ingest_repo_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    ingest_repo_parser.add_argument(
        "--output-dir", "-o", default="skills", help="Directory for generated skills"
    )
    ingest_repo_parser.add_argument("--name", help="Skill name")
    ingest_repo_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing skill"
    )

    # Registry command
    registry_parser = subparsers.add_parser(
        "registry", help="Build and search a local skill registry"
    )
    registry_subparsers = registry_parser.add_subparsers(
        dest="registry_command", required=True, help="Registry operations"
    )
    registry_build_parser = registry_subparsers.add_parser(
        "build", help="Build JSONL and optional SQLite skill registry"
    )
    registry_build_parser.add_argument(
        "--skills-dir",
        action="append",
        dest="skills_dirs",
        help="Skill directory root to index; can be repeated",
    )
    registry_build_parser.add_argument(
        "--output", default=str(DEFAULT_REGISTRY_JSONL), help="Output JSONL path"
    )
    registry_build_parser.add_argument(
        "--sqlite", default=str(DEFAULT_REGISTRY_SQLITE), help="Output SQLite path"
    )
    registry_build_parser.add_argument(
        "--no-sqlite", action="store_true", help="Skip SQLite registry output"
    )

    registry_search_parser = registry_subparsers.add_parser(
        "search", help="Search a JSONL skill registry"
    )
    registry_search_parser.add_argument("query", nargs="?", default="", help="Search query")
    registry_search_parser.add_argument(
        "--registry", default=str(DEFAULT_REGISTRY_JSONL), help="Registry JSONL path"
    )
    registry_search_parser.add_argument("--category", help="Filter by category")
    registry_search_parser.add_argument("--min-score", type=int, default=0)
    registry_search_parser.add_argument("--limit", type=int, default=20)
    registry_search_parser.add_argument("--json", action="store_true", help="Print JSON result")

    # Package command
    package_parser = subparsers.add_parser(
        "package", help="Package skills and manifests for distribution"
    )
    package_subparsers = package_parser.add_subparsers(
        dest="package_command", required=True, help="Package operations"
    )
    plugin_parser = package_subparsers.add_parser(
        "plugin", help="Bundle skills into a Codex plugin folder"
    )
    plugin_parser.add_argument("--skill", action="append", required=True, help="Skill to bundle")
    plugin_parser.add_argument("--output-dir", "-o", required=True, help="Plugin output directory")
    plugin_parser.add_argument("--name", required=True, help="Plugin display name")
    plugin_parser.add_argument("--version", default="0.1.0", help="Plugin version")
    plugin_parser.add_argument("--description", help="Plugin description")
    plugin_parser.add_argument("--overwrite", action="store_true", help="Overwrite output dir")
    plugin_parser.add_argument(
        "--no-manifest", action="store_true", help="Do not include Janusz tool manifest"
    )

    # MCP command
    mcp_parser = subparsers.add_parser("mcp", help="Run Janusz as an MCP stdio server")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP operations")
    mcp_serve_parser = mcp_subparsers.add_parser("serve", help="Serve MCP over stdio")
    mcp_serve_parser.add_argument("--root", default=".", help="Workspace root for resources")
    mcp_serve_parser.add_argument(
        "--memory-path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )
    mcp_parser.add_argument("--root", default=".", help="Workspace root for resources")
    mcp_parser.add_argument(
        "--memory-path", default=str(DEFAULT_MEMORY_PATH), help="Memory JSON path"
    )

    # GUI command
    subparsers.add_parser("gui", help="Launch the graphical user interface")

    # Schema commands
    schema_parser = subparsers.add_parser("schema", help="Manage modular schemas")
    schema_subparsers = schema_parser.add_subparsers(
        dest="schema_command", help="Schema operations"
    )

    # Schema list
    schema_list_parser = schema_subparsers.add_parser("list", help="List available schemas")
    schema_list_parser.add_argument("--category", help="Filter by category")
    schema_list_parser.add_argument("--tag", action="append", help="Filter by tags")

    # Schema create
    schema_create_parser = schema_subparsers.add_parser(
        "create", help="Create schema from document"
    )
    schema_create_parser.add_argument("file", help="Source document file")
    schema_create_parser.add_argument("--name", required=True, help="Schema name")
    schema_create_parser.add_argument("--description", required=True, help="Schema description")
    schema_create_parser.add_argument(
        "--category",
        default="technical",
        choices=["technical", "business", "educational", "process", "reference", "tutorial"],
        help="Schema category",
    )

    # Schema generate AI
    schema_ai_parser = schema_subparsers.add_parser("generate-ai", help="Generate schema using AI")
    schema_ai_parser.add_argument("--prompt", required=True, help="Natural language prompt")
    schema_ai_parser.add_argument(
        "--category",
        default="technical",
        choices=["technical", "business", "educational", "process", "reference", "tutorial"],
        help="Schema category",
    )

    # Orchestrator command
    orchestrator_parser = subparsers.add_parser(
        "orchestrate", help="Use AI orchestrator for intelligent processing"
    )
    orchestrator_parser.add_argument("request", help="Natural language processing request")
    orchestrator_parser.add_argument("--file", help="Document file to analyze")
    orchestrator_parser.add_argument("--use-ai", action="store_true", help="Enable AI analysis")

    # RAG commands
    rag_parser = subparsers.add_parser(
        "rag", help="RAG (Retrieval-Augmented Generation) operations"
    )
    rag_subparsers = rag_parser.add_subparsers(dest="rag_command", help="RAG operations")

    # RAG index
    rag_index_parser = rag_subparsers.add_parser("index", help="Index documents for RAG")
    rag_index_parser.add_argument("--directory", "-d", default="new", help="Directory to index")
    rag_index_parser.add_argument("--file", "-f", help="Specific file to index")

    # RAG query
    rag_query_parser = rag_subparsers.add_parser("query", help="Query the RAG system")
    rag_query_parser.add_argument("question", help="Question to ask")
    rag_query_parser.add_argument(
        "--max-results", "-n", type=int, default=5, help="Maximum results"
    )

    # RAG stats
    rag_subparsers.add_parser("stats", help="Show RAG system statistics")

    # RAG clear
    rag_subparsers.add_parser("clear", help="Clear RAG index")

    # Prompt commands
    prompt_parser = subparsers.add_parser("prompt", help="Prompt optimization and management tools")
    prompt_subparsers = prompt_parser.add_subparsers(
        dest="prompt_command", help="Prompt operations"
    )

    # Prompt optimize
    optimize_parser = prompt_subparsers.add_parser(
        "optimize", help="Optimize a prompt for better performance"
    )
    optimize_parser.add_argument("text", help="Prompt text to optimize")
    optimize_parser.add_argument(
        "--goal",
        "-g",
        choices=[
            "clarity",
            "efficiency",
            "specificity",
            "creativity",
            "conciseness",
            "comprehensiveness",
        ],
        default="clarity",
        help="Optimization goal",
    )
    optimize_parser.add_argument(
        "--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use"
    )
    optimize_parser.add_argument("--output", "-o", help="Save optimized prompt to file")

    # Prompt test
    test_parser = prompt_subparsers.add_parser(
        "test", help="Test prompt performance against test cases"
    )
    test_parser.add_argument("prompt", help="Prompt to test")
    test_parser.add_argument("--test-cases", "-t", required=True, help="JSON file with test cases")
    test_parser.add_argument("--output", "-o", help="Save test results to file")
    test_parser.add_argument(
        "--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use"
    )

    # Prompt benchmark
    benchmark_parser = prompt_subparsers.add_parser("benchmark", help="Benchmark multiple prompts")
    benchmark_parser.add_argument(
        "--prompts", "-p", required=True, help="JSON file with prompts to benchmark"
    )
    benchmark_parser.add_argument(
        "--test-cases", "-t", required=True, help="JSON file with test cases"
    )
    benchmark_parser.add_argument("--output", "-o", help="Save benchmark results to file")
    benchmark_parser.add_argument(
        "--model", "-m", default="anthropic/claude-3-haiku", help="AI model to use"
    )

    # Prompt library commands
    library_parser = prompt_subparsers.add_parser("library", help="Manage prompt library")
    library_subparsers = library_parser.add_subparsers(
        dest="library_command", help="Library operations"
    )

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
    import_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing templates"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Inspect a YAML or JSON package")
    test_parser.add_argument("file", help="YAML or JSON file to test")

    # Version
    parser.add_argument("--version", action="version", version="Janusz 1.0.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "convert":
        if args.file:
            success = convert_file_to_yaml(
                args.file,
                use_ai=getattr(args, "use_ai", False),
                ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
            )
            sys.exit(0 if success else 1)
        else:
            convert_directory(
                args.directory,
                use_ai=getattr(args, "use_ai", False),
                ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
            )

    elif args.command == "json":
        if args.validate_only:
            if not args.file:
                logger.error("--validate-only requires --file")
                sys.exit(1)
            success = validate_json_file(args.file)
            sys.exit(0 if success else 1)

        if args.file:
            success = convert_file_to_json(
                args.file,
                output_path=getattr(args, "output", None),
                use_ai=getattr(args, "use_ai", False),
                ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
            )
            sys.exit(0 if success else 1)
        else:
            json_convert_directory(
                args.directory,
                use_ai=getattr(args, "use_ai", False),
                ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
            )

    elif args.command == "skill":
        if getattr(args, "skill_command", None) == "lint":
            result = lint_skill(args.path)
            print(dumps_result(result) if args.json else format_lint_result(result))
            sys.exit(0 if result["valid"] else 1)

        if getattr(args, "skill_command", None) == "score":
            result = score_skill(args.path)
            if args.json:
                print(dumps_result(result))
            else:
                print(f"Skill: {result.get('name') or result['path']}")
                print(f"Score: {result['score']}/100 ({result['grade']})")
                print(f"Agent usable: {str(result['agent_usable']).lower()}")
                print(f"Issues: {result['issue_count']}")
                print(result["summary"])
            sys.exit(0 if result["agent_usable"] else 1)

        if args.file:
            try:
                skill_path = create_skill_package(
                    args.file,
                    output_dir=args.output_dir,
                    skill_name=getattr(args, "name", None),
                    overwrite=getattr(args, "overwrite", False),
                    use_ai=getattr(args, "use_ai", False),
                    ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
                )
                print(f"Created skill package: {skill_path}")
            except Exception as e:
                logger.error(f"Skill package creation failed: {e}")
                sys.exit(1)
        else:
            create_skill_packages_from_directory(
                args.directory,
                output_dir=args.output_dir,
                overwrite=getattr(args, "overwrite", False),
                use_ai=getattr(args, "use_ai", False),
                ai_model=getattr(args, "ai_model", "anthropic/claude-3-haiku"),
            )

    elif args.command == "memory":
        memory = JanuszMemory(Path(args.path))

        if args.memory_command == "seed":
            data = memory.seed(overwrite=getattr(args, "overwrite", False))
            print(f"Memory ready: {memory.path} ({len(data['skill_packs'])} skill packs)")

        elif args.memory_command == "list":
            skill_packs = memory.list_skill_packs()
            print(f"Remembered skill packs: {len(skill_packs)}")
            for item in skill_packs:
                print(
                    f"- {item['name']} [{item['category']}] "
                    f"priority={item['priority']} role={item['orchestrator_role']}"
                )

        elif args.memory_command == "context":
            print(json_module.dumps(memory.export_tool_context(), indent=2, ensure_ascii=False))

    elif args.command == "tool":
        memory_path = Path(args.memory_path)

        if args.tool_command == "manifest":
            if getattr(args, "output", None):
                output_path = Path(args.output)
                write_tool_manifest(output_path, memory_path=memory_path, workspace_root=Path.cwd())
                print(f"Tool manifest written: {output_path}")
            else:
                print(
                    json_module.dumps(
                        build_tool_manifest(memory_path=memory_path, workspace_root=Path.cwd()),
                        indent=2,
                        ensure_ascii=False,
                    )
                )

    elif args.command == "ingest":
        if args.ingest_command == "repo":
            try:
                skill_path = ingest_repo(
                    args.path,
                    output_dir=args.output_dir,
                    skill_name=getattr(args, "name", None),
                    overwrite=getattr(args, "overwrite", False),
                )
                print(f"Created repository skill package: {skill_path}")
            except Exception as e:
                logger.error(f"Repository ingest failed: {e}")
                sys.exit(1)

    elif args.command == "registry":
        if args.registry_command == "build":
            roots = args.skills_dirs or ["skills"]
            sqlite_path = None if args.no_sqlite else Path(args.sqlite)
            entries = build_registry(
                roots,
                output_jsonl=Path(args.output),
                sqlite_path=sqlite_path,
            )
            print(f"Indexed {len(entries)} skills into {args.output}")
            if sqlite_path is not None:
                print(f"SQLite registry written: {sqlite_path}")

        elif args.registry_command == "search":
            results = search_registry(
                query=args.query,
                registry_path=Path(args.registry),
                category=getattr(args, "category", None),
                min_score=getattr(args, "min_score", 0),
                limit=getattr(args, "limit", 20),
            )
            if args.json:
                print(json_module.dumps(results, indent=2, ensure_ascii=False))
            elif not results:
                print("No matching skills found.")
            else:
                print(f"Found {len(results)} skills:")
                for item in results:
                    print(
                        f"- {item['name']} [{item['category']}] "
                        f"score={item['quality_score']} path={item['path']}"
                    )

    elif args.command == "package":
        if args.package_command == "plugin":
            try:
                plugin_path = package_plugin(
                    skill_paths=args.skill,
                    output_dir=args.output_dir,
                    name=args.name,
                    version=getattr(args, "version", "0.1.0"),
                    description=getattr(args, "description", None),
                    overwrite=getattr(args, "overwrite", False),
                    include_manifest=not getattr(args, "no_manifest", False),
                )
                print(f"Created plugin package: {plugin_path}")
            except Exception as e:
                logger.error(f"Plugin packaging failed: {e}")
                sys.exit(1)

    elif args.command == "mcp":
        serve_stdio(
            root=Path(getattr(args, "root", ".")),
            memory_path=Path(getattr(args, "memory_path", str(DEFAULT_MEMORY_PATH))),
        )

    elif args.command == "gui":
        try:
            from .gui.main_app import main as gui_main

            cast(Any, gui_main)()
        except ImportError as e:
            logger.error(f"GUI components not available: {e}")
            logger.error("Make sure tkinter is installed: pip install tk")
            sys.exit(1)

    elif args.command == "schema":
        from .schemas.schema_manager import SchemaManager

        if args.schema_command == "list":
            schema_manager = SchemaManager()
            schemas = schema_manager.list_schemas(
                category=getattr(args, "category", None), tags=getattr(args, "tag", None)
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
            schema_manager = SchemaManager()
            # Convert file to document structure first
            converter = UniversalToYAMLConverter(args.file)
            doc_structure = converter.parse_text_structure(converter.extract_text_from_file())

            schema = schema_manager.create_schema_from_document(
                doc_structure, args.name, args.description, args.category
            )

            print(f"✅ Created schema: {schema.name} ({schema.id})")

        elif args.schema_command == "generate-ai":
            try:
                from janusz.ai.ai_content_analyzer import AIContentAnalyzer

                ai_analyzer = AIContentAnalyzer()
                schema_manager = SchemaManager(ai_analyzer=ai_analyzer)
                schema = schema_manager.generate_ai_schema(args.prompt, args.category)
                print(f"🤖 Generated AI schema: {schema.name} ({schema.id})")
            except (ImportError, RuntimeError, ValueError) as e:
                logger.error(f"AI schema generation unavailable: {e}")
                print(f"AI schema generation unavailable: {e}", file=sys.stderr)
                print(
                    "Configure JANUSZ_OPENROUTER_API_KEY and install Janusz with the "
                    "AI extra, for example: janusz[ai].",
                    file=sys.stderr,
                )
                sys.exit(1)
            except Exception as e:
                logger.error(f"AI schema generation failed: {e}")
                print(f"AI schema generation failed: {e}", file=sys.stderr)
                sys.exit(1)

    elif args.command == "orchestrate":
        from .orchestrator.ai_orchestrator import AIOrchestrator

        try:
            from janusz.ai.ai_content_analyzer import AIContentAnalyzer

            orchestrator_ai_analyzer: Any = (
                AIContentAnalyzer() if getattr(args, "use_ai", False) else None
            )
        except Exception:
            orchestrator_ai_analyzer = None
            if getattr(args, "use_ai", False):
                logger.warning("AI requested but not available")

        orchestrator = AIOrchestrator(ai_analyzer=orchestrator_ai_analyzer)

        # Load document if provided
        document = None
        if getattr(args, "file", None):
            converter = UniversalToYAMLConverter(args.file)
            document = converter.parse_text_structure(converter.extract_text_from_file())

        orchestrator_response = orchestrator.process_document_request(args.request, document)

        print("🎯 Orchestrator Response:")
        print(
            f"Recommended schemas: {', '.join(orchestrator_response.recommended_schemas) or 'None'}"
        )
        print(f"Confidence: {orchestrator_response.confidence_score:.1%}")
        print(f"Reasoning: {orchestrator_response.reasoning}")

        if orchestrator_response.alternative_options:
            print("\nAlternatives:")
            for alt in orchestrator_response.alternative_options:
                print(f"  • {alt.get('reason', alt)}")

        if orchestrator_response.processing_plan:
            print("\nProcessing plan:")
            for key, value in orchestrator_response.processing_plan.items():
                print(f"  • {key}: {value}")

        if orchestrator_response.estimated_time:
            print(f"\nEstimated time: {orchestrator_response.estimated_time} seconds")

    elif args.command == "rag":
        try:
            from .rag.rag_system import RAGSystem

            rag_system = RAGSystem()
        except Exception as e:
            logger.error(f"RAG system initialization failed: {e}")
            sys.exit(1)

        if args.rag_command == "index":
            if args.file:
                # Index single file
                try:
                    converter = UniversalToYAMLConverter(args.file)
                    doc_structure = converter.parse_text_structure(
                        converter.extract_text_from_file()
                    )
                    doc_id = rag_system.add_document(doc_structure)
                    print(f"✅ Indexed document: {args.file} (ID: {doc_id})")
                except Exception as e:
                    logger.error(f"Failed to index {args.file}: {e}")
                    sys.exit(1)
            else:
                # Index directory (simplified version)
                print("Directory indexing not yet implemented. Use individual files.")

        elif args.rag_command == "query":
            rag_response = rag_system.query(args.question, max_results=args.max_results)
            print(f"🤖 Answer: {rag_response.answer}")
            print(f"📊 Confidence: {rag_response.confidence_score:.1%}")
            print(f"📚 Sources: {len(rag_response.sources)}")

        elif args.rag_command == "stats":
            stats = rag_system.get_statistics()
            print("📊 RAG System Statistics:")
            for key, value in stats.items():
                print(f"  • {key}: {value}")

        elif args.rag_command == "clear":
            confirm = input("Are you sure you want to clear the RAG index? (y/N): ")
            if confirm.lower() == "y":
                cast(Any, rag_system).clear_index()
                print("✅ RAG index cleared")
            else:
                print("Operation cancelled")

    elif args.command == "prompt":
        if args.prompt_command == "optimize":
            import asyncio
            import json

            from .models import PromptOptimizationRequest
            from .prompts.prompt_optimizer import PromptOptimizer

            try:
                optimizer = PromptOptimizer(
                    model=getattr(args, "model", "anthropic/claude-3-haiku")
                )
            except Exception as e:
                logger.error(f"Failed to initialize prompt optimizer: {e}")
                sys.exit(1)

            # Prepare optimization request
            request_data = {
                "text": args.text,
                "optimization_goal": getattr(args, "goal", "clarity"),
            }

            # Create optimization request
            request = PromptOptimizationRequest(**request_data)

            try:
                print(f"🎯 Optimizing prompt for {request.optimization_goal}...")
                optimization_result = asyncio.run(optimizer.optimize_prompt(request))

                print("✅ Optimization completed!")
                print(f"📈 Improvement score: {optimization_result.improvement_score:.1%}")
                print("\n📝 Optimized prompt:")
                print(optimization_result.optimized_prompt)
                print("\n💡 Suggestions:")
                for suggestion in optimization_result.suggestions:
                    print(f"  • {suggestion}")

                # Save to file if requested
                if getattr(args, "output", None):
                    output_data = optimization_result.model_dump()
                    with open(args.output, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt optimization failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "test":
            import asyncio
            import json

            from .prompts.prompt_tester import PromptTester

            try:
                tester = PromptTester(model=getattr(args, "model", "anthropic/claude-3-haiku"))
            except Exception as e:
                logger.error(f"Failed to initialize prompt tester: {e}")
                sys.exit(1)

            try:
                # Load test cases
                with open(args.test_cases, encoding="utf-8") as f:
                    test_data = json.load(f)

                test_cases = test_data.get("test_cases", [])

                print(f"🧪 Testing prompt against {len(test_cases)} test cases...")
                prompt_test_results = asyncio.run(tester.test_prompt(args.prompt, test_cases))

                # Calculate summary stats
                scores = [test_result.quality_score for test_result in prompt_test_results]
                avg_score = sum(scores) / len(scores) if scores else 0

                print("✅ Testing completed!")
                print(f"📊 Average quality score: {avg_score:.1%}")
                print(
                    "📈 Test results: "
                    f"{len([r for r in prompt_test_results if r.quality_score >= 0.7])}/"
                    f"{len(prompt_test_results)} passed (≥70%)"
                )

                # Save results if requested
                if getattr(args, "output", None):
                    tester.save_test_results(prompt_test_results, args.output)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt testing failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "benchmark":
            import asyncio
            import json

            from .prompts.prompt_tester import PromptTester

            try:
                tester = PromptTester(model=getattr(args, "model", "anthropic/claude-3-haiku"))
            except Exception as e:
                logger.error(f"Failed to initialize prompt tester: {e}")
                sys.exit(1)

            try:
                # Load prompts and test cases
                with open(args.prompts, encoding="utf-8") as f:
                    prompts_data = json.load(f)

                with open(args.test_cases, encoding="utf-8") as f:
                    test_data = json.load(f)

                prompts = prompts_data.get("prompts", {})
                test_cases = test_data.get("test_cases", [])

                print(
                    f"🏁 Benchmarking {len(prompts)} prompts against {len(test_cases)} test cases..."
                )
                benchmark_results = asyncio.run(tester.benchmark_prompts(prompts, test_cases))

                # Sort by performance
                benchmark_results.sort(key=lambda item: item.average_score, reverse=True)

                print("✅ Benchmarking completed!")
                print("\n📊 Results Summary:")
                for i, benchmark_result in enumerate(benchmark_results[:5], 1):  # Top 5
                    print(
                        f"{i}. {benchmark_result.prompt_id}: "
                        f"{benchmark_result.average_score:.1%} "
                        f"(±{benchmark_result.metrics.get('std_dev', 0):.1%})"
                    )

                # Save results if requested
                if getattr(args, "output", None):
                    tester.save_benchmark_results(benchmark_results, args.output)
                    print(f"💾 Results saved to: {args.output}")

            except Exception as e:
                logger.error(f"Prompt benchmarking failed: {e}")
                sys.exit(1)

        elif args.prompt_command == "library":
            from .prompts.prompt_templates import PromptLibrary

            library = PromptLibrary()

            if args.library_command == "list":
                templates = library.list_templates()
                if not templates:
                    print(
                        "📚 No templates in library. Use 'janusz prompt library import' to add some."
                    )
                else:
                    print(f"📚 Found {len(templates)} templates:")
                    for template in templates:
                        print(f"  • {template.name} ({template.id}) - {template.category}")

            elif args.library_command == "search":
                library_results = library.search_templates(
                    args.query, limit=getattr(args, "limit", 10)
                )
                if not library_results:
                    print(f"🔍 No templates found for query: '{args.query}'")
                else:
                    print(f"🔍 Found {len(library_results)} templates matching '{args.query}':")
                    for template in library_results:
                        print(f"  • {template.name} ({template.id})")
                        print(
                            f"    {template.description[:100]}{'...' if len(template.description) > 100 else ''}"
                        )

            elif args.library_command == "export":
                library.export_library(args.output)
                print(f"📤 Library exported to: {args.output}")

            elif args.library_command == "import":
                count = library.import_library(
                    args.input, overwrite=getattr(args, "overwrite", False)
                )
                print(f"📥 Imported {count} templates from: {args.input}")

            else:
                print(
                    "Unknown library command. Use 'janusz prompt library --help' for available options."
                )

    elif args.command == "test":
        success = inspect_json_package(args.file)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
