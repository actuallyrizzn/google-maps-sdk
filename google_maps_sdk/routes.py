"""
Routes API Client

Modern routing API with traffic-aware routing capabilities.
"""

from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
import requests
from .base_client import BaseClient
from .retry import RetryConfig
from .types import RouteResponse, RouteMatrixResponse

if TYPE_CHECKING:
    from requests.adapters import HTTPAdapter
    from .circuit_breaker import CircuitBreaker
    from .config import ClientConfig

from .utils import (
    validate_waypoint_count,
    validate_route_matrix_size,
    validate_enum_value,
    validate_language_code,
    validate_units,
    validate_departure_time,
    validate_field_mask,
    VALID_TRAVEL_MODES,
    VALID_ROUTING_PREFERENCES,
    VALID_POLYLINE_QUALITY,
    VALID_POLYLINE_ENCODING,
)


class RoutesClient(BaseClient):
    """Client for Google Maps Routes API"""

    BASE_URL = "https://routes.googleapis.com"
    DEFAULT_API_VERSION = "v2"

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
        Initialize Routes API client

        Args:
            api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var) (issue #31)
            timeout: Request timeout in seconds
            api_version: API version (e.g., "v2", "v3") (default: "v2") (issue #76)
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
        
        super().__init__(
            api_key, 
            self.BASE_URL, 
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

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request using header-based authentication (issue #1)
        
        Routes API uses X-Goog-Api-Key header instead of query parameter
        for enhanced security per Google's recommendations.

        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Request headers
            params: Query parameters (API key will NOT be added here)
            timeout: Optional timeout override

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        # Routes API uses header-based auth, not query param (issue #1)
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        # Add API key to headers instead of params
        headers["X-Goog-Api-Key"] = self._api_key
        
        # Use provided timeout or default
        request_timeout = timeout if timeout is not None else self.timeout
        
        # Generate request ID for tracking (issue #28)
        import uuid
        request_id = str(uuid.uuid4())
        
        # Check cache first (issue #37)
        if self._cache is not None:
            from .cache import generate_cache_key
            cache_key = generate_cache_key("POST", url, params, data)
            cached_response = self._cache.get(cache_key)
            if cached_response is not None:
                self._logger.debug(f"Cache hit [ID: {request_id}]: {url}")
                return cached_response
        
        # Define the actual request function for circuit breaker (issue #39)
        def _make_request():
            nonlocal request_id
            # Log request (issue #26, #28)
            self._logger.debug(f"POST request [ID: {request_id}]: {url} with data keys: {list(data.keys()) if data else 'None'}")
            
            # Call request hooks (issue #35)
            headers_with_id = headers.copy() if headers else {}
            headers_with_id['X-Request-ID'] = request_id
            for hook in self._request_hooks:
                try:
                    hook("POST", url, headers_with_id, params, data)
                except Exception as e:
                    self._logger.warning(f"Request hook raised exception: {e}", exc_info=True)
            
            # Retry logic (issue #11) - RoutesClient has its own _post, so we need retry here too
            from .retry import should_retry, exponential_backoff
            import time
            from .exceptions import GoogleMapsAPIError
            from .utils import sanitize_api_key_for_logging
            
            last_exception = None
            last_request_id = request_id
            max_retries = self._retry_config.max_retries if self._retry_config else 0
            
            for attempt in range(max_retries + 1):
                # Generate new request ID for retries
                if attempt > 0:
                    request_id = str(uuid.uuid4())
                    last_request_id = request_id
                    self._logger.info(f"Retry attempt {attempt}/{max_retries} for POST {url} [ID: {request_id}]")
                    # Update headers with new request ID
                    headers_with_id = headers.copy() if headers else {}
                    headers_with_id['X-Request-ID'] = request_id
                    # Call request hooks for retry (issue #35)
                    for hook in self._request_hooks:
                        try:
                            hook("POST", url, headers_with_id, params, data)
                        except Exception as e:
                            self._logger.warning(f"Request hook raised exception: {e}", exc_info=True)
                
                try:
                    # Request compression for large payloads (issue #49)
                    post_data = data
                    post_headers = headers_with_id.copy()
                    use_json_param = True
                    
                    if self._enable_request_compression and data:
                        import json
                        import gzip
                        # Use custom JSON encoder if provided (issue #51)
                        if self._json_encoder:
                            data_json = json.dumps(data, cls=self._json_encoder)
                        else:
                            data_json = json.dumps(data)
                        data_bytes = data_json.encode('utf-8')
                        
                        if len(data_bytes) >= self._compression_threshold:
                            # Compress the data
                            compressed_data = gzip.compress(data_bytes)
                            post_data = compressed_data
                            post_headers['Content-Encoding'] = 'gzip'
                            post_headers['Content-Type'] = 'application/json'
                            use_json_param = False
                            self._logger.debug(f"Compressed request body: {len(data_bytes)} -> {len(compressed_data)} bytes [ID: {request_id}]")
                    
                    if use_json_param:
                        # Use custom JSON encoder if provided (issue #51)
                        if self._json_encoder:
                            # When using custom encoder, we need to manually encode
                            data_json = json.dumps(post_data, cls=self._json_encoder)
                            post_headers['Content-Type'] = 'application/json'
                            response = self.session.post(
                                url, data=data_json.encode('utf-8'), headers=post_headers, params=params, timeout=request_timeout
                            )
                        else:
                            response = self.session.post(
                                url, json=post_data, headers=post_headers, params=params, timeout=request_timeout
                            )
                    else:
                        response = self.session.post(
                            url, data=post_data, headers=post_headers, params=params, timeout=request_timeout
                        )
                    
                    # Call response hooks (issue #35)
                    for hook in self._response_hooks:
                        try:
                            hook(response)
                        except Exception as e:
                            self._logger.warning(f"Response hook raised exception: {e}", exc_info=True)
                    
                    # Log response (issue #26, #28)
                    self._logger.debug(f"POST response [ID: {request_id}]: {url} - Status: {response.status_code}")
                    
                    result = self._handle_response(response, request_id=request_id)
                    
                    # Cache successful response (issue #37)
                    if self._cache is not None and attempt == 0:  # Only cache on first successful attempt
                        from .cache import generate_cache_key
                        cache_key = generate_cache_key("POST", url, params, data)
                        self._cache[cache_key] = result
                        self._logger.debug(f"Cached response [ID: {request_id}]: {url}")
                    
                    return result
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    last_exception = e
                    
                    # Log error with request ID (issue #26, #28)
                    self._logger.warning(f"POST request failed [ID: {request_id}] (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {sanitize_api_key_for_logging(str(e), self._api_key)}")
                    
                    if self._retry_config and should_retry(e, None):
                        if attempt >= max_retries:
                            break
                        
                        delay = exponential_backoff(
                            attempt,
                            base_delay=self._retry_config.base_delay,
                            max_delay=self._retry_config.max_delay,
                            exponential_base=self._retry_config.exponential_base,
                            jitter=self._retry_config.jitter
                        )
                        self._logger.debug(f"Waiting {delay:.2f}s before retry [ID: {request_id}]")
                        time.sleep(delay)
                        continue
                    else:
                        break
                except GoogleMapsAPIError as e:
                    last_exception = e
                    
                    # Store request ID in exception (issue #28)
                    if not hasattr(e, 'request_id'):
                        e.request_id = request_id
                    
                    # Log error with request ID (issue #26, #28)
                    self._logger.warning(f"POST request failed [ID: {request_id}] (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {sanitize_api_key_for_logging(str(e), self._api_key)}")
                    
                    if self._retry_config and should_retry(e, e.status_code):
                        if attempt >= max_retries:
                            break
                        
                        delay = exponential_backoff(
                            attempt,
                            base_delay=self._retry_config.base_delay,
                            max_delay=self._retry_config.max_delay,
                            exponential_base=self._retry_config.exponential_base,
                            jitter=self._retry_config.jitter
                        )
                        self._logger.debug(f"Waiting {delay:.2f}s before retry [ID: {request_id}]")
                        time.sleep(delay)
                        continue
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
                    self._logger.error(f"POST request failed [ID: {request_id}]: {error_msg}", exc_info=True)
                    error = GoogleMapsAPIError(f"Request failed: {error_msg}", request_url=url)
                    error.request_id = request_id
                    raise error from e
            
            if last_exception:
                error_msg = sanitize_api_key_for_logging(str(last_exception), self._api_key)
                self._logger.error(f"POST request failed after {max_retries + 1} attempts [ID: {last_request_id}]: {error_msg}", exc_info=True)
                if isinstance(last_exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                    error_msg = sanitize_api_key_for_logging(str(last_exception), self._api_key)
                    error = GoogleMapsAPIError(f"Request failed after {max_retries + 1} attempts: {error_msg}", request_url=url)
                    error.request_id = last_request_id
                    raise error from last_exception
                else:
                    if isinstance(last_exception, GoogleMapsAPIError) and not hasattr(last_exception, 'request_id'):
                        last_exception.request_id = last_request_id
                    raise last_exception
            
            self._logger.error(f"POST request failed: Unknown error [ID: {request_id}]")
            error = GoogleMapsAPIError("Request failed: Unknown error", request_url=url)
            error.request_id = request_id
            raise error
        
        # Execute request with circuit breaker protection (issue #39)
        if self._circuit_breaker is not None:
            return self._circuit_breaker.call(_make_request)
        else:
            return _make_request()

    def compute_routes(
        self,
        origin: Dict[str, Any],
        destination: Dict[str, Any],
        intermediates: Optional[List[Dict[str, Any]]] = None,
        travel_mode: str = "DRIVE",
        routing_preference: Optional[str] = None,
        departure_time: Optional[str] = None,
        compute_alternative_routes: bool = False,
        route_modifiers: Optional[Dict[str, Any]] = None,
        language_code: Optional[str] = None,
        units: Optional[str] = None,
        optimize_waypoint_order: bool = False,
        polyline_quality: Optional[str] = None,
        polyline_encoding: Optional[str] = None,
        extra_computations: Optional[List[str]] = None,
        field_mask: Optional[str] = None,
    ) -> RouteResponse:
        """
        Calculate a route between an origin and destination

        Args:
            origin: Origin waypoint (location with latLng, placeId, or address)
            destination: Destination waypoint
            intermediates: Optional list of intermediate waypoints
            travel_mode: Travel mode (DRIVE, WALK, BICYCLE, TRANSIT)
            routing_preference: Routing preference (TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL)
            departure_time: Departure time (ISO 8601 format or "now")
            compute_alternative_routes: Whether to compute alternative routes
            route_modifiers: Route modifiers (avoidTolls, avoidHighways, avoidFerries)
            language_code: Language code for response (e.g., "en-US")
            units: Unit system (IMPERIAL, METRIC)
            optimize_waypoint_order: Whether to optimize waypoint order
            polyline_quality: Polyline quality (HIGH_QUALITY, OVERVIEW)
            polyline_encoding: Polyline encoding (ENCODED_POLYLINE, GEO_JSON_LINESTRING)
            extra_computations: Extra computations (TOLLS, FUEL_CONSUMPTION, etc.)
            field_mask: Field mask to limit response fields

        Returns:
            Response containing routes and route information

        Example:
            >>> client = RoutesClient(api_key="YOUR_KEY")
            >>> origin = {"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}}
            >>> destination = {"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}}
            >>> result = client.compute_routes(origin, destination, routing_preference="TRAFFIC_AWARE")
        """
        # Validation (issues #15, #16, #24, #34, #43, #44, #25)
        validate_waypoint_count(intermediates)
        travel_mode = validate_enum_value(travel_mode, VALID_TRAVEL_MODES, "travel_mode")
        if routing_preference:
            routing_preference = validate_enum_value(routing_preference, VALID_ROUTING_PREFERENCES, "routing_preference")
        if language_code:
            language_code = validate_language_code(language_code)
        if units:
            units = validate_units(units)
        if departure_time:
            departure_time = validate_departure_time(departure_time)
        if field_mask:
            field_mask = validate_field_mask(field_mask)
        if polyline_quality:
            polyline_quality = validate_enum_value(polyline_quality, VALID_POLYLINE_QUALITY, "polyline_quality")
        if polyline_encoding:
            polyline_encoding = validate_enum_value(polyline_encoding, VALID_POLYLINE_ENCODING, "polyline_encoding")
        
        endpoint = f"/directions/{self._api_version}:computeRoutes"
        
        request_body: Dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "travelMode": travel_mode,
        }

        if intermediates:
            request_body["intermediates"] = intermediates

        if routing_preference:
            request_body["routingPreference"] = routing_preference

        if departure_time:
            request_body["departureTime"] = departure_time

        if compute_alternative_routes:
            request_body["computeAlternativeRoutes"] = True

        if route_modifiers:
            request_body["routeModifiers"] = route_modifiers

        if language_code:
            request_body["languageCode"] = language_code

        if units:
            request_body["units"] = units

        if optimize_waypoint_order:
            request_body["optimizeWaypointOrder"] = True

        if polyline_quality:
            request_body["polylineQuality"] = polyline_quality

        if polyline_encoding:
            request_body["polylineEncoding"] = polyline_encoding

        if extra_computations:
            request_body["extraComputations"] = extra_computations

        headers = {}
        if field_mask:
            headers["X-Goog-FieldMask"] = field_mask

        return self._post(endpoint, data=request_body, headers=headers)

    def compute_route_matrix(
        self,
        origins: List[Dict[str, Any]],
        destinations: List[Dict[str, Any]],
        travel_mode: str = "DRIVE",
        routing_preference: Optional[str] = None,
        departure_time: Optional[str] = None,
        language_code: Optional[str] = None,
        units: Optional[str] = None,
        extra_computations: Optional[List[str]] = None,
        field_mask: Optional[str] = None,
    ) -> RouteMatrixResponse:
        """
        Compute travel times and distances for a matrix of origin-destination pairs

        Args:
            origins: List of origin waypoints
            destinations: List of destination waypoints
            travel_mode: Travel mode (DRIVE, WALK, BICYCLE, TRANSIT)
            routing_preference: Routing preference (TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL)
            departure_time: Departure time (ISO 8601 format or "now")
            language_code: Language code for response
            units: Unit system (IMPERIAL, METRIC)
            extra_computations: Extra computations
            field_mask: Field mask to limit response fields

        Returns:
            Response containing route matrix elements

        Example:
            >>> client = RoutesClient(api_key="YOUR_KEY")
            >>> origins = [{"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}}]
            >>> destinations = [{"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}}]
            >>> result = client.compute_route_matrix(origins, destinations)
        """
        # Validation (issues #15, #22, #41, #34, #43, #44, #25)
        validate_route_matrix_size(origins, destinations)
        travel_mode = validate_enum_value(travel_mode, VALID_TRAVEL_MODES, "travel_mode")
        if routing_preference:
            routing_preference = validate_enum_value(routing_preference, VALID_ROUTING_PREFERENCES, "routing_preference")
        if language_code:
            language_code = validate_language_code(language_code)
        if units:
            units = validate_units(units)
        if departure_time:
            departure_time = validate_departure_time(departure_time)
        if field_mask:
            field_mask = validate_field_mask(field_mask)
        
        endpoint = f"/distanceMatrix/{self._api_version}:computeRouteMatrix"

        request_body: Dict[str, Any] = {
            "origins": origins,
            "destinations": destinations,
            "travelMode": travel_mode,
        }

        if routing_preference:
            request_body["routingPreference"] = routing_preference

        if departure_time:
            request_body["departureTime"] = departure_time

        if language_code:
            request_body["languageCode"] = language_code

        if units:
            request_body["units"] = units

        if extra_computations:
            request_body["extraComputations"] = extra_computations

        headers = {}
        if field_mask:
            headers["X-Goog-FieldMask"] = field_mask

        return self._post(endpoint, data=request_body, headers=headers)

