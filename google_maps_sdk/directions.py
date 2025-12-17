"""
Directions API (Legacy) Client

Legacy directions service. Consider migrating to Routes API for new projects.
"""

from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
from .base_client import BaseClient
from .retry import RetryConfig
from .types import DirectionsResponse

if TYPE_CHECKING:
    from requests.adapters import HTTPAdapter
from .utils import (
    validate_waypoint_count,
    validate_language_code,
    validate_units,
    validate_departure_time,
    validate_non_empty_string,
    validate_enum_value,
    VALID_TRAVEL_MODES,
)


class DirectionsClient(BaseClient):
    """Client for Google Maps Directions API (Legacy)"""

    BASE_URL = "https://maps.googleapis.com/maps/api/directions"

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
    ):
        """
        Initialize Directions API client

        Args:
            api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var) (issue #31)
            timeout: Request timeout in seconds
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
            retry_config: Retry configuration (None to disable retries) (issue #11)
            enable_cache: Enable response caching (default: False) (issue #37)
            cache_ttl: Cache time-to-live in seconds (default: 300.0 = 5 minutes) (issue #37)
            cache_maxsize: Maximum number of cached responses (default: 100) (issue #37)
            http_adapter: Custom HTTPAdapter for proxies, custom SSL, etc. (None to use default) (issue #38)
        """
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
        )

    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        waypoints: Optional[List[str]] = None,
        alternatives: bool = False,
        avoid: Optional[List[str]] = None,
        language: Optional[str] = None,
        units: Optional[str] = None,
        region: Optional[str] = None,
        departure_time: Optional[Union[str, int]] = None,
        arrival_time: Optional[int] = None,
        traffic_model: Optional[str] = None,
        transit_mode: Optional[List[str]] = None,
        transit_routing_preference: Optional[str] = None,
        output_format: str = "json",
    ) -> DirectionsResponse:
        """
        Get directions between two locations

        Args:
            origin: Origin location (address, place ID, or lat/lng)
            destination: Destination location
            mode: Travel mode (driving, walking, bicycling, transit)
            waypoints: List of intermediate waypoints
            alternatives: Whether to return alternative routes
            avoid: Features to avoid (tolls, highways, ferries, indoor)
            language: Response language code (e.g., "en", "es")
            units: Unit system (metric, imperial)
            region: Region code for biasing (e.g., "us", "gb")
            departure_time: Departure time ("now" or Unix timestamp)
            arrival_time: Arrival time (Unix timestamp)
            traffic_model: Traffic model (best_guess, pessimistic, optimistic)
            transit_mode: Transit modes (bus, subway, train, tram, rail)
            transit_routing_preference: Transit routing (less_walking, fewer_transfers)
            output_format: Output format (json or xml)

        Returns:
            Directions response

        Example:
            >>> client = DirectionsClient(api_key="YOUR_KEY")
            >>> result = client.get_directions("Toronto", "Montreal")
        """
        # Validation (issues #16, #24, #43, #44, #25, #15)
        validate_non_empty_string(origin, "origin")
        validate_non_empty_string(destination, "destination")
        validate_waypoint_count(waypoints)
        mode = validate_enum_value(mode, VALID_TRAVEL_MODES, "mode", normalize_case=False)
        if language:
            language = validate_language_code(language)
        if units:
            units = validate_units(units)
        if departure_time:
            departure_time = validate_departure_time(departure_time)
        
        params: Dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
        }

        if waypoints:
            # Sanitize waypoints (issue #8)
            sanitized_waypoints = [validate_non_empty_string(wp, "waypoint") for wp in waypoints]
            params["waypoints"] = "|".join(sanitized_waypoints)

        if alternatives:
            params["alternatives"] = "true"

        if avoid:
            params["avoid"] = "|".join(avoid)

        if language:
            params["language"] = language

        if units:
            params["units"] = units

        if region:
            params["region"] = region

        if departure_time:
            if isinstance(departure_time, str):
                params["departure_time"] = departure_time
            else:
                params["departure_time"] = str(departure_time)

        if arrival_time:
            params["arrival_time"] = str(arrival_time)

        if traffic_model:
            params["traffic_model"] = traffic_model

        if transit_mode:
            params["transit_mode"] = "|".join(transit_mode)

        if transit_routing_preference:
            params["transit_routing_preference"] = transit_routing_preference

        endpoint = f"/{output_format}"
        return self._get(endpoint, params=params)

    def get_directions_json(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        waypoints: Optional[List[str]] = None,
        alternatives: bool = False,
        avoid: Optional[List[str]] = None,
        language: Optional[str] = None,
        units: Optional[str] = None,
        region: Optional[str] = None,
        departure_time: Optional[Union[str, int]] = None,
        arrival_time: Optional[int] = None,
        traffic_model: Optional[str] = None,
        transit_mode: Optional[List[str]] = None,
        transit_routing_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get directions in JSON format (convenience method)

        Args:
            Same as get_directions

        Returns:
            Directions response in JSON format
        """
        return self.get_directions(
            origin=origin,
            destination=destination,
            mode=mode,
            waypoints=waypoints,
            alternatives=alternatives,
            avoid=avoid,
            language=language,
            units=units,
            region=region,
            departure_time=departure_time,
            arrival_time=arrival_time,
            traffic_model=traffic_model,
            transit_mode=transit_mode,
            transit_routing_preference=transit_routing_preference,
            output_format="json",
        )

    def get_directions_xml(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        waypoints: Optional[List[str]] = None,
        alternatives: bool = False,
        avoid: Optional[List[str]] = None,
        language: Optional[str] = None,
        units: Optional[str] = None,
        region: Optional[str] = None,
        departure_time: Optional[Union[str, int]] = None,
        arrival_time: Optional[int] = None,
        traffic_model: Optional[str] = None,
        transit_mode: Optional[List[str]] = None,
        transit_routing_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get directions in XML format (convenience method)

        Args:
            Same as get_directions

        Returns:
            Directions response in XML format (as dict with 'raw' key containing XML string)
        """
        return self.get_directions(
            origin=origin,
            destination=destination,
            mode=mode,
            waypoints=waypoints,
            alternatives=alternatives,
            avoid=avoid,
            language=language,
            units=units,
            region=region,
            departure_time=departure_time,
            arrival_time=arrival_time,
            traffic_model=traffic_model,
            transit_mode=transit_mode,
            transit_routing_preference=transit_routing_preference,
            output_format="xml",
        )

    def __repr__(self) -> str:
        """String representation of client (issue #52)"""
        return f"{self.__class__.__name__}(api_key='***', timeout={self.timeout})"

