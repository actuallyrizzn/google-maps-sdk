"""
Google Maps Platform Python SDK

A comprehensive Python SDK for Google Maps Platform APIs including:
- Routes API
- Directions API (Legacy)
- Roads API
"""

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
]

