"""
Tests for FiletypeSluice - file type routing.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_sleuth.sluice import FiletypeSluice, SluiceType, create_sluice


class TestFiletypeSluice:
    """Test file type routing."""
    
    def test_route_python_file(self):
        """Test routing of Python files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("test.py"))
        assert route.sluice_type == SluiceType.PYTHON
        assert ".py" in route.extensions
    
    def test_route_typescript_file(self):
        """Test routing of TypeScript files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("app.ts"))
        assert route.sluice_type == SluiceType.TYPESCRIPT
        assert ".ts" in route.extensions
    
    def test_route_javascript_file(self):
        """Test routing of JavaScript files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("index.js"))
        assert route.sluice_type == SluiceType.JAVASCRIPT
    
    def test_route_markdown_file(self):
        """Test routing of Markdown files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("README.md"))
        assert route.sluice_type == SluiceType.MARKDOWN
    
    def test_route_json_file(self):
        """Test routing of JSON files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("config.json"))
        assert route.sluice_type == SluiceType.JSON
    
    def test_route_yaml_file(self):
        """Test routing of YAML files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("config.yaml"))
        assert route.sluice_type == SluiceType.YAML
    
    def test_route_shell_file(self):
        """Test routing of shell files."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("script.sh"))
        assert route.sluice_type == SluiceType.SHELL
    
    def test_route_makefile(self):
        """Test routing of Makefile."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("Makefile"))
        assert route.sluice_type == SluiceType.SHELL
    
    def test_route_unknown_file(self):
        """Test routing of unknown file types."""
        sluice = FiletypeSluice()
        route = sluice.route(Path("data.xyz"))
        assert route.sluice_type == SluiceType.GENERIC
    
    def test_should_apply_pattern(self):
        """Test pattern application decision."""
        sluice = FiletypeSluice()
        
        should_apply, reason = sluice.should_apply_pattern(
            Path("test.py"),
            "code_quality"
        )
        assert should_apply is True
        
        should_apply, reason = sluice.should_apply_pattern(
            Path("test.py"),
            "ai_output"
        )
        assert should_apply is False
    
    def test_filter_patterns(self):
        """Test pattern filtering."""
        sluice = FiletypeSluice()
        
        patterns = [
            {"pattern_id": "p1", "category": "code_quality", "languages": ["any"]},
            {"pattern_id": "p2", "category": "ai_behavior", "domain": "ai_output"},
        ]
        
        filtered = sluice.filter_patterns(Path("test.py"), patterns)
        assert len(filtered) == 1
        assert filtered[0]["pattern_id"] == "p1"


class TestCreateSluice:
    """Test factory function."""
    
    def test_create_sluice(self):
        """Test factory function returns instance."""
        sluice = create_sluice()
        assert isinstance(sluice, FiletypeSluice)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
