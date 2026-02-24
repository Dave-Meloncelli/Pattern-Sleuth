# Pattern Quality & Intent Framework

## Problem

Finding 1800+ patterns is noise if they're all low-quality. Users need:
- **Quality score** - How confident is this pattern?
- **Intent context** - Why does this pattern exist?
- **Signal-to-noise ratio** - Only show what matters

---

## Pattern Quality Dimensions

| Dimension | What It Measures | Low (1) | High (5) |
|-----------|-----------------|---------|----------|
| **Precision** | How often is this a real issue? | Many false positives | Almost always real |
| **Impact** | How bad is it if true? | Minor style issue | Security vuln / blocker |
| **Actionability** | Can user do something? | Vague warning | Clear fix |
| **Context** | Does context matter? | Always bad | Depends on situation |

---

## Pattern Tiers

### Tier 1: High Confidence (Show Always)
- Security vulnerabilities with clear exploit paths
- Placeholder code in validation functions
- Injection patterns with clear indicators
- **Signal: 90%+ true positive rate**

### Tier 2: Medium Confidence (Show in verbose)
- TODO/FIXME markers
- Naming violations
- Missing documentation
- **Signal: 50-90% true positive rate**

### Tier 3: Low Confidence (Show only on request)
- Style preferences
- Maybes and might-bes
- Context-dependent issues
- **Signal: <50% true positive rate**

---

## Result Presentation Philosophy

### Current Problem
```
FINDINGS: 1857
Critical: 26
High: 677
```
This is overwhelming. User sees "BLOCK" and 1857 issues but doesn't know what matters.

### Better Approach

**1. Priority Stack** (show top 5-10 by impact)
```
CRITICAL ISSUES (fix now):
  1. [sec_injection] Line 45 - SQL injection risk
  2. [neg_placeholder] validate() returns True - bypass risk
  
ACTIONABLE WARNINGS (fix soon):
  3. TODO at line 120
  4. Hardcoded path at line 200
  
NOISE (suppressed - 1843 low-signal findings)
```

**2. By Category Summary**
```
Security:     2 issues (1 critical, 1 high)
Quality:      5 issues (2 high, 3 medium)
Style:        1843 issues (suppressed - use --all to see)
```

**3. Intent Tags**
Each finding shows *why* it matters:
```
[sec_injection] "Attacker could execute arbitrary SQL"
[neg_placeholder] "Validation can be bypassed"
[neg_todo] "Incomplete work tracked"
```

---

## Implementation

1. Add `quality_tier` field to patterns
2. Add `intent` field explaining why pattern exists
3. Add `true_positive_estimate` based on testing
4. Filter results by tier in presentation
5. Summarize noise separately from signal

---

## Quality Scoring Formula

```
pattern_quality = (precision * 0.4) + (impact * 0.3) + (actionability * 0.2) + (context_fit * 0.1)
```

Where each dimension is 1-5.

**High Quality**: score >= 3.5
**Medium Quality**: 2.0 <= score < 3.5  
**Low Quality**: score < 2.0

---

## Default Behavior

- **Show**: All high-quality findings
- **Summarize**: Medium-quality by category
- **Suppress**: Low-quality unless --all flag

This makes the tool *useful* instead of *noisy*.
