# Issue #29: Non-JSON Response Handling - Solution

## Problem Analysis
The SDK had inconsistent handling for non-JSON responses:
- Non-JSON success responses returned `{"status": "OK", "raw": response.text}` which is inconsistent
- XML responses were not properly parsed
- No structured way to handle different response formats

## Solution Implemented
Created structured response type classes for different response formats and improved response handling.

### 1. Response Type Classes (`google_maps_sdk/response_types.py`)
- **XMLResponse**: Handles XML responses with parsing and dictionary conversion
- **NonJSONResponse**: Handles other non-JSON formats (plain text, HTML, etc.)

### 2. XMLResponse Features
- Lazy XML parsing (parsed on first access)
- `parsed` property returns ElementTree Element
- `to_dict()` method converts XML to dictionary
- Proper error handling for invalid XML

### 3. NonJSONResponse Features
- Stores response text, content type, and status code
- `to_dict()` method for consistent dictionary format
- Better structure than raw `{"status": "OK", "raw": text}`

### 4. Improved _handle_response
- Detects content type from headers
- Routes XML responses to XMLResponse
- Routes other non-JSON to NonJSONResponse
- Maintains backward compatibility (still returns dict)

## Implementation Details
```python
# Detect content type
content_type = response.headers.get('Content-Type', '').lower()
is_xml = 'xml' in content_type

if is_xml:
    xml_response = XMLResponse(response.text, response.status_code)
    return xml_response.to_dict()
else:
    # Try JSON, fallback to NonJSONResponse
    ...
```

## Testing
- Comprehensive response type tests (7 tests)
- Tests cover: XML parsing, dictionary conversion, error handling, non-JSON handling
- All tests pass ✅

## Files Changed
- `google_maps_sdk/response_types.py`: New response type classes
- `google_maps_sdk/base_client.py`: Updated `_handle_response` to use response types
- `tests/unit/test_response_types.py`: Response type tests

## Benefits
✅ Structured handling of XML responses
✅ Consistent API for different response formats
✅ Better error handling for invalid XML
✅ Backward compatible (still returns dict)
✅ Clear separation of concerns

## Usage
```python
from google_maps_sdk import DirectionsClient

client = DirectionsClient(api_key="YOUR_KEY")
result = client.get_directions("Toronto", "Montreal", output_format="xml")

# Result is now a properly structured dict from XMLResponse.to_dict()
# instead of {"status": "OK", "raw": "<xml>..."}
```
