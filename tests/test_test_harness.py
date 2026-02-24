"""
Tests for Pattern Test Harness - pattern validation.
"""

import pytest
from pathlib import Path
import sys
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_sleuth.test_harness import (
    PatternTestHarness,
    PatternTestCase,
    PatternTestResult,
    BatchTestResult,
    run_pattern_file_test,
    run_registry_batch_test,
)


class TestPatternTestHarness:
    """Test pattern test harness."""
    
    def test_harness_initialization(self):
        """Test harness initialization."""
        harness = PatternTestHarness()
        assert harness.test_cases is not None
        assert "neg_placeholder_return_true" in harness.test_cases
    
    def test_validate_pattern_schema_valid(self):
        """Test schema validation with valid pattern."""
        harness = PatternTestHarness()
        
        pattern = {
            "pattern_id": "test_pattern",
            "title": "Test Pattern",
            "category": "code_quality",
            "severity": "warn",
            "detection": {
                "strategy": "regex",
                "signals": ["test.*pattern"]
            }
        }
        
        valid, errors = harness.validate_pattern_schema(pattern)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_pattern_schema_missing_field(self):
        """Test schema validation with missing field."""
        harness = PatternTestHarness()
        
        pattern = {
            "pattern_id": "test_pattern",
            "title": "Test Pattern",
        }
        
        valid, errors = harness.validate_pattern_schema(pattern)
        assert valid is False
        assert any("category" in e for e in errors)
    
    def test_validate_pattern_schema_invalid_severity(self):
        """Test schema validation with invalid severity."""
        harness = PatternTestHarness()
        
        pattern = {
            "pattern_id": "test_pattern",
            "title": "Test Pattern",
            "category": "code_quality",
            "severity": "invalid_severity",
            "detection": {
                "strategy": "regex",
                "signals": ["test"]
            }
        }
        
        valid, errors = harness.validate_pattern_schema(pattern)
        assert valid is False
    
    def test_normalize_pattern_forensic_format(self):
        """Test pattern normalization for forensic format."""
        harness = PatternTestHarness()
        
        pattern = {
            "id": "TEST_001",
            "name": "Test Pattern",
            "regex": "test.*pattern",
            "severity": "HIGH"
        }
        
        normalized = harness.normalize_pattern(pattern)
        
        assert normalized["pattern_id"] == "TEST_001"
        assert normalized["title"] == "Test Pattern"
        assert "detection" in normalized
        assert normalized["severity"] == "high"
    
    def test_test_pattern_with_default_cases(self):
        """Test pattern testing with default test cases."""
        harness = PatternTestHarness()
        
        pattern = {
            "pattern_id": "neg_placeholder_return_true",
            "title": "Placeholder return True",
            "category": "code_quality",
            "severity": "block",
            "detection": {
                "strategy": "regex",
                "signals": [r"return\s+True\s*$", r"return\s+True\s*#.*placeholder"]
            }
        }
        
        result = harness.test_pattern(pattern)
        
        assert isinstance(result, PatternTestResult)
        assert result.valid_schema is True
        assert result.total_tests > 0
    
    def test_test_pattern_without_test_cases(self):
        """Test pattern without test cases."""
        harness = PatternTestHarness()
        
        pattern = {
            "pattern_id": "unknown_pattern",
            "title": "Unknown Pattern",
            "category": "code_quality",
            "severity": "warn",
            "detection": {
                "strategy": "regex",
                "signals": ["test"]
            }
        }
        
        result = harness.test_pattern(pattern)
        
        assert result.total_tests == 0
        assert result.accuracy == 0.0
    
    def test_test_batch(self):
        """Test batch testing."""
        harness = PatternTestHarness()
        
        patterns = [
            {
                "pattern_id": "p1",
                "title": "Pattern 1",
                "category": "code_quality",
                "severity": "warn",
                "detection": {"strategy": "regex", "signals": ["test"]}
            },
            {
                "pattern_id": "p2",
                "title": "Pattern 2",
                "category": "security",
                "severity": "high",
                "detection": {"strategy": "regex", "signals": ["test"]}
            }
        ]
        
        result = harness.test_batch(patterns)
        
        assert isinstance(result, BatchTestResult)
        assert result.total_patterns == 2
        assert result.valid_patterns == 2


class TestPatternTestCase:
    """Test PatternTestCase dataclass."""
    
    def test_test_case_creation(self):
        """Test PatternTestCase creation."""
        case = PatternTestCase(
            id="test_1",
            content="test content",
            should_match=True,
            description="Test case"
        )
        
        assert case.id == "test_1"
        assert case.should_match is True


class TestPatternTestResult:
    """Test PatternTestResult dataclass."""
    
    def test_to_dict(self):
        """Test serialization."""
        result = PatternTestResult(
            pattern_id="test",
            valid_schema=True,
            schema_errors=[],
            total_tests=10,
            passed=8,
            failed=2,
            false_positives=1,
            false_negatives=1,
            accuracy=0.8,
            precision=0.9,
            recall=0.85,
            avg_match_time_ms=1.5,
            regex_errors=[],
            details=[]
        )
        
        d = result.to_dict()
        
        assert d["pattern_id"] == "test"
        assert d["accuracy"] == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
