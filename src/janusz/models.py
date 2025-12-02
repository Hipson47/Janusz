#!/usr/bin/env python3
"""
Data Models for Janusz - Document-to-TOON Pipeline

This module defines Pydantic models for structured data validation.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Metadata for a converted document."""
    title: str
    source: str
    source_type: str
    converted_by: str = "Janusz v1.1.0"
    format_version: str = "1.1.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    parser_version: str = "1.1.0"


class Section(BaseModel):
    """A hierarchical section within a document."""
    id: Optional[str] = None
    title: str
    level: int = 1
    content: Optional[List[str]] = None  # Support both list and string for backward compatibility
    subsections: Optional[List['Section']] = Field(default_factory=list)  # Keep old field name for compatibility
    children: List['Section'] = Field(default_factory=list)  # New hierarchical field
    keywords: List['Keyword'] = Field(default_factory=list)


class Keyword(BaseModel):
    """A keyword with confidence level."""
    text: str
    confidence_level: Literal["low", "medium", "high"] = "medium"


class ExtractionItem(BaseModel):
    """An extracted item (best practice, example) with metadata."""
    text: str
    source_section_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    confidence_level: Literal["low", "medium", "high"] = "medium"


class Content(BaseModel):
    """Content structure of a document."""
    sections: List[Section] = Field(default_factory=list)
    raw_text: str


class Analysis(BaseModel):
    """Analysis results for a document."""
    keywords: List[Keyword] = Field(default_factory=list)
    best_practices: List[ExtractionItem] = Field(default_factory=list)
    examples: List[ExtractionItem] = Field(default_factory=list)


class DocumentStructure(BaseModel):
    """Complete document structure with metadata, content, and analysis."""
    metadata: Metadata
    content: Content
    analysis: Optional[Analysis] = None
