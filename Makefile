.PHONY: help install install-dev test test-cov lint format clean build publish-test publish publish-force

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
	@echo "  make build        - Build distribution packages"
	@echo "  make publish-test - Publish to TestPyPI"
	@echo "  make publish      - Publish to PyPI and GitHub release (requires tests to pass)"
	@echo "  make publish-force - Publish to PyPI and GitHub release without confirmation"

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
	rm -rf coverage.xml
	rm -rf junit.xml
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleaned!"

# Publishing targets
build: clean
	@echo "Building distribution packages..."
	python -m build
	@echo "✅ Built packages in dist/"

publish-test: build
	@echo "Publishing to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "✅ Published to TestPyPI!"
	@echo "Install with: pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-toolz"

publish: test lint build
	@echo "Publishing to PyPI and GitHub..."
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	read -p "Are you sure you want to publish v$$VERSION to PyPI and GitHub? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Creating git tag v$$VERSION..."; \
		git tag -a v$$VERSION -m "Release v$$VERSION"; \
		git push origin v$$VERSION; \
		echo "Creating GitHub release v$$VERSION..."; \
		gh release create v$$VERSION dist/* --generate-notes; \
		echo "Publishing to PyPI..."; \
		twine upload dist/*; \
		echo "✅ Published v$$VERSION to PyPI and GitHub!"; \
		echo "PyPI: https://pypi.org/project/mcp-toolz/$$VERSION/"; \
		echo "GitHub: https://github.com/taylorleese/mcp-toolz/releases/tag/v$$VERSION"; \
	else \
		echo "❌ Publish cancelled"; \
		exit 1; \
	fi

publish-force: test lint build
	@echo "Publishing to PyPI and GitHub (no confirmation)..."
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Creating git tag v$$VERSION..."; \
	git tag -a v$$VERSION -m "Release v$$VERSION"; \
	git push origin v$$VERSION; \
	echo "Creating GitHub release v$$VERSION..."; \
	gh release create v$$VERSION dist/* --generate-notes; \
	echo "Publishing to PyPI..."; \
	twine upload dist/*; \
	echo "✅ Published v$$VERSION to PyPI and GitHub!"; \
	echo "PyPI: https://pypi.org/project/mcp-toolz/$$VERSION/"; \
	echo "GitHub: https://github.com/taylorleese/mcp-toolz/releases/tag/v$$VERSION"
