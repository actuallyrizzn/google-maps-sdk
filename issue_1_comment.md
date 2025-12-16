# Issue #1: Routes API Authentication Method - Solution

## Problem Analysis
Routes API was using API key in query parameters (`?key=...`) instead of HTTP headers. This is a security vulnerability because:
- API keys in query parameters are logged in server access logs
- They appear in browser history and referrer headers
- They can be exposed in proxy logs and error messages
- Google's official documentation recommends using `X-Goog-Api-Key` header for Routes API

## Solution Implemented
Overrode the `_post` method in `RoutesClient` to use header-based authentication (`X-Goog-Api-Key` header) instead of query parameters, following Google's security best practices.

### Changes Made:
1. **Added `_post` method override in `RoutesClient` class** (`google_maps_sdk/routes.py`)
   - API key is now sent via `X-Goog-Api-Key` header instead of query parameter
   - Maintains backward compatibility with existing code
   - All other functionality remains unchanged

2. **Added comprehensive tests** (`tests/unit/test_routes_client.py`)
   - `test_post_uses_header_auth_not_query_param`: Verifies header-based auth for `compute_routes`
   - `test_post_route_matrix_uses_header_auth`: Verifies header-based auth for `compute_route_matrix`
   - Both tests confirm API key is in headers and NOT in query params

## Security Impact
✅ API keys are no longer exposed in query parameters
✅ Follows Google's security best practices for Routes API
✅ Reduces risk of API key leakage in logs and network monitoring

## Testing
- New authentication tests pass ✅
- Implementation verified to use `X-Goog-Api-Key` header
- No breaking changes to existing API

## Files Changed
- `google_maps_sdk/routes.py`: Added `_post` method override with header-based authentication
- `tests/unit/test_routes_client.py`: Added authentication verification tests
