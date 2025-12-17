"""
Unit tests for circuit breaker pattern (issue #39)
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from google_maps_sdk.base_client import BaseClient


@pytest.mark.unit
class TestCircuitBreaker:
    """Test CircuitBreaker class"""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state allows requests"""
        breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)
        
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.get_state() == CircuitBreaker.CLOSED

    def test_circuit_breaker_failure_count(self):
        """Test circuit breaker tracks failures"""
        breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)
        
        def failing_func():
            raise ValueError("Test error")
        
        # First failure
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_failure_count() == 1
        assert breaker.get_state() == CircuitBreaker.CLOSED
        
        # Second failure
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_failure_count() == 2
        assert breaker.get_state() == CircuitBreaker.CLOSED
        
        # Third failure - should open
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        assert breaker.get_failure_count() == 3
        assert breaker.get_state() == CircuitBreaker.OPEN

    def test_circuit_breaker_open_blocks_requests(self):
        """Test circuit breaker in open state blocks requests"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Cause circuit to open
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        
        assert breaker.get_state() == CircuitBreaker.OPEN
        
        # Should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_func)

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker transitions to half-open and recovers"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        def failing_func():
            raise ValueError("Test error")
        
        def success_func():
            return "success"
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        
        assert breaker.get_state() == CircuitBreaker.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Should transition to half-open and succeed
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.get_state() == CircuitBreaker.CLOSED
        assert breaker.get_failure_count() == 0

    def test_circuit_breaker_reset(self):
        """Test manual reset of circuit breaker"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        
        assert breaker.get_state() == CircuitBreaker.OPEN
        
        # Reset
        breaker.reset()
        assert breaker.get_state() == CircuitBreaker.CLOSED
        assert breaker.get_failure_count() == 0

    def test_circuit_breaker_success_resets_failure_count(self):
        """Test that success resets failure count"""
        breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)
        
        def failing_func():
            raise ValueError("Test error")
        
        def success_func():
            return "success"
        
        # Two failures
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        with pytest.raises(ValueError):
            breaker.call(failing_func)
        
        assert breaker.get_failure_count() == 2
        
        # Success should reset
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.get_failure_count() == 0


@pytest.mark.unit
class TestBaseClientCircuitBreaker:
    """Test BaseClient circuit breaker integration"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_circuit_breaker_blocks_requests(self, mock_get, api_key):
        """Test circuit breaker blocks requests when open"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            circuit_breaker=breaker
        )
        
        # Cause failures to open circuit
        from google_maps_sdk.exceptions import GoogleMapsAPIError
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        with pytest.raises(GoogleMapsAPIError):
            client._get("/test")
        
        # Circuit should be open now
        assert breaker.get_state() == CircuitBreaker.OPEN
        
        # Next request should be blocked
        with pytest.raises(CircuitBreakerOpenError):
            client._get("/test")
        
        client.close()
