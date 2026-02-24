# Pattern Sleuth - Domain Expansion Roadmap

## Vision

Pattern Sleuth is not just a code linter. It's a **Universal Pattern Detection Platform**. 

The same engine that detects anti-patterns in Python code can detect patterns in:
- Legal contracts
- Medical records
- Financial transactions
- Manufacturing logs
- Educational content
- Any structured data

---

## Current State: v1.0.0

| Capability | Domain | Status |
|------------|--------|--------|
| Code pattern detection | Software | ✅ Released |
| Documentation patterns | Software | ✅ Released |
| AI behavior patterns | Software | ✅ Released |
| Pattern test harness | Software | ✅ Released |
| Codebase discovery | Software | ✅ Released |

---

## Roadmap

### v1.1 - Enhanced Code Detection
- [ ] More language support (Go, Rust, Ruby, PHP)
- [ ] IDE integrations (VS Code, JetBrains)
- [ ] Pre-commit hooks
- [ ] CI/CD templates

### v2.0 - Domain Expansion

| Domain | Use Case | Pattern Types |
|--------|----------|---------------|
| **Legal** | Contract review | Missing clauses, risky terms, compliance gaps |
| **Healthcare** | Medical records | Diagnosis patterns, treatment gaps, documentation issues |
| **Finance** | Transactions | Fraud indicators, anomaly patterns, compliance violations |
| **Manufacturing** | Quality logs | Defect patterns, process deviations, equipment warnings |
| **Education** | Learning content | Misconception patterns, knowledge gaps, bias detection |

### v3.0 - Cross-Domain Intelligence

- **Pattern Translation**: Convert a medical diagnosis pattern into a debugging pattern
- **Meta-Patterns**: Patterns that describe patterns (universal structures)
- **Custom Domain Pack**: Create your own domain patterns

---

## Technical Foundation

The architecture already supports this:

```
pattern_sleuth/
  engine.py          <- Domain-agnostic detection engine
  registry/          <- Pattern definitions (can be ANY domain)
    patterns.json    <- Currently: code patterns
    legal.json       <- Future: contract patterns
    medical.json     <- Future: diagnosis patterns
    finance.json     <- Future: fraud patterns
  policy/            <- Severity/threshold rules per domain
```

### Adding a New Domain

```bash
# Create domain pack
pattern-sleuth create-domain --name legal --template

# Add patterns
pattern-sleuth add-pattern --domain legal --from-file my-patterns.json

# Test
pattern-sleuth test --registry legal/patterns.json

# Scan
pattern-sleuth scan ./contracts --domain legal
```

---

## Universal Pattern Schema

All domains use the same schema:

```json
{
  "pattern_id": "unique_id",
  "title": "Human Readable Title",
  "category": "category_name",
  "severity": "block|flag|warn|info",
  "description": "What this pattern detects",
  "detection": {
    "strategy": "regex|heuristic|ast|external",
    "signals": ["pattern1", "pattern2"]
  },
  "message": "User-friendly message",
  "domain": "code|legal|medical|finance|..."
}
```

---

## Business Value

| Metric | Code Only | Universal |
|--------|-----------|-----------|
| Addressable market | $500M | $5B+ |
| Industries | 1 | 10+ |
| Use cases | 5 | 50+ |
| Competitive moat | Low | High (no cross-domain competitor) |

---

## Research Opportunities

- Academic papers on cross-domain pattern transfer
- Patent potential for universal pattern language
- Industry partnerships (legal, healthcare, finance)

---

## Status

This roadmap is **planned**. Current release (v1.0.0) focuses on code patterns.

To express interest in specific domains, open an issue with label `domain-expansion`.

---

*Pattern Sleuth: Find what you missed. In any domain.*
