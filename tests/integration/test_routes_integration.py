"""
Integration tests for RoutesClient with mocked HTTP responses
"""

import pytest
import requests_mock
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.exceptions import (
    InvalidRequestError,
    PermissionDeniedError,
    QuotaExceededError,
)


@pytest.mark.integration
class TestRoutesClientIntegration:
    """Integration tests for RoutesClient"""

    def test_compute_routes_success(self, api_key, sample_origin, sample_destination):
        """Test successful compute_routes call"""
        mock_response = {
            "routes": [
                {
                    "distanceMeters": 1000,
                    "duration": "5m",
                    "polyline": {"encodedPolyline": "test"}
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=200
            )

            client = RoutesClient(api_key)
            result = client.compute_routes(sample_origin, sample_destination)

            assert "routes" in result
            assert len(result["routes"]) == 1
            assert result["routes"][0]["distanceMeters"] == 1000
            client.close()

    def test_compute_routes_with_traffic(self, api_key, sample_origin, sample_destination):
        """Test compute_routes with traffic-aware routing"""
        mock_response = {
            "routes": [
                {
                    "distanceMeters": 1000,
                    "duration": "5m",
                    "durationInTraffic": "7m"
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=200
            )

            client = RoutesClient(api_key)
            result = client.compute_routes(
                sample_origin,
                sample_destination,
                routing_preference="TRAFFIC_AWARE",
                departure_time="now"
            )

            assert "routes" in result
            client.close()

    def test_compute_routes_with_field_mask(self, api_key, sample_origin, sample_destination):
        """Test compute_routes with field mask"""
        mock_response = {"routes": [{"distanceMeters": 1000}]}

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=200
            )

            client = RoutesClient(api_key)
            result = client.compute_routes(
                sample_origin,
                sample_destination,
                field_mask="routes.distanceMeters"
            )

            # Verify request had field mask header
            request = m.request_history[0]
            assert "X-Goog-FieldMask" in request.headers
            assert request.headers["X-Goog-FieldMask"] == "routes.distanceMeters"
            client.close()

    def test_compute_routes_error_400(self, api_key, sample_origin, sample_destination):
        """Test compute_routes with 400 error"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid request"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=400
            )

            client = RoutesClient(api_key)
            with pytest.raises(InvalidRequestError):
                client.compute_routes(sample_origin, sample_destination)
            client.close()

    def test_compute_routes_error_403(self, api_key, sample_origin, sample_destination):
        """Test compute_routes with 403 error"""
        mock_response = {
            "error": {
                "code": 403,
                "message": "Permission denied"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=403
            )

            client = RoutesClient(api_key)
            with pytest.raises(PermissionDeniedError):
                client.compute_routes(sample_origin, sample_destination)
            client.close()

    def test_compute_route_matrix_success(self, api_key, sample_origin, sample_destination):
        """Test successful compute_route_matrix call"""
        mock_response = {
            "routeMatrixElements": [
                {
                    "originIndex": 0,
                    "destinationIndex": 0,
                    "duration": "5m",
                    "distanceMeters": 1000
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                json=mock_response,
                status_code=200
            )

            client = RoutesClient(api_key)
            result = client.compute_route_matrix(
                [sample_origin],
                [sample_destination]
            )

            assert "routeMatrixElements" in result
            assert len(result["routeMatrixElements"]) == 1
            client.close()

    def test_compute_route_matrix_with_all_params(self, api_key, sample_origin, sample_destination):
        """Test compute_route_matrix with all parameters"""
        mock_response = {"routeMatrixElements": []}

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                json=mock_response,
                status_code=200
            )

            client = RoutesClient(api_key)
            result = client.compute_route_matrix(
                origins=[sample_origin],
                destinations=[sample_destination],
                travel_mode="WALK",
                routing_preference="TRAFFIC_AWARE",
                departure_time="now",
                language_code="en-US",
                units="METRIC",
                extra_computations=["TOLLS"],
                field_mask="originIndex,destinationIndex"
            )

            # Verify request body
            request = m.request_history[0]
            request_json = request.json()
            assert request_json["travelMode"] == "WALK"
            assert request_json["routingPreference"] == "TRAFFIC_AWARE"
            assert request_json["departureTime"] == "now"
            assert request_json["languageCode"] == "en-US"
            assert request_json["units"] == "METRIC"
            assert request_json["extraComputations"] == ["TOLLS"]
            assert request.headers["X-Goog-FieldMask"] == "originIndex,destinationIndex"
            client.close()

