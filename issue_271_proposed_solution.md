# Proposed Solution for Issue #271: Regional Endpoints Support

## Problem Analysis
Currently, API endpoints are hardcoded to global endpoints:
- Routes API: `https://routes.googleapis.com` (global only)
- Roads API: `https://roads.googleapis.com` (global only)
- Directions API: `https://maps.googleapis.com` (global only)

Google Cloud APIs support regional endpoints for lower latency (e.g., `us-central1`, `europe-west1`, `asia-east1`).

## Proposed Solution

### 1. Add Regional Endpoint Parameter
- Add `region` parameter to client constructors (defaults to None for global)
- RoutesClient: support regional endpoints like `routes-{region}.googleapis.com`
- RoadsClient: support regional endpoints like `roads-{region}.googleapis.com`
- DirectionsClient: may not support regional endpoints (legacy API)

### 2. Update Base URL Construction
- If region is provided, construct regional base URL
- Format: `https://{service}-{region}.googleapis.com`
- If region is None, use global endpoint (backward compatible)

### 3. Add to ClientConfig
- Include `region` in `ClientConfig` dataclass for centralized configuration

### 4. Validation
- Validate region format (e.g., "us-central1", "europe-west1")
- Ensure backward compatibility (None = global)

### 5. Testing
- Test with different regions
- Test default (global) behavior
- Test region validation

## Implementation Plan
1. Add `region` parameter to RoutesClient, RoadsClient
2. Update BASE_URL construction to use region parameter
3. Add region to ClientConfig
4. Add validation for region format
5. Add comprehensive tests
6. Update documentation

## Benefits
✅ Support for regional endpoints for lower latency
✅ Better performance for region-specific deployments
✅ Backward compatible (defaults to global)
✅ Centralized configuration via ClientConfig
