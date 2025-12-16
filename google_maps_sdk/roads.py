"""
Roads API Client

Service for snapping GPS coordinates to roads and getting road metadata.
"""

from typing import Optional, List, Dict, Any
from .base_client import BaseClient


class RoadsClient(BaseClient):
    """Client for Google Maps Roads API"""

    BASE_URL = "https://roads.googleapis.com/v1"

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize Roads API client

        Args:
            api_key: Google Maps Platform API key
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, self.BASE_URL, timeout)

    def snap_to_roads(
        self,
        path: List[tuple],
        interpolate: bool = False,
    ) -> Dict[str, Any]:
        """
        Snap a GPS path to the most likely roads traveled

        Args:
            path: List of (latitude, longitude) tuples (max 100 points)
            interpolate: Whether to interpolate path to include all points forming full road geometry

        Returns:
            Response containing snapped points with place IDs

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> path = [(60.170880, 24.942795), (60.170879, 24.942796), (60.170877, 24.942796)]
            >>> result = client.snap_to_roads(path, interpolate=True)
        """
        if len(path) > 100:
            raise ValueError("Maximum 100 points allowed per request")

        # Format path as pipe-separated lat,lng pairs
        path_str = "|".join([f"{lat},{lng}" for lat, lng in path])

        params: Dict[str, Any] = {"path": path_str}

        if interpolate:
            params["interpolate"] = "true"

        return self._get("/snapToRoads", params=params)

    def nearest_roads(
        self,
        points: List[tuple],
    ) -> Dict[str, Any]:
        """
        Find the nearest road segments for a set of GPS points

        Args:
            points: List of (latitude, longitude) tuples (max 100 points)
                   Points don't need to form a continuous path

        Returns:
            Response containing nearest road segments with place IDs

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> points = [(60.170880, 24.942795), (60.170879, 24.942796)]
            >>> result = client.nearest_roads(points)
        """
        if len(points) > 100:
            raise ValueError("Maximum 100 points allowed per request")

        # Format points as pipe-separated lat,lng pairs
        points_str = "|".join([f"{lat},{lng}" for lat, lng in points])

        params = {"points": points_str}

        return self._get("/nearestRoads", params=params)

    def speed_limits(
        self,
        path: Optional[List[tuple]] = None,
        place_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get posted speed limits for road segments

        Args:
            path: List of (latitude, longitude) tuples representing road path (max 100 points)
            place_ids: List of Place IDs representing road segments (max 100)

        Returns:
            Response containing speed limits for road segments

        Example:
            >>> client = RoadsClient(api_key="YOUR_KEY")
            >>> # Using path
            >>> path = [(60.170880, 24.942795), (60.170879, 24.942796)]
            >>> result = client.speed_limits(path=path)
            >>> # Using place IDs
            >>> place_ids = ["ChIJ685WIFYViEgRHlHvBbiD5nE", "ChIJA01I-8YVhkgRGJb0fW4UX7Y"]
            >>> result = client.speed_limits(place_ids=place_ids)
        """
        if path and place_ids:
            raise ValueError("Either path or place_ids must be provided, not both")

        if not path and not place_ids:
            raise ValueError("Either path or place_ids must be provided")

        params: Dict[str, Any] = {}

        if path:
            if len(path) > 100:
                raise ValueError("Maximum 100 points allowed per request")
            path_str = "|".join([f"{lat},{lng}" for lat, lng in path])
            params["path"] = path_str

        if place_ids:
            if len(place_ids) > 100:
                raise ValueError("Maximum 100 place IDs allowed per request")
            params["placeId"] = ",".join(place_ids)

        return self._get("/speedLimits", params=params)

