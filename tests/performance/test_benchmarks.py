"""
Performance and benchmark tests (issue #260 / #62)
"""

import pytest
import time
import sys
import tracemalloc
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.client import GoogleMapsClient


@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Performance and benchmark tests"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_request_latency_benchmark(self, mock_get, api_key):
        """Benchmark: Request latency for GET requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Warm up
        client._get("/test")
        
        # Benchmark
        iterations = 100
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            client._get("/test")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_latency = (total_time / iterations) * 1000  # Convert to milliseconds
        
        print(f"\nRequest Latency Benchmark:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average latency: {avg_latency:.2f}ms")
        
        # Assert reasonable performance (should be < 10ms for mocked requests)
        assert avg_latency < 10.0, f"Average latency {avg_latency:.2f}ms exceeds 10ms threshold"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_post_request_latency_benchmark(self, mock_post, api_key):
        """Benchmark: Request latency for POST requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        data = {"key": "value", "nested": {"data": list(range(100))}}
        
        # Warm up
        client._post("/test", data=data)
        
        # Benchmark
        iterations = 100
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            client._post("/test", data=data)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_latency = (total_time / iterations) * 1000
        
        print(f"\nPOST Request Latency Benchmark:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average latency: {avg_latency:.2f}ms")
        
        assert avg_latency < 15.0, f"Average latency {avg_latency:.2f}ms exceeds 15ms threshold"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_throughput_benchmark(self, mock_get, api_key):
        """Benchmark: Throughput (requests per second)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Warm up
        client._get("/test")
        
        # Benchmark
        iterations = 1000
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            client._get("/test")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        throughput = iterations / total_time
        
        print(f"\nThroughput Benchmark:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Throughput: {throughput:.2f} requests/second")
        
        # Assert reasonable throughput (should be > 100 req/s for mocked requests)
        assert throughput > 100.0, f"Throughput {throughput:.2f} req/s below 100 req/s threshold"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_memory_usage_benchmark(self, mock_get, api_key):
        """Benchmark: Memory usage for client operations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "data": list(range(1000))}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        # Start memory tracking
        tracemalloc.start()
        
        client = BaseClient(api_key, "https://example.com")
        
        # Get initial memory
        snapshot1 = tracemalloc.take_snapshot()
        
        # Perform operations
        for _ in range(100):
            client._get("/test")
        
        # Get final memory
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        # Calculate memory increase
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_mb = peak / (1024 * 1024)
        
        print(f"\nMemory Usage Benchmark:")
        print(f"  Peak memory: {memory_mb:.2f} MB")
        print(f"  Current memory: {current / (1024 * 1024):.2f} MB")
        
        # Assert reasonable memory usage (should be < 50MB for 100 requests)
        assert memory_mb < 50.0, f"Peak memory {memory_mb:.2f} MB exceeds 50MB threshold"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_connection_pool_efficiency(self, mock_get, api_key):
        """Benchmark: Connection pool efficiency with multiple requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Test connection reuse
        iterations = 50
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            client._get("/test")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        # Verify session is reused (same session object)
        session_id = id(client.session)
        for _ in range(5):
            client._get("/test")
            assert id(client.session) == session_id
        
        print(f"\nConnection Pool Efficiency:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average time per request: {avg_time*1000:.2f}ms")
        print(f"  Session reused: True")
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests_performance(self, mock_get, api_key):
        """Benchmark: Performance with concurrent requests"""
        import threading
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        def make_request():
            client._get("/test")
        
        # Sequential requests
        start_time = time.perf_counter()
        for _ in range(50):
            make_request()
        sequential_time = time.perf_counter() - start_time
        
        # Concurrent requests
        threads = []
        start_time = time.perf_counter()
        for _ in range(50):
            t = threading.Thread(target=make_request)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        concurrent_time = time.perf_counter() - start_time
        
        print(f"\nConcurrent Requests Performance:")
        print(f"  Sequential time: {sequential_time:.4f}s")
        print(f"  Concurrent time: {concurrent_time:.4f}s")
        print(f"  Speedup: {sequential_time / concurrent_time:.2f}x")
        
        client.close()

    @patch("google_maps_sdk.routes.requests.Session.post")
    def test_routes_api_performance(self, mock_post, api_key, sample_origin, sample_destination):
        """Benchmark: Routes API performance"""
        mock_response = {
            "routes": [{
                "distanceMeters": 1000,
                "duration": "5m"
            }]
        }
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://routes.googleapis.com/test"
        )
        
        client = RoutesClient(api_key)
        
        # Warm up
        client.compute_routes(sample_origin, sample_destination)
        
        # Benchmark
        iterations = 50
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            client.compute_routes(sample_origin, sample_destination)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_latency = (total_time / iterations) * 1000
        
        print(f"\nRoutes API Performance:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average latency: {avg_latency:.2f}ms")
        
        assert avg_latency < 20.0, f"Average latency {avg_latency:.2f}ms exceeds 20ms threshold"
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_large_response_handling(self, mock_get, api_key):
        """Benchmark: Handling large responses"""
        # Create large response
        large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(1000)]}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = large_data
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Benchmark
        iterations = 10
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            result = client._get("/test")
            assert len(result["items"]) == 1000
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_latency = (total_time / iterations) * 1000
        
        print(f"\nLarge Response Handling:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average latency: {avg_latency:.2f}ms")
        print(f"  Response size: ~{len(str(large_data))} bytes")
        
        client.close()

    def test_client_initialization_performance(self, api_key):
        """Benchmark: Client initialization performance"""
        iterations = 100
        start_time = time.perf_counter()
        
        clients = []
        for _ in range(iterations):
            client = BaseClient(api_key, "https://example.com")
            clients.append(client)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        avg_time = (total_time / iterations) * 1000
        
        # Cleanup
        for client in clients:
            client.close()
        
        print(f"\nClient Initialization Performance:")
        print(f"  Iterations: {iterations}")
        print(f"  Total time: {total_time:.4f}s")
        print(f"  Average initialization time: {avg_time:.2f}ms")
        
        assert avg_time < 5.0, f"Average initialization time {avg_time:.2f}ms exceeds 5ms threshold"

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_caching_performance_improvement(self, mock_get, api_key):
        """Benchmark: Performance improvement with caching enabled"""
        from google_maps_sdk.cache import TTLCache
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "data": "cached"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        # Without cache
        client_no_cache = BaseClient(api_key, "https://example.com")
        start_time = time.perf_counter()
        for _ in range(100):
            client_no_cache._get("/test")
        time_no_cache = time.perf_counter() - start_time
        
        # With cache
        client_with_cache = BaseClient(
            api_key,
            "https://example.com",
            enable_cache=True,
            cache_ttl=300.0,
            cache_maxsize=100
        )
        start_time = time.perf_counter()
        for _ in range(100):
            client_with_cache._get("/test")
        time_with_cache = time.perf_counter() - start_time
        
        speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 1.0
        
        print(f"\nCaching Performance Improvement:")
        print(f"  Without cache: {time_no_cache:.4f}s")
        print(f"  With cache: {time_with_cache:.4f}s")
        print(f"  Speedup: {speedup:.2f}x")
        
        client_no_cache.close()
        client_with_cache.close()
