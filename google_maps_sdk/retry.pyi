"""
Type stubs for retry module (issue #46)
"""

from typing import Optional, Callable, Type

class RetryConfig:
    max_retries: int
    base_delay: float
    max_delay: float
    exponential_base: float
    jitter: bool
    
    def __init__(
        self,
        max_retries: int = ...,
        base_delay: float = ...,
        max_delay: float = ...,
        exponential_base: float = ...,
        jitter: bool = ...,
    ) -> None: ...

def should_retry(exception: Exception, status_code: Optional[int] = ...) -> bool: ...
def exponential_backoff(
    attempt: int,
    base_delay: float = ...,
    max_delay: float = ...,
    exponential_base: float = ...,
    jitter: bool = ...,
) -> float: ...
