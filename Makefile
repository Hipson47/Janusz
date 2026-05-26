# Janusz - AI Agent Knowledge Base Pipeline
# Automates Document -> YAML -> JSON -> Skill package workflows.

.PHONY: help clean install test convert json skill all lint format typecheck check setup-venv

help:
	@echo "Janusz - Document-to-JSON pipeline for AI agent knowledge bases"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup-venv  - Setup virtual environment with dependencies"
	@echo "  make install     - Install the package in development mode"
	@echo "  make convert     - Convert documents to YAML format"
	@echo "  make json        - Create JSON packages"
	@echo "  make skill       - Create Codex skill packages"
	@echo "  make ingest      - Create a repository operations skill"
	@echo "  make registry    - Build local skill registry"
	@echo "  make all         - Run full pipeline: Documents -> YAML -> JSON"
	@echo "  make test        - Run automated tests"
	@echo "  make lint        - Run code linting with ruff"
	@echo "  make format      - Format code with black"
	@echo "  make typecheck   - Run type checking with mypy"
	@echo "  make check       - Run lint + typecheck + test"
	@echo "  make clean       - Remove caches and temporary generated files"
	@echo ""
	@echo "File-specific commands:"
	@echo "  make convert FILE=path/to/document.pdf"
	@echo "  make json FILE=path/to/document.yaml"
	@echo "  make skill FILE=path/to/document.json"

setup-venv:
	@echo "Setting up virtual environment..."
	@test -d venv || python -m venv venv
	@venv/bin/pip install --upgrade pip
	@venv/bin/pip install -e .
	@echo "Virtual environment ready"

install:
	@echo "Installing Janusz in development mode..."
	@uv sync
	@echo "Installation completed"

convert:
	@echo "Converting documents to YAML..."
ifdef FILE
	@uv run python -m janusz.cli convert --file $(FILE)
else
	@uv run python -m janusz.cli convert
endif
	@echo "Document to YAML conversion completed"

json:
	@echo "Creating JSON packages..."
ifdef FILE
	@uv run python -m janusz.cli json --file $(FILE)
else
	@uv run python -m janusz.cli json
endif
	@echo "JSON packaging completed"

skill:
	@echo "Creating Codex skill packages..."
ifdef FILE
	@uv run python -m janusz.cli skill --file $(FILE)
else
	@uv run python -m janusz.cli skill
endif
	@echo "Skill packaging completed"

ingest:
	@echo "Creating repository operations skill..."
	@uv run python -m janusz.cli ingest repo $(if $(REPO),$(REPO),.) --output-dir $(if $(OUT),$(OUT),skills) --overwrite
	@echo "Repository ingest completed"

registry:
	@echo "Building skill registry..."
	@uv run python -m janusz.cli registry build --skills-dir $(if $(SKILLS),$(SKILLS),skills)
	@echo "Skill registry completed"

all: setup-venv
	@echo "Starting full pipeline: Documents -> YAML -> JSON"
	@make convert-in-venv
	@make json-in-venv
	@echo "Pipeline completed: Documents -> YAML -> JSON"

convert-in-venv:
	@echo "Converting documents to YAML..."
	@venv/bin/python -m janusz.cli convert

json-in-venv:
	@echo "Creating JSON packages..."
	@venv/bin/python -m janusz.cli json

test:
	@echo "Running tests..."
ifdef FILE
	@uv run python -m janusz.cli test $(FILE)
else
	@uv run pytest tests/ -v -s
endif

lint:
	@echo "Running ruff linter..."
	@uv run ruff check src/ tests/
	@echo "Linting completed"

format:
	@echo "Formatting code with black..."
	@uv run black src/ tests/
	@echo "Code formatting completed"

typecheck:
	@echo "Running mypy type checker..."
	@uv run mypy src/janusz/
	@echo "Type checking completed"

check: lint typecheck test
	@echo "Quality checks completed"

clean:
	@echo "Cleaning caches and temporary files..."
	@find . -name "*.temp.json" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup completed"
