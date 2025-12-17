"""
Roads API Client

Service for snapping GPS coordinates to roads and getting road metadata.
"""

from typing import Optional, List, Dict, Any, Tuple, Union, TYPE_CHECKING
from .base_client import BaseClient
from .retry import RetryConfig
from .types import SnapToRoadsResponse, NearestRoadsResponse, SpeedLimitsResponse
from .utils import validate_path_or_points, MAX_ROADS_POINTS

if TYPE_CHECKING:
    from requests.adapters import HTTPAdapter
    from .circuit_breaker import CircuitBreaker
    from .config import ClientConfig


class RoadsClient(BaseClient):
    """Client for Google Maps Roads API"""

    BASE_URL = "https://roads.googleapis.com"
    DEFAULT_API_VERSION = "v1"

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        timeout: int = 30,
        api_version: Optional[str] = None,
        rate_limit_max_calls: Optional[int] = None,
        rate_limit_period: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_cache: bool = False,
        cache_ttl: float = 300.0,
        cache_maxsize: int = 100,
        http_adapter: Optional['HTTPAdapter'] = None,
        circuit_breaker: Optional['CircuitBreaker'] = None,
        enable_request_compression: bool = False,
        compression_threshold: int = 1024,
        json_encoder: Optional[type] = None,
        config: Optional['ClientConfig'] = None,
    ):
        """
        Initialize Roads API client

        Args:
            api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var) (issue #31)
            timeout: Request timeout in seconds
            api_version: API version (e.g., "v1", "v2") (default: "v1") (issue #76)
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
            retry_config: Retry configuration (None to disable retries) (issue #11)
            enable_cache: Enable response caching (default: False) (issue #37)
            cache_ttl: Cache time-to-live in seconds (default: 300.0 = 5 minutes) (issue #37)
            cache_maxsize: Maximum number of cached responses (default: 100) (issue #37)
            http_adapter: Custom HTTPAdapter for proxies, custom SSL, etc. (None to use default) (issue #38)
            circuit_breaker: CircuitBreaker instance for failure protection (None to disable) (issue #39)
            enable_request_compression: Enable gzip compression for large POST requests (default: False) (issue #49)
            compression_threshold: Minimum payload size in bytes to compress (default: 1024) (issue #49)
            json_encoder: Custom JSON encoder class for encoding request data (None to use default) (issue #51)
            config: ClientConfig object to centralize configuration (issue #75). If provided, other parameters are ignored.
        """
        # If config object is provided, use it (issue #75, #76)
        if config is not None:
            api_key = config.api_key
            timeout = config.timeout
            api_version = config.api_version
            rate_limit_max_calls = config.rate_limit_max_calls
            rate_limit_period = config.rate_limit_period
            retry_config = config.retry_config
            enable_cache = config.enable_cache
            cache_ttl = config.cache_ttl
            cache_maxsize = config.cache_maxsize
            http_adapter = config.http_adapter
            circuit_breaker = config.circuit_breaker
            enable_request_compression = config.enable_request_compression
            compression_threshold = config.compression_threshold
            json_encoder = config.json_encoder
        
        # Validate and set API version (issue #76)
        from .utils import validate_api_version
        if api_version is None:
            api_version = self.DEFAULT_API_VERSION
        self._api_version = validate_api_version(api_version)
        
        # Construct base URL with version
        base_url_with_version = f"{self.BASE_URL}/{self._api_version}"
        
        super().__init__(
            api_key, 
            base_url_with_version, 
            timeout,
            rate_limit_max_calls=rate_limit_max_calls,
            rate_limit_period=rate_limit_period,
            retry_config=retry_config,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            cache_maxsize=cache_maxsize,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
            enable_request_compression=enable_request_compression,
            compression_threshold=compression_threshold,
            json_encoder=json_encoder,
        )

    def snap_to_roads(
        self,
        path: List[tuple],
        interpolate: bool = False,
    ) -> SnapToRoadsResponse:
        """
        Snap a GPS path to the most likely roads traveled

        Args:
            path: List of (latitude, longitude) tuples (max 100 points)
            interpolate: Whether to interpolate path to include all points forming full road geometry

        Returns:
            Response containing snapped points with place IDs

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> path = [(60.170880, 24.942795), (60.170879, 24.942796), (60.170877, 24.942796)]
            >>> result = client.snap_to_roads(path, interpolate=True)
        """
        # Validation (issues #20, #23)
        validate_path_or_points(path=path, points=None, max_points=MAX_ROADS_POINTS)

        # Format path as pipe-separated lat,lng pairs
        path_str = "|".join([f"{lat},{lng}" for lat, lng in path])

        params: Dict[str, Any] = {"path": path_str}

        if interpolate:
            params["interpolate"] = "true"

        return self._get("/snapToRoads", params=params)

    def nearest_roads(
        self,
        points: List[tuple],
    ) -> NearestRoadsResponse:
        """
        Find the nearest road segments for a set of GPS points

        Args:
            points: List of (latitude, longitude) tuples (max 100 points)
                   Points don't need to form a continuous path

        Returns:
            Response containing nearest road segments with place IDs

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> points = [(60.170880, 24.942795), (60.170879, 24.942796)]
            >>> result = client.nearest_roads(points)
        """
        # Validation (issues #20, #23)
        validate_path_or_points(path=None, points=points, max_points=MAX_ROADS_POINTS)

        # Format points as pipe-separated lat,lng pairs
        points_str = "|".join([f"{lat},{lng}" for lat, lng in points])

        params = {"points": points_str}

        return self._get("/nearestRoads", params=params)

    def speed_limits(
        self,
        path: Optional[List[tuple]] = None,
        place_ids: Optional[List[str]] = None,
    ) -> SpeedLimitsResponse:
        """
        Get posted speed limits for road segments

        Args:
            path: List of (latitude, longitude) tuples representing road path (max 100 points)
            place_ids: List of Place IDs representing road segments (max 100)

        Returns:
            Response containing speed limits for road segments

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> # Using path
            >>> path = [(60.170880, 24.942795), (60.170879, 24.942796)]
            >>> result = client.speed_limits(path=path)
            >>> # Using place IDs
            >>> place_ids = ["ChIJ685WIFYViEgRHlHvBbiD5nE", "ChIJA01I-8YVhkgRGJb0fW4UX7Y"]
            >>> result = client.speed_limits(place_ids=place_ids)
        """
        # Validation (issues #20, #23, #97)
        if path and place_ids:
            raise ValueError("Either path or place_ids must be provided, not both")

        if not path and not place_ids:
            raise ValueError("Either path or place_ids must be provided")

        params: Dict[str, Any] = {}

        if path:
            validate_path_or_points(path=path, points=None, max_points=MAX_ROADS_POINTS)
            path_str = "|".join([f"{lat},{lng}" for lat, lng in path])
            params["path"] = path_str

        if place_ids:
            if not isinstance(place_ids, list):
                raise TypeError("Place IDs must be a list")
            if len(place_ids) == 0:
                raise ValueError("Place IDs list cannot be empty")
            if len(place_ids) > MAX_ROADS_POINTS:
                raise ValueError(f"Maximum {MAX_ROADS_POINTS} place IDs allowed per request")
            params["placeId"] = ",".join(place_ids)

        return self._get("/speedLimits", params=params)

    def __repr__(self) -> str:
        """String representation of client (issue #52)"""
        return f"{self.__class__.__name__}(api_key='***', timeout={self.timeout})"

