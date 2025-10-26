.PHONY: all help install install-dev test test-cov lint format clean build commit-version publish-test publish

# Default target - format, lint, and test
all: format lint test

# Help target
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
	@echo "  make publish      - Publish to PyPI and GitHub release (runs tests first)"

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
	pre-commit run trailing-whitespace --all-files
	pre-commit run end-of-file-fixer --all-files
	pre-commit run autoflake --all-files
	pre-commit run black --all-files
	pre-commit run isort --all-files
	pre-commit run ruff-format --all-files
	pre-commit run ruff --all-files
	pre-commit run markdownlint --all-files

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
	python3 -m build
	@echo "✅ Built packages in dist/"

# Helper target to commit and push version changes if needed
commit-version:
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	if ! git diff --quiet pyproject.toml; then \
		echo "Detected version change to v$$VERSION in pyproject.toml"; \
		echo "Committing and pushing version change..."; \
		git add pyproject.toml; \
		git commit -m "Bump version to $$VERSION"; \
		git push; \
	fi

publish-test: build commit-version
	@echo "Publishing to TestPyPI via GitHub Actions..."
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Triggering publish workflow for TestPyPI (v$$VERSION)..."; \
	gh workflow run publish.yml -f environment=testpypi; \
	echo "✅ Workflow triggered!"; \
	echo "Monitor: https://github.com/taylorleese/mcp-toolz/actions/workflows/publish.yml"; \
	echo "After publish completes, install with:"; \
	echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-toolz"

publish: test lint commit-version
	@echo "Publishing to PyPI and GitHub..."
	@VERSION=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Creating git tag v$$VERSION..."; \
	git tag -a v$$VERSION -m "Release v$$VERSION"; \
	git push origin v$$VERSION; \
	echo "Creating GitHub release v$$VERSION..."; \
	gh release create v$$VERSION --generate-notes --verify-tag; \
	echo "✅ Release v$$VERSION created!"; \
	echo ""; \
	echo "GitHub Actions will automatically:"; \
	echo "  1. Build distribution packages"; \
	echo "  2. Publish to PyPI via Trusted Publishing"; \
	echo "  3. Generate and upload SLSA attestations"; \
	echo "  4. Sign artifacts with Sigstore"; \
	echo ""; \
	echo "Monitor: https://github.com/taylorleese/mcp-toolz/actions/workflows/publish.yml"; \
	echo "GitHub: https://github.com/taylorleese/mcp-toolz/releases/tag/v$$VERSION"; \
	echo "PyPI: https://pypi.org/project/mcp-toolz/$$VERSION/ (available in ~2 min)"
