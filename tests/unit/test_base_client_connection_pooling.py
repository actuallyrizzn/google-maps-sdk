"""
Unit tests for BaseClient connection pooling (issue #27)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from requests.adapters import HTTPAdapter


@pytest.mark.unit
class TestBaseClientConnectionPooling:
    """Test BaseClient connection pooling configuration"""

    def test_session_has_http_adapter(self, api_key):
        """Test that session has HTTP adapter mounted"""
        client = BaseClient(api_key, "https://example.com")
        session = client.session
        
        # Check that adapters are mounted
        assert 'https://' in session.adapters
        assert 'http://' in session.adapters
        
        # Check adapter type
        assert isinstance(session.adapters['https://'], HTTPAdapter)
        assert isinstance(session.adapters['http://'], HTTPAdapter)
        
        client.close()

    def test_adapter_configuration(self, api_key):
        """Test that adapter has correct configuration"""
        client = BaseClient(api_key, "https://example.com")
        session = client.session
        
        adapter = session.adapters['https://']
        
        # Check pool configuration (HTTPAdapter stores these as instance attributes)
        assert adapter._pool_connections == 10
        assert adapter._pool_maxsize == 20
        
        client.close()

    def test_adapter_no_retries(self, api_key):
        """Test that adapter has retries disabled (we handle retries ourselves)"""
        client = BaseClient(api_key, "https://example.com")
        session = client.session
        
        adapter = session.adapters['https://']
        
        # Check that max_retries is 0 (we handle retries in BaseClient)
        # HTTPAdapter stores max_retries as max_retries attribute
        assert adapter.max_retries is not None
        assert adapter.max_retries.total == 0
        
        client.close()

    def test_thread_local_adapters(self, api_key):
        """Test that each thread gets its own adapter configuration"""
        import threading
        
        client = BaseClient(api_key, "https://example.com")
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
        
        # Each thread should have its own adapter
        assert len(adapters) == 3
        
        # Adapters should be different objects (but same configuration)
        adapter_ids = [id(a) for a in adapters.values()]
        assert len(set(adapter_ids)) == 3  # All unique
        
        client.close()
