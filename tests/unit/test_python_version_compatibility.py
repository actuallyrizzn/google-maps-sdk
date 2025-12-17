"""
Unit tests for Python version compatibility testing setup (issue #276 / #84)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch


@pytest.mark.unit
class TestPythonVersionCompatibility:
    """Test Python version compatibility setup"""

    def test_python_version_in_range(self):
        """Test that current Python version is in supported range"""
        # setup.py claims support for Python 3.8-3.12
        # We test that it's at least 3.8 (minimum requirement)
        # Being above 3.12 is okay for development/testing
        version = sys.version_info
        assert version >= (3, 8), f"Python version {version.major}.{version.minor} is below minimum 3.8"
        # Note: We don't check upper bound here as we may test on newer versions

    def test_ci_workflow_exists(self):
        """Test that CI workflow exists"""
        workflow_file = Path(__file__).parent.parent.parent / ".github" / "workflows" / "test.yml"
        assert workflow_file.exists(), "CI test workflow should exist"

    def test_ci_workflow_has_python_matrix(self):
        """Test that CI workflow has Python version matrix"""
        workflow_file = Path(__file__).parent.parent.parent / ".github" / "workflows" / "test.yml"
        content = workflow_file.read_text()
        
        assert "matrix:" in content, "Workflow should have matrix strategy"
        assert "python-version:" in content, "Workflow should have python-version in matrix"
        assert "3.8" in content or "'3.8'" in content or '"3.8"' in content, "Workflow should test Python 3.8"
        assert "3.9" in content or "'3.9'" in content or '"3.9"' in content, "Workflow should test Python 3.9"
        assert "3.10" in content or "'3.10'" in content or '"3.10"' in content, "Workflow should test Python 3.10"
        assert "3.11" in content or "'3.11'" in content or '"3.11"' in content, "Workflow should test Python 3.11"
        assert "3.12" in content or "'3.12'" in content or '"3.12"' in content, "Workflow should test Python 3.12"

    def test_ci_workflow_runs_tests(self):
        """Test that CI workflow runs tests"""
        workflow_file = Path(__file__).parent.parent.parent / ".github" / "workflows" / "test.yml"
        content = workflow_file.read_text()
        
        assert "pytest" in content, "Workflow should run pytest"

    def test_setup_py_python_version_claim(self):
        """Test that setup.py claims Python version support"""
        setup_file = Path(__file__).parent.parent.parent / "setup.py"
        content = setup_file.read_text()
        
        # Should mention Python 3.8 or higher
        assert "3.8" in content or "python_requires" in content.lower(), \
            "setup.py should specify Python version requirements"

    def test_runtime_python_version_check_exists(self):
        """Test that __init__.py contains runtime Python version check"""
        init_file = Path(__file__).parent.parent.parent / "google_maps_sdk" / "__init__.py"
        content = init_file.read_text()
        
        # Should check Python version
        assert "sys.version_info" in content, "__init__.py should check Python version"
        assert "RuntimeError" in content, "__init__.py should raise RuntimeError for old Python"
        assert "3.8" in content, "__init__.py should mention minimum Python 3.8"

    def test_import_works_on_supported_python(self):
        """Test that import works on supported Python version (>= 3.8)"""
        # This test runs on Python >= 3.8, so import should succeed
        import google_maps_sdk
        assert google_maps_sdk.__version__ == "1.0.0"

    def test_runtime_version_check_raises_on_old_python(self):
        """Test that runtime version check raises RuntimeError on Python < 3.8"""
        # Create a mock version_info that mimics sys.version_info structure
        class MockVersionInfo:
            def __init__(self, major, minor):
                self.major = major
                self.minor = minor
            
            def __lt__(self, other):
                return (self.major, self.minor) < other
        
        # Mock sys.version_info to simulate Python 3.7
        with patch('sys.version_info', MockVersionInfo(3, 7)):
            # Need to reload the module to trigger the check
            import importlib
            if 'google_maps_sdk' in sys.modules:
                del sys.modules['google_maps_sdk']
            
            with pytest.raises(RuntimeError) as exc_info:
                import google_maps_sdk
            
            assert "requires Python 3.8 or higher" in str(exc_info.value)
            assert "3.7" in str(exc_info.value)
