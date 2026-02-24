"""
Tests for Pattern Discovery - codebase analysis.
"""

import pytest
from pathlib import Path
import sys
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_sleuth.discovery import (
    PatternArchaeologist,
    discover_codebase,
    NamingPattern,
    StructurePattern,
    DomainTerm,
    CodebaseUnderstanding,
)


class TestPatternArchaeologist:
    """Test pattern archaeologist."""
    
    def test_discover_empty_directory(self, tmp_path):
        """Test discovery on empty directory."""
        archaeologist = PatternArchaeologist(tmp_path)
        result = archaeologist.discover()
        
        assert result.total_files == 0
        assert result.total_lines == 0
    
    def test_discover_python_file(self, tmp_path):
        """Test discovery of Python file."""
        test_file = tmp_path / "example.py"
        test_file.write_text('''
class ExampleClass:
    """Example class."""
    
    def example_method(self):
        return True

def example_function():
    pass
''')
        
        archaeologist = PatternArchaeologist(tmp_path)
        result = archaeologist.discover()
        
        assert result.total_files == 1
        assert len(archaeologist.class_names) == 1
        assert "ExampleClass" in archaeologist.class_names
        assert len(archaeologist.function_names) >= 1
    
    def test_discover_naming_patterns(self, tmp_path):
        """Test naming pattern discovery."""
        test_file = tmp_path / "naming.py"
        test_file.write_text('''
def snake_case_function():
    pass

def another_snake_function():
    pass
''')
        
        archaeologist = PatternArchaeologist(tmp_path)
        result = archaeologist.discover()
        
        assert len(result.naming_patterns) > 0
    
    def test_classify_naming_style(self, tmp_path):
        """Test naming style classification."""
        archaeologist = PatternArchaeologist(tmp_path)
        
        assert archaeologist._classify_naming_style("snake_case") == "snake_case"
        assert archaeologist._classify_naming_style("PascalCase") == "PascalCase"
        assert archaeologist._classify_naming_style("SCREAMING_SNAKE") == "SCREAMING_SNAKE"


class TestDiscoverCodebase:
    """Test convenience function."""
    
    def test_discover_codebase(self, tmp_path):
        """Test discover_codebase function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        result = discover_codebase(tmp_path)
        
        assert isinstance(result, CodebaseUnderstanding)
        assert result.codebase_path == str(tmp_path)
        assert result.total_files == 1
    
    def test_discover_codebase_with_extensions(self, tmp_path):
        """Test discovery with custom extensions."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        md_file = tmp_path / "readme.md"
        md_file.write_text("# Test")
        
        result = discover_codebase(tmp_path, extensions=['.py'])
        
        assert result.total_files == 1


class TestCodebaseUnderstanding:
    """Test CodebaseUnderstanding dataclass."""
    
    def test_to_dict(self):
        """Test serialization."""
        understanding = CodebaseUnderstanding(
            codebase_path="/test",
            scan_timestamp="2026-01-01T00:00:00",
            total_files=10,
            total_lines=100,
            naming_patterns=[],
            structure_patterns=[],
            domain_terms=[],
            conventions={},
            anti_patterns=[],
            recommendations=[],
        )
        
        d = understanding.to_dict()
        
        assert d["codebase_path"] == "/test"
        assert d["total_files"] == 10
        assert "naming_patterns" in d


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
