**Issue #81** from deep code analysis
**Severity:** ⚪ DEPENDENCY
**Location:** requirements.txt vs requirements-dev.txt

## Issue Description
requirements.txt has loose version (>=2.31.0) while dev has specific versions.

## Impact
Potential dependency conflicts.

## Recommendation
Use consistent versioning strategy across both files.
