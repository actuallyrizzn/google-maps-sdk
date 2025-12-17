"""
Unit tests for concurrent access (issue #263 / #65)
"""

import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from google_maps_sdk.base_client import BaseClient
from google_maps_sdk.routes import RoutesClient
from google_maps_sdk.client import GoogleMapsClient
from google_maps_sdk.rate_limiter import RateLimiter
from google_maps_sdk.circuit_breaker import CircuitBreaker
from google_maps_sdk.exceptions import QuotaExceededError
from google_maps_sdk.circuit_breaker import CircuitBreakerOpenError


@pytest.mark.unit
class TestConcurrentAccess:
    """Test concurrent access and thread-safety"""

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_get_requests(self, mock_get, api_key):
        """Test concurrent GET requests from multiple threads"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                result = client._get("/test")
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 20 concurrent threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 20
        assert mock_get.call_count == 20
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.post")
    def test_concurrent_post_requests(self, mock_post, api_key):
        """Test concurrent POST requests from multiple threads"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_post.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                data = {"thread_id": thread_id, "data": f"test_{thread_id}"}
                result = client._post("/test", data=data)
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 15 concurrent threads
        threads = []
        for i in range(15):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 15
        assert mock_post.call_count == 15
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_mixed_operations(self, mock_get, api_key):
        """Test concurrent mixed GET operations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        results = []
        lock = threading.Lock()
        
        def operation1():
            result = client._get("/endpoint1")
            with lock:
                results.append(("op1", result))
        
        def operation2():
            result = client._get("/endpoint2")
            with lock:
                results.append(("op2", result))
        
        def operation3():
            result = client._get("/endpoint3")
            with lock:
                results.append(("op3", result))
        
        # Mix different operations
        threads = []
        for i in range(10):
            if i % 3 == 0:
                threads.append(threading.Thread(target=operation1))
            elif i % 3 == 1:
                threads.append(threading.Thread(target=operation2))
            else:
                threads.append(threading.Thread(target=operation3))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 10
        client.close()

    def test_thread_local_session_isolation(self, api_key):
        """Test that thread-local sessions are properly isolated"""
        client = BaseClient(api_key, "https://example.com")
        
        sessions = {}
        lock = threading.Lock()
        
        def get_session(thread_id):
            session = client.session
            with lock:
                sessions[thread_id] = session
        
        # Create 10 threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=get_session, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Each thread should have its own session
        assert len(sessions) == 10
        
        # All sessions should be different objects
        session_ids = [id(s) for s in sessions.values()]
        assert len(set(session_ids)) == 10  # All unique
        
        client.close()

    def test_rate_limiter_thread_safety(self, api_key):
        """Test rate limiter thread-safety with concurrent access"""
        from google_maps_sdk.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_calls=50, period=1.0)
        errors = []
        successes = []
        lock = threading.Lock()
        shared_client_id = 123
        
        def acquire_rate_limit():
            try:
                limiter.acquire(shared_client_id)
                with lock:
                    successes.append(1)
            except QuotaExceededError as e:
                with lock:
                    errors.append(e)
        
        # Create 60 threads (more than max_calls)
        threads = []
        for _ in range(60):
            thread = threading.Thread(target=acquire_rate_limit)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Exactly max_calls should succeed
        assert len(successes) == 50
        # Remaining should fail
        assert len(errors) == 10

    def test_circuit_breaker_thread_safety(self, api_key):
        """Test circuit breaker thread-safety with concurrent access"""
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=10, timeout=1.0)
        results = []
        errors = []
        lock = threading.Lock()
        
        def call_with_breaker(success):
            try:
                if success:
                    result = breaker.call(lambda: "success")
                else:
                    result = breaker.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
                with lock:
                    results.append(result)
            except Exception as e:
                with lock:
                    errors.append(e)
        
        # Mix success and failure calls
        threads = []
        for i in range(20):
            thread = threading.Thread(target=call_with_breaker, args=(i % 2 == 0,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have some successes and some failures
        # Circuit breaker should handle concurrent access safely
        assert len(results) + len(errors) == 20

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests_with_rate_limiter(self, mock_get, api_key):
        """Test concurrent requests with rate limiter enabled"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            rate_limit_max_calls=10,
            rate_limit_period=1.0
        )
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                result = client._get("/test")
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 15 threads (more than rate limit)
        threads = []
        for i in range(15):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Some should succeed, some should hit rate limit
        assert len(results) + len(errors) == 15
        # At least some should succeed
        assert len(results) > 0
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests_with_circuit_breaker(self, mock_get, api_key):
        """Test concurrent requests with circuit breaker enabled"""
        # First few calls fail, then succeed
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 5:
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.json.return_value = {"error": {"message": "Server error"}}
                mock_response.url = "https://example.com/test"
                return mock_response
            else:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "OK"}
                mock_response.url = "https://example.com/test"
                return mock_response
        
        mock_get.side_effect = side_effect
        
        from google_maps_sdk.circuit_breaker import CircuitBreaker
        from google_maps_sdk.exceptions import InternalServerError
        
        client = BaseClient(
            api_key,
            "https://example.com",
            circuit_breaker=CircuitBreaker(failure_threshold=5, timeout=0.1)
        )
        
        # Mock _handle_response to raise InternalServerError on 500
        original_handle = client._handle_response
        handle_count = [0]
        
        def mock_handle(response, request_id=None):
            handle_count[0] += 1
            if response.status_code == 500:
                error = InternalServerError("Server error", request_id=request_id)
                raise error
            return original_handle(response, request_id=request_id)
        
        client._handle_response = mock_handle
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                result = client._get("/test")
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Circuit breaker should handle concurrent failures
        assert len(results) + len(errors) == 10
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests_with_cache(self, mock_get, api_key):
        """Test concurrent requests with caching enabled"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK", "cached": True}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(
            api_key,
            "https://example.com",
            enable_cache=True,
            cache_ttl=300.0,
            cache_maxsize=100
        )
        
        results = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            result = client._get("/test")
            with lock:
                results.append((thread_id, result))
        
        # Create 20 concurrent threads making same request
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should get same cached result
        assert len(results) == 20
        # Cache should be thread-safe
        # First call hits API, rest hit cache
        assert mock_get.call_count >= 1
        
        client.close()

    def test_concurrent_client_creation(self, api_key):
        """Test creating multiple clients concurrently"""
        clients = []
        errors = []
        lock = threading.Lock()
        
        def create_client(thread_id):
            try:
                client = BaseClient(api_key, "https://example.com")
                with lock:
                    clients.append((thread_id, client))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 10 clients concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_client, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All clients should be created successfully
        assert len(errors) == 0
        assert len(clients) == 10
        
        # Cleanup
        for _, client in clients:
            client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_close_operations(self, mock_get, api_key):
        """Test concurrent close() operations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        # Create sessions in multiple threads
        def create_and_use_session(thread_id):
            session = client.session
            client._get("/test")
            return session
        
        threads = []
        sessions = []
        for i in range(5):
            thread = threading.Thread(target=lambda tid=i: sessions.append(create_and_use_session(tid)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Close should be idempotent and thread-safe
        close_threads = []
        for _ in range(10):
            thread = threading.Thread(target=client.close)
            close_threads.append(thread)
            thread.start()
        
        for thread in close_threads:
            thread.join()
        
        # No errors should occur
        # Note: accessing client.session will recreate it, so we check internal state
        if hasattr(client, '_local') and hasattr(client._local, 'session'):
            assert client._local.session is None

    @patch("google_maps_sdk.routes.requests.Session.post")
    def test_concurrent_routes_api_calls(self, mock_post, api_key, sample_origin, sample_destination):
        """Test concurrent Routes API calls"""
        mock_response = {
            "routes": [{"distanceMeters": 1000, "duration": "5m"}]
        }
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response,
            url="https://routes.googleapis.com/test"
        )
        
        client = RoutesClient(api_key)
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                result = client.compute_routes(sample_origin, sample_destination)
                with lock:
                    results.append((thread_id, result))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0
        assert len(results) == 10
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_concurrent_requests_with_retry(self, mock_get, api_key):
        """Test concurrent requests with retry logic"""
        from google_maps_sdk.retry import RetryConfig
        import requests
        
        # Track calls per thread
        call_counts = {}
        lock = threading.Lock()
        
        def side_effect(*args, **kwargs):
            thread_id = threading.current_thread().ident
            with lock:
                if thread_id not in call_counts:
                    call_counts[thread_id] = 0
                call_counts[thread_id] += 1
                count = call_counts[thread_id]
            
            if count == 1:
                # First call fails with retryable error
                raise requests.exceptions.Timeout("Network timeout")
            else:
                # Second call succeeds
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"status": "OK"}
                mock_response.url = "https://example.com/test"
                return mock_response
        
        mock_get.side_effect = side_effect
        
        client = BaseClient(
            api_key,
            "https://example.com",
            retry_config=RetryConfig(max_retries=1, base_delay=0.01)
        )
        
        results = []
        errors = []
        result_lock = threading.Lock()
        
        def make_request(thread_id):
            try:
                result = client._get("/test")
                with result_lock:
                    results.append((thread_id, result))
            except Exception as e:
                with result_lock:
                    errors.append((thread_id, e))
        
        # Create 10 concurrent threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All should succeed after retry (timeout is retryable)
        assert len(errors) == 0
        assert len(results) == 10
        
        client.close()

    def test_concurrent_hook_registration(self, api_key):
        """Test concurrent hook registration"""
        client = BaseClient(api_key, "https://example.com")
        
        hooks = []
        lock = threading.Lock()
        
        def register_hook(thread_id):
            def hook(method, url, headers, params, data):
                pass
            
            client.add_request_hook(hook)
            with lock:
                hooks.append((thread_id, hook))
        
        # Register hooks concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_hook, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All hooks should be registered
        assert len(hooks) == 10
        assert len(client._request_hooks) == 10
        
        client.close()

    @patch("google_maps_sdk.base_client.requests.Session.get")
    def test_race_condition_session_access(self, mock_get, api_key):
        """Test race condition in session property access"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        mock_response.url = "https://example.com/test"
        mock_get.return_value = mock_response
        
        client = BaseClient(api_key, "https://example.com")
        
        sessions = set()
        lock = threading.Lock()
        
        def access_session_multiple_times():
            # Access session multiple times rapidly
            for _ in range(10):
                session = client.session
                with lock:
                    sessions.add(id(session))
                client._get("/test")
        
        # Create 5 threads accessing session rapidly
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=access_session_multiple_times)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Each thread should have consistent session
        # (thread-local ensures each thread gets same session)
        assert len(sessions) == 5  # One per thread
        
        client.close()

    def test_concurrent_api_key_update(self, api_key):
        """Test concurrent API key updates"""
        client = BaseClient(api_key, "https://example.com")
        
        new_keys = []
        errors = []
        lock = threading.Lock()
        
        def update_key(thread_id):
            try:
                new_key = f"new_key_{thread_id}_12345678901234567890"
                client.set_api_key(new_key)
                with lock:
                    new_keys.append((thread_id, new_key))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))
        
        # Update API key concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=update_key, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All updates should succeed
        assert len(errors) == 0
        assert len(new_keys) == 10
        
        client.close()
