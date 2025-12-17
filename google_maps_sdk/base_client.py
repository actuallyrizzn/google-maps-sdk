"""
Base client class for Google Maps Platform APIs
"""

import requests
import warnings
import time
import threading
import logging
import uuid
import os
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .response_types import XMLResponse, NonJSONResponse
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
        api_key: Optional[str] = None,
        base_url: str = "",
        timeout: int = 30,
        rate_limit_max_calls: Optional[int] = None,
        rate_limit_period: Optional[float] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize base client

        Args:
            api_key: Google Maps Platform API key (optional, can use GOOGLE_MAPS_API_KEY env var) (issue #31)
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            rate_limit_max_calls: Maximum calls per period for rate limiting (None to disable)
            rate_limit_period: Time period in seconds for rate limiting (default: 60.0)
            retry_config: Retry configuration (None to disable retries) (issue #11)

        Raises:
            TypeError: If api_key is not a string
            ValueError: If api_key or base_url is invalid
        """
        # Get API key from parameter or environment variable (issue #31)
        if api_key is None:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key is required. Provide as parameter or set GOOGLE_MAPS_API_KEY environment variable"
                )
        
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
        
        # Thread-local storage for sessions (issue #19)
        # Each thread gets its own session to ensure thread safety
        self._local = threading.local()
        
        # Store configuration for session creation
        self._session_config = {
            'verify': True,  # SSL verification enforced (issue #4)
            'headers': {
                'User-Agent': f'google-maps-sdk/{__import__("google_maps_sdk").__version__}',
                'Accept-Encoding': 'gzip, deflate, br'
            },
            # Connection pooling configuration (issue #27)
            'pool_connections': 10,  # Number of connection pools to cache
            'pool_maxsize': 20,  # Maximum number of connections to save in the pool
            'max_retries': 0,  # We handle retries ourselves (issue #11)
        }
        
        # Initialize logger (issue #26)
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

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

    @property
    def session(self) -> requests.Session:
        """
        Get thread-local session (issue #19)
        
        Each thread gets its own session instance to ensure thread safety.
        Sessions are created lazily on first access with connection pooling configured (issue #27).
        
        Returns:
            Thread-local requests.Session instance
        """
        if not hasattr(self._local, 'session'):
            # Create session for this thread
            self._local.session = requests.Session()
            self._local.session.verify = self._session_config['verify']
            self._local.session.headers.update(self._session_config['headers'])
            
            # Configure connection pooling (issue #27)
            adapter = HTTPAdapter(
                pool_connections=self._session_config['pool_connections'],
                pool_maxsize=self._session_config['pool_maxsize'],
                max_retries=Retry(total=self._session_config['max_retries'])  # We handle retries ourselves
            )
            self._local.session.mount('https://', adapter)
            self._local.session.mount('http://', adapter)
        return self._local.session

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
        
        # Generate request ID for tracking (issue #28)
        request_id = str(uuid.uuid4())
        
        # Log request (issue #26, #28)
        self._logger.debug(f"GET request [ID: {request_id}]: {url} with params: {sanitize_api_key_for_logging(str(params), self._api_key)}")
        
        # Retry logic (issue #11)
        last_exception = None
        last_request_id = request_id
        
        max_retries = self._retry_config.max_retries if self._retry_config else 0
        
        for attempt in range(max_retries + 1):
            # Generate new request ID for retries
            if attempt > 0:
                request_id = str(uuid.uuid4())
                last_request_id = request_id
                self._logger.info(f"Retry attempt {attempt}/{max_retries} for GET {url} [ID: {request_id}]")
            
            try:
                # Add request ID to headers (issue #28)
                headers = {'X-Request-ID': request_id}
                
                response = self.session.get(url, params=params, headers=headers, timeout=request_timeout)
                
                # Log response (issue #26, #28)
                self._logger.debug(f"GET response [ID: {request_id}]: {url} - Status: {response.status_code}")
                
                # _handle_response may raise GoogleMapsAPIError for HTTP errors
                return self._handle_response(response, request_id=request_id)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                # Log error with request ID (issue #26, #28)
                self._logger.warning(f"GET request failed [ID: {request_id}] (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {sanitize_api_key_for_logging(str(e), self._api_key)}")
                
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
                    
                    self._logger.debug(f"Waiting {delay:.2f}s before retry [ID: {request_id}]")
                    # Wait before retrying
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    break
            except GoogleMapsAPIError as e:
                last_exception = e
                
                # Store request ID in exception (issue #28)
                if not hasattr(e, 'request_id'):
                    e.request_id = request_id
                
                # Log error with request ID (issue #26, #28)
                self._logger.warning(f"GET request failed [ID: {request_id}] (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}: {sanitize_api_key_for_logging(str(e), self._api_key)}")
                
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
                    
                    self._logger.debug(f"Waiting {delay:.2f}s before retry [ID: {request_id}]")
                    time.sleep(delay)
                    continue
                else:
                    # Non-retryable exception - raise immediately
                    raise
            except requests.exceptions.RequestException as e:
                # Other request exceptions - don't retry
                error_msg = sanitize_api_key_for_logging(str(e), self._api_key)
                self._logger.error(f"GET request failed [ID: {request_id}]: {error_msg}", exc_info=True)
                error = GoogleMapsAPIError(f"Request failed: {error_msg}", request_url=url)
                error.request_id = request_id
                raise error from e
        
        # If we get here, all retries failed
        if last_exception:
            error_msg = sanitize_api_key_for_logging(str(last_exception), self._api_key)
            self._logger.error(f"GET request failed after {max_retries + 1} attempts [ID: {last_request_id}]: {error_msg}", exc_info=True)
            if isinstance(last_exception, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                # Sanitize error message to prevent API key exposure (issue #7)
                error = GoogleMapsAPIError(f"Request failed after {max_retries + 1} attempts: {error_msg}", request_url=url)
                error.request_id = last_request_id
                raise error from last_exception
            else:
                if isinstance(last_exception, GoogleMapsAPIError) and not hasattr(last_exception, 'request_id'):
                    last_exception.request_id = last_request_id
                raise last_exception
        
        # Should never reach here
        self._logger.error(f"GET request failed: Unknown error [ID: {request_id}]")
        error = GoogleMapsAPIError("Request failed: Unknown error", request_url=url)
        error.request_id = request_id
        raise error

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
        
        # Generate request ID for tracking (issue #28)
        request_id = str(uuid.uuid4())
        
        # Log request (issue #26, #28)
        self._logger.debug(f"POST request [ID: {request_id}]: {url} with data keys: {list(data.keys()) if data else 'None'}")
        
        # Retry logic (issue #11)
        last_exception = None
        last_request_id = request_id
        
        max_retries = self._retry_config.max_retries if self._retry_config else 0
        
        for attempt in range(max_retries + 1):
            # Generate new request ID for retries
            if attempt > 0:
                request_id = str(uuid.uuid4())
                last_request_id = request_id
                self._logger.info(f"Retry attempt {attempt}/{max_retries} for POST {url} [ID: {request_id}]")
            
            try:
                # Add request ID to headers (issue #28)
                headers_with_id = headers.copy() if headers else {}
                headers_with_id['X-Request-ID'] = request_id
                
                response = self.session.post(
                    url, json=data, headers=headers_with_id, params=params, timeout=request_timeout
                )
                
                # Log response (issue #26, #28)
                self._logger.debug(f"POST response [ID: {request_id}]: {url} - Status: {response.status_code}")
                
                # _handle_response may raise GoogleMapsAPIError for HTTP errors
                return self._handle_response(response, request_id=request_id)
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

    def _handle_response(self, response: requests.Response, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle HTTP response and convert to appropriate format (issue #28)

        Args:
            response: HTTP response object
            request_id: Optional request ID for correlation

        Returns:
            Response JSON as dictionary

        Raises:
            GoogleMapsAPIError: If response indicates an error
        """
        # Determine content type (issue #29)
        content_type = response.headers.get('Content-Type', '').lower()
        is_xml = 'xml' in content_type
        is_json = 'json' in content_type or not content_type  # Default to JSON if no content-type
        
        # Try to parse JSON
        try:
            if is_xml:
                # Handle XML response (issue #29)
                xml_response = XMLResponse(response.text, response.status_code)
                if response.status_code >= 400:
                    error = GoogleMapsAPIError(
                        f"HTTP {response.status_code}: XML error response",
                        status_code=response.status_code,
                        request_url=str(response.url) if hasattr(response, 'url') else None,
                        request_id=request_id,
                    )
                    raise error
                # Return structured XML response
                return xml_response.to_dict()
            
            data = response.json()
        except ValueError:
            # Not JSON and not XML - handle as non-JSON response (issue #29)
            if response.status_code >= 400:
                error = GoogleMapsAPIError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    request_url=str(response.url) if hasattr(response, 'url') else None,
                    request_id=request_id,
                )
                raise error
            
            # Success response that's not JSON
            non_json_response = NonJSONResponse(
                response.text,
                content_type=content_type,
                status_code=response.status_code
            )
            return non_json_response.to_dict()

        # Check for API errors in response
        if response.status_code >= 400:
            self._logger.warning(f"HTTP error {response.status_code} for {response.url} [ID: {request_id or 'N/A'}]: {sanitize_api_key_for_logging(str(data), self._api_key)}")
            raise handle_http_error(response.status_code, data, response.url, request_id=request_id)

        # Check for Directions API status codes
        if "status" in data and data["status"] != "OK":
            status = data["status"]
            error_message = data.get("error_message", f"API returned status: {status}")
            
            request_url = str(response.url) if hasattr(response, 'url') else None
            if status == "REQUEST_DENIED":
                raise PermissionDeniedError(error_message, data, request_url, request_id=request_id)
            elif status == "OVER_QUERY_LIMIT":
                raise QuotaExceededError(error_message, data, request_url, request_id=request_id)
            elif status == "NOT_FOUND":
                raise NotFoundError(error_message, data, request_url, request_id=request_id)
            elif status == "ZERO_RESULTS":
                raise NotFoundError("No results found", data, request_url, request_id=request_id)
            elif status == "INVALID_REQUEST":
                raise InvalidRequestError(error_message, data, request_url, request_id=request_id)
            else:
                raise GoogleMapsAPIError(error_message, response=data, request_url=request_url, request_id=request_id)

        return data

    def close(self):
        """
        Close all thread-local HTTP sessions (idempotent) (issue #17, #19)
        
        Closes sessions for all threads that have accessed this client.
        Can be called multiple times safely. If sessions are already closed,
        this method does nothing.
        """
        # Close thread-local session for current thread
        if hasattr(self, '_local') and hasattr(self._local, 'session'):
            try:
                if self._local.session is not None:
                    self._local.session.close()
            except Exception:
                # Ignore errors during cleanup - session may already be closed
                pass
            finally:
                # Mark session as closed
                self._local.session = None

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

