"""
Configuration object for Google Maps Platform SDK (issue #75)
"""

from dataclasses import dataclass, field
from typing import Optional, Type
from requests.adapters import HTTPAdapter
from google_maps_sdk.retry import RetryConfig
from google_maps_sdk.circuit_breaker import CircuitBreaker


@dataclass
class ClientConfig:
    """
    Centralized configuration object for Google Maps Platform SDK clients
    
    This dataclass centralizes all client configuration options, making it easier
    to manage complex configurations and pass them around.
    
    Attributes:
        api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var)
        base_url: Base URL for the API (default: empty string)
        timeout: Request timeout in seconds (default: 30)
        api_version: API version string (e.g., "v1", "v2") (default: None, uses client default)
        region: Google Cloud region for regional endpoints (e.g., "us-central1", "europe-west1") (default: None for global) (issue #77)
        rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
        rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
        retry_config: Retry configuration (None to disable retries)
        enable_cache: Enable response caching (default: False)
        cache_ttl: Cache time-to-live in seconds (default: 300.0 = 5 minutes)
        cache_maxsize: Maximum number of cached responses (default: 100)
        http_adapter: Custom HTTPAdapter for proxies, custom SSL, etc. (None to use default)
        circuit_breaker: CircuitBreaker instance for failure protection (None to disable)
        enable_request_compression: Enable gzip compression for large POST requests (default: False)
        compression_threshold: Minimum payload size in bytes to compress (default: 1024)
        json_encoder: Custom JSON encoder class for encoding request data (None to use default)
    """
    api_key: Optional[str] = None
    base_url: str = ""
    timeout: int = 30
    api_version: Optional[str] = None
    region: Optional[str] = None
    rate_limit_max_calls: Optional[int] = None
    rate_limit_period: Optional[float] = None
    retry_config: Optional[RetryConfig] = None
    enable_cache: bool = False
    cache_ttl: float = 300.0
    cache_maxsize: int = 100
    http_adapter: Optional[HTTPAdapter] = None
    circuit_breaker: Optional[CircuitBreaker] = None
    enable_request_compression: bool = False
    compression_threshold: int = 1024
    json_encoder: Optional[Type] = None
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'api_version': self.api_version,
            'region': self.region,
            'rate_limit_max_calls': self.rate_limit_max_calls,
            'rate_limit_period': self.rate_limit_period,
            'retry_config': self.retry_config,
            'enable_cache': self.enable_cache,
            'cache_ttl': self.cache_ttl,
            'cache_maxsize': self.cache_maxsize,
            'http_adapter': self.http_adapter,
            'circuit_breaker': self.circuit_breaker,
            'enable_request_compression': self.enable_request_compression,
            'compression_threshold': self.compression_threshold,
            'json_encoder': self.json_encoder,
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ClientConfig':
        """
        Create configuration from dictionary
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            ClientConfig instance
        """
        return cls(**config_dict)
    
    def copy(self) -> 'ClientConfig':
        """
        Create a copy of the configuration
        
        Returns:
            New ClientConfig instance with same values
        """
        return ClientConfig(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            api_version=self.api_version,
            region=self.region,
            rate_limit_max_calls=self.rate_limit_max_calls,
            rate_limit_period=self.rate_limit_period,
            retry_config=self.retry_config,
            enable_cache=self.enable_cache,
            cache_ttl=self.cache_ttl,
            cache_maxsize=self.cache_maxsize,
            http_adapter=self.http_adapter,
            circuit_breaker=self.circuit_breaker,
            enable_request_compression=self.enable_request_compression,
            compression_threshold=self.compression_threshold,
            json_encoder=self.json_encoder,
        )
