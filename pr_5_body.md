Fixes #5

## Changes
- Implemented thread-safe RateLimiter class with token bucket algorithm
- Integrated optional rate limiting into BaseClient
- Added rate limiting support to all client classes
- Comprehensive test coverage (22 tests)

## Benefits
✅ Prevents accidental quota exhaustion
✅ Configurable per client instance
✅ Thread-safe implementation
✅ Backward compatible (optional feature)

## Usage
```python
client = RoutesClient(
    api_key="YOUR_KEY",
    rate_limit_max_calls=100,
    rate_limit_period=60.0
)
```
