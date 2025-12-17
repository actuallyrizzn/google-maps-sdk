# Issue #35: Request/Response Interceptors - Solution

## Problem Analysis
The SDK had no way to hook into request/response lifecycle, making it difficult to:
- Add custom logging
- Collect metrics
- Transform requests/responses
- Add custom headers dynamically
- Monitor API usage

## Solution Implemented
Added a comprehensive hook/interceptor system for requests and responses.

### 1. Request Hooks
- Called before each request (GET and POST)
- Receives: `(method, url, headers, params, data)`
- Can modify headers, params, or data
- Called for each retry attempt

### 2. Response Hooks
- Called after each response is received
- Receives: `(response)` - the requests.Response object
- Can inspect or log response data
- Called for successful responses

### 3. Hook Management
- `add_request_hook(hook)`: Add a request hook
- `add_response_hook(hook)`: Add a response hook
- `remove_request_hook(hook)`: Remove a specific hook
- `remove_response_hook(hook)`: Remove a specific hook
- `clear_request_hooks()`: Clear all request hooks
- `clear_response_hooks()`: Clear all response hooks

### 4. Error Handling
- Hook exceptions are caught and logged
- Hook failures don't break requests
- Allows hooks to fail gracefully

## Implementation Details
```python
# Add hooks
def log_request(method, url, headers, params, data):
    print(f"Making {method} request to {url}")

def log_response(response):
    print(f"Response status: {response.status_code}")

client.add_request_hook(log_request)
client.add_response_hook(log_response)
```

## Testing
- Comprehensive interceptor tests (11 tests)
- Tests cover: hook execution, validation, removal, exception handling
- All tests pass ✅

## Files Changed
- `google_maps_sdk/base_client.py`: Added hook system to `_get` and `_post`
- `google_maps_sdk/routes.py`: Added hook calls to overridden `_post`
- `tests/unit/test_interceptors.py`: Interceptor tests

## Benefits
✅ Extensible hook system
✅ Custom logging and metrics
✅ Request/response transformation
✅ Non-breaking (hook exceptions handled)
✅ Easy to add/remove hooks

## Usage Example
```python
from google_maps_sdk import RoutesClient

client = RoutesClient(api_key="YOUR_KEY")

# Add metrics hook
def track_metrics(method, url, headers, params, data):
    metrics.increment("api.requests", tags=[f"method:{method}"])

def log_response(response):
    metrics.timing("api.response_time", response.elapsed.total_seconds())
    metrics.increment("api.responses", tags=[f"status:{response.status_code}"])

client.add_request_hook(track_metrics)
client.add_response_hook(log_response)

# Hooks are called automatically for all requests
result = client.compute_routes(origin, destination)
```
