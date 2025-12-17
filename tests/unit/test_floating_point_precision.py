"""
Unit tests for floating point precision (issue #266 / #68)
"""

import pytest
from google_maps_sdk.utils import format_coordinate, validate_coordinate
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.roads import RoadsClient


@pytest.mark.unit
class TestFloatingPointPrecision:
    """Test floating point precision handling"""

    def test_high_precision_coordinates(self):
        """Test high precision coordinate formatting"""
        # Test with very high precision coordinates
        lat = 37.419734123456789
        lng = -122.082778456789012
        
        formatted = format_coordinate(lat, lng, precision=15)
        parts = formatted.split(',')
        
        assert len(parts) == 2
        # Should preserve precision up to specified decimal places
        assert float(parts[0]) == pytest.approx(lat, abs=1e-15)
        assert float(parts[1]) == pytest.approx(lng, abs=1e-15)

    def test_coordinate_rounding_behavior(self):
        """Test coordinate rounding behavior"""
        # Test default precision (7 decimal places)
        lat = 37.419734123456789
        lng = -122.082778456789012
        
        formatted = format_coordinate(lat, lng)
        parts = formatted.split(',')
        
        # Should round to 7 decimal places
        assert len(parts[0].split('.')[1]) <= 7
        assert len(parts[1].split('.')[1]) <= 7

    def test_coordinate_format_consistency(self):
        """Test coordinate format consistency"""
        coordinates = [
            (37.419734, -122.082778),
            (37.4197340, -122.0827780),  # Trailing zeros
            (37.41973400, -122.08277800),  # More trailing zeros
        ]
        
        formatted_coords = []
        for lat, lng in coordinates:
            formatted = format_coordinate(lat, lng)
            formatted_coords.append(formatted)
        
        # All should format consistently (trailing zeros may differ)
        # But the numeric values should be the same
        for i in range(1, len(formatted_coords)):
            parts1 = formatted_coords[0].split(',')
            parts2 = formatted_coords[i].split(',')
            assert float(parts1[0]) == float(parts2[0])
            assert float(parts1[1]) == float(parts2[1])

    def test_coordinates_near_boundaries(self):
        """Test coordinates near boundaries"""
        from google_maps_sdk.utils import MIN_LATITUDE, MAX_LATITUDE, MIN_LONGITUDE, MAX_LONGITUDE
        
        # Test coordinates just inside boundaries
        boundary_coords = [
            (MIN_LATITUDE + 0.0001, MIN_LONGITUDE + 0.0001),
            (MAX_LATITUDE - 0.0001, MAX_LONGITUDE - 0.0001),
            (MIN_LATITUDE + 1e-10, MIN_LONGITUDE + 1e-10),
            (MAX_LATITUDE - 1e-10, MAX_LONGITUDE - 1e-10),
        ]
        
        for lat, lng in boundary_coords:
            # Should validate successfully
            validated = validate_coordinate(lat, lng)
            assert validated == (lat, lng)
            
            # Should format correctly
            formatted = format_coordinate(lat, lng)
            parts = formatted.split(',')
            assert float(parts[0]) == pytest.approx(lat, abs=1e-7)
            assert float(parts[1]) == pytest.approx(lng, abs=1e-7)

    def test_floating_point_representation(self):
        """Test floating point representation issues"""
        # Test coordinates that might have floating point representation issues
        problematic_coords = [
            (0.1 + 0.2, 0.3),  # Classic floating point issue
            (1.0 / 3.0, 2.0 / 3.0),  # Repeating decimals
            (0.0000001, 0.0000002),  # Very small numbers
        ]
        
        for lat, lng in problematic_coords:
            # Should handle floating point representation correctly
            formatted = format_coordinate(lat, lng, precision=7)
            parts = formatted.split(',')
            
            # Should round appropriately
            assert float(parts[0]) == pytest.approx(lat, abs=1e-7)
            assert float(parts[1]) == pytest.approx(lng, abs=1e-7)

    def test_different_precision_levels(self):
        """Test different precision levels"""
        lat = 37.419734123456789
        lng = -122.082778456789012
        
        for precision in [0, 1, 2, 5, 7, 10, 15]:
            formatted = format_coordinate(lat, lng, precision=precision)
            parts = formatted.split(',')
            
            # Check decimal places
            if '.' in parts[0]:
                decimal_places = len(parts[0].split('.')[1])
                assert decimal_places <= precision
            
            # Values should be approximately correct
            assert float(parts[0]) == pytest.approx(lat, abs=10**(-precision))
            assert float(parts[1]) == pytest.approx(lng, abs=10**(-precision))

    def test_coordinate_precision_in_requests(self, api_key):
        """Test coordinate precision in actual requests"""
        from unittest.mock import patch, MagicMock
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "OK"}
            mock_response.url = "https://example.com/test"
            mock_post.return_value = mock_response
            
            client = BaseClient(api_key, "https://example.com")
            
            # High precision coordinates
            high_precision_data = {
                "origin": {"lat": 37.419734123456789, "lng": -122.082778456789012},
                "destination": {"lat": 37.417670123456789, "lng": -122.079595456789012}
            }
            
            client._post("/test", data=high_precision_data)
            
            # Verify coordinates were serialized
            assert mock_post.called
            call_args = mock_post.call_args
            request_data = call_args.kwargs.get('json', {})
            
            # Coordinates should be preserved (JSON serialization handles precision)
            if "origin" in request_data:
                assert request_data["origin"]["lat"] == pytest.approx(37.419734123456789, abs=1e-10)
            
            client.close()

    def test_routes_api_coordinate_precision(self, api_key, sample_origin, sample_destination):
        """Test Routes API coordinate precision"""
        from unittest.mock import patch, MagicMock
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_response = {
                "routes": [{"distanceMeters": 1000, "duration": "5m"}]
            }
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                url="https://routes.googleapis.com/test"
            )
            
            client = RoutesClient(api_key)
            
            # High precision origin/destination
            high_precision_origin = {
                "location": {
                    "latLng": {
                        "latitude": 37.419734123456789,
                        "longitude": -122.082778456789012
                    }
                }
            }
            high_precision_dest = {
                "location": {
                    "latLng": {
                        "latitude": 37.417670123456789,
                        "longitude": -122.079595456789012
                    }
                }
            }
            
            result = client.compute_routes(high_precision_origin, high_precision_dest)
            
            # Verify request was made with high precision coordinates
            assert mock_post.called
            call_args = mock_post.call_args
            request_data = call_args.kwargs.get('json', {})
            
            # Coordinates should be preserved in request
            if "origin" in request_data:
                origin_lat = request_data["origin"]["location"]["latLng"]["latitude"]
                assert origin_lat == pytest.approx(37.419734123456789, abs=1e-10)
            
            client.close()

    def test_roads_api_coordinate_precision(self, api_key):
        """Test Roads API coordinate precision"""
        from unittest.mock import patch, MagicMock
        
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_response = {
                "snappedPoints": [{"location": {"latitude": 60.0, "longitude": 24.0}}]
            }
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                url="https://roads.googleapis.com/test"
            )
            
            client = RoadsClient(api_key)
            
            # High precision path
            high_precision_path = [
                (60.170880123456789, 24.942795123456789),
                (60.170879123456789, 24.942796123456789),
            ]
            
            result = client.snap_to_roads(high_precision_path)
            
            # Verify request was made
            assert mock_get.called
            call_args = mock_get.call_args
            params = call_args.kwargs.get('params', {})
            
            # Path should be in params with coordinates preserved
            if "path" in params:
                # Coordinates should be formatted correctly
                path_str = params["path"]
                assert "60.170880" in path_str or "60.170880123" in path_str
            
            client.close()

    def test_coordinate_precision_round_trip(self):
        """Test coordinate precision in round-trip conversion"""
        original_coords = [
            (37.419734, -122.082778),
            (37.419734123, -122.082778456),
            (37.419734123456789, -122.082778456789012),
        ]
        
        for lat, lng in original_coords:
            # Format and parse back
            formatted = format_coordinate(lat, lng, precision=15)
            parts = formatted.split(',')
            parsed_lat = float(parts[0])
            parsed_lng = float(parts[1])
            
            # Should preserve precision within reasonable limits
            assert parsed_lat == pytest.approx(lat, abs=1e-10)
            assert parsed_lng == pytest.approx(lng, abs=1e-10)

    def test_scientific_notation_coordinates(self):
        """Test coordinates in scientific notation"""
        # Coordinates that might be represented in scientific notation (but within valid range)
        sci_coords = [
            (1.23e-5, 4.56e-5),  # Very small but valid
            (1.23e-10, 4.56e-10),  # Extremely small but valid
            (37.419734e0, -122.082778e0),  # Normal coordinates in scientific notation
        ]
        
        for lat, lng in sci_coords:
            # Should format correctly (not in scientific notation for coordinates)
            formatted = format_coordinate(lat, lng, precision=10)
            parts = formatted.split(',')
            
            # Should be in decimal notation, not scientific
            assert 'e' not in parts[0].lower()
            assert 'e' not in parts[1].lower()
            
            # Values should be correct
            assert float(parts[0]) == pytest.approx(lat, abs=1e-10)
            assert float(parts[1]) == pytest.approx(lng, abs=1e-10)

    def test_coordinate_precision_with_validation(self):
        """Test coordinate precision with validation"""
        # High precision coordinates that are valid
        high_precision_valid = [
            (37.419734123456789, -122.082778456789012),
            (0.0000001, 0.0000002),
            (89.9999999, 179.9999999),
        ]
        
        for lat, lng in high_precision_valid:
            # Should validate successfully
            validated = validate_coordinate(lat, lng)
            assert validated == (lat, lng)
            
            # Should format with appropriate precision
            formatted = format_coordinate(lat, lng, precision=10)
            parts = formatted.split(',')
            assert float(parts[0]) == pytest.approx(lat, abs=1e-10)
            assert float(parts[1]) == pytest.approx(lng, abs=1e-10)

    def test_coordinate_precision_edge_cases(self):
        """Test coordinate precision edge cases"""
        edge_cases = [
            (0.0, 0.0),  # Zero coordinates
            (-0.0, -0.0),  # Negative zero
            (90.0, 180.0),  # Maximum boundaries
            (-90.0, -180.0),  # Minimum boundaries
            (0.000000001, 0.000000002),  # Very small
            (89.999999999, 179.999999999),  # Very close to max
        ]
        
        for lat, lng in edge_cases:
            # Should handle edge cases correctly
            validated = validate_coordinate(lat, lng)
            formatted = format_coordinate(lat, lng, precision=10)
            
            parts = formatted.split(',')
            assert float(parts[0]) == pytest.approx(validated[0], abs=1e-10)
            assert float(parts[1]) == pytest.approx(validated[1], abs=1e-10)

    def test_coordinate_precision_consistency_across_apis(self, api_key):
        """Test coordinate precision consistency across APIs"""
        from unittest.mock import patch, MagicMock
        
        high_precision_coord = (37.419734123456789, -122.082778456789012)
        
        # Test with Routes API
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"routes": []},
                url="https://routes.googleapis.com/test"
            )
            
            client = RoutesClient(api_key)
            origin = {
                "location": {
                    "latLng": {
                        "latitude": high_precision_coord[0],
                        "longitude": high_precision_coord[1]
                    }
                }
            }
            destination = {
                "location": {
                    "latLng": {
                        "latitude": high_precision_coord[0] + 0.001,
                        "longitude": high_precision_coord[1] + 0.001
                    }
                }
            }
            
            client.compute_routes(origin, destination)
            assert mock_post.called
            
            client.close()
        
        # Test with Roads API
        with patch("google_maps_sdk.base_client.requests.Session.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"snappedPoints": []},
                url="https://roads.googleapis.com/test"
            )
            
            client = RoadsClient(api_key)
            path = [high_precision_coord]
            
            client.snap_to_roads(path)
            assert mock_get.called
            
            client.close()

    def test_coordinate_precision_with_json_serialization(self, api_key):
        """Test coordinate precision in JSON serialization"""
        from unittest.mock import patch, MagicMock
        import json
        
        with patch("google_maps_sdk.base_client.requests.Session.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "OK"},
                url="https://example.com/test"
            )
            
            client = BaseClient(api_key, "https://example.com")
            
            # High precision coordinates
            data = {
                "coordinates": [
                    {"lat": 37.419734123456789, "lng": -122.082778456789012},
                    {"lat": 37.417670123456789, "lng": -122.079595456789012}
                ]
            }
            
            client._post("/test", data=data)
            
            # Verify JSON serialization preserves precision
            assert mock_post.called
            call_args = mock_post.call_args
            
            # Check if json parameter was used
            if 'json' in call_args.kwargs:
                request_json = call_args.kwargs['json']
                # JSON should preserve float precision (Python's float precision)
                assert request_json["coordinates"][0]["lat"] == pytest.approx(37.419734123456789, abs=1e-15)
            
            client.close()

    def test_coordinate_precision_boundary_values(self):
        """Test coordinate precision with boundary values"""
        from google_maps_sdk.utils import MIN_LATITUDE, MAX_LATITUDE, MIN_LONGITUDE, MAX_LONGITUDE
        
        boundary_tests = [
            (MIN_LATITUDE, MIN_LONGITUDE),
            (MAX_LATITUDE, MAX_LONGITUDE),
            (MIN_LATITUDE + 1e-10, MIN_LONGITUDE + 1e-10),
            (MAX_LATITUDE - 1e-10, MAX_LONGITUDE - 1e-10),
        ]
        
        for lat, lng in boundary_tests:
            # Should validate
            validated = validate_coordinate(lat, lng)
            
            # Should format with precision
            formatted = format_coordinate(lat, lng, precision=10)
            parts = formatted.split(',')
            
            # Should preserve values within precision
            assert float(parts[0]) == pytest.approx(validated[0], abs=1e-10)
            assert float(parts[1]) == pytest.approx(validated[1], abs=1e-10)

    def test_coordinate_precision_very_small_differences(self):
        """Test coordinate precision with very small differences"""
        # Coordinates that differ by very small amounts
        base_lat = 37.419734
        base_lng = -122.082778
        
        small_diffs = [1e-10, 1e-9, 1e-8, 1e-7, 1e-6]
        
        for diff in small_diffs:
            lat = base_lat + diff
            lng = base_lng + diff
            
            formatted = format_coordinate(lat, lng, precision=10)
            parts = formatted.split(',')
            
            # Should preserve small differences at appropriate precision
            parsed_lat = float(parts[0])
            parsed_lng = float(parts[1])
            
            # At precision 10, differences >= 1e-10 should be preserved
            if diff >= 1e-10:
                assert abs(parsed_lat - base_lat) >= 1e-11
                assert abs(parsed_lng - base_lng) >= 1e-11
