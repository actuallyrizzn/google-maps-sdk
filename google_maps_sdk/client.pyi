"""
Type stubs for GoogleMapsClient (issue #46)
"""

from typing import Optional, Any
from .routes import RoutesClient
from .directions import DirectionsClient
from .roads import RoadsClient
from .retry import RetryConfig

class GoogleMapsClient:
    api_key: str
    timeout: int
    routes: RoutesClient
    directions: DirectionsClient
    roads: RoadsClient
    
    def __init__(
        self,
        api_key: Optional[str] = ...,
        timeout: int = ...,
        rate_limit_max_calls: Optional[int] = ...,
        rate_limit_period: Optional[float] = ...,
        retry_config: Optional[RetryConfig] = ...,
        enable_cache: bool = ...,
        cache_ttl: float = ...,
        cache_maxsize: int = ...,
        http_adapter: Optional[Any] = ...,
        circuit_breaker: Optional[Any] = ...,
    ) -> None: ...
    
    def set_api_key(self, api_key: str) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> "GoogleMapsClient": ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
    def __repr__(self) -> str: ...
