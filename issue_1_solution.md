# Issue #1: Routes API Authentication Method - Solution

## Problem
Routes API was using API key in query parameters instead of HTTP headers, which is a security vulnerability as API keys in query parameters are logged in server access logs, browser history, referrer headers, and proxy logs.

## Solution Implemented
Override the `_post` method in `RoutesClient` to use header-based authentication (`X-Goog-Api-Key` header) instead of query parameters, following Google's security best practices.

## Changes Made
- Added `_post` method override in `RoutesClient` class
- API key is now sent via `X-Goog-Api-Key` header instead of query parameter
- Maintains backward compatibility with existing code
- All other functionality remains unchanged

## Files Changed
- `google_maps_sdk/routes.py`: Added `_post` method override

## Testing
- Existing tests should continue to pass
- New tests verify header-based authentication is used
