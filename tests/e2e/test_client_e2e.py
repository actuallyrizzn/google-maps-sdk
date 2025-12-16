"""
End-to-end tests for GoogleMapsClient with real API calls
"""

import os
import pytest
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.e2e
@pytest.mark.slow
class TestGoogleMapsClientE2E:
    """E2E tests for GoogleMapsClient"""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment"""
        key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not key:
            pytest.skip("GOOGLE_MAPS_API_KEY not set")
        return key

    def test_unified_client_all_apis(self, api_key):
        """Test unified client with all APIs using real API"""
        origin = {
            "location": {
                "latLng": {
                    "latitude": 37.419734,
                    "longitude": -122.0827784
                }
            }
        }
        destination = {
            "location": {
                "latLng": {
                    "latitude": 37.417670,
                    "longitude": -122.079595
                }
            }
        }
        path = [
            (60.170880, 24.942795),
            (60.170879, 24.942796)
        ]

        with GoogleMapsClient(api_key) as client:
            # Test Routes API
            route = client.routes.compute_routes(origin, destination)
            assert "routes" in route

            # Test Directions API
            directions = client.directions.get_directions("Toronto", "Montreal")
            assert directions["status"] == "OK"

            # Test Roads API
            snapped = client.roads.snap_to_roads(path)
            assert "snappedPoints" in snapped


