# Contributing to mcp-toolz

Thank you for your interest in contributing to mcp-toolz! We welcome contributions from the community.

## Code of Conduct

Please be respectful and constructive in your interactions with other contributors. We are committed to providing a welcoming and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.13 or later
- Git
- A GitHub account

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/mcp-toolz.git
cd mcp-toolz
```

2. **Create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements-dev.txt
```

4. **Install pre-commit hooks**

```bash
pre-commit install
```

This will automatically run code quality checks before each commit.

## Development Workflow

### Creating a Branch

Create a feature branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Making Changes

1. **Write your code** following our coding standards (see below)
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run tests** to ensure everything works

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in parallel
pytest tests/ -n auto
```

### Code Quality Checks

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)
[![isort](https://img.shields.io/badge/imports-isort-blue)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

We use several tools to maintain code quality:

```bash
# Run all pre-commit hooks
make lint

# Or run individual checks:
black .                    # Code formatting
ruff check .               # Linting
mypy src/                  # Type checking
isort .                    # Import sorting
bandit -r src/             # Security checks
pip-audit                  # Dependency vulnerability scanning
```

All these checks run automatically via pre-commit hooks when you commit.

### Coding Standards

- **Style**: Follow PEP 8, enforced by `black` and `ruff`
- **Type Hints**: All functions must have type hints (checked by `mypy --strict`)
- **Docstrings**: Use Google-style docstrings for all public functions
- **Line Length**: Maximum 140 characters
- **Imports**: Organized by `isort` with black profile
- **Security**: Pass `bandit` security checks

### Testing Standards

- Maintain test coverage >= 80%
- Write unit tests for all new functionality
- Use pytest fixtures for common test data
- Mock external API calls (OpenAI, Anthropic, etc.)
- Test both success and error cases

## Submitting Changes

### Before Submitting

1. Ensure all tests pass: `make test`
2. Ensure code quality checks pass: `make lint`
3. Update documentation if needed
4. Add your changes to the commit

### Creating a Pull Request

1. **Push your branch** to your fork

```bash
git push origin feature/your-feature-name
```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Description of changes
   - Related issue number (if applicable)
   - Testing performed
   - Screenshots (if UI changes)

4. **Respond to reviews** - maintainers may request changes

### Pull Request Requirements

- All CI checks must pass (tests, linting, CodeQL, Trivy)
- Code coverage must not decrease
- At least one approval from a maintainer
- Branch must be up to date with main

## Project Structure

```
mcp-toolz/
├── src/
│   ├── context_manager/     # CLI and core logic
│   │   ├── cli.py           # Click-based CLI
│   │   ├── storage.py       # SQLite storage layer
│   │   ├── openai_client.py # ChatGPT integration
│   │   ├── anthropic_client.py  # Claude integration
│   │   ├── gemini_client.py     # Gemini integration
│   │   └── deepseek_client.py   # DeepSeek integration
│   ├── mcp_server/          # MCP server implementation
│   │   └── server.py        # MCP protocol handlers
│   └── models.py            # Pydantic data models
├── tests/                   # Test suite
├── .github/                 # GitHub Actions workflows
├── pyproject.toml           # Project metadata and config
└── README.md               # User documentation
```

## Areas for Contribution

### Good First Issues

Look for issues labeled `good first issue` - these are great starting points for new contributors.

### Feature Ideas

- Additional AI model integrations
- Enhanced context management features
- Improved CLI user experience
- Better MCP server capabilities
- Documentation improvements

### Bug Reports

Found a bug? Please open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

## Security

Please report security vulnerabilities privately to **tleese22 [at] gmail [dot] com**. See [SECURITY.md](SECURITY.md) for details.

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues and PRs
- Read the [README.md](README.md) for usage documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in our release notes and can request to be added to the project's contributors list.

Thank you for contributing to mcp-toolz!
