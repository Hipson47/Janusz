#!/usr/bin/env python3
"""
Janusz RAG Demo Script

Demonstrates the RAG (Retrieval-Augmented Generation) capabilities
of the Janusz document processing system.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def demo_rag_system():
    """Demonstrate RAG system capabilities."""

    print("🧠 Janusz RAG System Demo")
    print("=" * 50)

    try:
        from janusz.rag.rag_system import RAGSystem
        from janusz.converter import UniversalToYAMLConverter
        from janusz.models import DocumentStructure

        # Initialize RAG system
        print("🔧 Initializing RAG system...")
        rag_system = RAGSystem()
        print("✅ RAG system ready")

        # Create sample document
        sample_content = """
        # FastAPI Security Best Practices

        ## Authentication Methods

        FastAPI supports several authentication methods:

        1. **JWT (JSON Web Tokens)**: Stateless authentication using signed tokens
        2. **OAuth2**: Industry-standard authorization framework
        3. **API Keys**: Simple key-based authentication for APIs
        4. **HTTP Basic Auth**: Username/password authentication

        ## JWT Implementation

        To implement JWT authentication in FastAPI:

        - Use `python-jose` library for token operations
        - Create access tokens with expiration time
        - Validate tokens on protected endpoints
        - Implement refresh token rotation

        ## Security Headers

        Always implement security headers:

        - `X-Content-Type-Options: nosniff`
        - `X-Frame-Options: DENY`
        - `X-XSS-Protection: 1; mode=block`
        - `Strict-Transport-Security`

        ## Best Practices

        1. Use HTTPS in production
        2. Validate all input data
        3. Implement rate limiting
        4. Log security events
        5. Keep dependencies updated
        """

        print("\n📄 Creating sample document...")

        # Create temporary file
        temp_file = Path("temp_security_guide.md")
        temp_file.write_text(sample_content)

        try:
            # Convert to document structure
            converter = UniversalToYAMLConverter(str(temp_file))
            doc_structure = converter.parse_text_structure(sample_content)

            # Index document in RAG
            print("🗂️ Indexing document for RAG...")
            doc_id = rag_system.add_document(doc_structure)
            print(f"✅ Document indexed with ID: {doc_id}")

            # Demonstrate queries
            queries = [
                "How do I implement JWT authentication in FastAPI?",
                "What security headers should I implement?",
                "What are the best practices for FastAPI security?",
                "How does OAuth2 work in FastAPI?"
            ]

            print("\n❓ Testing RAG queries:")
            print("-" * 30)

            for i, query in enumerate(queries, 1):
                print(f"\n{i}. Question: {query}")
                try:
                    response = rag_system.query(query, max_results=3)
                    print(".1f"                    print(f"   Answer preview: {response.answer[:100]}...")
                    print(f"   Sources: {len(response.sources)}")
                except Exception as e:
                    print(f"   ❌ Query failed: {e}")

            # Show statistics
            print("
📊 RAG System Statistics:"            stats = rag_system.get_statistics()
            for key, value in stats.items():
                print(f"  • {key}: {value}")

        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("RAG dependencies may not be installed.")
        print("Install with: uv sync --all-extras")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 RAG Demo completed!")

def demo_cli_commands():
    """Show CLI commands for RAG."""
    print("\n💻 CLI Commands for RAG:")
    print("-" * 30)
    print("# Index a document")
    print("janusz rag index --file document.yaml")
    print()
    print("# Ask questions")
    print('janusz rag query "How does authentication work?"')
    print()
    print("# View statistics")
    print("janusz rag stats")
    print()
    print("# Clear index")
    print("janusz rag clear")

if __name__ == "__main__":
    demo_rag_system()
    demo_cli_commands()
