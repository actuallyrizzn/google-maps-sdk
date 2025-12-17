# Issue #26: Logging Infrastructure - Solution

## Problem Analysis
The SDK had no logging infrastructure, making it difficult to:
- Debug issues in production
- Monitor API usage
- Troubleshoot problems
- Track request/response flows

## Solution Implemented
Added comprehensive structured logging throughout the SDK using Python's standard `logging` module.

### 1. Logger Initialization
- Each client instance gets its own logger
- Logger name: `google_maps_sdk.BaseClient.ClientName`
- Uses standard Python logging module (no external dependencies)

### 2. Logging Points
- **Request logging**: Logs GET/POST requests with URLs and parameters (API keys sanitized)
- **Response logging**: Logs response status codes
- **Error logging**: Logs errors with full exception info
- **Retry logging**: Logs retry attempts and backoff delays
- **HTTP error logging**: Logs HTTP error responses

### 3. Log Levels
- **DEBUG**: Request/response details, retry delays
- **INFO**: Retry attempts
- **WARNING**: Transient failures, HTTP errors
- **ERROR**: Final failures after all retries, unexpected errors

### 4. API Key Sanitization
- All log messages use `sanitize_api_key_for_logging()` to prevent API key exposure
- API keys are replaced with `[API_KEY_REDACTED]` in logs

## Usage Example
```python
import logging
from google_maps_sdk import RoutesClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Or configure specific logger
logging.getLogger('google_maps_sdk').setLevel(logging.DEBUG)

client = RoutesClient(api_key="YOUR_KEY")
result = client.compute_routes(origin, destination)

# Logs will show:
# DEBUG: POST request: https://routes.googleapis.com/... with data keys: ['origin', 'destination', ...]
# DEBUG: POST response: ... - Status: 200
```

## Testing
- Logging is tested implicitly through other tests
- Logger initialization verified
- All log messages sanitize API keys

## Files Changed
- `google_maps_sdk/base_client.py`: Added logging to `_get`, `_post`, `_handle_response`
- `google_maps_sdk/routes.py`: Added logging to overridden `_post` method

## Benefits
✅ Better debugging and troubleshooting
✅ Production monitoring capabilities
✅ Request/response tracking
✅ Error tracking with full context
✅ API keys automatically sanitized in logs
✅ Uses standard library (no dependencies)

## Configuration
Users can configure logging using standard Python logging:
```python
import logging

# Enable debug logging for SDK
logging.getLogger('google_maps_sdk').setLevel(logging.DEBUG)

# Or configure specific client
logging.getLogger('google_maps_sdk.base_client.RoutesClient').setLevel(logging.INFO)
```
