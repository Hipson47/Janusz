"""
Janusz - Document-to-JSON Pipeline for AI Agent Knowledge Bases

A Python package that converts various document formats to structured YAML
and JSON packages for efficient AI agent prompting and knowledge storage.

Supported input formats: PDF, MD, TXT, DOCX, HTML, YAML, JSON
Output formats: YAML (structured), JSON (agent package), Codex skills, tool manifests

Example usage:
    from janusz import UniversalToYAMLConverter, JSONPackageConverter, JanuszMemory

    # Convert document to YAML
    converter = UniversalToYAMLConverter("document.pdf")
    converter.convert_to_yaml()

    # Convert YAML or a source document to JSON
    json_converter = JSONPackageConverter("document.yaml")
    json_converter.convert()
"""

__version__ = "1.0.0"
__author__ = "Janusz AI Team"
__description__ = "Document-to-JSON pipeline for AI agent knowledge bases"

from .converter import UniversalToYAMLConverter
from .converter import process_directory as convert_directory
from .json_packager import JSONPackageConverter
from .json_packager import convert_directory as json_convert_directory
from .memory import JanuszMemory
from .orchestrator_tool import build_tool_manifest
from .repo_ingester import ingest_repo
from .skill_packager import create_skill_package
from .skill_quality import lint_skill, score_skill

__all__ = [
    "UniversalToYAMLConverter",
    "JSONPackageConverter",
    "JanuszMemory",
    "build_tool_manifest",
    "ingest_repo",
    "lint_skill",
    "score_skill",
    "convert_directory",
    "json_convert_directory",
    "create_skill_package",
]
