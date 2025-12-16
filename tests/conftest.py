"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import Mock, MagicMock
import requests


@pytest.fixture
def api_key():
    """Test API key (must be at least 20 characters for validation)"""
    return "test_api_key_12345678901234567890"


@pytest.fixture
def mock_response():
    """Create a mock HTTP response"""
    def _create_response(status_code=200, json_data=None, text=None):
        response = Mock(spec=requests.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = text or ""
        return response
    return _create_response


@pytest.fixture
def sample_origin():
    """Sample origin location"""
    return {
        "location": {
            "latLng": {
                "latitude": 37.419734,
                "longitude": -122.0827784
            }
        }
    }


@pytest.fixture
def sample_destination():
    """Sample destination location"""
    return {
        "location": {
            "latLng": {
                "latitude": 37.417670,
                "longitude": -122.079595
            }
        }
    }


@pytest.fixture
def sample_path():
    """Sample GPS path"""
    return [
        (60.170880, 24.942795),
        (60.170879, 24.942796),
        (60.170877, 24.942796)
    ]


@pytest.fixture
def sample_place_ids():
    """Sample place IDs"""
    return [
        "ChIJ685WIFYViEgRHlHvBbiD5nE",
        "ChIJA01I-8YVhkgRGJb0fW4UX7Y"
    ]



