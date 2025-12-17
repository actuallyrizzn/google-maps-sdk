"""
Unit tests for error handling separation (issue #272 / #78)
"""

import pytest
from unittest.mock import Mock, patch
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import (
    GoogleMapsAPIError,
    InvalidRequestError,
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
)
from google_maps_sdk.response_types import XMLResponse, NonJSONResponse


@pytest.mark.unit
class TestErrorHandlingSeparation:
    """Test separation of error handling concerns"""

    def test_parse_response_json(self, api_key):
        """Test _parse_response with JSON response"""
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        
        client = BaseClient(api_key, "https://api.example.com")
        result = client._parse_response(mock_response)
        
        assert result == {"status": "OK", "data": "test"}
        client.close()

    def test_parse_response_xml(self, api_key):
        """Test _parse_response with XML response"""
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/xml'}
        mock_response.text = '<?xml version="1.0"?><root><status>OK</status></root>'
        mock_response.status_code = 200
        
        client = BaseClient(api_key, "https://api.example.com")
        result = client._parse_response(mock_response)
        
        assert isinstance(result, dict)
        assert "status" in result or "root" in result
        client.close()

    def test_parse_response_non_json(self, api_key):
        """Test _parse_response with non-JSON response"""
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "OK"
        mock_response.status_code = 200
        
        client = BaseClient(api_key, "https://api.example.com")
        result = client._parse_response(mock_response)
        
        assert isinstance(result, dict)
        assert "raw" in result or "status" in result
        client.close()

    def test_check_http_errors_no_error(self, api_key):
        """Test _check_http_errors with no error"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://api.example.com/test"
        mock_response.headers = {'Content-Type': 'application/json'}
        data = {"status": "OK"}
        
        client = BaseClient(api_key, "https://api.example.com")
        # Should not raise
        client._check_http_errors(mock_response, data)
        client.close()

    def test_check_http_errors_400(self, api_key):
        """Test _check_http_errors with 400 error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.url = "https://api.example.com/test"
        mock_response.headers = {'Content-Type': 'application/json'}
        data = {"error": {"message": "Bad request"}}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(InvalidRequestError):
            client._check_http_errors(mock_response, data)
        client.close()

    def test_check_http_errors_xml_error(self, api_key):
        """Test _check_http_errors with XML error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.url = "https://api.example.com/test"
        mock_response.headers = {'Content-Type': 'application/xml'}
        mock_response.text = "Error"
        data = {}  # XML parsed as empty dict
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError, match="XML error response"):
            client._check_http_errors(mock_response, data)
        client.close()

    def test_check_http_errors_non_json_error(self, api_key):
        """Test _check_http_errors with non-JSON error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.url = "https://api.example.com/test"
        mock_response.text = "Internal Server Error"
        data = "Internal Server Error"  # Not a dict
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError, match="HTTP 500"):
            client._check_http_errors(mock_response, data)
        client.close()

    def test_check_directions_api_errors_no_error(self, api_key):
        """Test _check_directions_api_errors with no error"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "OK"}
        
        client = BaseClient(api_key, "https://api.example.com")
        # Should not raise
        client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_request_denied(self, api_key):
        """Test _check_directions_api_errors with REQUEST_DENIED"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "REQUEST_DENIED", "error_message": "Access denied"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(PermissionDeniedError):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_over_query_limit(self, api_key):
        """Test _check_directions_api_errors with OVER_QUERY_LIMIT"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "OVER_QUERY_LIMIT", "error_message": "Quota exceeded"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(QuotaExceededError):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_not_found(self, api_key):
        """Test _check_directions_api_errors with NOT_FOUND"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "NOT_FOUND", "error_message": "Not found"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(NotFoundError):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_zero_results(self, api_key):
        """Test _check_directions_api_errors with ZERO_RESULTS"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "ZERO_RESULTS"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(NotFoundError, match="No results found"):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_invalid_request(self, api_key):
        """Test _check_directions_api_errors with INVALID_REQUEST"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "INVALID_REQUEST", "error_message": "Invalid request"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(InvalidRequestError):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_check_directions_api_errors_unknown_status(self, api_key):
        """Test _check_directions_api_errors with unknown status"""
        mock_response = Mock()
        mock_response.url = "https://api.example.com/test"
        data = {"status": "UNKNOWN_STATUS", "error_message": "Unknown error"}
        
        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError):
            client._check_directions_api_errors(data, mock_response)
        client.close()

    def test_handle_response_uses_separated_methods(self, api_key):
        """Test that _handle_response uses separated methods"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.url = "https://api.example.com/test"
        
        client = BaseClient(api_key, "https://api.example.com")
        
        # Mock the separated methods to verify they're called
        with patch.object(client, '_parse_response') as mock_parse, \
             patch.object(client, '_check_http_errors') as mock_http, \
             patch.object(client, '_check_directions_api_errors') as mock_directions:
            mock_parse.return_value = {"status": "OK", "data": "test"}
            
            result = client._handle_response(mock_response)
            
            # Verify methods were called
            mock_parse.assert_called_once_with(mock_response)
            mock_http.assert_called_once_with(mock_response, {"status": "OK", "data": "test"}, request_id=None)
            mock_directions.assert_called_once_with({"status": "OK", "data": "test"}, mock_response, request_id=None)
            assert result == {"status": "OK", "data": "test"}
        
        client.close()

    def test_separation_maintains_backward_compatibility(self, api_key):
        """Test that separation maintains backward compatibility"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.url = "https://api.example.com/test"
        
        client = BaseClient(api_key, "https://api.example.com")
        result = client._handle_response(mock_response)
        
        assert result == {"status": "OK", "data": "test"}
        client.close()

    def test_parse_response_raises_value_error_on_invalid_json(self, api_key):
        """Test _parse_response handles invalid JSON gracefully"""
        mock_response = Mock()
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON"
        mock_response.status_code = 200
        
        client = BaseClient(api_key, "https://api.example.com")
        # Should return NonJSONResponse dict, not raise
        result = client._parse_response(mock_response)
        assert isinstance(result, dict)
        client.close()
