#!/usr/bin/env python3
"""
JSON package utilities for Janusz agent knowledge bases.

The package format is plain structured JSON produced from YAML files, JSON files,
or supported source documents.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .converter import UniversalToYAMLConverter

logger = logging.getLogger(__name__)


class JSONPackageError(Exception):
    """Raised when a JSON package cannot be created or validated."""


class JSONPackageConverter:
    """Convert supported inputs to structured JSON packages."""

    STRUCTURED_EXTENSIONS = {".yaml", ".yml", ".json"}
    SUPPORTED_EXTENSIONS = UniversalToYAMLConverter.SUPPORTED_EXTENSIONS | STRUCTURED_EXTENSIONS

    def __init__(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        use_ai: bool = False,
        ai_model: str = "anthropic/claude-3-haiku",
    ):
        self.input_path = Path(input_path)
        self.output_path = (
            Path(output_path) if output_path else self.input_path.with_suffix(".json")
        )
        self.use_ai = use_ai
        self.ai_model = ai_model

        if self.input_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {self.input_path.suffix}. "
                f"Supported: {sorted(self.SUPPORTED_EXTENSIONS)}"
            )

    def validate_json(self) -> bool:
        """Return True when the input file is well-formed JSON."""
        try:
            load_json_file(self.input_path)
            return True
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            logger.error(f"Invalid JSON package '{self.input_path}': {exc}")
            return False

    def convert(self) -> bool:
        """Create or normalize a JSON package."""
        try:
            data = self.to_package_data()
            write_json_package(data, self.output_path)
            logger.info(f"Successfully wrote JSON package: {self.output_path}")
            return True
        except Exception as exc:
            logger.error(f"Failed to create JSON package for '{self.input_path}': {exc}")
            return False

    def to_package_data(self) -> Dict[str, Any]:
        """Load the input and return normalized package data."""
        suffix = self.input_path.suffix.lower()

        if suffix == ".json":
            data = load_json_file(self.input_path)
        elif suffix in {".yaml", ".yml"}:
            data = load_yaml_file(self.input_path)
        else:
            converter = UniversalToYAMLConverter(
                str(self.input_path),
                use_ai=self.use_ai,
                ai_model=self.ai_model,
            )
            text = converter.extract_text_from_file()
            if not text:
                raise JSONPackageError(f"No text extracted from '{self.input_path}'")
            data = converter.parse_text_structure(text).model_dump()

        if not isinstance(data, dict):
            raise JSONPackageError("Package root must be a JSON object")

        return data


def load_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a JSON object from disk."""
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise TypeError("JSON package root must be an object")
    return data


def load_yaml_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML object from disk."""
    with open(path, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise TypeError("YAML package root must be an object")
    return data


def load_structured_package(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML or JSON package."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".json":
        return load_json_file(source)
    if suffix in {".yaml", ".yml"}:
        return load_yaml_file(source)
    return JSONPackageConverter(str(source)).to_package_data()


def write_json_package(data: Dict[str, Any], output_path: Union[str, Path]) -> Path:
    """Write package data as pretty, deterministic JSON."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return destination


def convert_file(
    input_path: str,
    output_path: Optional[str] = None,
    use_ai: bool = False,
    ai_model: str = "anthropic/claude-3-haiku",
) -> bool:
    """Convert one supported file to a JSON package."""
    converter = JSONPackageConverter(
        input_path,
        output_path=output_path,
        use_ai=use_ai,
        ai_model=ai_model,
    )
    return converter.convert()


def validate_json_file(json_path: str) -> bool:
    """Validate one JSON package."""
    return JSONPackageConverter(json_path).validate_json()


def convert_directory(
    directory: str = "new",
    use_ai: bool = False,
    ai_model: str = "anthropic/claude-3-haiku",
) -> None:
    """Convert supported files in a directory to JSON packages."""
    dir_path = Path(directory)
    dir_path.mkdir(exist_ok=True)

    supported_files: List[Path] = []
    for extension in sorted(JSONPackageConverter.SUPPORTED_EXTENSIONS - {".json"}):
        supported_files.extend(dir_path.glob(f"**/*{extension}"))

    if not supported_files:
        logger.info(f"No supported files found in {directory}")
        return

    successful = 0
    failed = 0
    for file_path in supported_files:
        logger.info(f"Packaging as JSON: {file_path}")
        if convert_file(str(file_path), use_ai=use_ai, ai_model=ai_model):
            successful += 1
        else:
            failed += 1

    logger.info(f"JSON packaging completed: {successful} successful, {failed} failed")


def inspect_json_package(path: str) -> bool:
    """Log a compact inspection summary for YAML or JSON package files."""
    try:
        data = load_structured_package(path)
    except Exception as exc:
        logger.error(f"Package inspection failed: {exc}")
        return False

    metadata = data.get("metadata", {})
    content = data.get("content", {})
    analysis = data.get("analysis", {})

    logger.info(f"Package title: {metadata.get('title', Path(path).stem)}")
    logger.info(f"Source type: {metadata.get('source_type', 'unknown')}")
    logger.info(f"Sections: {len(content.get('sections') or [])}")
    logger.info(f"Keywords: {len(analysis.get('keywords') or [])}")
    logger.info(f"Best practices: {len(analysis.get('best_practices') or [])}")
    return True
