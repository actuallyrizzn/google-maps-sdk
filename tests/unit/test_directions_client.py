"""
Unit tests for DirectionsClient
"""

import pytest
from unittest.mock import patch
from google_maps_sdk.directions import DirectionsClient


@pytest.mark.unit
class TestDirectionsClientInit:
    """Test DirectionsClient initialization"""

    def test_init(self, api_key):
        """Test initialization"""
        client = DirectionsClient(api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://maps.googleapis.com/maps/api/directions"
        assert client.timeout == 30
        client.close()

    def test_init_with_timeout(self, api_key):
        """Test initialization with custom timeout"""
        client = DirectionsClient(api_key, timeout=60)
        assert client.timeout == 60
        client.close()


@pytest.mark.unit
class TestDirectionsClientGetDirections:
    """Test DirectionsClient.get_directions method"""

    @patch("google_maps_sdk.directions.BaseClient._get")
    def test_get_directions_basic(self, mock_get, api_key):
        """Test basic get_directions call"""
        mock_get.return_value = {"status": "OK", "routes": []}
        
        client = DirectionsClient(api_key)
        result = client.get_directions("Toronto", "Montreal")

        assert result == {"status": "OK", "routes": []}
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "/json"
        assert call_args[1]["params"]["origin"] == "Toronto"
        assert call_args[1]["params"]["destination"] == "Montreal"
        assert call_args[1]["params"]["mode"] == "driving"
        client.close()

    @patch("google_maps_sdk.directions.BaseClient._get")
    def test_get_directions_with_all_params(self, mock_get, api_key):
        """Test get_directions with all parameters"""
        mock_get.return_value = {"status": "OK", "routes": []}
        
        client = DirectionsClient(api_key)
        result = client.get_directions(
            origin="Toronto",
            destination="Montreal",
            mode="transit",
            waypoints=["Ottawa", "Quebec"],
            alternatives=True,
            avoid=["tolls", "highways"],
            language="en",
            units="imperial",
            region="ca",
            departure_time="now",
            arrival_time=1234567890,
            traffic_model="best_guess",
            transit_mode=["bus", "subway"],
            transit_routing_preference="less_walking",
            output_format="json"
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["origin"] == "Toronto"
        assert params["destination"] == "Montreal"
        assert params["mode"] == "transit"
        assert params["waypoints"] == "Ottawa|Quebec"
        assert params["alternatives"] == "true"
        assert params["avoid"] == "tolls|highways"
        assert params["language"] == "en"
        assert params["units"] == "imperial"
        assert params["region"] == "ca"
        assert params["departure_time"] == "now"
        assert params["arrival_time"] == "1234567890"
        assert params["traffic_model"] == "best_guess"
        assert params["transit_mode"] == "bus|subway"
        assert params["transit_routing_preference"] == "less_walking"
        client.close()

    @patch("google_maps_sdk.directions.BaseClient._get")
    def test_get_directions_departure_time_int(self, mock_get, api_key):
        """Test get_directions with integer departure_time"""
        mock_get.return_value = {"status": "OK", "routes": []}
        
        client = DirectionsClient(api_key)
        client.get_directions("Toronto", "Montreal", departure_time=1234567890)

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["departure_time"] == "1234567890"
        client.close()

    @patch("google_maps_sdk.directions.BaseClient._get")
    def test_get_directions_xml_format(self, mock_get, api_key):
        """Test get_directions with XML format"""
        mock_get.return_value = {"status": "OK", "raw": "<xml>...</xml>"}
        
        client = DirectionsClient(api_key)
        result = client.get_directions("Toronto", "Montreal", output_format="xml")

        call_args = mock_get.call_args
        assert call_args[0][0] == "/xml"
        client.close()


@pytest.mark.unit
class TestDirectionsClientConvenienceMethods:
    """Test DirectionsClient convenience methods"""

    @patch("google_maps_sdk.directions.DirectionsClient.get_directions")
    def test_get_directions_json(self, mock_get_directions, api_key):
        """Test get_directions_json convenience method"""
        mock_get_directions.return_value = {"status": "OK", "routes": []}
        
        client = DirectionsClient(api_key)
        result = client.get_directions_json("Toronto", "Montreal")

        mock_get_directions.assert_called_once_with(
            origin="Toronto",
            destination="Montreal",
            mode="driving",
            waypoints=None,
            alternatives=False,
            avoid=None,
            language=None,
            units=None,
            region=None,
            departure_time=None,
            arrival_time=None,
            traffic_model=None,
            transit_mode=None,
            transit_routing_preference=None,
            output_format="json"
        )
        client.close()

    @patch("google_maps_sdk.directions.DirectionsClient.get_directions")
    def test_get_directions_xml(self, mock_get_directions, api_key):
        """Test get_directions_xml convenience method"""
        mock_get_directions.return_value = {"status": "OK", "raw": "<xml>...</xml>"}
        
        client = DirectionsClient(api_key)
        result = client.get_directions_xml("Toronto", "Montreal")

        mock_get_directions.assert_called_once_with(
            origin="Toronto",
            destination="Montreal",
            mode="driving",
            waypoints=None,
            alternatives=False,
            avoid=None,
            language=None,
            units=None,
            region=None,
            departure_time=None,
            arrival_time=None,
            traffic_model=None,
            transit_mode=None,
            transit_routing_preference=None,
            output_format="xml"
        )
        client.close()





