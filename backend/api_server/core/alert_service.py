"""
Alert Service
Advanced system monitoring and alerting functionality
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

import psutil

logger = logging.getLogger(__name__)

class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(str, Enum):
    """Alert types"""
    SYSTEM = "system"
    DRONE = "drone"
    TRAINING = "training"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"

class Alert:
    """Alert data model"""
    
    def __init__(self, level: AlertLevel, alert_type: AlertType, message: str, 
                 details: Optional[str] = None, source: Optional[str] = None):
        self.id = f"alert_{int(time.time() * 1000)}"
        self.level = level
        self.type = alert_type
        self.message = message
        self.details = details
        self.source = source
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.resolved = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "level": self.level.value,
            "type": self.type.value,
            "message": self.message,
            "details": self.details,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }

class AlertRule:
    """Alert rule configuration"""
    
    def __init__(self, name: str, metric: str, operator: str, threshold: float,
                 level: AlertLevel, alert_type: AlertType, enabled: bool = True):
        self.name = name
        self.metric = metric
        self.operator = operator  # >, <, >=, <=, ==, !=
        self.threshold = threshold
        self.level = level
        self.type = alert_type
        self.enabled = enabled
        self.last_triggered = None
        self.cooldown_minutes = 5  # Minimum time between same alerts
        
    def should_trigger(self, value: float) -> bool:
        """Check if rule should trigger based on value"""
        if not self.enabled:
            return False
            
        # Check cooldown
        if (self.last_triggered and 
            datetime.now() - self.last_triggered < timedelta(minutes=self.cooldown_minutes)):
            return False
            
        # Evaluate condition
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "!=":
            return value != self.threshold
        
        return False

class AlertService:
    """Advanced alerting and monitoring service"""
    
    def __init__(self, max_alerts: int = 1000):
        self.alerts: List[Alert] = []
        self.max_alerts = max_alerts
        self.alert_rules: List[AlertRule] = []
        self.subscribers: List[callable] = []
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule("High CPU Usage", "cpu_usage", ">", 85.0, 
                     AlertLevel.WARNING, AlertType.SYSTEM),
            AlertRule("Critical CPU Usage", "cpu_usage", ">", 95.0, 
                     AlertLevel.CRITICAL, AlertType.SYSTEM),
            AlertRule("High Memory Usage", "memory_usage", ">", 85.0, 
                     AlertLevel.WARNING, AlertType.SYSTEM),
            AlertRule("Critical Memory Usage", "memory_usage", ">", 95.0, 
                     AlertLevel.CRITICAL, AlertType.SYSTEM),
            AlertRule("High Disk Usage", "disk_usage", ">", 90.0, 
                     AlertLevel.ERROR, AlertType.SYSTEM),
            AlertRule("Critical Disk Usage", "disk_usage", ">", 95.0, 
                     AlertLevel.CRITICAL, AlertType.SYSTEM),
            AlertRule("High Temperature", "temperature", ">", 80.0, 
                     AlertLevel.WARNING, AlertType.SYSTEM),
            AlertRule("Critical Temperature", "temperature", ">", 90.0, 
                     AlertLevel.CRITICAL, AlertType.SYSTEM),
            AlertRule("Low Battery", "battery_level", "<", 20.0, 
                     AlertLevel.WARNING, AlertType.DRONE),
            AlertRule("Critical Battery", "battery_level", "<", 10.0, 
                     AlertLevel.CRITICAL, AlertType.DRONE),
        ]
        
        self.alert_rules.extend(default_rules)
        logger.info(f"Initialized {len(default_rules)} default alert rules")
        
    def add_alert(self, level: AlertLevel, alert_type: AlertType, message: str,
                  details: Optional[str] = None, source: Optional[str] = None) -> Alert:
        """Add a new alert"""
        alert = Alert(level, alert_type, message, details, source)
        self.alerts.append(alert)
        
        # Maintain max alerts limit
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
            
        # Notify subscribers
        self._notify_subscribers(alert)
        
        logger.info(f"Added {level.value} alert: {message}")
        return alert
        
    def get_alerts(self, level: Optional[AlertLevel] = None, 
                   alert_type: Optional[AlertType] = None,
                   limit: Optional[int] = None,
                   unresolved_only: bool = False) -> List[Dict[str, Any]]:
        """Get alerts with filtering"""
        filtered_alerts = self.alerts
        
        if level:
            filtered_alerts = [a for a in filtered_alerts if a.level == level]
            
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.type == alert_type]
            
        if unresolved_only:
            filtered_alerts = [a for a in filtered_alerts if not a.resolved]
            
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            filtered_alerts = filtered_alerts[:limit]
            
        return [alert.to_dict() for alert in filtered_alerts]
        
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Acknowledged alert: {alert_id}")
                return True
        return False
        
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.acknowledged = True
                logger.info(f"Resolved alert: {alert_id}")
                return True
        return False
        
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff_date]
        cleared_count = original_count - len(self.alerts)
        
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} old alerts")
            
    def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule"""
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
        
    def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule"""
        for i, rule in enumerate(self.alert_rules):
            if rule.name == rule_name:
                del self.alert_rules[i]
                logger.info(f"Removed alert rule: {rule_name}")
                return True
        return False
        
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules"""
        return [
            {
                "name": rule.name,
                "metric": rule.metric,
                "operator": rule.operator,
                "threshold": rule.threshold,
                "level": rule.level.value,
                "type": rule.type.value,
                "enabled": rule.enabled,
                "cooldown_minutes": rule.cooldown_minutes,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            }
            for rule in self.alert_rules
        ]
        
    def subscribe_to_alerts(self, callback: callable):
        """Subscribe to alert notifications"""
        self.subscribers.append(callback)
        logger.info("Added alert subscriber")
        
    def _notify_subscribers(self, alert: Alert):
        """Notify all subscribers of new alert"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(alert))
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"Error notifying alert subscriber: {e}")
                
    def evaluate_system_metrics(self, metrics: Dict[str, Any]):
        """Evaluate system metrics against alert rules"""
        for rule in self.alert_rules:
            if rule.metric in metrics:
                value = metrics[rule.metric]
                if isinstance(value, (int, float)) and rule.should_trigger(value):
                    self.add_alert(
                        rule.level,
                        rule.type,
                        f"{rule.name}: {rule.metric} = {value} {rule.operator} {rule.threshold}",
                        details=f"Current value: {value}, Threshold: {rule.threshold}",
                        source="system_monitor"
                    )
                    rule.last_triggered = datetime.now()
                    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
        logger.info(f"Started alert monitoring with {interval_seconds}s interval")
        
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped alert monitoring")
        
    async def _monitoring_loop(self, interval_seconds: int):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect current system metrics
                metrics = {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent
                }
                
                # Get temperature if available
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries and 'cpu' in name.lower():
                                metrics["temperature"] = entries[0].current
                                break
                except:
                    pass
                    
                # Evaluate metrics against rules
                self.evaluate_system_metrics(metrics)
                
                # Clear old alerts periodically
                if int(time.time()) % 3600 == 0:  # Every hour
                    self.clear_old_alerts()
                    
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
                
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        now = datetime.now()
        
        # Count alerts by level in last 24 hours
        recent_alerts = [a for a in self.alerts 
                        if now - a.timestamp < timedelta(hours=24)]
        
        level_counts = {}
        type_counts = {}
        
        for alert in recent_alerts:
            level_counts[alert.level.value] = level_counts.get(alert.level.value, 0) + 1
            type_counts[alert.type.value] = type_counts.get(alert.type.value, 0) + 1
            
        unresolved_count = len([a for a in self.alerts if not a.resolved])
        critical_count = len([a for a in recent_alerts if a.level == AlertLevel.CRITICAL])
        
        return {
            "total_alerts": len(self.alerts),
            "recent_alerts_24h": len(recent_alerts),
            "unresolved_alerts": unresolved_count,
            "critical_alerts_24h": critical_count,
            "alerts_by_level": level_counts,
            "alerts_by_type": type_counts,
            "monitoring_active": self.monitoring_active,
            "alert_rules_count": len(self.alert_rules),
            "last_updated": now.isoformat()
        }
        
    async def shutdown(self):
        """Shutdown alert service"""
        await self.stop_monitoring()
        logger.info("Alert service shutdown complete")