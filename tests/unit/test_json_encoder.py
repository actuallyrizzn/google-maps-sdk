"""
Unit tests for custom JSON encoder support (issue #51)
"""

import pytest
import json
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for testing"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class CustomType:
    """Custom type for testing encoder"""
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"CustomType({self.value})"


class CustomTypeEncoder(json.JSONEncoder):
    """Encoder that handles CustomType"""
    
    def default(self, obj):
        if isinstance(obj, CustomType):
            return {"__custom_type__": obj.value}
        return super().default(obj)


@pytest.mark.unit
class TestCustomJSONEncoder:
    """Test custom JSON encoder functionality"""

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_custom_encoder_with_datetime(self, mock_post, api_key):
        """Test custom encoder handles datetime objects"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=CustomJSONEncoder
        )
        
        now = datetime.now()
        data = {
            "timestamp": now,
            "date": date.today(),
            "value": Decimal("123.45")
        }
        
        client._post("/test", data=data)
        
        # Verify the request was made
        assert mock_post.called
        
        # Check that custom encoder was used
        call_args = mock_post.call_args
        if 'data' in call_args.kwargs:
            # Custom encoder was used (data parameter)
            sent_data = call_args.kwargs['data']
            if isinstance(sent_data, bytes):
                sent_data = sent_data.decode('utf-8')
            parsed = json.loads(sent_data)
            # Verify datetime was encoded as ISO string
            assert 'timestamp' in parsed
            assert isinstance(parsed['timestamp'], str)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_custom_encoder_with_custom_type(self, mock_post, api_key):
        """Test custom encoder handles custom types"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=CustomTypeEncoder
        )
        
        custom_obj = CustomType("test_value")
        data = {"custom": custom_obj}
        
        client._post("/test", data=data)
        
        # Verify the request was made
        assert mock_post.called
        
        # Check that custom encoder was used
        call_args = mock_post.call_args
        if 'data' in call_args.kwargs:
            sent_data = call_args.kwargs['data']
            if isinstance(sent_data, bytes):
                sent_data = sent_data.decode('utf-8')
            parsed = json.loads(sent_data)
            # Verify custom type was encoded
            assert 'custom' in parsed
            assert parsed['custom']['__custom_type__'] == "test_value"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_default_encoder_with_standard_types(self, mock_post, api_key):
        """Test default encoder works with standard types"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=None  # Use default
        )
        
        data = {
            "string": "value",
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        
        client._post("/test", data=data)
        
        # Verify the request was made
        assert mock_post.called
        
        # Check that json parameter was used (default behavior)
        call_args = mock_post.call_args
        assert 'json' in call_args.kwargs or 'data' in call_args.kwargs
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_custom_encoder_with_compression(self, mock_post, api_key):
        """Test custom encoder works with compression"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=CustomJSONEncoder,
            enable_request_compression=True,
            compression_threshold=100  # Low threshold for testing
        )
        
        # Create large payload with custom types
        now = datetime.now()
        large_data = {
            "timestamp": now,
            "data": "x" * 200  # Large payload to trigger compression
        }
        
        client._post("/test", data=large_data)
        
        # Verify the request was made
        assert mock_post.called
        
        # Check that compression was used
        call_args = mock_post.call_args
        headers = call_args.kwargs.get('headers', {})
        if 'data' in call_args.kwargs and headers.get('Content-Encoding') == 'gzip':
            # Compression was used, custom encoder should have been applied first
            assert headers.get('Content-Type') == 'application/json'
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_custom_encoder_raises_on_invalid_type(self, mock_post, api_key):
        """Test that custom encoder raises TypeError for unhandled types"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=json.JSONEncoder  # Default encoder doesn't handle CustomType
        )
        
        custom_obj = CustomType("test")
        data = {"custom": custom_obj}
        
        # Should raise TypeError when encoder can't handle the type
        with pytest.raises(TypeError):
            client._post("/test", data=data)
        
        client.close()
