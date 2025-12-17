"""
Type stubs for types module (issue #46)
"""

from typing import Dict, Any, List, Tuple, Optional, Union, TypedDict

Coordinate = Tuple[float, float]
Path = List[Coordinate]
Waypoint = Dict[str, Any]
WaypointList = List[Waypoint]
APIResponse = Dict[str, Any]
LanguageCode = str
Units = str
TravelMode = str
DepartureTime = Union[str, int]
FieldMask = str

class RouteResponse(TypedDict, total=False):
    routes: List[Dict[str, Any]]
    fallbackInfo: Dict[str, Any]

class RouteMatrixResponse(TypedDict, total=False):
    routeMatrixElements: List[Dict[str, Any]]
    originIndex: int
    destinationIndex: int
    status: Dict[str, Any]
    condition: str
    distanceMeters: int
    duration: str
    staticDuration: str
    polyline: Dict[str, Any]
    routeModifiers: Dict[str, Any]

class DirectionsResponse(TypedDict, total=False):
    routes: List[Dict[str, Any]]
    status: str
    geocoded_waypoints: List[Dict[str, Any]]
    error_message: str

class SnapToRoadsResponse(TypedDict, total=False):
    snappedPoints: List[Dict[str, Any]]
    warningMessage: str

class NearestRoadsResponse(TypedDict, total=False):
    snappedPoints: List[Dict[str, Any]]

class SpeedLimitsResponse(TypedDict, total=False):
    speedLimits: List[Dict[str, Any]]
    snappedPoints: List[Dict[str, Any]]
