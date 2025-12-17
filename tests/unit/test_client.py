"""
Unit tests for GoogleMapsClient
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.unit
class TestGoogleMapsClientInit:
    """Test GoogleMapsClient initialization"""

    @patch("google_maps_sdk.client.RoutesClient")
    @patch("google_maps_sdk.client.DirectionsClient")
    @patch("google_maps_sdk.client.RoadsClient")
    def test_init(self, mock_roads, mock_directions, mock_routes, api_key):
        """Test initialization"""
        client = GoogleMapsClient(api_key)
        
        assert client.api_key == api_key
        assert client.timeout == 30
        assert client.routes is not None
        assert client.directions is not None
        assert client.roads is not None
        
        # Verify sub-clients were initialized
        mock_routes.assert_called_once_with(api_key, 30)
        mock_directions.assert_called_once_with(api_key, 30)
        mock_roads.assert_called_once_with(api_key, 30)
        
        client.close()

    @patch("google_maps_sdk.client.RoutesClient")
    @patch("google_maps_sdk.client.DirectionsClient")
    @patch("google_maps_sdk.client.RoadsClient")
    def test_init_with_timeout(self, mock_roads, mock_directions, mock_routes, api_key):
        """Test initialization with custom timeout"""
        client = GoogleMapsClient(api_key, timeout=60)
        
        assert client.timeout == 60
        mock_routes.assert_called_once_with(api_key, 60)
        mock_directions.assert_called_once_with(api_key, 60)
        mock_roads.assert_called_once_with(api_key, 60)
        
        client.close()


@pytest.mark.unit
class TestGoogleMapsClientClose:
    """Test GoogleMapsClient.close method"""

    @patch("google_maps_sdk.client.RoutesClient")
    @patch("google_maps_sdk.client.DirectionsClient")
    @patch("google_maps_sdk.client.RoadsClient")
    def test_close(self, mock_roads, mock_directions, mock_routes, api_key):
        """Test close method"""
        mock_routes_instance = MagicMock()
        mock_directions_instance = MagicMock()
        mock_roads_instance = MagicMock()
        
        mock_routes.return_value = mock_routes_instance
        mock_directions.return_value = mock_directions_instance
        mock_roads.return_value = mock_roads_instance
        
        client = GoogleMapsClient(api_key)
        client.close()
        
        mock_routes_instance.close.assert_called_once()
        mock_directions_instance.close.assert_called_once()
        mock_roads_instance.close.assert_called_once()


@pytest.mark.unit
class TestGoogleMapsClientContextManager:
    """Test GoogleMapsClient context manager"""

    @patch("google_maps_sdk.client.RoutesClient")
    @patch("google_maps_sdk.client.DirectionsClient")
    @patch("google_maps_sdk.client.RoadsClient")
    def test_context_manager(self, mock_roads, mock_directions, mock_routes, api_key):
        """Test using GoogleMapsClient as context manager"""
        mock_routes_instance = MagicMock()
        mock_directions_instance = MagicMock()
        mock_roads_instance = MagicMock()
        
        mock_routes.return_value = mock_routes_instance
        mock_directions.return_value = mock_directions_instance
        mock_roads.return_value = mock_roads_instance
        
        with GoogleMapsClient(api_key) as client:
            assert client.api_key == api_key
            assert client.routes is not None
            assert client.directions is not None
            assert client.roads is not None
        
        # Verify close was called on all sub-clients
        mock_routes_instance.close.assert_called_once()
        mock_directions_instance.close.assert_called_once()
        mock_roads_instance.close.assert_called_once()





