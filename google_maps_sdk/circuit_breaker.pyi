"""
Type stubs for circuit_breaker module (issue #46)
"""

from typing import Optional, Callable, Any, Type
from .exceptions import GoogleMapsAPIError

class CircuitBreaker:
    CLOSED: str
    OPEN: str
    HALF_OPEN: str
    
    failure_threshold: int
    timeout: float
    expected_exception: Type[Exception]
    state: str
    failure_count: int
    
    def __init__(
        self,
        failure_threshold: int = ...,
        timeout: float = ...,
        expected_exception: Type[Exception] = ...,
    ) -> None: ...
    
    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any: ...
    def reset(self) -> None: ...
    def get_state(self) -> str: ...
    def get_failure_count(self) -> int: ...

class CircuitBreakerOpenError(GoogleMapsAPIError):
    def __init__(self, message: str) -> None: ...
