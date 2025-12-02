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

    # AI processing metadata (optional)
    ai_processing_enabled: bool = False
    ai_model_used: Optional[str] = None
    ai_processing_time_seconds: Optional[float] = None


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


class AIInsight(BaseModel):
    """AI-generated insight with metadata."""
    text: str
    insight_type: Literal["summary", "improvement", "warning", "enhancement", "clarification"] = "enhancement"
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    reasoning: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source_section_ids: List[str] = Field(default_factory=list)


class AIExtractionResult(BaseModel):
    """Result from AI-powered extraction."""
    best_practices: List[ExtractionItem] = Field(default_factory=list)
    examples: List[ExtractionItem] = Field(default_factory=list)
    insights: List[AIInsight] = Field(default_factory=list)
    summary: Optional[str] = None
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)
    ai_model_used: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class Content(BaseModel):
    """Content structure of a document."""
    sections: List[Section] = Field(default_factory=list)
    raw_text: str


class Analysis(BaseModel):
    """Analysis results for a document."""
    keywords: List[Keyword] = Field(default_factory=list)
    best_practices: List[ExtractionItem] = Field(default_factory=list)
    examples: List[ExtractionItem] = Field(default_factory=list)

    # AI-enhanced fields (optional)
    ai_insights: Optional[List[AIInsight]] = None
    ai_summary: Optional[str] = None
    ai_quality_score: Optional[float] = None
    ai_extraction_used: bool = False


class DocumentStructure(BaseModel):
    """Complete document structure with metadata, content, and analysis."""
    metadata: Metadata
    content: Content
    analysis: Optional[Analysis] = None
