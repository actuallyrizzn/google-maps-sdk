"""
Unit tests for request/response interceptors (issue #35)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google_maps_sdk.base_client import BaseClient


@pytest.mark.unit
class TestRequestInterceptors:
    """Test request interceptors"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_request_hook_called(self, mock_get, api_key):
        """Test that request hooks are called"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        request_hook = Mock()
        client.add_request_hook(request_hook)
        
        client._get("/test")
        
        # Verify hook was called
        assert request_hook.called
        call_args = request_hook.call_args[0]
        assert call_args[0] == "GET"
        assert "test" in call_args[1]  # URL
        assert isinstance(call_args[2], dict)  # headers
        assert isinstance(call_args[3], dict)  # params
        assert call_args[4] is None  # data (GET has no data)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_request_hook_called_for_post(self, mock_post, api_key):
        """Test that request hooks are called for POST requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        request_hook = Mock()
        client.add_request_hook(request_hook)
        
        client._post("/test", data={"key": "value"})
        
        # Verify hook was called
        assert request_hook.called
        call_args = request_hook.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[4] == {"key": "value"}  # data
        
        client.close()

    def test_add_request_hook_validation(self, api_key):
        """Test that adding non-callable hook raises error"""
        client = BaseClient(api_key, "https://example.com")
        
        with pytest.raises(TypeError, match="Hook must be callable"):
            client.add_request_hook("not_callable")
        
        client.close()

    def test_remove_request_hook(self, api_key):
        """Test removing request hook"""
        client = BaseClient(api_key, "https://example.com")
        
        hook = Mock()
        client.add_request_hook(hook)
        assert len(client._request_hooks) == 1
        
        client.remove_request_hook(hook)
        assert len(client._request_hooks) == 0
        
        client.close()

    def test_clear_request_hooks(self, api_key):
        """Test clearing all request hooks"""
        client = BaseClient(api_key, "https://example.com")
        
        client.add_request_hook(Mock())
        client.add_request_hook(Mock())
        assert len(client._request_hooks) == 2
        
        client.clear_request_hooks()
        assert len(client._request_hooks) == 0
        
        client.close()


@pytest.mark.unit
class TestResponseInterceptors:
    """Test response interceptors"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_response_hook_called(self, mock_get, api_key):
        """Test that response hooks are called"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        response_hook = Mock()
        client.add_response_hook(response_hook)
        
        client._get("/test")
        
        # Verify hook was called with response
        assert response_hook.called
        call_args = response_hook.call_args[0]
        assert call_args[0] == mock_response
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_response_hook_called_for_post(self, mock_post, api_key):
        """Test that response hooks are called for POST requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        response_hook = Mock()
        client.add_response_hook(response_hook)
        
        client._post("/test", data={"key": "value"})
        
        # Verify hook was called
        assert response_hook.called
        call_args = response_hook.call_args[0]
        assert call_args[0] == mock_response
        
        client.close()

    def test_add_response_hook_validation(self, api_key):
        """Test that adding non-callable hook raises error"""
        client = BaseClient(api_key, "https://example.com")
        
        with pytest.raises(TypeError, match="Hook must be callable"):
            client.add_response_hook("not_callable")
        
        client.close()

    def test_remove_response_hook(self, api_key):
        """Test removing response hook"""
        client = BaseClient(api_key, "https://example.com")
        
        hook = Mock()
        client.add_response_hook(hook)
        assert len(client._response_hooks) == 1
        
        client.remove_response_hook(hook)
        assert len(client._response_hooks) == 0
        
        client.close()

    def test_clear_response_hooks(self, api_key):
        """Test clearing all response hooks"""
        client = BaseClient(api_key, "https://example.com")
        
        client.add_response_hook(Mock())
        client.add_response_hook(Mock())
        assert len(client._response_hooks) == 2
        
        client.clear_response_hooks()
        assert len(client._response_hooks) == 0
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_hook_exception_handled(self, mock_get, api_key):
        """Test that hook exceptions don't break requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        def failing_hook(*args):
            raise ValueError("Hook error")
        
        client.add_request_hook(failing_hook)
        client.add_response_hook(failing_hook)
        
        # Request should still succeed despite hook exception
        result = client._get("/test")
        assert result == {"status": "OK"}
        
        client.close()
