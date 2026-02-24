"""
Tests for Pattern Sleuth CLI.
"""

import pytest
from pathlib import Path
import sys
import subprocess
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_sleuth.cli import main, print_banner


class TestCLI:
    """Test CLI functionality."""
    
    def test_version(self):
        """Test version flag."""
        result = subprocess.run(
            ["pattern-sleuth", "--version"],
            capture_output=True,
            text=True
        )
        assert "pattern-sleuth" in result.stdout
    
    def test_scan_help(self):
        """Test scan help."""
        result = subprocess.run(
            ["pattern-sleuth", "scan", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "scan" in result.stdout.lower() or "paths" in result.stdout.lower()
    
    def test_list_help(self):
        """Test list help."""
        result = subprocess.run(
            ["pattern-sleuth", "list", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
    
    def test_scan_empty_directory(self, tmp_path):
        """Test scan on empty directory."""
        result = subprocess.run(
            ["pattern-sleuth", "scan", str(tmp_path), "--json"],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert "decision" in output
        assert "findings" in output
    
    def test_scan_with_findings(self, tmp_path):
        """Test scan that finds patterns."""
        test_file = tmp_path / "bad.py"
        test_file.write_text('''
def validate():
    return True  # placeholder
''')
        
        result = subprocess.run(
            ["pattern-sleuth", "scan", str(tmp_path), "--json"],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert len(output["findings"]) > 0
    
    def test_scan_clean_code(self, tmp_path):
        """Test scan on clean code."""
        test_file = tmp_path / "clean.py"
        test_file.write_text('''
def calculate(a: int, b: int) -> int:
    """Calculate sum."""
    return a + b
''')
        
        result = subprocess.run(
            ["pattern-sleuth", "scan", str(tmp_path), "--json"],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert output["decision"] == "PASS"
    
    def test_list_patterns(self):
        """Test list command."""
        result = subprocess.run(
            ["pattern-sleuth", "list", "--json"],
            capture_output=True,
            text=True
        )
        
        patterns = json.loads(result.stdout)
        assert isinstance(patterns, list)
        assert len(patterns) > 0
    
    def test_list_by_category(self):
        """Test list command with category filter."""
        result = subprocess.run(
            ["pattern-sleuth", "list", "--category", "security", "--json"],
            capture_output=True,
            text=True
        )
        
        patterns = json.loads(result.stdout)
        for p in patterns:
            assert p.get("category") == "security"
    
    def test_validate(self):
        """Test validate command."""
        result = subprocess.run(
            ["pattern-sleuth", "validate", "--json"],
            capture_output=True,
            text=True
        )
        
        output = json.loads(result.stdout)
        assert "valid" in output


class TestPrintBanner:
    """Test banner printing."""
    
    def test_print_banner(self, capsys):
        """Test that banner prints without error and contains expected content."""
        print_banner()
        captured = capsys.readouterr()
        assert "____" in captured.out
        assert len(captured.out) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
