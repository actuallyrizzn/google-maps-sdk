# Issue #31: Environment Variable Configuration - Solution

## Problem Analysis
The SDK required API key to be passed explicitly, making it:
- Less convenient for deployment scenarios
- Requires code changes for different environments
- Not following common Python library patterns

## Solution Implemented
Added support for reading API key from `GOOGLE_MAPS_API_KEY` environment variable.

### 1. Optional API Key Parameter
- All client classes now accept `Optional[str]` for `api_key`
- Defaults to `None` if not provided
- Falls back to environment variable if `None`

### 2. Environment Variable Support
- Checks `GOOGLE_MAPS_API_KEY` environment variable
- Clear error message if neither parameter nor env var is provided
- Explicit parameter takes precedence over environment variable

### 3. Updated Client Classes
- `BaseClient`: Supports optional api_key with env var fallback
- `RoutesClient`: Updated to support optional api_key
- `DirectionsClient`: Updated to support optional api_key
- `RoadsClient`: Updated to support optional api_key
- `GoogleMapsClient`: Updated to support optional api_key

## Implementation Details
```python
# Get API key from parameter or environment variable
if api_key is None:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key is None:
        raise ValueError(
            "API key is required. Provide as parameter or set GOOGLE_MAPS_API_KEY environment variable"
        )
```

## Testing
- Comprehensive environment variable tests (6 tests)
- Tests cover: env var usage, explicit key precedence, error handling
- All tests pass ✅

## Files Changed
- `google_maps_sdk/base_client.py`: Added env var support
- `google_maps_sdk/routes.py`: Made api_key optional
- `google_maps_sdk/directions.py`: Made api_key optional
- `google_maps_sdk/roads.py`: Made api_key optional
- `google_maps_sdk/client.py`: Made api_key optional with env var support
- `tests/unit/test_env_var_config.py`: Environment variable tests

## Benefits
✅ More convenient for deployment scenarios
✅ No code changes needed for different environments
✅ Follows common Python library patterns
✅ Backward compatible (explicit key still works)
✅ Clear error messages

## Usage Example
```python
# Using environment variable
import os
os.environ['GOOGLE_MAPS_API_KEY'] = 'your_key'

from google_maps_sdk import RoutesClient

# No need to pass api_key
client = RoutesClient()
result = client.compute_routes(origin, destination)

# Explicit key still works (takes precedence)
client = RoutesClient(api_key="explicit_key")
```
