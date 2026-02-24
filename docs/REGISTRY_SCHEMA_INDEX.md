# Pattern Registry Schema Index

## Overview

This document defines the alignment between pattern schemas, domains, and file type routing.

---

## Schema Alignment

### Two Pattern Formats

| Format | Source File | Detection Field |
|--------|-------------|-----------------|
| **Standard** | `patterns.json` | `detection.signals` array |
| **Forensic** | `forensic_intel.json` | `regex` string (normalized on load) |

**Both formats are normalized to standard format at load time by `PatternRegistry`.**

---

## Domain Attribution

### Domain Values

| Domain | Meaning | FiletypeSluice Behavior |
|--------|---------|-------------------------|
| `ai_output` | AI-generated content only | Only fires on `.txt`, `.log`, `.chat`, `.conversation` |
| `any` | All file types | Fires on any file (respecting `languages` filter) |
| NOT_SET | Legacy - defaults to `any` | Fires on any file |

### Category → Domain Mapping

These categories **MUST** have `domain: ai_output`:

- `adversarial_security` (except ADV_005 XSS which is `any`)
- `behavioral_drift`
- `reasoning_failure`
- `safety_guardrails`
- `agentic_architectural`
- `software_engineering_ai`
- `ai_workflow`

These categories **MUST** have `domain: any`:

- `code_quality`
- `process`
- `standards`
- `security`
- `translation_loss`
- `wind_ops`

---

## FiletypeSluice Routing

### Route Definitions

| SluiceType | Extensions | Patterns Apply | Patterns Skip |
|------------|------------|----------------|---------------|
| PYTHON | `.py`, `.pyw`, `.pyi` | code_quality, security, process, standards | ai_output |
| TYPESCRIPT | `.ts`, `.tsx` | code_quality, security, typescript_specific | ai_output |
| JAVASCRIPT | `.js`, `.jsx` | code_quality, security, javascript_specific | ai_output |
| MARKDOWN | `.md`, `.markdown` | documentation, standards, security | - |
| AI_OUTPUT | `.txt`, `.log`, `.chat` | ai_behavior, safety_guardrails, behavioral_drift, adversarial_security | code_quality |
| GENERIC | (catch-all) | security | ai_output, language_specific |

### Filtering Logic

1. **Domain Check**: If `domain == "ai_output"`, only apply to AI_OUTPUT file types
2. **Language Check**: If `languages` is set, check file extension matches
3. **Category Check**: If category in `patterns_skip`, exclude pattern

---

## Required Fields by Pattern Type

### Standard Pattern (patterns.json)

```json
{
  "pattern_id": "required string",
  "title": "required string",
  "category": "required: code_quality|process|standards|security|translation_loss|wind_ops|ai_workflow",
  "severity": "required: block|flag|warn",
  "domain": "required: ai_output|any",
  "detection": {
    "strategy": "required: regex|heuristic|external|manual",
    "signals": "required array of strings"
  }
}
```

### Forensic Pattern (forensic_intel.json)

```json
{
  "id": "required string",
  "name": "required string",
  "regex": "required string",
  "severity": "required: CRITICAL|HIGH|MEDIUM|LOW",
  "domain": "required: ai_output|any",
  "quality_tier": "optional: high|medium|low",
  "precision_estimate": "optional: 0.0-1.0"
}
```

---

## Test Harness Requirements

### Test Case Format

```json
{
  "pattern_id": [
    {"id": "tp_1", "content": "text to match", "should_match": true, "description": "why"},
    {"id": "tn_1", "content": "text not to match", "should_match": false, "description": "why"}
  ]
}
```

### Test Harness Behavior

1. Normalize pattern (convert `regex` field to `detection.signals`)
2. Use **normalized** pattern for test execution
3. Report schema validation errors
4. Calculate precision/recall/accuracy

---

## Changelog

- 2026-02-20: Initial index creation after alignment audit
