## Investigation

The issue description is clear: we need to add a runtime check for minimum Python version (3.8) in `google_maps_sdk/__init__.py`. Currently, the package specifies `python_requires=">=3.8"` in both `setup.py` and `pyproject.toml`, but there's no runtime validation. This means if someone installs the package on Python < 3.8, they'll get unclear errors when trying to import or use the SDK.

## Proposed Solution

Add a Python version check at the top of `google_maps_sdk/__init__.py` (before any other imports) that:
1. Checks if Python version is >= 3.8
2. Raises a clear `RuntimeError` with a helpful message if the version is too old
3. Uses `sys.version_info` for the check

This will provide immediate, clear feedback when the SDK is imported on an unsupported Python version.
