"""
Integration tests for error responses (issue #259 / #61)
"""

import pytest
import requests_mock
import requests
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.client import GoogleMapsClient
from google_maps_sdk.exceptions import (
    InvalidRequestError,
    PermissionDeniedError,
    NotFoundError,
    QuotaExceededError,
    InternalServerError,
    GoogleMapsAPIError,
)


@pytest.mark.integration
class TestErrorResponseIntegration:
    """Integration tests for error response handling"""

    # HTTP Error Codes Tests

    def test_routes_400_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 400 Bad Request error"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid request parameters"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=400
            )

            client = RoutesClient(api_key)
            with pytest.raises(InvalidRequestError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 400
            assert "Invalid request" in str(exc_info.value.message)
            client.close()

    def test_routes_403_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 403 Forbidden error"""
        mock_response = {
            "error": {
                "code": 403,
                "message": "API key not valid"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=403
            )

            client = RoutesClient(api_key)
            with pytest.raises(PermissionDeniedError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 403
            client.close()

    def test_routes_404_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 404 Not Found error"""
        mock_response = {
            "error": {
                "code": 404,
                "message": "Endpoint not found"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=404
            )

            client = RoutesClient(api_key)
            with pytest.raises(NotFoundError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 404
            client.close()

    def test_routes_429_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 429 Too Many Requests error"""
        mock_response = {
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=429
            )

            client = RoutesClient(api_key)
            with pytest.raises(QuotaExceededError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 429
            client.close()

    def test_routes_500_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 500 Internal Server Error"""
        mock_response = {
            "error": {
                "code": 500,
                "message": "Internal server error"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=500
            )

            client = RoutesClient(api_key)
            with pytest.raises(InternalServerError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 500
            client.close()

    def test_routes_502_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 502 Bad Gateway error"""
        mock_response = {
            "error": {
                "code": 502,
                "message": "Bad gateway"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=502
            )

            client = RoutesClient(api_key)
            with pytest.raises(InternalServerError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            # 502 is converted to InternalServerError with status_code 500 (>= 500)
            assert exc_info.value.status_code == 500
            client.close()

    def test_routes_503_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API 503 Service Unavailable error"""
        mock_response = {
            "error": {
                "code": 503,
                "message": "Service unavailable"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=503
            )

            client = RoutesClient(api_key)
            with pytest.raises(InternalServerError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            # 503 is converted to InternalServerError with status_code 500 (>= 500)
            assert exc_info.value.status_code == 500
            client.close()

    def test_directions_400_error(self, api_key):
        """Test Directions API 400 Bad Request error"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid request"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=400
            )

            client = DirectionsClient(api_key)
            with pytest.raises(InvalidRequestError) as exc_info:
                client.get_directions("Toronto", "Montreal")
            
            assert exc_info.value.status_code == 400
            client.close()

    def test_directions_429_error(self, api_key):
        """Test Directions API 429 Too Many Requests error"""
        mock_response = {
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=429
            )

            client = DirectionsClient(api_key)
            with pytest.raises(QuotaExceededError) as exc_info:
                client.get_directions("Toronto", "Montreal")
            
            assert exc_info.value.status_code == 429
            client.close()

    def test_roads_404_error(self, api_key, sample_path):
        """Test Roads API 404 Not Found error"""
        mock_response = {
            "error": {
                "code": 404,
                "message": "Not found"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=404
            )

            client = RoadsClient(api_key)
            with pytest.raises(NotFoundError) as exc_info:
                client.snap_to_roads(sample_path)
            
            assert exc_info.value.status_code == 404
            client.close()

    def test_roads_429_error(self, api_key, sample_path):
        """Test Roads API 429 Too Many Requests error"""
        mock_response = {
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=429
            )

            client = RoadsClient(api_key)
            with pytest.raises(QuotaExceededError) as exc_info:
                client.snap_to_roads(sample_path)
            
            assert exc_info.value.status_code == 429
            client.close()

    def test_roads_500_error(self, api_key, sample_path):
        """Test Roads API 500 Internal Server Error"""
        mock_response = {
            "error": {
                "code": 500,
                "message": "Internal server error"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=500
            )

            client = RoadsClient(api_key)
            with pytest.raises(InternalServerError) as exc_info:
                client.snap_to_roads(sample_path)
            
            assert exc_info.value.status_code == 500
            client.close()

    # API-Specific Error Responses

    def test_directions_invalid_request_status(self, api_key):
        """Test Directions API INVALID_REQUEST status"""
        mock_response = {
            "status": "INVALID_REQUEST",
            "error_message": "Invalid request parameters"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            # Use valid addresses but API returns INVALID_REQUEST status
            with pytest.raises(InvalidRequestError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_directions_request_denied_status(self, api_key):
        """Test Directions API REQUEST_DENIED status"""
        mock_response = {
            "status": "REQUEST_DENIED",
            "error_message": "Request denied"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            with pytest.raises(PermissionDeniedError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_directions_over_query_limit_status(self, api_key):
        """Test Directions API OVER_QUERY_LIMIT status"""
        mock_response = {
            "status": "OVER_QUERY_LIMIT",
            "error_message": "Quota exceeded"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            with pytest.raises(QuotaExceededError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_directions_not_found_status(self, api_key):
        """Test Directions API NOT_FOUND status"""
        mock_response = {
            "status": "NOT_FOUND",
            "error_message": "Not found"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            with pytest.raises(NotFoundError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_directions_zero_results_status(self, api_key):
        """Test Directions API ZERO_RESULTS status"""
        mock_response = {
            "status": "ZERO_RESULTS",
            "error_message": "No results found"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            with pytest.raises(NotFoundError, match="No results found"):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_routes_matrix_400_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API compute_route_matrix 400 error"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid origins or destinations"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                json=mock_response,
                status_code=400
            )

            client = RoutesClient(api_key)
            # Use valid origins/destinations but API returns 400 error
            with pytest.raises(InvalidRequestError):
                client.compute_route_matrix([sample_origin], [sample_destination])
            client.close()

    def test_routes_matrix_429_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API compute_route_matrix 429 error"""
        mock_response = {
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                json=mock_response,
                status_code=429
            )

            client = RoutesClient(api_key)
            with pytest.raises(QuotaExceededError):
                client.compute_route_matrix([sample_origin], [sample_destination])
            client.close()

    # Network Errors

    def test_routes_connection_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API connection error"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                exc=requests.exceptions.ConnectionError("Connection failed")
            )

            client = RoutesClient(api_key)
            with pytest.raises(GoogleMapsAPIError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert "Connection" in str(exc_info.value.message) or "connection" in str(exc_info.value.message).lower()
            client.close()

    def test_directions_connection_error(self, api_key):
        """Test Directions API connection error"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                exc=requests.exceptions.ConnectionError("Connection failed")
            )

            client = DirectionsClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_roads_connection_error(self, api_key, sample_path):
        """Test Roads API connection error"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                exc=requests.exceptions.ConnectionError("Connection failed")
            )

            client = RoadsClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.snap_to_roads(sample_path)
            client.close()

    # Timeout Scenarios

    def test_routes_timeout_error(self, api_key, sample_origin, sample_destination):
        """Test Routes API timeout error"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                exc=requests.exceptions.Timeout("Request timeout")
            )

            client = RoutesClient(api_key)
            with pytest.raises(GoogleMapsAPIError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert "timeout" in str(exc_info.value.message).lower() or "Timeout" in str(exc_info.value.message)
            client.close()

    def test_directions_timeout_error(self, api_key):
        """Test Directions API timeout error"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                exc=requests.exceptions.Timeout("Request timeout")
            )

            client = DirectionsClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_roads_timeout_error(self, api_key, sample_path):
        """Test Roads API timeout error"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                exc=requests.exceptions.Timeout("Request timeout")
            )

            client = RoadsClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.snap_to_roads(sample_path)
            client.close()

    # Unified Client Error Tests

    def test_unified_client_routes_error(self, api_key, sample_origin, sample_destination):
        """Test unified client Routes API error"""
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

            client = GoogleMapsClient(api_key)
            with pytest.raises(InvalidRequestError):
                client.routes.compute_routes(sample_origin, sample_destination)
            client.close()

    def test_unified_client_directions_error(self, api_key):
        """Test unified client Directions API error"""
        mock_response = {
            "error": {
                "code": 403,
                "message": "Permission denied"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=403
            )

            client = GoogleMapsClient(api_key)
            with pytest.raises(PermissionDeniedError):
                client.directions.get_directions("Toronto", "Montreal")
            client.close()

    def test_unified_client_roads_error(self, api_key, sample_path):
        """Test unified client Roads API error"""
        mock_response = {
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://roads.googleapis.com/v1/snapToRoads",
                json=mock_response,
                status_code=429
            )

            client = GoogleMapsClient(api_key)
            with pytest.raises(QuotaExceededError):
                client.roads.snap_to_roads(sample_path)
            client.close()

    # Error Response Structure Tests

    def test_error_response_with_details(self, api_key, sample_origin, sample_destination):
        """Test error response with detailed error information"""
        mock_response = {
            "error": {
                "code": 400,
                "message": "Invalid request",
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
                        "reason": "INVALID_ARGUMENT",
                        "domain": "routes.googleapis.com"
                    }
                ]
            }
        }

        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=mock_response,
                status_code=400
            )

            client = RoutesClient(api_key)
            with pytest.raises(InvalidRequestError) as exc_info:
                client.compute_routes(sample_origin, sample_destination)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.response == mock_response
            client.close()

    def test_error_response_malformed_json(self, api_key, sample_origin, sample_destination):
        """Test error response with malformed JSON"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                text="<html>Error</html>",
                status_code=500,
                headers={"Content-Type": "text/html"}
            )

            client = RoutesClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.compute_routes(sample_origin, sample_destination)
            client.close()

    def test_error_response_empty_body(self, api_key, sample_origin, sample_destination):
        """Test error response with empty body"""
        with requests_mock.Mocker() as m:
            m.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                text="",
                status_code=500
            )

            client = RoutesClient(api_key)
            with pytest.raises(GoogleMapsAPIError):
                client.compute_routes(sample_origin, sample_destination)
            client.close()
