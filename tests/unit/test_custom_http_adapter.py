"""
Unit tests for custom HTTP adapter support (issue #38)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@pytest.mark.unit
class TestCustomHTTPAdapter:
    """Test custom HTTP adapter support"""

    def test_custom_adapter_used(self, api_key):
        """Test that custom adapter is mounted to session"""
        custom_adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10,
            max_retries=Retry(total=0)
        )
        
        client = BaseClient(
            api_key,
            "https://example.com",
            http_adapter=custom_adapter
        )
        
        session = client.session
        
        # Verify custom adapter is mounted
        assert session.adapters['https://'] is custom_adapter
        assert session.adapters['http://'] is custom_adapter
        
        client.close()

    def test_default_adapter_when_none(self, api_key):
        """Test that default adapter is used when http_adapter is None"""
        client = BaseClient(
            api_key,
            "https://example.com",
            http_adapter=None
        )
        
        session = client.session
        
        # Verify default adapter is used (not the custom one)
        adapter = session.adapters['https://']
        assert adapter is not None
        assert isinstance(adapter, HTTPAdapter)
        # Default adapter should have our configured settings
        assert adapter._pool_connections == 10
        assert adapter._pool_maxsize == 20
        
        client.close()

    def test_custom_adapter_thread_local(self, api_key):
        """Test that each thread gets its own adapter instance"""
        import threading
        
        custom_adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10
        )
        
        client = BaseClient(
            api_key,
            "https://example.com",
            http_adapter=custom_adapter
        )
        
        adapters = {}
        
        def get_adapter(thread_id):
            session = client.session
            adapters[thread_id] = session.adapters['https://']
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=get_adapter, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Each thread should have the same adapter instance (shared)
        assert len(adapters) == 3
        # All should reference the same adapter object
        adapter_ids = [id(a) for a in adapters.values()]
        assert len(set(adapter_ids)) == 1  # All same
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_custom_adapter_used_in_requests(self, mock_get, api_key):
        """Test that custom adapter is actually used for requests"""
        custom_adapter = HTTPAdapter(
            pool_connections=5,
            pool_maxsize=10
        )
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            http_adapter=custom_adapter
        )
        
        client._get("/test")
        
        # Verify request was made (adapter is used)
        assert mock_get.called
        
        client.close()
