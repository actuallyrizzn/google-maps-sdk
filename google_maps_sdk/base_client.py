"""
Base client class for Google Maps Platform APIs
"""

import requests
from typing import Optional, Dict, Any
from .exceptions import (
    handle_http_error,
    GoogleMapsAPIError,
    PermissionDeniedError,
    QuotaExceededError,
    NotFoundError,
    InvalidRequestError,
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
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise GoogleMapsAPIError(f"Request failed: {str(e)}")

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request

        Args:
            endpoint: API endpoint
            data: Request body data
            headers: Request headers
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self.api_key
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        try:
            response = self.session.post(
                url, json=data, headers=headers, params=params, timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise GoogleMapsAPIError(f"Request failed: {str(e)}")

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
                )
            return {"status": "OK", "raw": response.text}

        # Check for API errors in response
        if response.status_code >= 400:
            raise handle_http_error(response.status_code, data)

        # Check for Directions API status codes
        if "status" in data and data["status"] != "OK":
            status = data["status"]
            error_message = data.get("error_message", f"API returned status: {status}")
            
            if status == "REQUEST_DENIED":
                raise PermissionDeniedError(error_message, data)
            elif status == "OVER_QUERY_LIMIT":
                raise QuotaExceededError(error_message, data)
            elif status == "NOT_FOUND":
                raise NotFoundError(error_message, data)
            elif status == "ZERO_RESULTS":
                raise NotFoundError("No results found", data)
            elif status == "INVALID_REQUEST":
                raise InvalidRequestError(error_message, data)
            else:
                raise GoogleMapsAPIError(error_message, response=data)

        return data

    def close(self):
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

