"""
Integration tests for DirectionsClient with mocked HTTP responses
"""

import pytest
import requests_mock
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.exceptions import (
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
    InvalidRequestError,
)


@pytest.mark.integration
class TestDirectionsClientIntegration:
    """Integration tests for DirectionsClient"""

    def test_get_directions_success(self, api_key):
        """Test successful get_directions call"""
        mock_response = {
            "status": "OK",
            "routes": [
                {
                    "legs": [
                        {
                            "distance": {"text": "100 km", "value": 100000},
                            "duration": {"text": "1 hour", "value": 3600}
                        }
                    ]
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            result = client.get_directions("Toronto", "Montreal")

            assert result["status"] == "OK"
            assert "routes" in result
            assert len(result["routes"]) == 1
            client.close()

    def test_get_directions_with_waypoints(self, api_key):
        """Test get_directions with waypoints"""
        mock_response = {"status": "OK", "routes": []}

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            result = client.get_directions(
                "Toronto",
                "Montreal",
                waypoints=["Ottawa", "Quebec"]
            )

            # Verify waypoints in request
            request = m.request_history[0]
            assert "waypoints" in request.qs
            # requests_mock lowercases query parameters
            waypoints_value = request.qs["waypoints"][0].lower()
            assert waypoints_value == "ottawa|quebec"
            client.close()

    def test_get_directions_with_traffic(self, api_key):
        """Test get_directions with traffic information"""
        mock_response = {
            "status": "OK",
            "routes": [
                {
                    "legs": [
                        {
                            "duration": {"text": "1 hour", "value": 3600},
                            "duration_in_traffic": {"text": "1.5 hours", "value": 5400}
                        }
                    ]
                }
            ]
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            result = client.get_directions(
                "Toronto",
                "Montreal",
                departure_time="now",
                traffic_model="best_guess"
            )

            request = m.request_history[0]
            assert request.qs["departure_time"][0] == "now"
            assert request.qs["traffic_model"][0] == "best_guess"
            client.close()

    def test_get_directions_xml(self, api_key):
        """Test get_directions with XML format"""
        xml_content = "<DirectionsResponse><status>OK</status></DirectionsResponse>"

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/xml",
                text=xml_content,
                status_code=200,
                headers={"Content-Type": "application/xml"}
            )

            client = DirectionsClient(api_key)
            result = client.get_directions("Toronto", "Montreal", output_format="xml")

            assert "raw" in result or "status" in result
            client.close()

    def test_get_directions_error_request_denied(self, api_key):
        """Test get_directions with REQUEST_DENIED status"""
        mock_response = {
            "status": "REQUEST_DENIED",
            "error_message": "Permission denied"
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

    def test_get_directions_error_over_query_limit(self, api_key):
        """Test get_directions with OVER_QUERY_LIMIT status"""
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

    def test_get_directions_error_not_found(self, api_key):
        """Test get_directions with NOT_FOUND status"""
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

    def test_get_directions_error_zero_results(self, api_key):
        """Test get_directions with ZERO_RESULTS status"""
        mock_response = {"status": "ZERO_RESULTS"}

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

    def test_get_directions_error_invalid_request(self, api_key):
        """Test get_directions with INVALID_REQUEST status"""
        mock_response = {
            "status": "INVALID_REQUEST",
            "error_message": "Invalid request"
        }

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            with pytest.raises(InvalidRequestError):
                client.get_directions("Toronto", "Montreal")
            client.close()

    def test_get_directions_json_convenience(self, api_key):
        """Test get_directions_json convenience method"""
        mock_response = {"status": "OK", "routes": []}

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                json=mock_response,
                status_code=200
            )

            client = DirectionsClient(api_key)
            result = client.get_directions_json("Toronto", "Montreal")

            assert result["status"] == "OK"
            client.close()

    def test_get_directions_xml_convenience(self, api_key):
        """Test get_directions_xml convenience method"""
        xml_content = "<DirectionsResponse><status>OK</status></DirectionsResponse>"

        with requests_mock.Mocker() as m:
            m.get(
                "https://maps.googleapis.com/maps/api/directions/xml",
                text=xml_content,
                status_code=200
            )

            client = DirectionsClient(api_key)
            result = client.get_directions_xml("Toronto", "Montreal")

            # XML response should be in 'raw' field
            assert result is not None
            client.close()

