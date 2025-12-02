#!/usr/bin/env python3
"""
AI Content Analyzer for Janusz - Document-to-TOON Pipeline

This module provides AI-powered content analysis using OpenRouter API.
Enhances document understanding with LLM capabilities for better extraction
of insights, summaries, and quality assessments.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
import httpx

from ..models import (
    AIInsight, AIExtractionResult, ExtractionItem,
    DocumentStructure, Section
)

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Exception raised when OpenRouter API calls fail."""
    pass


class OpenRouterClient:
    """Client for OpenRouter API integration."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-3-haiku"):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If None, reads from JANUSZ_OPENROUTER_API_KEY env var
            model: Default model to use for analysis
        """
        self.api_key = api_key or os.getenv("JANUSZ_OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set JANUSZ_OPENROUTER_API_KEY environment variable.")

        self.model = model
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/janusz",  # Replace with actual repo
                "X-Title": "Janusz AI Document Processor"
            },
            timeout=60.0
        )

    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """Make a chat completion request to OpenRouter."""
        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }

        try:
            response = self.client.post("/chat/completions", json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise OpenRouterError(f"API request failed: {e}") from e

    def __del__(self):
        """Clean up HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()


class AIContentAnalyzer:
    """
    AI-powered content analyzer using OpenRouter API.

    Provides intelligent analysis of documents including:
    - Context-aware extraction of best practices
    - Quality assessment and improvement suggestions
    - Automated summarization
    - Insight generation
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "anthropic/claude-3-haiku",
                 enable_cache: bool = True):
        """
        Initialize AI Content Analyzer.

        Args:
            api_key: OpenRouter API key
            model: Model to use for analysis
            enable_cache: Whether to cache API responses
        """
        self.client = OpenRouterClient(api_key=api_key, model=model)
        self.enable_cache = enable_cache
        self._response_cache = {} if enable_cache else None
        self.model_used = model

    def analyze_document(self, document: DocumentStructure) -> AIExtractionResult:
        """
        Perform comprehensive AI analysis of a document.

        Args:
            document: DocumentStructure to analyze

        Returns:
            AIExtractionResult with enhanced analysis
        """
        start_time = time.time()

        try:
            # Extract text content for analysis
            full_text = document.content.raw_text
            sections = document.content.sections

            # Perform AI analysis
            ai_insights = self._extract_insights(full_text, sections)
            ai_best_practices = self._extract_best_practices_ai(full_text, sections)
            ai_examples = self._extract_examples_ai(full_text, sections)
            ai_summary = self._generate_summary(full_text)

            # Calculate quality score
            quality_score = self._assess_quality(document, ai_insights)

            processing_time = time.time() - start_time

            return AIExtractionResult(
                best_practices=ai_best_practices,
                examples=ai_examples,
                insights=ai_insights,
                summary=ai_summary,
                quality_score=quality_score,
                ai_model_used=self.model_used,
                processing_time_seconds=processing_time
            )

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return minimal result on failure
            return AIExtractionResult(
                ai_model_used=self.model_used,
                processing_time_seconds=time.time() - start_time
            )

    def _extract_insights(self, text: str, sections: List[Section]) -> List[AIInsight]:
        """Extract AI insights from document content."""
        if len(text) < 100:
            return []

        prompt = f"""
        Analyze this technical document and provide insights that would be valuable for developers and engineers.
        Focus on: best practices, potential improvements, warnings about common mistakes, and clarifications.

        Document content (first 2000 characters):
        {text[:2000]}

        Provide insights in JSON format:
        {{
            "insights": [
                {{
                    "text": "insight description",
                    "insight_type": "improvement|warning|enhancement|clarification",
                    "confidence_score": 0.0-1.0,
                    "reasoning": "why this insight is valuable",
                    "tags": ["tag1", "tag2"]
                }}
            ]
        }}
        """

        try:
            response = self.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=1500)

            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            insights = []
            for insight_data in parsed.get("insights", []):
                insight = AIInsight(**insight_data)
                insights.append(insight)

            return insights[:10]  # Limit to top 10 insights

        except (json.JSONDecodeError, KeyError, OpenRouterError) as e:
            logger.warning(f"Failed to extract AI insights: {e}")
            return []

    def _extract_best_practices_ai(self, text: str, sections: List[Section]) -> List[ExtractionItem]:
        """AI-powered extraction of best practices."""
        prompt = f"""
        Extract best practices and recommendations from this technical document.
        Focus on actionable advice that developers should follow.

        Document content:
        {text[:3000]}

        Return in JSON format:
        {{
            "best_practices": [
                {{
                    "text": "best practice description",
                    "tags": ["category1", "category2"],
                    "confidence_level": "high|medium|low"
                }}
            ]
        }}
        """

        try:
            response = self.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=1200)

            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            practices = []
            for practice_data in parsed.get("best_practices", []):
                practice = ExtractionItem(**practice_data)
                practices.append(practice)

            return practices[:15]  # Limit results

        except (json.JSONDecodeError, KeyError, OpenRouterError) as e:
            logger.warning(f"Failed to extract AI best practices: {e}")
            return []

    def _extract_examples_ai(self, text: str, sections: List[Section]) -> List[ExtractionItem]:
        """AI-powered extraction of examples."""
        prompt = f"""
        Extract practical examples and code samples from this technical document.
        Focus on concrete examples that developers can learn from.

        Document content:
        {text[:3000]}

        Return in JSON format:
        {{
            "examples": [
                {{
                    "text": "example description with any code",
                    "tags": ["example", "code", "tutorial"],
                    "confidence_level": "high|medium|low"
                }}
            ]
        }}
        """

        try:
            response = self.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=1200)

            content = response["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            examples = []
            for example_data in parsed.get("examples", []):
                example = ExtractionItem(**example_data)
                examples.append(example)

            return examples[:15]  # Limit results

        except (json.JSONDecodeError, KeyError, OpenRouterError) as e:
            logger.warning(f"Failed to extract AI examples: {e}")
            return []

    def _generate_summary(self, text: str) -> Optional[str]:
        """Generate AI summary of the document."""
        if len(text) < 200:
            return None

        prompt = f"""
        Provide a concise but comprehensive summary of this technical document.
        Focus on the main topics, key takeaways, and purpose of the document.

        Document content (first 1500 characters):
        {text[:1500]}

        Summary (2-3 sentences):
        """

        try:
            response = self.client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=300)

            summary = response["choices"][0]["message"]["content"].strip()
            return summary if len(summary) > 20 else None

        except OpenRouterError as e:
            logger.warning(f"Failed to generate AI summary: {e}")
            return None

    def _assess_quality(self, document: DocumentStructure, insights: List[AIInsight]) -> float:
        """Assess overall quality score of the document."""
        # Simple heuristic-based scoring
        score = 0.5  # Base score

        # Factor in document length
        if len(document.content.raw_text) > 1000:
            score += 0.1
        elif len(document.content.raw_text) < 200:
            score -= 0.2

        # Factor in number of sections
        if len(document.content.sections) > 3:
            score += 0.1
        elif len(document.content.sections) == 0:
            score -= 0.2

        # Factor in AI insights quality
        if len(insights) > 5:
            score += 0.2
        elif len(insights) == 0:
            score -= 0.1

        # Factor in metadata completeness
        metadata_complete = all([
            document.metadata.title,
            document.metadata.source,
            document.metadata.source_type
        ])
        if metadata_complete:
            score += 0.1

        return max(0.0, min(1.0, score))  # Clamp to 0-1 range

    def get_available_models(self) -> List[str]:
        """Get list of available models from OpenRouter."""
        try:
            response = self.client.client.get("/models")
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
        except Exception as e:
            logger.error(f"Failed to fetch available models: {e}")
            return ["anthropic/claude-3-haiku", "openai/gpt-4", "meta-llama/llama-2-70b-chat"]


# Import here to avoid circular imports
import os
