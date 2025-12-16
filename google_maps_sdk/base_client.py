"""
Base client class for Google Maps Platform APIs
"""

import requests
import warnings
from typing import Optional, Dict, Any
from .exceptions import (
    handle_http_error,
    GoogleMapsAPIError,
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
    InvalidRequestError,
)
from .utils import (
    validate_api_key,
    validate_base_url,
    validate_timeout,
    sanitize_api_key_for_logging,
)


class BaseClient:
    """Base client for all Google Maps Platform API clients"""

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """
        Initialize base client

        Args:
            api_key: Google Maps Platform API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds

        Raises:
            TypeError: If api_key is not a string
            ValueError: If api_key or base_url is invalid
        """
        # Validate and store API key (issue #2, #6)
        self._api_key = validate_api_key(api_key)
        
        # Validate base URL (issue #30)
        self.base_url = validate_base_url(base_url)
        
        # Validate timeout (issue #40)
        self.timeout = validate_timeout(timeout)
        
        # Create session with SSL verification enforced (issue #4)
        self.session = requests.Session()
        self.session.verify = True  # Explicitly enforce SSL verification
        
        # Set User-Agent header (issue #13)
        # Set Accept-Encoding header for response compression (issue #45)
        self.session.headers.update({
            'User-Agent': f'google-maps-sdk/{__import__("google_maps_sdk").__version__}',
            'Accept-Encoding': 'gzip, deflate, br'
        })

    @property
    def api_key(self) -> str:
        """
        Get API key with warning (issue #6)
        
        Returns:
            API key string
            
        Warns:
            UserWarning: When API key is accessed directly
        """
        warnings.warn(
            "Accessing API key directly is not recommended. "
            "Consider using the client methods instead.",
            UserWarning,
            stacklevel=2
        )
        return self._api_key

    def set_api_key(self, api_key: str) -> None:
        """
        Update API key (useful for key rotation) (issue #33)
        
        Args:
            api_key: New API key
            
        Raises:
            TypeError: If api_key is not a string
            ValueError: If api_key is invalid
        """
        self._api_key = validate_api_key(api_key)

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Make a GET request

        Args:
            endpoint: API endpoint
            params: Query parameters
            timeout: Optional timeout override (issue #12)

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self._api_key
        
        # Use provided timeout or default (issue #12)
        request_timeout = timeout if timeout is not None else self.timeout
        
        try:
            response = self.session.get(url, params=params, timeout=request_timeout)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            # Sanitize error message to prevent API key exposure (issue #7)
            error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
            raise GoogleMapsAPIError(f"Request failed: {error_msg}") from e

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request

        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Request headers
            params: Query parameters
            timeout: Optional timeout override (issue #12)

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self._api_key
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        # Use provided timeout or default (issue #12)
        request_timeout = timeout if timeout is not None else self.timeout
        
        try:
            response = self.session.post(
                url, json=data, headers=headers, params=params, timeout=request_timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            # Sanitize error message to prevent API key exposure (issue #7)
            error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
            raise GoogleMapsAPIError(f"Request failed: {error_msg}") from e

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and convert to appropriate format

        Args:
            response: HTTP response object

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If response indicates an error
        """
        # Try to parse JSON
        try:
            data = response.json()
        except ValueError:
            # If not JSON, check status code
            if response.status_code >= 400:
                raise GoogleMapsAPIError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    request_url=str(response.url) if hasattr(response, 'url') else None,
                )
            return {"status": "OK", "raw": response.text}

        # Check for API errors in response
        if response.status_code >= 400:
            raise handle_http_error(response.status_code, data, response.url)

        # Check for Directions API status codes
        if "status" in data and data["status"] != "OK":
            status = data["status"]
            error_message = data.get("error_message", f"API returned status: {status}")
            
            request_url = str(response.url) if hasattr(response, 'url') else None
            if status == "REQUEST_DENIED":
                raise PermissionDeniedError(error_message, data, request_url)
            elif status == "OVER_QUERY_LIMIT":
                raise QuotaExceededError(error_message, data, request_url)
            elif status == "NOT_FOUND":
                raise NotFoundError(error_message, data, request_url)
            elif status == "ZERO_RESULTS":
                raise NotFoundError("No results found", data, request_url)
            elif status == "INVALID_REQUEST":
                raise InvalidRequestError(error_message, data, request_url)
            else:
                raise GoogleMapsAPIError(error_message, response=data, request_url=request_url)

        return data

    def close(self):
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        """String representation of client (issue #52)"""
        return f"{self.__class__.__name__}(api_key='***', base_url={self.base_url!r}, timeout={self.timeout})"

