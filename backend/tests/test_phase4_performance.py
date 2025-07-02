"""
Test Phase 4 Performance Service
Tests for performance monitoring, caching, and optimization
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock

from backend.api_server.core.performance_service import (
    PerformanceService,
    PerformanceMetrics,
    SimpleCache,
    performance_monitor
)

class TestPerformanceMetrics:
    """Test PerformanceMetrics functionality"""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics"""
        metrics = PerformanceMetrics(max_samples=100)
        
        assert len(metrics.metrics_history) == 0
        assert metrics.max_samples == 100
        assert metrics.start_time > 0
        
    def test_record_metric(self):
        """Test recording performance metrics"""
        metrics = PerformanceMetrics()
        
        metrics.record_metric("test_metric", 42.5, {"source": "test"})
        
        assert len(metrics.metrics_history) == 1
        
        metric = metrics.metrics_history[0]
        assert metric["name"] == "test_metric"
        assert metric["value"] == 42.5
        assert metric["metadata"]["source"] == "test"
        assert "timestamp" in metric
        assert "datetime" in metric
        
    def test_max_samples_limit(self):
        """Test max samples limit enforcement"""
        metrics = PerformanceMetrics(max_samples=3)
        
        # Record more metrics than the limit
        for i in range(5):
            metrics.record_metric(f"metric_{i}", i)
            
        # Should only keep the last 3
        assert len(metrics.metrics_history) == 3
        assert metrics.metrics_history[0]["name"] == "metric_2"
        assert metrics.metrics_history[-1]["name"] == "metric_4"
        
    def test_get_metrics_no_filter(self):
        """Test getting all metrics"""
        metrics = PerformanceMetrics()
        
        for i in range(3):
            metrics.record_metric(f"test_{i}", i)
            
        all_metrics = metrics.get_metrics()
        assert len(all_metrics) == 3
        
    def test_get_metrics_filter_by_name(self):
        """Test getting metrics filtered by name"""
        metrics = PerformanceMetrics()
        
        metrics.record_metric("cpu_usage", 50.0)
        metrics.record_metric("memory_usage", 60.0)
        metrics.record_metric("cpu_usage", 55.0)
        
        cpu_metrics = metrics.get_metrics("cpu_usage")
        assert len(cpu_metrics) == 2
        assert all(m["name"] == "cpu_usage" for m in cpu_metrics)
        
    def test_get_metrics_filter_by_duration(self):
        """Test getting metrics filtered by duration"""
        metrics = PerformanceMetrics()
        
        # Record old metric
        old_time = time.time() - 3600  # 1 hour ago
        with patch('time.time', return_value=old_time):
            metrics.record_metric("old_metric", 1.0)
            
        # Record recent metric
        metrics.record_metric("recent_metric", 2.0)
        
        # Get metrics from last 30 minutes
        recent_metrics = metrics.get_metrics(duration_minutes=30)
        assert len(recent_metrics) == 1
        assert recent_metrics[0]["name"] == "recent_metric"
        
    def test_get_metric_summary(self):
        """Test getting metric summary statistics"""
        metrics = PerformanceMetrics()
        
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            metrics.record_metric("test_metric", value)
            
        summary = metrics.get_metric_summary("test_metric")
        
        assert summary["count"] == 5
        assert summary["min"] == 10.0
        assert summary["max"] == 50.0
        assert summary["avg"] == 30.0
        assert summary["latest"] == 50.0
        assert summary["metric_name"] == "test_metric"
        
    def test_get_metric_summary_empty(self):
        """Test getting summary for non-existent metric"""
        metrics = PerformanceMetrics()
        
        summary = metrics.get_metric_summary("nonexistent")
        assert summary["count"] == 0

class TestSimpleCache:
    """Test SimpleCache functionality"""
    
    def test_cache_creation(self):
        """Test creating cache"""
        cache = SimpleCache(default_ttl=300)
        
        assert len(cache.cache) == 0
        assert cache.default_ttl == 300
        
    def test_cache_set_get(self):
        """Test setting and getting cache values"""
        cache = SimpleCache()
        
        cache.set("test_key", "test_value")
        
        value = cache.get("test_key")
        assert value == "test_value"
        
    def test_cache_get_nonexistent(self):
        """Test getting non-existent cache value"""
        cache = SimpleCache()
        
        value = cache.get("nonexistent_key")
        assert value is None
        
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = SimpleCache(default_ttl=1)  # 1 second TTL
        
        cache.set("test_key", "test_value")
        
        # Should exist immediately
        assert cache.get("test_key") == "test_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("test_key") is None
        
    def test_cache_custom_ttl(self):
        """Test cache with custom TTL"""
        cache = SimpleCache(default_ttl=300)
        
        cache.set("test_key", "test_value", ttl=1)
        
        # Should exist immediately
        assert cache.get("test_key") == "test_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("test_key") is None
        
    def test_cache_delete(self):
        """Test deleting cache entries"""
        cache = SimpleCache()
        
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        success = cache.delete("test_key")
        assert success is True
        assert cache.get("test_key") is None
        
        # Try to delete non-existent key
        success = cache.delete("nonexistent_key")
        assert success is False
        
    def test_cache_clear(self):
        """Test clearing all cache entries"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        
    def test_cache_cleanup_expired(self):
        """Test cleaning up expired entries"""
        cache = SimpleCache(default_ttl=1)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Add a fresh entry
        cache.set("key3", "value3", ttl=300)
        
        # Cleanup expired entries
        expired_count = cache.cleanup_expired()
        
        assert expired_count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
        
    def test_cache_get_stats(self):
        """Test getting cache statistics"""
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access one key to increment hits
        cache.get("key1")
        cache.get("key1")
        
        stats = cache.get_stats()
        
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["total_hits"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["total_size_mb"] >= 0

class TestPerformanceService:
    """Test PerformanceService functionality"""
    
    def test_performance_service_creation(self):
        """Test creating performance service"""
        service = PerformanceService(cache_ttl=300, max_metrics=1000)
        
        assert service.cache.default_ttl == 300
        assert service.metrics.max_samples == 1000
        assert len(service.api_calls) == 0
        assert service.request_count == 0
        assert service.error_count == 0
        
    def test_record_api_call(self):
        """Test recording API calls"""
        service = PerformanceService()
        
        service.record_api_call("/test/endpoint", 0.5, True)
        
        assert service.request_count == 1
        assert service.error_count == 0
        assert "/test/endpoint" in service.api_calls
        assert len(service.api_calls["/test/endpoint"]) == 1
        
        call = service.api_calls["/test/endpoint"][0]
        assert call["duration"] == 0.5
        assert call["success"] is True
        
    def test_record_api_call_error(self):
        """Test recording API call errors"""
        service = PerformanceService()
        
        service.record_api_call("/test/endpoint", 1.0, False)
        
        assert service.request_count == 1
        assert service.error_count == 1
        
    def test_get_api_performance_specific_endpoint(self):
        """Test getting performance for specific endpoint"""
        service = PerformanceService()
        
        # Record multiple calls
        service.record_api_call("/test", 0.1, True)
        service.record_api_call("/test", 0.2, True)
        service.record_api_call("/test", 0.3, False)  # Error
        
        perf = service.get_api_performance("/test")
        
        assert perf["call_count"] == 3
        assert perf["success_rate"] == 66.67  # 2/3 * 100
        assert perf["avg_duration_ms"] == 200.0  # (0.1+0.2+0.3)/3 * 1000
        assert perf["min_duration_ms"] == 100.0
        assert perf["max_duration_ms"] == 300.0
        assert perf["total_errors"] == 1
        
    def test_get_api_performance_all_endpoints(self):
        """Test getting performance for all endpoints"""
        service = PerformanceService()
        
        service.record_api_call("/endpoint1", 0.1, True)
        service.record_api_call("/endpoint2", 0.2, True)
        
        perf = service.get_api_performance()  # No specific endpoint
        
        assert perf["call_count"] == 2
        assert perf["success_rate"] == 100.0
        
    def test_get_api_performance_empty(self):
        """Test getting performance when no calls recorded"""
        service = PerformanceService()
        
        perf = service.get_api_performance("/nonexistent")
        assert perf["call_count"] == 0
        
    def test_get_system_performance(self):
        """Test getting system performance metrics"""
        service = PerformanceService()
        
        with patch('psutil.cpu_percent', return_value=50.0), \
             patch('psutil.cpu_count', return_value=4), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.net_io_counters') as mock_network, \
             patch('psutil.Process') as mock_process:
            
            # Mock memory info
            mock_memory.return_value.total = 8 * 1024**3  # 8GB
            mock_memory.return_value.available = 4 * 1024**3  # 4GB
            mock_memory.return_value.used = 4 * 1024**3  # 4GB
            mock_memory.return_value.percent = 50.0
            
            # Mock disk info
            mock_disk.return_value.total = 1000 * 1024**3  # 1TB
            mock_disk.return_value.used = 500 * 1024**3  # 500GB
            mock_disk.return_value.free = 500 * 1024**3  # 500GB
            mock_disk.return_value.percent = 50.0
            
            # Mock network info
            mock_network.return_value.bytes_sent = 1024**2  # 1MB
            mock_network.return_value.bytes_recv = 2 * 1024**2  # 2MB
            mock_network.return_value.packets_sent = 1000
            mock_network.return_value.packets_recv = 2000
            
            # Mock process info
            mock_process_instance = MagicMock()
            mock_process_instance.memory_info.return_value.rss = 100 * 1024**2  # 100MB
            mock_process.return_value = mock_process_instance
            
            perf = service.get_system_performance()
            
            assert perf["cpu"]["usage_percent"] == 50.0
            assert perf["cpu"]["count"] == 4
            assert perf["memory"]["total_gb"] == 8.0
            assert perf["memory"]["usage_percent"] == 50.0
            assert perf["disk"]["usage_percent"] == 50.0
            assert perf["network"]["bytes_sent_mb"] == 1.0
            assert "timestamp" in perf
            
    def test_get_performance_summary(self):
        """Test getting comprehensive performance summary"""
        service = PerformanceService()
        
        # Record some API calls
        service.record_api_call("/test", 0.1, True)
        service.record_api_call("/test", 0.2, False)
        
        # Use cache
        service.cache.set("test_key", "test_value")
        service.cache_hits = 5
        service.cache_misses = 2
        
        with patch.object(service, 'get_system_performance') as mock_sys_perf:
            mock_sys_perf.return_value = {
                "cpu": {"usage_percent": 30.0},
                "memory": {"usage_percent": 40.0},
                "timestamp": "2024-01-01T00:00:00"
            }
            
            summary = service.get_performance_summary()
            
            assert "system" in summary
            assert "application" in summary
            assert "cache" in summary
            assert "api_endpoints" in summary
            
            app_info = summary["application"]
            assert app_info["total_requests"] == 2
            assert app_info["total_errors"] == 1
            assert app_info["error_rate_percent"] == 50.0
            
            cache_info = summary["cache"]
            assert cache_info["hit_rate_percent"] == 71.43  # 5/(5+2)*100
            
    def test_optimize_performance(self):
        """Test performance optimization"""
        service = PerformanceService()
        
        # Add some expired cache entries
        service.cache.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        
        # Add some old API calls
        old_time = time.time() - 7200  # 2 hours ago
        service.api_calls["old_endpoint"] = [
            {"timestamp": old_time, "duration": 0.1, "success": True}
        ]
        
        # Add old metrics
        old_metric = {
            "name": "old_metric",
            "value": 1.0,
            "timestamp": old_time,
            "datetime": "2024-01-01T00:00:00",
            "metadata": {}
        }
        service.metrics.metrics_history.append(old_metric)
        
        result = service.optimize_performance()
        
        assert "optimizations_performed" in result
        assert "total_optimizations" in result
        assert result["total_optimizations"] > 0
        
    def test_cached_call_decorator(self):
        """Test cached call decorator"""
        service = PerformanceService()
        
        call_count = 0
        
        @service.cached_call("test_func", ttl=300)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
            
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Function not called again
        
        # Different arguments should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
        
    @pytest.mark.asyncio
    async def test_cached_call_decorator_async(self):
        """Test cached call decorator with async function"""
        service = PerformanceService()
        
        call_count = 0
        
        @service.cached_call("test_async_func")
        async def async_expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3
            
        # First call should execute function
        result1 = await async_expensive_function(5)
        assert result1 == 15
        assert call_count == 1
        
        # Second call should use cache
        result2 = await async_expensive_function(5)
        assert result2 == 15
        assert call_count == 1  # Function not called again

class TestPerformanceMonitorDecorator:
    """Test performance monitoring decorator"""
    
    def test_performance_monitor_sync(self):
        """Test performance monitor decorator with sync function"""
        # Create a mock performance service
        mock_service = MagicMock()
        
        @performance_monitor("test_endpoint")
        def test_function():
            return "success"
            
        # Attach mock service to function
        test_function._performance_service = mock_service
        
        result = test_function()
        
        assert result == "success"
        mock_service.record_api_call.assert_called_once()
        
        # Check call arguments
        call_args = mock_service.record_api_call.call_args
        assert call_args[0][0] == "test_endpoint"  # metric name
        assert call_args[0][1] > 0  # execution time
        assert call_args[0][2] is True  # success
        
    def test_performance_monitor_sync_error(self):
        """Test performance monitor decorator with sync function error"""
        mock_service = MagicMock()
        
        @performance_monitor("test_endpoint")
        def failing_function():
            raise ValueError("Test error")
            
        failing_function._performance_service = mock_service
        
        with pytest.raises(ValueError):
            failing_function()
            
        # Should record the error
        mock_service.record_api_call.assert_called_once()
        call_args = mock_service.record_api_call.call_args
        assert call_args[0][2] is False  # success = False
        
    @pytest.mark.asyncio
    async def test_performance_monitor_async(self):
        """Test performance monitor decorator with async function"""
        mock_service = MagicMock()
        
        @performance_monitor("async_endpoint")
        async def async_test_function():
            await asyncio.sleep(0.01)
            return "async_success"
            
        async_test_function._performance_service = mock_service
        
        result = await async_test_function()
        
        assert result == "async_success"
        mock_service.record_api_call.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_performance_monitor_async_error(self):
        """Test performance monitor decorator with async function error"""
        mock_service = MagicMock()
        
        @performance_monitor("async_endpoint")
        async def async_failing_function():
            await asyncio.sleep(0.01)
            raise ValueError("Async test error")
            
        async_failing_function._performance_service = mock_service
        
        with pytest.raises(ValueError):
            await async_failing_function()
            
        # Should record the error
        mock_service.record_api_call.assert_called_once()
        call_args = mock_service.record_api_call.call_args
        assert call_args[0][2] is False  # success = False

@pytest.mark.asyncio
class TestPerformanceServiceAsync:
    """Test async functionality of PerformanceService"""
    
    async def test_start_monitoring(self):
        """Test starting performance monitoring"""
        service = PerformanceService()
        
        # Start monitoring with short interval for testing
        monitoring_task = asyncio.create_task(service.start_monitoring(0.1))
        
        # Let it run briefly
        await asyncio.sleep(0.2)
        
        # Cancel monitoring
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
            
        # Should have recorded some metrics
        assert len(service.metrics.metrics_history) > 0
        
    async def test_shutdown(self):
        """Test service shutdown"""
        service = PerformanceService()
        
        # Add some cache entries
        service.cache.set("test_key", "test_value")
        
        await service.shutdown()
        
        # Cache should be cleared
        assert len(service.cache.cache) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])