#!/usr/bin/env python3
"""
Data Models for Janusz - Document-to-TOON Pipeline

This module defines Pydantic models for structured data validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple

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


# Phase 5: Prompt Optimization Models

class PromptTemplate(BaseModel):
    """A template for LLM prompts with variables and metadata."""
    id: str
    name: str
    description: str
    template: str
    variables: List[str] = Field(default_factory=list)
    category: Literal["extraction", "generation", "analysis", "qa", "optimization", "coding", "writing", "custom"]
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    average_score: float = Field(ge=0.0, le=1.0, default=0.5)


class TestResult(BaseModel):
    """Result of a single prompt test."""
    prompt_id: str
    test_input: str
    expected_output: Optional[str] = None
    actual_output: str
    execution_time: float
    token_usage: int
    quality_score: float = Field(ge=0.0, le=1.0)
    metrics: Dict[str, float] = Field(default_factory=dict)  # accuracy, coherence, relevance, etc.
    feedback: Optional[str] = None


class OptimizationResult(BaseModel):
    """Result of prompt optimization."""
    original_prompt: str
    optimized_prompt: str
    improvement_score: float = Field(ge=0.0, le=1.0)
    optimization_steps: List[str] = Field(default_factory=list)
    test_results_before: List[TestResult] = Field(default_factory=list)
    test_results_after: List[TestResult] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class BenchmarkResult(BaseModel):
    """Comprehensive benchmark result for prompt evaluation."""
    prompt_id: str
    model_name: str
    test_dataset: str
    metrics: Dict[str, float] = Field(default_factory=dict)
    average_score: float = Field(ge=0.0, le=1.0)
    execution_time: float
    total_token_usage: int
    sample_size: int
    confidence_interval: Optional[Tuple[float, float]] = None
    comparison_baseline: Optional[str] = None
    improvement_percentage: Optional[float] = None


class PromptOptimizationRequest(BaseModel):
    """Request for prompt optimization."""
    text: str
    context: Optional[str] = None
    target_model: str = "anthropic/claude-3-haiku"
    optimization_goal: Literal["clarity", "efficiency", "specificity", "creativity", "conciseness", "comprehensiveness"]
    constraints: List[str] = Field(default_factory=list)
    test_cases: List[Dict[str, str]] = Field(default_factory=list)


class AdvancedSearchFilters(BaseModel):
    """Advanced filters for RAG search."""
    categories: List[str] = Field(default_factory=list)
    date_range: Optional[Tuple[str, str]] = None
    authors: List[str] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=list)
    source_types: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    min_score: float = 0.0
    max_results: int = 10
    include_metadata: bool = True
