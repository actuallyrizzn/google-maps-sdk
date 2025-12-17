"""
Unit tests for request ID tracking (issue #28)
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import GoogleMapsAPIError


@pytest.mark.unit
class TestRequestIDTracking:
    """Test request ID tracking functionality"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_get_request_has_id_in_header(self, mock_get, api_key):
        """Test that GET requests include X-Request-ID header"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._get("/test")
        
        # Verify request was made with X-Request-ID header
        assert mock_get.called
        call_kwargs = mock_get.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-Request-ID' in call_kwargs['headers']
        
        # Verify request ID is a valid UUID
        request_id = call_kwargs['headers']['X-Request-ID']
        uuid.UUID(request_id)  # Will raise if invalid
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_post_request_has_id_in_header(self, mock_post, api_key):
        """Test that POST requests include X-Request-ID header"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        client._post("/test", data={"test": "data"})
        
        # Verify request was made with X-Request-ID header
        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert 'headers' in call_kwargs
        assert 'X-Request-ID' in call_kwargs['headers']
        
        # Verify request ID is a valid UUID
        request_id = call_kwargs['headers']['X-Request-ID']
        uuid.UUID(request_id)  # Will raise if invalid
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_exception_has_request_id(self, mock_get, api_key):
        """Test that exceptions include request ID"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        try:
            client._get("/test")
            pytest.fail("Should have raised exception")
        except GoogleMapsAPIError as e:
            # Verify exception has request_id
            assert hasattr(e, 'request_id')
            assert e.request_id is not None
            
            # Verify request ID is a valid UUID
            uuid.UUID(e.request_id)
            
            # Verify request ID appears in string representation
            assert e.request_id in str(e)
        
        client.close()

    def test_request_id_in_logs(self, api_key, caplog):
        """Test that request IDs appear in log messages"""
        import logging
        
        # Set up logging capture
        with caplog.at_level(logging.DEBUG):
            with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "OK"}
                mock_response.url = "https://example.com/test"
                mock_get.return_value = mock_response
                
                client = BaseClient(api_key, "https://example.com")
                client._get("/test")
                
                # Check that logs contain request ID
                log_messages = [record.message for record in caplog.records]
                request_log = [msg for msg in log_messages if "GET request" in msg]
                assert len(request_log) > 0
                assert "[ID:" in request_log[0]
                
                client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_retry_gets_new_request_id(self, mock_get, api_key):
        """Test that retries get new request IDs"""
        from google_maps_sdk.retry import RetryConfig
        
        # First call fails, second succeeds
        mock_responses = [
            MagicMock(status_code=500, json=lambda: {"error": "Server error"}, url="https://example.com/test"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_get.side_effect = mock_responses
        
        client = BaseClient(
            api_key, 
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.1)
        )
        
        # Mock _handle_response to raise InternalServerError on first call
        original_handle = client._handle_response
        call_count = [0]
        
        def mock_handle(response, request_id=None):
            call_count[0] += 1
            if call_count[0] == 1:
                from google_maps_sdk.exceptions import InternalServerError
                raise InternalServerError("Server error", request_id=request_id)
            return original_handle(response, request_id=request_id)
        
        client._handle_response = mock_handle
        
        try:
            client._get("/test")
        except Exception:
            pass
        
        # Verify two requests were made with different request IDs
        assert mock_get.call_count == 2
        first_id = mock_get.call_args_list[0][1]['headers']['X-Request-ID']
        second_id = mock_get.call_args_list[1][1]['headers']['X-Request-ID']
        assert first_id != second_id
        
        client.close()
