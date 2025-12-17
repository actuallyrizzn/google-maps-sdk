# Proposed Solution for Issue #278: Custom Exception Handlers

## Problem Analysis
Currently, exception handling behavior cannot be customized. Users cannot add custom exception handler callbacks to modify how exceptions are handled.

## Proposed Solution

### 1. Add Exception Handler Callback Support
- Add `exception_handler` parameter to client constructors
- Handler is a callable that receives exception and can modify/transform it
- Handler can return a modified exception or raise a different exception

### 2. Integration Points
- Call handler in `_handle_response` before raising exceptions
- Call handler in retry logic before re-raising
- Call handler in circuit breaker before raising CircuitBreakerOpenError

### 3. Handler Signature
- Handler receives: (exception, request_info) -> exception or None
- If handler returns None, original exception is raised
- If handler returns/raises exception, that exception is used

### 4. Add to ClientConfig
- Include `exception_handler` in ClientConfig

## Implementation Plan
1. Add `exception_handler` parameter to BaseClient
2. Call handler at exception points
3. Add to ClientConfig
4. Add comprehensive tests
5. Document usage

## Benefits
✅ Customizable exception handling
✅ Better error transformation
✅ Integration with logging/monitoring
✅ Flexible error handling strategies
✅ Backward compatible (optional)
