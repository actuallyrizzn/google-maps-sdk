# Issue #11: Retry Logic with Exponential Backoff - Solution

## Problem Analysis
The SDK had no automatic retry for transient failures, forcing users to implement their own retry logic, leading to inconsistent behavior and code duplication.

## Solution Implemented
Implemented comprehensive retry logic with exponential backoff for handling transient failures.

### 1. Retry Module (`google_maps_sdk/retry.py`)
- `RetryConfig` class for configuring retry behavior
- `should_retry()` function to determine if an exception should trigger retry
- `exponential_backoff()` function for calculating backoff delays
- `retry_with_backoff()` decorator (for future use)
- Retries on: timeouts, connection errors, 5xx server errors
- Does NOT retry on: 4xx client errors, 429 rate limit errors

### 2. BaseClient Integration
- Optional retry configuration (disabled by default for backward compatibility)
- Retry logic integrated into `_get` and `_post` methods
- Exponential backoff with configurable parameters:
  - `max_retries`: Maximum retry attempts (default: 3)
  - `base_delay`: Initial delay in seconds (default: 1.0)
  - `max_delay`: Maximum delay cap (default: 60.0)
  - `exponential_base`: Base for exponential calculation (default: 2.0)
  - `jitter`: Random jitter to prevent thundering herd (default: True)

### 3. RoutesClient Integration
- RoutesClient overrides `_post`, so retry logic added there as well
- Maintains header-based authentication while adding retry support

### 4. Client Class Updates
- All client classes (RoutesClient, DirectionsClient, RoadsClient, GoogleMapsClient) support `retry_config` parameter
- Backward compatible - retry is optional

## Usage Example
```python
from google_maps_sdk import RoutesClient, RetryConfig

# Enable retry: 3 attempts with exponential backoff
retry_config = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)

client = RoutesClient(
    api_key="YOUR_KEY",
    retry_config=retry_config
)

# Transient failures will be automatically retried
result = client.compute_routes(origin, destination)
```

## Testing
- Comprehensive unit tests for retry module (15 tests)
- Tests cover: config validation, retry decision logic, exponential backoff calculation, retry decorator
- All tests pass ✅

## Files Changed
- `google_maps_sdk/retry.py`: New retry implementation
- `google_maps_sdk/base_client.py`: Integrated retry logic
- `google_maps_sdk/routes.py`: Added retry logic to overridden `_post` method
- `google_maps_sdk/directions.py`: Added retry_config parameter
- `google_maps_sdk/roads.py`: Added retry_config parameter
- `google_maps_sdk/client.py`: Added retry_config parameter
- `tests/unit/test_retry.py`: Comprehensive retry tests

## Benefits
✅ Automatic handling of transient failures
✅ Configurable retry behavior
✅ Exponential backoff prevents overwhelming servers
✅ Jitter prevents thundering herd problem
✅ Backward compatible (optional feature)
✅ Clear error messages after all retries exhausted
