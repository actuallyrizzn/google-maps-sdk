"""
Unit tests for BaseClient
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import (
    GoogleMapsAPIError,
    InvalidRequestError,
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
)


@pytest.mark.unit
class TestBaseClientInit:
    """Test BaseClient initialization"""

    def test_init_success(self, api_key):
        """Test successful initialization"""
        client = BaseClient(api_key, "https://api.example.com")
        assert client.api_key == api_key
        assert client.base_url == "https://api.example.com"
        assert client.timeout == 30
        assert client.session is not None
        client.close()

    def test_init_with_timeout(self, api_key):
        """Test initialization with custom timeout"""
        client = BaseClient(api_key, "https://api.example.com", timeout=60)
        assert client.timeout == 60
        client.close()

    def test_init_with_trailing_slash(self, api_key):
        """Test initialization removes trailing slash from base_url"""
        client = BaseClient(api_key, "https://api.example.com/")
        assert client.base_url == "https://api.example.com"
        client.close()

    def test_init_empty_api_key(self):
        """Test initialization fails with empty API key"""
        with pytest.raises(ValueError, match="API key is required"):
            BaseClient("", "https://api.example.com")

    def test_init_none_api_key(self):
        """Test initialization fails with None API key"""
        with pytest.raises(ValueError, match="API key is required"):
            BaseClient(None, "https://api.example.com")


@pytest.mark.unit
class TestBaseClientGet:
    """Test BaseClient._get method"""

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_get_success(self, mock_session_class, api_key):
        """Test successful GET request"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        mock_session.get.return_value = mock_response

        client = BaseClient(api_key, "https://api.example.com")
        result = client._get("/test", {"param": "value"})

        assert result == {"status": "OK", "data": "test"}
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert "key" in call_args[1]["params"]
        assert call_args[1]["params"]["key"] == api_key
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_get_with_no_params(self, mock_session_class, api_key):
        """Test GET request with no params"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_session.get.return_value = mock_response

        client = BaseClient(api_key, "https://api.example.com")
        result = client._get("/test")

        assert result == {"status": "OK"}
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_get_with_endpoint_slash(self, mock_session_class, api_key):
        """Test GET request handles endpoint with leading slash"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_session.get.return_value = mock_response

        client = BaseClient(api_key, "https://api.example.com")
        client._get("/test")

        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://api.example.com/test"
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_get_request_exception(self, mock_session_class, api_key):
        """Test GET request raises exception on network error"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.get.side_effect = requests.exceptions.RequestException("Network error")

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError, match="Request failed"):
            client._get("/test")
        client.close()


@pytest.mark.unit
class TestBaseClientPost:
    """Test BaseClient._post method"""

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_post_success(self, mock_session_class, api_key):
        """Test successful POST request"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        mock_session.post.return_value = mock_response

        client = BaseClient(api_key, "https://api.example.com")
        result = client._post("/test", {"key": "value"})

        assert result == {"status": "OK", "data": "test"}
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] == {"key": "value"}
        assert "key" in call_args[1]["params"]
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_post_with_custom_headers(self, mock_session_class, api_key):
        """Test POST request with custom headers"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_session.post.return_value = mock_response

        client = BaseClient(api_key, "https://api.example.com")
        headers = {"X-Custom": "value"}
        client._post("/test", headers=headers)

        call_args = mock_session.post.call_args
        assert call_args[1]["headers"]["X-Custom"] == "value"
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session")
    def test_post_request_exception(self, mock_session_class, api_key):
        """Test POST request raises exception on network error"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.post.side_effect = requests.exceptions.RequestException("Network error")

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError, match="Request failed"):
            client._post("/test")
        client.close()


@pytest.mark.unit
class TestBaseClientHandleResponse:
    """Test BaseClient._handle_response method"""

    def test_handle_response_success(self, api_key):
        """Test handling successful JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        result = client._handle_response(mock_response)

        assert result == {"status": "OK", "data": "test"}
        client.close()

    def test_handle_response_non_json_success(self, api_key):
        """Test handling successful non-JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "OK"

        client = BaseClient(api_key, "https://api.example.com")
        result = client._handle_response(mock_response)

        assert result == {"status": "OK", "raw": "OK"}
        client.close()

    def test_handle_response_http_error(self, api_key):
        """Test handling HTTP error response"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(InvalidRequestError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_directions_api_error(self, api_key):
        """Test handling Directions API error status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "REQUEST_DENIED",
            "error_message": "Permission denied"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(PermissionDeniedError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_over_query_limit(self, api_key):
        """Test handling OVER_QUERY_LIMIT status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OVER_QUERY_LIMIT",
            "error_message": "Quota exceeded"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(QuotaExceededError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_not_found(self, api_key):
        """Test handling NOT_FOUND status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "NOT_FOUND",
            "error_message": "Not found"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(NotFoundError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_zero_results(self, api_key):
        """Test handling ZERO_RESULTS status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(NotFoundError, match="No results found"):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_invalid_request(self, api_key):
        """Test handling INVALID_REQUEST status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "INVALID_REQUEST",
            "error_message": "Invalid request"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(InvalidRequestError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_unknown_status(self, api_key):
        """Test handling unknown status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "UNKNOWN_STATUS"
        }
        mock_response.text = ""

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError):
            client._handle_response(mock_response)
        client.close()

    def test_handle_response_non_json_error(self, api_key):
        """Test handling non-JSON error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "Internal Server Error"

        client = BaseClient(api_key, "https://api.example.com")
        with pytest.raises(GoogleMapsAPIError, match="HTTP 500"):
            client._handle_response(mock_response)
        client.close()


@pytest.mark.unit
class TestBaseClientContextManager:
    """Test BaseClient context manager"""

    def test_context_manager(self, api_key):
        """Test using BaseClient as context manager"""
        with BaseClient(api_key, "https://api.example.com") as client:
            assert client.api_key == api_key
        # Session should be closed after context exit

    def test_close(self, api_key):
        """Test close method"""
        client = BaseClient(api_key, "https://api.example.com")
        client.close()
        # Should not raise exception



