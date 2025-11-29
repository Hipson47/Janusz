# Janusz - AI Agent Knowledge Base Pipeline
# Automates Document -> YAML -> TOON conversion
# Supports: PDF, MD, TXT, DOCX, HTML, RTF, EPUB

.PHONY: help clean install test convert toon all

# Default target - show help
help:
	@echo "Janusz - Document-to-TOON Pipeline for AI Agent Knowledge Bases"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install the package in development mode"
	@echo "  make convert     - Convert documents to YAML format"
	@echo "  make toon        - Convert YAML files to TOON format"
	@echo "  make json        - Convert JSON files to TOON format"
	@echo "  make all         - Run full pipeline: Documents → YAML → TOON"
	@echo "  make test        - Run automated tests"
	@echo "  make clean       - Remove generated files and cache"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "File-specific commands:"
	@echo "  make convert FILE=path/to/document.pdf"
	@echo "  make toon FILE=path/to/document.yaml"
	@echo "  make json FILE=path/to/data.json"
	@echo "  make test FILE=path/to/document.yaml"
	@echo ""
	@echo "Supported formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB, JSON, YAML"

# Install package in development mode
install:
	@echo "📦 Installing Janusz in development mode..."
	@pip install -e .
	@echo "✓ Installation completed"

# Convert documents to YAML
convert:
	@echo "🔄 Converting documents to YAML..."
ifdef FILE
	@python -m janusz.cli convert --file $(FILE)
else
	@python -m janusz.cli convert
endif
	@echo "✓ Document to YAML conversion completed"

# Convert YAML files to TOON
toon:
	@echo "🎨 Converting YAMLs to TOON..."
ifdef FILE
	@python -m janusz.cli toon --file $(FILE)
else
	@python -m janusz.cli toon
endif
	@echo "✓ YAML to TOON conversion completed"

# Convert JSON files to TOON
json:
	@echo "🎨 Converting JSONs to TOON..."
ifdef FILE
	@python -m janusz.cli json --file $(FILE)
else
	@python -m janusz.cli json
endif
	@echo "✓ JSON to TOON conversion completed"

# Run full pipeline
all: convert toon
	@echo "✓ Pipeline completed: Documents → YAML → TOON"

# Run tests
test:
	@echo "🧪 Running tests..."
ifdef FILE
	@python -m janusz.cli test $(FILE)
else
	@pytest tests/ -v
endif

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
