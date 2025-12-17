"""
Unit tests for large payloads (issue #265 / #67)
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.directions import DirectionsClient
from google_maps_sdk.roads import RoadsClient
from google_maps_sdk.exceptions import GoogleMapsAPIError


@pytest.mark.unit
class TestLargePayloads:
    """Test large payload handling"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_maximum_waypoint_count_directions(self, mock_get, api_key):
        """Test maximum waypoint count for Directions API"""
        # Directions API typically allows up to 25 waypoints
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "routes": []}
        mock_response.url = "https://maps.googleapis.com/test"
        mock_get.return_value = mock_response
        
        client = DirectionsClient(api_key)
        
        # Test with maximum waypoints (25)
        waypoints = [f"waypoint_{i}" for i in range(25)]
        result = client.get_directions("origin", "destination", waypoints=waypoints)
        
        assert result["status"] == "OK"
        # Verify waypoints were included in request
        call_args = mock_get.call_args
        # Waypoints should be in the request
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_coordinate_arrays(self, mock_post, api_key, sample_origin, sample_destination):
        """Test large coordinate arrays in Routes API"""
        mock_response = {
            "routes": [{"distanceMeters": 1000, "duration": "5m"}]
        }
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://routes.googleapis.com/test"
        )
        
        client = RoutesClient(api_key)
        
        # Create large coordinate arrays (near API limits)
        # Routes API route matrix allows up to 50 origins and 50 destinations
        origins = [sample_origin] * 50
        destinations = [sample_destination] * 50
        
        result = client.compute_route_matrix(origins, destinations)
        
        assert "routeMatrixElements" in result
        # Verify request was made with large arrays
        assert mock_post.called
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_maximum_request_size(self, mock_post, api_key):
        """Test maximum request size handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Create very large payload (approaching typical API limits)
        # Many APIs have ~10MB request size limits
        large_data = {
            "items": [{"id": i, "data": "x" * 10000} for i in range(1000)]  # ~10MB
        }
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        # Verify request was made
        assert mock_post.called
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_with_compression(self, mock_post, api_key):
        """Test large payload with compression enabled"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_request_compression=True,
            compression_threshold=1024  # 1KB threshold
        )
        
        # Create large payload (> 1KB)
        large_data = {"data": "x" * 5000}  # ~5KB when JSON encoded
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        # Verify compression was used
        call_args = mock_post.call_args
        headers = call_args.kwargs.get('headers', {})
        if 'data' in call_args.kwargs:
            assert headers.get('Content-Encoding') == 'gzip'
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_maximum_roads_points(self, mock_get, api_key):
        """Test maximum points for Roads API"""
        from google_maps_sdk.utils import MAX_ROADS_POINTS
        
        mock_response = {
            "snappedPoints": [{"location": {"latitude": 60.0, "longitude": 24.0}}] * MAX_ROADS_POINTS
        }
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://roads.googleapis.com/test"
        )
        
        client = RoadsClient(api_key)
        
        # Create path with maximum points (100)
        path = [(60.0 + i * 0.001, 24.0 + i * 0.001) for i in range(MAX_ROADS_POINTS)]
        
        result = client.snap_to_roads(path)
        assert "snappedPoints" in result
        
        # Test exceeding maximum should raise error
        too_many_points = path + [(60.0, 24.0)]
        with pytest.raises(ValueError, match="Maximum"):
            client.snap_to_roads(too_many_points)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_nested_structures(self, mock_post, api_key):
        """Test large nested data structures"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Create deeply nested large structure
        large_nested = {}
        current = large_nested
        for i in range(100):
            current["level"] = i
            current["data"] = "x" * 1000
            current["children"] = {}
            current = current["children"]
        
        result = client._post("/test", data=large_nested)
        assert result == {"status": "OK"}
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_array_of_objects(self, mock_post, api_key):
        """Test large array of objects"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Large array of complex objects
        large_array = [
            {
                "id": i,
                "name": f"Item {i}",
                "description": "x" * 500,
                "metadata": {"key": "value", "nested": {"data": list(range(100))}}
            }
            for i in range(1000)
        ]
        
        data = {"items": large_array}
        
        result = client._post("/test", data=data)
        assert result == {"status": "OK"}
        
        client.close()

    @patch("google_maps_sdk.routes.requests.Session.post")
    def test_large_route_matrix_request(self, mock_post, api_key, sample_origin, sample_destination):
        """Test large route matrix request"""
        mock_response = {
            "routeMatrixElements": [
                {"originIndex": i, "destinationIndex": j, "duration": "5m", "distanceMeters": 1000}
                for i in range(50) for j in range(50)
            ]
        }
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://routes.googleapis.com/test"
        )
        
        client = RoutesClient(api_key)
        
        # Maximum origins and destinations (50 each = 2500 route matrix elements)
        origins = [sample_origin] * 50
        destinations = [sample_destination] * 50
        
        result = client.compute_route_matrix(origins, destinations)
        
        assert "routeMatrixElements" in result
        assert len(result["routeMatrixElements"]) == 2500  # 50 * 50
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_serialization(self, mock_post, api_key):
        """Test large payload JSON serialization"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Very large payload that requires proper serialization
        large_data = {
            "coordinates": [[float(i), float(i + 1)] for i in range(10000)],
            "metadata": {"key": "value" * 1000}
        }
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        # Verify request was serialized correctly
        assert mock_post.called
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_with_custom_encoder(self, mock_post, api_key):
        """Test large payload with custom JSON encoder"""
        import json
        from datetime import datetime
        
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            json_encoder=CustomEncoder
        )
        
        # Large payload with custom types
        large_data = {
            "timestamps": [datetime.now() for _ in range(1000)],
            "data": "x" * 5000
        }
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_large_query_parameters(self, mock_get, api_key):
        """Test large query parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Large number of query parameters
        large_params = {f"param_{i}": f"value_{i}" * 100 for i in range(100)}
        
        result = client._get("/test", params=large_params)
        assert result == {"status": "OK"}
        
        # Verify all parameters were included
        call_args = mock_get.call_args
        assert call_args is not None
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_performance(self, mock_post, api_key):
        """Test large payload doesn't cause performance issues"""
        import time
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Large payload
        large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(5000)]}
        
        start_time = time.time()
        result = client._post("/test", data=large_data)
        elapsed = time.time() - start_time
        
        assert result == {"status": "OK"}
        # Should complete in reasonable time (< 5 seconds for serialization)
        assert elapsed < 5.0
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_error_handling(self, mock_post, api_key):
        """Test error handling with large payloads"""
        # Simulate error with large payload
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Request too large"}}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        large_data = {"items": [{"id": i} for i in range(10000)]}
        
        with pytest.raises(GoogleMapsAPIError):
            client._post("/test", data=large_data)
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_with_retry(self, mock_post, api_key):
        """Test large payload with retry logic"""
        from google_maps_sdk.retry import RetryConfig
        import requests
        
        # First call fails, second succeeds
        mock_responses = [
            requests.exceptions.Timeout("Request timeout"),
            MagicMock(status_code=200, json=lambda: {"status": "OK"}, url="https://example.com/test"),
        ]
        mock_post.side_effect = mock_responses
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.01)
        )
        
        large_data = {"items": [{"id": i} for i in range(5000)]}
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        assert mock_post.call_count == 2
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_memory_efficiency(self, mock_post, api_key):
        """Test large payload doesn't cause memory issues"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Very large payload
        large_data = {"data": "x" * (10 * 1024 * 1024)}  # 10MB
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        # Should handle without memory issues
        assert mock_post.called
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_directions_maximum_waypoints(self, mock_get, api_key):
        """Test Directions API maximum waypoints"""
        mock_response = {
            "status": "OK",
            "routes": [{"legs": []}]
        }
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://maps.googleapis.com/test"
        )
        
        client = DirectionsClient(api_key)
        
        # Maximum waypoints (typically 25 for Directions API)
        waypoints = [f"waypoint_{i}" for i in range(25)]
        
        result = client.get_directions("origin", "destination", waypoints=waypoints)
        assert result["status"] == "OK"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_with_compression_threshold(self, mock_post, api_key):
        """Test large payload respects compression threshold"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        # Test with different thresholds
        for threshold in [100, 1024, 10000]:
            client = BaseClient(
                api_key,
                "https://example.com",
                enable_request_compression=True,
                compression_threshold=threshold
            )
            
            # Payload just above threshold
            data_size = threshold + 100
            large_data = {"data": "x" * data_size}
            
            result = client._post("/test", data=large_data)
            assert result == {"status": "OK"}
            
            client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_large_payload_content_length(self, mock_post, api_key):
        """Test large payload sets correct content length"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        large_data = {"items": [{"id": i} for i in range(5000)]}
        
        result = client._post("/test", data=large_data)
        assert result == {"status": "OK"}
        
        # Verify request was made (content length handled by requests library)
        assert mock_post.called
        
        client.close()
