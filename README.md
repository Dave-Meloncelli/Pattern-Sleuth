# Pattern Sleuth

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Anti-pattern detection engine for code, documentation, and AI-generated content.**

Detects 97 patterns including security issues, code quality problems, and AI behavior anomalies. Zero dependencies, fully configurable, MIT licensed.

## Installation

```bash
pip install pattern-sleuth
```

Or with pipx for isolated installation:

```bash
pipx install pattern-sleuth
```

## Quick Start

```bash
# Scan current directory
pattern-sleuth scan .

# Scan specific paths
pattern-sleuth scan ./src ./tests

# Output as JSON
pattern-sleuth scan ./src --json > results.json

# Verbose output with detailed findings
pattern-sleuth scan ./src --verbose

# Show all findings including low-confidence
pattern-sleuth scan ./src --all
```

## Features

- **97 Built-in Patterns**: Code quality, security, AI behavior, process patterns
- **Smart Filtering**: Quality-tiered results, file-type routing (AI patterns only on AI outputs)
- **Zero Dependencies**: Pure Python, no external libraries required
- **Configurable**: Custom pattern registries, policies, and severity levels
- **Multiple Output Formats**: Human-readable, JSON, or programmatic API
- **CI/CD Ready**: Exit codes for PASS/WARN/FLAG/BLOCK decisions
- **Extensible**: Add your own patterns via JSON registry

## Pattern Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **code_quality** | Code smells and anti-patterns | Placeholder returns, empty implementations, TODOs |
| **security** | Security vulnerabilities | Prompt injection, exposed secrets, XSS patterns |
| **ai_behavior** | AI-specific patterns (for AI outputs only) | Instruction drift, silent refusal, identity confusion |
| **process** | Workflow violations | Missing checks, bypassed gates, incomplete workflows |

## Quality Tiers

Patterns are rated by confidence level:

| Tier | Description | Default Display |
|------|-------------|-----------------|
| **High** | Well-tested, low false-positive rate | Always shown |
| **Medium** | Good signals, some context needed | Always shown |
| **Low/Experimental** | Exploratory patterns | Use `--all` to show |

## Commands

```bash
# Scan files or directories
pattern-sleuth scan /path/to/project

# List all available patterns
pattern-sleuth list

# List patterns by category
pattern-sleuth list --category security

# Discover patterns in a codebase (archaeology mode)
pattern-sleuth discover /path/to/codebase

# Validate configuration
pattern-sleuth validate

# Test patterns against test cases
pattern-sleuth test --registry ./registry.json
```

## Usage

### Command Line

```bash
# Basic scan
pattern-sleuth scan /path/to/project

# With custom registry
pattern-sleuth scan /path/to/project --registry ./my-patterns.json

# Output to file
pattern-sleuth scan /path/to/project --output results.json

# JSON output to stdout
pattern-sleuth scan /path/to/project --json
```

### Programmatic

```python
from pattern_sleuth import PatternSleuth

# Create engine
engine = PatternSleuth(
    root="/path/to/project",
    registry_path="/path/to/custom-registry.json",
)

# Run scan
result = engine.scan()

# Check decision
if result.decision == "BLOCK":
    print("Critical issues found!")
    for finding in result.findings:
        if finding.severity == "critical":
            print(f"  {finding.file}:{finding.line} - {finding.title}")

# Get summary
print(f"Scanned {result.files_scanned} files")
print(f"Found {result.summary['total']} patterns")

# Check quality tiers
for finding in result.findings:
    quality = finding.details.get("quality_tier", "medium")
    print(f"  [{quality}] {finding.title}")
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS - No blocking patterns |
| 1 | WARN/FLAG/BLOCK - Issues found |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PATTERN_SLEUTH_ROOT` | Base directory for operations | Current working directory |
| `PATTERN_SLEUTH_REGISTRY_PATH` | Path to pattern registry JSON | Built-in registry |
| `PATTERN_SLEUTH_POLICY_PATH` | Path to policy JSON | Built-in policy |

### Custom Pattern Registry

Create a JSON file with your patterns:

```json
{
  "registry_version": "1.0.0",
  "entries": [
    {
      "pattern_id": "custom_no_print_debug",
      "title": "Debug print statement",
      "category": "code_quality",
      "severity": "warn",
      "languages": ["python"],
      "detection": {
        "strategy": "regex",
        "signals": ["print\\s*\\(.*debug"]
      },
      "message": "Debug print statement found"
    }
  ]
}
```

### Pattern Properties

| Property | Description |
|----------|-------------|
| `pattern_id` | Unique identifier (snake_case) |
| `title` | Human-readable title |
| `category` | Pattern category |
| `severity` | `block`, `flag`, `warn`, or `info` |
| `languages` | Target languages (e.g., `["python"]`, `["typescript"]`) |
| `domain` | `any` or `ai_output` (AI patterns only match non-code files) |
| `quality_tier` | `high`, `medium`, `low`, or `experimental` |
| `detection.signals` | Regex patterns to detect |

## CI/CD Integration

### GitHub Actions

```yaml
name: Pattern Check

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install pattern-sleuth
        run: pip install pattern-sleuth
      
      - name: Run scan
        run: pattern-sleuth scan ./src --json > results.json
      
      - name: Check results
        run: |
          if [ $? -ne 0 ]; then
            echo "Pattern check failed - see results.json"
            exit 1
          fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pattern-sleuth
        name: Pattern Sleuth
        entry: pattern-sleuth scan
        language: system
        types: [python]
        pass_filenames: false
        args: [.]
```

## Why Pattern Sleuth?

Traditional linters focus on syntax and style. Pattern Sleuth focuses on **semantic patterns** — the kind of issues that indicate deeper problems:

- **Placeholder code** that passes reviews but fails in production
- **Security anti-patterns** that standard scanners miss
- **Process violations** that indicate workflow problems

### Smart Routing

Pattern Sleuth uses a **filetype sluice** to route patterns intelligently:

- Python files → Code quality, security patterns only
- TypeScript/JavaScript → Language-specific patterns
- AI output files (.txt, .log, .chat) → AI behavior patterns

This prevents false positives from AI patterns matching words like "understand" in your Python code.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

## Changelog

### 1.0.0 (2026-02-23)
- Initial release
- 97 built-in patterns across 8 categories
- FiletypeSluice for smart pattern routing
- Quality-tiered filtering (high/medium/low)
- CLI with scan, list, validate, discover, test commands
- Zero external dependencies
- Custom registry support
- CI/CD integration
