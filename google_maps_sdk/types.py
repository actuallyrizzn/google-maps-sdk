"""
Type aliases for Google Maps Platform SDK (issue #56)
"""

from typing import Dict, Any, List, Tuple, Optional, Union

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
