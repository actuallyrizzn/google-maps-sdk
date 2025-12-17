"""
Google Maps Platform Python SDK

A comprehensive Python SDK for Google Maps Platform APIs including:
- Routes API
- Directions API (Legacy)
- Roads API
"""

import sys

# Check minimum Python version
if sys.version_info < (3, 8):
    raise RuntimeError(
        "google-maps-sdk requires Python 3.8 or higher. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

from .client import GoogleMapsClient
from .routes import RoutesClient
from .directions import DirectionsClient
from .roads import RoadsClient
from .exceptions import (
    GoogleMapsAPIError,
    InvalidRequestError,
    PermissionDeniedError,
    NotFoundError,
    QuotaExceededError,
    InternalServerError,
)
from .types import (
    Coordinate,
    Path,
    Waypoint,
    WaypointList,
    APIResponse,
    LanguageCode,
    Units,
    TravelMode,
    DepartureTime,
    FieldMask,
    RouteResponse,
    RouteMatrixResponse,
    DirectionsResponse,
    SnapToRoadsResponse,
    NearestRoadsResponse,
    SpeedLimitsResponse,
)

__version__ = "1.0.0"

# Validate __all__ exports (issue #50)
# All public exports should be listed here
__all__ = [
    # Clients
    "GoogleMapsClient",
    "RoutesClient",
    "DirectionsClient",
    "RoadsClient",
    # Exceptions
    "GoogleMapsAPIError",
    "InvalidRequestError",
    "PermissionDeniedError",
    "NotFoundError",
    "QuotaExceededError",
    "InternalServerError",
    # Type aliases
    "Coordinate",
    "Path",
    "Waypoint",
    "WaypointList",
    "APIResponse",
    "LanguageCode",
    "Units",
    "TravelMode",
    "DepartureTime",
    "FieldMask",
    # Response types (issue #18)
    "RouteResponse",
    "RouteMatrixResponse",
    "DirectionsResponse",
    "SnapToRoadsResponse",
    "NearestRoadsResponse",
    "SpeedLimitsResponse",
]

