**Issue #78** from deep code analysis
**Severity:** ⚪ ARCHITECTURE
**Location:** google_maps_sdk/base_client.py:104-151

## Issue Description
Error handling logic is mixed with response parsing.

## Impact
Hard to test and maintain.

## Recommendation
Separate error handling into dedicated methods for better testability and maintainability.
