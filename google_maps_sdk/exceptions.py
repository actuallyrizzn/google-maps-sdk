"""
Custom exceptions for Google Maps Platform SDK
"""


class GoogleMapsAPIError(Exception):
    """Base exception for all Google Maps API errors"""

    def __init__(self, message: str, status_code: int = None, response: dict = None, request_url: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.request_url = request_url

    def __repr__(self) -> str:
        """String representation of exception (issue #32)"""
        parts = [f"{self.__class__.__name__}(message={self.message!r}"]
        if self.status_code is not None:
            parts.append(f"status_code={self.status_code}")
        if self.request_url:
            parts.append(f"request_url={self.request_url!r}")
        return ", ".join(parts) + ")"

    def __str__(self) -> str:
        """Human-readable error message with context (issue #14)"""
        msg = self.message
        if self.status_code:
            msg = f"[HTTP {self.status_code}] {msg}"
        if self.request_url:
            msg = f"{msg} (URL: {self.request_url})"
        return msg


class InvalidRequestError(GoogleMapsAPIError):
    """Raised when the request is invalid (400)"""

    def __init__(self, message: str, response: dict = None, request_url: str = None):
        super().__init__(message, status_code=400, response=response, request_url=request_url)


class PermissionDeniedError(GoogleMapsAPIError):
    """Raised when API key is invalid or permissions are insufficient (403)"""

    def __init__(self, message: str, response: dict = None, request_url: str = None):
        super().__init__(message, status_code=403, response=response, request_url=request_url)


class NotFoundError(GoogleMapsAPIError):
    """Raised when resource is not found (404)"""

    def __init__(self, message: str, response: dict = None, request_url: str = None):
        super().__init__(message, status_code=404, response=response, request_url=request_url)


class QuotaExceededError(GoogleMapsAPIError):
    """Raised when API quota is exceeded (429)"""

    def __init__(self, message: str, response: dict = None, request_url: str = None):
        super().__init__(message, status_code=429, response=response, request_url=request_url)


class InternalServerError(GoogleMapsAPIError):
    """Raised when there's an internal server error (500)"""

    def __init__(self, message: str, response: dict = None, request_url: str = None):
        super().__init__(message, status_code=500, response=response, request_url=request_url)


def handle_http_error(status_code: int, response: dict, request_url: str = None) -> GoogleMapsAPIError:
    """Convert HTTP status code to appropriate exception"""
    error_message = response.get("error", {}).get("message", "Unknown error")
    
    if status_code == 400:
        return InvalidRequestError(error_message, response, request_url)
    elif status_code == 403:
        return PermissionDeniedError(error_message, response, request_url)
    elif status_code == 404:
        return NotFoundError(error_message, response, request_url)
    elif status_code == 429:
        return QuotaExceededError(error_message, response, request_url)
    elif status_code >= 500:
        return InternalServerError(error_message, response, request_url)
    else:
        return GoogleMapsAPIError(error_message, status_code, response, request_url)

