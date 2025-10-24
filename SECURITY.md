# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of mcp-toolz seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **tleese22 [at] gmail [dot] com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report (if applicable):

- Type of issue (e.g., injection, privilege escalation, information disclosure, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

### Response Timeline

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will send you a more detailed response within 96 hours indicating the next steps in handling your report
- We will keep you informed about the progress towards a fix and full announcement
- We may ask for additional information or guidance

### Disclosure Policy

- We ask that you do not publicly disclose the vulnerability until we have released a fix
- We will credit you for the discovery when we announce the fix (unless you prefer to remain anonymous)
- When we receive a security bug report, we will confirm the problem, determine affected versions, audit code to find similar problems, and prepare fixes for all supported versions
- We will release new versions as soon as possible

### Preferred Languages

We prefer all communications to be in English.

## Security Best Practices

When using mcp-toolz:

1. **Protect API Keys**: Never commit API keys to version control. Use `.env` files or environment variables. The `.env.example` file provides a template.
2. **Database Security**: The SQLite database (`~/.mcp-toolz/contexts.db`) may contain sensitive conversation data, code snippets, and AI responses. Ensure appropriate file permissions (e.g., `chmod 600`).
3. **MCP Server**: When running as an MCP server, ensure your Claude Code configuration is secure and only accessible to authorized users.
4. **Updates**: Keep mcp-toolz updated to the latest version to receive security patches. Use `pip install --upgrade mcp-toolz`.
5. **Dependencies**: We actively monitor dependencies for vulnerabilities. Review security advisories before updating.
6. **Input Validation**: While mcp-toolz validates inputs, always sanitize data before storing sensitive information.

## Security Measures

mcp-toolz implements the following security measures:

- **Dependency Scanning**: Automated vulnerability scanning via Dependabot and GitHub's Dependency Review Action
- **Code Quality**: Pre-commit hooks with security linters:
  - `bandit` for Python security issues
  - `ruff` for code quality and security patterns
  - `mypy` for type safety
- **Static Analysis**: Strict type checking to prevent type-related bugs
- **License Compliance**: Automated license verification in CI/CD
- **SQL Injection Prevention**: Parameterized queries throughout the codebase (no string concatenation)
- **Input Validation**: Pydantic models for strict data validation
- **Least Privilege**: GitHub Actions use minimal required permissions
- **Secure Defaults**: Safe configuration defaults, explicit opt-in for sensitive features

## Continuous Monitoring

We continuously monitor security through:

- GitHub Dependabot alerts
- GitHub Security Advisories
- Pre-commit security checks
- Dependency Review on all pull requests
- Regular dependency updates

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue.
