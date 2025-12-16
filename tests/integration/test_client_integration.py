"""
Integration tests for GoogleMapsClient with mocked HTTP responses
"""

import pytest
import requests_mock
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.integration
class TestGoogleMapsClientIntegration:
    """Integration tests for GoogleMapsClient"""

    def test_unified_client_routes(self, api_key, sample_origin, sample_destination):
        """Test unified client Routes API access"""
        mock_response = {"routes": [{"distanceMeters": 1000}]}

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=200
            )

            client = GoogleMapsClient(api_key)
            result = client.routes.compute_routes(sample_origin, sample_destination)

            assert "routes" in result
            client.close()

    def test_unified_client_directions(self, api_key):
        """Test unified client Directions API access"""
        mock_response = {"status": "OK", "routes": []}

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = GoogleMapsClient(api_key)
            result = client.directions.get_directions("Toronto", "Montreal")

            assert result["status"] == "OK"
            client.close()

    def test_unified_client_roads(self, api_key, sample_path):
        """Test unified client Roads API access"""
        mock_response = {"snappedPoints": []}

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=200
            )

            client = GoogleMapsClient(api_key)
            result = client.roads.snap_to_roads(sample_path)

            assert "snappedPoints" in result
            client.close()

    def test_unified_client_all_apis(self, api_key, sample_origin, sample_destination, sample_path):
        """Test unified client with all APIs"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json={"routes": []},
                status_code=200
            )
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json={"status": "OK", "routes": []},
                status_code=200
            )
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json={"snappedPoints": []},
                status_code=200
            )

            client = GoogleMapsClient(api_key)
            
            # Test all APIs
            route = client.routes.compute_routes(sample_origin, sample_destination)
            directions = client.directions.get_directions("Toronto", "Montreal")
            snapped = client.roads.snap_to_roads(sample_path)

            assert "routes" in route
            assert directions["status"] == "OK"
            assert "snappedPoints" in snapped
            
            client.close()

