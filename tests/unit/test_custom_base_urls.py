"""
Tests for custom base URLs for testing (issue #109)
"""

import pytest
from unittest.mock import Mock, patch
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.config import ClientConfig


class TestCustomBaseURLs:
    """Test custom base URL support for testing/staging"""
    
    def test_routes_client_custom_base_url(self):
        """Test RoutesClient with custom base URL"""
        test_base_url = "https://test-routes.googleapis.com"
        client = RoutesClient(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url
        )
        assert client.base_url == test_base_url
    
    def test_routes_client_custom_base_url_overrides_region(self):
        """Test that custom base_url takes precedence over region"""
        test_base_url = "https://staging-routes.googleapis.com"
        client = RoutesClient(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url,
            region="us-central1"
        )
        assert client.base_url == test_base_url
    
    def test_routes_client_region_when_no_base_url(self):
        """Test that region is used when base_url is not provided"""
        client = RoutesClient(
            api_key="test_key_12345678901234567890",
            region="us-central1"
        )
        assert client.base_url == "https://routes-us-central1.googleapis.com"
    
    def test_routes_client_default_when_no_base_url_no_region(self):
        """Test that default global URL is used when neither base_url nor region provided"""
        client = RoutesClient(
            api_key="test_key_12345678901234567890"
        )
        assert client.base_url == RoutesClient.BASE_URL_GLOBAL
    
    def test_roads_client_custom_base_url(self):
        """Test RoadsClient with custom base URL"""
        test_base_url = "https://test-roads.googleapis.com"
        client = RoadsClient(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url
        )
        # RoadsClient appends version to base_url, so check it starts with our base_url
        assert client.base_url.startswith(test_base_url)
    
    def test_roads_client_custom_base_url_overrides_region(self):
        """Test that custom base_url takes precedence over region in RoadsClient"""
        test_base_url = "https://staging-roads.googleapis.com"
        client = RoadsClient(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url,
            region="europe-west1"
        )
        assert client.base_url.startswith(test_base_url)
    
    def test_directions_client_custom_base_url(self):
        """Test DirectionsClient with custom base URL"""
        test_base_url = "https://test-maps.googleapis.com/maps/api/directions"
        client = DirectionsClient(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url
        )
        assert client.base_url == test_base_url
    
    def test_directions_client_default_when_no_base_url(self):
        """Test that DirectionsClient uses default when base_url not provided"""
        client = DirectionsClient(
            api_key="test_key_12345678901234567890"
        )
        assert client.base_url == DirectionsClient.BASE_URL
    
    def test_custom_base_url_via_client_config(self):
        """Test custom base_url via ClientConfig"""
        test_base_url = "https://test-routes.googleapis.com"
        config = ClientConfig(
            api_key="test_key_12345678901234567890",
            base_url=test_base_url
        )
        client = RoutesClient(config=config)
        assert client.base_url == test_base_url
    
    def test_custom_base_url_for_staging(self):
        """Test using custom base_url for staging environment"""
        staging_url = "https://staging-routes.googleapis.com"
        client = RoutesClient(
            api_key="test_key_12345678901234567890",
            base_url=staging_url
        )
        assert client.base_url == staging_url
    
    def test_custom_base_url_for_local_testing(self):
        """Test using custom base_url for local testing"""
        local_url = "http://localhost:8080"
        client = RoutesClient(
            api_key="test_key_12345678901234567890",
            base_url=local_url
        )
        assert client.base_url == local_url
    
    def test_custom_base_url_with_all_clients(self):
        """Test custom base_url works with all client types"""
        test_urls = {
            RoutesClient: "https://test-routes.googleapis.com",
            RoadsClient: "https://test-roads.googleapis.com",
            DirectionsClient: "https://test-maps.googleapis.com/maps/api/directions",
        }
        
        for client_class, test_url in test_urls.items():
            client = client_class(
                api_key="test_key_12345678901234567890",
                base_url=test_url
            )
            if client_class == RoadsClient:
                # RoadsClient appends version
                assert client.base_url.startswith(test_url)
            else:
                assert client.base_url == test_url
