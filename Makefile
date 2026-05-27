# Janusz - AI Agent Knowledge Base Pipeline
# Automates Document -> YAML -> JSON -> Skill package workflows.

.PHONY: help clean install test convert json skill all lint format format-check typecheck compile security-audit build-package wheel-smoke check release-check mutate-core setup-venv

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
	@echo "  make format      - Format code with ruff"
	@echo "  make typecheck   - Run type checking with mypy"
	@echo "  make check       - Run developer quality gate"
	@echo "  make release-check - Run full production release gate"
	@echo "  make wheel-smoke - Smoke test the built wheel in a clean venv"
	@echo "  make mutate-core - Run mutation testing for core modules"
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
	@uv sync --group dev --locked
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
	@uv run python -m pytest tests/ -v --capture=no
endif

lint:
	@echo "Running ruff linter..."
	@uv run ruff check .
	@echo "Linting completed"

format:
	@echo "Formatting code with ruff..."
	@uv run ruff format .
	@echo "Code formatting completed"

format-check:
	@echo "Checking code formatting with ruff..."
	@uv run ruff format --check .
	@echo "Format check completed"

typecheck:
	@echo "Running mypy type checker..."
	@uv run mypy src/janusz/
	@echo "Type checking completed"

compile:
	@echo "Compiling Python sources..."
	@uv run python -m compileall -q src scripts examples tests
	@echo "Compilation completed"

security-audit:
	@echo "Running dependency security audit..."
	@for attempt in 1 2 3; do \
		uv run pip-audit && exit 0; \
		status=$$?; \
		if [ $$attempt -eq 3 ]; then exit $$status; fi; \
		echo "pip-audit failed, retrying ($$attempt/3)..."; \
		sleep 5; \
	done

build-package:
	@echo "Building package artifacts..."
	@rm -rf dist build
	@uv build

wheel-smoke:
	@echo "Smoke testing built wheel..."
	@set -e; \
	test -n "$$(find dist -maxdepth 1 -name '*.whl' -print -quit)" || { echo "No wheel found in dist/. Run make build-package first."; exit 1; }; \
	rm -rf /tmp/janusz-wheel-test; \
	python -m venv /tmp/janusz-wheel-test; \
	/tmp/janusz-wheel-test/bin/python -m pip install --upgrade pip; \
	/tmp/janusz-wheel-test/bin/pip install dist/*.whl; \
	/tmp/janusz-wheel-test/bin/janusz --help >/dev/null; \
	/tmp/janusz-wheel-test/bin/janusz --version; \
	tmpdir=$$(mktemp -d); \
	printf '# Smoke Document\n\nThis document verifies JSON and skill packaging.\n' > $$tmpdir/smoke.md; \
	(cd $$tmpdir && /tmp/janusz-wheel-test/bin/janusz json --file smoke.md --output smoke.json >/dev/null); \
	(cd $$tmpdir && /tmp/janusz-wheel-test/bin/janusz skill --file smoke.json --output-dir skills >/dev/null); \
	test -f $$tmpdir/smoke.json; \
	test -n "$$(find $$tmpdir/skills -name SKILL.md -print -quit)"; \
	rm -rf $$tmpdir
	@echo "Wheel smoke completed"

mutate-core:
	@echo "Running mutation tests for core modules..."
	@uv run mutmut run

check: lint format-check typecheck test
	@echo "Quality checks completed"

release-check:
	@uv lock --check
	@$(MAKE) lint
	@$(MAKE) format-check
	@$(MAKE) typecheck
	@$(MAKE) compile
	@uv run python -m pytest tests --capture=no --cov=janusz --cov-report=term-missing --cov-fail-under=70
	@uv run bandit -q -r src/janusz
	@$(MAKE) security-audit
	@$(MAKE) build-package
	@$(MAKE) wheel-smoke
	@uv run python scripts/check_release_version.py
	@echo "Release checks completed"

clean:
	@echo "Cleaning caches and temporary files..."
	@find . -name "*.temp.json" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage .mutmut-cache htmlcov coverage.xml
	@echo "Cleanup completed"
