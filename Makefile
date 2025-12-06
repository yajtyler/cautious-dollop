# DNS Benchmark Tool - Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help install install-dev test lint format clean build upload docs watch serve-docs

# Default target
help:
	@echo "DNS Benchmark Tool - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install the package for production use"
	@echo "  install-dev  Install the package with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run the test suite"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run code linting and type checking"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts and cache files"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Generate documentation"
	@echo "  serve-docs   Serve documentation locally"
	@echo ""
	@echo "Build & Release:"
	@echo "  build        Build the package for distribution"
	@echo "  upload       Upload package to PyPI"
	@echo "  upload-test  Upload package to Test PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  watch        Watch for file changes and run tests"
	@echo "  benchmark     Run a quick benchmark test"
	@echo "  check         Run all quality checks"

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8
MYPY := mypy
SPHINX := sphinx-build

# Installation
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	pre-commit install

# Development
test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ -v --cov=dns_benchmark --cov-report=html --cov-report=term-missing

test-fast:
	$(PYTEST) tests/ -v -x --ff

lint:
	$(FLAKE8) dns_benchmark/ tests/
	$(MYPY) dns_benchmark/
	bandit -r dns_benchmark/

format:
	$(BLACK) dns_benchmark/ tests/
	$(ISORT) dns_benchmark/ tests/

format-check:
	$(BLACK) --check dns_benchmark/ tests/
	$(ISORT) --check-only dns_benchmark/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Documentation
docs:
	$(SPHINX) -b html docs/ docs/_build/html
	@echo "Documentation built in docs/_build/html"

serve-docs:
	cd docs/_build/html && $(PYTHON) -m http.server 8000

docs-live:
	sphinx-autobuild docs/ docs/_build/html --host 0.0.0.0 --port 8000

# Build & Release
build: clean
	$(PYTHON) setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository testpypi dist/*

# Utilities
watch:
	$(PYTEST) tests/ -f --disable-warnings

benchmark:
	$(PYTHON) -m dns_benchmark --queries 10 --domains "google.com,cloudflare.com"

check: format-check lint test-cov
	@echo "All checks passed!"

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"

# Quality assurance
qa: format lint test-cov
	@echo "Quality assurance checks completed!"

# Release preparation
release-check: clean test-cov lint build
	@echo "Release checks completed!"

# Database/migrations (if applicable)
migrate:
	@echo "No database migrations needed for this project"

# Security checks
security:
	safety check
	bandit -r dns_benchmark/

# Performance profiling
profile:
	$(PYTHON) -m cProfile -o profile.stats -m dns_benchmark --queries 100
	$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Memory profiling
memory-profile:
	$(PYTHON) -m memory_profiler -m dns_benchmark --queries 50

# Dependency management
deps-update:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

deps-check:
	$(PIP) check
	pipdeptree

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate

# Version management
version-patch:
	bump2version patch

version-minor:
	bump2version minor

version-major:
	bump2version major

# Docker (if applicable)
docker-build:
	docker build -t dns-benchmark .

docker-run:
	docker run --rm dns-benchmark

# CI/CD helpers
ci-test:
	$(PYTEST) tests/ --junitxml=test-results.xml --cov=dns_benchmark --cov-report=xml

ci-lint:
	$(FLAKE8) dns_benchmark/ tests/ --output-file=lint-results.txt
	$(MYPY) dns_benchmark/ --junit-xml=type-results.xml

# Help for specific areas
help-dev:
	@echo "Development Commands:"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make test          Run tests"
	@echo "  make format        Format code"
	@echo "  make lint          Check code quality"
	@echo "  make watch         Watch for changes and run tests"

help-deploy:
	@echo "Deployment Commands:"
	@echo "  make build         Build package for distribution"
	@echo "  make upload        Upload to PyPI"
	@echo "  make upload-test    Upload to Test PyPI"

help-docs:
	@echo "Documentation Commands:"
	@echo "  make docs          Generate HTML documentation"
	@echo "  make serve-docs    Serve docs locally"
	@echo "  make docs-live     Live-reload docs during development"

# Quick start for new developers
quick-start: install-dev
	@echo "Running quick benchmark test..."
	make benchmark
	@echo ""
	@echo "Quick start complete!"
	@echo "Run 'make help' for more commands"