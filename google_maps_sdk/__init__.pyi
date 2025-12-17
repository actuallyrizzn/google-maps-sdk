"""
Type stubs for Google Maps Platform Python SDK (issue #46)
"""

from typing import Any
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

__version__: str

__all__: list[str]
