#!/usr/bin/env python3
"""
Schema Manager for Janusz Modular Schema System

Manages creation, storage, retrieval, and application of modular document schemas.
Provides AI-powered schema generation and intelligent matching.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import ModularSchema, SchemaComponent, DocumentStructure
from ..ai.ai_content_analyzer import AIContentAnalyzer

logger = logging.getLogger(__name__)


class SchemaManager:
    """
    Manages modular schemas for document processing.

    Provides functionality for:
    - Schema creation and storage
    - Schema retrieval and matching
    - Schema application to documents
    - AI-powered schema generation
    """

    def __init__(self, schema_dir: str = "schemas", ai_analyzer: Optional[AIContentAnalyzer] = None):
        """
        Initialize Schema Manager.

        Args:
            schema_dir: Directory to store schema files
            ai_analyzer: Optional AI analyzer for schema generation
        """
        self.schema_dir = Path(schema_dir)
        self.schema_dir.mkdir(exist_ok=True)
        self.ai_analyzer = ai_analyzer
        self._schemas_cache: Dict[str, ModularSchema] = {}
        self._load_schemas()

    def _load_schemas(self):
        """Load all available schemas from disk."""
        self._schemas_cache.clear()

        for schema_file in self.schema_dir.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    schema = ModularSchema(**schema_data)
                    self._schemas_cache[schema.id] = schema
            except Exception as e:
                logger.warning(f"Failed to load schema {schema_file}: {e}")

        logger.info(f"Loaded {len(self._schemas_cache)} schemas")

    def get_schema(self, schema_id: str) -> Optional[ModularSchema]:
        """Get a schema by ID."""
        return self._schemas_cache.get(schema_id)

    def list_schemas(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[ModularSchema]:
        """List available schemas with optional filtering."""
        schemas = list(self._schemas_cache.values())

        if category:
            schemas = [s for s in schemas if s.category == category]

        if tags:
            schemas = [s for s in schemas if any(tag in s.tags for tag in tags)]

        return sorted(schemas, key=lambda s: s.usage_count, reverse=True)

    def save_schema(self, schema: ModularSchema):
        """Save a schema to disk."""
        schema_file = self.schema_dir / f"{schema.id}.json"

        try:
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema.model_dump(), f, indent=2, ensure_ascii=False)

            self._schemas_cache[schema.id] = schema
            logger.info(f"Saved schema: {schema.name} ({schema.id})")

        except Exception as e:
            logger.error(f"Failed to save schema {schema.id}: {e}")
            raise

    def create_schema_from_document(self, document: DocumentStructure,
                                  name: str, description: str,
                                  category: str = "technical") -> ModularSchema:
        """
        Create a modular schema from an existing document.

        Args:
            document: Document to analyze for schema creation
            name: Human-readable name for the schema
            description: Description of when to use this schema
            category: Schema category

        Returns:
            Newly created modular schema
        """
        schema_id = f"schema_{int(datetime.now().timestamp())}"

        # Extract components from document
        components = self._extract_components_from_document(document)

        # Generate tags based on content
        tags = self._generate_tags_from_document(document)

        schema = ModularSchema(
            id=schema_id,
            name=name,
            description=description,
            category=category,
            tags=tags,
            components=components,
            ai_generated=False,
            confidence_score=0.8,
            usage_count=0
        )

        self.save_schema(schema)
        return schema

    def generate_ai_schema(self, prompt: str, category: str = "technical") -> ModularSchema:
        """
        Generate a new schema using AI based on a natural language prompt.

        Args:
            prompt: Natural language description of the desired schema
            category: Schema category

        Returns:
            AI-generated modular schema
        """
        if not self.ai_analyzer:
            raise ValueError("AI analyzer not available for schema generation")

        # Use AI to generate schema structure
        ai_prompt = f"""
        Create a modular schema for document processing based on this description:

        {prompt}

        Generate a JSON schema with the following structure:
        {{
            "name": "schema name",
            "description": "when to use this schema",
            "category": "{category}",
            "tags": ["relevant", "tags"],
            "components": [
                {{
                    "type": "text|code|workflow|diagram|table|list|section",
                    "content": "description or template",
                    "metadata": {{"key": "value"}},
                    "required": true|false,
                    "order": 0
                }}
            ]
        }}

        Make the schema practical and reusable for document processing.
        """

        try:
            response = self.ai_analyzer.client.chat_completion([
                {"role": "user", "content": ai_prompt}
            ], max_tokens=1000)

            content = response["choices"][0]["message"]["content"]

            # Parse AI response
            schema_data = json.loads(content)
            schema_data["id"] = f"ai_schema_{int(datetime.now().timestamp())}"
            schema_data["ai_generated"] = True
            schema_data["ai_model_used"] = self.ai_analyzer.model_used
            schema_data["confidence_score"] = 0.7  # AI-generated, slightly lower confidence

            schema = ModularSchema(**schema_data)
            self.save_schema(schema)

            logger.info(f"Generated AI schema: {schema.name}")
            return schema

        except Exception as e:
            logger.error(f"Failed to generate AI schema: {e}")
            raise

    def find_matching_schemas(self, document: DocumentStructure,
                            limit: int = 5) -> List[ModularSchema]:
        """
        Find schemas that match a given document.

        Args:
            document: Document to find matching schemas for
            limit: Maximum number of schemas to return

        Returns:
            List of matching schemas sorted by relevance
        """
        document_tags = self._generate_tags_from_document(document)
        document_category = self._infer_document_category(document)

        candidates = []

        for schema in self._schemas_cache.values():
            score = self._calculate_schema_match_score(schema, document_tags, document_category)
            if score > 0.3:  # Minimum threshold
                candidates.append((schema, score))

        # Sort by score and return top matches
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [schema for schema, score in candidates[:limit]]

    def apply_schema_to_document(self, document: DocumentStructure,
                               schema_id: str) -> DocumentStructure:
        """
        Apply a modular schema to a document structure.

        Args:
            document: Document to apply schema to
            schema_id: ID of schema to apply

        Returns:
            Document with applied schema metadata
        """
        schema = self.get_schema(schema_id)
        if not schema:
            raise ValueError(f"Schema {schema_id} not found")

        # Update document metadata
        document.applied_schema = schema_id

        # Increment usage count
        schema.usage_count += 1
        self.save_schema(schema)

        logger.info(f"Applied schema '{schema.name}' to document")
        return document

    def _extract_components_from_document(self, document: DocumentStructure) -> List[Dict[str, Any]]:
        """Extract schema components from a document."""
        components = []

        # Extract from sections
        for i, section in enumerate(document.content.sections):
            component = {
                "type": "section",
                "content": f"Section with title pattern: {section.title[:50]}...",
                "metadata": {
                    "level": section.level,
                    "has_subsections": len(section.subsections) > 0
                },
                "required": i < 3,  # First 3 sections are likely required
                "order": i
            }
            components.append(component)

        # Extract from analysis if available
        if document.analysis and document.analysis.best_practices:
            component = {
                "type": "list",
                "content": "Best practices checklist",
                "metadata": {"item_count": len(document.analysis.best_practices)},
                "required": False,
                "order": len(components)
            }
            components.append(component)

        return components

    def _generate_tags_from_document(self, document: DocumentStructure) -> List[str]:
        """Generate relevant tags from document content."""
        tags = []

        # Add category-based tags
        if "api" in document.metadata.title.lower() or "api" in document.content.raw_text.lower():
            tags.extend(["api", "integration", "web"])
        if "security" in document.metadata.title.lower():
            tags.extend(["security", "best-practices", "compliance"])
        if "tutorial" in document.metadata.title.lower():
            tags.extend(["tutorial", "guide", "learning"])

        # Add keywords from analysis
        if document.analysis and document.analysis.keywords:
            keyword_tags = [kw.text.lower() for kw in document.analysis.keywords[:5]]
            tags.extend(keyword_tags)

        return list(set(tags))  # Remove duplicates

    def _infer_document_category(self, document: DocumentStructure) -> str:
        """Infer document category from content."""
        text = document.content.raw_text.lower()

        if any(word in text for word in ["api", "endpoint", "rest", "graphql"]):
            return "technical"
        elif any(word in text for word in ["process", "workflow", "procedure"]):
            return "process"
        elif any(word in text for word in ["tutorial", "guide", "learn"]):
            return "educational"
        else:
            return "technical"  # Default

    def _calculate_schema_match_score(self, schema: ModularSchema,
                                    document_tags: List[str],
                                    document_category: str) -> float:
        """Calculate how well a schema matches a document."""
        score = 0.0

        # Category match (high weight)
        if schema.category == document_category:
            score += 0.4

        # Tag overlap
        schema_tags = set(schema.tags)
        doc_tags = set(document_tags)
        tag_overlap = len(schema_tags.intersection(doc_tags))
        if tag_overlap > 0:
            score += min(0.4, tag_overlap * 0.1)

        # Usage bonus (popular schemas get slight preference)
        usage_bonus = min(0.1, schema.usage_count * 0.01)
        score += usage_bonus

        return score

    def delete_schema(self, schema_id: str):
        """Delete a schema."""
        if schema_id in self._schemas_cache:
            schema_file = self.schema_dir / f"{schema_id}.json"
            if schema_file.exists():
                schema_file.unlink()

            del self._schemas_cache[schema_id]
            logger.info(f"Deleted schema: {schema_id}")
        else:
            raise ValueError(f"Schema {schema_id} not found")

    def get_schema_stats(self) -> Dict[str, Any]:
        """Get statistics about available schemas."""
        if not self._schemas_cache:
            return {"total_schemas": 0}

        categories = {}
        total_usage = 0

        for schema in self._schemas_cache.values():
            categories[schema.category] = categories.get(schema.category, 0) + 1
            total_usage += schema.usage_count

        ai_generated = sum(1 for s in self._schemas_cache.values() if s.ai_generated)

        return {
            "total_schemas": len(self._schemas_cache),
            "categories": categories,
            "total_usage": total_usage,
            "ai_generated": ai_generated,
            "avg_usage": total_usage / len(self._schemas_cache)
        }
