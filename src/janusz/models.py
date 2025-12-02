#!/usr/bin/env python3
"""
Data Models for Janusz - Document-to-TOON Pipeline

This module defines Pydantic models for structured data validation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Metadata for a converted document."""
    title: str
    source: str
    source_type: str
    converted_by: str = "Janusz v1.0.0"
    format_version: str = "2.0"


class Section(BaseModel):
    """A section within a document."""
    title: str
    content: List[str]
    subsections: List['Section'] = Field(default_factory=list)


class Content(BaseModel):
    """Content structure of a document."""
    sections: List[Section] = Field(default_factory=list)
    raw_text: str


class Analysis(BaseModel):
    """Analysis results for a document."""
    keywords: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)


class DocumentStructure(BaseModel):
    """Complete document structure with metadata, content, and analysis."""
    metadata: Metadata
    content: Content
    analysis: Optional[Analysis] = None
