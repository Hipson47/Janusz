# Janusz - AI Agent Knowledge Base Pipeline
# Automates Document -> YAML -> TOON conversion
# Works on 'new' directory by default - place your documents there
# Supports: PDF, MD, TXT, DOCX, HTML, RTF, EPUB

.PHONY: help clean install test convert toon all

# Default target - show help
help:
	@echo "Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup-venv  - Setup virtual environment with all dependencies"
	@echo "  make install     - Install the package in development mode"
	@echo "  make convert     - Convert documents to YAML format"
	@echo "  make toon        - Convert YAML files to TOON format"
	@echo "  make json        - Validate JSON files (no TOON conversion)"
	@echo "  make json-toon   - Convert JSON files to TOON format"
	@echo "  make all         - Run full pipeline with venv: Documents → YAML → TOON"
	@echo "  make test        - Run automated tests"
	@echo "  make lint        - Run code linting with ruff"
	@echo "  make format      - Format code with black"
	@echo "  make typecheck   - Run type checking with mypy"
	@echo "  make check       - Run all quality checks (lint + type + test)"
	@echo "  make clean       - Remove generated files and cache"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "File-specific commands:"
	@echo "  make convert FILE=path/to/document.pdf"
	@echo "  make toon FILE=path/to/document.yaml"
	@echo "  make json FILE=path/to/data.json"
	@echo "  make json-toon FILE=path/to/data.json"
	@echo "  make test FILE=path/to/document.yaml"
	@echo ""
	@echo "Supported formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB, JSON, YAML"

# Setup virtual environment and install dependencies
setup-venv:
	@echo "🐍 Setting up virtual environment..."
	@test -d venv || python -m venv venv
	@venv/bin/pip install --upgrade pip
	@venv/bin/pip install -e .
	@echo "✓ Virtual environment ready"

# Install package in development mode (legacy, prefer setup-venv)
install:
	@echo "📦 Installing Janusz in development mode..."
	@uv sync
	@echo "✓ Installation completed"

# Convert documents to YAML
convert:
	@echo "🔄 Converting documents to YAML..."
ifdef FILE
	@PYTHONPATH=src python -m janusz.cli convert --file $(FILE)
else
	@PYTHONPATH=src python -m janusz.cli convert
endif
	@echo "✓ Document to YAML conversion completed"

# Convert YAML files to TOON
toon:
	@echo "🎨 Converting YAMLs to TOON..."
	@command -v toon >/dev/null 2>&1 || { echo "⚠️  TOON CLI not found!"; echo "📦 Please install it manually:"; echo "   - From GitHub: https://github.com/toon-format/toon"; echo "   - Via cargo: cargo install toon"; echo "   - Or download binary from releases"; exit 1; }
ifdef FILE
	@PYTHONPATH=src python -m janusz.cli toon --file $(FILE)
else
	@PYTHONPATH=src python -m janusz.cli toon
endif
	@echo "✓ YAML to TOON conversion completed"

# Validate JSON files (no TOON conversion)
json:
	@echo "📋 Validating JSON files..."
ifdef FILE
	@PYTHONPATH=src python -m janusz.cli json --no-toon --file $(FILE)
else
	@PYTHONPATH=src python -m janusz.cli json --no-toon
endif
	@echo "✓ JSON validation completed"

# Convert JSON files to TOON
json-toon:
	@echo "🎨 Converting JSONs to TOON..."
	@command -v toon >/dev/null 2>&1 || { echo "⚠️  TOON CLI not found!"; echo "📦 Please install it manually:"; echo "   - From GitHub: https://github.com/toon-format/toon"; echo "   - Via cargo: cargo install toon"; echo "   - Or download binary from releases"; exit 1; }
ifdef FILE
	@PYTHONPATH=src python -m janusz.cli json --file $(FILE)
else
	@PYTHONPATH=src python -m janusz.cli json
endif
	@echo "✓ JSON to TOON conversion completed"

# Run full pipeline with virtual environment
all: setup-venv
	@echo "🚀 Starting full pipeline: Documents → YAML → TOON"
	@make convert-in-venv
	@make toon-in-venv
	@echo "✓ Pipeline completed: Documents → YAML → TOON"

# Convert documents to YAML (internal use with venv)
convert-in-venv:
	@echo "🔄 Converting documents to YAML..."
	@venv/bin/python -m janusz.cli convert

# Convert YAML files to TOON (internal use with venv)
toon-in-venv:
	@echo "🎨 Converting YAMLs to TOON..."
	@command -v toon >/dev/null 2>&1 || { echo "⚠️  TOON CLI not found!"; echo "📦 Please install it manually:"; echo "   - From GitHub: https://github.com/toon-format/toon"; echo "   - Via cargo: cargo install toon"; echo "   - Or download binary from releases"; exit 1; }
	@venv/bin/python -m janusz.cli toon

# Run tests
test:
	@echo "🧪 Running tests..."
ifdef FILE
	@PYTHONPATH=src python -m janusz.cli test $(FILE)
else
	@PYTHONPATH=src python -m pytest tests/ -v
endif

# Run linting
lint:
	@echo "🔍 Running ruff linter..."
	@uv run ruff check src/ tests/
	@echo "✓ Linting completed"

# Format code
format:
	@echo "🎨 Formatting code with black..."
	@uv run black src/ tests/
	@echo "✓ Code formatting completed"

# Type checking
typecheck:
	@echo "🔍 Running mypy type checker..."
	@uv run mypy src/janusz/
	@echo "✓ Type checking completed"

# Full quality check
check: lint test
	@echo "✓ All quality checks passed"

# Clean generated files and cache
clean:
	@echo "🧹 Cleaning generated files and cache..."
	@find . -name "*.yaml" -not -path "./baza*" -delete 2>/dev/null || true
	@find . -name "*.toon" -not -path "./baza*" -delete 2>/dev/null || true
	@find . -name "*.temp.json" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup completed"
