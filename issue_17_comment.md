# Issue #17: Session Close on Exception - Solution

## Problem Analysis
The SDK had issues with session cleanup:
- If exception occurs in `__exit__`, session may not be closed
- `close()` is not idempotent - calling it multiple times may raise exceptions
- No check if session is already closed

This could lead to resource leaks if exceptions occur during context manager exit.

## Solution Implemented
Made session closing robust and idempotent:

### 1. Idempotent `close()` Method
- Can be called multiple times safely
- Checks if session exists and is not None before closing
- Handles exceptions during close gracefully
- Sets session to None after closing to mark as closed

### 2. Exception-Safe `__exit__` Method
- Wraps `close()` in try-except to handle exceptions during cleanup
- Prevents cleanup exceptions from masking original exceptions
- Ensures session is closed even if exceptions occur

### 3. GoogleMapsClient Updates
- Updated `close()` to handle exceptions from sub-clients
- Updated `__exit__` to be exception-safe

## Implementation Details
```python
def close(self):
    """Close the HTTP session (idempotent)"""
    if hasattr(self, 'session') and self.session is not None:
        try:
            self.session.close()
        except Exception:
            pass  # Ignore errors during cleanup
        finally:
            self.session = None  # Mark as closed

def __exit__(self, exc_type, exc_val, exc_tb):
    """Exit context manager, ensuring session is closed"""
    try:
        self.close()
    except Exception:
        pass  # Ignore errors during cleanup
```

## Testing
- Comprehensive unit tests (7 tests)
- Tests cover: successful close, idempotency, exception handling, context manager behavior
- All tests pass ✅

## Files Changed
- `google_maps_sdk/base_client.py`: Made `close()` idempotent and `__exit__` exception-safe
- `google_maps_sdk/client.py`: Updated `close()` and `__exit__` for exception safety
- `tests/unit/test_base_client_close.py`: Comprehensive close/context manager tests

## Benefits
✅ No resource leaks even if exceptions occur
✅ `close()` can be called multiple times safely
✅ Context manager always cleans up properly
✅ Cleanup exceptions don't mask original exceptions
