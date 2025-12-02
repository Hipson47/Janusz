#!/usr/bin/env python3
"""
Create sample modular schemas for Janusz.

This script creates common document processing schemas that can be used
as templates for different types of technical documentation.
"""

import json
import os
from pathlib import Path

# Sample schemas
SAMPLE_SCHEMAS = [
    {
        "id": "api_documentation_schema",
        "name": "API Documentation",
        "description": "Standard schema for REST API documentation with endpoints, authentication, and examples",
        "category": "technical",
        "tags": ["api", "rest", "documentation", "endpoints"],
        "components": [
            {
                "type": "section",
                "content": "API Overview and Introduction",
                "metadata": {"level": 1, "required": True},
                "required": True,
                "order": 0
            },
            {
                "type": "section",
                "content": "Authentication and Authorization",
                "metadata": {"level": 1, "security_focus": True},
                "required": True,
                "order": 1
            },
            {
                "type": "section",
                "content": "API Endpoints Reference",
                "metadata": {"level": 1, "technical": True},
                "required": True,
                "order": 2
            },
            {
                "type": "section",
                "content": "Request/Response Examples",
                "metadata": {"level": 2, "examples": True},
                "required": False,
                "order": 3
            },
            {
                "type": "list",
                "content": "Common Error Codes and Handling",
                "metadata": {"error_handling": True},
                "required": True,
                "order": 4
            }
        ],
        "dependencies": [],
        "ai_generated": False,
        "confidence_score": 0.9,
        "created_at": "2025-12-02T20:00:00",
        "usage_count": 5
    },
    {
        "id": "security_best_practices_schema",
        "name": "Security Best Practices",
        "description": "Comprehensive security guidelines and best practices for application development",
        "category": "technical",
        "tags": ["security", "best-practices", "compliance", "risk-management"],
        "components": [
            {
                "type": "section",
                "content": "Security Overview and Threat Model",
                "metadata": {"level": 1, "threat_modeling": True},
                "required": True,
                "order": 0
            },
            {
                "type": "list",
                "content": "Authentication Best Practices",
                "metadata": {"authentication": True},
                "required": True,
                "order": 1
            },
            {
                "type": "list",
                "content": "Input Validation and Sanitization",
                "metadata": {"input_validation": True},
                "required": True,
                "order": 2
            },
            {
                "type": "section",
                "content": "Data Protection and Encryption",
                "metadata": {"level": 2, "encryption": True},
                "required": True,
                "order": 3
            },
            {
                "type": "list",
                "content": "Monitoring and Logging Recommendations",
                "metadata": {"monitoring": True},
                "required": False,
                "order": 4
            }
        ],
        "dependencies": [],
        "ai_generated": False,
        "confidence_score": 0.95,
        "created_at": "2025-12-02T20:00:00",
        "usage_count": 8
    },
    {
        "id": "tutorial_guide_schema",
        "name": "Tutorial and Learning Guide",
        "description": "Educational content schema for tutorials, guides, and learning materials",
        "category": "educational",
        "tags": ["tutorial", "guide", "learning", "education", "how-to"],
        "components": [
            {
                "type": "section",
                "content": "Introduction and Learning Objectives",
                "metadata": {"level": 1, "objectives": True},
                "required": True,
                "order": 0
            },
            {
                "type": "list",
                "content": "Prerequisites and Requirements",
                "metadata": {"prerequisites": True},
                "required": True,
                "order": 1
            },
            {
                "type": "section",
                "content": "Step-by-Step Instructions",
                "metadata": {"level": 1, "step_by_step": True},
                "required": True,
                "order": 2
            },
            {
                "type": "code",
                "content": "Code Examples and Samples",
                "metadata": {"examples": True, "code_samples": True},
                "required": False,
                "order": 3
            },
            {
                "type": "section",
                "content": "Troubleshooting and Common Issues",
                "metadata": {"level": 2, "troubleshooting": True},
                "required": False,
                "order": 4
            },
            {
                "type": "list",
                "content": "Next Steps and Further Reading",
                "metadata": {"next_steps": True},
                "required": True,
                "order": 5
            }
        ],
        "dependencies": [],
        "ai_generated": False,
        "confidence_score": 0.85,
        "created_at": "2025-12-02T20:00:00",
        "usage_count": 12
    },
    {
        "id": "deployment_guide_schema",
        "name": "Deployment and DevOps Guide",
        "description": "Schema for deployment guides, CI/CD pipelines, and infrastructure documentation",
        "category": "process",
        "tags": ["deployment", "devops", "ci-cd", "infrastructure", "docker", "kubernetes"],
        "components": [
            {
                "type": "section",
                "content": "Deployment Architecture Overview",
                "metadata": {"level": 1, "architecture": True},
                "required": True,
                "order": 0
            },
            {
                "type": "list",
                "content": "Prerequisites and Environment Setup",
                "metadata": {"prerequisites": True, "environment": True},
                "required": True,
                "order": 1
            },
            {
                "type": "section",
                "content": "Build and Packaging Process",
                "metadata": {"level": 2, "build": True},
                "required": True,
                "order": 2
            },
            {
                "type": "section",
                "content": "Deployment Steps and Procedures",
                "metadata": {"level": 1, "deployment": True},
                "required": True,
                "order": 3
            },
            {
                "type": "section",
                "content": "Monitoring and Maintenance",
                "metadata": {"level": 2, "monitoring": True},
                "required": False,
                "order": 4
            },
            {
                "type": "list",
                "content": "Rollback Procedures and Troubleshooting",
                "metadata": {"rollback": True, "troubleshooting": True},
                "required": True,
                "order": 5
            }
        ],
        "dependencies": [],
        "ai_generated": False,
        "confidence_score": 0.88,
        "created_at": "2025-12-02T20:00:00",
        "usage_count": 6
    }
]

def create_sample_schemas():
    """Create sample schemas in the schemas directory."""
    schemas_dir = Path("schemas")
    schemas_dir.mkdir(exist_ok=True)

    print("Creating sample schemas...")

    for schema in SAMPLE_SCHEMAS:
        schema_file = schemas_dir / f"{schema['id']}.json"

        try:
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)

            print(f"✅ Created schema: {schema['name']}")

        except Exception as e:
            print(f"❌ Failed to create schema {schema['id']}: {e}")

    print(f"\n🎉 Created {len(SAMPLE_SCHEMAS)} sample schemas in {schemas_dir}/")

def main():
    """Main function."""
    print("🚀 Janusz Sample Schema Creator")
    print("=" * 40)

    create_sample_schemas()

    print("\n📖 Available schemas:")
    for schema in SAMPLE_SCHEMAS:
        print(f"  • {schema['id']}: {schema['name']}")
        print(f"    {schema['description']}")
        print(f"    Category: {schema['category']}, Tags: {', '.join(schema['tags'])}")
        print()

    print("💡 To use schemas:")
    print("  janusz schema list")
    print("  janusz orchestrate 'Convert this API doc' --file document.md")
    print("  janusz orchestrate 'Create security guide' --use-ai")

if __name__ == "__main__":
    main()
