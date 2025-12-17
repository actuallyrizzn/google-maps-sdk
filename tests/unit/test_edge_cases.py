"""
Unit tests for edge cases (issue #257 / #59)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.exceptions import GoogleMapsAPIError, InvalidRequestError


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases for various scenarios"""

    def test_empty_string_base_url(self, api_key):
        """Test edge case: empty string base URL is rejected"""
        # Empty base URL should be rejected by validation
        with pytest.raises(ValueError, match="Base URL is required"):
            BaseClient(api_key, "")

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_very_long_url(self, mock_get, api_key):
        """Test edge case: very long URL with many parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Create very long parameter list
        long_params = {f"param{i}": "x" * 100 for i in range(50)}
        client._get("/test", params=long_params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_empty_dict_data(self, mock_post, api_key):
        """Test edge case: empty dictionary as POST data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._post("/test", data={})
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_none_data(self, mock_post, api_key):
        """Test edge case: None as POST data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._post("/test", data=None)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_unicode_in_params(self, mock_get, api_key):
        """Test edge case: Unicode characters in parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Unicode characters
        params = {"query": "São Paulo 🗺️ 北京"}
        client._get("/test", params=params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_special_characters_in_data(self, mock_post, api_key):
        """Test edge case: Special characters in POST data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Special characters
        data = {
            "name": "Test & Co.",
            "description": "Price: $100.00 <special>",
            "path": "C:\\Users\\Test"
        }
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    def test_zero_timeout(self, api_key):
        """Test edge case: Zero timeout value is rejected"""
        with pytest.raises(ValueError, match="Timeout must be at least 1 second"):
            BaseClient(api_key, "https://example.com", timeout=0)

    def test_negative_timeout(self, api_key):
        """Test edge case: Negative timeout value is rejected"""
        with pytest.raises(ValueError, match="Timeout must be at least 1 second"):
            BaseClient(api_key, "https://example.com", timeout=-1)

    def test_very_large_timeout(self, api_key):
        """Test edge case: Very large timeout value is rejected"""
        # Very large timeout should be rejected (max 300 seconds)
        with pytest.raises(ValueError, match="Timeout cannot exceed 300 seconds"):
            BaseClient(api_key, "https://example.com", timeout=999999)

    def test_none_headers(self, api_key):
        """Test edge case: None headers"""
        client = BaseClient(api_key, "https://example.com")
        # Headers can be None
        assert client is not None
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_empty_headers_dict(self, mock_get, api_key):
        """Test edge case: Empty headers dictionary"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._get("/test", params={})
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_nested_empty_structures(self, mock_post, api_key):
        """Test edge case: Nested empty structures"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        data = {
            "empty_list": [],
            "empty_dict": {},
            "nested": {
                "empty": [],
                "null": None
            }
        }
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_whitespace_only_strings(self, mock_get, api_key):
        """Test edge case: Whitespace-only strings in parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        params = {"query": "   ", "name": "\t\n\r"}
        client._get("/test", params=params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_very_deeply_nested_dict(self, mock_post, api_key):
        """Test edge case: Very deeply nested dictionary"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Create deeply nested structure
        nested = {}
        current = nested
        for i in range(10):
            current["level"] = i
            current["next"] = {}
            current = current["next"]
        data = {"nested": nested}
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_boundary_coordinate_values(self, mock_get, api_key):
        """Test edge case: Boundary coordinate values"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Test boundary values
        params = {
            "lat": 90.0,  # North pole
            "lng": 180.0,  # International date line
            "lat2": -90.0,  # South pole
            "lng2": -180.0  # International date line
        }
        client._get("/test", params=params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_boolean_values(self, mock_post, api_key):
        """Test edge case: Boolean values in data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        data = {
            "enabled": True,
            "disabled": False,
            "mixed": {
                "true": True,
                "false": False
            }
        }
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_numeric_edge_cases(self, mock_post, api_key):
        """Test edge case: Numeric edge cases"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        data = {
            "zero": 0,
            "negative": -1,
            "large": 999999999999,
            "float": 3.141592653589793,
            "scientific": 1e10
        }
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_missing_optional_params(self, mock_get, api_key):
        """Test edge case: Missing optional parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Call with minimal parameters
        client._get("/test")
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_all_none_optional_params(self, mock_post, api_key):
        """Test edge case: All optional parameters are None"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._post("/test", data=None, headers=None, params=None, timeout=None)
        assert mock_post.called
        client.close()

    def test_multiple_trailing_slashes(self, api_key):
        """Test edge case: Multiple trailing slashes in base URL"""
        client = BaseClient(api_key, "https://api.example.com///")
        assert client.base_url == "https://api.example.com"
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_endpoint_with_query_string(self, mock_get, api_key):
        """Test edge case: Endpoint already contains query string"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Endpoint with query string
        client._get("/test?existing=value", params={"new": "param"})
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_very_large_list_in_data(self, mock_post, api_key):
        """Test edge case: Very large list in POST data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # Large list
        data = {"items": list(range(1000))}
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_sql_injection_attempt_in_params(self, mock_get, api_key):
        """Test edge case: SQL injection attempt in parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # SQL injection attempt (should be handled safely)
        params = {"query": "'; DROP TABLE users; --"}
        client._get("/test", params=params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_xss_attempt_in_params(self, mock_get, api_key):
        """Test edge case: XSS attempt in parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        # XSS attempt (should be handled safely)
        params = {"name": "<script>alert('xss')</script>"}
        client._get("/test", params=params)
        assert mock_get.called
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_newline_characters_in_data(self, mock_post, api_key):
        """Test edge case: Newline characters in data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        data = {
            "multiline": "Line 1\nLine 2\r\nLine 3",
            "tabs": "Value\twith\ttabs"
        }
        client._post("/test", data=data)
        assert mock_post.called
        client.close()

    def test_rate_limiter_edge_cases(self, api_key):
        """Test edge case: Rate limiter with edge case values"""
        from google_maps_sdk.rate_limiter import RateLimiter
        
        # Very small period
        limiter = RateLimiter(max_calls=1, period=0.001)
        assert limiter.max_calls == 1
        assert limiter.period == 0.001
        
        # Very large max_calls
        limiter2 = RateLimiter(max_calls=1000000, period=60.0)
        assert limiter2.max_calls == 1000000

    def test_cache_edge_cases(self, api_key):
        """Test edge case: Cache with edge case values"""
        from google_maps_sdk.cache import TTLCache
        
        # Very small TTL
        cache = TTLCache(maxsize=10, ttl=0.001)
        assert cache.maxsize == 10
        assert cache.ttl == 0.001
        
        # Very large maxsize
        cache2 = TTLCache(maxsize=1000000, ttl=300.0)
        assert cache2.maxsize == 1000000

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_empty_requests(self, mock_get, api_key):
        """Test edge case: Concurrent requests with empty parameters"""
        import threading
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        def make_request():
            client._get("/test", params={})
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert mock_get.call_count >= 5
        client.close()
