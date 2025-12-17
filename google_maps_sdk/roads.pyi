"""
Type stubs for RoadsClient (issue #46)
"""

from typing import Optional, List, Tuple, Any
from .base_client import BaseClient
from .retry import RetryConfig
from .types import SnapToRoadsResponse, NearestRoadsResponse, SpeedLimitsResponse

class RoadsClient(BaseClient):
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
    
    def snap_to_roads(
        self,
        path: List[Tuple[float, float]],
        interpolate: bool = ...,
    ) -> SnapToRoadsResponse: ...
    
    def nearest_roads(
        self,
        points: List[Tuple[float, float]],
    ) -> NearestRoadsResponse: ...
    
    def speed_limits(
        self,
        place_ids: List[str],
    ) -> SpeedLimitsResponse: ...
