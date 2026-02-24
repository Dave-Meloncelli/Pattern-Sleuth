"""
PATTERN_SLEUTH - Anti-Pattern Detection Engine
===============================================
A standalone tool for detecting negative patterns in code, documentation,
and AI-generated content. Zero external dependencies required.

MIT Licensed - Use anywhere, configure paths via environment or parameters.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Sequence
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from .sluice import FiletypeSluice, SluiceType


def parse_signal(signal: str) -> Optional[str]:
    """
    Parse a signal string into a usable regex.
    
    Args:
        signal: Raw signal string which may contain regex patterns or
                description-style signals like 'line matches `...`'.
    
    Returns:
        Extracted regex pattern string, or None if signal cannot be parsed.
    """
    if not signal:
        return None
    
    if signal.startswith('line matches `') and signal.endswith('`'):
        return signal[14:-1]
    if signal.startswith('or matches `') and signal.endswith('`'):
        return signal[12:-1]
    if signal.startswith('matches `') and signal.endswith('`'):
        return signal[9:-1]
    if signal.startswith('contains `') and signal.endswith('`'):
        return signal[10:-1]
    
    if 'context window' in signal.lower():
        return None
    
    if re.match(r'^[\w\s\-{}()\[\]\\^$.*+?|]+$', signal):
        return signal
    
    return signal


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Decision(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FLAG = "FLAG"
    BLOCK = "BLOCK"


@dataclass
class Finding:
    pattern_id: str
    title: str
    category: str
    severity: str
    file: str
    line: Optional[int]
    excerpt: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScanResult:
    generated_at: str
    decision: str
    reasons: List[str]
    files_scanned: int
    findings: List[Finding]
    summary: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "decision": self.decision,
            "reasons": self.reasons,
            "files_scanned": self.files_scanned,
            "findings_count": len(self.findings),
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
        }


def get_byo_root() -> Path:
    """Get the root directory from environment or default to cwd."""
    return Path(os.environ.get("PATTERN_SLEUTH_ROOT", Path.cwd()))


def get_byo_registry_path() -> Path:
    """Get registry path from environment or default."""
    env_path = os.environ.get("PATTERN_SLEUTH_REGISTRY_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).parent / "registry" / "patterns.json"


def get_byo_policy_path() -> Path:
    """Get policy path from environment or default."""
    env_path = os.environ.get("PATTERN_SLEUTH_POLICY_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).parent / "policy" / "policy.json"


class PatternRegistry:
    """Loads and manages pattern definitions from JSON registry."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or get_byo_registry_path()
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self._load()
    
    def _load(self):
        """Load patterns from registry file."""
        if not self.registry_path.exists():
            self._load_defaults()
            return
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = data.get("entries", [])
            for entry in entries:
                pattern_id = entry.get("pattern_id")
                if pattern_id:
                    self.patterns[pattern_id] = entry
                    
                    category = entry.get("category", "general")
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(pattern_id)
            
            for category, patterns in data.items():
                if category not in ["registry_version", "entries", "intent", "entry_schema", "master_list_mapping", "evidence_sources_catalog", "notes"]:
                    if isinstance(patterns, list):
                        for p in patterns:
                            pid = p.get("id") or p.get("pattern_id")
                            if pid:
                                pattern_entry = dict(p)
                                pattern_entry["category"] = category
                                self.patterns[pid] = pattern_entry
                                if category not in self.categories:
                                    self.categories[category] = []
                                self.categories[category].append(pid)
            
            forensic_path = self.registry_path.parent / "forensic_intel.json"
            if forensic_path.exists():
                try:
                    with open(forensic_path, 'r', encoding='utf-8') as f:
                        forensic_data = json.load(f)
                    for category, patterns in forensic_data.items():
                        if isinstance(patterns, list):
                            for p in patterns:
                                pid = p.get("id") or p.get("pattern_id")
                                if pid:
                                    pattern_entry = dict(p)
                                    pattern_entry["pattern_id"] = pid
                                    pattern_entry["title"] = p.get("name") or p.get("title") or pid
                                    pattern_entry["category"] = category
                                    pattern_entry["severity"] = (p.get("severity") or "warn").lower()
                                    pattern_entry["languages"] = p.get("languages", ["any"])
                                    pattern_entry["domain"] = p.get("domain", "any")
                                    pattern_entry["quality_tier"] = p.get("quality_tier", "medium")
                                    pattern_entry["precision_estimate"] = p.get("precision_estimate", 0.5)
                                    if "detection" not in pattern_entry and "regex" in p:
                                        pattern_entry["detection"] = {
                                            "strategy": "regex",
                                            "signals": [p["regex"]]
                                        }
                                    self.patterns[pid] = pattern_entry
                                    if category not in self.categories:
                                        self.categories[category] = []
                                    self.categories[category].append(pid)
                except Exception:
                    pass
            
            # Load additional language-specific pattern files
            for pattern_file in ["typescript_patterns.json", "java_patterns.json", "attack_vector_patterns.json", "cwe_top25_patterns.json", "mined_patterns.json"]:
                lang_path = self.registry_path.parent / pattern_file
                if lang_path.exists():
                    try:
                        with open(lang_path, 'r', encoding='utf-8') as f:
                            lang_data = json.load(f)
                        for entry in lang_data.get("entries", []):
                            pid = entry.get("pattern_id")
                            if pid and pid not in self.patterns:
                                self.patterns[pid] = entry
                                category = entry.get("category", "general")
                                if category not in self.categories:
                                    self.categories[category] = []
                                self.categories[category].append(pid)
                    except Exception:
                        pass
                                
        except Exception as e:
            self._load_defaults()
    
    def _load_defaults(self):
        """Load built-in default patterns."""
        self.patterns = {
            "neg_placeholder_return_true": {
                "pattern_id": "neg_placeholder_return_true",
                "title": "Placeholder return True",
                "category": "code_quality",
                "severity": "block",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"return\s+True\s*#.*placeholder", r"return\s+True\s*$"]
                },
                "message": "Function returns True without real validation"
            },
            "neg_placeholder_not_implemented": {
                "pattern_id": "neg_placeholder_not_implemented",
                "title": "NotImplementedError stub",
                "category": "code_quality",
                "severity": "block",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"raise\s+NotImplementedError"]
                },
                "message": "Incomplete implementation - NotImplementedError raised"
            },
            "neg_todo_fixme": {
                "pattern_id": "neg_todo_fixme",
                "title": "TODO/FIXME markers",
                "category": "code_quality",
                "severity": "flag",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"#\s*TODO", r"#\s*FIXME", r"//\s*TODO", r"//\s*FIXME"]
                },
                "message": "Unresolved TODO/FIXME marker"
            },
            "neg_empty_pass": {
                "pattern_id": "neg_empty_pass",
                "title": "Empty implementation (pass)",
                "category": "code_quality",
                "severity": "flag",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"def\s+\w+\([^)]*\):\s*pass\s*$"]
                },
                "message": "Empty function body - pass only"
            },
            "sec_prompt_injection": {
                "pattern_id": "sec_prompt_injection",
                "title": "Prompt injection pattern",
                "category": "security",
                "severity": "block",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"ignore\s+all\s+previous\s+instructions", r"forget\s+everything"]
                },
                "message": "Potential prompt injection pattern detected"
            },
            "sec_exposed_secret": {
                "pattern_id": "sec_exposed_secret",
                "title": "Exposed secret/credential",
                "category": "security",
                "severity": "block",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", r"password\s*=\s*['\"][^'\"]+['\"]"]
                },
                "message": "Potential exposed secret or credential"
            },
            "ai_instruction_drift": {
                "pattern_id": "ai_instruction_drift",
                "title": "AI instruction drift",
                "category": "ai_behavior",
                "severity": "flag",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"drift|ignoring.*instruction|bypassing.*protocol"]
                },
                "message": "Potential AI instruction drift pattern"
            },
            "ai_silent_refusal": {
                "pattern_id": "ai_silent_refusal",
                "title": "AI silent refusal",
                "category": "ai_behavior",
                "severity": "warn",
                "detection": {
                    "strategy": "regex",
                    "signals": [r"I\s+cannot\s+assist", r"I'm\s+not\s+able\s+to"]
                },
                "message": "Potential AI refusal pattern"
            },
        }
        
        for pid in self.patterns:
            category = self.patterns[pid].get("category", "general")
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(pid)
    
    def get_patterns_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all patterns for a category."""
        pattern_ids = self.categories.get(category, [])
        return [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]
    
    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all patterns."""
        return list(self.patterns.values())


class PatternScanner:
    """Scans files and content for patterns."""
    
    def __init__(self, registry: Optional[PatternRegistry] = None):
        self.registry = registry or PatternRegistry()
        self.sluice = FiletypeSluice()
    
    def scan_file(self, file_path: Path, content: Optional[str] = None, min_quality: str = "low") -> List[Finding]:
        """Scan a single file for patterns."""
        findings = []
        
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                return findings
        
        lines = content.split('\n')
        
        all_patterns = self.registry.get_all_patterns()
        filtered_patterns = self.sluice.filter_patterns(file_path, all_patterns)
        
        quality_order = {"high": 0, "medium": 1, "low": 2, "experimental": 3}
        min_quality_level = quality_order.get(min_quality, 2)
        
        for pattern in filtered_patterns:
            detection = pattern.get("detection", {})
            strategy = detection.get("strategy", "regex")
            signals = detection.get("signals", [])
            
            pattern_quality = pattern.get("quality_tier", "medium")
            if quality_order.get(pattern_quality, 2) > min_quality_level:
                continue
            
            if strategy != "regex":
                continue
            
            for signal in signals:
                regex = parse_signal(signal)
                if not regex:
                    continue
                try:
                    for match in re.finditer(regex, content, re.IGNORECASE | re.MULTILINE):
                        line_num = content[:match.start()].count('\n') + 1
                        excerpt = lines[line_num - 1].strip()[:100] if line_num <= len(lines) else ""
                        
                        findings.append(Finding(
                            pattern_id=pattern.get("pattern_id", "unknown"),
                            title=pattern.get("title", "Unknown pattern"),
                            category=pattern.get("category", "general"),
                            severity=pattern.get("severity", "warn"),
                            file=str(file_path),
                            line=line_num,
                            excerpt=excerpt,
                            message=pattern.get("message", "Pattern detected"),
                            details={
                                "match": match.group()[:100],
                                "quality_tier": pattern.get("quality_tier", "medium"),
                                "precision_estimate": pattern.get("precision_estimate", 0.5),
                                "domain": pattern.get("domain", "any"),
                            }
                        ))
                except re.error:
                    pass
        
        return findings
    
    def scan_directory(
        self,
        directory: Path,
        extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[Sequence[str]] = None,
    ) -> Tuple[List[Finding], int]:
        """Scan a directory recursively."""
        extensions = extensions or ['.py', '.md', '.json', '.yaml', '.yml', '.ts', '.tsx', '.js', '.jsx']
        exclude_dirs_set = set(exclude_dirs) if exclude_dirs else {
            '__pycache__', '.git', 'node_modules', '.venv', 'venv', 
            'dist', 'build', 'tests', 'test_runs', '.pytest_cache',
            'registry'  # Registry files are pattern definitions, not code to scan
        }
        
        skip_files = {
            'challenge_generator.py',
            'test_cases.json',
            'sovereign_patterns.json',
            'delegated_patterns.json',
        }
        
        all_findings = []
        files_scanned = 0
        
        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue
            if any(part in exclude_dirs_set for part in file_path.parts):
                continue
            if file_path.name in skip_files:
                continue
            if file_path.suffix.lower() not in extensions:
                continue
            
            findings = self.scan_file(file_path)
            all_findings.extend(findings)
            files_scanned += 1
        
        return all_findings, files_scanned


class PatternSleuth:
    """Main Pattern Sleuth engine."""
    
    VERSION = "1.0.0"
    
    def __init__(
        self,
        root: Optional[Path] = None,
        registry_path: Optional[Path] = None,
        policy_path: Optional[Path] = None,
    ):
        self.root = root or get_byo_root()
        self.registry = PatternRegistry(registry_path or get_byo_registry_path())
        self.scanner = PatternScanner(self.registry)
    
    def scan(
        self,
        targets: Optional[List[Path]] = None,
        extensions: Optional[List[str]] = None,
    ) -> ScanResult:
        """Scan targets for patterns."""
        targets = targets or [self.root]
        
        all_findings = []
        files_scanned = 0
        
        for target in targets:
            if not target.exists():
                continue
            
            if target.is_file():
                findings = self.scanner.scan_file(target)
                all_findings.extend(findings)
                files_scanned += 1
            elif target.is_dir():
                findings, count = self.scanner.scan_directory(target, extensions)
                all_findings.extend(findings)
                files_scanned += count
        
        decision, reasons = self._compute_decision(all_findings)
        summary = self._compute_summary(all_findings)
        
        return ScanResult(
            generated_at=datetime.now(timezone.utc).isoformat(),
            decision=decision,
            reasons=reasons,
            files_scanned=files_scanned,
            findings=all_findings,
            summary=summary,
        )
    
    def _compute_decision(self, findings: List[Finding]) -> Tuple[str, List[str]]:
        """Compute overall decision from findings."""
        critical = sum(1 for f in findings if f.severity == "critical" or f.severity == "block")
        high = sum(1 for f in findings if f.severity == "high" or f.severity == "flag")
        medium = sum(1 for f in findings if f.severity == "medium" or f.severity == "warn")
        
        reasons = []
        if critical:
            reasons.append(f"{critical} critical/blocking findings")
        if high:
            reasons.append(f"{high} high/flag findings")
        if medium:
            reasons.append(f"{medium} medium/warn findings")
        
        if not reasons:
            reasons.append("No patterns detected above threshold")
        
        if critical > 0:
            return Decision.BLOCK.value, reasons
        elif high > 0:
            return Decision.FLAG.value, reasons
        elif medium > 0:
            return Decision.WARN.value, reasons
        return Decision.PASS.value, reasons
    
    def _compute_summary(self, findings: List[Finding]) -> Dict[str, int]:
        """Compute summary statistics."""
        summary = {
            "total": len(findings),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        
        for f in findings:
            sev = f.severity.lower()
            if sev in ("critical", "block"):
                summary["critical"] += 1
            elif sev in ("high", "flag"):
                summary["high"] += 1
            elif sev in ("medium", "warn"):
                summary["medium"] += 1
            elif sev == "low":
                summary["low"] += 1
            else:
                summary["info"] += 1
        
        return summary


def scan_roots(
    roots: List[Path],
    registry_path: Optional[Path] = None,
    policy_path: Optional[Path] = None,
    extensions: Optional[List[str]] = None,
) -> ScanResult:
    """
    Convenience function to scan multiple root directories.
    
    Args:
        roots: List of paths to scan.
        registry_path: Optional path to custom pattern registry JSON.
        policy_path: Optional path to custom policy JSON.
        extensions: Optional list of file extensions to include.
    
    Returns:
        ScanResult with all findings from all roots.
    """
    engine = PatternSleuth(
        root=roots[0] if roots else None,
        registry_path=registry_path,
        policy_path=policy_path,
    )
    return engine.scan(targets=roots, extensions=extensions)


