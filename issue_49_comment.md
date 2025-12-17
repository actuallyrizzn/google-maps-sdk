# Issue #49: Request Compression - Solution

## Problem Analysis
The SDK had no support for gzip compression of large POST requests, resulting in:
- Larger payloads than necessary
- Increased bandwidth usage
- Slower request transmission

## Solution Implemented
Added optional gzip compression for large POST requests with configurable threshold.

### 1. Compression Configuration
- `enable_request_compression`: Boolean flag to enable/disable compression (default: False)
- `compression_threshold`: Minimum payload size in bytes to compress (default: 1024 bytes)

### 2. Implementation Details
- Compression is only applied when:
  - `enable_request_compression` is True
  - Request has data payload
  - Payload size (after JSON encoding) >= `compression_threshold`
- Uses Python's built-in `gzip` module for compression
- Sets `Content-Encoding: gzip` header when compressed
- Sets `Content-Type: application/json` header explicitly
- Logs compression ratio for debugging

### 3. Integration
- Added compression parameters to `BaseClient.__init__`
- Updated `RoutesClient`, `DirectionsClient`, `RoadsClient` to accept and pass compression parameters
- Updated `GoogleMapsClient` to pass compression parameters to sub-clients
- Compression logic integrated into `BaseClient._post` method
- Also integrated into `RoutesClient._post` override

### 4. Testing
- Created comprehensive unit tests:
  - Compression enabled for large payloads
  - Compression disabled when flag is False
  - Compression not applied for small payloads below threshold
  - Verification that compressed data is actually gzip compressed

## Files Changed
- `google_maps_sdk/base_client.py`: Added compression logic and parameters
- `google_maps_sdk/routes.py`: Added compression parameters and logic to `_post` override
- `google_maps_sdk/directions.py`: Added compression parameters
- `google_maps_sdk/roads.py`: Added compression parameters
- `google_maps_sdk/client.py`: Added compression parameters
- `tests/unit/test_request_compression.py`: New test file with 4 comprehensive tests

## Benefits
✅ Reduced bandwidth usage for large requests
✅ Faster request transmission
✅ Configurable threshold for flexibility
✅ Backward compatible (disabled by default)
✅ Automatic compression when enabled and threshold met

## Usage
```python
# Enable compression for requests >= 1KB
client = GoogleMapsClient(
    api_key="YOUR_KEY",
    enable_request_compression=True,
    compression_threshold=1024
)

# Or disable compression (default)
client = GoogleMapsClient(api_key="YOUR_KEY")
```
