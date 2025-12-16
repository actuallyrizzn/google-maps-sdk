"""
Custom exceptions for Google Maps Platform SDK
"""


class GoogleMapsAPIError(Exception):
    """Base exception for all Google Maps API errors"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class InvalidRequestError(GoogleMapsAPIError):
    """Raised when the request is invalid (400)"""

    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=400, response=response)


class PermissionDeniedError(GoogleMapsAPIError):
    """Raised when API key is invalid or permissions are insufficient (403)"""

    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=403, response=response)


class NotFoundError(GoogleMapsAPIError):
    """Raised when resource is not found (404)"""

    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=404, response=response)


class QuotaExceededError(GoogleMapsAPIError):
    """Raised when API quota is exceeded (429)"""

    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=429, response=response)


class InternalServerError(GoogleMapsAPIError):
    """Raised when there's an internal server error (500)"""

    def __init__(self, message: str, response: dict = None):
        super().__init__(message, status_code=500, response=response)


def handle_http_error(status_code: int, response: dict) -> GoogleMapsAPIError:
    """Convert HTTP status code to appropriate exception"""
    error_message = response.get("error", {}).get("message", "Unknown error")
    
    if status_code == 400:
        return InvalidRequestError(error_message, response)
    elif status_code == 403:
        return PermissionDeniedError(error_message, response)
    elif status_code == 404:
        return NotFoundError(error_message, response)
    elif status_code == 429:
        return QuotaExceededError(error_message, response)
    elif status_code >= 500:
        return InternalServerError(error_message, response)
    else:
        return GoogleMapsAPIError(error_message, status_code, response)

