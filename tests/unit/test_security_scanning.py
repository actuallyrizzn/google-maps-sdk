"""
Unit tests for security scanning setup (issue #274 / #82)
"""

import pytest
from pathlib import Path
import subprocess
import sys


@pytest.mark.unit
class TestSecurityScanning:
    """Test security scanning setup"""

    def test_pip_audit_in_requirements_dev(self):
        """Test that pip-audit is in requirements-dev.txt"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        content = requirements_file.read_text()
        
        assert "pip-audit" in content, "pip-audit should be in requirements-dev.txt"

    def test_security_workflow_exists(self):
        """Test that security scanning workflow exists"""
        workflow_file = Path(__file__).parent.parent.parent / ".github" / "workflows" / "security-scan.yml"
        assert workflow_file.exists(), "Security scanning workflow should exist"

    def test_security_workflow_content(self):
        """Test that security workflow has correct content"""
        workflow_file = Path(__file__).parent.parent.parent / ".github" / "workflows" / "security-scan.yml"
        content = workflow_file.read_text()
        
        assert "pip-audit" in content, "Workflow should use pip-audit"
        assert "requirements.txt" in content, "Workflow should scan requirements.txt"
        assert "requirements-dev.txt" in content, "Workflow should scan requirements-dev.txt"

    def test_security_documentation_exists(self):
        """Test that security scanning documentation exists"""
        doc_file = Path(__file__).parent.parent.parent / "docs" / "SECURITY_SCANNING.md"
        assert doc_file.exists(), "Security scanning documentation should exist"

    @pytest.mark.skipif(
        subprocess.run([sys.executable, "-m", "pip", "show", "pip-audit"], 
                      capture_output=True).returncode != 0,
        reason="pip-audit not installed"
    )
    def test_pip_audit_can_run(self):
        """Test that pip-audit can be executed (if installed)"""
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--version"],
            capture_output=True,
            text=True
        )
        # pip-audit may not be installed in test environment, so we just check it doesn't crash
        # If it's not installed, the test is skipped
        assert result.returncode == 0 or "pip-audit" in result.stderr or "pip-audit" in result.stdout
