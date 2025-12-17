# Issue #39: Circuit Breaker Pattern - Solution

## Problem Analysis
The SDK had no circuit breaker for handling repeated failures, causing:
- Continued requests during outages
- Wasted resources and quota
- No automatic recovery mechanism
- Poor resilience during service degradation

## Solution Implemented
Added comprehensive circuit breaker pattern implementation for failure protection.

### 1. CircuitBreaker Class (`google_maps_sdk/circuit_breaker.py`)
- Three states: CLOSED (normal), OPEN (blocking), HALF_OPEN (testing recovery)
- Configurable failure threshold and timeout
- Thread-safe with locks
- Automatic state transitions

### 2. Circuit Breaker Integration
- Optional circuit breaker parameter in all client classes
- Wraps request execution in `_get` and `_post` methods
- Tracks failures and opens circuit after threshold
- Automatically attempts recovery after timeout

### 3. Circuit Breaker States
- **CLOSED**: Normal operation, requests allowed
- **OPEN**: Too many failures, requests blocked immediately
- **HALF_OPEN**: Testing if service recovered, allows one request

### 4. Configuration Parameters
- `failure_threshold`: Number of failures before opening (default: 5)
- `timeout`: Time to wait before half-open attempt (default: 60.0 seconds)
- `expected_exception`: Exception type that counts as failure (default: Exception)

### 5. Client Updates
- All client classes support `circuit_breaker` parameter
- Parameter passed through to BaseClient
- Works with all API clients

## Implementation Details
```python
from google_maps_sdk.circuit_breaker import CircuitBreaker
from google_maps_sdk import RoutesClient

# Create circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60.0
)

# Use with client
client = RoutesClient(
    api_key="YOUR_KEY",
    circuit_breaker=breaker
)

# Circuit breaker automatically protects all requests
result = client.compute_routes(origin, destination)
```

## Testing
- Comprehensive circuit breaker tests (7 tests)
- Tests cover: state transitions, failure tracking, blocking, recovery, reset
- All tests pass ✅

## Files Changed
- `google_maps_sdk/circuit_breaker.py`: New circuit breaker implementation
- `google_maps_sdk/base_client.py`: Integrated circuit breaker into `_get` and `_post`
- `google_maps_sdk/routes.py`: Added circuit breaker to overridden `_post`
- `google_maps_sdk/directions.py`: Added circuit breaker parameter
- `google_maps_sdk/roads.py`: Added circuit breaker parameter
- `google_maps_sdk/client.py`: Added circuit breaker parameter
- `tests/unit/test_circuit_breaker.py`: Comprehensive circuit breaker tests

## Benefits
✅ Prevents wasted requests during outages
✅ Automatic recovery mechanism
✅ Configurable failure threshold and timeout
✅ Thread-safe implementation
✅ Backward compatible (disabled by default)

## Usage Example
```python
from google_maps_sdk.circuit_breaker import CircuitBreaker
from google_maps_sdk import RoutesClient

# Create circuit breaker with custom settings
breaker = CircuitBreaker(
    failure_threshold=5,  # Open after 5 failures
    timeout=60.0  # Wait 60s before attempting recovery
)

client = RoutesClient(
    api_key="YOUR_KEY",
    circuit_breaker=breaker
)

# Circuit breaker automatically protects requests
# After 5 failures, circuit opens and blocks requests
# After 60s, attempts recovery (half-open state)
# On success, circuit closes and normal operation resumes
```
