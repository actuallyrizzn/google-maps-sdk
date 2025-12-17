"""
Tests for response validation (issue #99)
"""

import pytest
import requests
from unittest.mock import Mock, patch
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.exceptions import GoogleMapsAPIError


class TestResponseValidation:
    """Test response validation functionality"""
    
    def test_response_validator_not_called_when_none(self):
        """Test that response validator is not called when None"""
        client = BaseClient(api_key="test_key_12345678901234567890", base_url="https://example.com")
        assert client._response_validator is None
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        result = client._handle_response(mock_response)
        assert result == {"status": "OK", "data": "test"}
    
    def test_response_validator_called_for_successful_responses(self):
        """Test that response validator is called for successful responses"""
        validator_calls = []
        
        def validator(data, request_info):
            validator_calls.append((data, request_info))
            assert data == {"status": "OK", "data": "test"}
            assert request_info['status_code'] == 200
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        result = client._handle_response(mock_response)
        assert result == {"status": "OK", "data": "test"}
        assert len(validator_calls) == 1
    
    def test_response_validator_can_transform_data(self):
        """Test that response validator can transform response data"""
        def validator(data, request_info):
            # Add additional field
            data['validated'] = True
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        result = client._handle_response(mock_response)
        assert result == {"status": "OK", "validated": True}
    
    def test_response_validator_returns_none_uses_original(self):
        """Test that returning None from validator uses original data"""
        def validator(data, request_info):
            return None
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "data": "test"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        result = client._handle_response(mock_response)
        assert result == {"status": "OK", "data": "test"}
    
    def test_response_validator_can_raise_value_error(self):
        """Test that validator can raise ValueError for invalid data"""
        def validator(data, request_info):
            if "status" not in data:
                raise ValueError("Missing 'status' field in response")
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"data": "test"}  # Missing 'status'
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(ValueError, match="Missing 'status' field"):
            client._handle_response(mock_response)
    
    def test_response_validator_can_raise_google_maps_api_error(self):
        """Test that validator can raise GoogleMapsAPIError"""
        def validator(data, request_info):
            if "status" not in data:
                raise GoogleMapsAPIError("Invalid response structure")
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"data": "test"}  # Missing 'status'
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(GoogleMapsAPIError, match="Invalid response structure"):
            client._handle_response(mock_response)
    
    def test_response_validator_receives_request_info(self):
        """Test that response validator receives complete request info"""
        received_info = None
        
        def validator(data, request_info):
            nonlocal received_info
            received_info = request_info
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        request_id = "test-request-id"
        client._handle_response(mock_response, request_id=request_id)
        
        assert received_info is not None
        assert received_info['status_code'] == 200
        assert received_info['url'] == "https://example.com/test"
        assert received_info['request_id'] == request_id
    
    def test_response_validator_error_logged_and_raised(self):
        """Test that if validator raises unexpected error, it's logged and raised as GoogleMapsAPIError"""
        def validator(data, request_info):
            raise RuntimeError("Unexpected error")
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        with patch.object(client._logger, 'warning') as mock_warning:
            with pytest.raises(GoogleMapsAPIError, match="Response validation failed"):
                client._handle_response(mock_response)
            
            # Should log warning about validator error
            assert mock_warning.called
    
    def test_response_validator_with_client_config(self):
        """Test response validator via ClientConfig"""
        from google_maps_sdk.config import ClientConfig
        
        validator_calls = []
        
        def validator(data, request_info):
            validator_calls.append((data, request_info))
            return data
        
        config = ClientConfig(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        client = BaseClient(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK"}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        client._handle_response(mock_response)
        
        assert len(validator_calls) == 1
    
    def test_response_validator_not_called_on_errors(self):
        """Test that response validator is not called when errors occur"""
        validator_calls = []
        
        def validator(data, request_info):
            validator_calls.append((data, request_info))
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        with pytest.raises(GoogleMapsAPIError):
            client._handle_response(mock_response)
        
        # Validator should not be called for error responses
        assert len(validator_calls) == 0
    
    def test_response_validator_called_after_error_checks(self):
        """Test that response validator is called after error checks pass"""
        validator_calls = []
        
        def validator(data, request_info):
            validator_calls.append((data, request_info))
            # Validator should receive data that passed error checks
            assert "status" in data
            return data
        
        client = BaseClient(
            api_key="test_key_12345678901234567890",
            base_url="https://example.com",
            response_validator=validator
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "OK", "routes": []}
        mock_response.text = ""
        mock_response.url = "https://example.com/test"
        
        result = client._handle_response(mock_response)
        assert len(validator_calls) == 1
        assert result == {"status": "OK", "routes": []}
