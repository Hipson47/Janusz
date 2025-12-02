#!/usr/bin/env python3
"""
Janusz GUI Demo Script

This script demonstrates how to use the Janusz GUI programmatically.
It creates sample documents and shows how the GUI would process them.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_sample_documents():
    """Create sample documents for GUI demonstration."""

    # Create sample directory if it doesn't exist
    sample_dir = Path("examples/sample_docs")
    sample_dir.mkdir(exist_ok=True)

    # Sample Markdown document
    md_content = """# AI-Powered Document Processing

## Overview

This document demonstrates the capabilities of Janusz AI-powered document processing system.

## Key Features

- **Intelligent Analysis**: AI-powered extraction of insights and best practices
- **Multiple Formats**: Support for PDF, Markdown, DOCX, HTML, and plain text
- **Quality Assessment**: Automated quality scoring and improvement suggestions
- **Modular Architecture**: Extensible design for custom processing pipelines

## Best Practices

1. Always validate input data before processing
2. Use appropriate AI models for different document types
3. Implement proper error handling and logging
4. Consider performance implications of AI processing

## Examples

Here's an example of how to configure AI processing:

```python
from janusz.ai.ai_content_analyzer import AIContentAnalyzer

analyzer = AIContentAnalyzer(
    api_key="your-openrouter-key",
    model="anthropic/claude-3-haiku"
)

results = analyzer.analyze_document(document)
```

## Conclusion

AI-powered document processing enables more intelligent and efficient knowledge extraction from technical documentation.
"""

    # Sample technical documentation
    tech_content = """# FastAPI Security Best Practices

## Authentication & Authorization

### JWT Token Implementation

When implementing JWT tokens in FastAPI:

1. Use proper secret keys (minimum 256 bits)
2. Implement token expiration
3. Validate token signatures on every request
4. Store refresh tokens securely

### OAuth2 Integration

For OAuth2 integration:
- Use established libraries like `authlib`
- Implement proper state parameter validation
- Handle token refresh automatically
- Log authentication failures

## Input Validation

### Pydantic Models

Always use Pydantic models for input validation:

```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v
```

### SQL Injection Prevention

- Use parameterized queries
- Implement proper escaping
- Use ORMs like SQLAlchemy
- Validate all input data

## Error Handling

### Custom Exception Handlers

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "details": str(exc)}
    )
```

## Security Headers

Always implement security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`

## Conclusion

Security should be implemented at every layer of your FastAPI application.
"""

    # Write sample files
    with open(sample_dir / "ai_overview.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(sample_dir / "fastapi_security.md", "w", encoding="utf-8") as f:
        f.write(tech_content)

    print(f"✅ Created sample documents in {sample_dir}")
    return sample_dir

def demo_gui_features():
    """Demonstrate GUI features programmatically."""

    print("🚀 Janusz GUI Demo")
    print("=" * 50)

    # Create sample documents
    sample_dir = create_sample_documents()

    print("\n📁 Available documents:")
    for file_path in sample_dir.glob("*.md"):
        size = file_path.stat().st_size
        print(f"  • {file_path.name} ({size} bytes)")

    print("\n🎯 GUI Features:")
    print("  • File selection from knowledge base")
    print("  • Format conversion (YAML/JSON/TOON)")
    print("  • AI-powered analysis")
    print("  • Progress tracking")
    print("  • Batch processing")

    print("\n🤖 AI Features (when enabled):")
    print("  • Best practices extraction")
    print("  • Quality assessment")
    print("  • Automated summaries")
    print("  • RAG-powered Q&A system")

    print("\n🔍 RAG Features:")
    print("  • Natural language queries")
    print("  • Semantic search across documents")
    print("  • AI-generated answers with citations")
    print("  • Confidence scoring")
    print("  • Source validation")
    print("  • Improvement suggestions")

    print("\n📊 To run the GUI:")
    print("  janusz gui")
    print("  # or")
    print("  python scripts/gui.py")

    print("\n⚠️  Note: GUI requires tkinter")
    print("  Install on Ubuntu: sudo apt-get install python3-tk")

    return sample_dir

if __name__ == "__main__":
    demo_gui_features()
