"""
Type stubs for rate_limiter module (issue #46)
"""

from typing import Optional

class RateLimiter:
    max_calls: int
    period: float
    
    def __init__(self, max_calls: int = ..., period: float = ...) -> None: ...
    def acquire(self, client_id: int) -> None: ...
    def reset(self) -> None: ...
