# Proposed Solution for Issue #272: Separation of Concerns for Error Handling

## Problem Analysis
Currently, `_handle_response` in `base_client.py` mixes response parsing with error handling:
- Response parsing (JSON/XML/non-JSON)
- HTTP error checking
- Directions API status code checking
- Exception raising

This makes the code hard to test and maintain.

## Proposed Solution

### 1. Separate Response Parsing
- Create `_parse_response()` method to handle response parsing only
- Returns parsed data (dict) or response type objects
- No error handling logic

### 2. Separate HTTP Error Handling
- Create `_check_http_errors()` method to check for HTTP status codes
- Raises appropriate exceptions for HTTP errors
- Takes parsed data and response object

### 3. Separate Directions API Error Handling
- Create `_check_directions_api_errors()` method to check Directions API status codes
- Raises appropriate exceptions for Directions API errors
- Takes parsed data and response object

### 4. Refactor `_handle_response`
- Call `_parse_response()` first
- Call `_check_http_errors()` if needed
- Call `_check_directions_api_errors()` if needed
- Return parsed data

## Implementation Plan
1. Create `_parse_response()` method for response parsing
2. Create `_check_http_errors()` method for HTTP error checking
3. Create `_check_directions_api_errors()` method for Directions API error checking
4. Refactor `_handle_response()` to use these methods
5. Add comprehensive tests for each method
6. Ensure backward compatibility

## Benefits
✅ Better separation of concerns
✅ Easier to test individual components
✅ More maintainable code
✅ Clearer code structure
✅ Easier to extend error handling
