"""
Unit tests for BaseClient close() and context manager (issue #17)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google_maps_sdk.base_client import BaseClient


@pytest.mark.unit
class TestBaseClientClose:
    """Test BaseClient.close() method"""

    def test_close_success(self, api_key):
        """Test successful close"""
        client = BaseClient(api_key, "https://example.com")
        assert client.session is not None
        
        # Close should succeed
        client.close()
        
        # Session should be None after close
        assert client.session is None

    def test_close_idempotent(self, api_key):
        """Test close() can be called multiple times safely"""
        client = BaseClient(api_key, "https://example.com")
        
        # First close
        client.close()
        assert client.session is None
        
        # Second close should not raise
        client.close()
        assert client.session is None
        
        # Third close should not raise
        client.close()
        assert client.session is None

    def test_close_handles_exception(self, api_key):
        """Test close() handles exceptions gracefully"""
        client = BaseClient(api_key, "https://example.com")
        
        # Mock session.close() to raise an exception
        client.session.close = Mock(side_effect=Exception("Close error"))
        
        # Close should not raise, even if session.close() fails
        client.close()
        
        # Session should still be set to None
        assert client.session is None

    def test_close_after_already_closed(self, api_key):
        """Test close() after session is already closed"""
        client = BaseClient(api_key, "https://example.com")
        
        # Close once
        client.close()
        assert client.session is None
        
        # Close again - should not raise
        client.close()
        assert client.session is None


@pytest.mark.unit
class TestBaseClientContextManager:
    """Test BaseClient context manager"""

    def test_context_manager_success(self, api_key):
        """Test context manager closes session on success"""
        with BaseClient(api_key, "https://example.com") as client:
            assert client.session is not None
        
        # Session should be closed after context exit
        assert client.session is None

    def test_context_manager_exception(self, api_key):
        """Test context manager closes session even on exception"""
        try:
            with BaseClient(api_key, "https://example.com") as client:
                assert client.session is not None
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Session should still be closed even though exception occurred
        assert client.session is None

    def test_context_manager_close_exception(self, api_key):
        """Test context manager handles exceptions during close()"""
        with BaseClient(api_key, "https://example.com") as client:
            # Mock close() to raise an exception
            original_close = client.close
            def failing_close():
                try:
                    original_close()
                except Exception:
                    pass
                # Simulate exception during close
                raise Exception("Close failed")
            
            client.close = failing_close
        
        # Even if close() raises, __exit__ should handle it
        # The session should still be None (set during first close attempt)
        # This test verifies __exit__ doesn't propagate close() exceptions
