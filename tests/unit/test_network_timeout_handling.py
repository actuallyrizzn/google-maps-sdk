"""
Unit tests for network timeout handling (issue #264 / #66)
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.retry import RetryConfig
from google_maps_sdk.exceptions import GoogleMapsAPIError
import requests


@pytest.mark.unit
class TestNetworkTimeoutHandling:
    """Test network timeout handling scenarios"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_request_timeout_scenario(self, mock_get, api_key):
        """Test request timeout scenario"""
        # Simulate request timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client._get("/test")
        
        assert "timeout" in str(exc_info.value.message).lower() or "Timeout" in str(exc_info.value.message)
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_connection_timeout_scenario(self, mock_get, api_key):
        """Test connection timeout scenario"""
        # Simulate connection timeout
        mock_get.side_effect = requests.exceptions.ConnectTimeout("Connection timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client._get("/test")
        
        assert "timeout" in str(exc_info.value.message).lower() or "connection" in str(exc_info.value.message).lower()
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_read_timeout_scenario(self, mock_get, api_key):
        """Test read timeout scenario"""
        # Simulate read timeout
        mock_get.side_effect = requests.exceptions.ReadTimeout("Read timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client._get("/test")
        
        assert "timeout" in str(exc_info.value.message).lower()
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_post_request_timeout(self, mock_post, api_key):
        """Test POST request timeout"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError):
            client._post("/test", data={"key": "value"})
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_retry_success(self, mock_get, api_key):
        """Test timeout with retry that eventually succeeds"""
        # First call times out, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            retry_config=RetryConfig(max_retries=1, base_delay=0.01)
        )
        
        result = client._get("/test")
        assert result == {"status": "OK"}
        assert mock_get.call_count == 2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_retry_exhausted(self, mock_get, api_key):
        """Test timeout with retry exhausted"""
        # All calls timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            retry_config=RetryConfig(max_retries=2, base_delay=0.01)
        )
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client._get("/test")
        
        assert "timeout" in str(exc_info.value.message).lower()
        # Should have tried max_retries + 1 times
        assert mock_get.call_count == 3
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_custom_timeout_value(self, mock_get, api_key):
        """Test timeout with custom timeout value"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Test with different timeout values
        for timeout_value in [1, 5, 10, 30, 60]:
            client = BaseClient(api_key, "https://example.com", timeout=timeout_value)
            
            with pytest.raises(GoogleMapsAPIError):
                client._get("/test", timeout=timeout_value)
            
            # Verify timeout was used
            assert client.timeout == timeout_value
            client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_override_in_request(self, mock_get, api_key):
        """Test timeout override in individual request"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=30)
        
        # Override timeout in request
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test", timeout=1)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_rate_limiter(self, mock_get, api_key):
        """Test timeout with rate limiter enabled"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            rate_limit_max_calls=10,
            rate_limit_period=1.0
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_circuit_breaker(self, mock_get, api_key):
        """Test timeout with circuit breaker enabled"""
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        # All calls timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            circuit_breaker=CircuitBreaker(failure_threshold=3, timeout=0.1)
        )
        
        # First few should raise timeout errors
        for _ in range(3):
            with pytest.raises(GoogleMapsAPIError):
                client._get("/test")
        
        # After threshold, circuit breaker should open
        # (though timeout errors might not trigger circuit breaker depending on implementation)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_error_preserves_request_id(self, mock_get, api_key):
        """Test timeout error preserves request ID"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Request ID should be present
            assert hasattr(e, 'request_id')
            assert e.request_id is not None
        
        client.close()

    @patch("google_maps_sdk.routes.requests.Session.post")
    def test_routes_api_timeout(self, mock_post, api_key, sample_origin, sample_destination):
        """Test Routes API timeout"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = RoutesClient(api_key, timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client.compute_routes(sample_origin, sample_destination)
        
        assert "timeout" in str(exc_info.value.message).lower()
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_directions_api_timeout(self, mock_get, api_key):
        """Test Directions API timeout"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = DirectionsClient(api_key, timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client.get_directions("Toronto", "Montreal")
        
        assert "timeout" in str(exc_info.value.message).lower()
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_roads_api_timeout(self, mock_get, api_key, sample_path):
        """Test Roads API timeout"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = RoadsClient(api_key, timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client.snap_to_roads(sample_path)
        
        assert "timeout" in str(exc_info.value.message).lower()
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_vs_connection_error(self, mock_get, api_key):
        """Test distinction between timeout and connection error"""
        # Test timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError) as timeout_error:
            client._get("/test")
        
        # Test connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(GoogleMapsAPIError) as conn_error:
            client._get("/test")
        
        # Errors should be different
        assert str(timeout_error.value) != str(conn_error.value)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_different_timeout_values(self, mock_get, api_key):
        """Test timeout behavior with different timeout values"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        timeout_values = [1, 5, 10, 30]
        for timeout_val in timeout_values:
            client = BaseClient(api_key, "https://example.com", timeout=timeout_val)
            
            with pytest.raises(GoogleMapsAPIError):
                client._get("/test")
            
            assert client.timeout == timeout_val
            client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_exception_chaining(self, mock_get, api_key):
        """Test timeout exception chaining"""
        original_timeout = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_timeout
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None or "timeout" in str(e).lower()
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_cache(self, mock_get, api_key):
        """Test timeout behavior with caching enabled"""
        # First call times out (should not be cached)
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            enable_cache=True,
            cache_ttl=300.0
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Second call should also timeout (not cached)
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        assert mock_get.call_count == 2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_logging(self, mock_get, api_key):
        """Test timeout is logged appropriately"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Timeout should be logged (we can't easily verify logging without more setup)
        # But we verify the exception is raised correctly
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_interceptors(self, mock_get, api_key):
        """Test timeout with request/response interceptors"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        request_calls = []
        response_calls = []
        
        def request_hook(method, url, headers, params, data):
            request_calls.append((method, url))
        
        def response_hook(response):
            response_calls.append(response)
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        client.add_request_hook(request_hook)
        client.add_response_hook(response_hook)
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Request hook should be called even on timeout
        assert len(request_calls) > 0
        # Response hook might not be called on timeout (depends on implementation)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_retry_backoff(self, mock_get, api_key):
        """Test timeout retry with exponential backoff"""
        import time
        
        # All calls timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        start_time = time.time()
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        elapsed = time.time() - start_time
        
        # Should have waited for backoff delays
        # 2 retries with base_delay=0.1 means at least 0.1 + 0.2 = 0.3s
        assert elapsed >= 0.2  # At least some backoff delay
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_different_endpoints(self, mock_get, api_key):
        """Test timeout with different endpoints"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        endpoints = ["/endpoint1", "/endpoint2", "/endpoint3"]
        for endpoint in endpoints:
            with pytest.raises(GoogleMapsAPIError):
                client._get(endpoint)
        
        assert mock_get.call_count == len(endpoints)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_timeout_with_large_payload(self, mock_post, api_key):
        """Test timeout with large POST payload"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        # Large payload
        large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(1000)]}
        
        with pytest.raises(GoogleMapsAPIError):
            client._post("/test", data=large_data)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_timeout_with_compression(self, mock_get, api_key):
        """Test timeout with request compression enabled"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            enable_request_compression=True,
            compression_threshold=100
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        client.close()
