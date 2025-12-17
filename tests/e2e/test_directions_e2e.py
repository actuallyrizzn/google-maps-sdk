"""
End-to-end tests for DirectionsClient with real API calls
"""

import os
import pytest
from google_maps_sdk.directions import DirectionsClient


@pytest.mark.e2e
@pytest.mark.slow
class TestDirectionsClientE2E:
    """E2E tests for DirectionsClient"""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment"""
        key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not key:
            pytest.skip("GOOGLE_MAPS_API_KEY not set")
        return key

    def test_get_directions_real(self, api_key):
        """Test get_directions with real API"""
        client = DirectionsClient(api_key)
        result = client.get_directions("Toronto", "Montreal")

        assert result["status"] == "OK"
        assert "routes" in result
        assert len(result["routes"]) > 0
        route = result["routes"][0]
        assert "legs" in route
        client.close()

    def test_get_directions_with_waypoints(self, api_key):
        """Test get_directions with waypoints"""
        client = DirectionsClient(api_key)
        result = client.get_directions(
            "Chicago, IL",
            "Los Angeles, CA",
            waypoints=["Joplin, MO", "Oklahoma City, OK"]
        )

        assert result["status"] == "OK"
        assert "routes" in result
        client.close()

    def test_get_directions_with_traffic(self, api_key):
        """Test get_directions with traffic information"""
        client = DirectionsClient(api_key)
        result = client.get_directions(
            "Toronto",
            "Montreal",
            departure_time="now",
            traffic_model="best_guess"
        )

        assert result["status"] == "OK"
        if "routes" in result and len(result["routes"]) > 0:
            route = result["routes"][0]
            if "legs" in route and len(route["legs"]) > 0:
                leg = route["legs"][0]
                # May or may not have duration_in_traffic depending on traffic data
                assert "duration" in leg
        client.close()

    def test_get_directions_json_convenience(self, api_key):
        """Test get_directions_json convenience method"""
        client = DirectionsClient(api_key)
        result = client.get_directions_json("Toronto", "Montreal")

        assert result["status"] == "OK"
        client.close()





