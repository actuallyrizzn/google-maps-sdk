"""
Base client class for Google Maps Platform APIs
"""

import requests
import warnings
import time
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
from .rate_limiter import RateLimiter
from .retry import RetryConfig, should_retry, exponential_backoff


class BaseClient:
    """Base client for all Google Maps Platform API clients"""

    def __init__(
        self, 
        api_key: str, 
        base_url: str, 
        timeout: int = 30,
        rate_limit_max_calls: Optional[int] = None,
        rate_limit_period: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize base client

        Args:
            api_key: Google Maps Platform API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
            retry_config: Retry configuration (None to disable retries) (issue #11)

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
        
        # Initialize rate limiter (issue #5)
        if rate_limit_max_calls is not None:
            period = rate_limit_period if rate_limit_period is not None else 60.0
            self._rate_limiter = RateLimiter(max_calls=rate_limit_max_calls, period=period)
        else:
            self._rate_limiter = None
        
        # Initialize retry configuration (issue #11)
        self._retry_config = retry_config
        
        # Store client ID for rate limiting
        self._client_id = id(self)
        
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
        Make a GET request with optional retry logic (issue #11)

        Args:
            endpoint: API endpoint
            params: Query parameters
            timeout: Optional timeout override (issue #12)

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If request fails
            QuotaExceededError: If rate limit is exceeded (issue #5)
        """
        # Apply rate limiting (issue #5)
        if self._rate_limiter is not None:
            self._rate_limiter.acquire(self._client_id)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self._api_key
        
        # Use provided timeout or default (issue #12)
        request_timeout = timeout if timeout is not None else self.timeout
        
        # Retry logic (issue #11)
        last_exception = None
        
        max_retries = self._retry_config.max_retries if self._retry_config else 0
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=request_timeout)
                # _handle_response may raise GoogleMapsAPIError for HTTP errors
                return self._handle_response(response)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                # Check if we should retry
                if self._retry_config and should_retry(e, None):
                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        break
                    
                    # Calculate backoff delay
                    delay = exponential_backoff(
                        attempt,
                        base_delay=self._retry_config.base_delay,
                        max_delay=self._retry_config.max_delay,
                        exponential_base=self._retry_config.exponential_base,
                        jitter=self._retry_config.jitter
                    )
                    
                    # Wait before retrying
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    break
            except GoogleMapsAPIError as e:
                last_exception = e
                
                # Check if we should retry (e.g., 5xx errors)
                if self._retry_config and should_retry(e, e.status_code):
                    if attempt >= max_retries:
                        break
                    
                    delay = exponential_backoff(
                        attempt,
                        base_delay=self._retry_config.base_delay,
                        max_delay=self._retry_config.max_delay,
                        exponential_base=self._retry_config.exponential_base,
                        jitter=self._retry_config.jitter
                    )
                    
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    raise
            except requests.exceptions.RequestException as e:
                # Other request exceptions - don't retry
                error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
                raise GoogleMapsAPIError(f"Request failed: {error_msg}") from e
        
        # If we get here, all retries failed
        if last_exception:
            if isinstance(last_exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                # Sanitize error message to prevent API key exposure (issue #7)
                error_msg = sanitize_api_key_for_logging(str(last_exception), self._api_key)
                raise GoogleMapsAPIError(f"Request failed after {max_retries + 1} attempts: {error_msg}") from last_exception
            else:
                raise last_exception
        
        # Should never reach here
        raise GoogleMapsAPIError("Request failed: Unknown error")

    def _post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request with optional retry logic (issue #11)

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
            QuotaExceededError: If rate limit is exceeded (issue #5)
        """
        # Apply rate limiting (issue #5)
        if self._rate_limiter is not None:
            self._rate_limiter.acquire(self._client_id)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if params is None:
            params = {}
        
        params["key"] = self._api_key
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        # Use provided timeout or default (issue #12)
        request_timeout = timeout if timeout is not None else self.timeout
        
        # Retry logic (issue #11)
        last_exception = None
        
        max_retries = self._retry_config.max_retries if self._retry_config else 0
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.post(
                    url, json=data, headers=headers, params=params, timeout=request_timeout
                )
                # _handle_response may raise GoogleMapsAPIError for HTTP errors
                return self._handle_response(response)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                # Check if we should retry
                if self._retry_config and should_retry(e, None):
                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        break
                    
                    # Calculate backoff delay
                    delay = exponential_backoff(
                        attempt,
                        base_delay=self._retry_config.base_delay,
                        max_delay=self._retry_config.max_delay,
                        exponential_base=self._retry_config.exponential_base,
                        jitter=self._retry_config.jitter
                    )
                    
                    # Wait before retrying
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    break
            except GoogleMapsAPIError as e:
                last_exception = e
                
                # Check if we should retry (e.g., 5xx errors)
                if self._retry_config and should_retry(e, e.status_code):
                    if attempt >= max_retries:
                        break
                    
                    delay = exponential_backoff(
                        attempt,
                        base_delay=self._retry_config.base_delay,
                        max_delay=self._retry_config.max_delay,
                        exponential_base=self._retry_config.exponential_base,
                        jitter=self._retry_config.jitter
                    )
                    
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    raise
            except requests.exceptions.RequestException as e:
                # Other request exceptions - don't retry
                error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
                raise GoogleMapsAPIError(f"Request failed: {error_msg}") from e
        
        # If we get here, all retries failed
        if last_exception:
            if isinstance(last_exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                # Sanitize error message to prevent API key exposure (issue #7)
                error_msg = sanitize_api_key_for_logging(str(last_exception), self._api_key)
                raise GoogleMapsAPIError(f"Request failed after {max_retries + 1} attempts: {error_msg}") from last_exception
            else:
                raise last_exception
        
        # Should never reach here
        raise GoogleMapsAPIError("Request failed: Unknown error")

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
        """
        Close the HTTP session (idempotent) (issue #17)
        
        Can be called multiple times safely. If session is already closed,
        this method does nothing.
        """
        if hasattr(self, 'session') and self.session is not None:
            try:
                self.session.close()
            except Exception:
                # Ignore errors during cleanup - session may already be closed
                pass
            finally:
                # Mark session as closed to make subsequent calls idempotent
                self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager, ensuring session is closed even if exceptions occur (issue #17)
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        try:
            self.close()
        except Exception:
            # Ignore errors during cleanup to prevent masking original exception
            pass

    def __repr__(self) -> str:
        """String representation of client (issue #52)"""
        return f"{self.__class__.__name__}(api_key='***', base_url={self.base_url!r}, timeout={self.timeout})"

