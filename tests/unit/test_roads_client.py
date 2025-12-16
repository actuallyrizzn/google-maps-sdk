"""
Unit tests for RoadsClient
"""

import pytest
from unittest.mock import patch
from google_maps_sdk.roads import RoadsClient


@pytest.mark.unit
class TestRoadsClientInit:
    """Test RoadsClient initialization"""

    def test_init(self, api_key):
        """Test initialization"""
        client = RoadsClient(api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://roads.googleapis.com/v1"
        assert client.timeout == 30
        client.close()

    def test_init_with_timeout(self, api_key):
        """Test initialization with custom timeout"""
        client = RoadsClient(api_key, timeout=60)
        assert client.timeout == 60
        client.close()


@pytest.mark.unit
class TestRoadsClientSnapToRoads:
    """Test RoadsClient.snap_to_roads method"""

    @patch("google_maps_sdk.roads.BaseClient._get")
    def test_snap_to_roads_basic(self, mock_get, api_key, sample_path):
        """Test basic snap_to_roads call"""
        mock_get.return_value = {"snappedPoints": []}
        
        client = RoadsClient(api_key)
        result = client.snap_to_roads(sample_path)

        assert result == {"snappedPoints": []}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/snapToRoads"
        assert "path" in call_args[1]["params"]
        # Python may format floats without trailing zeros
        path_str = call_args[1]["params"]["path"]
        assert "60.17088" in path_str or "60.170880" in path_str
        assert "24.942795" in path_str
        client.close()

    @patch("google_maps_sdk.roads.BaseClient._get")
    def test_snap_to_roads_with_interpolate(self, mock_get, api_key, sample_path):
        """Test snap_to_roads with interpolation"""
        mock_get.return_value = {"snappedPoints": []}
        
        client = RoadsClient(api_key)
        result = client.snap_to_roads(sample_path, interpolate=True)

        call_args = mock_get.call_args
        assert call_args[1]["params"]["interpolate"] == "true"
        client.close()

    def test_snap_to_roads_too_many_points(self, api_key):
        """Test snap_to_roads with too many points"""
        path = [(0.0, 0.0)] * 101  # 101 points
        
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Maximum 100 points"):
            client.snap_to_roads(path)
        client.close()


@pytest.mark.unit
class TestRoadsClientNearestRoads:
    """Test RoadsClient.nearest_roads method"""

    @patch("google_maps_sdk.roads.BaseClient._get")
    def test_nearest_roads_basic(self, mock_get, api_key, sample_path):
        """Test basic nearest_roads call"""
        mock_get.return_value = {"snappedPoints": []}
        
        points = sample_path[:2]  # Use first 2 points

        client = RoadsClient(api_key)
        result = client.nearest_roads(points)

        assert result == {"snappedPoints": []}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/nearestRoads"
        assert "points" in call_args[1]["params"]
        client.close()

    def test_nearest_roads_too_many_points(self, api_key):
        """Test nearest_roads with too many points"""
        points = [(0.0, 0.0)] * 101  # 101 points
        
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Maximum 100 points"):
            client.nearest_roads(points)
        client.close()


@pytest.mark.unit
class TestRoadsClientSpeedLimits:
    """Test RoadsClient.speed_limits method"""

    @patch("google_maps_sdk.roads.BaseClient._get")
    def test_speed_limits_with_path(self, mock_get, api_key, sample_path):
        """Test speed_limits with path"""
        mock_get.return_value = {"speedLimits": []}
        
        path = sample_path[:2]  # Use first 2 points

        client = RoadsClient(api_key)
        result = client.speed_limits(path=path)

        assert result == {"speedLimits": []}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/speedLimits"
        assert "path" in call_args[1]["params"]
        client.close()

    @patch("google_maps_sdk.roads.BaseClient._get")
    def test_speed_limits_with_place_ids(self, mock_get, api_key, sample_place_ids):
        """Test speed_limits with place IDs"""
        mock_get.return_value = {"speedLimits": []}
        
        client = RoadsClient(api_key)
        result = client.speed_limits(place_ids=sample_place_ids)

        assert result == {"speedLimits": []}
        call_args = mock_get.call_args
        assert "placeId" in call_args[1]["params"]
        assert call_args[1]["params"]["placeId"] == ",".join(sample_place_ids)
        client.close()

    def test_speed_limits_both_provided(self, api_key, sample_path, sample_place_ids):
        """Test speed_limits with both path and place_ids (should fail)"""
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Either path or place_ids"):
            client.speed_limits(path=sample_path, place_ids=sample_place_ids)
        client.close()

    def test_speed_limits_neither_provided(self, api_key):
        """Test speed_limits with neither path nor place_ids (should fail)"""
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Either path or place_ids"):
            client.speed_limits()
        client.close()

    def test_speed_limits_too_many_points(self, api_key):
        """Test speed_limits with too many points"""
        path = [(0.0, 0.0)] * 101  # 101 points
        
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Maximum 100 points"):
            client.speed_limits(path=path)
        client.close()

    def test_speed_limits_too_many_place_ids(self, api_key):
        """Test speed_limits with too many place IDs"""
        place_ids = ["ChIJ"] * 101  # 101 place IDs
        
        client = RoadsClient(api_key)
        with pytest.raises(ValueError, match="Maximum 100 place IDs"):
            client.speed_limits(place_ids=place_ids)
        client.close()

