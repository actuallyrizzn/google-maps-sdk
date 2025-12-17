"""
Tests for custom exception handlers (issue #98)
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import (
    GoogleMapsAPIError,
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
    InvalidRequestError,
    InternalServerError,
)
from google_maps_sdk.circuit_breaker import CircuitBreakerOpenError


class TestExceptionHandlers:
    """Test custom exception handler functionality"""
    
    def test_exception_handler_not_called_when_none(self):
        """Test that exception handler is not called when None"""
        client = BaseClient(api_key="test_key_12345678901234567890", base_url="https://example.com")
        assert client._exception_handler is None
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(InternalServerError):
            client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
    
    def test_exception_handler_called_for_http_errors(self):
        """Test that exception handler is called for HTTP errors"""
        def handler(exception, request_info):
            assert isinstance(exception, InternalServerError)
            assert request_info['status_code'] == 500
            assert request_info['url'] == "https://example.com/test"
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(InternalServerError):
            client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
    
    def test_exception_handler_can_transform_exception(self):
        """Test that exception handler can transform exceptions"""
        def handler(exception, request_info):
            # Transform to a different exception
            return GoogleMapsAPIError("Custom error message", status_code=500)
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(GoogleMapsAPIError) as exc_info:
            client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
        assert "Custom error message" in str(exc_info.value)
    
    def test_exception_handler_returns_none_uses_original(self):
        """Test that returning None from handler uses original exception"""
        def handler(exception, request_info):
            return None
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(InternalServerError):
            client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
    
    def test_exception_handler_called_for_directions_api_errors(self):
        """Test that exception handler is called for Directions API errors"""
        def handler(exception, request_info):
            assert isinstance(exception, PermissionDeniedError)
            assert request_info['status'] == "REQUEST_DENIED"
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.url = "https://example.com/test"
        data = {"status": "REQUEST_DENIED", "error_message": "Permission denied"}
        
        with pytest.raises(PermissionDeniedError):
            client._check_directions_api_errors(data, mock_response)
    
    def test_exception_handler_called_for_retry_failures(self):
        """Test that exception handler is called for retry failures"""
        handler_calls = []
        
        def handler(exception, request_info):
            handler_calls.append((exception, request_info))
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.headers = {'Content-Type': 'application/json'}
            mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
            mock_response.url = "https://example.com/test"
            mock_get.return_value = mock_response
            
            with pytest.raises(InternalServerError):
                client._get("/test")
            
            # Handler should be called
            assert len(handler_calls) > 0
    
    def test_exception_handler_called_for_circuit_breaker_errors(self):
        """Test that exception handler is called for circuit breaker errors"""
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        handler_calls = []
        
        def handler(exception, request_info):
            handler_calls.append((exception, request_info))
            return exception
        
        circuit_breaker = CircuitBreaker(failure_threshold=1, timeout=60.0)
        circuit_breaker.state = circuit_breaker.OPEN
        circuit_breaker.last_failure_time = None
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler,
            circuit_breaker=circuit_breaker
        )
        
        with pytest.raises(CircuitBreakerOpenError):
            client._get("/test")
        
        # Handler should be called
        assert len(handler_calls) == 1
        assert isinstance(handler_calls[0][0], CircuitBreakerOpenError)
        assert handler_calls[0][1]['method'] == 'GET'
    
    def test_exception_handler_error_logged_but_original_used(self):
        """Test that if handler raises error, it's logged but original exception is used"""
        def handler(exception, request_info):
            raise ValueError("Handler error")
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with patch.object(client._logger, 'warning') as mock_warning:
            with pytest.raises(InternalServerError):
                client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
            
            # Should log warning about handler error
            assert mock_warning.called
    
    def test_exception_handler_with_client_config(self):
        """Test exception handler via ClientConfig"""
        from google_maps_sdk.config import ClientConfig
        
        handler_calls = []
        
        def handler(exception, request_info):
            handler_calls.append((exception, request_info))
            return exception
        
        config = ClientConfig(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        client = BaseClient(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Internal Server Error"}}
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(InternalServerError):
            client._check_http_errors(mock_response, {"error": {"message": "Internal Server Error"}})
        
        assert len(handler_calls) == 1
    
    def test_exception_handler_receives_request_info(self):
        """Test that exception handler receives complete request info"""
        received_info = None
        
        def handler(exception, request_info):
            nonlocal received_info
            received_info = request_info
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Not Found"}}
        mock_response.url = "https://example.com/test"
        
        request_id = "test-request-id"
        
        with pytest.raises(NotFoundError):
            client._check_http_errors(mock_response, {"error": {"message": "Not Found"}}, request_id=request_id)
        
        assert received_info is not None
        assert received_info['status_code'] == 404
        assert received_info['url'] == "https://example.com/test"
        assert received_info['request_id'] == request_id
    
    def test_exception_handler_for_xml_errors(self):
        """Test exception handler for XML error responses"""
        handler_calls = []
        
        def handler(exception, request_info):
            handler_calls.append((exception, request_info))
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'application/xml'}
        mock_response.text = "<error>Internal Server Error</error>"
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(GoogleMapsAPIError):
            client._check_http_errors(mock_response, {})
        
        assert len(handler_calls) == 1
    
    def test_exception_handler_for_non_json_errors(self):
        """Test exception handler for non-JSON error responses"""
        handler_calls = []
        
        def handler(exception, request_info):
            handler_calls.append((exception, request_info))
            return exception
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            exception_handler=handler
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.text = "Internal Server Error"
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(GoogleMapsAPIError):
            client._check_http_errors(mock_response, {})
        
        assert len(handler_calls) == 1
