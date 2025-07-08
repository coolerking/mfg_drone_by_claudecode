"""
Phase 5: Monitoring Service for MCP Server
Provides comprehensive monitoring capabilities including:
- Performance monitoring and metrics
- Error tracking and alerting
- System health monitoring
- Real-time analytics and reporting
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import threading
import queue

import logging
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and data"""
    name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class AlertInstance:
    """Alert instance (triggered alert)"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class PerformanceSnapshot:
    """System performance snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float


class MonitoringService:
    """Comprehensive monitoring service for MCP Server"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_instances: List[AlertInstance] = []
        self.performance_history: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        
        # Performance tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.endpoint_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_callbacks: List[Callable] = []
        
        # Initialize default metrics
        self._initialize_default_metrics()
        self._initialize_default_alerts()
        
        logger.info("Monitoring Service initialized")
    
    def _initialize_default_metrics(self):
        """Initialize default system metrics"""
        default_metrics = [
            ("system_cpu_percent", MetricType.GAUGE, "System CPU usage percentage", "%"),
            ("system_memory_percent", MetricType.GAUGE, "System memory usage percentage", "%"),
            ("system_disk_percent", MetricType.GAUGE, "System disk usage percentage", "%"),
            ("api_request_count", MetricType.COUNTER, "Total API requests", "requests"),
            ("api_request_duration", MetricType.HISTOGRAM, "API request duration", "seconds"),
            ("api_error_count", MetricType.COUNTER, "Total API errors", "errors"),
            ("active_connections", MetricType.GAUGE, "Active connections", "connections"),
            ("nlp_processing_time", MetricType.HISTOGRAM, "NLP processing time", "seconds"),
            ("backend_response_time", MetricType.HISTOGRAM, "Backend response time", "seconds"),
            ("command_success_rate", MetricType.GAUGE, "Command success rate", "%"),
            ("security_events", MetricType.COUNTER, "Security events", "events"),
            ("rate_limit_violations", MetricType.COUNTER, "Rate limit violations", "violations"),
        ]
        
        for name, metric_type, description, unit in default_metrics:
            self.create_metric(name, metric_type, description, unit)
    
    def _initialize_default_alerts(self):
        """Initialize default alerts"""
        default_alerts = [
            ("high_cpu_usage", "High CPU Usage", "cpu_percent > 80", 80.0, AlertSeverity.WARNING),
            ("critical_cpu_usage", "Critical CPU Usage", "cpu_percent > 95", 95.0, AlertSeverity.CRITICAL),
            ("high_memory_usage", "High Memory Usage", "memory_percent > 85", 85.0, AlertSeverity.WARNING),
            ("critical_memory_usage", "Critical Memory Usage", "memory_percent > 95", 95.0, AlertSeverity.CRITICAL),
            ("high_error_rate", "High Error Rate", "error_rate > 5", 5.0, AlertSeverity.ERROR),
            ("slow_response_time", "Slow Response Time", "avg_response_time > 2", 2.0, AlertSeverity.WARNING),
            ("critical_response_time", "Critical Response Time", "avg_response_time > 5", 5.0, AlertSeverity.ERROR),
            ("security_incident", "Security Incident", "security_events > 10", 10.0, AlertSeverity.ERROR),
        ]
        
        for alert_id, name, condition, threshold, severity in default_alerts:
            self.create_alert(alert_id, name, condition, threshold, severity)
    
    # Metric Management
    
    def create_metric(self, name: str, metric_type: MetricType, description: str, 
                     unit: str = "", labels: Dict[str, str] = None):
        """Create a new metric"""
        if name in self.metrics:
            logger.warning(f"Metric {name} already exists")
            return
        
        metric = Metric(
            name=name,
            metric_type=metric_type,
            description=description,
            unit=unit,
            labels=labels or {}
        )
        
        self.metrics[name] = metric
        logger.debug(f"Created metric: {name}")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        if name not in self.metrics:
            logger.warning(f"Metric {name} not found")
            return
        
        data_point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {}
        )
        
        self.metrics[name].data_points.append(data_point)
    
    def increment_counter(self, name: str, increment: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        if name not in self.metrics:
            logger.warning(f"Counter metric {name} not found")
            return
        
        metric = self.metrics[name]
        if metric.metric_type != MetricType.COUNTER:
            logger.warning(f"Metric {name} is not a counter")
            return
        
        # Get current value (last data point) and add increment
        current_value = 0.0
        if metric.data_points:
            current_value = metric.data_points[-1].value
        
        new_value = current_value + increment
        self.record_metric(name, new_value, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        if name not in self.metrics:
            logger.warning(f"Gauge metric {name} not found")
            return
        
        metric = self.metrics[name]
        if metric.metric_type != MetricType.GAUGE:
            logger.warning(f"Metric {name} is not a gauge")
            return
        
        self.record_metric(name, value, labels)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a value for histogram metric"""
        if name not in self.metrics:
            logger.warning(f"Histogram metric {name} not found")
            return
        
        metric = self.metrics[name]
        if metric.metric_type != MetricType.HISTOGRAM:
            logger.warning(f"Metric {name} is not a histogram")
            return
        
        self.record_metric(name, value, labels)
    
    def time_function(self, metric_name: str):
        """Decorator to time function execution"""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.observe_histogram(metric_name, duration)
            
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.observe_histogram(metric_name, duration)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    # Performance Monitoring
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      duration: float, user_id: str = None):
        """Record API request metrics"""
        # Update general metrics
        self.increment_counter("api_request_count", labels={"endpoint": endpoint, "method": method})
        self.observe_histogram("api_request_duration", duration, labels={"endpoint": endpoint})
        
        if status_code >= 400:
            self.increment_counter("api_error_count", labels={
                "endpoint": endpoint, 
                "status_code": str(status_code)
            })
        
        # Update endpoint-specific stats
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "total_requests": 0,
                "total_errors": 0,
                "total_duration": 0.0,
                "min_duration": float('inf'),
                "max_duration": 0.0,
                "last_request": None
            }
        
        stats = self.endpoint_stats[endpoint]
        stats["total_requests"] += 1
        stats["total_duration"] += duration
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["max_duration"] = max(stats["max_duration"], duration)
        stats["last_request"] = datetime.utcnow()
        
        if status_code >= 400:
            stats["total_errors"] += 1
        
        # Store recent request times for rolling averages
        self.request_times.append(duration)
    
    def record_nlp_processing(self, command: str, duration: float, confidence: float, success: bool):
        """Record NLP processing metrics"""
        self.observe_histogram("nlp_processing_time", duration)
        
        labels = {"success": str(success)}
        if success:
            # Record confidence as a gauge
            self.set_gauge("nlp_confidence", confidence, labels={"command_type": "parsed"})
    
    def record_backend_call(self, endpoint: str, duration: float, success: bool):
        """Record backend API call metrics"""
        self.observe_histogram("backend_response_time", duration, labels={"endpoint": endpoint})
        
        if not success:
            self.increment_counter("backend_errors", labels={"endpoint": endpoint})
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for the specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Calculate request rate
        recent_requests = [
            dp for metric in self.metrics.values() 
            if metric.name == "api_request_count"
            for dp in metric.data_points
            if dp.timestamp > cutoff_time
        ]
        
        request_rate = len(recent_requests) / time_window_minutes if recent_requests else 0.0
        
        # Calculate average response time
        recent_durations = [
            dp.value for metric in self.metrics.values()
            if metric.name == "api_request_duration"
            for dp in metric.data_points
            if dp.timestamp > cutoff_time
        ]
        
        avg_response_time = statistics.mean(recent_durations) if recent_durations else 0.0
        
        # Calculate error rate
        recent_errors = [
            dp for metric in self.metrics.values()
            if metric.name == "api_error_count"
            for dp in metric.data_points
            if dp.timestamp > cutoff_time
        ]
        
        error_rate = len(recent_errors) / max(len(recent_requests), 1) * 100
        
        return {
            "time_window_minutes": time_window_minutes,
            "request_rate_per_minute": request_rate,
            "total_requests": len(recent_requests),
            "avg_response_time_seconds": avg_response_time,
            "error_rate_percent": error_rate,
            "total_errors": len(recent_errors),
            "endpoint_stats": dict(self.endpoint_stats)
        }
    
    # System Monitoring
    
    def collect_system_metrics(self):
        """Collect current system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("system_cpu_percent", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.set_gauge("system_memory_percent", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.set_gauge("system_disk_percent", disk_percent)
            
            # Network stats
            network = psutil.net_io_counters()
            self.set_gauge("network_bytes_sent", network.bytes_sent)
            self.set_gauge("network_bytes_recv", network.bytes_recv)
            
            # Create performance snapshot
            snapshot = PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk_percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                active_connections=self._get_active_connections(),
                request_count=self._get_recent_request_count(),
                error_count=self._get_recent_error_count(),
                avg_response_time=self._get_avg_response_time()
            )
            
            self.performance_history.append(snapshot)
            
            # Check alerts
            self._check_alerts(snapshot)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
    
    def _get_active_connections(self) -> int:
        """Get number of active connections"""
        # This would typically come from the web server
        # For now, return a placeholder value
        return len([conn for conn in psutil.net_connections() if conn.status == 'ESTABLISHED'])
    
    def _get_recent_request_count(self) -> int:
        """Get recent request count (last 5 minutes)"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        if "api_request_count" in self.metrics:
            recent_requests = [
                dp for dp in self.metrics["api_request_count"].data_points
                if dp.timestamp > cutoff_time
            ]
            return len(recent_requests)
        return 0
    
    def _get_recent_error_count(self) -> int:
        """Get recent error count (last 5 minutes)"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        if "api_error_count" in self.metrics:
            recent_errors = [
                dp for dp in self.metrics["api_error_count"].data_points
                if dp.timestamp > cutoff_time
            ]
            return len(recent_errors)
        return 0
    
    def _get_avg_response_time(self) -> float:
        """Get average response time (last 5 minutes)"""
        if self.request_times:
            return statistics.mean(list(self.request_times)[-100:])  # Last 100 requests
        return 0.0
    
    # Alert Management
    
    def create_alert(self, alert_id: str, name: str, condition: str, 
                    threshold: float, severity: AlertSeverity, enabled: bool = True):
        """Create a new alert"""
        alert = Alert(
            id=alert_id,
            name=name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            enabled=enabled
        )
        
        self.alerts[alert_id] = alert
        logger.debug(f"Created alert: {alert_id}")
    
    def _check_alerts(self, snapshot: PerformanceSnapshot):
        """Check all alerts against current metrics"""
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
            
            triggered = self._evaluate_alert_condition(alert, snapshot)
            
            if triggered:
                self._trigger_alert(alert, snapshot)
    
    def _evaluate_alert_condition(self, alert: Alert, snapshot: PerformanceSnapshot) -> bool:
        """Evaluate if alert condition is met"""
        try:
            # Simple condition evaluation based on alert ID patterns
            if "cpu" in alert.id.lower():
                return snapshot.cpu_percent > alert.threshold
            elif "memory" in alert.id.lower():
                return snapshot.memory_percent > alert.threshold
            elif "response_time" in alert.id.lower():
                return snapshot.avg_response_time > alert.threshold
            elif "error_rate" in alert.id.lower():
                if snapshot.request_count > 0:
                    error_rate = (snapshot.error_count / snapshot.request_count) * 100
                    return error_rate > alert.threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating alert condition for {alert.id}: {str(e)}")
            return False
    
    def _trigger_alert(self, alert: Alert, snapshot: PerformanceSnapshot):
        """Trigger an alert"""
        now = datetime.utcnow()
        
        # Check if alert was recently triggered (avoid spam)
        if alert.last_triggered and (now - alert.last_triggered).seconds < 300:  # 5 minutes
            return
        
        # Get the actual metric value that triggered the alert
        metric_value = self._get_alert_metric_value(alert, snapshot)
        
        alert_instance = AlertInstance(
            alert_id=alert.id,
            timestamp=now,
            severity=alert.severity,
            message=f"{alert.name}: {alert.condition} (value: {metric_value:.2f}, threshold: {alert.threshold})",
            metric_value=metric_value,
            threshold=alert.threshold
        )
        
        self.alert_instances.append(alert_instance)
        alert.last_triggered = now
        alert.trigger_count += 1
        
        # Log alert
        if alert.severity == AlertSeverity.CRITICAL:
            logger.critical(f"ALERT CRITICAL: {alert_instance.message}")
        elif alert.severity == AlertSeverity.ERROR:
            logger.error(f"ALERT ERROR: {alert_instance.message}")
        elif alert.severity == AlertSeverity.WARNING:
            logger.warning(f"ALERT WARNING: {alert_instance.message}")
        else:
            logger.info(f"ALERT INFO: {alert_instance.message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_instance)
            except Exception as e:
                logger.error(f"Error in alert callback: {str(e)}")
    
    def _get_alert_metric_value(self, alert: Alert, snapshot: PerformanceSnapshot) -> float:
        """Get the metric value that triggered the alert"""
        if "cpu" in alert.id.lower():
            return snapshot.cpu_percent
        elif "memory" in alert.id.lower():
            return snapshot.memory_percent
        elif "response_time" in alert.id.lower():
            return snapshot.avg_response_time
        elif "error_rate" in alert.id.lower():
            if snapshot.request_count > 0:
                return (snapshot.error_count / snapshot.request_count) * 100
        
        return 0.0
    
    def add_alert_callback(self, callback: Callable[[AlertInstance], None]):
        """Add callback function to be called when alerts are triggered"""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[AlertInstance]:
        """Get currently active (unresolved) alerts"""
        return [alert for alert in self.alert_instances if not alert.resolved]
    
    def resolve_alert(self, alert_instance_id: str):
        """Resolve an alert instance"""
        for alert_instance in self.alert_instances:
            if alert_instance.alert_id == alert_instance_id and not alert_instance.resolved:
                alert_instance.resolved = True
                alert_instance.resolved_at = datetime.utcnow()
                logger.info(f"Resolved alert: {alert_instance.message}")
                break
    
    # Real-time Monitoring
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start real-time monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.collect_system_metrics()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {str(e)}")
                    time.sleep(interval_seconds)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"Started monitoring with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Stopped monitoring")
    
    # Analytics and Reporting
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        latest_snapshot = self.performance_history[-1] if self.performance_history else None
        
        if not latest_snapshot:
            return {"status": "no_data", "message": "No performance data available"}
        
        # Determine overall health status
        health_score = 100
        health_issues = []
        
        if latest_snapshot.cpu_percent > 80:
            health_score -= 20
            health_issues.append(f"High CPU usage: {latest_snapshot.cpu_percent:.1f}%")
        
        if latest_snapshot.memory_percent > 85:
            health_score -= 20
            health_issues.append(f"High memory usage: {latest_snapshot.memory_percent:.1f}%")
        
        if latest_snapshot.avg_response_time > 2.0:
            health_score -= 15
            health_issues.append(f"Slow response time: {latest_snapshot.avg_response_time:.2f}s")
        
        active_alerts = self.get_active_alerts()
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        
        if critical_alerts:
            health_score -= 30
            health_issues.append(f"{len(critical_alerts)} critical alerts active")
        
        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "timestamp": latest_snapshot.timestamp,
            "system_metrics": {
                "cpu_percent": latest_snapshot.cpu_percent,
                "memory_percent": latest_snapshot.memory_percent,
                "disk_percent": latest_snapshot.disk_usage_percent,
                "avg_response_time": latest_snapshot.avg_response_time,
                "active_connections": latest_snapshot.active_connections,
                "request_rate": latest_snapshot.request_count,
                "error_rate": latest_snapshot.error_count
            },
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "health_issues": health_issues,
            "uptime_hours": self._calculate_uptime(),
            "performance_summary": self.get_performance_summary()
        }
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime in hours"""
        if self.performance_history:
            first_snapshot = self.performance_history[0]
            uptime_delta = datetime.utcnow() - first_snapshot.timestamp
            return uptime_delta.total_seconds() / 3600
        return 0.0
    
    def export_metrics(self, format_type: str = "json") -> str:
        """Export all metrics in specified format"""
        if format_type.lower() == "json":
            return self._export_metrics_json()
        elif format_type.lower() == "prometheus":
            return self._export_metrics_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_metrics_json(self) -> str:
        """Export metrics in JSON format"""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {},
            "performance_history": [],
            "alerts": {},
            "alert_instances": []
        }
        
        # Export metrics
        for name, metric in self.metrics.items():
            export_data["metrics"][name] = {
                "type": metric.metric_type.value,
                "description": metric.description,
                "unit": metric.unit,
                "labels": metric.labels,
                "data_points": [
                    {
                        "timestamp": dp.timestamp.isoformat(),
                        "value": dp.value,
                        "labels": dp.labels
                    }
                    for dp in metric.data_points
                ]
            }
        
        # Export performance history (last 100 snapshots)
        for snapshot in list(self.performance_history)[-100:]:
            export_data["performance_history"].append({
                "timestamp": snapshot.timestamp.isoformat(),
                "cpu_percent": snapshot.cpu_percent,
                "memory_percent": snapshot.memory_percent,
                "memory_available_mb": snapshot.memory_available_mb,
                "disk_usage_percent": snapshot.disk_usage_percent,
                "active_connections": snapshot.active_connections,
                "request_count": snapshot.request_count,
                "error_count": snapshot.error_count,
                "avg_response_time": snapshot.avg_response_time
            })
        
        # Export alerts
        for alert_id, alert in self.alerts.items():
            export_data["alerts"][alert_id] = {
                "name": alert.name,
                "condition": alert.condition,
                "threshold": alert.threshold,
                "severity": alert.severity.value,
                "enabled": alert.enabled,
                "trigger_count": alert.trigger_count,
                "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None
            }
        
        # Export recent alert instances
        recent_alerts = [
            alert for alert in self.alert_instances
            if alert.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        for alert_instance in recent_alerts:
            export_data["alert_instances"].append({
                "alert_id": alert_instance.alert_id,
                "timestamp": alert_instance.timestamp.isoformat(),
                "severity": alert_instance.severity.value,
                "message": alert_instance.message,
                "metric_value": alert_instance.metric_value,
                "threshold": alert_instance.threshold,
                "resolved": alert_instance.resolved,
                "resolved_at": alert_instance.resolved_at.isoformat() if alert_instance.resolved_at else None
            })
        
        return json.dumps(export_data, indent=2)
    
    def _export_metrics_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        for name, metric in self.metrics.items():
            # Add metric metadata
            lines.append(f"# HELP {name} {metric.description}")
            lines.append(f"# TYPE {name} {metric.metric_type.value}")
            
            # Add latest data point
            if metric.data_points:
                latest = metric.data_points[-1]
                labels_str = ""
                if latest.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in latest.labels.items()]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{name}{labels_str} {latest.value}")
        
        return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    # Create monitoring service
    monitoring = MonitoringService()
    
    # Start monitoring
    monitoring.start_monitoring(interval_seconds=5)
    
    # Simulate some metrics
    import random
    
    for i in range(10):
        # Simulate API requests
        monitoring.record_request(
            endpoint="/api/drones",
            method="GET",
            status_code=200 if random.random() > 0.1 else 500,
            duration=random.uniform(0.1, 2.0)
        )
        
        # Simulate NLP processing
        monitoring.record_nlp_processing(
            command="test command",
            duration=random.uniform(0.05, 0.5),
            confidence=random.uniform(0.7, 0.95),
            success=random.random() > 0.05
        )
        
        time.sleep(1)
    
    # Get health report
    health_report = monitoring.get_system_health_report()
    print("System Health Report:")
    print(json.dumps(health_report, indent=2, default=str))
    
    # Get performance summary
    perf_summary = monitoring.get_performance_summary()
    print("\nPerformance Summary:")
    print(json.dumps(perf_summary, indent=2, default=str))
    
    # Stop monitoring
    monitoring.stop_monitoring()