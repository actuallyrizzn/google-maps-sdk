"""
Main Google Maps Platform client

Unified client providing access to all Google Maps Platform APIs.
"""

from typing import Optional
from .routes import RoutesClient
from .directions import DirectionsClient
from .roads import RoadsClient


class GoogleMapsClient:
    """
    Unified client for Google Maps Platform APIs

    Provides access to Routes API, Directions API, and Roads API through
    a single client interface.
    """

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Google Maps Platform client

        Args:
            api_key: Google Maps Platform API key
            timeout: Request timeout in seconds for all API calls

        Example:
            >>> client = GoogleMapsClient(api_key="YOUR_API_KEY")
            >>> routes = client.routes.compute_routes(origin, destination)
        """
        self.api_key = api_key
        self.timeout = timeout

        # Initialize sub-clients
        self.routes = RoutesClient(api_key, timeout)
        self.directions = DirectionsClient(api_key, timeout)
        self.roads = RoadsClient(api_key, timeout)

    def close(self):
        """Close all HTTP sessions"""
        self.routes.close()
        self.directions.close()
        self.roads.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

