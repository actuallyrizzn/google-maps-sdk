"""
Unit tests for RoutesClient
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.routes import RoutesClient


@pytest.mark.unit
class TestRoutesClientInit:
    """Test RoutesClient initialization"""

    def test_init(self, api_key):
        """Test initialization"""
        client = RoutesClient(api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://routes.googleapis.com"
        assert client.timeout == 30
        client.close()

    def test_init_with_timeout(self, api_key):
        """Test initialization with custom timeout"""
        client = RoutesClient(api_key, timeout=60)
        assert client.timeout == 60
        client.close()


@pytest.mark.unit
class TestRoutesClientComputeRoutes:
    """Test RoutesClient.compute_routes method"""

    @patch("google_maps_sdk.routes.BaseClient._post")
    def test_compute_routes_basic(self, mock_post, api_key, sample_origin, sample_destination):
        """Test basic compute_routes call"""
        mock_post.return_value = {"routes": []}
        
        client = RoutesClient(api_key)
        result = client.compute_routes(sample_origin, sample_destination)

        assert result == {"routes": []}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/directions/v2:computeRoutes"
        assert call_args[1]["data"]["origin"] == sample_origin
        assert call_args[1]["data"]["destination"] == sample_destination
        assert call_args[1]["data"]["travelMode"] == "DRIVE"
        client.close()

    @patch("google_maps_sdk.routes.BaseClient._post")
    def test_compute_routes_with_all_params(self, mock_post, api_key, sample_origin, sample_destination):
        """Test compute_routes with all parameters"""
        mock_post.return_value = {"routes": []}
        
        intermediates = [{"location": {"latLng": {"latitude": 37.415, "longitude": -122.080}}}]
        route_modifiers = {"avoidTolls": True, "avoidHighways": False}
        extra_computations = ["TOLLS", "FUEL_CONSUMPTION"]

        client = RoutesClient(api_key)
        result = client.compute_routes(
            origin=sample_origin,
            destination=sample_destination,
            intermediates=intermediates,
            travel_mode="WALK",
            routing_preference="TRAFFIC_AWARE",
            departure_time="now",
            compute_alternative_routes=True,
            route_modifiers=route_modifiers,
            language_code="en-US",
            units="IMPERIAL",
            optimize_waypoint_order=True,
            polyline_quality="HIGH_QUALITY",
            polyline_encoding="ENCODED_POLYLINE",
            extra_computations=extra_computations,
            field_mask="routes.duration,routes.distanceMeters"
        )

        call_args = mock_post.call_args
        data = call_args[1]["data"]
        assert data["intermediates"] == intermediates
        assert data["travelMode"] == "WALK"
        assert data["routingPreference"] == "TRAFFIC_AWARE"
        assert data["departureTime"] == "now"
        assert data["computeAlternativeRoutes"] is True
        assert data["routeModifiers"] == route_modifiers
        assert data["languageCode"] == "en-US"
        assert data["units"] == "IMPERIAL"
        assert data["optimizeWaypointOrder"] is True
        assert data["polylineQuality"] == "HIGH_QUALITY"
        assert data["polylineEncoding"] == "ENCODED_POLYLINE"
        assert data["extraComputations"] == extra_computations
        assert call_args[1]["headers"]["X-Goog-FieldMask"] == "routes.duration,routes.distanceMeters"
        client.close()

    @patch("google_maps_sdk.routes.BaseClient._post")
    def test_compute_routes_optional_params_none(self, mock_post, api_key, sample_origin, sample_destination):
        """Test compute_routes with optional params as None"""
        mock_post.return_value = {"routes": []}
        
        client = RoutesClient(api_key)
        client.compute_routes(sample_origin, sample_destination)

        call_args = mock_post.call_args
        data = call_args[1]["data"]
        assert "intermediates" not in data
        assert "routingPreference" not in data
        assert "departureTime" not in data
        assert "computeAlternativeRoutes" not in data
        assert "routeModifiers" not in data
        client.close()


@pytest.mark.unit
class TestRoutesClientComputeRouteMatrix:
    """Test RoutesClient.compute_route_matrix method"""

    @patch("google_maps_sdk.routes.BaseClient._post")
    def test_compute_route_matrix_basic(self, mock_post, api_key, sample_origin, sample_destination):
        """Test basic compute_route_matrix call"""
        mock_post.return_value = {"routeMatrixElements": []}
        
        origins = [sample_origin]
        destinations = [sample_destination]

        client = RoutesClient(api_key)
        result = client.compute_route_matrix(origins, destinations)

        assert result == {"routeMatrixElements": []}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "/distanceMatrix/v2:computeRouteMatrix"
        assert call_args[1]["data"]["origins"] == origins
        assert call_args[1]["data"]["destinations"] == destinations
        assert call_args[1]["data"]["travelMode"] == "DRIVE"
        client.close()

    @patch("google_maps_sdk.routes.BaseClient._post")
    def test_compute_route_matrix_with_all_params(self, mock_post, api_key, sample_origin, sample_destination):
        """Test compute_route_matrix with all parameters"""
        mock_post.return_value = {"routeMatrixElements": []}
        
        origins = [sample_origin]
        destinations = [sample_destination]
        extra_computations = ["TOLLS"]

        client = RoutesClient(api_key)
        result = client.compute_route_matrix(
            origins=origins,
            destinations=destinations,
            travel_mode="WALK",
            routing_preference="TRAFFIC_AWARE",
            departure_time="now",
            language_code="en-US",
            units="METRIC",
            extra_computations=extra_computations,
            field_mask="originIndex,destinationIndex,duration"
        )

        call_args = mock_post.call_args
        data = call_args[1]["data"]
        assert data["travelMode"] == "WALK"
        assert data["routingPreference"] == "TRAFFIC_AWARE"
        assert data["departureTime"] == "now"
        assert data["languageCode"] == "en-US"
        assert data["units"] == "METRIC"
        assert data["extraComputations"] == extra_computations
        assert call_args[1]["headers"]["X-Goog-FieldMask"] == "originIndex,destinationIndex,duration"
        client.close()



