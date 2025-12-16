"""
Unit tests for exception classes
"""

import pytest
from google_maps_sdk.exceptions import (
    GoogleMapsAPIError,
    InvalidRequestError,
    PermissionDeniedError,
    NotFoundError,
    QuotaExceededError,
    InternalServerError,
    handle_http_error,
)


@pytest.mark.unit
class TestGoogleMapsAPIError:
    """Test base exception class"""

    def test_init_with_message(self):
        """Test initialization with message only"""
        error = GoogleMapsAPIError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response is None

    def test_init_with_all_params(self):
        """Test initialization with all parameters"""
        response = {"error": "details"}
        error = GoogleMapsAPIError("Test error", status_code=500, response=response)
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.response == response


@pytest.mark.unit
class TestInvalidRequestError:
    """Test InvalidRequestError"""

    def test_init(self):
        """Test initialization"""
        error = InvalidRequestError("Invalid request")
        assert error.message == "Invalid request"
        assert error.status_code == 400
        assert isinstance(error, GoogleMapsAPIError)


@pytest.mark.unit
class TestPermissionDeniedError:
    """Test PermissionDeniedError"""

    def test_init(self):
        """Test initialization"""
        error = PermissionDeniedError("Permission denied")
        assert error.message == "Permission denied"
        assert error.status_code == 403
        assert isinstance(error, GoogleMapsAPIError)


@pytest.mark.unit
class TestNotFoundError:
    """Test NotFoundError"""

    def test_init(self):
        """Test initialization"""
        error = NotFoundError("Not found")
        assert error.message == "Not found"
        assert error.status_code == 404
        assert isinstance(error, GoogleMapsAPIError)


@pytest.mark.unit
class TestQuotaExceededError:
    """Test QuotaExceededError"""

    def test_init(self):
        """Test initialization"""
        error = QuotaExceededError("Quota exceeded")
        assert error.message == "Quota exceeded"
        assert error.status_code == 429
        assert isinstance(error, GoogleMapsAPIError)


@pytest.mark.unit
class TestInternalServerError:
    """Test InternalServerError"""

    def test_init(self):
        """Test initialization"""
        error = InternalServerError("Server error")
        assert error.message == "Server error"
        assert error.status_code == 500
        assert isinstance(error, GoogleMapsAPIError)


@pytest.mark.unit
class TestHandleHttpError:
    """Test handle_http_error function"""

    def test_handle_400(self):
        """Test handling 400 error"""
        response = {"error": {"message": "Bad request"}}
        error = handle_http_error(400, response)
        assert isinstance(error, InvalidRequestError)
        assert error.message == "Bad request"

    def test_handle_403(self):
        """Test handling 403 error"""
        response = {"error": {"message": "Forbidden"}}
        error = handle_http_error(403, response)
        assert isinstance(error, PermissionDeniedError)
        assert error.message == "Forbidden"

    def test_handle_404(self):
        """Test handling 404 error"""
        response = {"error": {"message": "Not found"}}
        error = handle_http_error(404, response)
        assert isinstance(error, NotFoundError)
        assert error.message == "Not found"

    def test_handle_429(self):
        """Test handling 429 error"""
        response = {"error": {"message": "Too many requests"}}
        error = handle_http_error(429, response)
        assert isinstance(error, QuotaExceededError)
        assert error.message == "Too many requests"

    def test_handle_500(self):
        """Test handling 500 error"""
        response = {"error": {"message": "Internal server error"}}
        error = handle_http_error(500, response)
        assert isinstance(error, InternalServerError)
        assert error.message == "Internal server error"

    def test_handle_502(self):
        """Test handling 502 error (>= 500)"""
        response = {"error": {"message": "Bad gateway"}}
        error = handle_http_error(502, response)
        assert isinstance(error, InternalServerError)

    def test_handle_unknown_status(self):
        """Test handling unknown status code"""
        response = {"error": {"message": "Unknown error"}}
        error = handle_http_error(418, response)  # I'm a teapot
        assert isinstance(error, GoogleMapsAPIError)
        assert error.status_code == 418

    def test_handle_missing_error_message(self):
        """Test handling response without error message"""
        response = {}
        error = handle_http_error(400, response)
        assert isinstance(error, InvalidRequestError)
        assert error.message == "Unknown error"



