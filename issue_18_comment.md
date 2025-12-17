# Issue #18: Type Hints for Return Values - Solution

## Problem Analysis
Methods were returning `Dict[str, Any]` without more specific typing, leading to:
- Poor IDE support and autocomplete
- No type checking capabilities
- Unclear API contracts for users

## Solution Implemented
Added TypedDict definitions for all API response types to provide better type hints and IDE support.

### TypedDict Classes Added (`google_maps_sdk/types.py`)
1. **RouteResponse** - For `RoutesClient.compute_routes()` responses
2. **RouteMatrixResponse** - For `RoutesClient.compute_route_matrix()` responses
3. **DirectionsResponse** - For `DirectionsClient.get_directions()` responses
4. **SnapToRoadsResponse** - For `RoadsClient.snap_to_roads()` responses
5. **NearestRoadsResponse** - For `RoadsClient.nearest_roads()` responses
6. **SpeedLimitsResponse** - For `RoadsClient.speed_limits()` responses

### Method Return Type Updates
- `RoutesClient.compute_routes()` → `RouteResponse`
- `RoutesClient.compute_route_matrix()` → `RouteMatrixResponse`
- `DirectionsClient.get_directions()` → `DirectionsResponse`
- `RoadsClient.snap_to_roads()` → `SnapToRoadsResponse`
- `RoadsClient.nearest_roads()` → `NearestRoadsResponse`
- `RoadsClient.speed_limits()` → `SpeedLimitsResponse`

### TypedDict Design
- Used `total=False` to make all fields optional (flexible for partial responses)
- Defined main structure while allowing for dynamic fields
- Exported in `__init__.py` for easy import

## Benefits
✅ Better IDE autocomplete and type checking
✅ Clearer API contracts
✅ Improved developer experience
✅ Backward compatible (runtime behavior unchanged)
✅ Type checkers (mypy, pyright) can validate usage

## Usage Example
```python
from google_maps_sdk import RoutesClient, RouteResponse

client = RoutesClient(api_key="YOUR_KEY")
result: RouteResponse = client.compute_routes(origin, destination)

# IDE now knows result has 'routes' field
routes = result["routes"]  # Type checker validates this
```

## Files Changed
- `google_maps_sdk/types.py`: Added TypedDict definitions for all response types
- `google_maps_sdk/routes.py`: Updated return types to RouteResponse/RouteMatrixResponse
- `google_maps_sdk/directions.py`: Updated return type to DirectionsResponse
- `google_maps_sdk/roads.py`: Updated return types to Roads API response types
- `google_maps_sdk/__init__.py`: Exported new TypedDict classes

## Notes
- TypedDict uses `total=False` to allow partial responses (field masks, etc.)
- Runtime behavior is unchanged - this is purely a type hint improvement
- Compatible with mypy, pyright, and other type checkers
