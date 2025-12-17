"""
Type stubs for DirectionsClient (issue #46)
"""

from typing import Optional, List, Union, Any
from .base_client import BaseClient
from .retry import RetryConfig
from .types import DirectionsResponse

class DirectionsClient(BaseClient):
    BASE_URL: str
    
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
    
    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = ...,
        waypoints: Optional[List[str]] = ...,
        alternatives: bool = ...,
        avoid: Optional[List[str]] = ...,
        language: Optional[str] = ...,
        units: Optional[str] = ...,
        region: Optional[str] = ...,
        departure_time: Optional[Union[str, int]] = ...,
        arrival_time: Optional[int] = ...,
        traffic_model: Optional[str] = ...,
        transit_mode: Optional[List[str]] = ...,
        transit_routing_preference: Optional[str] = ...,
        output_format: str = ...,
    ) -> DirectionsResponse: ...
