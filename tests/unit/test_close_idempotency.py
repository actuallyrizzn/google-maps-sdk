"""
Unit tests for close() idempotency (issue #268 / #70)
"""

import pytest
import threading
import requests
from unittest.mock import patch, MagicMock, Mock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.client import GoogleMapsClient
from google_maps_sdk.exceptions import GoogleMapsAPIError


@pytest.mark.unit
class TestCloseIdempotency:
    """Test close() method idempotency"""

    def test_multiple_close_calls(self, api_key):
        """Test close() can be called multiple times safely"""
        client = BaseClient(api_key, "https://example.com")
        assert client.session is not None
        
        # Call close() multiple times
        for i in range(10):
            client.close()
            # Session should be None after first close
            if hasattr(client, '_local') and hasattr(client._local, 'session'):
                assert client._local.session is None

    def test_close_after_exception(self, api_key):
        """Test close() after exception"""
        client = BaseClient(api_key, "https://example.com")
        assert client.session is not None
        
        # Simulate an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Close should still work after exception
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None
        
        # Close again should still work
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    def test_close_in_context_manager(self, api_key):
        """Test close() idempotency in context manager"""
        with BaseClient(api_key, "https://example.com") as client:
            assert client.session is not None
        
        # After context exit, close() should still be idempotent
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None
        
        # Close again
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    def test_close_with_multiple_threads(self, api_key):
        """Test close() idempotency with multiple threads"""
        client = BaseClient(api_key, "https://example.com")
        
        close_called = []
        errors = []
        lock = threading.Lock()
        
        def close_from_thread(thread_id):
            try:
                client.close()
                with lock:
                    close_called.append(thread_id)
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create multiple threads calling close()
        threads = []
        for i in range(10):
            thread = threading.Thread(target=close_from_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All close() calls should succeed
        assert len(errors) == 0
        assert len(close_called) == 10
        
        # Session should be None
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    def test_close_after_request_error(self, api_key):
        """Test close() after request error"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            client = BaseClient(api_key, "https://example.com", timeout=1)
            
            try:
                client._get("/test")
            except GoogleMapsAPIError:
                pass
            
            # Close should work after error
            client.close()
            if hasattr(client, '_local') and hasattr(client._local, 'session'):
                assert client._local.session is None
            
            # Close again should still work
            client.close()
            if hasattr(client, '_local') and hasattr(client._local, 'session'):
                assert client._local.session is None

    def test_close_with_session_close_exception(self, api_key):
        """Test close() idempotency when session.close() raises exception"""
        client = BaseClient(api_key, "https://example.com")
        
        # Mock session.close() to raise exception
        client.session.close = Mock(side_effect=Exception("Close error"))
        
        # First close should handle exception
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None
        
        # Second close should still work (idempotent)
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    def test_close_after_context_manager_exception(self, api_key):
        """Test close() after context manager exception"""
        try:
            with BaseClient(api_key, "https://example.com") as client:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Close should still work after context manager exception
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None
        
        # Close again should still work
        client.close()
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    def test_close_routes_client_idempotency(self, api_key):
        """Test RoutesClient close() idempotency"""
        client = RoutesClient(api_key)
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_directions_client_idempotency(self, api_key):
        """Test DirectionsClient close() idempotency"""
        client = DirectionsClient(api_key)
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_roads_client_idempotency(self, api_key):
        """Test RoadsClient close() idempotency"""
        client = RoadsClient(api_key)
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_google_maps_client_idempotency(self, api_key):
        """Test GoogleMapsClient close() idempotency"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.client.RoutesClient") as mock_routes:
            with patch("google_maps_sdk.client.DirectionsClient") as mock_directions:
                with patch("google_maps_sdk.client.RoadsClient") as mock_roads:
                    mock_routes_instance = MagicMock()
                    mock_directions_instance = MagicMock()
                    mock_roads_instance = MagicMock()
                    
                    mock_routes.return_value = mock_routes_instance
                    mock_directions.return_value = mock_directions_instance
                    mock_roads.return_value = mock_roads_instance
                    
                    client = GoogleMapsClient(api_key)
                    
                    # Multiple close calls
                    for _ in range(5):
                        client.close()
                    
                    # Should not raise
                    # All sub-clients should have close() called
                    assert mock_routes_instance.close.call_count >= 1
                    assert mock_directions_instance.close.call_count >= 1
                    assert mock_roads_instance.close.call_count >= 1

    def test_close_after_operations(self, api_key):
        """Test close() idempotency after operations"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "OK"}
            mock_response.url = "https://example.com/test"
            mock_get.return_value = mock_response
            
            client = BaseClient(api_key, "https://example.com")
            
            # Perform operations
            client._get("/test")
            client._get("/test")
            
            # Close multiple times
            for _ in range(5):
                client.close()
            
            # Should not raise

    def test_close_with_rate_limiter(self, api_key):
        """Test close() idempotency with rate limiter enabled"""
        client = BaseClient(
            api_key,
            "https://example.com",
            rate_limit_max_calls=10,
            rate_limit_period=1.0
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_with_circuit_breaker(self, api_key):
        """Test close() idempotency with circuit breaker enabled"""
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        client = BaseClient(
            api_key,
            "https://example.com",
            circuit_breaker=CircuitBreaker(failure_threshold=5, timeout=1.0)
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_with_cache(self, api_key):
        """Test close() idempotency with cache enabled"""
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_cache=True,
            cache_ttl=300.0,
            cache_maxsize=100
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_after_retry_exhausted(self, api_key):
        """Test close() idempotency after retry exhausted"""
        from unittest.mock import patch
        from google_maps_sdk.retry import RetryConfig
        import requests
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            client = BaseClient(
                api_key,
                "https://example.com",
                timeout=1,
                retry_config=RetryConfig(max_retries=1, base_delay=0.01)
            )
            
            try:
                client._get("/test")
            except GoogleMapsAPIError:
                pass
            
            # Close multiple times after retry exhaustion
            for _ in range(5):
                client.close()
            
            # Should not raise

    def test_close_with_interceptors(self, api_key):
        """Test close() idempotency with interceptors"""
        client = BaseClient(api_key, "https://example.com")
        
        def hook(*args):
            pass
        
        client.add_request_hook(hook)
        client.add_response_hook(hook)
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_after_validation_error(self, api_key):
        """Test close() idempotency after validation error"""
        try:
            BaseClient("", "https://example.com")  # Invalid API key
        except ValueError:
            pass
        
        # Create valid client
        client = BaseClient(api_key, "https://example.com")
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_concurrent_with_operations(self, api_key):
        """Test close() idempotency concurrent with operations"""
        from unittest.mock import patch
        import threading
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "OK"}
            mock_response.url = "https://example.com/test"
            mock_get.return_value = mock_response
            
            client = BaseClient(api_key, "https://example.com")
            
            operations_completed = []
            close_called = []
            lock = threading.Lock()
            
            def make_request():
                try:
                    client._get("/test")
                    with lock:
                        operations_completed.append(1)
                except Exception:
                    pass
            
            def call_close():
                try:
                    client.close()
                    with lock:
                        close_called.append(1)
                except Exception:
                    pass
            
            # Mix operations and close calls
            threads = []
            for i in range(10):
                if i % 2 == 0:
                    threads.append(threading.Thread(target=make_request))
                else:
                    threads.append(threading.Thread(target=call_close))
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # All should complete without errors
            assert len(operations_completed) + len(close_called) == 10

    def test_close_state_consistency(self, api_key):
        """Test close() maintains consistent state across multiple calls"""
        client = BaseClient(api_key, "https://example.com")
        
        # Track session state
        states = []
        
        for _ in range(5):
            if hasattr(client, '_local') and hasattr(client._local, 'session'):
                states.append(client._local.session is None)
            client.close()
        
        # All states after first close should be None
        assert all(state is True for state in states[1:])

    def test_close_with_custom_adapter(self, api_key):
        """Test close() idempotency with custom HTTP adapter"""
        from requests.adapters import HTTPAdapter
        
        custom_adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1)
        client = BaseClient(
            api_key,
            "https://example.com",
            http_adapter=custom_adapter
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_after_successful_request(self, api_key):
        """Test close() idempotency after successful request"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "OK"}
            mock_response.url = "https://example.com/test"
            mock_get.return_value = mock_response
            
            client = BaseClient(api_key, "https://example.com")
            
            # Successful request
            client._get("/test")
            
            # Multiple close calls
            for _ in range(5):
                client.close()
            
            # Should not raise

    def test_close_with_compression_enabled(self, api_key):
        """Test close() idempotency with compression enabled"""
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=True,
            compression_threshold=100
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_with_custom_json_encoder(self, api_key):
        """Test close() idempotency with custom JSON encoder"""
        import json
        from datetime import datetime
        
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=CustomEncoder
        )
        
        # Multiple close calls
        for _ in range(5):
            client.close()
        
        # Should not raise

    def test_close_all_clients_idempotency(self, api_key):
        """Test close() idempotency across all client types"""
        clients = [
            BaseClient(api_key, "https://example.com"),
            RoutesClient(api_key),
            DirectionsClient(api_key),
            RoadsClient(api_key),
        ]
        
        # Close all clients multiple times
        for _ in range(5):
            for client in clients:
                client.close()
        
        # Should not raise

    def test_close_thread_safety_idempotency(self, api_key):
        """Test close() idempotency is thread-safe"""
        client = BaseClient(api_key, "https://example.com")
        
        errors = []
        lock = threading.Lock()
        
        def close_safely(thread_id):
            try:
                for _ in range(10):
                    client.close()
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create multiple threads calling close() repeatedly
        threads = []
        for i in range(5):
            thread = threading.Thread(target=close_safely, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # No errors should occur
        assert len(errors) == 0

    def test_close_after_partial_initialization(self, api_key):
        """Test close() idempotency after partial initialization"""
        client = BaseClient(api_key, "https://example.com")
        
        # Close before any operations
        client.close()
        
        # Close again
        client.close()
        
        # Should not raise

    def test_close_with_none_session(self, api_key):
        """Test close() idempotency when session is None"""
        client = BaseClient(api_key, "https://example.com")
        
        # Manually set session to None (simulating already closed)
        if hasattr(client, '_local'):
            client._local.session = None
        
        # Close should still work
        client.close()
        
        # Close again
        client.close()
        
        # Should not raise
