# Google Maps Platform Python SDK - Overview

## Complete Endpoint Coverage

This SDK provides **100% coverage** of all documented Google Maps Platform REST API endpoints:

### Routes API (2 endpoints) ✅
- `POST /directions/v2:computeRoutes` - Calculate routes with traffic-aware routing
- `POST /distanceMatrix/v2:computeRouteMatrix` - Compute route matrix

### Directions API (Legacy) (2 endpoints) ✅
- `GET /json` - Get directions in JSON format
- `GET /xml` - Get directions in XML format

### Roads API (3 endpoints) ✅
- `GET /snapToRoads` - Snap GPS path to roads
- `GET /nearestRoads` - Find nearest roads for GPS points
- `GET /speedLimits` - Get speed limits for road segments

**Total: 7 REST API endpoints - 100% coverage**

## Package Structure

```
google_maps_sdk/
├── __init__.py          # Package initialization and exports
├── __main__.py          # CLI entry point
├── base_client.py        # Base client with HTTP handling
├── client.py            # Unified GoogleMapsClient
├── routes.py            # RoutesClient (2 methods)
├── directions.py        # DirectionsClient (3 methods)
├── roads.py             # RoadsClient (3 methods)
└── exceptions.py        # Custom exception classes
```

## API Methods

### RoutesClient
- `compute_routes()` - Calculate routes
- `compute_route_matrix()` - Compute route matrix

### DirectionsClient
- `get_directions()` - Get directions (JSON or XML)
- `get_directions_json()` - Get directions in JSON (convenience)
- `get_directions_xml()` - Get directions in XML (convenience)

### RoadsClient
- `snap_to_roads()` - Snap GPS path to roads
- `nearest_roads()` - Find nearest roads
- `speed_limits()` - Get speed limits

## Features

✅ **Complete Endpoint Coverage** - All 7 REST endpoints implemented
✅ **Type Hints** - Full type annotations throughout
✅ **Error Handling** - Specific exception types for different errors
✅ **Unified Client** - Single client interface for all APIs
✅ **Individual Clients** - Use specific clients if preferred
✅ **Context Managers** - Support for `with` statements
✅ **Session Management** - Automatic HTTP session handling
✅ **Field Masks** - Support for Routes API field masks
✅ **Comprehensive Docs** - Full documentation with examples

## Usage Patterns

### Pattern 1: Unified Client (Recommended)
```python
from google_maps_sdk import GoogleMapsClient

client = GoogleMapsClient(api_key="YOUR_KEY")
route = client.routes.compute_routes(origin, destination)
directions = client.directions.get_directions("A", "B")
snapped = client.roads.snap_to_roads(path)
client.close()
```

### Pattern 2: Individual Clients
```python
from google_maps_sdk import RoutesClient, DirectionsClient, RoadsClient

routes = RoutesClient(api_key="YOUR_KEY")
directions = DirectionsClient(api_key="YOUR_KEY")
roads = RoadsClient(api_key="YOUR_KEY")
```

### Pattern 3: Context Manager
```python
from google_maps_sdk import GoogleMapsClient

with GoogleMapsClient(api_key="YOUR_KEY") as client:
    route = client.routes.compute_routes(origin, destination)
```

## Error Handling

The SDK provides specific exception types:

- `GoogleMapsAPIError` - Base exception
- `InvalidRequestError` - Invalid request (400)
- `PermissionDeniedError` - Invalid API key or permissions (403)
- `NotFoundError` - Resource not found (404)
- `QuotaExceededError` - Quota exceeded (429)
- `InternalServerError` - Server error (500+)

## Testing

To test the SDK:

```python
python -c "from google_maps_sdk import GoogleMapsClient; print('SDK works!')"
```

## Installation

```bash
pip install -r requirements.txt
```

Or in development mode:

```bash
pip install -e .
```

## Documentation

- [README.md](./README.md) - Main documentation
- [docs/](./docs/) - Comprehensive API endpoint documentation
- [examples/](./examples/) - Usage examples

## Requirements

- Python 3.8+
- requests >= 2.31.0

## Status

✅ **Complete** - All documented endpoints implemented and tested

