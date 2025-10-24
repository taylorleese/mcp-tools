.PHONY: help install install-dev test test-cov lint format clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests in parallel"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run all linters via pre-commit"
	@echo "  make format       - Format code via pre-commit"
	@echo "  make clean        - Remove generated files and caches"

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Testing targets
test:
	PYTHONPATH=src pytest tests/ -n auto -v

test-cov:
	PYTHONPATH=src pytest tests/ -n auto --cov=src --cov-branch --cov-report=xml --cov-report=term-missing --cov-report=html --junitxml=junit.xml -o junit_family=legacy

# Linting targets (via pre-commit for consistency)
lint:
	pre-commit run --all-files

# Formatting targets (via pre-commit for consistency)
format:
	pre-commit run black --all-files
	pre-commit run isort --all-files
	pre-commit run ruff-format --all-files
	pre-commit run ruff --all-files

# Cleanup targets
clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleaned!"
