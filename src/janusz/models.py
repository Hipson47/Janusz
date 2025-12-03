#!/usr/bin/env python3
"""
Data Models for Janusz - Document-to-TOON Pipeline

This module defines Pydantic models for structured data validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

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


class ModularSchema(BaseModel):
    """A modular, reusable schema for document processing."""
    id: str
    name: str
    description: str
    category: Literal["technical", "business", "educational", "process", "reference", "tutorial"] = "technical"
    tags: List[str] = Field(default_factory=list)
    components: List[Dict[str, Any]] = Field(default_factory=list)  # Flexible component structure
    dependencies: List[str] = Field(default_factory=list)  # IDs of required schemas
    ai_generated: bool = False
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    ai_model_used: Optional[str] = None


class SchemaComponent(BaseModel):
    """A component within a modular schema."""
    type: Literal["text", "code", "workflow", "diagram", "table", "list", "section"] = "text"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    required: bool = False
    order: int = 0


class OrchestratorContext(BaseModel):
    """Context information for orchestrator decision making."""
    user_intent: str
    document_type: Optional[str] = None
    domain: Optional[str] = None
    complexity_level: Literal["simple", "medium", "complex"] = "medium"
    time_constraints: Optional[str] = None
    quality_requirements: Literal["draft", "standard", "high"] = "standard"
    available_schemas: List[str] = Field(default_factory=list)
    previous_interactions: List[Dict[str, Any]] = Field(default_factory=list)


class OrchestratorResponse(BaseModel):
    """Response from the AI orchestrator."""
    recommended_schemas: List[str]  # Schema IDs
    reasoning: str
    confidence_score: float
    alternative_options: List[Dict[str, Any]] = Field(default_factory=list)
    processing_plan: Dict[str, Any] = Field(default_factory=dict)
    estimated_time: Optional[int] = None  # in seconds


class SearchResult(BaseModel):
    """Result from semantic search with relevance score."""
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float
    source_section: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)


class VectorDocument(BaseModel):
    """Document prepared for vector storage."""
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    chunks: List[Dict[str, Any]] = Field(default_factory=list)  # For chunked documents
    last_indexed: Optional[str] = None


class RAGQuery(BaseModel):
    """Query for RAG system."""
    question: str
    context_documents: List[str] = Field(default_factory=list)  # Document IDs to search in
    max_results: int = 5
    include_metadata: bool = True
    rerank_results: bool = True


class RAGResponse(BaseModel):
    """Response from RAG system."""
    answer: str
    sources: List[SearchResult] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    reasoning_chain: List[str] = Field(default_factory=list)  # How the answer was constructed
    processing_time: Optional[float] = None


class DocumentStructure(BaseModel):
    """Complete document structure with metadata, content, and analysis."""
    metadata: Metadata
    content: Content
    analysis: Optional[Analysis] = None
    applied_schema: Optional[str] = None  # ID of applied modular schema
    vector_document: Optional[VectorDocument] = None  # For RAG indexing
