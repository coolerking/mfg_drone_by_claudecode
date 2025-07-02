"""
Test Phase 4 Alert System
Tests for alert service, rules, and monitoring
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.api_server.core.alert_service import (
    AlertService, 
    Alert, 
    AlertRule, 
    AlertLevel, 
    AlertType
)

class TestAlert:
    """Test Alert model"""
    
    def test_alert_creation(self):
        """Test creating an alert"""
        alert = Alert(
            AlertLevel.WARNING,
            AlertType.SYSTEM,
            "Test alert message",
            details="Test details",
            source="test"
        )
        
        assert alert.level == AlertLevel.WARNING
        assert alert.type == AlertType.SYSTEM
        assert alert.message == "Test alert message"
        assert alert.details == "Test details"
        assert alert.source == "test"
        assert alert.acknowledged is False
        assert alert.resolved is False
        assert alert.id.startswith("alert_")
        assert isinstance(alert.timestamp, datetime)
        
    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = Alert(
            AlertLevel.ERROR,
            AlertType.DRONE,
            "Test message"
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["level"] == "error"
        assert alert_dict["type"] == "drone"
        assert alert_dict["message"] == "Test message"
        assert alert_dict["acknowledged"] is False
        assert alert_dict["resolved"] is False
        assert "id" in alert_dict
        assert "timestamp" in alert_dict

class TestAlertRule:
    """Test AlertRule functionality"""
    
    def test_alert_rule_creation(self):
        """Test creating an alert rule"""
        rule = AlertRule(
            "High CPU",
            "cpu_usage",
            ">",
            80.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        
        assert rule.name == "High CPU"
        assert rule.metric == "cpu_usage"
        assert rule.operator == ">"
        assert rule.threshold == 80.0
        assert rule.level == AlertLevel.WARNING
        assert rule.type == AlertType.SYSTEM
        assert rule.enabled is True
        assert rule.cooldown_minutes == 5
        
    def test_rule_should_trigger_greater_than(self):
        """Test rule triggering with > operator"""
        rule = AlertRule(
            "Test Rule",
            "metric",
            ">",
            50.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        
        assert rule.should_trigger(60.0) is True
        assert rule.should_trigger(50.0) is False
        assert rule.should_trigger(40.0) is False
        
    def test_rule_should_trigger_less_than(self):
        """Test rule triggering with < operator"""
        rule = AlertRule(
            "Test Rule",
            "metric",
            "<",
            30.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        
        assert rule.should_trigger(20.0) is True
        assert rule.should_trigger(30.0) is False
        assert rule.should_trigger(40.0) is False
        
    def test_rule_should_trigger_equals(self):
        """Test rule triggering with == operator"""
        rule = AlertRule(
            "Test Rule",
            "metric",
            "==",
            100.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        
        assert rule.should_trigger(100.0) is True
        assert rule.should_trigger(99.0) is False
        assert rule.should_trigger(101.0) is False
        
    def test_rule_cooldown(self):
        """Test rule cooldown functionality"""
        rule = AlertRule(
            "Test Rule",
            "metric",
            ">",
            50.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        rule.cooldown_minutes = 1  # 1 minute cooldown
        
        # First trigger should work
        assert rule.should_trigger(60.0) is True
        rule.last_triggered = datetime.now()
        
        # Immediate second trigger should not work (cooldown)
        assert rule.should_trigger(60.0) is False
        
        # After cooldown, should work again
        rule.last_triggered = datetime.now() - timedelta(minutes=2)
        assert rule.should_trigger(60.0) is True
        
    def test_rule_disabled(self):
        """Test disabled rule doesn't trigger"""
        rule = AlertRule(
            "Test Rule",
            "metric",
            ">",
            50.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM,
            enabled=False
        )
        
        assert rule.should_trigger(60.0) is False

class TestAlertService:
    """Test AlertService functionality"""
    
    def test_alert_service_creation(self):
        """Test creating alert service"""
        service = AlertService(max_alerts=100)
        
        assert len(service.alerts) == 0
        assert service.max_alerts == 100
        assert len(service.alert_rules) > 0  # Should have default rules
        assert service.monitoring_active is False
        
    def test_add_alert(self):
        """Test adding alerts"""
        service = AlertService()
        
        alert = service.add_alert(
            AlertLevel.INFO,
            AlertType.SYSTEM,
            "Test alert"
        )
        
        assert len(service.alerts) == 1
        assert service.alerts[0] == alert
        assert alert.level == AlertLevel.INFO
        assert alert.type == AlertType.SYSTEM
        assert alert.message == "Test alert"
        
    def test_max_alerts_limit(self):
        """Test max alerts limit enforcement"""
        service = AlertService(max_alerts=3)
        
        # Add more alerts than the limit
        for i in range(5):
            service.add_alert(
                AlertLevel.INFO,
                AlertType.SYSTEM,
                f"Alert {i}"
            )
            
        # Should only keep the last 3 alerts
        assert len(service.alerts) == 3
        assert service.alerts[0].message == "Alert 2"
        assert service.alerts[-1].message == "Alert 4"
        
    def test_get_alerts_no_filter(self):
        """Test getting all alerts"""
        service = AlertService()
        
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Info alert")
        service.add_alert(AlertLevel.WARNING, AlertType.DRONE, "Warning alert")
        service.add_alert(AlertLevel.ERROR, AlertType.TRAINING, "Error alert")
        
        alerts = service.get_alerts()
        assert len(alerts) == 3
        
        # Should be sorted by timestamp (newest first)
        assert alerts[0]["message"] == "Error alert"
        assert alerts[-1]["message"] == "Info alert"
        
    def test_get_alerts_filter_by_level(self):
        """Test getting alerts filtered by level"""
        service = AlertService()
        
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Info alert")
        service.add_alert(AlertLevel.WARNING, AlertType.SYSTEM, "Warning alert")
        service.add_alert(AlertLevel.ERROR, AlertType.SYSTEM, "Error alert")
        
        warning_alerts = service.get_alerts(level=AlertLevel.WARNING)
        assert len(warning_alerts) == 1
        assert warning_alerts[0]["message"] == "Warning alert"
        
    def test_get_alerts_filter_by_type(self):
        """Test getting alerts filtered by type"""
        service = AlertService()
        
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "System alert")
        service.add_alert(AlertLevel.INFO, AlertType.DRONE, "Drone alert")
        service.add_alert(AlertLevel.INFO, AlertType.TRAINING, "Training alert")
        
        drone_alerts = service.get_alerts(alert_type=AlertType.DRONE)
        assert len(drone_alerts) == 1
        assert drone_alerts[0]["message"] == "Drone alert"
        
    def test_get_alerts_unresolved_only(self):
        """Test getting only unresolved alerts"""
        service = AlertService()
        
        alert1 = service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Alert 1")
        alert2 = service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Alert 2")
        
        # Resolve one alert
        alert1.resolved = True
        
        unresolved = service.get_alerts(unresolved_only=True)
        assert len(unresolved) == 1
        assert unresolved[0]["message"] == "Alert 2"
        
    def test_get_alerts_with_limit(self):
        """Test getting alerts with limit"""
        service = AlertService()
        
        for i in range(10):
            service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, f"Alert {i}")
            
        limited_alerts = service.get_alerts(limit=5)
        assert len(limited_alerts) == 5
        
    def test_acknowledge_alert(self):
        """Test acknowledging alerts"""
        service = AlertService()
        
        alert = service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Test alert")
        
        assert alert.acknowledged is False
        
        success = service.acknowledge_alert(alert.id)
        assert success is True
        assert alert.acknowledged is True
        
    def test_acknowledge_nonexistent_alert(self):
        """Test acknowledging non-existent alert"""
        service = AlertService()
        
        success = service.acknowledge_alert("nonexistent-id")
        assert success is False
        
    def test_resolve_alert(self):
        """Test resolving alerts"""
        service = AlertService()
        
        alert = service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Test alert")
        
        assert alert.resolved is False
        assert alert.acknowledged is False
        
        success = service.resolve_alert(alert.id)
        assert success is True
        assert alert.resolved is True
        assert alert.acknowledged is True  # Should also acknowledge
        
    def test_resolve_nonexistent_alert(self):
        """Test resolving non-existent alert"""
        service = AlertService()
        
        success = service.resolve_alert("nonexistent-id")
        assert success is False
        
    def test_clear_old_alerts(self):
        """Test clearing old alerts"""
        service = AlertService()
        
        # Add old alert
        old_alert = service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Old alert")
        old_alert.timestamp = datetime.now() - timedelta(days=10)
        
        # Add recent alert
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Recent alert")
        
        assert len(service.alerts) == 2
        
        # Clear alerts older than 7 days
        service.clear_old_alerts(days=7)
        
        assert len(service.alerts) == 1
        assert service.alerts[0].message == "Recent alert"
        
    def test_add_alert_rule(self):
        """Test adding custom alert rules"""
        service = AlertService()
        initial_rule_count = len(service.alert_rules)
        
        custom_rule = AlertRule(
            "Custom Rule",
            "custom_metric",
            ">",
            100.0,
            AlertLevel.CRITICAL,
            AlertType.PERFORMANCE
        )
        
        service.add_alert_rule(custom_rule)
        
        assert len(service.alert_rules) == initial_rule_count + 1
        assert service.alert_rules[-1] == custom_rule
        
    def test_remove_alert_rule(self):
        """Test removing alert rules"""
        service = AlertService()
        
        # Add a custom rule
        custom_rule = AlertRule(
            "Removable Rule",
            "test_metric",
            ">",
            50.0,
            AlertLevel.WARNING,
            AlertType.SYSTEM
        )
        service.add_alert_rule(custom_rule)
        initial_count = len(service.alert_rules)
        
        # Remove the rule
        success = service.remove_alert_rule("Removable Rule")
        assert success is True
        assert len(service.alert_rules) == initial_count - 1
        
        # Try to remove non-existent rule
        success = service.remove_alert_rule("Non-existent Rule")
        assert success is False
        
    def test_get_alert_rules(self):
        """Test getting alert rules"""
        service = AlertService()
        
        rules = service.get_alert_rules()
        assert len(rules) > 0
        
        # Check rule format
        rule = rules[0]
        assert "name" in rule
        assert "metric" in rule
        assert "operator" in rule
        assert "threshold" in rule
        assert "level" in rule
        assert "type" in rule
        assert "enabled" in rule
        
    def test_evaluate_system_metrics(self):
        """Test evaluating system metrics against rules"""
        service = AlertService()
        initial_alert_count = len(service.alerts)
        
        # Simulate high CPU usage that should trigger alerts
        metrics = {
            "cpu_usage": 90.0,  # Should trigger warning (>85) and critical (>95) - only warning
            "memory_usage": 70.0,  # Should not trigger
            "disk_usage": 92.0  # Should trigger error (>90)
        }
        
        service.evaluate_system_metrics(metrics)
        
        # Should have added some alerts
        assert len(service.alerts) > initial_alert_count
        
        # Check that appropriate alerts were created
        alert_messages = [alert.message for alert in service.alerts]
        cpu_alerts = [msg for msg in alert_messages if "cpu_usage" in msg.lower()]
        disk_alerts = [msg for msg in alert_messages if "disk_usage" in msg.lower()]
        
        assert len(cpu_alerts) > 0
        assert len(disk_alerts) > 0
        
    def test_subscribe_to_alerts(self):
        """Test alert subscription functionality"""
        service = AlertService()
        received_alerts = []
        
        def alert_callback(alert):
            received_alerts.append(alert)
            
        service.subscribe_to_alerts(alert_callback)
        
        # Add an alert
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Test alert")
        
        # Callback should have been called
        assert len(received_alerts) == 1
        assert received_alerts[0].message == "Test alert"
        
    def test_get_alert_summary(self):
        """Test getting alert summary statistics"""
        service = AlertService()
        
        # Add various alerts
        service.add_alert(AlertLevel.INFO, AlertType.SYSTEM, "Info alert")
        service.add_alert(AlertLevel.WARNING, AlertType.DRONE, "Warning alert")
        service.add_alert(AlertLevel.CRITICAL, AlertType.TRAINING, "Critical alert")
        
        # Resolve one alert
        service.alerts[0].resolved = True
        
        summary = service.get_alert_summary()
        
        assert "total_alerts" in summary
        assert "recent_alerts_24h" in summary
        assert "unresolved_alerts" in summary
        assert "critical_alerts_24h" in summary
        assert "alerts_by_level" in summary
        assert "alerts_by_type" in summary
        assert "monitoring_active" in summary
        assert "alert_rules_count" in summary
        
        assert summary["total_alerts"] == 3
        assert summary["unresolved_alerts"] == 2
        assert summary["critical_alerts_24h"] == 1
        assert summary["monitoring_active"] is False

@pytest.mark.asyncio
class TestAlertServiceAsync:
    """Test async functionality of AlertService"""
    
    async def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        service = AlertService()
        
        assert service.monitoring_active is False
        
        # Start monitoring
        await service.start_monitoring(interval_seconds=1)
        assert service.monitoring_active is True
        assert service.monitoring_task is not None
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop monitoring
        await service.stop_monitoring()
        assert service.monitoring_active is False
        
    async def test_monitoring_loop_generates_alerts(self):
        """Test that monitoring loop can generate alerts"""
        service = AlertService()
        initial_alert_count = len(service.alerts)
        
        # Mock high CPU usage
        with patch('psutil.cpu_percent', return_value=95.0):
            # Start monitoring with very short interval
            await service.start_monitoring(interval_seconds=0.1)
            
            # Let it run briefly
            await asyncio.sleep(0.2)
            
            # Stop monitoring
            await service.stop_monitoring()
            
        # Should have generated some alerts for high CPU
        assert len(service.alerts) > initial_alert_count
        
    async def test_shutdown(self):
        """Test service shutdown"""
        service = AlertService()
        
        # Start monitoring
        await service.start_monitoring(interval_seconds=1)
        assert service.monitoring_active is True
        
        # Shutdown should stop monitoring
        await service.shutdown()
        assert service.monitoring_active is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])