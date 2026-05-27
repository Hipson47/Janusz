#!/usr/bin/env python3
"""Minimal RAG example for Janusz experimental retrieval features.

RAG is not part of the stable 1.0 production surface. This example stays
executable and fails with an actionable message when optional dependencies or
embedding providers are not configured.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from janusz.converter import UniversalToYAMLConverter

SAMPLE_CONTENT = """# FastAPI Security Best Practices

## Authentication Methods

FastAPI applications commonly use JWT, OAuth2, API keys, or HTTP Basic Auth.

## Security Headers

Production APIs should use security headers such as X-Content-Type-Options,
X-Frame-Options, Content-Security-Policy, and Strict-Transport-Security.
"""


def demo_rag_system() -> None:
    """Demonstrate the RAG API when optional dependencies are available."""
    print("Janusz RAG demo (experimental)")
    print("=" * 32)

    try:
        from janusz.rag.rag_system import RAGSystem
    except ImportError as exc:
        print(f"RAG modules are unavailable: {exc}")
        print("Install optional dependencies with: uv sync --extra rag")
        return

    with TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "security-guide.md"
        source.write_text(SAMPLE_CONTENT, encoding="utf-8")

        converter = UniversalToYAMLConverter(str(source))
        document = converter.parse_text_structure(SAMPLE_CONTENT)

        try:
            rag_system = RAGSystem()
            document_id = rag_system.add_document(document)
            response = rag_system.query(
                "What security headers should I configure?",
                generate_answer=False,
            )
        except Exception as exc:
            print(f"RAG demo could not run: {exc}")
            print("Install janusz[rag] and configure an embedding provider to use RAG.")
            return

        print(f"Indexed document: {document_id}")
        print("Search-only response:")
        print(response.answer)


def demo_cli_commands() -> None:
    """Show CLI commands for RAG."""
    print("\nCLI commands:")
    print("janusz rag index --file document.yaml")
    print('janusz rag query "How does authentication work?"')
    print("janusz rag stats")


if __name__ == "__main__":
    demo_rag_system()
    demo_cli_commands()
