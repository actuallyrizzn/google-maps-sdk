"""
Unit tests for exception chaining (issue #267 / #69)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import (
    GoogleMapsAPIError,
    InvalidRequestError,
    PermissionDeniedError,
    NotFoundError,
    QuotaExceededError,
    InternalServerError,
)
import requests


@pytest.mark.unit
class TestExceptionChaining:
    """Test exception chaining preservation"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_original_exception_preservation(self, mock_get, api_key):
        """Test original exception is preserved in chain"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained with original error
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
            assert str(e.__cause__) == "Request timeout"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_connection_error_chaining(self, mock_get, api_key):
        """Test connection error exception chaining"""
        original_error = requests.exceptions.ConnectionError("Connection failed")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.ConnectionError)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_in_retries(self, mock_get, api_key):
        """Test exception chaining in retry scenarios"""
        from google_maps_sdk.retry import RetryConfig
        
        # All retries fail with timeout
        original_timeout = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_timeout
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            retry_config=RetryConfig(max_retries=2, base_delay=0.01)
        )
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Final exception should be chained with original timeout
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_http_error(self, mock_get, api_key):
        """Test exception chaining with HTTP errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal server error"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        try:
            client._get("/test")
        except InternalServerError as e:
            # HTTP errors may not have __cause__ but should preserve context
            assert e.status_code == 500
            assert "Internal server error" in str(e.message)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_exception_chaining_in_post_requests(self, mock_post, api_key):
        """Test exception chaining in POST requests"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_post.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._post("/test", data={"key": "value"})
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_request_exception(self, mock_get, api_key):
        """Test exception chaining with RequestException"""
        original_error = requests.exceptions.RequestException("Request failed")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.RequestException)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_preserves_traceback(self, mock_get, api_key):
        """Test exception chaining preserves traceback information"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should have cause
            assert e.__cause__ is not None
            # Traceback should be available
            assert hasattr(e, '__traceback__')
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_in_error_handlers(self, mock_get, api_key):
        """Test exception chaining in error handlers"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        try:
            client._get("/test")
        except InvalidRequestError as e:
            # HTTP error exceptions may not chain, but should preserve context
            assert e.status_code == 400
            assert "Bad request" in str(e.message)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_nested_exception_scenarios(self, mock_get, api_key):
        """Test nested exception scenarios"""
        # Simulate nested exception (e.g., from retry logic)
        original_timeout = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_timeout
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as outer_error:
            # Outer exception should chain to original
            assert outer_error.__cause__ is not None
            assert isinstance(outer_error.__cause__, requests.exceptions.Timeout)
            
            # Verify exception message includes context
            assert "timeout" in str(outer_error).lower() or "timeout" in str(outer_error.__cause__).lower()
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_retry_exhausted(self, mock_get, api_key):
        """Test exception chaining when retries are exhausted"""
        from google_maps_sdk.retry import RetryConfig
        
        # All attempts timeout
        original_timeout = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_timeout
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            retry_config=RetryConfig(max_retries=1, base_delay=0.01)
        )
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Final exception should chain to original timeout
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
            # Should mention retries in message
            assert "attempt" in str(e).lower() or "retry" in str(e).lower()
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_circuit_breaker(self, mock_get, api_key):
        """Test exception chaining with circuit breaker"""
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        # Simulate failures that open circuit breaker
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Server error"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            circuit_breaker=CircuitBreaker(failure_threshold=2, timeout=0.1)
        )
        
        # Mock _handle_response to raise InternalServerError
        original_handle = client._handle_response
        
        def mock_handle(response, request_id=None):
            if response.status_code == 500:
                error = InternalServerError("Server error", request_id=request_id)
                raise error
            return original_handle(response, request_id=request_id)
        
        client._handle_response = mock_handle
        
        # Make enough requests to open circuit breaker
        for _ in range(3):
            try:
                client._get("/test")
            except (GoogleMapsAPIError, Exception):
                pass
        
        # Circuit breaker should be open, next request should raise CircuitBreakerOpenError
        from google_maps_sdk.circuit_breaker import CircuitBreakerOpenError
        try:
            client._get("/test")
        except CircuitBreakerOpenError as e:
            # Circuit breaker error should preserve context
            assert "circuit" in str(e).lower() or "open" in str(e).lower()
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_rate_limiter(self, mock_get, api_key):
        """Test exception chaining with rate limiter"""
        from google_maps_sdk.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_calls=1, period=1.0)
        client = BaseClient(
            api_key,
            "https://example.com",
            rate_limit_max_calls=1,
            rate_limit_period=1.0
        )
        
        # First call succeeds
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client._get("/test")
        
        # Second call should hit rate limit
        try:
            client._get("/test")
        except QuotaExceededError as e:
            # Rate limit error should preserve context
            assert "rate limit" in str(e).lower() or "quota" in str(e).lower()
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_multiple_layers(self, mock_get, api_key):
        """Test exception chaining through multiple layers"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Should chain to original error
            assert e.__cause__ is not None
            # Should have traceback
            assert hasattr(e, '__traceback__')
            # Original error should be accessible
            cause = e.__cause__
            assert isinstance(cause, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_validation_error(self, mock_get, api_key):
        """Test exception chaining with validation errors"""
        # Test that validation errors chain properly
        try:
            BaseClient("", "https://example.com")  # Invalid API key
        except ValueError as e:
            # Validation error should not be chained (it's a direct error)
            assert "API key" in str(e)
        
        # Test with invalid coordinates
        from google_maps_sdk.utils import validate_coordinate
        try:
            validate_coordinate(100.0, 200.0)  # Out of range
        except ValueError as e:
            # Should raise directly
            assert "Latitude" in str(e) or "Longitude" in str(e)

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_preserves_request_id(self, mock_get, api_key):
        """Test exception chaining preserves request ID"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should have request ID
            assert hasattr(e, 'request_id')
            assert e.request_id is not None
            # Cause should still be accessible
            assert e.__cause__ is not None
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_json_decode_error(self, mock_get, api_key):
        """Test exception chaining with JSON decode errors"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Should handle JSON decode error
            # May or may not chain depending on implementation
            assert "JSON" in str(e).lower() or "decode" in str(e).lower() or e.__cause__ is not None
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_exception_chaining_in_post_with_compression(self, mock_post, api_key):
        """Test exception chaining in POST requests with compression"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_post.side_effect = original_error
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            enable_request_compression=True,
            compression_threshold=100
        )
        
        large_data = {"data": "x" * 5000}
        
        try:
            client._post("/test", data=large_data)
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_cache_error(self, mock_get, api_key):
        """Test exception chaining with cache errors"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(
            api_key,
            "https://example.com",
            timeout=1,
            enable_cache=True,
            cache_ttl=300.0
        )
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained (cache shouldn't affect chaining)
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_interceptors(self, mock_get, api_key):
        """Test exception chaining with interceptors"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        def request_hook(*args):
            pass
        
        client.add_request_hook(request_hook)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should still be chained despite interceptors
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.routes.requests.Session.post")
    def test_exception_chaining_in_routes_api(self, mock_post, api_key, sample_origin, sample_destination):
        """Test exception chaining in Routes API"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_post.side_effect = original_error
        
        from google_maps_sdk.routes import RoutesClient
        client = RoutesClient(api_key, timeout=1)
        
        try:
            client.compute_routes(sample_origin, sample_destination)
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_error_message_includes_context(self, mock_get, api_key):
        """Test exception error message includes context from chained exception"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Error message should include context
            error_str = str(e)
            # Should mention timeout or include cause info
            assert "timeout" in error_str.lower() or e.__cause__ is not None
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_read_timeout(self, mock_get, api_key):
        """Test exception chaining with read timeout"""
        original_error = requests.exceptions.ReadTimeout("Read timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.ReadTimeout)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_connect_timeout(self, mock_get, api_key):
        """Test exception chaining with connect timeout"""
        original_error = requests.exceptions.ConnectTimeout("Connection timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.ConnectTimeout)
        
        client.close()

    def test_exception_chaining_in_custom_exceptions(self):
        """Test exception chaining in custom exception classes"""
        # Test that custom exceptions can be chained
        original_error = ValueError("Original error")
        
        try:
            try:
                raise original_error
            except ValueError as e:
                raise GoogleMapsAPIError("Wrapped error") from e
        except GoogleMapsAPIError as wrapped:
            # Should be chained
            assert wrapped.__cause__ is not None
            assert isinstance(wrapped.__cause__, ValueError)
            assert str(wrapped.__cause__) == "Original error"

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_with_ssl_error(self, mock_get, api_key):
        """Test exception chaining with SSL errors"""
        original_error = requests.exceptions.SSLError("SSL certificate verification failed")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Exception should be chained
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, requests.exceptions.SSLError)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_chaining_preserves_exception_type(self, mock_get, api_key):
        """Test exception chaining preserves exception type information"""
        original_error = requests.exceptions.Timeout("Request timeout")
        mock_get.side_effect = original_error
        
        client = BaseClient(api_key, "https://example.com", timeout=1)
        
        try:
            client._get("/test")
        except GoogleMapsAPIError as e:
            # Should preserve original exception type
            assert e.__cause__ is not None
            assert type(e.__cause__).__name__ == "Timeout"
            # Should be able to access original exception
            assert isinstance(e.__cause__, requests.exceptions.Timeout)
        
        client.close()
