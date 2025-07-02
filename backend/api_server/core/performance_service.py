"""
Performance Service
Advanced performance monitoring, caching, and optimization
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
import json
import gc

import psutil

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics_history: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def record_metric(self, metric_name: str, value: float, metadata: Optional[Dict] = None):
        """Record a performance metric"""
        metric = {
            "name": metric_name,
            "value": value,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.metrics_history.append(metric)
        
        # Maintain max samples
        if len(self.metrics_history) > self.max_samples:
            self.metrics_history = self.metrics_history[-self.max_samples:]
            
    def get_metrics(self, metric_name: Optional[str] = None, 
                   duration_minutes: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get metrics with optional filtering"""
        metrics = self.metrics_history
        
        if metric_name:
            metrics = [m for m in metrics if m["name"] == metric_name]
            
        if duration_minutes:
            cutoff_time = time.time() - (duration_minutes * 60)
            metrics = [m for m in metrics if m["timestamp"] >= cutoff_time]
            
        return metrics
        
    def get_metric_summary(self, metric_name: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get statistical summary of a metric"""
        metrics = self.get_metrics(metric_name, duration_minutes)
        
        if not metrics:
            return {"count": 0}
            
        values = [m["value"] for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "duration_minutes": duration_minutes,
            "metric_name": metric_name
        }

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry["expires_at"]:
                entry["hits"] += 1
                return entry["value"]
            else:
                del self.cache[key]
        return None
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "hits": 0,
            "size_bytes": len(str(value).encode('utf-8'))
        }
        
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
        
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if current_time >= entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
            
        return len(expired_keys)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        total_hits = sum(entry["hits"] for entry in self.cache.values())
        total_size = sum(entry["size_bytes"] for entry in self.cache.values())
        
        active_entries = sum(
            1 for entry in self.cache.values() 
            if current_time < entry["expires_at"]
        )
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "total_hits": total_hits,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

def performance_monitor(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record metric if performance service is available
                if hasattr(func, '_performance_service'):
                    func._performance_service.record_api_call(
                        metric_name, execution_time, True
                    )
                    
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                if hasattr(func, '_performance_service'):
                    func._performance_service.record_api_call(
                        metric_name, execution_time, False
                    )
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if hasattr(func, '_performance_service'):
                    func._performance_service.record_api_call(
                        metric_name, execution_time, True
                    )
                    
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                if hasattr(func, '_performance_service'):
                    func._performance_service.record_api_call(
                        metric_name, execution_time, False
                    )
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class PerformanceService:
    """Comprehensive performance monitoring and optimization service"""
    
    def __init__(self, cache_ttl: int = 300, max_metrics: int = 10000):
        self.metrics = PerformanceMetrics(max_metrics)
        self.cache = SimpleCache(cache_ttl)
        self.api_calls: Dict[str, List[Dict]] = {}
        self.start_time = time.time()
        
        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def record_api_call(self, endpoint: str, duration: float, success: bool):
        """Record API call performance"""
        if endpoint not in self.api_calls:
            self.api_calls[endpoint] = []
            
        call_record = {
            "timestamp": time.time(),
            "duration": duration,
            "success": success
        }
        
        self.api_calls[endpoint].append(call_record)
        
        # Keep only recent calls (last 1000 per endpoint)
        if len(self.api_calls[endpoint]) > 1000:
            self.api_calls[endpoint] = self.api_calls[endpoint][-1000:]
            
        # Update counters
        self.request_count += 1
        if not success:
            self.error_count += 1
            
        # Record metric
        self.metrics.record_metric(
            f"api_call_{endpoint}",
            duration,
            {"success": success}
        )
        
    def get_api_performance(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get API performance statistics"""
        if endpoint and endpoint in self.api_calls:
            calls = self.api_calls[endpoint]
        else:
            calls = []
            for ep_calls in self.api_calls.values():
                calls.extend(ep_calls)
                
        if not calls:
            return {"call_count": 0}
            
        durations = [call["duration"] for call in calls]
        success_count = sum(1 for call in calls if call["success"])
        
        return {
            "call_count": len(calls),
            "success_rate": round(success_count / len(calls) * 100, 2),
            "avg_duration_ms": round(sum(durations) / len(durations) * 1000, 2),
            "min_duration_ms": round(min(durations) * 1000, 2),
            "max_duration_ms": round(max(durations) * 1000, 2),
            "total_errors": len(calls) - success_count
        }
        
    def get_system_performance(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "cpu": {
                "usage_percent": round(cpu_percent, 1),
                "count": cpu_count,
                "load_avg": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": round(memory.percent, 1),
                "process_memory_mb": round(process_memory.rss / (1024**2), 2)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round(disk.percent, 1)
            },
            "network": {
                "bytes_sent_mb": round(network.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(network.bytes_recv / (1024**2), 2),
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "uptime_seconds": int(time.time() - self.start_time),
            "timestamp": datetime.now().isoformat()
        }
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        system_perf = self.get_system_performance()
        cache_stats = self.cache.get_stats()
        
        # Calculate error rate
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        
        # Cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        # API performance summary
        api_summary = {}
        for endpoint in self.api_calls.keys():
            api_summary[endpoint] = self.get_api_performance(endpoint)
            
        return {
            "system": system_perf,
            "application": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": round(error_rate, 2),
                "uptime_seconds": int(time.time() - self.start_time)
            },
            "cache": {
                **cache_stats,
                "hit_rate_percent": round(cache_hit_rate, 2),
                "total_hits": self.cache_hits,
                "total_misses": self.cache_misses
            },
            "api_endpoints": api_summary,
            "timestamp": datetime.now().isoformat()
        }
        
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform performance optimizations"""
        optimizations = []
        
        # Clean up expired cache entries
        expired_count = self.cache.cleanup_expired()
        if expired_count > 0:
            optimizations.append(f"Cleaned {expired_count} expired cache entries")
            
        # Force garbage collection
        gc_collected = gc.collect()
        if gc_collected > 0:
            optimizations.append(f"Garbage collected {gc_collected} objects")
            
        # Clean old API call records
        cleaned_calls = 0
        cutoff_time = time.time() - 3600  # Keep last hour
        
        for endpoint in self.api_calls:
            original_count = len(self.api_calls[endpoint])
            self.api_calls[endpoint] = [
                call for call in self.api_calls[endpoint] 
                if call["timestamp"] >= cutoff_time
            ]
            cleaned_calls += original_count - len(self.api_calls[endpoint])
            
        if cleaned_calls > 0:
            optimizations.append(f"Cleaned {cleaned_calls} old API call records")
            
        # Clean old metrics
        cutoff_time = time.time() - 7200  # Keep last 2 hours
        original_metrics_count = len(self.metrics.metrics_history)
        self.metrics.metrics_history = [
            metric for metric in self.metrics.metrics_history
            if metric["timestamp"] >= cutoff_time
        ]
        cleaned_metrics = original_metrics_count - len(self.metrics.metrics_history)
        
        if cleaned_metrics > 0:
            optimizations.append(f"Cleaned {cleaned_metrics} old metrics")
            
        return {
            "optimizations_performed": optimizations,
            "total_optimizations": len(optimizations),
            "timestamp": datetime.now().isoformat()
        }
        
    def cached_call(self, key: str, ttl: Optional[int] = None):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = f"{key}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self.cache_hits += 1
                    return cached_result
                    
                self.cache_misses += 1
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl)
                
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = f"{key}:{hash(str(args) + str(kwargs))}"
                
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self.cache_hits += 1
                    return cached_result
                    
                self.cache_misses += 1
                
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl)
                
                return result
                
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
        
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start performance monitoring"""
        logger.info("Started performance monitoring")
        
        while True:
            try:
                # Record system metrics
                system_perf = self.get_system_performance()
                self.metrics.record_metric("cpu_usage", system_perf["cpu"]["usage_percent"])
                self.metrics.record_metric("memory_usage", system_perf["memory"]["usage_percent"])
                self.metrics.record_metric("disk_usage", system_perf["disk"]["usage_percent"])
                
                # Perform periodic optimizations
                if int(time.time()) % 1800 == 0:  # Every 30 minutes
                    self.optimize_performance()
                    
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(interval_seconds)
                
    async def shutdown(self):
        """Shutdown performance service"""
        self.cache.clear()
        logger.info("Performance service shutdown complete")