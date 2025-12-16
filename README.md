# Google Maps Platform Python SDK

A comprehensive Python SDK for Google Maps Platform APIs covering **100% of documented endpoints**:

- ✅ **Routes API** (2 endpoints) - Modern routing with traffic-aware routing
- ✅ **Directions API (Legacy)** (2 endpoints) - Legacy directions service
- ✅ **Roads API** (3 endpoints) - Road snapping and speed limits

## Features

- **Complete Coverage**: All 7 REST API endpoints documented
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Comprehensive exception handling with specific error types
- **Unified Client**: Single client interface for all APIs
- **Context Managers**: Support for `with` statements
- **Flexible**: Use unified client or individual API clients

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

### Unified Client (Recommended)

```python
from google_maps_sdk import GoogleMapsClient

# Initialize client
client = GoogleMapsClient(api_key="YOUR_API_KEY")

# Use Routes API
origin = {"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}}
destination = {"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}}
route = client.routes.compute_routes(origin, destination, routing_preference="TRAFFIC_AWARE")

# Use Directions API
directions = client.directions.get_directions("Toronto", "Montreal")

# Use Roads API
path = [(60.170880, 24.942795), (60.170879, 24.942796)]
snapped = client.roads.snap_to_roads(path, interpolate=True)

# Clean up
client.close()
```

### Individual API Clients

```python
from google_maps_sdk import RoutesClient, DirectionsClient, RoadsClient

# Routes API
routes_client = RoutesClient(api_key="YOUR_API_KEY")
route = routes_client.compute_routes(origin, destination)

# Directions API
directions_client = DirectionsClient(api_key="YOUR_API_KEY")
directions = directions_client.get_directions("Toronto", "Montreal")

# Roads API
roads_client = RoadsClient(api_key="YOUR_API_KEY")
snapped = roads_client.snap_to_roads(path)
```

### Context Manager

```python
from google_maps_sdk import GoogleMapsClient

with GoogleMapsClient(api_key="YOUR_API_KEY") as client:
    route = client.routes.compute_routes(origin, destination)
    # Client automatically closes when exiting context
```

## API Documentation

### Routes API

#### Compute Routes

Calculate a route with traffic-aware routing:

```python
from google_maps_sdk import RoutesClient

client = RoutesClient(api_key="YOUR_API_KEY")

origin = {
    "location": {
        "latLng": {
            "latitude": 37.419734,
            "longitude": -122.0827784
        }
    }
}

destination = {
    "location": {
        "latLng": {
            "latitude": 37.417670,
            "longitude": -122.079595
        }
    }
}

# Basic route
route = client.compute_routes(origin, destination)

# With traffic-aware routing
route = client.compute_routes(
    origin=origin,
    destination=destination,
    routing_preference="TRAFFIC_AWARE",
    departure_time="now",
    compute_alternative_routes=True
)

# With waypoints
intermediates = [
    {"location": {"latLng": {"latitude": 37.415, "longitude": -122.080}}}
]
route = client.compute_routes(
    origin=origin,
    destination=destination,
    intermediates=intermediates,
    optimize_waypoint_order=True
)
```

#### Compute Route Matrix

Compute travel times for multiple origin-destination pairs:

```python
origins = [
    {"location": {"latLng": {"latitude": 37.419734, "longitude": -122.0827784}}},
    {"location": {"latLng": {"latitude": 37.420, "longitude": -122.083}}}
]

destinations = [
    {"location": {"latLng": {"latitude": 37.417670, "longitude": -122.079595}}},
    {"location": {"latLng": {"latitude": 37.418, "longitude": -122.080}}}
]

matrix = client.compute_route_matrix(
    origins=origins,
    destinations=destinations,
    routing_preference="TRAFFIC_AWARE"
)
```

### Directions API (Legacy)

#### Get Directions

```python
from google_maps_sdk import DirectionsClient

client = DirectionsClient(api_key="YOUR_API_KEY")

# Basic directions
result = client.get_directions("Toronto", "Montreal")

# With waypoints
result = client.get_directions(
    origin="Chicago, IL",
    destination="Los Angeles, CA",
    waypoints=["Joplin, MO", "Oklahoma City, OK"]
)

# With traffic information
result = client.get_directions(
    origin="Toronto",
    destination="Montreal",
    departure_time="now",
    traffic_model="best_guess"
)

# Transit directions
result = client.get_directions(
    origin="Brooklyn",
    destination="Queens",
    mode="transit",
    transit_mode=["bus", "subway"]
)
```

### Roads API

#### Snap to Roads

Snap GPS coordinates to the nearest roads:

```python
from google_maps_sdk import RoadsClient

client = RoadsClient(api_key="YOUR_API_KEY")

# GPS path (list of lat/lng tuples)
path = [
    (60.170880, 24.942795),
    (60.170879, 24.942796),
    (60.170877, 24.942796)
]

# Snap to roads
result = client.snap_to_roads(path)

# With interpolation
result = client.snap_to_roads(path, interpolate=True)
```

#### Nearest Roads

Find nearest roads for GPS points:

```python
points = [
    (60.170880, 24.942795),
    (60.170879, 24.942796)
]

result = client.nearest_roads(points)
```

#### Speed Limits

Get speed limits for road segments:

```python
# Using path
path = [(60.170880, 24.942795), (60.170879, 24.942796)]
result = client.speed_limits(path=path)

# Using place IDs
place_ids = ["ChIJ685WIFYViEgRHlHvBbiD5nE", "ChIJA01I-8YVhkgRGJb0fW4UX7Y"]
result = client.speed_limits(place_ids=place_ids)
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from google_maps_sdk import (
    GoogleMapsClient,
    InvalidRequestError,
    PermissionDeniedError,
    NotFoundError,
    QuotaExceededError,
    InternalServerError,
)

client = GoogleMapsClient(api_key="YOUR_API_KEY")

try:
    route = client.routes.compute_routes(origin, destination)
except InvalidRequestError as e:
    print(f"Invalid request: {e.message}")
except PermissionDeniedError as e:
    print(f"Permission denied: {e.message}")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e.message}")
except GoogleMapsAPIError as e:
    print(f"API error: {e.message}")
```

## Complete Endpoint Coverage

### Routes API (2 endpoints)
- ✅ `POST /directions/v2:computeRoutes` - Calculate routes
- ✅ `POST /distanceMatrix/v2:computeRouteMatrix` - Route matrix

### Directions API (2 endpoints)
- ✅ `GET /json` - Directions in JSON format
- ✅ `GET /xml` - Directions in XML format

### Roads API (3 endpoints)
- ✅ `GET /snapToRoads` - Snap GPS path to roads
- ✅ `GET /nearestRoads` - Find nearest roads
- ✅ `GET /speedLimits` - Get speed limits

**Total: 7 REST API endpoints - 100% coverage**

## Requirements

- Python 3.8+
- requests >= 2.31.0

## Documentation

See the [docs](./docs/) directory for comprehensive API documentation:

- [Routes API Endpoints](./docs/routes-api-endpoints.md)
- [Directions API Endpoints](./docs/directions-api-endpoints.md)
- [Roads API Endpoints](./docs/roads-api-endpoints.md)
- [Complete Endpoint Reference](./docs/complete-endpoint-reference.md)

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Check the [documentation](./docs/)
- Open an issue on GitHub
