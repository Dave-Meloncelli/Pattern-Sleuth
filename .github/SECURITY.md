# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Pattern Sleuth, please report it responsibly:

1. **Do not** open a public issue
2. Email: admin@rpgreliquary.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

We will respond within 48 hours and work with you to resolve the issue.

## Security Guarantees

Pattern Sleuth:

- **Runs locally** - No data leaves your machine
- **No network calls** - Works entirely offline
- **No telemetry** - We don't track usage
- **No secrets in code** - BYO API keys via environment variables
- **Static analysis only** - Does not execute your code

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes |

## Known Limitations

- Pattern Sleuth uses regex-based detection. It may produce false positives or miss some patterns.
- It does not perform dynamic analysis or execute code.
- Results should be reviewed by a human before taking action.
