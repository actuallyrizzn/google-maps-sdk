# Issue #37: Caching Mechanism - Solution

## Problem Analysis
The SDK had no built-in caching for responses, causing:
- Repeated identical requests waste API quota
- Unnecessary network overhead
- Slower response times for repeated queries

## Solution Implemented
Added optional TTL (Time-To-Live) caching mechanism for API responses.

### 1. TTLCache Implementation (`google_maps_sdk/cache.py`)
- Simple TTL cache with expiration
- Configurable maxsize and TTL
- Automatic eviction of expired entries
- LRU-style eviction when cache is full

### 2. Cache Key Generation
- `generate_cache_key()` function creates MD5 hash from request parameters
- Includes: method, URL, params, and data
- Ensures identical requests get same cache key

### 3. Cache Integration
- Optional caching (disabled by default for backward compatibility)
- Cache checked before making requests
- Successful responses cached after handling
- Only caches on first successful attempt (not retries)

### 4. Configuration Parameters
- `enable_cache`: Enable/disable caching (default: False)
- `cache_ttl`: Time-to-live in seconds (default: 300.0 = 5 minutes)
- `cache_maxsize`: Maximum number of cached responses (default: 100)

### 5. Client Updates
- All client classes support cache parameters
- Parameters passed through to BaseClient
- Works with all API clients (Routes, Directions, Roads)

## Implementation Details
```python
# Enable caching
client = RoutesClient(
    api_key="YOUR_KEY",
    enable_cache=True,
    cache_ttl=300.0,  # 5 minutes
    cache_maxsize=100
)

# First request - makes API call
result1 = client.compute_routes(origin, destination)

# Second identical request - uses cache
result2 = client.compute_routes(origin, destination)  # No API call!
```

## Testing
- Comprehensive cache tests (13 tests)
- Tests cover: TTL expiration, maxsize, cache hits/misses, GET/POST caching
- All tests pass ✅

## Files Changed
- `google_maps_sdk/cache.py`: New TTL cache implementation
- `google_maps_sdk/base_client.py`: Integrated caching into `_get` and `_post`
- `google_maps_sdk/routes.py`: Added caching to overridden `_post`
- `google_maps_sdk/directions.py`: Added cache parameters
- `google_maps_sdk/roads.py`: Added cache parameters
- `google_maps_sdk/client.py`: Added cache parameters
- `tests/unit/test_cache.py`: Comprehensive cache tests

## Benefits
✅ Reduces API quota usage for repeated requests
✅ Faster response times for cached requests
✅ Configurable TTL and cache size
✅ Backward compatible (disabled by default)
✅ Automatic expiration and eviction

## Usage Example
```python
from google_maps_sdk import RoutesClient

# Enable caching with 5-minute TTL
client = RoutesClient(
    api_key="YOUR_KEY",
    enable_cache=True,
    cache_ttl=300.0,
    cache_maxsize=100
)

# First call makes API request
result1 = client.compute_routes(origin, destination)

# Second identical call uses cache (no API request)
result2 = client.compute_routes(origin, destination)
```
