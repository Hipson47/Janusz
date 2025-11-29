"""
Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases

A Python package that converts various document formats to structured YAML
and then optimizes them to TOON (Token-Oriented Object Notation) format
for efficient AI agent prompting and knowledge storage.

Supported input formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB
Output formats: YAML (structured), TOON (optimized for AI)

Example usage:
    from janusz import UniversalToYAMLConverter, YAMLToTOONConverter

    # Convert document to YAML
    converter = UniversalToYAMLConverter("document.pdf")
    converter.convert_to_yaml()

    # Convert YAML to TOON
    toon_converter = YAMLToTOONConverter("document.yaml")
    toon_converter.convert()
"""

__version__ = "1.0.0"
__author__ = "Janusz AI Team"
__description__ = "Document-to-TOON pipeline for AI agent knowledge bases"

from .converter import UniversalToYAMLConverter
from .converter import process_directory as convert_directory
from .toon_adapter import YAMLToTOONConverter
from .toon_adapter import convert_directory as toon_convert_directory

__all__ = [
    "UniversalToYAMLConverter",
    "YAMLToTOONConverter",
    "convert_directory",
    "toon_convert_directory",
]
