"""
Pytest configuration and fixtures for Janusz tests.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_markdown_content():
    """Sample Markdown content for testing."""
    return """# Sample Document

This is a sample document for testing the conversion pipeline.

## Best Practices

- Always test your code
- Use meaningful variable names
- Write documentation

## Examples

Here's an example of how to use the API:

```python
converter = UniversalToYAMLConverter("document.md")
converter.convert_to_yaml()
```
"""


@pytest.fixture
def sample_yaml_data():
    """Sample YAML data structure for testing."""
    return {
        "metadata": {
            "title": "Test Document",
            "source": "test.md",
            "source_type": "markdown",
            "converted_by": "Universal Document to YAML Converter",
            "format_version": "2.0",
        },
        "content": {
            "sections": [
                {
                    "title": "# Introduction",
                    "content": ["This is an introduction."],
                    "subsections": [],
                }
            ],
            "raw_text": "# Introduction\n\nThis is an introduction.",
        },
        "analysis": {
            "keywords": ["Introduction"],
            "patterns": [],
            "best_practices": [],
            "examples": [],
        },
    }
