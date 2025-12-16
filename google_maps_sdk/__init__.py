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

__version__ = "1.0.0"
__all__ = [
    "GoogleMapsClient",
    "RoutesClient",
    "DirectionsClient",
    "RoadsClient",
    "GoogleMapsAPIError",
    "InvalidRequestError",
    "PermissionDeniedError",
    "NotFoundError",
    "QuotaExceededError",
    "InternalServerError",
]

