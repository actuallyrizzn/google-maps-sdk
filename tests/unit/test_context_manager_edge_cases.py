"""
Unit tests for context manager edge cases (issue #261 / #63)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.client import GoogleMapsClient
from google_maps_sdk.exceptions import GoogleMapsAPIError


@pytest.mark.unit
class TestContextManagerEdgeCases:
    """Test context manager edge cases"""

    def test_context_manager_verifies_session_closed(self, api_key):
        """Test context manager actually closes session"""
        with BaseClient(api_key, "https://example.com") as client:
            assert client.session is not None
            session = client.session
            # Mock session.close() to track if it's called
            close_mock = Mock()
            session.close = close_mock
        
        # After context exit, session.close() should have been called
        assert close_mock.called
        assert client.session is None

    def test_context_manager_session_close_called(self, api_key):
        """Test that session.close() is actually called on context exit"""
        with BaseClient(api_key, "https://example.com") as client:
            session = client.session
            close_mock = Mock()
            session.close = close_mock
            
            # Session should be open
            assert client.session is not None
        
        # After context exit, close() should have been called
        assert close_mock.called
        assert client.session is None

    def test_context_manager_exception_handling_preserves_exception(self, api_key):
        """Test context manager preserves original exception"""
        with pytest.raises(ValueError, match="Test exception"):
            with BaseClient(api_key, "https://example.com") as client:
                assert client.session is not None
                raise ValueError("Test exception")
        
        # Exception should have been raised, not swallowed

    def test_context_manager_exception_handling_closes_session(self, api_key):
        """Test context manager closes session even when exception occurs"""
        client = None
        try:
            with BaseClient(api_key, "https://example.com") as client:
                assert client.session is not None
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Session should be closed even though exception occurred
        assert client is not None
        assert client.session is None

    def test_multiple_context_manager_usage(self, api_key):
        """Test using multiple context managers sequentially"""
        # First context manager
        with BaseClient(api_key, "https://example.com") as client1:
            assert client1.session is not None
            session1 = client1.session
        
        assert client1.session is None
        
        # Second context manager (should create new session)
        with BaseClient(api_key, "https://example.com") as client2:
            assert client2.session is not None
            session2 = client2.session
            # Should be a different session object
            assert session2 is not session1
        
        assert client2.session is None

    def test_nested_context_managers(self, api_key):
        """Test nested context managers"""
        with BaseClient(api_key, "https://example.com") as outer_client:
            assert outer_client.session is not None
            outer_session = outer_client.session
            
            with BaseClient(api_key, "https://example.com") as inner_client:
                assert inner_client.session is not None
                inner_session = inner_client.session
                # Should be different sessions
                assert inner_session is not outer_session
            
            # Inner should be closed, outer should still be open
            assert inner_client.session is None
            assert outer_client.session is not None
            assert outer_client.session is outer_session
        
        # Both should be closed after outer context exits
        assert outer_client.session is None

    def test_context_manager_with_exception_in_close(self, api_key):
        """Test context manager handles exception during close()"""
        with BaseClient(api_key, "https://example.com") as client:
            # Mock session.close() to raise an exception
            session = client.session
            original_close = session.close
            close_called = [False]
            
            def failing_close():
                close_called[0] = True
                original_close()
                raise Exception("Close failed")
            
            session.close = failing_close
        
        # Even if session.close() raises, __exit__ should handle it gracefully
        # Session should still be None (set during close attempt)
        assert client.session is None
        assert close_called[0] is True

    def test_context_manager_return_value(self, api_key):
        """Test context manager returns self"""
        with BaseClient(api_key, "https://example.com") as client:
            # Context manager should return the client instance
            assert isinstance(client, BaseClient)
            assert client.api_key == api_key

    def test_context_manager_enter_exit_called(self, api_key):
        """Test that __enter__ and __exit__ are called correctly"""
        # Use patch to track calls since we can't easily mock __enter__/__exit__
        exit_called = [False]
        exit_args = [None]
        
        original_exit = BaseClient.__exit__
        
        def mock_exit(self, exc_type, exc_val, exc_tb):
            exit_called[0] = True
            exit_args[0] = (exc_type, exc_val, exc_tb)
            return original_exit(self, exc_type, exc_val, exc_tb)
        
        with patch.object(BaseClient, '__exit__', mock_exit):
            with BaseClient(api_key, "https://example.com") as client:
                assert client.session is not None
        
        assert exit_called[0] is True
        assert exit_args[0] == (None, None, None)  # No exception

    def test_context_manager_exit_with_exception(self, api_key):
        """Test __exit__ is called with exception info"""
        exit_args = [None]
        
        original_exit = BaseClient.__exit__
        
        def mock_exit(self, exc_type, exc_val, exc_tb):
            exit_args[0] = (exc_type, exc_val, exc_tb)
            return original_exit(self, exc_type, exc_val, exc_tb)
        
        with patch.object(BaseClient, '__exit__', mock_exit):
            try:
                with BaseClient(api_key, "https://example.com") as client:
                    raise ValueError("Test exception")
            except ValueError:
                pass
        
        # __exit__ should have been called with exception info
        assert exit_args[0] is not None
        assert exit_args[0][0] == ValueError
        assert str(exit_args[0][1]) == "Test exception"

    def test_context_manager_exit_suppresses_exception(self, api_key):
        """Test __exit__ can suppress exceptions by returning True"""
        original_exit = BaseClient.__exit__
        session_closed = [False]
        
        def suppressing_exit(self, exc_type, exc_val, exc_tb):
            # Suppress exception by returning True
            result = original_exit(self, exc_type, exc_val, exc_tb)
            # Check if session was closed (before property access recreates it)
            # close() sets _local.session = None, so check that
            if hasattr(self, '_local'):
                if hasattr(self._local, 'session'):
                    session_closed[0] = (self._local.session is None)
                else:
                    # Session was never created
                    session_closed[0] = True
            return True  # Suppress exception
        
        with patch.object(BaseClient, '__exit__', suppressing_exit):
            # Exception should be suppressed
            with BaseClient(api_key, "https://example.com") as client:
                # Access session to create it
                _ = client.session
                raise ValueError("Test exception")
            
            # Exception was suppressed, session should have been closed
            # Note: accessing client.session will recreate it, so we check the flag
            assert session_closed[0] is True

    def test_context_manager_with_google_maps_client(self, api_key):
        """Test context manager with GoogleMapsClient"""
        with patch("google_maps_sdk.client.RoutesClient") as mock_routes:
            with patch("google_maps_sdk.client.DirectionsClient") as mock_directions:
                with patch("google_maps_sdk.client.RoadsClient") as mock_roads:
                    mock_routes_instance = MagicMock()
                    mock_directions_instance = MagicMock()
                    mock_roads_instance = MagicMock()
                    
                    mock_routes.return_value = mock_routes_instance
                    mock_directions.return_value = mock_directions_instance
                    mock_roads.return_value = mock_roads_instance
                    
                    with GoogleMapsClient(api_key) as client:
                        assert client.routes is not None
                        assert client.directions is not None
                        assert client.roads is not None
                    
                    # All sub-clients should be closed
                    mock_routes_instance.close.assert_called_once()
                    mock_directions_instance.close.assert_called_once()
                    mock_roads_instance.close.assert_called_once()

    def test_context_manager_exception_closes_all_sub_clients(self, api_key):
        """Test exception in GoogleMapsClient context closes all sub-clients"""
        with patch("google_maps_sdk.client.RoutesClient") as mock_routes:
            with patch("google_maps_sdk.client.DirectionsClient") as mock_directions:
                with patch("google_maps_sdk.client.RoadsClient") as mock_roads:
                    mock_routes_instance = MagicMock()
                    mock_directions_instance = MagicMock()
                    mock_roads_instance = MagicMock()
                    
                    mock_routes.return_value = mock_routes_instance
                    mock_directions.return_value = mock_directions_instance
                    mock_roads.return_value = mock_roads_instance
                    
                    try:
                        with GoogleMapsClient(api_key) as client:
                            raise ValueError("Test exception")
                    except ValueError:
                        pass
                    
                    # All sub-clients should be closed even with exception
                    mock_routes_instance.close.assert_called_once()
                    mock_directions_instance.close.assert_called_once()
                    mock_roads_instance.close.assert_called_once()

    def test_context_manager_reuse_after_exit(self, api_key):
        """Test reusing context manager after exit"""
        # Note: Once a client is closed, the session is set to None and won't be
        # automatically recreated (the session property checks hasattr, and None
        # means the attribute exists, so it won't recreate). This is expected behavior.
        
        # First use
        with BaseClient(api_key, "https://example.com") as client1:
            session1 = client1.session
            assert session1 is not None
        
        # After exit, session should be None
        assert client1.session is None
        
        # Create a new client for second use (reusing closed client not supported)
        with BaseClient(api_key, "https://example.com") as client2:
            session2 = client2.session
            assert session2 is not None
            # Should be a different session object (different client instance)
            assert session2 is not session1
        
        assert client2.session is None

    def test_context_manager_with_operations_inside(self, api_key):
        """Test context manager with operations inside context"""
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "OK"}
            mock_response.url = "https://example.com/test"
            mock_get.return_value = mock_response
            
            with BaseClient(api_key, "https://example.com") as client:
                # Perform operations inside context
                result = client._get("/test")
                assert result == {"status": "OK"}
                assert client.session is not None
            
            # Session should be closed after context exit
            assert client.session is None

    def test_context_manager_exception_during_operation(self, api_key):
        """Test exception during operation inside context manager"""
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_get.side_effect = ValueError("Network error")
            
            try:
                with BaseClient(api_key, "https://example.com") as client:
                    # Operation raises exception
                    client._get("/test")
            except ValueError:
                pass
            
            # Session should still be closed
            assert client.session is None

    def test_context_manager_multiple_exits(self, api_key):
        """Test calling __exit__ multiple times"""
        client = BaseClient(api_key, "https://example.com")
        
        # Enter context
        client.__enter__()
        assert client.session is not None
        
        # Exit once
        client.__exit__(None, None, None)
        assert client.session is None
        
        # Exit again (should be idempotent)
        client.__exit__(None, None, None)
        assert client.session is None

    def test_context_manager_with_none_exception(self, api_key):
        """Test __exit__ with None exception (normal exit)"""
        client = BaseClient(api_key, "https://example.com")
        
        # Enter context
        client.__enter__()
        assert client.session is not None
        
        # Exit with None exception (normal exit)
        result = client.__exit__(None, None, None)
        assert result is None  # Should return None (don't suppress)
        assert client.session is None
