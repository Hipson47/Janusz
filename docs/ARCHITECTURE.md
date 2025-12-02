# Architecture Overview

## Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases

Janusz is a Python package that converts various document formats to structured YAML and then optimizes them to TOON (Token-Oriented Object Notation) format for efficient AI agent prompting and knowledge storage.

## Core Pipeline

```
Documents → YAML → TOON
    ↓        ↓      ↓
converter  adapter  TOON CLI
```

### 1. Document Conversion (converter.py)

**Purpose**: Extract text from various document formats and structure it as YAML.

**Supported Input Formats**:
- PDF (via `pdfplumber`)
- Markdown (.md)
- Plain Text (.txt)
- DOCX (via `python-docx`, optional)
- HTML (via `html2text` + `beautifulsoup4`, optional)
- RTF, EPUB (planned for v1.1.0)

**Output**: Structured YAML with metadata, content sections, and analysis.

**Key Classes**:
- `UniversalToYAMLConverter`: Main conversion class
- Supports batch processing via `process_directory()`

### 2. TOON Conversion (toon_adapter.py, json_to_toon.py)

**Purpose**: Convert structured data to optimized TOON format for AI consumption.

**Process**:
1. YAML/JSON → Intermediate JSON
2. JSON → TOON (via external TOON CLI)

**Key Classes**:
- `YAMLToTOONConverter`: YAML → TOON pipeline
- `JSONToTOONConverter`: JSON → TOON pipeline
- Both support validation and batch processing

### 3. CLI Orchestration (cli.py)

**Purpose**: Provide unified command-line interface for the entire pipeline.

**Commands**:
- `convert`: Documents → YAML
- `toon`: YAML → TOON
- `json`: JSON → TOON
- `test`: Validation with detailed output

**Features**:
- Single file or directory processing
- Progress logging
- Error handling and validation

## Project Structure

```
📁 workspace/
├── 📁 src/janusz/              # Main package (src layout)
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── converter.py           # Document → YAML converter
│   ├── toon_adapter.py        # YAML → TOON converter
│   └── json_to_toon.py        # JSON → TOON converter
├── 📁 tests/                  # Test suite
│   ├── conftest.py            # Test fixtures
│   ├── test_converter.py      # Converter tests
│   ├── test_toon_adapter.py   # TOON adapter tests
│   └── test_json_to_toon.py   # JSON to TOON tests
├── 📁 docs/                   # Documentation
│   ├── ARCHITECTURE.md        # This file
│   ├── PDF_TO_YAML_*.md       # Knowledge base indexes
│   └── TOON_*.md              # TOON integration docs
├── 📁 scripts/                # Automation scripts
│   └── toon.sh                # Full pipeline script
├── 📁 .cursor/                # Operational playbook layer
│   ├── rules/                 # Development rules
│   └── rules.yaml             # Cursor IDE configuration
├── pyproject.toml             # Package configuration
├── Makefile                   # Build automation
├── README.md                  # User documentation
└── .gitignore                 # Git ignore rules
```

## Data Flow

### Document Processing Pipeline

1. **Input Detection**: File extension determines processing method
2. **Text Extraction**: Format-specific extractors pull content
3. **Structure Analysis**: Identify sections, headers, patterns
4. **YAML Serialization**: Create structured output with metadata
5. **TOON Optimization**: Convert to token-efficient binary format

### CLI Integration

The CLI (`janusz` command) orchestrates the pipeline:

```bash
# Full pipeline
janusz convert && janusz toon

# Individual steps
janusz convert --file document.pdf
janusz toon --file document.yaml
```

## Automation Layer

### Makefile Targets

- `make install`: Development setup
- `make convert/toon/json`: Individual pipeline steps
- `make all`: Full pipeline
- `make test`: Run test suite
- `make lint/format/typecheck`: Code quality
- `make check`: Full quality gate

### Scripts

- `scripts/toon.sh`: Automated pipeline execution
- Handles error checking and progress reporting

## Quality Assurance

### Testing Strategy

- **Unit Tests**: Core functionality in `tests/`
- **Integration Tests**: End-to-end pipeline validation
- **CLI Tests**: Command-line interface coverage

### Code Quality Tools

- **Linting**: Ruff (fast, comprehensive)
- **Formatting**: Black (consistent style)
- **Type Checking**: mypy (static analysis)
- **Coverage**: pytest-cov

## Dependencies

### Core Dependencies
- `pdfplumber`: PDF text extraction
- `pyyaml`: YAML processing
- `python-docx`: DOCX support
- `html2text`: HTML conversion
- `beautifulsoup4`: HTML parsing

### Development Dependencies
- `pytest`: Testing framework
- `ruff`: Linting and formatting
- `black`: Code formatting
- `mypy`: Type checking

### External Tools
- **TOON CLI**: Required for TOON conversion (separate installation)

## Operational Rules (.cursor/)

The `.cursor/` directory contains operational playbooks:

- **Development Rules**: Coding standards, workflow
- **Security Rules**: Safe development practices
- **Testing Rules**: Quality assurance guidelines
- **FastAPI Rules**: API development standards

These rules ensure consistent development practices and security.

## Security Considerations

- Private knowledge bases in `baza wiedzy 28.11/` and `new/` are gitignored
- No credentials or secrets committed
- Input validation on all external data
- Sandboxed execution environment

## Future Extensions

### Format Support
- RTF, EPUB document processing (planned for v1.1.0)
- Additional structured formats (XML, CSV)

### Pipeline Enhancements
- Parallel processing for large document sets
- Cloud storage integration
- Web UI for document management

### AI Integration
- Direct TOON output to AI agents
- Automated knowledge base updates
- Quality scoring for converted content
