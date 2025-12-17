Issue #1 has been resolved! ✅

## Solution Summary
Routes API now uses header-based authentication (`X-Goog-Api-Key` header) instead of query parameters, following Google's security best practices.

## Implementation
- Overrode `_post` method in `RoutesClient` to use header-based authentication
- Added comprehensive tests to verify the implementation
- No breaking changes to existing API

## PR & Commit
- PR: #255
- Commit: cd0a9d1

The implementation prevents API key exposure in query parameters, server logs, browser history, and referrer headers, significantly improving security posture.
