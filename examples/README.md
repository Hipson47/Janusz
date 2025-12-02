# Janusz Examples & Token Savings Demo

This directory contains examples demonstrating Janusz's document processing capabilities and token compression benefits for AI agent knowledge bases.

## Overview

Janusz transforms unstructured documents into structured, AI-optimized formats with significant token savings. The pipeline converts documents through three stages:

1. **Document → YAML**: Extracts structure, keywords, and best practices
2. **YAML → TOON**: Compresses to token-efficient binary format
3. **Analysis**: Provides confidence levels and compression statistics

## Sample Files

### Input Documents

- **`sample_architecture.md`**: A comprehensive software architecture document with hierarchical sections, best practices, and technical specifications
- **`sample_spec.txt`**: A simpler API specification in plain text format

### Generated Outputs

- **`sample_architecture_janusz.yaml`**: Structured YAML output with metadata, hierarchical sections, keywords, and best practices
- **`sample_architecture_token_stats.json`**: Detailed token statistics comparing raw text, YAML, and TOON formats

## Running the Examples

### Prerequisites

1. Install Janusz: `pip install janusz` or `uv sync`
2. Install TOON CLI: `cargo install toon` (optional, for full TOON conversion)
3. Install NLP dependencies: `pip install janusz[nlp]` (optional, for enhanced keyword extraction)

### Measure Token Savings

Use the provided script to process example files and see token savings:

```bash
# Process the architecture document
python examples/scripts/measure_token_savings.py examples/inputs/sample_architecture.md

# Process the API specification
python examples/scripts/measure_token_savings.py examples/inputs/sample_spec.txt
```

Example output:
```
🔄 Processing sample_architecture.md...
📄 Original text tokens: 1,247
📋 YAML tokens: 1,089 (-12.7% savings)
🎨 TOON tokens: 834 (-33.1% savings)
   Compression ratio: 1.48x
```

### Manual Processing

You can also process files manually using Janusz CLI:

```bash
# Convert to YAML
janusz convert --file examples/inputs/sample_architecture.md

# Convert YAML to TOON
janusz toon --file sample_architecture.yaml

# Get detailed conversion info
janusz test sample_architecture.yaml
```

## Token Savings Analysis

### Why Token Savings Matter

Large Language Models (LLMs) have token limits for context windows. Efficient token usage means:

- **More content** can fit in limited context windows
- **Lower costs** for API calls (token-based pricing)
- **Better performance** with relevant information prioritized
- **Scalability** for processing large document collections

### Typical Savings

Based on our examples:

- **YAML Structure**: 10-15% token reduction through structured formatting
- **TOON Compression**: 25-40% additional savings through binary optimization
- **Combined**: 35-50% total token reduction vs raw text

### Factors Affecting Savings

1. **Document Structure**: Well-structured documents (headings, lists) compress better
2. **Content Type**: Technical documentation often has more compressible patterns
3. **NLP Enhancement**: Advanced keyword extraction can improve compression
4. **TOON Optimization**: Binary format provides consistent compression benefits

## Advanced Features Demonstrated

### Hierarchical Section Parsing

The architecture example shows how Janusz preserves document hierarchy:

```yaml
content:
  sections:
    - title: "Overview"
      level: 1
      content: [...]
      children: []  # Can have nested subsections
    - title: "System Components"
      level: 1
      content: [...]
      children:
        - title: "Authentication Service"
          level: 2
          content: [...]
```

### Keyword Extraction with Confidence

Keywords are extracted with confidence levels:

```yaml
analysis:
  keywords:
    - text: "authentication"
      confidence_level: "high"
    - text: "microservices"
      confidence_level: "medium"
    - text: "kubernetes"
      confidence_level: "low"
```

### Best Practices & Examples

Structured extraction of actionable content:

```yaml
analysis:
  best_practices:
    - text: "Always validate JWT tokens on each request"
      source_section_id: "section_auth"
      tags: ["security", "authentication"]
      confidence_level: "high"
  examples:
    - text: "Use cross-validation for model evaluation"
      source_section_id: "section_ml"
      tags: ["machine-learning"]
      confidence_level: "medium"
```

## Integration Examples

### Python API Usage

```python
from janusz.converter import UniversalToYAMLConverter
from janusz.toon_adapter import YAMLToTOONConverter

# Convert document to structured YAML
converter = UniversalToYAMLConverter("document.pdf")
converter.convert_to_yaml()  # Creates document.yaml

# Convert to TOON for AI consumption
toon_converter = YAMLToTOONConverter("document.yaml")
toon_converter.convert()  # Creates document.toon

# Get token statistics
stats = toon_converter.get_token_stats()
print(f"Compression ratio: {stats['compression_ratio']}")
```

### Command Line Usage

```bash
# Full pipeline
./scripts/toon.sh

# Individual steps
janusz convert --file document.pdf
janusz toon --file document.yaml
janusz test document.yaml
```

## Troubleshooting

### Missing TOON CLI

If TOON conversion fails:
```bash
# Install TOON CLI
cargo install toon

# Or use the automated installer
./scripts/toon.sh  # Will install TOON if missing
```

### Missing NLP Libraries

For enhanced keyword extraction:
```bash
# Install NLP dependencies
pip install janusz[nlp]

# Or continue with basic heuristics
# (NLP is optional, basic functionality works without it)
```

### File Format Issues

- Ensure files are UTF-8 encoded
- Check for supported formats: PDF, MD, TXT, DOCX, HTML
- RTF and EPUB are planned for future releases

## Contributing Examples

To add more examples:

1. Add input files to `examples/inputs/`
2. Run the measurement script to generate outputs
3. Update this README with new results
4. Ensure files are license-compatible and reasonably sized

## Performance Benchmarks

For production deployments, consider:

- **Batch Processing**: Process multiple documents together
- **Caching**: Cache processed results for frequently accessed documents
- **Parallel Processing**: Use multiple workers for large document sets
- **Incremental Updates**: Only reprocess changed documents

## GUI Demonstration

### Running the GUI Demo

```bash
# Create sample documents for GUI testing
python examples/gui_demo.py

# Launch the GUI
janusz gui

# Or use the alternative launcher
python scripts/gui.py
```

### GUI Features

The Janusz GUI provides an intuitive desktop interface for:

- **Document Selection**: Browse and select files from knowledge base directories
- **Format Conversion**: Convert to YAML, JSON, or TOON formats
- **AI Integration**: Enable AI-powered analysis for enhanced insights
- **Progress Tracking**: Real-time processing status and detailed logs
- **Batch Operations**: Process multiple files simultaneously

### Sample Documents

The `gui_demo.py` script creates sample technical documents including:

- **AI Overview Document**: Comprehensive guide to AI-powered processing
- **FastAPI Security Guide**: Technical documentation with best practices

These documents showcase different types of content that benefit from AI-enhanced processing.

---

*These examples demonstrate Janusz's capabilities for transforming unstructured knowledge into AI-optimized formats with significant token efficiency gains.*
