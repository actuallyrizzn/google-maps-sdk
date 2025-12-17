# Issue #262: Invalid API Key Format Tests - Solution

## Problem Analysis
The test suite only tested empty/None API keys, missing tests for various invalid formats, resulting in:
- Incomplete validation testing
- Missing tests for whitespace-only keys
- Missing tests for too short keys
- Missing tests for invalid characters
- Missing tests for special characters

## Solution Implemented
Added comprehensive tests for invalid API key formats.

### 1. Invalid Formats Covered
- Whitespace-only keys (spaces, tabs, newlines)
- Too short keys (below minimum length)
- Invalid characters (newlines, tabs, null bytes, control characters)
- Special characters (quotes, backslashes, forward slashes)
- Unicode characters
- Leading/trailing whitespace
- Spaces in middle
- Very long keys
- Type validation (non-string types)
- Validation consistency across clients

### 2. Test Categories
- **Whitespace Tests**: Various whitespace-only scenarios
- **Length Tests**: Too short and very long keys
- **Character Tests**: Invalid, special, Unicode characters
- **Type Tests**: Non-string type validation
- **Client Tests**: Validation consistency across all clients

### 3. Testing
- Created comprehensive test file `tests/unit/test_invalid_api_key_formats.py`
- 22 invalid API key format test scenarios
- Tests BaseClient, RoutesClient, DirectionsClient, RoadsClient, GoogleMapsClient
- Tests validation error messages
- Tests type validation

## Files Changed
- `tests/unit/test_invalid_api_key_formats.py`: New comprehensive invalid API key format test file

## Benefits
✅ Comprehensive invalid API key format coverage
✅ Better detection of validation bugs
✅ Improved confidence in API key validation
✅ Tests validation consistency across clients
✅ Tests various edge cases and invalid formats
