"""
PATTERN_DISCOVERY.PY
====================
Discovers patterns in legacy codebases - naming, structure, domain terms.
Produces a "codebase understanding" report with alignment recommendations.

This is the archaeologist - finds what's actually there, not what should be.
"""

import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Counter as TypingCounter
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
from datetime import datetime, timezone


@dataclass
class NamingPattern:
    """Discovered naming pattern"""
    pattern_type: str  # file, class, function, variable, constant
    style: str  # snake_case, PascalCase, camelCase, SCREAMING_SNAKE
    examples: List[str]
    frequency: int
    confidence: float


@dataclass
class StructurePattern:
    """Discovered code structure pattern"""
    pattern_id: str
    description: str
    file_count: int
    example_files: List[str]
    characteristics: Dict[str, Any]


@dataclass
class DomainTerm:
    """Domain-specific terminology"""
    term: str
    category: str
    frequency: int
    files_found: List[str]
    context: str  # where it appears (class names, comments, etc)


@dataclass
class CodebaseUnderstanding:
    """Complete understanding of a codebase"""
    codebase_path: str
    scan_timestamp: str
    total_files: int
    total_lines: int
    
    naming_patterns: List[NamingPattern]
    structure_patterns: List[StructurePattern]
    domain_terms: List[DomainTerm]
    
    conventions: Dict[str, Any]
    anti_patterns: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "codebase_path": self.codebase_path,
            "scan_timestamp": self.scan_timestamp,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "naming_patterns": [asdict(p) for p in self.naming_patterns],
            "structure_patterns": [asdict(p) for p in self.structure_patterns],
            "domain_terms": [asdict(t) for t in self.domain_terms],
            "conventions": self.conventions,
            "anti_patterns": self.anti_patterns,
            "recommendations": self.recommendations,
        }


class PatternArchaeologist:
    """
    Discovers patterns in legacy codebases.
    
    Philosophy: What IS there, not what SHOULD be there.
    Then recommends alignment based on what we find.
    """
    
    NAMING_STYLES = {
        "snake_case": re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$'),
        "PascalCase": re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
        "camelCase": re.compile(r'^[a-z][a-zA-Z0-9]*$'),
        "SCREAMING_SNAKE": re.compile(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$'),
        "kebab-case": re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$'),
        "mixed": re.compile(r'.*'),  # fallback
    }
    
    COMMON_IMPORTS = [
        "json", "os", "sys", "re", "logging", "datetime", "pathlib",
        "typing", "dataclasses", "enum", "collections", "asyncio",
        "requests", "flask", "fastapi", "pytest", "unittest",
    ]
    
    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path
        self.files_scanned: List[Path] = []
        self.lines_scanned = 0
        
        self.file_names: List[str] = []
        self.class_names: List[str] = []
        self.function_names: List[str] = []
        self.variable_names: List[str] = []
        self.constant_names: List[str] = []
        
        self.docstring_patterns: List[Dict[str, Any]] = []
        self.import_patterns: TypingCounter[str] = Counter()
        
        self.structure_patterns: Dict[str, List[Path]] = defaultdict(list)
        
        self.domain_vocabulary: Dict[str, TypingCounter[str]] = defaultdict(Counter)
    
    def discover(self, extensions: Optional[List[str]] = None) -> CodebaseUnderstanding:
        """
        Main discovery method. Scans codebase and extracts patterns.
        """
        extensions = extensions or ['.py']
        
        self._scan_files(extensions)
        naming = self._analyze_naming()
        structure = self._analyze_structure()
        domain = self._analyze_domain()
        conventions = self._infer_conventions()
        anti = self._detect_anti_patterns()
        recommendations = self._generate_recommendations(naming, structure, domain)
        
        return CodebaseUnderstanding(
            codebase_path=str(self.codebase_path),
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
            total_files=len(self.files_scanned),
            total_lines=self.lines_scanned,
            naming_patterns=naming,
            structure_patterns=structure,
            domain_terms=domain,
            conventions=conventions,
            anti_patterns=anti,
            recommendations=recommendations,
        )
    
    def _scan_files(self, extensions: List[str]):
        """Scan all files and collect names."""
        skip_files = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 
                      'Cargo.lock', 'composer.lock', 'Gemfile.lock'}
        
        for ext in extensions:
            for file_path in self.codebase_path.rglob(f'*{ext}'):
                if not file_path.is_file():
                    continue
                if file_path.name in skip_files:
                    continue
                if any(skip in file_path.parts for skip in ['__pycache__', '.git', 'node_modules', '.venv', 'venv', 'dist', 'build']):
                    continue
                
                self.files_scanned.append(file_path)
                self.file_names.append(file_path.stem)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    self.lines_scanned += content.count('\n') + 1
                    
                    if ext == '.py':
                        self._extract_names(file_path, content)
                        self._extract_docstring_patterns(file_path, content)
                        self._extract_imports(content)
                    
                    self._extract_vocabulary(file_path, content)
                    self._extract_generic_patterns(file_path, content, ext)
                except Exception:
                    pass
    
    def _extract_generic_patterns(self, file_path: Path, content: str, ext: str):
        """Extract patterns from non-Python files."""
        if ext in ['.sh', '.bash']:
            function_pattern = re.compile(r'^(?:function\s+)?(\w+)\s*\(\)', re.MULTILINE)
            for match in function_pattern.finditer(content):
                self.function_names.append(match.group(1))
            
            const_pattern = re.compile(r'^(\w+)=(?:["\']|[^=])', re.MULTILINE)
            for match in const_pattern.finditer(content):
                name = match.group(1)
                if name.isupper() or (name[0].isupper() and '_' in name):
                    self.constant_names.append(name)
        
        elif ext in ['.psm1', '.ps1']:
            function_pattern = re.compile(r'(?:function|filter)\s+(\w[-\w]*)', re.IGNORECASE)
            for match in function_pattern.finditer(content):
                self.function_names.append(match.group(1))
        
        elif ext in ['.md', '.markdown']:
            headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
            for h in headers:
                words = re.findall(r'\b[A-Z][a-z]+\b', h)
                for w in words:
                    if len(w) > 3:
                        self.domain_vocabulary[file_path.parent.name][w.lower()] += 1
        
        elif ext == '.json':
            try:
                data = json.loads(content)
                self._extract_json_keys(data, file_path.parent.name)
            except Exception:
                pass
    
    def _extract_json_keys(self, data: Any, category: str, depth: int = 0):
        """Recursively extract keys from JSON."""
        if depth > 5:
            return
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str) and len(key) > 3:
                    self.domain_vocabulary[category][key.lower()] += 1
                self._extract_json_keys(value, category, depth + 1)
        elif isinstance(data, list):
            for item in data:
                self._extract_json_keys(item, category, depth + 1)
    
    def _extract_names(self, file_path: Path, content: str):
        """Extract class, function, variable names."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.class_names.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    self.function_names.append(node.name)
                    for arg in node.args.args:
                        self.variable_names.append(arg.arg)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if name.isupper() or (name.isupper() and '_' in name):
                                self.constant_names.append(name)
                            else:
                                self.variable_names.append(name)
        except SyntaxError:
            pass
    
    def _extract_docstring_patterns(self, file_path: Path, content: str):
        """Extract docstring patterns (headers, sections)."""
        docstring_match = re.search(r'"""([^"]+)"""', content[:2000], re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1)
            
            has_author = bool(re.search(r'Author:', docstring, re.IGNORECASE))
            has_date = bool(re.search(r'Date:|Created:', docstring, re.IGNORECASE))
            has_version = bool(re.search(r'Version:', docstring, re.IGNORECASE))
            has_features = bool(re.search(r'Features:', docstring, re.IGNORECASE))
            has_purpose = bool(re.search(r'Purpose:|PURPOSE:', docstring, re.IGNORECASE))
            
            self.docstring_patterns.append({
                "file": str(file_path.name),
                "has_author": has_author,
                "has_date": has_date,
                "has_version": has_version,
                "has_features": has_features,
                "has_purpose": has_purpose,
                "length": len(docstring),
            })
    
    def _extract_imports(self, content: str):
        """Extract import patterns."""
        for match in re.finditer(r'^(?:from\s+(\S+)\s+)?import\s+(.+)$', content, re.MULTILINE):
            module = match.group(1) or match.group(2).split(',')[0].strip()
            base_module = module.split('.')[0]
            self.import_patterns[base_module] += 1
    
    def _extract_vocabulary(self, file_path: Path, content: str):
        """Extract domain-specific vocabulary."""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content)
        word_freq = Counter(words)
        
        category = file_path.parent.name
        for word, count in word_freq.most_common(50):
            self.domain_vocabulary[category][word.lower()] += count
    
    def _classify_naming_style(self, name: str) -> str:
        """Classify the naming style of a name."""
        for style, pattern in self.NAMING_STYLES.items():
            if pattern.match(name):
                return style
        return "mixed"
    
    def _analyze_naming(self) -> List[NamingPattern]:
        """Analyze naming patterns."""
        patterns = []
        
        for name_type, names in [
            ("file", self.file_names),
            ("class", self.class_names),
            ("function", self.function_names),
            ("variable", self.variable_names),
            ("constant", self.constant_names),
        ]:
            if not names:
                continue
            
            styles = Counter(self._classify_naming_style(n) for n in names)
            dominant_style, dominant_count = styles.most_common(1)[0]
            
            examples = [n for n in names if self._classify_naming_style(n) == dominant_style][:10]
            
            patterns.append(NamingPattern(
                pattern_type=name_type,
                style=dominant_style,
                examples=examples,
                frequency=dominant_count,
                confidence=dominant_count / len(names),
            ))
        
        return patterns
    
    def _analyze_structure(self) -> List[StructurePattern]:
        """Analyze code structure patterns."""
        patterns = []
        
        has_dataclass = sum(1 for f in self.files_scanned if self._file_has_pattern(f, '@dataclass'))
        has_enum = sum(1 for f in self.files_scanned if self._file_has_pattern(f, 'class.*Enum'))
        has_logging = sum(1 for f in self.files_scanned if self._file_has_pattern(f, 'logging.basicConfig'))
        has_type_hints = sum(1 for f in self.files_scanned if self._file_has_pattern(f, 'from typing import'))
        
        if has_dataclass > 0:
            patterns.append(StructurePattern(
                pattern_id="uses_dataclasses",
                description="Uses @dataclass for structured data",
                file_count=has_dataclass,
                example_files=[str(f.name) for f in self.files_scanned[:5]],
                characteristics={"modern_python": True, "structured_data": True},
            ))
        
        if has_enum > 0:
            patterns.append(StructurePattern(
                pattern_id="uses_enums",
                description="Uses Enum for type-safe values",
                file_count=has_enum,
                example_files=[str(f.name) for f in self.files_scanned[:5]],
                characteristics={"type_safety": True},
            ))
        
        if has_logging > 0:
            patterns.append(StructurePattern(
                pattern_id="structured_logging",
                description="Uses structured logging",
                file_count=has_logging,
                example_files=[str(f.name) for f in self.files_scanned[:5]],
                characteristics={"observability": True},
            ))
        
        if has_type_hints > 0:
            patterns.append(StructurePattern(
                pattern_id="type_hints",
                description="Uses type hints",
                file_count=has_type_hints,
                example_files=[str(f.name) for f in self.files_scanned[:5]],
                characteristics={"type_safety": True, "modern_python": True},
            ))
        
        return patterns
    
    def _file_has_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches a pattern."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return bool(re.search(pattern, content))
        except Exception:
            return False
    
    def _analyze_domain(self) -> List[DomainTerm]:
        """Analyze domain-specific terminology."""
        domain_terms = []
        
        all_words = Counter()
        for category, counter in self.domain_vocabulary.items():
            all_words.update(counter)
        
        common_words = set(w for w, c in all_words.most_common(100))
        standard_lib = set(self.COMMON_IMPORTS)
        standard_words = {'self', 'none', 'true', 'false', 'class', 'def', 'return', 'import', 'from'}
        
        for category, counter in self.domain_vocabulary.items():
            for word, count in counter.most_common(20):
                if word.lower() not in standard_lib and word.lower() not in standard_words:
                    if len(word) > 3 and count > 2:
                        files = [str(f.name) for f in self.files_scanned 
                                 if self._file_contains_word(f, word)]
                        
                        domain_terms.append(DomainTerm(
                            term=word,
                            category=category,
                            frequency=count,
                            files_found=files[:5],
                            context=category,
                        ))
        
        seen = set()
        unique_terms = []
        for term in domain_terms:
            if term.term not in seen:
                seen.add(term.term)
                unique_terms.append(term)
        
        return unique_terms[:50]
    
    def _file_contains_word(self, file_path: Path, word: str) -> bool:
        """Check if file contains a word."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            return word.lower() in content
        except Exception:
            return False
    
    def _infer_conventions(self) -> Dict[str, Any]:
        """Infer conventions from discovered patterns."""
        conventions = {
            "naming": {},
            "structure": {},
            "documentation": {},
        }
        
        if self.class_names:
            class_styles = Counter(self._classify_naming_style(n) for n in self.class_names)
            conventions["naming"]["classes"] = class_styles.most_common(1)[0][0]
        
        if self.function_names:
            func_styles = Counter(self._classify_naming_style(n) for n in self.function_names)
            conventions["naming"]["functions"] = func_styles.most_common(1)[0][0]
        
        if self.file_names:
            file_styles = Counter(self._classify_naming_style(n) for n in self.file_names)
            conventions["naming"]["files"] = file_styles.most_common(1)[0][0]
        
        docstats = {
            "with_author": sum(1 for d in self.docstring_patterns if d.get("has_author")),
            "with_date": sum(1 for d in self.docstring_patterns if d.get("has_date")),
            "with_version": sum(1 for d in self.docstring_patterns if d.get("has_version")),
            "with_features": sum(1 for d in self.docstring_patterns if d.get("has_features")),
        }
        conventions["documentation"] = docstats
        
        top_imports = [i for i, c in self.import_patterns.most_common(10)]
        conventions["structure"]["common_imports"] = top_imports
        
        return conventions
    
    def _detect_anti_patterns(self) -> List[Dict[str, Any]]:
        """Detect anti-patterns in the codebase."""
        anti_patterns = []
        
        hardcoded_paths = 0
        for f in self.files_scanned:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                if re.search(r'["\'][A-Z]:\\[^"\']+["\']', content):
                    hardcoded_paths += 1
            except Exception:
                pass
        
        if hardcoded_paths > 0:
            anti_patterns.append({
                "type": "hardcoded_paths",
                "severity": "medium",
                "count": hardcoded_paths,
                "description": f"{hardcoded_paths} files contain hardcoded Windows paths",
                "recommendation": "Use Path.cwd() or configurable root paths",
            })
        
        bare_except = 0
        for f in self.files_scanned:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                if re.search(r'except\s*:', content):
                    bare_except += 1
            except Exception:
                pass
        
        if bare_except > 0:
            anti_patterns.append({
                "type": "bare_except",
                "severity": "low",
                "count": bare_except,
                "description": f"{bare_except} files use bare except clauses",
                "recommendation": "Catch specific exceptions",
            })
        
        return anti_patterns
    
    def _generate_recommendations(
        self,
        naming: List[NamingPattern],
        structure: List[StructurePattern],
        domain: List[DomainTerm],
    ) -> List[Dict[str, Any]]:
        """Generate alignment recommendations."""
        recommendations = []
        
        for np in naming:
            if np.confidence < 0.7:
                recommendations.append({
                    "category": "naming",
                    "priority": "high",
                    "issue": f"Inconsistent {np.pattern_type} naming ({np.confidence:.0%} consistent)",
                    "current": f"Mixed styles in {np.pattern_type}s",
                    "recommendation": f"Standardize {np.pattern_type}s to {np.style}",
                    "examples": np.examples[:5],
                })
        
        structure_ids = [s.pattern_id for s in structure]
        if "type_hints" not in structure_ids:
            recommendations.append({
                "category": "structure",
                "priority": "medium",
                "issue": "No type hints detected",
                "current": "Untyped codebase",
                "recommendation": "Add type hints for better IDE support and safety",
            })
        
        if len(domain) > 20:
            recommendations.append({
                "category": "domain",
                "priority": "low",
                "issue": "Large domain vocabulary detected",
                "current": f"{len(domain)} unique domain terms",
                "recommendation": "Consider creating a domain glossary or constants file",
                "examples": [d.term for d in domain[:10]],
            })
        
        return recommendations


def discover_codebase(
    codebase_path: Path,
    extensions: Optional[List[str]] = None,
) -> CodebaseUnderstanding:
    """
    Convenience function to discover patterns in a codebase.
    
    Args:
        codebase_path: Root path of the codebase to analyze.
        extensions: List of file extensions to scan. Defaults to ['.py'].
    
    Returns:
        CodebaseUnderstanding with all discovered patterns.
    """
    archaeologist = PatternArchaeologist(codebase_path)
    return archaeologist.discover(extensions)
