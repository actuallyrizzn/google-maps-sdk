"""
Routes API Client

Modern routing API with traffic-aware routing capabilities.
"""

from typing import Optional, Dict, Any, List
import requests
from .base_client import BaseClient
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

    def __init__(
        self, 
        api_key: str, 
        timeout: int = 30,
        rate_limit_max_calls: Optional[int] = None,
        rate_limit_period: Optional[float] = None,
    ):
        """
        Initialize Routes API client

        Args:
            api_key: Google Maps Platform API key
            timeout: Request timeout in seconds
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
        """
        super().__init__(
            api_key, 
            self.BASE_URL, 
            timeout,
            rate_limit_max_calls=rate_limit_max_calls,
            rate_limit_period=rate_limit_period,
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
        
        try:
            response = self.session.post(
                url, json=data, headers=headers, params=params, timeout=request_timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            # Sanitize error message to prevent API key exposure
            from .utils import sanitize_api_key_for_logging
            error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
            from .exceptions import GoogleMapsAPIError
            raise GoogleMapsAPIError(f"Request failed: {error_msg}") from e

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
    ) -> Dict[str, Any]:
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
        
        endpoint = "/directions/v2:computeRoutes"
        
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
    ) -> Dict[str, Any]:
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
        
        endpoint = "/distanceMatrix/v2:computeRouteMatrix"

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

