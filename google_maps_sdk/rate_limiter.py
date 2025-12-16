"""
Rate limiting functionality for API requests
"""

import time
import threading
from typing import Optional
from collections import defaultdict
from .exceptions import QuotaExceededError


class RateLimiter:
    """
    Thread-safe rate limiter using token bucket algorithm
    
    Limits the number of requests that can be made within a time period.
    """
    
    def __init__(self, max_calls: int = 100, period: float = 60.0):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds (default: 60 seconds)
            
        Raises:
            ValueError: If max_calls or period is invalid
        """
        if max_calls < 1:
            raise ValueError("max_calls must be at least 1")
        if period <= 0:
            raise ValueError("period must be positive")
        
        self.max_calls = max_calls
        self.period = period
        self._lock = threading.Lock()
        # Track calls per client instance (using object id as key)
        self._calls: dict[int, list[float]] = defaultdict(list)
    
    def acquire(self, client_id: Optional[int] = None) -> None:
        """
        Acquire permission to make a request
        
        Args:
            client_id: Optional client identifier (defaults to current thread)
            
        Raises:
            QuotaExceededError: If rate limit is exceeded
        """
        if client_id is None:
            # Use thread ID as default identifier
            client_id = id(threading.current_thread())
        
        now = time.time()
        
        with self._lock:
            # Clean up old calls outside the time window
            self._calls[client_id] = [
                call_time 
                for call_time in self._calls[client_id] 
                if now - call_time < self.period
            ]
            
            # Check if we've exceeded the limit
            if len(self._calls[client_id]) >= self.max_calls:
                # Calculate time until next call is allowed
                oldest_call = min(self._calls[client_id])
                wait_time = self.period - (now - oldest_call)
                raise QuotaExceededError(
                    f"Rate limit exceeded: {self.max_calls} calls per {self.period}s. "
                    f"Retry after {wait_time:.2f} seconds."
                )
            
            # Record this call
            self._calls[client_id].append(now)
    
    def reset(self, client_id: Optional[int] = None) -> None:
        """
        Reset rate limit for a specific client
        
        Args:
            client_id: Optional client identifier (defaults to current thread)
        """
        if client_id is None:
            client_id = id(threading.current_thread())
        
        with self._lock:
            if client_id in self._calls:
                del self._calls[client_id]
    
    def get_remaining_calls(self, client_id: Optional[int] = None) -> int:
        """
        Get remaining calls available in current period
        
        Args:
            client_id: Optional client identifier (defaults to current thread)
            
        Returns:
            Number of remaining calls
        """
        if client_id is None:
            client_id = id(threading.current_thread())
        
        now = time.time()
        
        with self._lock:
            # Clean up old calls
            self._calls[client_id] = [
                call_time 
                for call_time in self._calls[client_id] 
                if now - call_time < self.period
            ]
            
            return max(0, self.max_calls - len(self._calls[client_id]))
    
    def get_wait_time(self, client_id: Optional[int] = None) -> float:
        """
        Get time to wait before next call is allowed
        
        Args:
            client_id: Optional client identifier (defaults to current thread)
            
        Returns:
            Wait time in seconds (0 if no wait needed)
        """
        if client_id is None:
            client_id = id(threading.current_thread())
        
        now = time.time()
        
        with self._lock:
            if client_id not in self._calls or not self._calls[client_id]:
                return 0.0
            
            # Clean up old calls
            self._calls[client_id] = [
                call_time 
                for call_time in self._calls[client_id] 
                if now - call_time < self.period
            ]
            
            if len(self._calls[client_id]) < self.max_calls:
                return 0.0
            
            # Calculate wait time until oldest call expires
            oldest_call = min(self._calls[client_id])
            wait_time = self.period - (now - oldest_call)
            return max(0.0, wait_time)
