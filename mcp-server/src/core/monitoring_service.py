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
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import hashlib
import pickle

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


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ActivityType(Enum):
    """Types of monitored activities"""
    LOGIN_ATTEMPT = "login_attempt"
    API_ACCESS = "api_access"
    FILE_UPLOAD = "file_upload"
    COMMAND_EXECUTION = "command_execution"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_EVENT = "system_event"


@dataclass
class SecurityEvent:
    """Security event record with persistence support"""
    id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""
    severity: ThreatLevel = ThreatLevel.LOW
    source_ip: str = "unknown"
    user_id: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for the event"""
        content = f"{self.timestamp}{self.event_type}{self.source_ip}{self.user_id}{self.description}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class SuspiciousActivity:
    """Suspicious activity detection record"""
    id: str
    timestamp: datetime
    activity_type: ActivityType
    source_ip: str
    user_id: Optional[str]
    risk_score: float  # 0-100
    indicators: List[str]
    related_events: List[str]  # Event IDs
    auto_blocked: bool = False
    investigation_notes: str = ""


@dataclass
class SecurityIncident:
    """Security incident record"""
    id: str
    timestamp: datetime
    title: str
    description: str
    severity: ThreatLevel
    status: IncidentStatus
    assigned_to: Optional[str]
    related_events: List[str]  # Event IDs
    related_activities: List[str]  # Activity IDs
    timeline: List[Dict[str, Any]]  # Timeline of actions
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.timeline:
            self.timeline = [{
                "timestamp": self.timestamp,
                "action": "incident_created",
                "description": "Security incident created",
                "user": "system"
            }]


@dataclass
class SecurityReport:
    """Security report data"""
    id: str
    timestamp: datetime
    report_type: str  # daily, weekly, monthly, incident
    time_range: Dict[str, datetime]
    summary: Dict[str, Any]
    events: List[SecurityEvent]
    activities: List[SuspiciousActivity]
    incidents: List[SecurityIncident]
    recommendations: List[str]
    charts_data: Dict[str, Any] = field(default_factory=dict)


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
    
    def __init__(self, db_path: str = "security_monitoring.db"):
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
        
        # Enhanced security monitoring
        self.db_path = db_path
        self.security_events: deque = deque(maxlen=10000)  # In-memory cache
        self.suspicious_activities: deque = deque(maxlen=1000)
        self.security_incidents: deque = deque(maxlen=100)
        self.activity_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Notification settings
        self.notification_settings = {
            "email_enabled": False,
            "email_smtp_host": "",
            "email_smtp_port": 587,
            "email_username": "",
            "email_password": "",
            "email_recipients": [],
            "report_schedule": "daily"  # daily, weekly, monthly
        }
        
        # Initialize database and default settings
        self._initialize_database()
        self._initialize_default_metrics()
        self._initialize_default_alerts()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Enhanced Monitoring Service initialized")
    
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
    
    def _initialize_database(self):
        """Initialize SQLite database for persistent storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    event_type TEXT,
                    severity TEXT,
                    source_ip TEXT,
                    user_id TEXT,
                    description TEXT,
                    metadata TEXT,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at DATETIME
                )
            ''')
            
            # Create suspicious activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suspicious_activities (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    activity_type TEXT,
                    source_ip TEXT,
                    user_id TEXT,
                    risk_score REAL,
                    indicators TEXT,
                    related_events TEXT,
                    auto_blocked BOOLEAN DEFAULT 0,
                    investigation_notes TEXT
                )
            ''')
            
            # Create security incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_incidents (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    title TEXT,
                    description TEXT,
                    severity TEXT,
                    status TEXT,
                    assigned_to TEXT,
                    related_events TEXT,
                    related_activities TEXT,
                    timeline TEXT,
                    resolution TEXT,
                    resolved_at DATETIME
                )
            ''')
            
            # Create security reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_reports (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    report_type TEXT,
                    time_range TEXT,
                    summary TEXT,
                    events TEXT,
                    activities TEXT,
                    incidents TEXT,
                    recommendations TEXT,
                    charts_data TEXT
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source_ip ON security_events(source_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON suspicious_activities(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_risk_score ON suspicious_activities(risk_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON security_incidents(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_severity ON security_incidents(severity)')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def _start_background_tasks(self):
        """Start background tasks for monitoring and reporting"""
        # Start activity pattern analysis
        self.pattern_analysis_thread = threading.Thread(
            target=self._activity_pattern_analysis, 
            daemon=True
        )
        self.pattern_analysis_thread.start()
        
        # Start report generation scheduler
        self.report_scheduler_thread = threading.Thread(
            target=self._report_scheduler,
            daemon=True
        )
        self.report_scheduler_thread.start()
        
        logger.info("Background tasks started")
    
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
    
    # Enhanced Security Monitoring and Logging
    
    def log_security_event(self, event_type: str, severity: ThreatLevel, 
                          source_ip: str = "unknown", user_id: Optional[str] = None,
                          description: str = "", metadata: Dict[str, Any] = None) -> str:
        """Log and persist security event"""
        try:
            # Create security event
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                source_ip=source_ip,
                user_id=user_id,
                description=description,
                metadata=metadata or {}
            )
            
            # Add to in-memory cache
            self.security_events.append(event)
            
            # Persist to database
            self._persist_security_event(event)
            
            # Log to system logger
            if severity == ThreatLevel.CRITICAL:
                logger.critical(f"SECURITY CRITICAL: {event_type} - {description}")
            elif severity == ThreatLevel.HIGH:
                logger.error(f"SECURITY HIGH: {event_type} - {description}")
            elif severity == ThreatLevel.MEDIUM:
                logger.warning(f"SECURITY MEDIUM: {event_type} - {description}")
            else:
                logger.info(f"SECURITY LOW: {event_type} - {description}")
            
            # Trigger suspicious activity analysis
            self._analyze_for_suspicious_activity(event)
            
            # Check for incident creation
            self._check_for_incident_creation(event)
            
            return event.id
            
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            return ""
    
    def _persist_security_event(self, event: SecurityEvent):
        """Persist security event to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_events 
                (id, timestamp, event_type, severity, source_ip, user_id, description, metadata, resolved, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.id,
                event.timestamp,
                event.event_type,
                event.severity.value,
                event.source_ip,
                event.user_id,
                event.description,
                json.dumps(event.metadata),
                event.resolved,
                event.resolved_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting security event: {str(e)}")
    
    def _analyze_for_suspicious_activity(self, event: SecurityEvent):
        """Analyze event for suspicious activity patterns"""
        try:
            # Calculate risk score based on event characteristics
            risk_score = self._calculate_risk_score(event)
            
            if risk_score >= 60:  # Threshold for suspicious activity
                indicators = self._identify_risk_indicators(event)
                
                # Create suspicious activity record
                activity = SuspiciousActivity(
                    id=f"SA_{event.id}",
                    timestamp=event.timestamp,
                    activity_type=self._map_event_to_activity_type(event.event_type),
                    source_ip=event.source_ip,
                    user_id=event.user_id,
                    risk_score=risk_score,
                    indicators=indicators,
                    related_events=[event.id],
                    auto_blocked=risk_score >= 85  # Auto-block high-risk activities
                )
                
                # Add to in-memory cache
                self.suspicious_activities.append(activity)
                
                # Persist to database
                self._persist_suspicious_activity(activity)
                
                logger.warning(f"Suspicious activity detected: {activity.id} (Risk: {risk_score})")
                
                # Auto-block if risk is very high
                if activity.auto_blocked:
                    self._auto_block_activity(activity)
                
        except Exception as e:
            logger.error(f"Error analyzing for suspicious activity: {str(e)}")
    
    def _calculate_risk_score(self, event: SecurityEvent) -> float:
        """Calculate risk score for an event (0-100)"""
        score = 0.0
        
        # Base score by severity
        severity_scores = {
            ThreatLevel.LOW: 10,
            ThreatLevel.MEDIUM: 30,
            ThreatLevel.HIGH: 60,
            ThreatLevel.CRITICAL: 80
        }
        score += severity_scores.get(event.severity, 10)
        
        # Additional risk factors
        if event.event_type in ["MALICIOUS_INPUT_DETECTED", "ADVANCED_INJECTION_DETECTED"]:
            score += 20
        
        if event.event_type in ["RATE_LIMIT_EXCEEDED", "BLOCKED_IP_ACCESS"]:
            score += 15
        
        # Check for repeated events from same source
        recent_events = [e for e in self.security_events 
                        if e.source_ip == event.source_ip 
                        and (event.timestamp - e.timestamp).seconds < 3600]  # Last hour
        
        if len(recent_events) > 5:
            score += 10 * min(len(recent_events) - 5, 5)  # Cap at 50 points
        
        # Check for events from unusual locations or patterns
        if self._is_unusual_activity(event):
            score += 15
        
        return min(score, 100)
    
    def _identify_risk_indicators(self, event: SecurityEvent) -> List[str]:
        """Identify risk indicators for an event"""
        indicators = []
        
        # High severity events
        if event.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            indicators.append("high_severity_event")
        
        # Injection attempts
        if "injection" in event.event_type.lower():
            indicators.append("injection_attempt")
        
        # Rate limiting violations
        if "rate_limit" in event.event_type.lower():
            indicators.append("rate_limit_violation")
        
        # Repeated events from same source
        recent_events = [e for e in self.security_events 
                        if e.source_ip == event.source_ip 
                        and (event.timestamp - e.timestamp).seconds < 3600]
        
        if len(recent_events) > 5:
            indicators.append("repeated_events_same_source")
        
        # Unusual timing
        if event.timestamp.hour < 6 or event.timestamp.hour > 22:
            indicators.append("unusual_timing")
        
        # Failed authentication attempts
        if "authentication" in event.event_type.lower() and "failed" in event.description.lower():
            indicators.append("authentication_failure")
        
        return indicators
    
    def _map_event_to_activity_type(self, event_type: str) -> ActivityType:
        """Map event type to activity type"""
        if "login" in event_type.lower() or "authentication" in event_type.lower():
            return ActivityType.LOGIN_ATTEMPT
        elif "api" in event_type.lower():
            return ActivityType.API_ACCESS
        elif "file" in event_type.lower() or "upload" in event_type.lower():
            return ActivityType.FILE_UPLOAD
        elif "command" in event_type.lower():
            return ActivityType.COMMAND_EXECUTION
        elif "config" in event_type.lower():
            return ActivityType.CONFIGURATION_CHANGE
        else:
            return ActivityType.SYSTEM_EVENT
    
    def _is_unusual_activity(self, event: SecurityEvent) -> bool:
        """Check if activity is unusual based on historical patterns"""
        # Simple heuristic - can be enhanced with ML
        
        # Check if source IP is new
        historical_ips = set(e.source_ip for e in self.security_events)
        if event.source_ip not in historical_ips:
            return True
        
        # Check if activity is at unusual time
        if event.timestamp.hour < 6 or event.timestamp.hour > 22:
            return True
        
        # Check if user is performing unusual actions
        if event.user_id:
            user_events = [e for e in self.security_events if e.user_id == event.user_id]
            if len(user_events) > 0:
                typical_event_types = set(e.event_type for e in user_events)
                if event.event_type not in typical_event_types:
                    return True
        
        return False
    
    def _persist_suspicious_activity(self, activity: SuspiciousActivity):
        """Persist suspicious activity to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO suspicious_activities 
                (id, timestamp, activity_type, source_ip, user_id, risk_score, 
                 indicators, related_events, auto_blocked, investigation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.id,
                activity.timestamp,
                activity.activity_type.value,
                activity.source_ip,
                activity.user_id,
                activity.risk_score,
                json.dumps(activity.indicators),
                json.dumps(activity.related_events),
                activity.auto_blocked,
                activity.investigation_notes
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting suspicious activity: {str(e)}")
    
    def _auto_block_activity(self, activity: SuspiciousActivity):
        """Auto-block high-risk suspicious activity"""
        try:
            # Log the auto-block action
            logger.critical(f"Auto-blocking suspicious activity: {activity.id}")
            
            # Here you would implement actual blocking logic
            # For example, adding IP to firewall rules, disabling user account, etc.
            
            # For now, just log it as a security event
            self.log_security_event(
                "AUTO_BLOCK_ACTIVATED",
                ThreatLevel.HIGH,
                source_ip=activity.source_ip,
                user_id=activity.user_id,
                description=f"Auto-blocked suspicious activity: {activity.id}",
                metadata={"blocked_activity_id": activity.id}
            )
            
        except Exception as e:
            logger.error(f"Error auto-blocking activity: {str(e)}")
    
    def _check_for_incident_creation(self, event: SecurityEvent):
        """Check if event should trigger incident creation"""
        try:
            # Incident creation criteria
            create_incident = False
            incident_title = ""
            incident_description = ""
            
            # Critical events always create incidents
            if event.severity == ThreatLevel.CRITICAL:
                create_incident = True
                incident_title = f"Critical Security Event: {event.event_type}"
                incident_description = f"Critical security event detected: {event.description}"
            
            # Multiple high-severity events from same source
            elif event.severity == ThreatLevel.HIGH:
                recent_high_events = [e for e in self.security_events 
                                    if e.source_ip == event.source_ip 
                                    and e.severity == ThreatLevel.HIGH
                                    and (event.timestamp - e.timestamp).seconds < 3600]
                
                if len(recent_high_events) >= 3:
                    create_incident = True
                    incident_title = f"Multiple High-Severity Events from {event.source_ip}"
                    incident_description = f"Multiple high-severity events detected from {event.source_ip}"
            
            # Specific event types that should create incidents
            critical_event_types = [
                "ADVANCED_INJECTION_DETECTED",
                "DANGEROUS_FILE_UPLOAD",
                "EXECUTABLE_FILE_DETECTED",
                "AUTO_BLOCK_ACTIVATED"
            ]
            
            if event.event_type in critical_event_types:
                create_incident = True
                incident_title = f"Security Incident: {event.event_type}"
                incident_description = f"Security incident triggered by: {event.description}"
            
            # Create incident if criteria met
            if create_incident:
                incident = SecurityIncident(
                    id=f"INC_{event.id}",
                    timestamp=event.timestamp,
                    title=incident_title,
                    description=incident_description,
                    severity=event.severity,
                    status=IncidentStatus.OPEN,
                    assigned_to=None,
                    related_events=[event.id],
                    related_activities=[],
                    timeline=[{
                        "timestamp": event.timestamp,
                        "action": "incident_created",
                        "description": "Security incident created automatically",
                        "user": "system"
                    }]
                )
                
                # Add to in-memory cache
                self.security_incidents.append(incident)
                
                # Persist to database
                self._persist_security_incident(incident)
                
                logger.error(f"Security incident created: {incident.id}")
                
                # Send notification
                self._send_incident_notification(incident)
                
        except Exception as e:
            logger.error(f"Error checking for incident creation: {str(e)}")
    
    def _persist_security_incident(self, incident: SecurityIncident):
        """Persist security incident to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_incidents 
                (id, timestamp, title, description, severity, status, assigned_to,
                 related_events, related_activities, timeline, resolution, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident.id,
                incident.timestamp,
                incident.title,
                incident.description,
                incident.severity.value,
                incident.status.value,
                incident.assigned_to,
                json.dumps(incident.related_events),
                json.dumps(incident.related_activities),
                json.dumps(incident.timeline, default=str),
                incident.resolution,
                incident.resolved_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting security incident: {str(e)}")
    
    def _send_incident_notification(self, incident: SecurityIncident):
        """Send notification for security incident"""
        try:
            if not self.notification_settings.get("email_enabled", False):
                return
            
            # Create email notification
            subject = f"Security Incident Alert: {incident.title}"
            body = f"""
            Security Incident Alert
            
            Incident ID: {incident.id}
            Timestamp: {incident.timestamp}
            Severity: {incident.severity.value}
            Status: {incident.status.value}
            
            Description:
            {incident.description}
            
            Related Events: {', '.join(incident.related_events)}
            
            Please investigate immediately.
            
            This is an automated alert from the MCP Server Security Monitoring System.
            """
            
            self._send_email_notification(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending incident notification: {str(e)}")
    
    def _send_email_notification(self, subject: str, body: str, attachments: List[str] = None):
        """Send email notification"""
        try:
            if not self.notification_settings.get("email_enabled", False):
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.notification_settings["email_username"]
            msg['To'] = ", ".join(self.notification_settings["email_recipients"])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(
                self.notification_settings["email_smtp_host"],
                self.notification_settings["email_smtp_port"]
            )
            server.starttls()
            server.login(
                self.notification_settings["email_username"],
                self.notification_settings["email_password"]
            )
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent: {subject}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    def _activity_pattern_analysis(self):
        """Background task for analyzing activity patterns"""
        while True:
            try:
                time.sleep(300)  # Run every 5 minutes
                
                # Analyze recent activity patterns
                self._analyze_activity_patterns()
                
            except Exception as e:
                logger.error(f"Error in activity pattern analysis: {str(e)}")
    
    def _analyze_activity_patterns(self):
        """Analyze activity patterns for anomalies"""
        try:
            # Get recent events (last hour)
            recent_events = [e for e in self.security_events 
                           if (datetime.utcnow() - e.timestamp).seconds < 3600]
            
            if not recent_events:
                return
            
            # Group events by source IP
            ip_events = defaultdict(list)
            for event in recent_events:
                ip_events[event.source_ip].append(event)
            
            # Analyze each IP's activity
            for ip, events in ip_events.items():
                if len(events) >= 10:  # Threshold for pattern analysis
                    # Check for coordinated attacks
                    if self._detect_coordinated_attack(events):
                        self.log_security_event(
                            "COORDINATED_ATTACK_DETECTED",
                            ThreatLevel.HIGH,
                            source_ip=ip,
                            description=f"Coordinated attack pattern detected from {ip}"
                        )
                    
                    # Check for scanning behavior
                    if self._detect_scanning_behavior(events):
                        self.log_security_event(
                            "SCANNING_BEHAVIOR_DETECTED",
                            ThreatLevel.MEDIUM,
                            source_ip=ip,
                            description=f"Scanning behavior detected from {ip}"
                        )
            
        except Exception as e:
            logger.error(f"Error analyzing activity patterns: {str(e)}")
    
    def _detect_coordinated_attack(self, events: List[SecurityEvent]) -> bool:
        """Detect coordinated attack patterns"""
        # Look for multiple different attack types in short time
        event_types = set(e.event_type for e in events)
        attack_types = [t for t in event_types if "injection" in t.lower() or "malicious" in t.lower()]
        
        return len(attack_types) >= 3
    
    def _detect_scanning_behavior(self, events: List[SecurityEvent]) -> bool:
        """Detect scanning/reconnaissance behavior"""
        # Look for rapid sequential access to different endpoints
        timestamps = [e.timestamp for e in events]
        timestamps.sort()
        
        # Check for rapid sequential events
        rapid_events = 0
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i-1]).seconds < 5:
                rapid_events += 1
        
        return rapid_events >= 8
    
    def _report_scheduler(self):
        """Background task for scheduled report generation"""
        last_daily_report = datetime.utcnow() - timedelta(days=1)
        last_weekly_report = datetime.utcnow() - timedelta(weeks=1)
        
        while True:
            try:
                now = datetime.utcnow()
                
                # Generate daily report
                if (now - last_daily_report).days >= 1:
                    self._generate_scheduled_report("daily")
                    last_daily_report = now
                
                # Generate weekly report
                if (now - last_weekly_report).days >= 7:
                    self._generate_scheduled_report("weekly")
                    last_weekly_report = now
                
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in report scheduler: {str(e)}")
    
    def _generate_scheduled_report(self, report_type: str):
        """Generate scheduled security report"""
        try:
            # Generate report
            report = self.generate_security_report(report_type)
            
            # Save to database
            self._persist_security_report(report)
            
            # Send notification if enabled
            if self.notification_settings.get("email_enabled", False):
                self._send_report_notification(report)
            
            logger.info(f"Generated {report_type} security report: {report.id}")
            
        except Exception as e:
            logger.error(f"Error generating scheduled report: {str(e)}")
    
    def generate_security_report(self, report_type: str = "daily") -> SecurityReport:
        """Generate comprehensive security report"""
        try:
            # Determine time range
            now = datetime.utcnow()
            if report_type == "daily":
                start_time = now - timedelta(days=1)
            elif report_type == "weekly":
                start_time = now - timedelta(weeks=1)
            elif report_type == "monthly":
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)
            
            # Get events in time range
            events = [e for e in self.security_events 
                     if e.timestamp >= start_time]
            
            # Get activities in time range
            activities = [a for a in self.suspicious_activities 
                         if a.timestamp >= start_time]
            
            # Get incidents in time range
            incidents = [i for i in self.security_incidents 
                        if i.timestamp >= start_time]
            
            # Generate summary
            summary = self._generate_report_summary(events, activities, incidents)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(events, activities, incidents)
            
            # Generate charts data
            charts_data = self._generate_charts_data(events, activities, incidents)
            
            # Create report
            report = SecurityReport(
                id=f"RPT_{report_type}_{int(now.timestamp())}",
                timestamp=now,
                report_type=report_type,
                time_range={"start": start_time, "end": now},
                summary=summary,
                events=events,
                activities=activities,
                incidents=incidents,
                recommendations=recommendations,
                charts_data=charts_data
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating security report: {str(e)}")
            raise
    
    def _generate_report_summary(self, events: List[SecurityEvent], 
                                activities: List[SuspiciousActivity], 
                                incidents: List[SecurityIncident]) -> Dict[str, Any]:
        """Generate report summary statistics"""
        summary = {
            "total_events": len(events),
            "total_activities": len(activities),
            "total_incidents": len(incidents),
            "events_by_severity": {},
            "activities_by_risk": {},
            "incidents_by_severity": {},
            "top_source_ips": {},
            "top_event_types": {},
            "resolution_status": {}
        }
        
        # Events by severity
        for severity in ThreatLevel:
            summary["events_by_severity"][severity.value] = len([
                e for e in events if e.severity == severity
            ])
        
        # Activities by risk level
        high_risk = len([a for a in activities if a.risk_score >= 80])
        medium_risk = len([a for a in activities if 60 <= a.risk_score < 80])
        low_risk = len([a for a in activities if a.risk_score < 60])
        
        summary["activities_by_risk"] = {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        }
        
        # Incidents by severity
        for severity in ThreatLevel:
            summary["incidents_by_severity"][severity.value] = len([
                i for i in incidents if i.severity == severity
            ])
        
        # Top source IPs
        ip_counts = defaultdict(int)
        for event in events:
            ip_counts[event.source_ip] += 1
        
        summary["top_source_ips"] = dict(sorted(ip_counts.items(), 
                                              key=lambda x: x[1], 
                                              reverse=True)[:10])
        
        # Top event types
        event_type_counts = defaultdict(int)
        for event in events:
            event_type_counts[event.event_type] += 1
        
        summary["top_event_types"] = dict(sorted(event_type_counts.items(), 
                                                key=lambda x: x[1], 
                                                reverse=True)[:10])
        
        # Resolution status
        resolved_events = len([e for e in events if e.resolved])
        resolved_incidents = len([i for i in incidents if i.status == IncidentStatus.RESOLVED])
        
        summary["resolution_status"] = {
            "resolved_events": resolved_events,
            "unresolved_events": len(events) - resolved_events,
            "resolved_incidents": resolved_incidents,
            "open_incidents": len(incidents) - resolved_incidents
        }
        
        return summary
    
    def _generate_security_recommendations(self, events: List[SecurityEvent], 
                                         activities: List[SuspiciousActivity], 
                                         incidents: List[SecurityIncident]) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        # Check for high-risk activities
        high_risk_activities = [a for a in activities if a.risk_score >= 80]
        if high_risk_activities:
            recommendations.append(f"Investigate {len(high_risk_activities)} high-risk activities immediately")
        
        # Check for unresolved incidents
        open_incidents = [i for i in incidents if i.status == IncidentStatus.OPEN]
        if open_incidents:
            recommendations.append(f"Resolve {len(open_incidents)} open security incidents")
        
        # Check for frequent source IPs
        ip_counts = defaultdict(int)
        for event in events:
            ip_counts[event.source_ip] += 1
        
        frequent_ips = [ip for ip, count in ip_counts.items() if count >= 20]
        if frequent_ips:
            recommendations.append(f"Consider blocking or monitoring frequent source IPs: {', '.join(frequent_ips[:5])}")
        
        # Check for injection attempts
        injection_events = [e for e in events if "injection" in e.event_type.lower()]
        if injection_events:
            recommendations.append(f"Review and strengthen input validation (${len(injection_events)} injection attempts)")
        
        # Check for failed authentication
        auth_failures = [e for e in events if "authentication" in e.event_type.lower() and "failed" in e.description.lower()]
        if auth_failures:
            recommendations.append(f"Review authentication security ({len(auth_failures)} failed attempts)")
        
        if not recommendations:
            recommendations.append("Security posture is good - continue monitoring")
        
        return recommendations
    
    def _generate_charts_data(self, events: List[SecurityEvent], 
                             activities: List[SuspiciousActivity], 
                             incidents: List[SecurityIncident]) -> Dict[str, Any]:
        """Generate data for charts and visualizations"""
        charts_data = {
            "events_timeline": [],
            "severity_distribution": {},
            "top_threats": [],
            "activity_heatmap": {}
        }
        
        # Events timeline (hourly buckets)
        timeline_buckets = defaultdict(int)
        for event in events:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            timeline_buckets[hour_key] += 1
        
        charts_data["events_timeline"] = [
            {"time": time, "count": count}
            for time, count in sorted(timeline_buckets.items())
        ]
        
        # Severity distribution
        for severity in ThreatLevel:
            charts_data["severity_distribution"][severity.value] = len([
                e for e in events if e.severity == severity
            ])
        
        # Top threats by event type
        event_type_counts = defaultdict(int)
        for event in events:
            event_type_counts[event.event_type] += 1
        
        charts_data["top_threats"] = [
            {"threat": event_type, "count": count}
            for event_type, count in sorted(event_type_counts.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)[:10]
        ]
        
        # Activity heatmap by hour and day
        heatmap_data = defaultdict(int)
        for event in events:
            day_hour = f"{event.timestamp.strftime('%A')}_{event.timestamp.hour}"
            heatmap_data[day_hour] += 1
        
        charts_data["activity_heatmap"] = dict(heatmap_data)
        
        return charts_data
    
    def _persist_security_report(self, report: SecurityReport):
        """Persist security report to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_reports 
                (id, timestamp, report_type, time_range, summary, events, 
                 activities, incidents, recommendations, charts_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.id,
                report.timestamp,
                report.report_type,
                json.dumps(report.time_range, default=str),
                json.dumps(report.summary),
                json.dumps([e.__dict__ for e in report.events], default=str),
                json.dumps([a.__dict__ for a in report.activities], default=str),
                json.dumps([i.__dict__ for i in report.incidents], default=str),
                json.dumps(report.recommendations),
                json.dumps(report.charts_data)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error persisting security report: {str(e)}")
    
    def _send_report_notification(self, report: SecurityReport):
        """Send notification for security report"""
        try:
            # Generate report summary email
            subject = f"Security Report - {report.report_type.title()} ({report.timestamp.strftime('%Y-%m-%d')})"
            
            body = f"""
            Security Report Summary - {report.report_type.title()}
            Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            
            Summary:
            - Total Events: {report.summary['total_events']}
            - Suspicious Activities: {report.summary['total_activities']}
            - Security Incidents: {report.summary['total_incidents']}
            
            Events by Severity:
            - Critical: {report.summary['events_by_severity'].get('critical', 0)}
            - High: {report.summary['events_by_severity'].get('high', 0)}
            - Medium: {report.summary['events_by_severity'].get('medium', 0)}
            - Low: {report.summary['events_by_severity'].get('low', 0)}
            
            Top Recommendations:
            {chr(10).join(f"- {rec}" for rec in report.recommendations[:5])}
            
            For detailed analysis, please check the security dashboard.
            
            This is an automated report from the MCP Server Security Monitoring System.
            """
            
            # Export report to CSV for attachment
            csv_file = self._export_report_to_csv(report)
            attachments = [csv_file] if csv_file else []
            
            self._send_email_notification(subject, body, attachments)
            
            # Clean up temporary files
            if csv_file and os.path.exists(csv_file):
                os.remove(csv_file)
            
        except Exception as e:
            logger.error(f"Error sending report notification: {str(e)}")
    
    def _export_report_to_csv(self, report: SecurityReport) -> Optional[str]:
        """Export report data to CSV file"""
        try:
            filename = f"security_report_{report.report_type}_{int(report.timestamp.timestamp())}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write events
                writer.writerow(["Events"])
                writer.writerow(["ID", "Timestamp", "Type", "Severity", "Source IP", "User ID", "Description"])
                
                for event in report.events:
                    writer.writerow([
                        event.id,
                        event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        event.event_type,
                        event.severity.value,
                        event.source_ip,
                        event.user_id or "",
                        event.description
                    ])
                
                writer.writerow([])  # Empty row
                
                # Write suspicious activities
                writer.writerow(["Suspicious Activities"])
                writer.writerow(["ID", "Timestamp", "Type", "Source IP", "Risk Score", "Indicators"])
                
                for activity in report.activities:
                    writer.writerow([
                        activity.id,
                        activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        activity.activity_type.value,
                        activity.source_ip,
                        activity.risk_score,
                        ", ".join(activity.indicators)
                    ])
                
                writer.writerow([])  # Empty row
                
                # Write incidents
                writer.writerow(["Security Incidents"])
                writer.writerow(["ID", "Timestamp", "Title", "Severity", "Status", "Description"])
                
                for incident in report.incidents:
                    writer.writerow([
                        incident.id,
                        incident.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        incident.title,
                        incident.severity.value,
                        incident.status.value,
                        incident.description
                    ])
            
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting report to CSV: {str(e)}")
            return None
    
    def get_security_events(self, start_time: Optional[datetime] = None, 
                           end_time: Optional[datetime] = None,
                           severity: Optional[ThreatLevel] = None,
                           source_ip: Optional[str] = None,
                           limit: int = 1000) -> List[SecurityEvent]:
        """Get security events with filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_events WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            if source_ip:
                query += " AND source_ip = ?"
                params.append(source_ip)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = SecurityEvent(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow(),
                    event_type=row[2],
                    severity=ThreatLevel(row[3]),
                    source_ip=row[4],
                    user_id=row[5],
                    description=row[6],
                    metadata=json.loads(row[7]) if row[7] else {},
                    resolved=bool(row[8]),
                    resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
                events.append(event)
            
            conn.close()
            return events
            
        except Exception as e:
            logger.error(f"Error getting security events: {str(e)}")
            return []
    
    def get_suspicious_activities(self, start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 min_risk_score: float = 0.0,
                                 limit: int = 1000) -> List[SuspiciousActivity]:
        """Get suspicious activities with filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM suspicious_activities WHERE risk_score >= ?"
            params = [min_risk_score]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY risk_score DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            activities = []
            for row in rows:
                activity = SuspiciousActivity(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow(),
                    activity_type=ActivityType(row[2]),
                    source_ip=row[3],
                    user_id=row[4],
                    risk_score=row[5],
                    indicators=json.loads(row[6]) if row[6] else [],
                    related_events=json.loads(row[7]) if row[7] else [],
                    auto_blocked=bool(row[8]),
                    investigation_notes=row[9] or ""
                )
                activities.append(activity)
            
            conn.close()
            return activities
            
        except Exception as e:
            logger.error(f"Error getting suspicious activities: {str(e)}")
            return []
    
    def get_security_incidents(self, start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None,
                              status: Optional[IncidentStatus] = None,
                              limit: int = 100) -> List[SecurityIncident]:
        """Get security incidents with filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_incidents WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            incidents = []
            for row in rows:
                incident = SecurityIncident(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow(),
                    title=row[2],
                    description=row[3],
                    severity=ThreatLevel(row[4]),
                    status=IncidentStatus(row[5]),
                    assigned_to=row[6],
                    related_events=json.loads(row[7]) if row[7] else [],
                    related_activities=json.loads(row[8]) if row[8] else [],
                    timeline=json.loads(row[9]) if row[9] else [],
                    resolution=row[10],
                    resolved_at=datetime.fromisoformat(row[11]) if row[11] else None
                )
                incidents.append(incident)
            
            conn.close()
            return incidents
            
        except Exception as e:
            logger.error(f"Error getting security incidents: {str(e)}")
            return []
    
    def update_notification_settings(self, settings: Dict[str, Any]):
        """Update notification settings"""
        self.notification_settings.update(settings)
        logger.info("Notification settings updated")
    
    def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        try:
            now = datetime.utcnow()
            last_24h = now - timedelta(days=1)
            last_7d = now - timedelta(days=7)
            
            # Get recent data
            recent_events = self.get_security_events(start_time=last_24h)
            recent_activities = self.get_suspicious_activities(start_time=last_24h)
            recent_incidents = self.get_security_incidents(start_time=last_24h)
            
            # Get weekly data for trends
            weekly_events = self.get_security_events(start_time=last_7d)
            weekly_activities = self.get_suspicious_activities(start_time=last_7d)
            
            # Calculate metrics
            dashboard_data = {
                "overview": {
                    "events_24h": len(recent_events),
                    "activities_24h": len(recent_activities),
                    "incidents_24h": len(recent_incidents),
                    "critical_events_24h": len([e for e in recent_events if e.severity == ThreatLevel.CRITICAL]),
                    "high_risk_activities_24h": len([a for a in recent_activities if a.risk_score >= 80]),
                    "open_incidents": len([i for i in recent_incidents if i.status == IncidentStatus.OPEN])
                },
                "trends": {
                    "events_7d": len(weekly_events),
                    "activities_7d": len(weekly_activities),
                    "avg_events_per_day": len(weekly_events) / 7,
                    "avg_activities_per_day": len(weekly_activities) / 7
                },
                "top_threats": self._get_top_threats(recent_events),
                "top_source_ips": self._get_top_source_ips(recent_events),
                "severity_distribution": self._get_severity_distribution(recent_events),
                "activity_timeline": self._get_activity_timeline(recent_events),
                "recent_critical_events": [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp.isoformat(),
                        "type": e.event_type,
                        "description": e.description,
                        "source_ip": e.source_ip
                    }
                    for e in recent_events 
                    if e.severity == ThreatLevel.CRITICAL
                ][:10],
                "high_risk_activities": [
                    {
                        "id": a.id,
                        "timestamp": a.timestamp.isoformat(),
                        "type": a.activity_type.value,
                        "source_ip": a.source_ip,
                        "risk_score": a.risk_score,
                        "indicators": a.indicators
                    }
                    for a in recent_activities 
                    if a.risk_score >= 80
                ][:10]
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting security dashboard data: {str(e)}")
            return {}
    
    def _get_top_threats(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Get top threat types"""
        threat_counts = defaultdict(int)
        for event in events:
            threat_counts[event.event_type] += 1
        
        return [
            {"type": threat_type, "count": count}
            for threat_type, count in sorted(threat_counts.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)[:10]
        ]
    
    def _get_top_source_ips(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Get top source IPs"""
        ip_counts = defaultdict(int)
        for event in events:
            ip_counts[event.source_ip] += 1
        
        return [
            {"ip": ip, "count": count}
            for ip, count in sorted(ip_counts.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:10]
        ]
    
    def _get_severity_distribution(self, events: List[SecurityEvent]) -> Dict[str, int]:
        """Get severity distribution"""
        distribution = {}
        for severity in ThreatLevel:
            distribution[severity.value] = len([e for e in events if e.severity == severity])
        
        return distribution
    
    def _get_activity_timeline(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Get activity timeline (hourly buckets)"""
        timeline_buckets = defaultdict(int)
        for event in events:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            timeline_buckets[hour_key] += 1
        
        return [
            {"time": time, "count": count}
            for time, count in sorted(timeline_buckets.items())
        ]


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