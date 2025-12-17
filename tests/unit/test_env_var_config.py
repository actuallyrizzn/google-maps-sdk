"""
Unit tests for environment variable configuration (issue #31)
"""

import pytest
import os
from unittest.mock import patch
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.unit
class TestEnvironmentVariableConfig:
    """Test environment variable configuration"""

    def test_base_client_with_env_var(self):
        """Test BaseClient uses environment variable when api_key is None"""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'env_test_key_12345678901234567890'}):
            client = BaseClient(api_key=None, base_url="https://example.com")
            assert client._api_key == 'env_test_key_12345678901234567890'
            client.close()

    def test_base_client_with_explicit_key(self):
        """Test BaseClient prefers explicit api_key over environment variable"""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'env_key'}):
            client = BaseClient(api_key='explicit_key_12345678901234567890', base_url="https://example.com")
            assert client._api_key == 'explicit_key_12345678901234567890'
            client.close()

    def test_base_client_no_key_raises(self):
        """Test BaseClient raises error when no key provided and env var not set"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                BaseClient(api_key=None, base_url="https://example.com")

    def test_routes_client_with_env_var(self):
        """Test RoutesClient uses environment variable"""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'env_test_key_12345678901234567890'}):
            client = RoutesClient(api_key=None)
            assert client._api_key == 'env_test_key_12345678901234567890'
            client.close()

    def test_google_maps_client_with_env_var(self):
        """Test GoogleMapsClient uses environment variable"""
        with patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'env_test_key_12345678901234567890'}):
            client = GoogleMapsClient(api_key=None)
            assert client.api_key == 'env_test_key_12345678901234567890'
            assert client.routes._api_key == 'env_test_key_12345678901234567890'
            client.close()

    def test_google_maps_client_no_key_raises(self):
        """Test GoogleMapsClient raises error when no key provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                GoogleMapsClient(api_key=None)
