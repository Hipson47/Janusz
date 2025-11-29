# AI Agent Knowledge Base Pipeline
# Automates Document -> YAML -> TOON conversion
# Supports: PDF, MD, TXT, DOCX, HTML, RTF, EPUB

.PHONY: toon help clean all pdf-to-yaml yaml-to-toon

# Default target - run full pipeline
toon: pdf-to-yaml yaml-to-toon
	@echo "✓ Pipeline completed: PDF → YAML → TOON"

# Convert all supported documents to YAML
pdf-to-yaml:
	@echo "🔄 Converting documents to YAML..."
	@python pdf_yaml_converter.py
	@echo "✓ Document to YAML conversion completed"

# Convert all YAMLs to TOON
yaml-to-toon:
	@echo "🔄 Converting YAMLs to TOON..."
	@python toon.py
	@echo "✓ YAML to TOON conversion completed"

# Convert PDFs and show YAML conversion details
yaml: pdf-to-yaml
	@echo "✓ YAML files ready"

# Clean generated files (YAML and TOON)
clean:
	@echo "🧹 Cleaning generated files..."
	@find . -name "*.yaml" -not -path "./baza*" -delete 2>/dev/null || true
	@find . -name "*.toon" -not -path "./baza*" -delete 2>/dev/null || true
	@echo "✓ Generated files cleaned"

# Show available commands
help:
	@echo "Available commands:"
	@echo "  make toon        - Run full pipeline: Documents → YAML → TOON"
	@echo "  make yaml        - Convert documents to YAML only"
	@echo "  make pdf-to-yaml - Convert documents to YAML only"
	@echo "  make yaml-to-toon - Convert YAMLs to TOON only"
	@echo "  make clean       - Remove generated YAML and TOON files"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "Supported formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB"

# Alternative names for convenience
all: toon
