"""
Unit tests for caching mechanism (issue #37)
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.cache import TTLCache, generate_cache_key


@pytest.mark.unit
class TestTTLCache:
    """Test TTLCache class"""

    def test_cache_init(self):
        """Test cache initialization"""
        cache = TTLCache(maxsize=10, ttl=60.0)
        assert cache.maxsize == 10
        assert cache.ttl == 60.0
        assert len(cache) == 0

    def test_cache_set_get(self):
        """Test setting and getting cache values"""
        cache = TTLCache(maxsize=10, ttl=60.0)
        cache["key1"] = "value1"
        assert cache["key1"] == "value1"
        assert len(cache) == 1

    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = TTLCache(maxsize=10, ttl=0.1)  # Very short TTL
        cache["key1"] = "value1"
        assert "key1" in cache
        assert cache["key1"] == "value1"
        
        # Wait for expiration
        time.sleep(0.15)
        assert "key1" not in cache
        with pytest.raises(KeyError):
            _ = cache["key1"]

    def test_cache_maxsize(self):
        """Test cache respects maxsize"""
        cache = TTLCache(maxsize=2, ttl=60.0)
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        cache["key3"] = "value3"  # Should evict oldest
        
        # Should have maxsize items
        assert len(cache) == 2
        assert "key3" in cache  # Newest should be present

    def test_cache_get_default(self):
        """Test cache get with default"""
        cache = TTLCache(maxsize=10, ttl=60.0)
        assert cache.get("nonexistent", "default") == "default"
        cache["key1"] = "value1"
        assert cache.get("key1", "default") == "value1"

    def test_cache_clear(self):
        """Test clearing cache"""
        cache = TTLCache(maxsize=10, ttl=60.0)
        cache["key1"] = "value1"
        cache["key2"] = "value2"
        assert len(cache) == 2
        
        cache.clear()
        assert len(cache) == 0


@pytest.mark.unit
class TestCacheKeyGeneration:
    """Test cache key generation"""

    def test_generate_cache_key(self):
        """Test cache key generation"""
        key1 = generate_cache_key("GET", "https://example.com/test", {"param": "value"}, None)
        key2 = generate_cache_key("GET", "https://example.com/test", {"param": "value"}, None)
        
        # Same parameters should generate same key
        assert key1 == key2

    def test_cache_key_different_params(self):
        """Test different parameters generate different keys"""
        key1 = generate_cache_key("GET", "https://example.com/test", {"param": "value1"}, None)
        key2 = generate_cache_key("GET", "https://example.com/test", {"param": "value2"}, None)
        
        assert key1 != key2

    def test_cache_key_different_methods(self):
        """Test different methods generate different keys"""
        key1 = generate_cache_key("GET", "https://example.com/test", {}, None)
        key2 = generate_cache_key("POST", "https://example.com/test", {}, None)
        
        assert key1 != key2


@pytest.mark.unit
class TestBaseClientCaching:
    """Test BaseClient caching integration"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_cache_hit(self, mock_get, api_key):
        """Test cache hit returns cached response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "cached": False}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key, 
            "https://example.com",
            enable_cache=True,
            cache_ttl=60.0
        )
        
        # First call - should make request
        result1 = client._get("/test")
        assert mock_get.call_count == 1
        
        # Second call - should use cache
        result2 = client._get("/test")
        assert mock_get.call_count == 1  # No additional call
        assert result1 == result2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_cache_miss(self, mock_get, api_key):
        """Test cache miss makes request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key, 
            "https://example.com",
            enable_cache=True,
            cache_ttl=60.0
        )
        
        # Different endpoints should not hit cache
        client._get("/test1")
        client._get("/test2")
        
        assert mock_get.call_count == 2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_cache_disabled(self, mock_get, api_key):
        """Test cache disabled makes all requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key, 
            "https://example.com",
            enable_cache=False
        )
        
        # Should make request each time
        client._get("/test")
        client._get("/test")
        
        assert mock_get.call_count == 2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_post_cache(self, mock_post, api_key):
        """Test POST requests are cached"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key, 
            "https://example.com",
            enable_cache=True,
            cache_ttl=60.0
        )
        
        data = {"key": "value"}
        
        # First call
        result1 = client._post("/test", data=data)
        assert mock_post.call_count == 1
        
        # Second call with same data - should use cache
        result2 = client._post("/test", data=data)
        assert mock_post.call_count == 1
        assert result1 == result2
        
        client.close()
