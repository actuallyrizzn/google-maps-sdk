"""
Unit tests for retry logic (issue #11)
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.retry import (
    RetryConfig,
    should_retry,
    exponential_backoff,
    retry_with_backoff,
)
from google_maps_sdk.exceptions import InternalServerError, GoogleMapsAPIError
import requests


@pytest.mark.unit
class TestRetryConfig:
    """Test RetryConfig class"""

    def test_init_default(self):
        """Test initialization with default values"""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_init_custom(self):
        """Test initialization with custom values"""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False

    def test_init_invalid(self):
        """Test initialization with invalid values"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            RetryConfig(max_retries=-1)
        
        with pytest.raises(ValueError, match="base_delay must be positive"):
            RetryConfig(base_delay=0)
        
        with pytest.raises(ValueError, match="max_delay must be positive"):
            RetryConfig(max_delay=0)
        
        with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
            RetryConfig(base_delay=10, max_delay=5)


@pytest.mark.unit
class TestShouldRetry:
    """Test should_retry function"""

    def test_retry_on_timeout(self):
        """Test retry on timeout"""
        assert should_retry(requests.exceptions.Timeout(), None) is True

    def test_retry_on_connection_error(self):
        """Test retry on connection error"""
        assert should_retry(requests.exceptions.ConnectionError(), None) is True

    def test_retry_on_5xx_error(self):
        """Test retry on 5xx server errors"""
        error = InternalServerError("Server error")
        assert should_retry(error, 500) is True
        assert should_retry(error, 503) is True

    def test_no_retry_on_429(self):
        """Test no retry on 429 (rate limit)"""
        error = GoogleMapsAPIError("Rate limited", status_code=429)
        assert should_retry(error, 429) is False

    def test_no_retry_on_4xx(self):
        """Test no retry on 4xx client errors"""
        error = GoogleMapsAPIError("Bad request", status_code=400)
        assert should_retry(error, 400) is False


@pytest.mark.unit
class TestExponentialBackoff:
    """Test exponential_backoff function"""

    def test_backoff_increases(self):
        """Test backoff increases with attempts"""
        delay1 = exponential_backoff(0, base_delay=1.0, max_delay=60.0, jitter=False)
        delay2 = exponential_backoff(1, base_delay=1.0, max_delay=60.0, jitter=False)
        delay3 = exponential_backoff(2, base_delay=1.0, max_delay=60.0, jitter=False)
        
        assert delay1 < delay2 < delay3

    def test_backoff_respects_max(self):
        """Test backoff respects max delay"""
        delay = exponential_backoff(10, base_delay=1.0, max_delay=60.0, jitter=False)
        assert delay <= 60.0

    def test_backoff_with_jitter(self):
        """Test backoff includes jitter"""
        delay1 = exponential_backoff(1, base_delay=1.0, max_delay=60.0, jitter=True)
        delay2 = exponential_backoff(1, base_delay=1.0, max_delay=60.0, jitter=True)
        
        # With jitter, delays should vary (very unlikely to be exactly the same)
        # But both should be within reasonable bounds
        base_delay_no_jitter = 1.0 * (2.0 ** 1)  # 2.0
        assert 2.0 <= delay1 <= 2.5  # 2.0 + 25% jitter
        assert 2.0 <= delay2 <= 2.5


@pytest.mark.unit
class TestRetryWithBackoff:
    """Test retry_with_backoff decorator"""

    def test_no_retry_on_success(self):
        """Test no retry when function succeeds"""
        @retry_with_backoff(max_retries=3)
        def success_func():
            return "success"
        
        assert success_func() == "success"

    def test_retry_on_transient_error(self):
        """Test retry on transient error"""
        call_count = [0]
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        def transient_error_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise requests.exceptions.Timeout("Timeout")
            return "success"
        
        assert transient_error_func() == "success"
        assert call_count[0] == 2

    def test_fails_after_max_retries(self):
        """Test function fails after max retries"""
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        def always_fails():
            raise requests.exceptions.Timeout("Timeout")
        
        with pytest.raises(requests.exceptions.Timeout):
            always_fails()

    def test_no_retry_on_non_retryable_error(self):
        """Test no retry on non-retryable error"""
        call_count = [0]
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def non_retryable_error():
            call_count[0] += 1
            raise ValueError("Not retryable")
        
        with pytest.raises(ValueError):
            non_retryable_error()
        
        # Should only be called once (no retries)
        assert call_count[0] == 1
