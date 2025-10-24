# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in mcp-toolz, please report it by emailing **tleese22 [at] gmail [dot] com** rather than opening a public issue.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

### Response Timeline

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a detailed response indicating next steps within 5 business days
- We will work on a fix and release a patch as quickly as possible, depending on complexity

### Disclosure Policy

- We ask that you do not publicly disclose the vulnerability until we have released a fix
- We will credit you for the discovery when we announce the fix (unless you prefer to remain anonymous)

## Security Best Practices

When using mcp-toolz:

1. **API Keys**: Never commit API keys to version control. Always use environment variables (`.env` file)
2. **Database Security**: Ensure your `contexts.db` file has appropriate permissions if it contains sensitive information
3. **Updates**: Keep mcp-toolz and its dependencies up to date to receive the latest security patches

## Dependencies

We use Dependabot to automatically monitor and update dependencies with known security vulnerabilities.
