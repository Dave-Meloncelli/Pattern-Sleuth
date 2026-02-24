# Contributing to Pattern Sleuth

Thanks for your interest in contributing! This guide will help you get started.

## Quick Links

- [Report a Bug](https://github.com/Dave-Meloncelli/pattern-sleuth/issues/new?template=bug.md)
- [Request a Pattern](https://github.com/Dave-Meloncelli/pattern-sleuth/issues/new?template=pattern.md)
- [Ask a Question](https://github.com/Dave-Meloncelli/pattern-sleuth/discussions)

## Ways to Contribute

### 1. Add New Patterns

The best way to improve Pattern Sleuth is to add patterns!

**Pattern Schema:**

```json
{
  "pattern_id": "unique_pattern_id",
  "title": "Human-Readable Title",
  "category": "code_quality|security|ai_behavior|process",
  "severity": "block|flag|warn|info",
  "description": "What this pattern detects",
  "detection": {
    "strategy": "regex",
    "signals": ["regex.*pattern.*here"]
  },
  "message": "What to tell the user when detected"
}
```

**Steps:**

1. Create a test case first in `tests/patterns/your_pattern_test.json`
2. Add your pattern to `pattern_sleuth/registry/patterns.json`
3. Run `pattern-sleuth test --pattern your_pattern.json`
4. Submit a PR

### 2. Improve Existing Patterns

- Reduce false positives
- Improve regex performance
- Add better messages
- Write more test cases

### 3. Fix Bugs

Check the [issue tracker](https://github.com/Dave-Meloncelli/pattern-sleuth/issues) for bugs.

### 4. Improve Documentation

- Fix typos
- Add examples
- Clarify explanations
- Translate documentation

## Development Setup

```bash
# Clone the repo
git clone https://github.com/Dave-Meloncelli/pattern-sleuth.git
cd pattern-sleuth

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Test CLI
pattern-sleuth scan . --verbose
```

## Testing Patterns

Before submitting a pattern, test it:

```bash
# Test a single pattern
pattern-sleuth test --pattern my-pattern.json --test-cases my-tests.json

# Test entire registry
pattern-sleuth test --registry pattern_sleuth/registry/patterns.json

# View results
pattern-sleuth test --registry pattern_sleuth/registry/patterns.json --output test-results.json
```

## Pattern Quality Standards

A good pattern should:

| Criteria | Target |
|----------|--------|
| Schema valid | ✅ 100% |
| Test coverage | ✅ ≥3 test cases |
| Accuracy | ✅ ≥80% |
| False positive rate | ✅ <10% |
| Performance | ✅ <100ms per file |

## Code Style

- Python 3.10+ syntax
- Type hints on public functions
- Docstrings on classes and public methods
- ASCII-only in core code (Tower compliance)
- No external dependencies in core engine

## Commit Messages

```
type(scope): brief description

- detail 1
- detail 2

Closes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

## Pull Request Process

1. Fork the repo
2. Create a feature branch (`feat/my-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Update documentation if needed
6. Submit PR with description

## Code of Conduct

- Be respectful
- Be constructive
- Focus on what's best for the community
- Show empathy towards others

## Questions?

Open a [discussion](https://github.com/Dave-Meloncelli/pattern-sleuth/discussions) or ask in your PR.
