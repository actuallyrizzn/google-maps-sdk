"""
Main Google Maps Platform client

Unified client providing access to all Google Maps Platform APIs.
"""

from typing import Optional, TYPE_CHECKING
from .routes import RoutesClient
from .directions import DirectionsClient
from .roads import RoadsClient
from .retry import RetryConfig

if TYPE_CHECKING:
    from requests.adapters import HTTPAdapter
    from .circuit_breaker import CircuitBreaker


class GoogleMapsClient:
    """
    Unified client for Google Maps Platform APIs

    Provides access to Routes API, Directions API, and Roads API through
    a single client interface.
    """

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        timeout: int = 30,
        rate_limit_max_calls: Optional[int] = None,
        rate_limit_period: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_cache: bool = False,
        cache_ttl: float = 300.0,
        cache_maxsize: int = 100,
        http_adapter: Optional['HTTPAdapter'] = None,
        circuit_breaker: Optional['CircuitBreaker'] = None,
    ):
        """
        Initialize Google Maps Platform client

        Args:
            api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var) (issue #31)
            timeout: Request timeout in seconds for all API calls
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
            retry_config: Retry configuration (None to disable retries) (issue #11)
            enable_cache: Enable response caching (default: False) (issue #37)
            cache_ttl: Cache time-to-live in seconds (default: 300.0 = 5 minutes) (issue #37)
            cache_maxsize: Maximum number of cached responses (default: 100) (issue #37)
            http_adapter: Custom HTTPAdapter for proxies, custom SSL, etc. (None to use default) (issue #38)
            circuit_breaker: CircuitBreaker instance for failure protection (None to disable) (issue #39)

        Example:
            >>> client = GoogleMapsClient(api_key="YOUR_API_KEY")
            >>> # Or use environment variable:
            >>> # export GOOGLE_MAPS_API_KEY=your_key
            >>> client = GoogleMapsClient()
            >>> routes = client.routes.compute_routes(origin, destination)
        """
        # Get API key from parameter or environment variable (issue #31)
        if api_key is None:
            import os
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key is required. Provide as parameter or set GOOGLE_MAPS_API_KEY environment variable"
                )
        
        self.api_key = api_key
        self.timeout = timeout

        # Initialize sub-clients with rate limiting, retry, cache, custom adapter, and circuit breaker
        self.routes = RoutesClient(
            api_key, 
            timeout,
            rate_limit_max_calls=rate_limit_max_calls,
            rate_limit_period=rate_limit_period,
            retry_config=retry_config,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            cache_maxsize=cache_maxsize,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
        )
        self.directions = DirectionsClient(
            api_key, 
            timeout,
            rate_limit_max_calls=rate_limit_max_calls,
            rate_limit_period=rate_limit_period,
            retry_config=retry_config,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            cache_maxsize=cache_maxsize,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
        )
        self.roads = RoadsClient(
            api_key, 
            timeout,
            rate_limit_max_calls=rate_limit_max_calls,
            rate_limit_period=rate_limit_period,
            retry_config=retry_config,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            cache_maxsize=cache_maxsize,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
        )

    def set_api_key(self, api_key: str) -> None:
        """
        Update API key for all sub-clients (useful for key rotation) (issue #33)
        
        Args:
            api_key: New API key
            
        Raises:
            TypeError: If api_key is not a string
            ValueError: If api_key is invalid
        """
        from .utils import validate_api_key
        self.api_key = validate_api_key(api_key)
        self.routes.set_api_key(api_key)
        self.directions.set_api_key(api_key)
        self.roads.set_api_key(api_key)

    def close(self):
        """
        Close all HTTP sessions (idempotent) (issue #17)
        
        Can be called multiple times safely. If sessions are already closed,
        this method does nothing.
        """
        # Close each sub-client, ignoring errors
        for client in [self.routes, self.directions, self.roads]:
            try:
                if hasattr(client, 'close'):
                    client.close()
            except Exception:
                # Ignore errors during cleanup
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager, ensuring all sessions are closed even if exceptions occur (issue #17)
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        try:
            self.close()
        except Exception:
            # Ignore errors during cleanup to prevent masking original exception
            pass

    def __repr__(self) -> str:
        """String representation of client (issue #52)"""
        return f"{self.__class__.__name__}(api_key='***', timeout={self.timeout})"

