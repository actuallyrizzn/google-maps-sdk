"""
Unit tests for BaseClient rate limiting (issue #5)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import QuotaExceededError


@pytest.mark.unit
class TestBaseClientRateLimiting:
    """Test rate limiting in BaseClient"""

    def test_rate_limiting_disabled_by_default(self, api_key):
        """Test rate limiting is disabled by default"""
        client = BaseClient(api_key, "https://example.com")
        assert client._rate_limiter is None
        client.close()

    def test_rate_limiting_enabled(self, api_key):
        """Test rate limiting can be enabled"""
        client = BaseClient(
            api_key, 
            "https://example.com",
            rate_limit_max_calls=10,
            rate_limit_period=60.0
        )
        assert client._rate_limiter is not None
        assert client._rate_limiter.max_calls == 10
        assert client._rate_limiter.period == 60.0
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_get_respects_rate_limit(self, mock_get, api_key):
        """Test _get respects rate limit"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            rate_limit_max_calls=2,
            rate_limit_period=1.0
        )
        
        # First two calls should succeed
        client._get("/test")
        client._get("/test")
        
        # Third call should fail with rate limit
        with pytest.raises(QuotaExceededError):
            client._get("/test")
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_post_respects_rate_limit(self, mock_post, api_key):
        """Test _post respects rate limit"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            rate_limit_max_calls=1,
            rate_limit_period=1.0
        )
        
        # First call should succeed
        client._post("/test", data={"test": "data"})
        
        # Second call should fail with rate limit
        with pytest.raises(QuotaExceededError):
            client._post("/test", data={"test": "data"})
        
        client.close()
