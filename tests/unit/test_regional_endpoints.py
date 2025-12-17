"""
Unit tests for regional endpoints (issue #271 / #77)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.utils import validate_region
from google_maps_sdk.config import ClientConfig


@pytest.mark.unit
class TestRegionalEndpoints:
    """Test regional endpoint support"""

    def test_validate_region_valid(self):
        """Test validation of valid regions"""
        assert validate_region("us-central1") == "us-central1"
        assert validate_region("europe-west1") == "europe-west1"
        assert validate_region("asia-east1") == "asia-east1"
        assert validate_region("US-CENTRAL1") == "us-central1"  # Case normalization
        assert validate_region("Europe-West1") == "europe-west1"

    def test_validate_region_none(self):
        """Test validation with None"""
        assert validate_region(None) is None

    def test_validate_region_invalid(self):
        """Test validation of invalid regions"""
        with pytest.raises(ValueError, match="Invalid region format"):
            validate_region("invalid")
        
        with pytest.raises(ValueError, match="Invalid region format"):
            validate_region("us")
        
        with pytest.raises(ValueError, match="Invalid region format"):
            validate_region("us-central")
        
        with pytest.raises(ValueError, match="Invalid region format"):
            validate_region("us_central1")

    def test_validate_region_empty(self):
        """Test validation with empty string"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_region("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_region("   ")

    def test_validate_region_type(self):
        """Test validation with wrong type"""
        with pytest.raises(TypeError, match="must be a string"):
            validate_region(1)
        
        with pytest.raises(TypeError, match="must be a string"):
            validate_region([])

    def test_routes_client_global_endpoint(self, api_key):
        """Test RoutesClient uses global endpoint by default"""
        client = RoutesClient(api_key)
        assert client.base_url == "https://routes.googleapis.com"
        assert client._region is None
        client.close()

    def test_routes_client_regional_endpoint(self, api_key):
        """Test RoutesClient with regional endpoint"""
        client = RoutesClient(api_key, region="us-central1")
        assert client.base_url == "https://routes-us-central1.googleapis.com"
        assert client._region == "us-central1"
        client.close()

    def test_routes_client_multiple_regions(self, api_key):
        """Test RoutesClient with different regions"""
        regions = ["us-central1", "europe-west1", "asia-east1"]
        
        for region in regions:
            client = RoutesClient(api_key, region=region)
            assert client.base_url == f"https://routes-{region}.googleapis.com"
            assert client._region == region
            client.close()

    def test_roads_client_global_endpoint(self, api_key):
        """Test RoadsClient uses global endpoint by default"""
        client = RoadsClient(api_key)
        assert "https://roads.googleapis.com" in client.base_url
        assert client._region is None
        client.close()

    def test_roads_client_regional_endpoint(self, api_key):
        """Test RoadsClient with regional endpoint"""
        client = RoadsClient(api_key, region="us-central1")
        assert client.base_url == "https://roads-us-central1.googleapis.com/v1"
        assert client._region == "us-central1"
        client.close()

    def test_roads_client_multiple_regions(self, api_key):
        """Test RoadsClient with different regions"""
        regions = ["us-central1", "europe-west1", "asia-east1"]
        
        for region in regions:
            client = RoadsClient(api_key, region=region)
            assert client.base_url == f"https://roads-{region}.googleapis.com/v1"
            assert client._region == region
            client.close()

    def test_region_in_client_config(self, api_key):
        """Test region in ClientConfig"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            region="us-central1"
        )
        
        assert config.region == "us-central1"
        
        # Test with RoutesClient
        client = RoutesClient(config=config)
        assert client.base_url == "https://routes-us-central1.googleapis.com"
        assert client._region == "us-central1"
        client.close()

    def test_region_config_precedence(self, api_key):
        """Test that config region takes precedence"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://routes.googleapis.com",
            region="europe-west1"
        )
        
        # Pass both config and individual parameter
        # Config should take precedence
        client = RoutesClient(api_key=api_key, region="us-central1", config=config)
        assert client.base_url == "https://routes-europe-west1.googleapis.com"
        assert client._region == "europe-west1"
        client.close()

    def test_routes_client_region_validation(self, api_key):
        """Test RoutesClient validates region format"""
        with pytest.raises(ValueError, match="Invalid region format"):
            RoutesClient(api_key, region="invalid")

    def test_roads_client_region_validation(self, api_key):
        """Test RoadsClient validates region format"""
        with pytest.raises(ValueError, match="Invalid region format"):
            RoadsClient(api_key, region="invalid")

    def test_region_case_insensitive(self, api_key):
        """Test region is case-insensitive (normalized to lowercase)"""
        client = RoutesClient(api_key, region="US-CENTRAL1")
        assert client._region == "us-central1"
        assert "us-central1" in client.base_url
        client.close()
        
        client = RoadsClient(api_key, region="EUROPE-WEST1")
        assert client._region == "europe-west1"
        assert "europe-west1" in client.base_url
        client.close()

    def test_region_with_api_version(self, api_key):
        """Test region works with API version"""
        client = RoutesClient(api_key, region="us-central1", api_version="v2")
        assert client.base_url == "https://routes-us-central1.googleapis.com"
        assert client._api_version == "v2"
        assert client._region == "us-central1"
        client.close()
        
        client = RoadsClient(api_key, region="europe-west1", api_version="v1")
        assert client.base_url == "https://roads-europe-west1.googleapis.com/v1"
        assert client._api_version == "v1"
        assert client._region == "europe-west1"
        client.close()

    def test_region_backward_compatibility(self, api_key):
        """Test that None region maintains backward compatibility"""
        # RoutesClient should default to global
        client = RoutesClient(api_key)
        assert client.base_url == "https://routes.googleapis.com"
        assert client._region is None
        client.close()
        
        # RoadsClient should default to global
        client = RoadsClient(api_key)
        assert "https://roads.googleapis.com" in client.base_url
        assert client._region is None
        client.close()

    def test_region_in_config_dict(self):
        """Test region in config dictionary"""
        config = ClientConfig(region="us-central1")
        config_dict = config.to_dict()
        
        assert 'region' in config_dict
        assert config_dict['region'] == "us-central1"

    def test_region_from_config_dict(self):
        """Test creating config from dict with region"""
        config_dict = {
            'region': 'europe-west1'
        }
        
        config = ClientConfig.from_dict(config_dict)
        assert config.region == 'europe-west1'

    def test_region_copy(self):
        """Test region is copied correctly"""
        original = ClientConfig(region="us-central1")
        copied = original.copy()
        
        assert copied.region == original.region
        
        # Modify copy
        copied.region = "europe-west1"
        assert original.region == "us-central1"
        assert copied.region == "europe-west1"

    def test_routes_client_regional_endpoint_requests(self, api_key, sample_origin, sample_destination):
        """Test RoutesClient makes requests to regional endpoint"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"routes": []}
            mock_response.url = "https://routes-us-central1.googleapis.com/test"
            mock_post.return_value = mock_response
            
            client = RoutesClient(api_key, region="us-central1")
            
            client.compute_routes(sample_origin, sample_destination)
            
            # Verify request was made to regional endpoint
            call_args = mock_post.call_args
            url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
            assert "routes-us-central1.googleapis.com" in url
            
            client.close()

    def test_roads_client_regional_endpoint_requests(self, api_key):
        """Test RoadsClient makes requests to regional endpoint"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"snappedPoints": []}
            mock_response.url = "https://roads-europe-west1.googleapis.com/test"
            mock_get.return_value = mock_response
            
            client = RoadsClient(api_key, region="europe-west1")
            
            path = [(60.170880, 24.942795)]
            client.snap_to_roads(path)
            
            # Verify request was made to regional endpoint
            call_args = mock_get.call_args
            url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
            assert "roads-europe-west1.googleapis.com" in url
            
            client.close()

    def test_region_with_config_object(self, api_key):
        """Test regional endpoints using ClientConfig object"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://routes.googleapis.com",
            region="us-central1"
        )
        
        client = RoutesClient(config=config)
        assert client.base_url == "https://routes-us-central1.googleapis.com"
        assert client._region == "us-central1"
        client.close()

    def test_region_none_uses_global(self, api_key):
        """Test that None region uses global endpoint"""
        # RoutesClient
        client = RoutesClient(api_key, region=None)
        assert client.base_url == "https://routes.googleapis.com"
        assert client._region is None
        client.close()
        
        # RoadsClient
        client = RoadsClient(api_key, region=None)
        assert "https://roads.googleapis.com" in client.base_url
        assert client._region is None
        client.close()

    def test_region_validation_error_messages(self):
        """Test region validation error messages"""
        with pytest.raises(ValueError, match="Invalid region format.*Expected format"):
            validate_region("invalid")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_region("")

    def test_region_with_all_features(self, api_key):
        """Test region with all client features"""
        from google_maps_sdk.retry import RetryConfig
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        config = ClientConfig(
            api_key=api_key,
            region="us-central1",
            api_version="v2",
            timeout=60,
            enable_cache=True,
            retry_config=RetryConfig(max_retries=3),
            circuit_breaker=CircuitBreaker(failure_threshold=5),
        )
        
        client = RoutesClient(config=config)
        assert client.base_url == "https://routes-us-central1.googleapis.com"
        assert client._region == "us-central1"
        assert client._api_version == "v2"
        client.close()
