"""
Type aliases and TypedDict definitions for Google Maps Platform SDK (issue #18, #56)
"""

from typing import Dict, Any, List, Tuple, Optional, Union, TypedDict

# Coordinate types
Coordinate = Tuple[float, float]
"""A coordinate tuple (latitude, longitude)"""

Path = List[Coordinate]
"""A list of coordinates representing a path"""

# API request/response types
Waypoint = Dict[str, Any]
"""A waypoint object (location with latLng, placeId, or address)"""

WaypointList = List[Waypoint]
"""A list of waypoints"""

APIResponse = Dict[str, Any]
"""Generic API response dictionary"""

# Parameter types
LanguageCode = str
"""Language code (e.g., 'en', 'en-US')"""

Units = str
"""Unit system ('IMPERIAL' or 'METRIC')"""

TravelMode = str
"""Travel mode ('DRIVE', 'WALK', 'BICYCLE', 'TRANSIT')"""

DepartureTime = Union[str, int]
"""Departure time ('now', ISO 8601 string, or Unix timestamp)"""

FieldMask = str
"""Field mask string (comma-separated field paths)"""


# TypedDict definitions for API responses (issue #18)
class RouteResponse(TypedDict, total=False):
    """Response from Routes API compute_routes method"""
    routes: List[Dict[str, Any]]
    """List of route objects"""
    fallbackInfo: Dict[str, Any]
    """Fallback information if route computation used fallback data"""


class RouteMatrixResponse(TypedDict, total=False):
    """Response from Routes API compute_route_matrix method"""
    routeMatrixElements: List[Dict[str, Any]]
    """List of route matrix elements"""
    originIndex: int
    """Index of the origin in the request"""
    destinationIndex: int
    """Index of the destination in the request"""
    status: Dict[str, Any]
    """Status of the route matrix element"""
    condition: str
    """Condition of the route (e.g., 'ROUTE_EXISTS')"""
    distanceMeters: int
    """Distance in meters"""
    duration: str
    """Duration as a string (e.g., '3600s')"""
    staticDuration: str
    """Static duration without traffic"""
    polyline: Dict[str, Any]
    """Encoded polyline"""
    routeModifiers: Dict[str, Any]
    """Route modifiers applied"""


class DirectionsResponse(TypedDict, total=False):
    """Response from Directions API get_directions method"""
    routes: List[Dict[str, Any]]
    """List of route objects"""
    status: str
    """Status of the request (e.g., 'OK', 'NOT_FOUND')"""
    geocoded_waypoints: List[Dict[str, Any]]
    """Geocoded waypoint information"""
    error_message: str
    """Error message if status is not OK"""


class SnapToRoadsResponse(TypedDict, total=False):
    """Response from Roads API snap_to_roads method"""
    snappedPoints: List[Dict[str, Any]]
    """List of snapped points with place IDs and coordinates"""
    warningMessage: str
    """Warning message if any issues occurred"""


class NearestRoadsResponse(TypedDict, total=False):
    """Response from Roads API nearest_roads method"""
    snappedPoints: List[Dict[str, Any]]
    """List of snapped points with place IDs and coordinates"""


class SpeedLimitsResponse(TypedDict, total=False):
    """Response from Roads API speed_limits method"""
    speedLimits: List[Dict[str, Any]]
    """List of speed limit information"""
    snappedPoints: List[Dict[str, Any]]
    """List of snapped points corresponding to speed limits"""
