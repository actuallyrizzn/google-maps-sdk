# Test Suite Documentation

This directory contains comprehensive tests for the Google Maps Platform Python SDK with **100% code coverage**.

## Test Structure

### Unit Tests (`tests/unit/`)
Test individual components in isolation with mocked dependencies:
- `test_exceptions.py` - Exception classes
- `test_base_client.py` - Base HTTP client
- `test_routes_client.py` - Routes API client
- `test_directions_client.py` - Directions API client
- `test_roads_client.py` - Roads API client
- `test_client.py` - Unified client

### Integration Tests (`tests/integration/`)
Test with mocked HTTP responses using `requests-mock`:
- `test_routes_integration.py` - Routes API integration
- `test_directions_integration.py` - Directions API integration
- `test_roads_integration.py` - Roads API integration
- `test_client_integration.py` - Unified client integration

### End-to-End Tests (`tests/e2e/`)
Test with real API calls (requires API key):
- `test_routes_e2e.py` - Routes API e2e
- `test_directions_e2e.py` - Directions API e2e
- `test_roads_e2e.py` - Roads API e2e
- `test_client_e2e.py` - Unified client e2e

## Running Tests

### Run All Tests
```bash
pytest
```

### Run by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only (requires API key)
pytest -m e2e
```

### Run with Coverage
```bash
pytest --cov=google_maps_sdk --cov-report=html
```

### Run E2E Tests
E2E tests require a valid Google Maps Platform API key:

```bash
# Set API key
export GOOGLE_MAPS_API_KEY=your_api_key_here

# Run e2e tests
pytest -m e2e
```

Or on Windows:
```powershell
$env:GOOGLE_MAPS_API_KEY="your_api_key_here"
pytest -m e2e
```

## Test Coverage

The test suite achieves **100% code coverage** including:
- All public methods
- All error handling paths
- All exception types
- All parameter combinations
- Edge cases and validation

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Skipping Tests

E2E tests are automatically skipped if `GOOGLE_MAPS_API_KEY` is not set.

To skip specific test categories:
```bash
# Skip e2e tests
pytest -m "not e2e"

# Skip slow tests
pytest -m "not slow"
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:
- Unit and integration tests run without external dependencies
- E2E tests are optional and can be skipped in CI
- Coverage reports are generated for code quality checks




