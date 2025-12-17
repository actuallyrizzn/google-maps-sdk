"""
Type stubs for exceptions (issue #46)
"""

from typing import Optional, Dict, Any

class GoogleMapsAPIError(Exception):
    message: str
    status_code: Optional[int]
    response: Optional[Dict[str, Any]]
    request_url: Optional[str]
    request_id: Optional[str]
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = ...,
        response: Optional[Dict[str, Any]] = ...,
        request_url: Optional[str] = ...,
        request_id: Optional[str] = ...,
    ) -> None: ...
    
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class InvalidRequestError(GoogleMapsAPIError): ...
class PermissionDeniedError(GoogleMapsAPIError): ...
class NotFoundError(GoogleMapsAPIError): ...
class QuotaExceededError(GoogleMapsAPIError): ...
class InternalServerError(GoogleMapsAPIError): ...
class CircuitBreakerOpenError(GoogleMapsAPIError): ...

def handle_http_error(
    status_code: int,
    response: Dict[str, Any],
    request_url: Optional[str] = ...,
    request_id: Optional[str] = ...,
) -> GoogleMapsAPIError: ...
