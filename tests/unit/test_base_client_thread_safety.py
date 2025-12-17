"""
Unit tests for BaseClient thread safety (issue #19)
"""

import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient


@pytest.mark.unit
class TestBaseClientThreadSafety:
    """Test BaseClient thread safety with thread-local sessions"""

    def test_thread_local_sessions(self, api_key):
        """Test that each thread gets its own session"""
        client = BaseClient(api_key, "https://example.com")
        
        sessions = {}
        errors = []
        
        def get_session(thread_id):
            try:
                sessions[thread_id] = client.session
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=get_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # No errors should occur
        assert len(errors) == 0
        
        # Each thread should have its own session
        assert len(sessions) == 5
        
        # Sessions should be different objects
        session_ids = [id(s) for s in sessions.values()]
        assert len(set(session_ids)) == 5  # All unique
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests(self, mock_get, api_key):
        """Test concurrent requests from different threads"""
        client = BaseClient(api_key, "https://example.com")
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                # Each thread gets its own mock response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "OK", "thread": thread_id}
                mock_response.url = f"https://example.com/test?thread={thread_id}"
                
                # Mock get to return our response
                mock_get.return_value = mock_response
                
                result = client._get("/test")
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create multiple threads making requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 10
        
        client.close()

    def test_session_property_lazy_creation(self, api_key):
        """Test that session is created lazily on first access"""
        client = BaseClient(api_key, "https://example.com")
        
        # Session should not exist before first access
        assert not hasattr(client._local, 'session')
        
        # Accessing session property should create it
        session = client.session
        assert session is not None
        assert hasattr(client._local, 'session')
        assert client._local.session is session
        
        client.close()

    def test_session_configuration(self, api_key):
        """Test that thread-local sessions have correct configuration"""
        client = BaseClient(api_key, "https://example.com")
        
        session = client.session
        
        # Verify SSL verification is enforced
        assert session.verify is True
        
        # Verify headers are set
        assert 'User-Agent' in session.headers
        assert 'Accept-Encoding' in session.headers
        
        client.close()

    def test_close_thread_local(self, api_key):
        """Test that close() only affects current thread's session"""
        client = BaseClient(api_key, "https://example.com")
        
        # Create sessions in multiple threads
        thread_sessions = {}
        
        def create_session(thread_id):
            thread_sessions[thread_id] = client.session
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Close from main thread
        client.close()
        
        # Main thread's session should be closed
        assert not hasattr(client._local, 'session') or client._local.session is None
        
        # Other threads' sessions are still in their thread-local storage
        # (We can't easily verify this without accessing from those threads)
        
        client.close()
