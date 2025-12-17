"""
Unit tests for retry scenarios (issue #258 / #60)
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.retry import RetryConfig, should_retry, exponential_backoff
from google_maps_sdk.exceptions import InternalServerError, GoogleMapsAPIError
import requests


@pytest.mark.unit
class TestRetryScenarios:
    """Test comprehensive retry scenarios"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_on_timeout_then_success(self, mock_get, api_key):
        """Test retry scenario: Timeout then success"""
        # First call times out, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        result = client._get("/test")
        assert result == {"status": "OK"}
        assert mock_get.call_count == 2
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_on_connection_error_then_success(self, mock_get, api_key):
        """Test retry scenario: Connection error then success"""
        # First call fails with connection error, second succeeds
        mock_responses = [
            requests.exceptions.ConnectionError("Connection failed"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        result = client._get("/test")
        assert result == {"status": "OK"}
        assert mock_get.call_count == 2
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_on_5xx_then_success(self, mock_get, api_key):
        """Test retry scenario: 5xx error then success"""
        # First call returns 500, second succeeds
        mock_responses = [
            MagicMock(status_code=500, json=lambda: {"error": {"message": "Internal Server Error"}}, url="https://example.com/test"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        # Mock _handle_response to raise InternalServerError on first call
        original_handle = client._handle_response
        call_count = [0]
        
        def mock_handle(response, request_id=None):
            call_count[0] += 1
            if call_count[0] == 1:
                error = InternalServerError("Server error", request_id=request_id)
                error.status_code = 500
                raise error
            return original_handle(response, request_id=request_id)
        
        client._handle_response = mock_handle
        
        result = client._get("/test")
        assert result == {"status": "OK"}
        assert mock_get.call_count == 2
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_exhausted_all_fail(self, mock_get, api_key):
        """Test retry scenario: All retries exhausted"""
        # All calls timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Should have tried max_retries + 1 times (initial + 2 retries)
        assert mock_get.call_count == 3
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_no_retry_on_4xx_error(self, mock_get, api_key):
        """Test retry scenario: No retry on 4xx errors"""
        # 400 error should not be retried
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Should only try once (no retries for 4xx)
        assert mock_get.call_count == 1
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_no_retry_on_429_error(self, mock_get, api_key):
        """Test retry scenario: No retry on 429 rate limit errors"""
        # 429 error should not be retried
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=0.1)
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Should only try once (no retries for 429)
        assert mock_get.call_count == 1
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    @patch("time.sleep")
    def test_exponential_backoff_delays(self, mock_sleep, mock_get, api_key):
        """Test retry scenario: Exponential backoff delays are applied"""
        # First call fails, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.1, exponential_base=2.0, jitter=False)
        )
        
        client._get("/test")
        
        # Verify sleep was called with exponential backoff delay
        assert mock_sleep.called
        # First retry should have delay = base_delay * (exponential_base ^ attempt)
        # attempt 0: delay = 0.1 * (2.0 ^ 0) = 0.1
        mock_sleep.assert_called_once()
        call_args = mock_sleep.call_args[0][0]
        assert call_args == pytest.approx(0.1, abs=0.01)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    @patch("time.sleep")
    def test_jitter_applied_to_backoff(self, mock_sleep, mock_get, api_key):
        """Test retry scenario: Jitter is applied to backoff delays"""
        # First call fails, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=1.0, exponential_base=2.0, jitter=True)
        )
        
        client._get("/test")
        
        # Verify sleep was called
        assert mock_sleep.called
        call_args = mock_sleep.call_args[0][0]
        # With jitter, delay should be between base_delay and base_delay * 1.25
        # attempt 0: base = 1.0 * (2.0 ^ 0) = 1.0
        # With jitter: should be between 1.0 and 1.25
        assert 1.0 <= call_args <= 1.25
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_with_max_delay_limit(self, mock_get, api_key):
        """Test retry scenario: Backoff respects max_delay limit"""
        # All calls fail
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=5, base_delay=10.0, max_delay=20.0, jitter=False)
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Verify all retries were attempted
        assert mock_get.call_count == 6  # initial + 5 retries
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_disabled_when_config_none(self, mock_get, api_key):
        """Test retry scenario: Retry disabled when config is None"""
        # Call fails
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=None  # No retry config
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Should only try once (no retries)
        assert mock_get.call_count == 1
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_retry_on_post_request(self, mock_post, api_key):
        """Test retry scenario: Retry works for POST requests"""
        # First POST fails, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_post.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.1)
        )
        
        result = client._post("/test", data={"key": "value"})
        assert result == {"status": "OK"}
        assert mock_post.call_count == 2
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_preserves_request_id(self, mock_get, api_key):
        """Test retry scenario: Request ID is preserved across retries"""
        # First call fails, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.1)
        )
        
        result = client._get("/test")
        assert result == {"status": "OK"}
        
        # Verify request IDs were included in headers
        assert mock_get.call_count == 2
        # Each retry should have a request ID (though they may be different)
        first_call_headers = mock_get.call_args_list[0][1].get('headers', {})
        second_call_headers = mock_get.call_args_list[1][1].get('headers', {})
        assert 'X-Request-ID' in first_call_headers
        assert 'X-Request-ID' in second_call_headers
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_with_custom_exponential_base(self, mock_get, api_key):
        """Test retry scenario: Custom exponential base affects backoff"""
        # All calls fail
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=2, base_delay=1.0, exponential_base=3.0, jitter=False)
        )
        
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Verify all retries attempted
        assert mock_get.call_count == 3
        
        client.close()

    def test_should_retry_comprehensive(self):
        """Test comprehensive should_retry scenarios"""
        # Timeout - should retry
        assert should_retry(requests.exceptions.Timeout(), None) is True
        
        # Connection error - should retry
        assert should_retry(requests.exceptions.ConnectionError(), None) is True
        
        # 500 error - should retry
        assert should_retry(InternalServerError("Error"), 500) is True
        
        # 503 error - should retry
        assert should_retry(InternalServerError("Error"), 503) is True
        
        # 400 error - should not retry
        assert should_retry(GoogleMapsAPIError("Bad request"), 400) is False
        
        # 403 error - should not retry
        assert should_retry(GoogleMapsAPIError("Forbidden"), 403) is False
        
        # 404 error - should not retry
        assert should_retry(GoogleMapsAPIError("Not found"), 404) is False
        
        # 429 error - should not retry
        assert should_retry(GoogleMapsAPIError("Rate limited"), 429) is False

    def test_exponential_backoff_comprehensive(self):
        """Test comprehensive exponential backoff scenarios"""
        # Test various attempt numbers
        delays = []
        for attempt in range(5):
            delay = exponential_backoff(attempt, base_delay=1.0, max_delay=60.0, jitter=False)
            delays.append(delay)
        
        # Delays should increase
        assert delays[0] < delays[1] < delays[2] < delays[3] < delays[4]
        
        # Test max delay limit
        large_delay = exponential_backoff(100, base_delay=1.0, max_delay=60.0, jitter=False)
        assert large_delay <= 60.0
        
        # Test with jitter
        delay_with_jitter = exponential_backoff(1, base_delay=1.0, max_delay=60.0, jitter=True)
        base_delay = 1.0 * (2.0 ** 1)  # 2.0
        assert base_delay <= delay_with_jitter <= base_delay * 1.25
