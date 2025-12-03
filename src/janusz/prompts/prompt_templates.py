#!/usr/bin/env python3
"""
Prompt Templates Library for Janusz

This module provides a comprehensive library of prompt templates
for various use cases and domains.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import PromptTemplate

logger = logging.getLogger(__name__)


class PromptLibrary:
    """
    Manages a library of prompt templates with search, import/export functionality.

    Provides pre-built templates for common use cases and allows custom template management.
    """

    def __init__(self, library_path: str = "prompts"):
        self.library_path = Path(library_path)
        self.library_path.mkdir(exist_ok=True)
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_library()

        # Initialize with default templates if library is empty
        if not self.templates:
            self._initialize_default_templates()

    def _load_library(self):
        """Load templates from disk."""
        for template_file in self.library_path.glob("*.json"):
            try:
                with open(template_file, encoding='utf-8') as f:
                    data = json.load(f)
                    template = PromptTemplate(**data)
                    self.templates[template.id] = template
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

        logger.info(f"Loaded {len(self.templates)} prompt templates")

    def _save_template(self, template: PromptTemplate):
        """Save a single template to disk."""
        template_file = self.library_path / f"{template.id}.json"
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template.model_dump(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save template {template.id}: {e}")

    def _initialize_default_templates(self):
        """Initialize library with default templates."""
        default_templates = [
            PromptTemplate(
                id="extraction_technical",
                name="Technical Documentation Extraction",
                description="Extract technical information, code examples, and best practices from documentation",
                template="""Analyze the following technical documentation and extract:

1. **Key Concepts**: Main ideas, technologies, or frameworks mentioned
2. **Code Examples**: Any code snippets, commands, or configurations
3. **Best Practices**: Recommended approaches, guidelines, or standards
4. **Requirements**: Prerequisites, dependencies, or system requirements
5. **Implementation Details**: Step-by-step instructions or procedures

Document Text:
---
{text}
---

Provide a structured summary with clear sections and actionable information.""",
                variables=["text"],
                category="extraction",
                tags=["technical", "documentation", "code", "best-practices"],
                author="Janusz System",
            ),

            PromptTemplate(
                id="qa_comprehensive",
                name="Comprehensive Q&A",
                description="Provide detailed, well-structured answers to complex questions",
                template="""Please provide a comprehensive answer to the following question:

**Question**: {question}

**Context** (if provided):
{context}

**Answer Structure**:
1. **Direct Answer**: Clear, concise response to the question
2. **Explanation**: Detailed explanation with reasoning
3. **Evidence**: Supporting facts, examples, or data
4. **Considerations**: Important caveats, limitations, or context
5. **Related Information**: Additional relevant details or connections

Ensure the answer is accurate, well-structured, and directly addresses the question.""",
                variables=["question", "context"],
                category="qa",
                tags=["comprehensive", "structured", "evidence-based"],
                author="Janusz System",
            ),

            PromptTemplate(
                id="analysis_code_review",
                name="Code Review Analysis",
                description="Analyze code for quality, security, and best practices",
                template="""Perform a comprehensive code review of the following code:

```code
{code}
```

**Review Focus Areas**:

1. **Functionality**: Does the code work as intended?
2. **Code Quality**: Readability, maintainability, documentation
3. **Security**: Potential vulnerabilities or security issues
4. **Performance**: Efficiency, optimization opportunities
5. **Best Practices**: Adherence to language/framework conventions
6. **Error Handling**: Robustness and error management
7. **Testing**: Testability and test coverage considerations

**Recommendations**: Provide specific, actionable suggestions for improvement.

**Severity Levels**: High/Medium/Low priority issues.""",
                variables=["code"],
                category="analysis",
                tags=["code-review", "security", "quality", "best-practices"],
                author="Janusz System",
            ),

            PromptTemplate(
                id="generation_api_docs",
                name="API Documentation Generation",
                description="Generate comprehensive API documentation from code or specifications",
                template="""Generate comprehensive API documentation for the following {api_type}:

**API Details**:
{api_specification}

**Documentation Structure**:

### Overview
- **Purpose**: What does this API do?
- **Authentication**: Required authentication methods
- **Base URL**: Primary endpoint URL

### Endpoints

For each endpoint, document:

#### `{method} {path}`
**Description**: What does this endpoint do?

**Parameters**:
- **Path Parameters**: URL path variables
- **Query Parameters**: Optional query string parameters
- **Request Body**: JSON schema or format description
- **Headers**: Required or optional headers

**Response**:
- **Success Response**: HTTP status codes and response format
- **Error Responses**: Error conditions and error response format

**Example Request**:
```
{example_request}
```

**Example Response**:
```json
{example_response}
```

### Error Handling
- Common error scenarios
- Error response format
- Troubleshooting tips

### Usage Examples
- Code examples in multiple languages
- Common use cases and workflows

Ensure the documentation is clear, comprehensive, and developer-friendly.""",
                variables=["api_type", "api_specification", "example_request", "example_response"],
                category="generation",
                tags=["api", "documentation", "rest", "developer-tools"],
                author="Janusz System",
            ),

            PromptTemplate(
                id="optimization_prompt_clarity",
                name="Prompt Clarity Optimization",
                description="Optimize prompts for maximum clarity and understandability",
                template="""Analyze and optimize the following prompt for maximum clarity:

**Original Prompt**:
{prompt}

**Optimization Goals**:
1. **Clear Language**: Use unambiguous, straightforward language
2. **Logical Structure**: Organize information in a logical flow
3. **Specific Instructions**: Provide concrete, actionable guidance
4. **Context Setting**: Ensure sufficient context is provided
5. **Success Criteria**: Define clear success metrics

**Optimized Version**:

[Provide a rewritten version of the prompt that significantly improves clarity while maintaining the original intent]

**Key Improvements Made**:
- List the specific changes and why they improve clarity
- Explain how the optimized version addresses potential misunderstandings
- Note any assumptions that were clarified or removed

**Testing Recommendations**:
- Suggest how to test the optimized prompt's effectiveness""",
                variables=["prompt"],
                category="optimization",
                tags=["clarity", "prompt-engineering", "communication"],
                author="Janusz System",
            ),

            PromptTemplate(
                id="writing_technical_blog",
                name="Technical Blog Post",
                description="Write engaging technical blog posts with proper structure",
                template="""Write a comprehensive technical blog post about: {topic}

**Article Structure**:

### Title
Create an engaging, SEO-friendly title that captures the main topic

### Introduction
- Hook the reader with a relevant problem or question
- Provide context and background
- State the article's main objective
- Preview what readers will learn

### Main Content

#### Section 1: Understanding the Problem
- Explain the technical challenge or concept
- Provide real-world context or use cases
- Include relevant background information

#### Section 2: Technical Deep Dive
- Break down complex concepts into digestible parts
- Include code examples, diagrams, or illustrations
- Explain implementation details
- Discuss trade-offs and considerations

#### Section 3: Best Practices & Implementation
- Provide practical guidance
- Include code snippets with explanations
- Discuss common pitfalls and how to avoid them
- Offer performance optimization tips

### Conclusion
- Summarize key takeaways
- Provide next steps or further reading
- Call to action (comments, questions, social sharing)

### References & Resources
- Link to official documentation
- Cite research papers or articles
- Provide additional learning resources

**Writing Guidelines**:
- Use clear, accessible language for developers
- Include practical code examples
- Maintain technical accuracy
- Structure content for scannability (headings, lists, code blocks)
- Keep sections focused and actionable

**Target Audience**: {audience_level} developers
**Word Count Goal**: {word_count}
**Key Takeaways**: {key_points}""",
                variables=["topic", "audience_level", "word_count", "key_points"],
                category="writing",
                tags=["blog", "technical-writing", "education", "content-creation"],
                author="Janusz System",
            ),
        ]

        for template in default_templates:
            self.templates[template.id] = template
            self._save_template(template)

        logger.info(f"Initialized library with {len(default_templates)} default templates")

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[PromptTemplate]:
        """List templates, optionally filtered by category and tags."""
        templates = list(self.templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]

        return sorted(templates, key=lambda t: t.name)

    def search_templates(self, query: str, limit: int = 10) -> List[PromptTemplate]:
        """Search templates by name, description, or tags."""
        query_lower = query.lower()
        matches = []

        for template in self.templates.values():
            score = 0

            # Name match (highest weight)
            if query_lower in template.name.lower():
                score += 10

            # Description match
            if query_lower in template.description.lower():
                score += 5

            # Tag matches
            for tag in template.tags:
                if query_lower in tag.lower():
                    score += 3

            # Category match
            if query_lower in template.category.lower():
                score += 2

            if score > 0:
                matches.append((template, score))

        # Sort by score and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [template for template, score in matches[:limit]]

    def add_template(self, template: PromptTemplate) -> bool:
        """Add a new template to the library."""
        if template.id in self.templates:
            logger.warning(f"Template {template.id} already exists")
            return False

        template.created_at = datetime.now().isoformat()
        template.updated_at = datetime.now().isoformat()

        self.templates[template.id] = template
        self._save_template(template)

        logger.info(f"Added template: {template.name} ({template.id})")
        return True

    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing template."""
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} not found")
            return False

        template = self.templates[template_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now().isoformat()

        self._save_template(template)
        logger.info(f"Updated template: {template_id}")
        return True

    def delete_template(self, template_id: str) -> bool:
        """Delete a template from the library."""
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} not found")
            return False

        # Remove from memory
        del self.templates[template_id]

        # Remove from disk
        template_file = self.library_path / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()

        logger.info(f"Deleted template: {template_id}")
        return True

    def export_library(self, output_path: str):
        """Export entire library to a JSON file."""
        output_file = Path(output_path)

        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "template_count": len(self.templates),
                "version": "1.0"
            },
            "templates": [template.model_dump() for template in self.templates.values()]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self.templates)} templates to {output_path}")

    def import_library(self, input_path: str, overwrite: bool = False) -> int:
        """Import templates from a JSON file."""
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Import file not found: {input_path}")

        with open(input_file, encoding='utf-8') as f:
            import_data = json.load(f)

        imported_count = 0

        for template_data in import_data.get("templates", []):
            try:
                template = PromptTemplate(**template_data)

                if template.id in self.templates and not overwrite:
                    logger.warning(f"Template {template.id} already exists, skipping (use overwrite=True)")
                    continue

                self.templates[template.id] = template
                self._save_template(template)
                imported_count += 1

            except Exception as e:
                logger.error(f"Failed to import template: {e}")

        logger.info(f"Imported {imported_count} templates from {input_path}")
        return imported_count

    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about the template library."""
        categories = {}
        tags = {}

        for template in self.templates.values():
            # Category stats
            categories[template.category] = categories.get(template.category, 0) + 1

            # Tag stats
            for tag in template.tags:
                tags[tag] = tags.get(tag, 0) + 1

        return {
            "total_templates": len(self.templates),
            "categories": categories,
            "tags": dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)),
            "most_used": sorted(self.templates.values(),
                              key=lambda t: t.usage_count, reverse=True)[:5],
            "highest_rated": sorted(self.templates.values(),
                                  key=lambda t: t.average_score, reverse=True)[:5],
        }

    def record_usage(self, template_id: str, score: Optional[float] = None):
        """Record usage of a template and optionally update its score."""
        if template_id in self.templates:
            template = self.templates[template_id]
            template.usage_count += 1

            if score is not None:
                # Simple moving average update
                template.average_score = (template.average_score + score) / 2
                template.updated_at = datetime.now().isoformat()

            self._save_template(template)
