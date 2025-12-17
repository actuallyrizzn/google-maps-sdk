**Issue #75** from deep code analysis
**Severity:** ⚪ ARCHITECTURE
**Location:** Entire codebase

## Issue Description
Configuration scattered across parameters, hard to manage complex configurations.

## Impact
Hard to manage complex configurations, many parameters to pass around.

## Recommendation
Create ClientConfig dataclass to centralize configuration.
