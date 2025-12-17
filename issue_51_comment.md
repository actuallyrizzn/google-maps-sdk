# Issue #51: Custom JSON Encoders - Solution

## Problem Analysis
The SDK used default JSON encoding, which cannot handle custom types (datetime, Decimal, custom classes, etc.), resulting in:
- Limited flexibility for complex request bodies
- TypeError when trying to serialize custom types
- No way to customize JSON serialization behavior

## Solution Implemented
Added support for custom JSON encoders to handle custom types and complex request bodies.

### 1. Custom JSON Encoder Configuration
- `json_encoder`: Optional parameter to specify a custom JSON encoder class (default: None)
- Encoder must be a subclass of `json.JSONEncoder`
- Used for all POST request data encoding

### 2. Implementation Details
- Custom encoder is used when encoding data for:
  - Regular POST requests (non-compressed)
  - Compressed POST requests (applied before compression)
- When custom encoder is provided:
  - Data is manually encoded using `json.dumps(data, cls=encoder)`
  - Content-Type header is explicitly set to `application/json`
  - Encoded data is sent as bytes in the `data` parameter
- When no custom encoder is provided:
  - Uses default `requests` library JSON encoding (via `json` parameter)
  - More efficient for standard types

### 3. Integration
- Added `json_encoder` parameter to `BaseClient.__init__`
- Updated `RoutesClient`, `DirectionsClient`, `RoadsClient` to accept and pass encoder
- Updated `GoogleMapsClient` to pass encoder to sub-clients
- Encoder integrated into `BaseClient._post` method
- Also integrated into `RoutesClient._post` override
- Works seamlessly with compression feature (encoder applied before compression)

### 4. Testing
- Created comprehensive unit tests:
  - Custom encoder with datetime/date/Decimal types
  - Custom encoder with custom types
  - Default encoder with standard types
  - Custom encoder with compression
  - Error handling for unhandled types

## Files Changed
- `google_maps_sdk/base_client.py`: Added encoder parameter, storage, and usage in `_post`
- `google_maps_sdk/routes.py`: Added encoder parameter and usage in `_post` override
- `google_maps_sdk/directions.py`: Added encoder parameter
- `google_maps_sdk/roads.py`: Added encoder parameter
- `google_maps_sdk/client.py`: Added encoder parameter
- `tests/unit/test_json_encoder.py`: New test file with 5 comprehensive tests

## Benefits
✅ Support for custom types (datetime, Decimal, custom classes)
✅ Flexible JSON serialization
✅ Works with compression feature
✅ Backward compatible (None uses default encoding)
✅ Type-safe error handling

## Usage
```python
from datetime import datetime
from decimal import Decimal
import json

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Use custom encoder
client = GoogleMapsClient(
    api_key="YOUR_KEY",
    json_encoder=CustomEncoder
)

# Now you can use custom types in requests
data = {
    "timestamp": datetime.now(),
    "price": Decimal("99.99")
}
client.routes._post("/endpoint", data=data)
```
