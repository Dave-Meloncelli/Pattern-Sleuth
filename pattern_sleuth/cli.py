#!/usr/bin/env python3
"""
Pattern Sleuth CLI
==================
Command-line interface for anti-pattern detection.
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import List
from datetime import datetime

from .engine import PatternSleuth, scan_roots, ScanResult

TAGLINES = [
    "Find what you missed.",
    "Your code has secrets. We find them.",
    "Detective work for your codebase.",
    "Patterns hiding in plain sight.",
    "The archaeology your code deserves.",
]

STATUS_MESSAGES = {
    "PASS": {
        "title": "All Clear!",
        "emoji": "PASS",
        "message": "No blocking patterns detected. Nice work, detective.",
    },
    "WARN": {
        "title": "Heads Up",
        "emoji": "WARN",
        "message": "Some warnings found. Worth a look when you have time.",
    },
    "FLAG": {
        "title": "Found Something",
        "emoji": "FLAG",
        "message": "High-priority patterns detected. You'll want to address these.",
    },
    "BLOCK": {
        "title": "Stop Right There",
        "emoji": "BLOCK",
        "message": "Critical patterns detected. Fix these before shipping.",
    },
}


def print_banner():
    """Print a friendly banner."""
    tagline = random.choice(TAGLINES)
    print()
    print("  ____                _     _     _   _ ")
    print(" |  _ \\ _ __ ___  ___| |__ | |__ | |_(_)")
    print(" | |_) | '__/ _ \\/ __| '_ \\| '_ \\| __| |")
    print(" |  __/| | | (_) \\__ \\ | | | |_) | |_| |")
    print(" |_|   |_|  \\___/|___/_| |_|_.__/ \\__|_|")
    print()
    print(f"  {tagline}")
    print()


def print_report(result: ScanResult, verbose: bool = False, show_low_quality: bool = False):
    """Print human-readable report with personality."""
    print(f"\n{'~'*60}")
    print(f"  SCAN RESULTS")
    print(f"{'~'*60}")
    
    print(f"\n  Scanned {result.files_scanned} files at {result.generated_at[11:19]}")
    
    status = STATUS_MESSAGES.get(result.decision, STATUS_MESSAGES["WARN"])
    print(f"\n  [{status['emoji']}] {status['title']}")
    print(f"      {status['message']}")
    
    high_q = sum(1 for f in result.findings if f.details.get("quality_tier") == "high")
    med_q = sum(1 for f in result.findings if f.details.get("quality_tier") == "medium")
    low_q = sum(1 for f in result.findings if f.details.get("quality_tier") in ("low", "experimental", None))
    
    print(f"\n  By Quality Tier:")
    print(f"    High confidence:    {high_q:3}")
    print(f"    Medium confidence:  {med_q:3}")
    print(f"    Low/experimental:   {low_q:3}")
    
    print(f"\n  By Severity:")
    print(f"    Critical:  {result.summary.get('critical', 0):3}  (must fix)")
    print(f"    High:      {result.summary.get('high', 0):3}  (should fix)")
    print(f"    Medium:    {result.summary.get('medium', 0):3}  (consider)")
    print(f"    Low:       {result.summary.get('low', 0) + result.summary.get('info', 0):3}  (info)")
    print(f"    -----------")
    print(f"    Total:     {result.summary.get('total', 0):3}")
    
    display_findings = [f for f in result.findings if f.details.get("quality_tier") != "low" or show_low_quality]
    
    if display_findings and verbose:
        print(f"\n  Findings (showing {min(10, len(display_findings))} of {len(display_findings)}):")
        for f in display_findings[:10]:
            sev = f.severity.lower()
            severity_icon = {"critical": "X", "block": "X", "high": "!", "flag": "!", "medium": "?", "warn": "?", "low": "-", "info": "-"}.get(sev, "•")
            quality = f.details.get("quality_tier", "med")
            print(f"\n    [{severity_icon}] {f.title} [{quality}]")
            print(f"        {f.file}:{f.line or '-'}")
            print(f"        {f.message}")
        
        if len(display_findings) > 10:
            print(f"\n    ... and {len(display_findings) - 10} more findings")
    elif result.findings and not verbose:
        high_conf = [f for f in result.findings if f.details.get("quality_tier") == "high"]
        if high_conf:
            print(f"\n  Top High-Confidence Findings:")
            for f in high_conf[:5]:
                print(f"    - {f.title} ({f.file}:{f.line or '-'})")
    
    print(f"\n{'~'*60}")
    
    if result.decision == "PASS":
        print("  Ready to ship! Your code looks clean.")
    elif result.decision == "BLOCK":
        print("  Don't ship yet. Fix the critical issues above.")
    else:
        print(f"  Run with --verbose to see all {result.summary.get('total', 0)} findings.")
    
    print(f"{'~'*60}\n")


def cmd_scan(args):
    """Handle scan subcommand."""
    paths = [Path(p) for p in args.paths]
    
    registry_path = Path(args.registry) if args.registry else None
    policy_path = Path(args.policy) if args.policy else None
    
    engine = PatternSleuth(
        root=paths[0] if paths else None,
        registry_path=registry_path,
        policy_path=policy_path,
    )
    
    result = engine.scan(targets=paths)
    
    # Filter by scope
    scope = getattr(args, 'scope', 'universal')
    
    # Categories for universal patterns (work on any codebase)
    # These match the 'category' field in patterns, not the registry section
    universal_categories = [
        # AI behavior
        'adversarial_security', 'ai_workflow', 'software_engineering_ai',
        # AI code drift
        'code_quality', 'translation_loss',
        # Universal process/standards
        'universal_process', 'universal_standards',
        'process', 'standards',  # Some patterns use these generically
        'forensic', 'behavioral_drift', 'reasoning_failure', 'safety_guardrails',
        # Additional categories used by universal patterns
        'security',  # Some AI behavior patterns are categorized as security
    ]
    
    # Categories for Federation-specific patterns
    federation_categories = [
        'federation_process', 'federation_standards'
    ]
    
    if scope == 'universal':
        result.findings = [f for f in result.findings if f.category in universal_categories]
    elif scope == 'federation':
        result.findings = [f for f in result.findings if f.category in federation_categories]
    # 'all' or anything else = no filtering
    
    # Recalculate summary
    if scope in ['universal', 'federation']:
        result.summary = {
            'critical': sum(1 for f in result.findings if f.severity in ['critical', 'block']),
            'high': sum(1 for f in result.findings if f.severity in ['high', 'flag']),
            'medium': sum(1 for f in result.findings if f.severity in ['medium', 'warn']),
            'low': sum(1 for f in result.findings if f.severity in ['low', 'info']),
            'total': len(result.findings),
        }
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Results written to: {output_path}")
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_report(result, verbose=args.verbose, show_low_quality=getattr(args, 'all', False))
        print(f"\n  Scope: {scope}")
        if scope == 'universal':
            print("    (49 universal patterns - works on any codebase)")
        elif scope == 'federation':
            print("    (10 Federation-specific patterns)")
        elif scope == 'all':
            print("    (59 sovereign patterns: universal + federation)")
    
    return 0 if result.decision == "PASS" else 1


def cmd_list(args):
    """Handle list subcommand."""
    from .engine import PatternRegistry
    
    registry_path = Path(args.registry) if args.registry else None
    registry = PatternRegistry(registry_path)
    
    if args.category:
        patterns = registry.get_patterns_for_category(args.category)
    else:
        patterns = registry.get_all_patterns()
    
    if args.json:
        print(json.dumps(patterns, indent=2))
    else:
        print(f"\n{len(patterns)} patterns in registry:\n")
        
        by_category = {}
        for p in patterns:
            cat = p.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(p)
        
        for category, cats_patterns in sorted(by_category.items()):
            print(f"[{category}]")
            for p in cats_patterns:
                sev = p.get("severity", "warn")
                print(f"  [{sev:6}] {p.get('pattern_id', '?'):40} - {p.get('title', '?')}")
            print()
    
    return 0


def cmd_test(args):
    """Handle test subcommand - test patterns against test cases."""
    from .test_harness import PatternTestHarness
    
    harness = PatternTestHarness()
    batch_result = None
    
    if args.test_cases:
        harness.load_test_cases(Path(args.test_cases))
    
    if args.pattern:
        with open(args.pattern, 'r', encoding='utf-8') as f:
            pattern = json.load(f)
        result = harness.test_pattern(pattern)
        results = [result]
    elif args.registry:
        batch_result = harness.test_registry(Path(args.registry))
        results = batch_result.pattern_results
    else:
        print("Specify --pattern or --registry")
        return 1
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if batch_result:
            output_data = batch_result.to_dict()
        else:
            output_data = [r.to_dict() for r in results]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)
        print(f"Results written to: {output_path}")
    
    if args.json:
        if batch_result:
            print(json.dumps(batch_result.to_dict(), indent=2))
        else:
            print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"PATTERN TEST RESULTS")
        print(f"{'='*60}")
        
        for r in results:
            status = "PASS" if r.accuracy >= 0.8 and r.valid_schema else "FAIL"
            print(f"\n[{status}] {r.pattern_id}")
            print(f"  Schema valid: {r.valid_schema}")
            print(f"  Tests: {r.passed}/{r.total_tests} passed")
            print(f"  Accuracy: {r.accuracy:.1%}")
            if r.false_positives > 0:
                print(f"  False positives: {r.false_positives}")
            if r.false_negatives > 0:
                print(f"  False negatives: {r.false_negatives}")
            if r.schema_errors:
                print(f"  Schema errors: {r.schema_errors[:2]}")
        
        print(f"\n{'='*60}\n")
    
    failed = sum(1 for r in results if r.accuracy < 0.8 or not r.valid_schema)
    return 0 if failed == 0 else 1


def cmd_discover(args):
    """Handle discover subcommand."""
    from .discovery import discover_codebase
    
    codebase_path = Path(args.path)
    if not codebase_path.exists():
        print(f"Path not found: {codebase_path}")
        return 1
    
    result = discover_codebase(codebase_path)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        print(f"Report written to: {output_path}")
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"CODEBASE DISCOVERY REPORT")
        print(f"{'='*60}")
        print(f"Path: {result.codebase_path}")
        print(f"Files scanned: {result.total_files}")
        print(f"Lines scanned: {result.total_lines}")
        
        print(f"\n--- NAMING CONVENTIONS ---")
        for np in result.naming_patterns:
            print(f"  {np.pattern_type:10}: {np.style:15} ({np.confidence:.0%} consistent)")
            if np.examples:
                print(f"              examples: {', '.join(np.examples[:3])}")
        
        print(f"\n--- CODE STRUCTURE ---")
        for sp in result.structure_patterns:
            print(f"  {sp.pattern_id}: {sp.description} ({sp.file_count} files)")
        
        if result.domain_terms:
            print(f"\n--- DOMAIN VOCABULARY (top 15) ---")
            for dt in result.domain_terms[:15]:
                print(f"  {dt.term:20}: {dt.frequency:4}x in {dt.context}")
        
        if result.anti_patterns:
            print(f"\n--- ANTI-PATTERNS ---")
            for a in result.anti_patterns:
                print(f"  [{a['severity']}] {a['type']}: {a['description']}")
        
        if result.recommendations:
            print(f"\n--- RECOMMENDATIONS ---")
            for r in result.recommendations:
                print(f"  [{r['priority']}] {r['category']}: {r['issue']}")
                print(f"      -> {r['recommendation']}")
        
        print(f"\n{'='*60}\n")
    
    return 0


def cmd_validate(args):
    """Handle validate subcommand."""
    from .engine import PatternRegistry
    
    issues = []
    registry = None
    
    registry_path = Path(args.registry) if args.registry else None
    if registry_path and not registry_path.exists():
        issues.append(f"Registry not found: {registry_path}")
    
    try:
        registry = PatternRegistry(registry_path)
        if not registry.patterns:
            issues.append("No patterns loaded from registry")
    except Exception as e:
        issues.append(f"Registry load error: {e}")
    
    if args.json:
        print(json.dumps({
            "valid": len(issues) == 0,
            "issues": issues,
            "patterns_loaded": len(registry.patterns) if registry else 0,
        }, indent=2))
    else:
        if issues:
            print("Validation FAILED:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Validation PASSED")
            if registry:
                print(f"  Patterns loaded: {len(registry.patterns)}")
    
    return 0 if len(issues) == 0 else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="pattern-sleuth",
        description="Detect anti-patterns in code, docs, and AI-generated content",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    scan_parser = subparsers.add_parser("scan", help="Scan files or directories")
    scan_parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to scan (default: current directory)",
    )
    scan_parser.add_argument(
        "--registry", "-r",
        help="Path to pattern registry JSON",
    )
    scan_parser.add_argument(
        "--policy", "-p",
        help="Path to policy JSON",
    )
    scan_parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON)",
    )
    scan_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout",
    )
    scan_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed findings",
    )
    scan_parser.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all",
        help="Show all findings including low-confidence",
    )
    scan_parser.add_argument(
        "--scope", "-s",
        choices=["universal", "federation", "all"],
        default="universal",
        help="Pattern scope: universal (49 patterns, works anywhere), federation (10 patterns, Fed-only), all (59 patterns)",
    )
    
    list_parser = subparsers.add_parser("list", help="List available patterns")
    list_parser.add_argument(
        "--category", "-c",
        help="Filter by category",
    )
    list_parser.add_argument(
        "--registry", "-r",
        help="Path to pattern registry JSON",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument(
        "--registry", "-r",
        help="Path to pattern registry JSON",
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    discover_parser = subparsers.add_parser("discover", help="Discover patterns in a codebase")
    discover_parser.add_argument(
        "path",
        default=".",
        nargs="?",
        help="Path to codebase to analyze",
    )
    discover_parser.add_argument(
        "--output", "-o",
        help="Output file for report (JSON)",
    )
    discover_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout",
    )
    
    test_parser = subparsers.add_parser("test", help="Test patterns against test cases")
    test_parser.add_argument(
        "--pattern", "-p",
        help="Path to single pattern JSON to test",
    )
    test_parser.add_argument(
        "--registry", "-r",
        help="Path to pattern registry to test all patterns",
    )
    test_parser.add_argument(
        "--test-cases", "-t",
        help="Path to test cases JSON file or directory",
    )
    test_parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON)",
    )
    test_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON to stdout",
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "discover":
        return cmd_discover(args)
    elif args.command == "test":
        return cmd_test(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
