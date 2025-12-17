# Proposed Solution for Issue #270: API Versioning Support

## Problem Analysis
Currently, API endpoints are hardcoded with specific versions:
- Routes API: `https://routes.googleapis.com/directions/v2:computeRoutes` (hardcoded v2)
- Roads API: `https://roads.googleapis.com/v1/snapToRoads` (hardcoded v1)
- Directions API: `https://maps.googleapis.com/maps/api/directions` (no version in path, but legacy)

## Proposed Solution

### 1. Add API Version Parameter
- Add `api_version` parameter to client constructors (defaults to current version)
- RoutesClient: default `api_version="v2"`
- RoadsClient: default `api_version="v1"`
- DirectionsClient: no version (legacy API, but could support future versions)

### 2. Update Endpoint Construction
- Modify endpoint construction to use version parameter
- Routes API: `/directions/{version}:computeRoutes` instead of hardcoded `/directions/v2:computeRoutes`
- Roads API: `/v{version}/snapToRoads` instead of hardcoded `/v1/snapToRoads`

### 3. Add to ClientConfig
- Include `api_version` in `ClientConfig` dataclass for centralized configuration

### 4. Validation
- Validate version format (e.g., "v1", "v2", "v3")
- Ensure backward compatibility with default versions

### 5. Testing
- Test with different API versions
- Test default version behavior
- Test version validation

## Implementation Plan
1. Add `api_version` parameter to RoutesClient, RoadsClient, DirectionsClient
2. Update endpoint construction methods to use version parameter
3. Add version to ClientConfig
4. Add validation for version format
5. Add comprehensive tests
6. Update documentation

## Benefits
✅ Support for multiple API versions
✅ Future-proof for new API versions
✅ Backward compatible (defaults to current versions)
✅ Centralized configuration via ClientConfig
