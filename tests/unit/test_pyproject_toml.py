"""
Unit tests for pyproject.toml support (issue #277 / #85)
"""

import pytest
from pathlib import Path
import sys


@pytest.mark.unit
class TestPyprojectToml:
    """Test pyproject.toml support"""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        assert pyproject_file.exists(), "pyproject.toml should exist"

    def test_pyproject_toml_has_build_system(self):
        """Test that pyproject.toml has build system configuration"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_file.read_text()
        
        assert "[build-system]" in content, "pyproject.toml should have build-system section"
        assert "setuptools" in content or "build-backend" in content, \
            "pyproject.toml should specify build backend"

    def test_pyproject_toml_has_project_metadata(self):
        """Test that pyproject.toml has project metadata"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_file.read_text()
        
        assert "[project]" in content, "pyproject.toml should have project section"
        assert "name" in content, "pyproject.toml should have project name"
        assert "version" in content, "pyproject.toml should have project version"
        assert "requires-python" in content, "pyproject.toml should specify Python version requirement"

    def test_pyproject_toml_has_dependencies(self):
        """Test that pyproject.toml has dependencies"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_file.read_text()
        
        assert "dependencies" in content, "pyproject.toml should have dependencies section"
        assert "requests" in content, "pyproject.toml should include requests dependency"

    def test_pyproject_toml_has_dev_dependencies(self):
        """Test that pyproject.toml has dev dependencies"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_file.read_text()
        
        assert "optional-dependencies" in content or "[project.optional-dependencies]" in content, \
            "pyproject.toml should have optional dependencies section"
        assert "dev" in content, "pyproject.toml should have dev dependencies"

    def test_pyproject_toml_has_tool_config(self):
        """Test that pyproject.toml has tool configuration"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        content = pyproject_file.read_text()
        
        # Should have tool configuration for pytest, black, mypy, etc.
        assert "[tool." in content, "pyproject.toml should have tool configuration sections"

    def test_pyproject_toml_matches_requirements(self):
        """Test that pyproject.toml dependencies match requirements.txt"""
        pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        
        pyproject_content = pyproject_file.read_text()
        requirements_content = requirements_file.read_text()
        
        # Check that requests version matches
        if "requests==" in requirements_content:
            req_version = [line for line in requirements_content.split('\n') if 'requests==' in line][0].split('==')[1].strip()
            assert f"requests=={req_version}" in pyproject_content, \
                f"pyproject.toml should have same requests version as requirements.txt ({req_version})"
