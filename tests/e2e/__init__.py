"""
End-to-end tests - test with real API calls

These tests require a valid API key and will make real API calls.
Set GOOGLE_MAPS_API_KEY environment variable to run these tests.
"""

import os
import pytest

# Skip all e2e tests if API key is not provided
if not os.getenv("GOOGLE_MAPS_API_KEY"):
    pytest.skip("GOOGLE_MAPS_API_KEY not set, skipping e2e tests", allow_module_level=True)


