"""
Type stubs for RoutesClient (issue #46)
"""

from typing import Optional, Dict, Any, List
from .base_client import BaseClient
from .retry import RetryConfig
from .types import RouteResponse, RouteMatrixResponse

class RoutesClient(BaseClient):
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
    
    def compute_routes(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        intermediates: Optional[List[Dict[str, Any]]] = ...,
        travel_mode: str = ...,
        routing_preference: Optional[str] = ...,
        departure_time: Optional[str] = ...,
        compute_alternative_routes: bool = ...,
        route_modifiers: Optional[Dict[str, Any]] = ...,
        language_code: Optional[str] = ...,
        units: Optional[str] = ...,
        optimize_waypoint_order: bool = ...,
        polyline_quality: Optional[str] = ...,
        polyline_encoding: Optional[str] = ...,
        extra_computations: Optional[List[str]] = ...,
        field_mask: Optional[str] = ...,
    ) -> RouteResponse: ...
    
    def compute_route_matrix(
        self,
        origins: List[Dict[str, Any]],
        destinations: List[Dict[str, Any]],
        travel_mode: str = ...,
        routing_preference: Optional[str] = ...,
        departure_time: Optional[str] = ...,
    ) -> RouteMatrixResponse: ...
