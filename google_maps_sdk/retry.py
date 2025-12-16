"""
Retry logic with exponential backoff for transient failures
"""

import time
import random
from typing import Callable, Type, Tuple, Optional, Union
from functools import wraps
import requests
from .exceptions import GoogleMapsAPIError, InternalServerError


def should_retry(exception: Exception, status_code: Optional[int] = None) -> bool:
    """
    Determine if an exception should trigger a retry
    
    Args:
        exception: The exception that occurred
        status_code: Optional HTTP status code
        
    Returns:
        True if the exception should trigger a retry
    """
    # Retry on network errors
    if isinstance(exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    
    # Retry on 5xx server errors (but not 429 - that's handled by rate limiter)
    if status_code is not None:
        if 500 <= status_code < 600 and status_code != 429:
            return True
    
    # Retry on InternalServerError
    if isinstance(exception, InternalServerError):
        return True
    
    return False


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    # Calculate exponential delay: base_delay * (exponential_base ^ attempt)
    delay = base_delay * (exponential_base ** attempt)
    
    # Cap at max_delay
    delay = min(delay, max_delay)
    
    # Add jitter to prevent thundering herd
    if jitter:
        # Add random jitter up to 25% of delay
        jitter_amount = delay * 0.25 * random.random()
        delay += jitter_amount
    
    return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        jitter: Whether to add random jitter (default: True)
        retryable_exceptions: Tuple of exception types that should trigger retry
        
    Returns:
        Decorator function
    """
    if retryable_exceptions is None:
        retryable_exceptions = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            InternalServerError,
        )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            status_code = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    # Extract status code if available
                    if hasattr(e, 'status_code'):
                        status_code = e.status_code
                    elif isinstance(e, GoogleMapsAPIError):
                        status_code = e.status_code
                    
                    # Check if we should retry
                    if not should_retry(e, status_code):
                        raise
                    
                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        raise
                    
                    # Calculate backoff delay
                    delay = exponential_backoff(
                        attempt,
                        base_delay=base_delay,
                        max_delay=max_delay,
                        exponential_base=exponential_base,
                        jitter=jitter
                    )
                    
                    # Wait before retrying
                    time.sleep(delay)
                    
                except Exception as e:
                    # Non-retryable exception - raise immediately
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Whether to add random jitter
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if base_delay <= 0:
            raise ValueError("base_delay must be positive")
        if max_delay <= 0:
            raise ValueError("max_delay must be positive")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")
        
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
