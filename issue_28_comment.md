# Issue #28: Request ID Tracking - Solution

## Problem Analysis
The SDK had no request ID generation or tracking, making it difficult to:
- Correlate requests with responses in logs
- Debug issues in distributed systems
- Track requests across retries
- Debug production issues

## Solution Implemented
Added comprehensive request ID tracking throughout the SDK.

### 1. Request ID Generation
- Each request gets a unique UUID v4 request ID
- Request IDs are generated at the start of each request attempt
- Retries get new request IDs for each attempt

### 2. Request ID in Headers
- Request ID added to `X-Request-ID` header for all requests
- Allows server-side correlation if Google's APIs support it
- Included in both GET and POST requests

### 3. Request ID in Exceptions
- All exceptions include `request_id` attribute
- Request ID appears in exception string representation
- Helps correlate errors with specific requests

### 4. Request ID in Logs
- All log messages include request ID in format `[ID: {request_id}]`
- Makes it easy to filter logs by request
- Enables request tracing through logs

### 5. Exception Updates
- Updated `GoogleMapsAPIError` to accept `request_id` parameter
- All exception subclasses support request_id
- `handle_http_error()` function passes request_id to exceptions

## Implementation Details
```python
# Generate request ID
request_id = str(uuid.uuid4())

# Add to headers
headers['X-Request-ID'] = request_id

# Include in exceptions
error = GoogleMapsAPIError("Error message", request_id=request_id)

# Include in logs
logger.debug(f"Request [ID: {request_id}]: ...")
```

## Testing
- Comprehensive request ID tests (5 tests)
- Tests cover: header inclusion, exception tracking, log inclusion, retry behavior
- All tests pass ✅

## Files Changed
- `google_maps_sdk/base_client.py`: Added request ID generation and tracking to `_get` and `_post`
- `google_maps_sdk/routes.py`: Added request ID tracking to overridden `_post` method
- `google_maps_sdk/exceptions.py`: Added `request_id` support to all exception classes
- `tests/unit/test_request_id_tracking.py`: Request ID tracking tests

## Benefits
✅ Easy request/response correlation
✅ Better debugging in production
✅ Request tracing through logs
✅ Support for distributed systems
✅ Unique IDs for each request attempt

## Usage Example
```python
from google_maps_sdk import RoutesClient

client = RoutesClient(api_key="YOUR_KEY")
try:
    result = client.compute_routes(origin, destination)
except GoogleMapsAPIError as e:
    print(f"Request failed with ID: {e.request_id}")
    # Use request_id to correlate with logs
```
