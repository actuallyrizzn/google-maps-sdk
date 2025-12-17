"""
Unit tests for version pinning consistency (issue #273 / #81)
"""

import pytest
import re
from pathlib import Path


@pytest.mark.unit
class TestVersionPinning:
    """Test version pinning consistency"""

    def test_requirements_txt_uses_pinned_versions(self):
        """Test that requirements.txt uses pinned versions (==)"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        content = requirements_file.read_text()
        
        # Check that all dependencies use == for pinning
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for line in lines:
            if '==' in line:
                # Pinned version - good
                assert '==' in line, f"Line should use == for pinning: {line}"
            elif '>=' in line:
                # Loose version - should not be present
                pytest.fail(f"requirements.txt should use pinned versions (==), not loose (>=): {line}")
            elif '~=' in line:
                # Compatible release - acceptable but prefer ==
                pass
            elif '>' in line or '<' in line:
                # Other version specifiers - should not be present
                pytest.fail(f"requirements.txt should use pinned versions (==): {line}")

    def test_requirements_dev_txt_uses_pinned_versions(self):
        """Test that requirements-dev.txt uses pinned versions (==)"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        content = requirements_file.read_text()
        
        # Check that all dependencies use == for pinning
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for line in lines:
            if '==' in line:
                # Pinned version - good
                assert '==' in line, f"Line should use == for pinning: {line}"
            elif '>=' in line:
                # Loose version - should not be present
                pytest.fail(f"requirements-dev.txt should use pinned versions (==), not loose (>=): {line}")
            elif '~=' in line:
                # Compatible release - acceptable but prefer ==
                pass
            elif '>' in line or '<' in line:
                # Other version specifiers - should not be present
                pytest.fail(f"requirements-dev.txt should use pinned versions (==): {line}")

    def test_version_pinning_consistency(self):
        """Test that both requirements files use consistent versioning strategy"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        requirements_dev_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        
        req_content = requirements_file.read_text()
        req_dev_content = requirements_dev_file.read_text()
        
        # Extract version specifiers
        req_specifiers = re.findall(r'([>=<~!]+)', req_content)
        req_dev_specifiers = re.findall(r'([>=<~!]+)', req_dev_content)
        
        # Both should use == for pinning
        assert all('==' in spec or spec == '==' for spec in req_specifiers if spec), \
            "requirements.txt should use == for version pinning"
        assert all('==' in spec or spec == '==' for spec in req_dev_specifiers if spec), \
            "requirements-dev.txt should use == for version pinning"

    def test_requirements_txt_has_no_loose_versions(self):
        """Test that requirements.txt has no loose version specifiers"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        content = requirements_file.read_text()
        
        # Should not contain >=, >, <, <=, ~= (except in comments)
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for line in lines:
            if '>=' in line or '>' in line or '<=' in line or '<' in line or '~=' in line:
                # Check if it's in a comment
                if '#' in line:
                    comment_start = line.index('#')
                    if line.index('>=' if '>=' in line else '>' if '>' in line else '<=' if '<=' in line else '<' if '<' in line else '~=') < comment_start:
                        pytest.fail(f"requirements.txt should not have loose version specifiers: {line}")

    def test_requirements_dev_txt_has_no_loose_versions(self):
        """Test that requirements-dev.txt has no loose version specifiers"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        content = requirements_file.read_text()
        
        # Should not contain >=, >, <, <=, ~= (except in comments)
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for line in lines:
            if '>=' in line or '>' in line or '<=' in line or '<' in line or '~=' in line:
                # Check if it's in a comment
                if '#' in line:
                    comment_start = line.index('#')
                    specifiers = ['>=', '>', '<=', '<', '~=']
                    for spec in specifiers:
                        if spec in line and line.index(spec) < comment_start:
                            pytest.fail(f"requirements-dev.txt should not have loose version specifiers: {line}")

    def test_requirements_files_exist(self):
        """Test that both requirements files exist"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        requirements_dev_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        
        assert requirements_file.exists(), "requirements.txt should exist"
        assert requirements_dev_file.exists(), "requirements-dev.txt should exist"

    def test_version_format_validity(self):
        """Test that version numbers follow valid format"""
        requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
        requirements_dev_file = Path(__file__).parent.parent.parent / "requirements-dev.txt"
        
        for req_file in [requirements_file, requirements_dev_file]:
            content = req_file.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            
            for line in lines:
                if '==' in line:
                    # Extract package and version
                    parts = line.split('==')
                    if len(parts) == 2:
                        package = parts[0].strip()
                        version = parts[1].strip()
                        
                        # Version should match semantic versioning pattern
                        version_pattern = re.compile(r'^\d+\.\d+(\.\d+)?([a-zA-Z0-9.-]+)?$')
                        assert version_pattern.match(version), \
                            f"Invalid version format in {req_file.name}: {line}"
