"""
Circuit breaker pattern implementation (issue #39)
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from .exceptions import GoogleMapsAPIError


class CircuitBreaker:
    """
    Circuit breaker to prevent requests during outages (issue #39)
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered, allows one request
    """
    
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit (default: 5)
            timeout: Time in seconds to wait before attempting half-open (default: 60.0)
            expected_exception: Exception type that counts as failure (default: Exception)
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by func
        """
        with self._lock:
            # Check if circuit should transition from OPEN to HALF_OPEN
            if self.state == self.OPEN:
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.timeout:
                        self.state = self.HALF_OPEN
                        self.failure_count = 0
                    else:
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker is OPEN. Wait {self.timeout - elapsed:.1f}s before retry"
                        )
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        # Try to execute function
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit breaker if in HALF_OPEN
            with self._lock:
                if self.state == self.HALF_OPEN:
                    self.state = self.CLOSED
                    self.failure_count = 0
                    self.last_failure_time = None
                elif self.state == self.CLOSED:
                    # Reset failure count on success
                    self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            # Failure - increment failure count
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = self.OPEN
                
                # If in HALF_OPEN and failure, go back to OPEN
                if self.state == self.HALF_OPEN:
                    self.state = self.OPEN
            
            raise
    
    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state"""
        with self._lock:
            self.state = self.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
    
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        with self._lock:
            return self.state
    
    def get_failure_count(self) -> int:
        """Get current failure count"""
        with self._lock:
            return self.failure_count


class CircuitBreakerOpenError(GoogleMapsAPIError):
    """Raised when circuit breaker is open and request is blocked"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=503)
