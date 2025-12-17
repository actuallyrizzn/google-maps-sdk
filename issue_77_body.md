**Issue #77** from deep code analysis
**Severity:** ⚪ ARCHITECTURE
**Location:** google_maps_sdk/routes.py:14

## Issue Description
Hardcoded global endpoints, cannot use regional endpoints for lower latency.

## Impact
Cannot use regional endpoints for lower latency.

## Recommendation
Support regional endpoint configuration for lower latency deployments.
