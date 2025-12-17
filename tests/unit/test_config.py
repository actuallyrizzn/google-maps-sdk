"""
Unit tests for ClientConfig (issue #269 / #75)
"""

import pytest
from google_maps_sdk.config import ClientConfig
from google_maps_sdk.retry import RetryConfig
from google_maps_sdk.circuit_breaker import CircuitBreaker
from requests.adapters import HTTPAdapter
import json


@pytest.mark.unit
class TestClientConfig:
    """Test ClientConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = ClientConfig()
        
        assert config.api_key is None
        assert config.base_url == ""
        assert config.timeout == 30
        assert config.rate_limit_max_calls is None
        assert config.rate_limit_period is None
        assert config.retry_config is None
        assert config.enable_cache is False
        assert config.cache_ttl == 300.0
        assert config.cache_maxsize == 100
        assert config.http_adapter is None
        assert config.circuit_breaker is None
        assert config.enable_request_compression is False
        assert config.compression_threshold == 1024
        assert config.json_encoder is None

    def test_custom_config(self):
        """Test custom configuration values"""
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
        http_adapter = HTTPAdapter()
        
        config = ClientConfig(
            api_key="test_key",
            base_url="https://example.com",
            timeout=60,
            rate_limit_max_calls=100,
            rate_limit_period=60.0,
            retry_config=retry_config,
            enable_cache=True,
            cache_ttl=600.0,
            cache_maxsize=200,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
            enable_request_compression=True,
            compression_threshold=2048,
        )
        
        assert config.api_key == "test_key"
        assert config.base_url == "https://example.com"
        assert config.timeout == 60
        assert config.rate_limit_max_calls == 100
        assert config.rate_limit_period == 60.0
        assert config.retry_config == retry_config
        assert config.enable_cache is True
        assert config.cache_ttl == 600.0
        assert config.cache_maxsize == 200
        assert config.http_adapter == http_adapter
        assert config.circuit_breaker == circuit_breaker
        assert config.enable_request_compression is True
        assert config.compression_threshold == 2048

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        config = ClientConfig(
            api_key="test_key",
            base_url="https://example.com",
            timeout=60,
            retry_config=retry_config,
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['api_key'] == "test_key"
        assert config_dict['base_url'] == "https://example.com"
        assert config_dict['timeout'] == 60
        assert config_dict['retry_config'] == retry_config

    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        config_dict = {
            'api_key': 'test_key',
            'base_url': 'https://example.com',
            'timeout': 60,
            'retry_config': retry_config,
            'enable_cache': True,
        }
        
        config = ClientConfig.from_dict(config_dict)
        
        assert config.api_key == 'test_key'
        assert config.base_url == 'https://example.com'
        assert config.timeout == 60
        assert config.retry_config == retry_config
        assert config.enable_cache is True

    def test_config_copy(self):
        """Test copying configuration"""
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        original = ClientConfig(
            api_key="test_key",
            base_url="https://example.com",
            timeout=60,
            retry_config=retry_config,
            enable_cache=True,
        )
        
        copied = original.copy()
        
        assert copied.api_key == original.api_key
        assert copied.base_url == original.base_url
        assert copied.timeout == original.timeout
        assert copied.retry_config == original.retry_config
        assert copied.enable_cache == original.enable_cache
        
        # Modify copy and verify original unchanged
        copied.timeout = 120
        assert original.timeout == 60

    def test_config_with_base_client(self, api_key):
        """Test using config with BaseClient"""
        from google_maps_sdk.base_client import BaseClient
        
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            timeout=60,
            enable_cache=True,
        )
        
        client = BaseClient(config=config)
        
        assert client.base_url == "https://example.com"
        assert client.timeout == 60
        assert client._cache is not None
        
        client.close()

    def test_config_precedence_over_parameters(self, api_key):
        """Test that config parameter takes precedence over individual parameters"""
        from google_maps_sdk.base_client import BaseClient
        
        config = ClientConfig(
            api_key=api_key,
            base_url="https://config.example.com",
            timeout=90,
        )
        
        # Pass both config and individual parameters
        # Config should take precedence
        client = BaseClient(
            api_key=api_key,
            base_url="https://param.example.com",
            timeout=30,
            config=config
        )
        
        assert client.base_url == "https://config.example.com"
        assert client.timeout == 90
        
        client.close()

    def test_config_with_retry_config(self, api_key):
        """Test config with retry configuration"""
        from google_maps_sdk.base_client import BaseClient
        
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            retry_config=retry_config,
        )
        
        client = BaseClient(config=config)
        
        assert client._retry_config == retry_config
        
        client.close()

    def test_config_with_circuit_breaker(self, api_key):
        """Test config with circuit breaker"""
        from google_maps_sdk.base_client import BaseClient
        
        circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            circuit_breaker=circuit_breaker,
        )
        
        client = BaseClient(config=config)
        
        assert client._circuit_breaker == circuit_breaker
        
        client.close()

    def test_config_with_http_adapter(self, api_key):
        """Test config with HTTP adapter"""
        from google_maps_sdk.base_client import BaseClient
        
        http_adapter = HTTPAdapter(pool_connections=5, pool_maxsize=10)
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            http_adapter=http_adapter,
        )
        
        client = BaseClient(config=config)
        
        assert client._http_adapter == http_adapter
        
        client.close()

    def test_config_with_custom_json_encoder(self, api_key):
        """Test config with custom JSON encoder"""
        from google_maps_sdk.base_client import BaseClient
        from datetime import datetime
        
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            json_encoder=CustomEncoder,
        )
        
        client = BaseClient(config=config)
        
        assert client._json_encoder == CustomEncoder
        
        client.close()

    def test_config_with_all_options(self, api_key):
        """Test config with all options enabled"""
        from google_maps_sdk.base_client import BaseClient
        
        retry_config = RetryConfig(max_retries=3, base_delay=1.0)
        circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
        http_adapter = HTTPAdapter()
        
        config = ClientConfig(
            api_key=api_key,
            base_url="https://example.com",
            timeout=60,
            rate_limit_max_calls=100,
            rate_limit_period=60.0,
            retry_config=retry_config,
            enable_cache=True,
            cache_ttl=600.0,
            cache_maxsize=200,
            http_adapter=http_adapter,
            circuit_breaker=circuit_breaker,
            enable_request_compression=True,
            compression_threshold=2048,
        )
        
        client = BaseClient(config=config)
        
        assert client.base_url == "https://example.com"
        assert client.timeout == 60
        assert client._retry_config == retry_config
        assert client._cache is not None
        assert client._circuit_breaker == circuit_breaker
        assert client._http_adapter == http_adapter
        assert client._enable_request_compression is True
        assert client._compression_threshold == 2048
        
        client.close()

    def test_config_immutability_after_copy(self):
        """Test that copied config is independent"""
        original = ClientConfig(
            api_key="original_key",
            timeout=30,
        )
        
        copied = original.copy()
        copied.api_key = "new_key"
        copied.timeout = 60
        
        assert original.api_key == "original_key"
        assert original.timeout == 30
        assert copied.api_key == "new_key"
        assert copied.timeout == 60

    def test_config_with_none_values(self):
        """Test config with None values"""
        config = ClientConfig(
            api_key=None,
            retry_config=None,
            circuit_breaker=None,
            http_adapter=None,
            json_encoder=None,
        )
        
        assert config.api_key is None
        assert config.retry_config is None
        assert config.circuit_breaker is None
        assert config.http_adapter is None
        assert config.json_encoder is None

    def test_config_dict_serialization(self):
        """Test config dictionary serialization"""
        config = ClientConfig(
            api_key="test_key",
            base_url="https://example.com",
            timeout=60,
            enable_cache=True,
        )
        
        config_dict = config.to_dict()
        
        # Verify all fields are present
        assert 'api_key' in config_dict
        assert 'base_url' in config_dict
        assert 'timeout' in config_dict
        assert 'enable_cache' in config_dict
        assert 'cache_ttl' in config_dict
        assert 'cache_maxsize' in config_dict

    def test_config_from_dict_with_partial_values(self):
        """Test creating config from dictionary with partial values"""
        config_dict = {
            'api_key': 'test_key',
            'timeout': 60,
        }
        
        config = ClientConfig.from_dict(config_dict)
        
        assert config.api_key == 'test_key'
        assert config.timeout == 60
        # Other values should use defaults
        assert config.base_url == ""
        assert config.enable_cache is False
