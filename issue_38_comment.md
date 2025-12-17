# Issue #38: Custom HTTP Adapters - Solution

## Problem Analysis
The SDK had no support for custom HTTP adapters, limiting deployment flexibility:
- Cannot use proxies
- Cannot customize SSL settings
- Cannot use custom connection pooling configurations
- Limited deployment options

## Solution Implemented
Added support for custom HTTPAdapter instances to be provided during client initialization.

### 1. HTTPAdapter Parameter
- `http_adapter` parameter added to all client classes
- Optional parameter (None uses default adapter)
- Custom adapter takes precedence over default configuration

### 2. Adapter Mounting
- Custom adapter mounted for both `https://` and `http://` protocols
- Works with thread-local sessions
- Each thread gets its own session with the adapter

### 3. Default Behavior
- When `http_adapter` is None, uses default adapter with configured pooling
- Maintains backward compatibility
- Default adapter still has optimized pooling settings

### 4. Client Updates
- All client classes support `http_adapter` parameter
- Parameter passed through to BaseClient
- Works with all API clients

## Implementation Details
```python
from requests.adapters import HTTPAdapter

# Create custom adapter (e.g., for proxy)
custom_adapter = HTTPAdapter(
    pool_connections=5,
    pool_maxsize=10
)

client = RoutesClient(
    api_key="YOUR_KEY",
    http_adapter=custom_adapter
)
```

## Testing
- Comprehensive adapter tests (4 tests)
- Tests cover: custom adapter usage, default behavior, thread-local behavior
- All tests pass ✅

## Files Changed
- `google_maps_sdk/base_client.py`: Added `http_adapter` parameter and mounting logic
- `google_maps_sdk/routes.py`: Added `http_adapter` parameter
- `google_maps_sdk/directions.py`: Added `http_adapter` parameter
- `google_maps_sdk/roads.py`: Added `http_adapter` parameter
- `google_maps_sdk/client.py`: Added `http_adapter` parameter
- `tests/unit/test_custom_http_adapter.py`: Custom adapter tests

## Benefits
✅ Support for proxies
✅ Custom SSL configuration
✅ Custom connection pooling
✅ Deployment flexibility
✅ Backward compatible (default adapter used if None)

## Usage Example
```python
from requests.adapters import HTTPAdapter
from google_maps_sdk import RoutesClient

# Custom adapter for proxy support
adapter = HTTPAdapter(
    pool_connections=5,
    pool_maxsize=10
)

client = RoutesClient(
    api_key="YOUR_KEY",
    http_adapter=adapter
)

# All requests will use the custom adapter
result = client.compute_routes(origin, destination)
```
