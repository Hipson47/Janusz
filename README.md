# Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases

A Python package that converts various document formats to structured YAML and then optimizes them to TOON (Token-Oriented Object Notation) format for efficient AI agent prompting and knowledge storage.

## 🎯 What it does

This project converts documents in various formats to optimized TOON format, perfect for:
- Prompt engineering for AI agents
- Compact knowledge storage
- Efficient token usage in LLM models

## 📋 Supported Formats

| Format | Extension | Requirements |
|--------|-----------|-------------|
| PDF | `.pdf` | `pdfplumber` |
| Markdown | `.md` | - |
| Plain Text | `.txt` | - |
| DOCX | `.docx` | `python-docx` (optional) |
| HTML | `.html` | `html2text` or `beautifulsoup4` (optional) |
| RTF | `.rtf` | (reserved) |
| EPUB | `.epub` | (reserved) |
| JSON | `.json` | - |
| YAML | `.yaml` | - |

## 🚀 Quick Start

### Installation

```bash
# Install from source (recommended for development)
pip install -e .

# Or install dependencies manually
pip install pdfplumber pyyaml python-docx html2text beautifulsoup4
```

### Full pipeline in one command

```bash
# Run complete process: Documents → YAML → TOON
make all

# Or use the CLI directly
janusz convert && janusz toon
```

### Step by step

```bash
# 1. Convert documents to YAML
make convert
# or
janusz convert

# 2. Convert YAML to TOON
make toon
# or
janusz toon
```

### Single file conversion

```bash
# Convert specific file to YAML
janusz convert --file "document.md"

# Convert specific YAML to TOON
janusz toon --file "document.yaml"

# Convert specific JSON to TOON
janusz json --file "data.json"

# Test TOON conversion with detailed output
janusz test "document.yaml"
janusz test "data.json"
```

## 📁 Project Structure

```
📁 workspace/
├── 📁 src/janusz/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── converter.py        # Document to YAML converter
│   ├── toon_adapter.py     # YAML to TOON converter
│   ├── json_to_toon.py     # JSON to TOON converter
│   └── cli.py             # Command-line interface
├── 📁 tests/               # Test suite
│   ├── test_converter.py   # Converter tests
│   ├── test_toon_adapter.py # TOON adapter tests
│   ├── test_json_to_toon.py # JSON to TOON tests
│   └── conftest.py         # Test fixtures
├── 📄 pyproject.toml       # Package configuration
├── 📄 Makefile            # Build automation
├── 📄 README.md           # This file
├── 📄 LICENSE             # MIT License
└── 📁 baza wiedzy 28.11/  # Knowledge base (preserved)
```

## 🛠️ Requirements

### Core Dependencies
- `pdfplumber>=0.9.0` - PDF text extraction
- `pyyaml>=6.0` - YAML processing
- `python-docx>=1.0.0` - DOCX support
- `html2text>=2020.1.16` - HTML to text conversion
- `beautifulsoup4>=4.12.0` - HTML parsing fallback

### External Tools
- [TOON CLI](https://github.com/toon-format/toon) - Required for TOON conversion

## 📖 CLI Commands

```bash
# Show help
janusz --help

# Convert all documents in current directory to YAML
janusz convert

# Convert specific document to YAML
janusz convert --file path/to/document.pdf

# Convert all YAML files to TOON
janusz toon

# Convert specific YAML to TOON
janusz toon --file path/to/document.yaml

# Convert all JSON files to TOON
janusz json

# Convert specific JSON to TOON
janusz json --file path/to/data.json

# Test TOON conversion with detailed output
janusz test path/to/document.yaml
janusz test path/to/data.json
```

### Make Commands

```bash
make help        # Show available commands
make install     # Install package in development mode
make convert     # Convert documents to YAML
make toon        # Convert YAML to TOON
make json        # Convert JSON to TOON
make all         # Full pipeline
make test        # Run test suite
make clean       # Clean generated files
```

## 🔧 How it Works

1. **Text Extraction** - Extract text from various document formats or parse JSON/YAML
2. **Structure Parsing** - Identify sections, headers, and patterns
3. **Content Analysis** - Extract key concepts and examples
4. **Structured Format** - Create YAML format with metadata or use existing JSON structure
5. **TOON Optimization** - Convert to compact format for AI consumption

## 📊 Example Output Structure

### YAML Format
```yaml
metadata:
  title: "Document Name"
  source: "file.md"
  source_type: "markdown"
  converted_by: "Universal Document to YAML Converter"
  format_version: "2.0"
content:
  sections:
    - title: "# Header"
      content: ["Section content"]
      subsections: []
  raw_text: "Full document text"
analysis:
  keywords: ["important", "terms"]
  best_practices: ["Recommendations"]
  examples: ["Code examples"]
```

### TOON Format
Optimized binary format for efficient AI processing with token compression.

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_converter.py -v

# Run with coverage
pytest --cov=janusz --cov-report=html
```

## 🤝 Contributing

1. Add support for new formats in `converter.py`
2. Improve parsing for existing formats
3. Add tests and validation
4. Update documentation

### Development Setup

```bash
# Clone and setup
git clone <repository>
cd <repository>

# Install in development mode (includes all dependencies)
make install

# Or using uv (recommended)
uv sync

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Run full quality check
make check

# Test CLI functionality
janusz --help
janusz convert --file "example.md"
```

### Development Workflow

1. **Setup**: `make install` or `uv sync`
2. **Code**: Make changes to `src/janusz/`
3. **Test**: `make test` - ensure all tests pass
4. **Quality**: `make check` - lint, format, and type check
5. **Commit**: Only clean, tested code

### Code Quality Tools

- **Linting**: Ruff (fast Python linter)
- **Formatting**: Black (opinionated code formatter)
- **Type checking**: mypy (static type analysis)
- **Testing**: pytest with coverage

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## 📄 License

This project is available under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License allows:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

With the requirement to preserve author and license information.

## 🔗 Related Projects

- [TOON Format](https://github.com/toon-format/toon) - Token-Oriented Object Notation
- [Cursor IDE](https://cursor.sh) - IDE with AI integration
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF processing library
