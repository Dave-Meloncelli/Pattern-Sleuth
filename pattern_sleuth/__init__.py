"""
Pattern Sleuth - Anti-Pattern Detection Engine
===============================================
A standalone tool for detecting negative patterns in code, documentation,
and AI-generated content.

Usage:
    from pattern_sleuth import PatternSleuth
    
    engine = PatternSleuth(root="/path/to/project")
    result = engine.scan()
    
    for finding in result.findings:
        print(f"{finding.severity}: {finding.title}")
"""

__version__ = "1.0.0"

from .engine import (
    PatternSleuth,
    PatternRegistry,
    PatternScanner,
    Finding,
    ScanResult,
    Decision,
    Severity,
    scan_roots,
    get_byo_root,
    get_byo_registry_path,
    get_byo_policy_path,
)

__all__ = [
    "PatternSleuth",
    "PatternRegistry",
    "PatternScanner",
    "Finding",
    "ScanResult",
    "Decision",
    "Severity",
    "scan_roots",
    "get_byo_root",
    "get_byo_registry_path",
    "get_byo_policy_path",
    "__version__",
]
