"""
FILETYPE_SLUICE.PY
==================
Routes files to appropriate pattern detectors based on file type.
No more Python patterns firing on .ts files. No more AI patterns on code.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class SluiceType(Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    SHELL = "shell"
    CONFIG = "config"
    AI_OUTPUT = "ai_output"
    GENERIC = "generic"
    UNKNOWN = "unknown"


@dataclass
class SluiceRoute:
    """Where a file should be routed."""
    sluice_type: SluiceType
    extensions: Set[str]
    patterns_apply: List[str]  # Pattern categories that apply
    patterns_skip: List[str]    # Pattern categories to skip
    confidence: float          # How confident in this routing


class FiletypeSluice:
    """
    Routes files to appropriate pattern detectors.
    
    Philosophy: A pattern should only fire if:
    1. The file type is relevant to the pattern
    2. The pattern domain matches the file's purpose
    3. The pattern has acceptable precision for this context
    """
    
    # Files to skip entirely (generated, lock files, minified)
    SKIP_PATTERNS = {
        "package-lock.json",
        "pnpm-lock.yaml",
        "pnpm-lock.json",
        "yarn.lock",
        "poetry.lock",
        "Cargo.lock",
        "composer.lock",
        "Gemfile.lock",
        "*.min.js",
        "*.min.css",
        "*.d.ts",
        "*.pyc",
        "*.pyo",
        "dist/**",
        "build/**",
        "node_modules/**",
        "__pycache__/**",
        ".git/**",
        ".pytest_cache/**",
        "*.egg-info/**",
    }
    
    SKIP_DIRECTORIES = {
        "test_runs",
        "tests",
        "__pycache__",
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "dist",
        "build",
    }
    
    SKIP_CONTENT_PATTERNS = {
        "challenge_generator.py",
        "test_*.py",
    }
    
    # Extensions to skip (low signal files)
    SKIP_EXTENSIONS = {
        ".lock",
        ".min.js",
        ".min.css",
        ".d.ts",
        ".pyc",
        ".pyo",
        ".map",  # Source maps
    }
    
    # File type definitions
    ROUTES = {
        SluiceType.PYTHON: SluiceRoute(
            sluice_type=SluiceType.PYTHON,
            extensions={".py", ".pyw", ".pyi"},
            patterns_apply=[
                "code_quality",
                "security", 
                "process",
                "standards",
            ],
            patterns_skip=[
                "ai_output",
                "typescript_specific",
                "javascript_specific",
            ],
            confidence=0.95,
        ),
        SluiceType.TYPESCRIPT: SluiceRoute(
            sluice_type=SluiceType.TYPESCRIPT,
            extensions={".ts", ".tsx", ".mts", ".cts"},
            patterns_apply=[
                "code_quality",
                "security",
                "typescript_specific",
            ],
            patterns_skip=[
                "ai_output",
                "python_specific",
            ],
            confidence=0.95,
        ),
        SluiceType.JAVASCRIPT: SluiceRoute(
            sluice_type=SluiceType.JAVASCRIPT,
            extensions={".js", ".jsx", ".mjs", ".cjs"},
            patterns_apply=[
                "code_quality",
                "security",
                "javascript_specific",
            ],
            patterns_skip=[
                "ai_output",
                "typescript_specific",
                "python_specific",
            ],
            confidence=0.95,
        ),
        SluiceType.MARKDOWN: SluiceRoute(
            sluice_type=SluiceType.MARKDOWN,
            extensions={".md", ".markdown", ".rst"},
            patterns_apply=[
                "documentation",
                "standards",
                "security",  # Can have code blocks
            ],
            patterns_skip=[
                "typescript_specific",
                "python_specific",
            ],
            confidence=0.90,
        ),
        SluiceType.JSON: SluiceRoute(
            sluice_type=SluiceType.JSON,
            extensions={".json"},
            patterns_apply=[
                "config",
                "standards",
            ],
            patterns_skip=[
                "security",
                "code_quality",
                "ai_output",
                "python_specific",
                "typescript_specific",
            ],
            confidence=0.85,
        ),
        SluiceType.YAML: SluiceRoute(
            sluice_type=SluiceType.YAML,
            extensions={".yaml", ".yml"},
            patterns_apply=[
                "config",
                "security",
            ],
            patterns_skip=[
                "ai_output",
                "code_quality",
            ],
            confidence=0.95,
        ),
        SluiceType.SHELL: SluiceRoute(
            sluice_type=SluiceType.SHELL,
            extensions={".sh", ".bash", ".zsh", ".ps1", ".psm1"},
            patterns_apply=[
                "code_quality",
                "security",
            ],
            patterns_skip=[
                "ai_output",
                "python_specific",
                "typescript_specific",
            ],
            confidence=0.90,
        ),
        SluiceType.AI_OUTPUT: SluiceRoute(
            sluice_type=SluiceType.AI_OUTPUT,
            extensions={".txt", ".log", ".chat", ".conversation"},
            patterns_apply=[
                "ai_behavior",
                "safety_guardrails",
                "behavioral_drift",
                "adversarial_security",
            ],
            patterns_skip=[
                "code_quality",
                "python_specific",
                "typescript_specific",
            ],
            confidence=0.80,
        ),
        SluiceType.GENERIC: SluiceRoute(
            sluice_type=SluiceType.GENERIC,
            extensions=set(),  # Catch-all
            patterns_apply=[
                "security",
            ],
            patterns_skip=[
                "ai_output",
                "language_specific",
            ],
            confidence=0.50,
        ),
    }
    
    # Extension to SluiceType mapping (for fast lookup)
    EXT_MAP: Dict[str, SluiceType] = {}
    
    def __init__(self):
        # Build extension map
        for sluice_type, route in self.ROUTES.items():
            for ext in route.extensions:
                self.EXT_MAP[ext.lower()] = sluice_type
    
    def route(self, file_path: Path) -> SluiceRoute:
        """
        Route a file to the appropriate detector.
        """
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # Check for skip files (lock files, generated, minified)
        if ext in self.SKIP_EXTENSIONS:
            return SluiceRoute(
                sluice_type=SluiceType.UNKNOWN,
                extensions={ext},
                patterns_apply=[],
                patterns_skip=["all"],
                confidence=1.0,
            )
        
        # Check skip patterns
        for pattern in self.SKIP_PATTERNS:
            if pattern.startswith("*."):
                if name.endswith(pattern[1:]):
                    return SluiceRoute(
                        sluice_type=SluiceType.UNKNOWN,
                        extensions={ext},
                        patterns_apply=[],
                        patterns_skip=["all"],
                        confidence=1.0,
                    )
            elif pattern == name:
                return SluiceRoute(
                    sluice_type=SluiceType.UNKNOWN,
                    extensions={ext},
                    patterns_apply=[],
                    patterns_skip=["all"],
                    confidence=1.0,
                )
        
        # Direct extension match
        if ext in self.EXT_MAP:
            return self.ROUTES[self.EXT_MAP[ext]]
        
        # Filename-based detection
        name = file_path.name.lower()
        if name in {"makefile", "dockerfile", "vagrantfile"}:
            return self.ROUTES[SluiceType.SHELL]
        
        if name.startswith(".env") or name.endswith(".env"):
            return self.ROUTES[SluiceType.CONFIG]
        
        if "chat" in name or "log" in name or "conversation" in name:
            return self.ROUTES[SluiceType.AI_OUTPUT]
        
        # Content-based detection (slower, used as fallback)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = f.read(500)
            
            # Check for Python shebang or imports
            if sample.startswith('#!') and 'python' in sample[:50]:
                return self.ROUTES[SluiceType.PYTHON]
            
            if re.search(r'^import\s+\w+|^from\s+\w+\s+import', sample, re.MULTILINE):
                return self.ROUTES[SluiceType.PYTHON]
            
            if re.search(r'^import\s+\{|^export\s+(interface|type|const)', sample, re.MULTILINE):
                return self.ROUTES[SluiceType.TYPESCRIPT]
            
        except Exception:
            pass
        
        return self.ROUTES[SluiceType.GENERIC]
    
    def should_apply_pattern(
        self,
        file_path: Path,
        pattern_category: str,
        pattern_domain: str = "any",
    ) -> Tuple[bool, str]:
        """
        Determine if a pattern should be applied to a file.
        
        Returns: (should_apply, reason)
        """
        route = self.route(file_path)
        
        # Check domain
        if pattern_domain == "ai_output":
            if route.sluice_type != SluiceType.AI_OUTPUT:
                return False, f"AI output pattern skipped on {route.sluice_type.value} file"
        
        # Check category
        if pattern_category in route.patterns_skip:
            return False, f"Category '{pattern_category}' skipped for {route.sluice_type.value}"
        
        if pattern_category in route.patterns_apply:
            return True, f"Category '{pattern_category}' applies to {route.sluice_type.value}"
        
        # Default: apply with reduced confidence
        return True, f"Category '{pattern_category}' may apply (default allow)"
    
    def filter_patterns(
        self,
        file_path: Path,
        patterns: List[Dict],
    ) -> List[Dict]:
        """
        Filter patterns to only those relevant for this file.
        """
        route = self.route(file_path)
        filtered = []
        
        for pattern in patterns:
            category = pattern.get("category", "general")
            domain = pattern.get("domain", "any")
            languages = pattern.get("languages", ["any"])
            
            # Domain check
            if domain == "ai_output":
                if route.sluice_type != SluiceType.AI_OUTPUT:
                    continue
            
            # Language check
            if "any" not in languages:
                lang_map = {
                    "python": {".py", ".pyw", ".pyi"},
                    "typescript": {".ts", ".tsx"},
                    "javascript": {".js", ".jsx"},
                    "markdown": {".md", ".markdown"},
                }
                
                allowed_exts = set()
                for lang in languages:
                    allowed_exts.update(lang_map.get(lang, set()))
                
                if allowed_exts and file_path.suffix.lower() not in allowed_exts:
                    continue
            
            # Category check
            if category in route.patterns_skip:
                continue
            
            filtered.append(pattern)
        
        return filtered


def create_sluice() -> FiletypeSluice:
    """
    Factory function to create a FiletypeSluice instance.
    
    Returns:
        A new FiletypeSluice instance.
    """
    return FiletypeSluice()
