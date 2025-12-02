#!/usr/bin/env python3
"""
Extraction Patterns for Janusz - Document-to-TOON Pipeline

Provides pattern-based extraction for best practices and examples.
"""

import logging
import re
from typing import List, Tuple

from .models import ExtractionItem

logger = logging.getLogger(__name__)


def extract_best_practices_and_examples(text: str, sections: List[dict]) -> Tuple[List[ExtractionItem], List[ExtractionItem]]:
    """
    Extract best practices and examples from text using pattern matching.

    Args:
        text: Full document text
        sections: List of section dictionaries with 'title', 'content', etc.

    Returns:
        Tuple of (best_practices, examples) lists
    """
    best_practices = []
    examples = []

    # Create mapping of section content to section IDs for reference
    section_map = {}
    for i, section in enumerate(sections):
        section_id = f"section_{i}"
        section_content = " ".join(section.get('content', []))
        section_map[section_id] = {
            'title': section.get('title', ''),
            'content': section_content
        }

    # Pattern 1: Section-based extraction
    for section_id, section_data in section_map.items():
        title_lower = section_data['title'].lower()
        content = section_data['content']

        # Best practices sections
        if any(keyword in title_lower for keyword in ['best practice', 'recommendation', 'guideline', 'dos and don\'ts']):
            items = _extract_items_from_section(content, 'best_practice', section_id)
            best_practices.extend(items)

        # Examples sections
        elif any(keyword in title_lower for keyword in ['example', 'sample', 'demo', 'usage']):
            items = _extract_items_from_section(content, 'example', section_id)
            examples.extend(items)

    # Pattern 2: Content-based extraction (paragraph-level patterns)
    lines = text.split('\n')
    current_section_id = None

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Track current section
        if re.match(r'^#{1,6}|\d+\.|\w+:$', line):
            current_section_id = f"section_{i}"

        # Best practices patterns
        if any(pattern in line_lower for pattern in [
            'recommend', 'should', 'must', 'always', 'never', 'avoid',
            'best practice', 'good practice', 'do not', 'don\'t'
        ]):
            # Extract the sentence or relevant context
            context = _extract_context(lines, i, 2)
            if context.strip():
                best_practices.append(ExtractionItem(
                    text=context.strip(),
                    source_section_id=current_section_id,
                    tags=['content_pattern'],
                    confidence_level='medium'
                ))

        # Examples patterns
        elif any(pattern in line_lower for pattern in [
            'for example', 'e.g.', 'such as', 'like this', 'sample',
            'here is', 'consider', 'imagine', 'suppose'
        ]):
            context = _extract_context(lines, i, 3)
            if context.strip():
                examples.append(ExtractionItem(
                    text=context.strip(),
                    source_section_id=current_section_id,
                    tags=['content_pattern'],
                    confidence_level='medium'
                ))

    return best_practices, examples


def _extract_items_from_section(content: str, item_type: str, section_id: str) -> List[ExtractionItem]:
    """Extract items from a section's content."""
    items = []

    # Split by bullets, numbers, or line breaks
    lines = content.split('\n')
    current_item = []
    confidence_level = 'high'  # Section-based extractions are high confidence

    for line in lines:
        line = line.strip()

        # Check for list items (bullets, numbers, dashes)
        if re.match(r'^[-*•]\s|^(\d+\.|\(\d+\))\s|^-\s', line):
            # Save previous item if exists
            if current_item:
                items.append(ExtractionItem(
                    text='\n'.join(current_item),
                    source_section_id=section_id,
                    tags=[item_type, 'section_based'],
                    confidence_level=confidence_level
                ))

            # Start new item
            current_item = [line]
        elif line and current_item:
            # Continue current item
            current_item.append(line)
        elif line and not current_item:
            # Single line item
            current_item = [line]

    # Save last item
    if current_item:
        items.append(ExtractionItem(
            text='\n'.join(current_item),
            source_section_id=section_id,
            tags=[item_type, 'section_based'],
            confidence_level=confidence_level
        ))

    return items


def _extract_context(lines: List[str], center_line: int, context_lines: int = 2) -> str:
    """Extract context around a line for pattern-based extractions."""
    start = max(0, center_line - context_lines)
    end = min(len(lines), center_line + context_lines + 1)

    context = []
    for i in range(start, end):
        line = lines[i].strip()
        if line:
            context.append(line)

    return '\n'.join(context)
