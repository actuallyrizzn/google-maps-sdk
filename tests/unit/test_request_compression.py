"""
Unit tests for request compression (issue #49)
"""

import pytest
import gzip
import json
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient


@pytest.mark.unit
class TestRequestCompression:
    """Test request compression functionality"""

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_compression_enabled_large_payload(self, mock_post, api_key):
        """Test compression is applied for large payloads"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=True,
            compression_threshold=100  # Low threshold for testing
        )
        
        # Create large payload
        large_data = {"key": "x" * 200}  # > 100 bytes when JSON encoded
        
        client._post("/test", data=large_data)
        
        # Verify compression was used
        call_args = mock_post.call_args
        assert call_args is not None
        
        # Check that data was passed (not json parameter)
        assert 'data' in call_args.kwargs or 'json' in call_args.kwargs
        
        # Check Content-Encoding header
        headers = call_args.kwargs.get('headers', {})
        if 'data' in call_args.kwargs:
            # Compressed data was used
            assert headers.get('Content-Encoding') == 'gzip'
            assert headers.get('Content-Type') == 'application/json'
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_compression_disabled(self, mock_post, api_key):
        """Test compression is not applied when disabled"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=False
        )
        
        large_data = {"key": "x" * 200}
        
        client._post("/test", data=large_data)
        
        # Verify json parameter was used (not compressed)
        call_args = mock_post.call_args
        assert 'json' in call_args.kwargs
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_compression_small_payload(self, mock_post, api_key):
        """Test compression is not applied for small payloads"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=True,
            compression_threshold=1024  # 1KB threshold
        )
        
        # Small payload
        small_data = {"key": "value"}
        
        client._post("/test", data=small_data)
        
        # Verify json parameter was used (not compressed)
        call_args = mock_post.call_args
        assert 'json' in call_args.kwargs
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_compression_verification(self, mock_post, api_key):
        """Test that compressed data is actually gzip compressed"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=True,
            compression_threshold=100
        )
        
        large_data = {"key": "x" * 200}
        
        client._post("/test", data=large_data)
        
        call_args = mock_post.call_args
        if 'data' in call_args.kwargs:
            compressed_data = call_args.kwargs['data']
            # Verify it's actually gzip compressed
            decompressed = gzip.decompress(compressed_data)
            decoded = json.loads(decompressed.decode('utf-8'))
            assert decoded == large_data
        
        client.close()
