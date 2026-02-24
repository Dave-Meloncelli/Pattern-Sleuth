"""
Tests for Pattern Sleuth
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_sleuth import PatternSleuth, PatternRegistry, Finding, Decision


class TestPatternRegistry:
    """Test pattern registry loading."""
    
    def test_load_defaults(self):
        """Test that default patterns are loaded."""
        registry = PatternRegistry()
        assert len(registry.patterns) > 0
        assert "neg_placeholder_return_true" in registry.patterns
    
    def test_categories_exist(self):
        """Test that categories are populated."""
        registry = PatternRegistry()
        assert "code_quality" in registry.categories
        assert "security" in registry.categories


class TestPatternScanner:
    """Test pattern scanning."""
    
    def test_scan_placeholder_return(self, tmp_path):
        """Test detection of placeholder return True."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def validate():
    return True  # placeholder
""")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        assert len(result.findings) > 0
        assert any("placeholder" in f.pattern_id.lower() or "placeholder" in f.title.lower() for f in result.findings)
    
    def test_scan_not_implemented(self, tmp_path):
        """Test detection of NotImplementedError."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def stub():
    raise NotImplementedError
""")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        assert len(result.findings) > 0
        assert any("notimplemented" in f.pattern_id.lower() or "notimplemented" in f.title.lower() for f in result.findings)
    
    def test_scan_todo_fixme(self, tmp_path):
        """Test detection of TODO/FIXME markers."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# TODO: implement this later
# FIXME: broken code
""")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        assert len(result.findings) > 0
        assert any("todo" in f.pattern_id.lower() or "fixme" in f.pattern_id.lower() or "todo" in f.title.lower() or "fixme" in f.title.lower() for f in result.findings)


class TestDecision:
    """Test decision computation."""
    
    def test_pass_on_clean_code(self, tmp_path):
        """Test PASS decision on clean code."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("""
def calculate(a, b):
    return a + b
""")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        assert result.decision == Decision.PASS.value
    
    def test_block_on_critical(self, tmp_path):
        """Test BLOCK decision on critical findings."""
        test_file = tmp_path / "critical.py"
        test_file.write_text("""
def check():
    return True  # placeholder
    raise NotImplementedError
""")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        assert result.decision in [Decision.FLAG.value, Decision.BLOCK.value]


class TestScanResult:
    """Test scan result structure."""
    
    def test_to_dict(self, tmp_path):
        """Test result serialization."""
        test_file = tmp_path / "test.py"
        test_file.write_text("# test")
        
        engine = PatternSleuth(root=tmp_path)
        result = engine.scan()
        
        d = result.to_dict()
        assert "decision" in d
        assert "findings" in d
        assert "summary" in d
        assert "files_scanned" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
