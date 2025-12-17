**Issue #99** from deep code analysis
**Severity:** ⚪ CODE QUALITY
**Location:** google_maps_sdk/base_client.py

## Issue Description
Response structure is not validated against expected schema.

## Impact
Invalid responses may be returned to users.

## Recommendation
Add optional response validation against expected schemas.
