"""
Unit tests for API versioning (issue #270 / #76)
"""

import pytest
from unittest.mock import patch, MagicMock
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.utils import validate_api_version
from google_maps_sdk.config import ClientConfig


@pytest.mark.unit
class TestAPIVersioning:
    """Test API versioning support"""

    def test_validate_api_version_valid(self):
        """Test validation of valid API versions"""
        assert validate_api_version("v1") == "v1"
        assert validate_api_version("v2") == "v2"
        assert validate_api_version("v3") == "v3"
        assert validate_api_version("V1") == "v1"  # Case normalization
        assert validate_api_version("V2") == "v2"

    def test_validate_api_version_none(self):
        """Test validation with None"""
        assert validate_api_version(None) is None

    def test_validate_api_version_invalid(self):
        """Test validation of invalid API versions"""
        with pytest.raises(ValueError, match="Invalid API version format"):
            validate_api_version("1")
        
        with pytest.raises(ValueError, match="Invalid API version format"):
            validate_api_version("version1")
        
        with pytest.raises(ValueError, match="Invalid API version format"):
            validate_api_version("v")
        
        with pytest.raises(ValueError, match="Invalid API version format"):
            validate_api_version("v1.0")
        
        with pytest.raises(ValueError, match="Invalid API version format"):
            validate_api_version("v1.2.3")

    def test_validate_api_version_empty(self):
        """Test validation with empty string"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_api_version("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_api_version("   ")

    def test_validate_api_version_type(self):
        """Test validation with wrong type"""
        with pytest.raises(TypeError, match="must be a string"):
            validate_api_version(1)
        
        with pytest.raises(TypeError, match="must be a string"):
            validate_api_version([])

    def test_routes_client_default_version(self, api_key):
        """Test RoutesClient uses default v2 version"""
        client = RoutesClient(api_key)
        assert client._api_version == "v2"
        client.close()

    def test_routes_client_custom_version(self, api_key):
        """Test RoutesClient with custom version"""
        client = RoutesClient(api_key, api_version="v3")
        assert client._api_version == "v3"
        client.close()

    def test_routes_client_compute_routes_endpoint(self, api_key, sample_origin, sample_destination):
        """Test RoutesClient compute_routes uses correct version in endpoint"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"routes": []}
            mock_response.url = "https://routes.googleapis.com/test"
            mock_post.return_value = mock_response
            
            client = RoutesClient(api_key, api_version="v3")
            
            client.compute_routes(sample_origin, sample_destination)
            
            # Verify endpoint includes version
            call_args = mock_post.call_args
            url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
            assert "/directions/v3:computeRoutes" in url
            
            client.close()

    def test_routes_client_compute_route_matrix_endpoint(self, api_key, sample_origin, sample_destination):
        """Test RoutesClient compute_route_matrix uses correct version in endpoint"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_response = {
                "routeMatrixElements": []
            }
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                url="https://routes.googleapis.com/test"
            )
            
            client = RoutesClient(api_key, api_version="v3")
            
            client.compute_route_matrix([sample_origin], [sample_destination])
            
            # Verify endpoint includes version
            call_args = mock_post.call_args
            url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
            assert "/distanceMatrix/v3:computeRouteMatrix" in url
            
            client.close()

    def test_roads_client_default_version(self, api_key):
        """Test RoadsClient uses default v1 version"""
        client = RoadsClient(api_key)
        assert client._api_version == "v1"
        assert "/v1" in client.base_url
        client.close()

    def test_roads_client_custom_version(self, api_key):
        """Test RoadsClient with custom version"""
        client = RoadsClient(api_key, api_version="v2")
        assert client._api_version == "v2"
        assert "/v2" in client.base_url
        client.close()

    def test_roads_client_endpoints_with_version(self, api_key):
        """Test RoadsClient endpoints use correct version"""
        from unittest.mock import patch
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"snappedPoints": []}
            mock_response.url = "https://roads.googleapis.com/test"
            mock_get.return_value = mock_response
            
            client = RoadsClient(api_key, api_version="v2")
            
            path = [(60.170880, 24.942795)]
            client.snap_to_roads(path)
            
            # Verify base URL includes version
            assert client.base_url == "https://roads.googleapis.com/v2"
            
            client.close()

    def test_api_version_in_client_config(self, api_key):
        """Test API version in ClientConfig"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            api_version="v3"
        )
        
        assert config.api_version == "v3"
        
        # Test with RoutesClient
        client = RoutesClient(config=config)
        assert client._api_version == "v3"
        client.close()

    def test_api_version_config_precedence(self, api_key):
        """Test that config api_version takes precedence"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://routes.googleapis.com",
            api_version="v3"
        )
        
        # Pass both config and individual parameter
        # Config should take precedence
        client = RoutesClient(api_key=api_key, api_version="v2", config=config)
        assert client._api_version == "v3"
        client.close()

    def test_routes_client_version_validation(self, api_key):
        """Test RoutesClient validates API version format"""
        with pytest.raises(ValueError, match="Invalid API version format"):
            RoutesClient(api_key, api_version="invalid")

    def test_roads_client_version_validation(self, api_key):
        """Test RoadsClient validates API version format"""
        with pytest.raises(ValueError, match="Invalid API version format"):
            RoadsClient(api_key, api_version="invalid")

    def test_api_version_case_insensitive(self, api_key):
        """Test API version is case-insensitive (normalized to lowercase)"""
        client = RoutesClient(api_key, api_version="V2")
        assert client._api_version == "v2"
        client.close()
        
        client = RoadsClient(api_key, api_version="V1")
        assert client._api_version == "v1"
        client.close()

    def test_api_version_with_all_clients(self, api_key):
        """Test API versioning with all client types"""
        # RoutesClient
        routes_client = RoutesClient(api_key, api_version="v2")
        assert routes_client._api_version == "v2"
        routes_client.close()
        
        # RoadsClient
        roads_client = RoadsClient(api_key, api_version="v1")
        assert roads_client._api_version == "v1"
        roads_client.close()
        
        # DirectionsClient (legacy, no version support yet)
        directions_client = DirectionsClient(api_key)
        # Directions API doesn't have version in path currently
        directions_client.close()

    def test_api_version_backward_compatibility(self, api_key):
        """Test that default versions maintain backward compatibility"""
        # RoutesClient should default to v2
        client = RoutesClient(api_key)
        assert client._api_version == "v2"
        client.close()
        
        # RoadsClient should default to v1
        client = RoadsClient(api_key)
        assert client._api_version == "v1"
        client.close()

    def test_api_version_in_config_dict(self):
        """Test API version in config dictionary"""
        config = ClientConfig(api_version="v3")
        config_dict = config.to_dict()
        
        assert 'api_version' in config_dict
        assert config_dict['api_version'] == "v3"

    def test_api_version_from_config_dict(self):
        """Test creating config from dict with API version"""
        config_dict = {
            'api_version': 'v3'
        }
        
        config = ClientConfig.from_dict(config_dict)
        assert config.api_version == 'v3'

    def test_api_version_copy(self):
        """Test API version is copied correctly"""
        original = ClientConfig(api_version="v2")
        copied = original.copy()
        
        assert copied.api_version == original.api_version
        
        # Modify copy
        copied.api_version = "v3"
        assert original.api_version == "v2"
        assert copied.api_version == "v3"

    def test_routes_client_multiple_versions(self, api_key, sample_origin, sample_destination):
        """Test RoutesClient with different versions"""
        from unittest.mock import patch
        
        versions = ["v1", "v2", "v3"]
        
        for version in versions:
            with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"routes": []}
                mock_response.url = "https://routes.googleapis.com/test"
                mock_post.return_value = mock_response
                
                client = RoutesClient(api_key, api_version=version)
                assert client._api_version == version
                
                client.compute_routes(sample_origin, sample_destination)
                
                # Verify endpoint uses correct version
                call_args = mock_post.call_args
                url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
                assert f"/directions/{version}:computeRoutes" in url
                
                client.close()

    def test_roads_client_multiple_versions(self, api_key):
        """Test RoadsClient with different versions"""
        versions = ["v1", "v2"]
        
        for version in versions:
            client = RoadsClient(api_key, api_version=version)
            assert client._api_version == version
            assert f"/{version}" in client.base_url
            client.close()

    def test_api_version_with_config_object(self, api_key):
        """Test API versioning using ClientConfig object"""
        config = ClientConfig(
            api_key=api_key,
            base_url="https://routes.googleapis.com",
            api_version="v3"
        )
        
        client = RoutesClient(config=config)
        assert client._api_version == "v3"
        client.close()

    def test_api_version_none_uses_default(self, api_key):
        """Test that None api_version uses client default"""
        # RoutesClient
        client = RoutesClient(api_key, api_version=None)
        assert client._api_version == "v2"  # Default
        client.close()
        
        # RoadsClient
        client = RoadsClient(api_key, api_version=None)
        assert client._api_version == "v1"  # Default
        client.close()

    def test_api_version_validation_error_messages(self):
        """Test API version validation error messages"""
        with pytest.raises(ValueError, match="Invalid API version format.*Expected format"):
            validate_api_version("invalid")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_api_version("")
