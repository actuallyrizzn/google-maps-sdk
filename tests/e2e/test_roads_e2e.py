"""
End-to-end tests for RoadsClient with real API calls
"""

import os
import pytest
from google_maps_sdk.roads import RoadsClient


@pytest.mark.e2e
@pytest.mark.slow
class TestRoadsClientE2E:
    """E2E tests for RoadsClient"""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment"""
        key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not key:
            pytest.skip("GOOGLE_MAPS_API_KEY not set")
        return key

    def test_snap_to_roads_real(self, api_key):
        """Test snap_to_roads with real API"""
        path = [
            (60.170880, 24.942795),
            (60.170879, 24.942796),
            (60.170877, 24.942796)
        ]

        client = RoadsClient(api_key)
        result = client.snap_to_roads(path)

        assert "snappedPoints" in result
        assert len(result["snappedPoints"]) > 0
        point = result["snappedPoints"][0]
        assert "location" in point
        assert "placeId" in point
        client.close()

    def test_snap_to_roads_with_interpolate(self, api_key):
        """Test snap_to_roads with interpolation"""
        path = [
            (60.170880, 24.942795),
            (60.170879, 24.942796)
        ]

        client = RoadsClient(api_key)
        result = client.snap_to_roads(path, interpolate=True)

        assert "snappedPoints" in result
        client.close()

    def test_nearest_roads_real(self, api_key):
        """Test nearest_roads with real API"""
        points = [
            (60.170880, 24.942795),
            (60.170879, 24.942796)
        ]

        client = RoadsClient(api_key)
        result = client.nearest_roads(points)

        assert "snappedPoints" in result
        assert len(result["snappedPoints"]) > 0
        client.close()

    def test_speed_limits_with_path(self, api_key):
        """Test speed_limits with path"""
        path = [
            (60.170880, 24.942795),
            (60.170879, 24.942796)
        ]

        client = RoadsClient(api_key)
        result = client.speed_limits(path=path)

        # Speed limits may not be available for all paths
        assert result is not None
        if "speedLimits" in result:
            assert len(result["speedLimits"]) > 0
        client.close()

    def test_speed_limits_with_place_ids(self, api_key):
        """Test speed_limits with place IDs"""
        # First get place IDs from snap_to_roads
        path = [
            (60.170880, 24.942795),
            (60.170879, 24.942796)
        ]

        client = RoadsClient(api_key)
        snap_result = client.snap_to_roads(path)
        
        if "snappedPoints" in snap_result and len(snap_result["snappedPoints"]) > 0:
            place_ids = [
                point["placeId"]
                for point in snap_result["snappedPoints"]
                if "placeId" in point
            ]
            
            if place_ids:
                result = client.speed_limits(place_ids=place_ids)
                assert result is not None
                if "speedLimits" in result:
                    assert len(result["speedLimits"]) > 0
        
        client.close()





