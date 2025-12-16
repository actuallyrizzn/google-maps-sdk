"""
Integration tests for RoadsClient with mocked HTTP responses
"""

import pytest
import requests_mock
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.exceptions import (
    InvalidRequestError,
    PermissionDeniedError,
)


@pytest.mark.integration
class TestRoadsClientIntegration:
    """Integration tests for RoadsClient"""

    def test_snap_to_roads_success(self, api_key, sample_path):
        """Test successful snap_to_roads call"""
        mock_response = {
            "snappedPoints": [
                {
                    "location": {"latitude": 60.170880, "longitude": 24.942795},
                    "originalIndex": 0,
                    "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=200
            )

            client = RoadsClient(api_key)
            result = client.snap_to_roads(sample_path)

            assert "snappedPoints" in result
            assert len(result["snappedPoints"]) == 1
            assert result["snappedPoints"][0]["placeId"] == "ChIJ685WIFYViEgRHlHvBbiD5nE"
            client.close()

    def test_snap_to_roads_with_interpolate(self, api_key, sample_path):
        """Test snap_to_roads with interpolation"""
        mock_response = {"snappedPoints": []}

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=200
            )

            client = RoadsClient(api_key)
            result = client.snap_to_roads(sample_path, interpolate=True)

            # Verify interpolate parameter in request
            request = m.request_history[0]
            assert "interpolate" in request.qs
            assert request.qs["interpolate"][0] == "true"
            client.close()

    def test_nearest_roads_success(self, api_key, sample_path):
        """Test successful nearest_roads call"""
        mock_response = {
            "snappedPoints": [
                {
                    "location": {"latitude": 60.170880, "longitude": 24.942795},
                    "originalIndex": 0,
                    "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE"
                }
            ]
        }

        points = sample_path[:2]

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/nearestRoads",
                json=mock_response,
                status_code=200
            )

            client = RoadsClient(api_key)
            result = client.nearest_roads(points)

            assert "snappedPoints" in result
            client.close()

    def test_speed_limits_with_path(self, api_key, sample_path):
        """Test speed_limits with path"""
        mock_response = {
            "speedLimits": [
                {
                    "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE",
                    "speedLimit": 60,
                    "units": "KPH"
                }
            ],
            "snappedPoints": []
        }

        path = sample_path[:2]

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/speedLimits",
                json=mock_response,
                status_code=200
            )

            client = RoadsClient(api_key)
            result = client.speed_limits(path=path)

            assert "speedLimits" in result
            assert len(result["speedLimits"]) == 1
            assert result["speedLimits"][0]["speedLimit"] == 60
            client.close()

    def test_speed_limits_with_place_ids(self, api_key, sample_place_ids):
        """Test speed_limits with place IDs"""
        mock_response = {
            "speedLimits": [
                {
                    "placeId": "ChIJ685WIFYViEgRHlHvBbiD5nE",
                    "speedLimit": 50,
                    "units": "MPH"
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/speedLimits",
                json=mock_response,
                status_code=200
            )

            client = RoadsClient(api_key)
            result = client.speed_limits(place_ids=sample_place_ids)

            # Verify place IDs in request
            request = m.request_history[0]
            # requests_mock lowercases query parameters
            assert "placeid" in request.qs
            assert request.qs["placeid"][0].lower() == ",".join(sample_place_ids).lower()
            client.close()

    def test_speed_limits_error_400(self, api_key, sample_path):
        """Test speed_limits with 400 error"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid request"
            }
        }

        path = sample_path[:2]

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/speedLimits",
                json=mock_response,
                status_code=400
            )

            client = RoadsClient(api_key)
            with pytest.raises(InvalidRequestError):
                client.speed_limits(path=path)
            client.close()

    def test_speed_limits_error_403(self, api_key, sample_path):
        """Test speed_limits with 403 error"""
        mock_response = {
            "error": {
                "code": 403,
                "message": "Permission denied"
            }
        }

        path = sample_path[:2]

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/speedLimits",
                json=mock_response,
                status_code=403
            )

            client = RoadsClient(api_key)
            with pytest.raises(PermissionDeniedError):
                client.speed_limits(path=path)
            client.close()

