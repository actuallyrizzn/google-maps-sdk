"""
End-to-end tests for RoutesClient with real API calls
"""

import os
import pytest
from google_maps_sdk.routes import RoutesClient


@pytest.mark.e2e
@pytest.mark.slow
class TestRoutesClientE2E:
    """E2E tests for RoutesClient"""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment"""
        key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not key:
            pytest.skip("GOOGLE_MAPS_API_KEY not set")
        return key

    def test_compute_routes_real(self, api_key):
        """Test compute_routes with real API"""
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

        client = RoutesClient(api_key)
        result = client.compute_routes(origin, destination)

        assert "routes" in result
        assert len(result["routes"]) > 0
        route = result["routes"][0]
        assert "distanceMeters" in route or "duration" in route
        client.close()

    def test_compute_routes_with_traffic(self, api_key):
        """Test compute_routes with traffic-aware routing"""
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

        client = RoutesClient(api_key)
        result = client.compute_routes(
            origin,
            destination,
            routing_preference="TRAFFIC_AWARE",
            departure_time="now"
        )

        assert "routes" in result
        client.close()

    def test_compute_route_matrix_real(self, api_key):
        """Test compute_route_matrix with real API"""
        origins = [
            {
                "location": {
                    "latLng": {
                        "latitude": 37.419734,
                        "longitude": -122.0827784
                    }
                }
            }
        ]
        destinations = [
            {
                "location": {
                    "latLng": {
                        "latitude": 37.417670,
                        "longitude": -122.079595
                    }
                }
            }
        ]

        client = RoutesClient(api_key)
        result = client.compute_route_matrix(origins, destinations)

        # Route matrix may return stream or array
        assert result is not None
        client.close()





