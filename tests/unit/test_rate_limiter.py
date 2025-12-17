"""
Unit tests for rate limiter
"""

import pytest
import time
import threading
from google_maps_sdk.rate_limiter import RateLimiter
from google_maps_sdk.exceptions import QuotaExceededError


@pytest.mark.unit
class TestRateLimiterInit:
    """Test RateLimiter initialization"""

    def test_init_default(self):
        """Test initialization with default values"""
        limiter = RateLimiter()
        assert limiter.max_calls == 100
        assert limiter.period == 60.0

    def test_init_custom(self):
        """Test initialization with custom values"""
        limiter = RateLimiter(max_calls=50, period=30.0)
        assert limiter.max_calls == 50
        assert limiter.period == 30.0

    def test_init_invalid_max_calls(self):
        """Test initialization with invalid max_calls"""
        with pytest.raises(ValueError, match="max_calls must be at least 1"):
            RateLimiter(max_calls=0)
        
        with pytest.raises(ValueError, match="max_calls must be at least 1"):
            RateLimiter(max_calls=-1)

    def test_init_invalid_period(self):
        """Test initialization with invalid period"""
        with pytest.raises(ValueError, match="period must be positive"):
            RateLimiter(period=0)
        
        with pytest.raises(ValueError, match="period must be positive"):
            RateLimiter(period=-1)


@pytest.mark.unit
class TestRateLimiterAcquire:
    """Test RateLimiter.acquire method"""

    def test_acquire_single_call(self):
        """Test single call is allowed"""
        limiter = RateLimiter(max_calls=1, period=1.0)
        limiter.acquire()
        # Should not raise

    def test_acquire_multiple_calls_within_limit(self):
        """Test multiple calls within limit"""
        limiter = RateLimiter(max_calls=5, period=1.0)
        for _ in range(5):
            limiter.acquire()
        # Should not raise

    def test_acquire_exceeds_limit(self):
        """Test that exceeding limit raises QuotaExceededError"""
        limiter = RateLimiter(max_calls=2, period=1.0)
        limiter.acquire()
        limiter.acquire()
        
        with pytest.raises(QuotaExceededError) as exc_info:
            limiter.acquire()
        
        assert "Rate limit exceeded" in str(exc_info.value)
        assert "2 calls per 1.0s" in str(exc_info.value)

    def test_acquire_resets_after_period(self):
        """Test that calls reset after period expires"""
        limiter = RateLimiter(max_calls=1, period=0.1)
        limiter.acquire()
        
        # Should fail immediately
        with pytest.raises(QuotaExceededError):
            limiter.acquire()
        
        # Wait for period to expire
        time.sleep(0.15)
        
        # Should now succeed
        limiter.acquire()
        # Should not raise

    def test_acquire_with_client_id(self):
        """Test acquire with specific client ID"""
        limiter = RateLimiter(max_calls=1, period=1.0)
        client_id_1 = 123
        client_id_2 = 456
        
        limiter.acquire(client_id_1)
        limiter.acquire(client_id_2)  # Different client, should succeed
        
        # Same client should fail
        with pytest.raises(QuotaExceededError):
            limiter.acquire(client_id_1)


@pytest.mark.unit
class TestRateLimiterThreadSafety:
    """Test RateLimiter thread safety"""

    def test_concurrent_acquire(self):
        """Test concurrent acquire calls are thread-safe"""
        limiter = RateLimiter(max_calls=10, period=1.0)
        errors = []
        shared_client_id = 999  # Use same client ID for all threads
        
        def make_call():
            try:
                limiter.acquire(shared_client_id)
            except QuotaExceededError as e:
                errors.append(e)
        
        threads = [threading.Thread(target=make_call) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All 10 calls should succeed
        assert len(errors) == 0
        
        # 11th call should fail
        with pytest.raises(QuotaExceededError):
            limiter.acquire(shared_client_id)


@pytest.mark.unit
class TestRateLimiterReset:
    """Test RateLimiter.reset method"""

    def test_reset_clears_calls(self):
        """Test reset clears call history"""
        limiter = RateLimiter(max_calls=1, period=1.0)
        client_id = 123
        
        limiter.acquire(client_id)
        
        # Should fail
        with pytest.raises(QuotaExceededError):
            limiter.acquire(client_id)
        
        # Reset
        limiter.reset(client_id)
        
        # Should now succeed
        limiter.acquire(client_id)


@pytest.mark.unit
class TestRateLimiterRemainingCalls:
    """Test RateLimiter.get_remaining_calls method"""

    def test_remaining_calls_initial(self):
        """Test remaining calls when none used"""
        limiter = RateLimiter(max_calls=5, period=1.0)
        assert limiter.get_remaining_calls() == 5

    def test_remaining_calls_after_use(self):
        """Test remaining calls after some calls"""
        limiter = RateLimiter(max_calls=5, period=1.0)
        limiter.acquire()
        limiter.acquire()
        assert limiter.get_remaining_calls() == 3

    def test_remaining_calls_exhausted(self):
        """Test remaining calls when limit reached"""
        limiter = RateLimiter(max_calls=2, period=1.0)
        limiter.acquire()
        limiter.acquire()
        assert limiter.get_remaining_calls() == 0

    def test_remaining_calls_resets_after_period(self):
        """Test remaining calls reset after period"""
        limiter = RateLimiter(max_calls=1, period=0.1)
        limiter.acquire()
        assert limiter.get_remaining_calls() == 0
        
        time.sleep(0.15)
        assert limiter.get_remaining_calls() == 1


@pytest.mark.unit
class TestRateLimiterWaitTime:
    """Test RateLimiter.get_wait_time method"""

    def test_wait_time_no_wait(self):
        """Test wait time when no wait needed"""
        limiter = RateLimiter(max_calls=5, period=1.0)
        limiter.acquire()
        assert limiter.get_wait_time() == 0.0

    def test_wait_time_when_limit_reached(self):
        """Test wait time when limit is reached"""
        limiter = RateLimiter(max_calls=1, period=0.5)
        limiter.acquire()
        
        wait_time = limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 0.5

    def test_wait_time_resets_after_period(self):
        """Test wait time resets after period"""
        limiter = RateLimiter(max_calls=1, period=0.1)
        limiter.acquire()
        
        time.sleep(0.15)
        assert limiter.get_wait_time() == 0.0
