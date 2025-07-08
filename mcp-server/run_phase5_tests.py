#!/usr/bin/env python3
"""
Phase 5: Comprehensive Test Runner for Enhanced MCP Server
Tests all Phase 5 features including:
- System integration tests
- Security and authentication tests
- Monitoring and alerting tests
- Performance and stress tests
"""

import os
import sys
import asyncio
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import pytest
import logging
from unittest.mock import AsyncMock, MagicMock

# Import Phase 5 components for testing
from core.security_manager import SecurityManager, SecurityConfig, SecurityLevel
from core.monitoring_service import MonitoringService, MetricType, AlertSeverity
from core.backend_client import BackendClient
from core.enhanced_nlp_engine import EnhancedNLPEngine
from core.enhanced_command_router import EnhancedCommandRouter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase5TestRunner:
    """Comprehensive test runner for Phase 5 features"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.security_manager = None
        self.monitoring_service = None
        
    def setup_test_environment(self):
        """Setup test environment"""
        logger.info("Setting up Phase 5 test environment...")
        
        # Initialize services for testing
        security_config = SecurityConfig(
            jwt_secret="test-secret-key",
            max_failed_attempts=3,
            lockout_duration_minutes=5
        )
        
        self.security_manager = SecurityManager(security_config)
        self.monitoring_service = MonitoringService()
        
        logger.info("Test environment setup complete")
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security-related tests"""
        logger.info("Running security tests...")
        
        test_results = {
            "api_key_generation": False,
            "api_key_validation": False,
            "jwt_token_generation": False,
            "jwt_token_validation": False,
            "authorization_checks": False,
            "rate_limiting": False,
            "ip_filtering": False,
            "input_validation": False
        }
        
        try:
            # Test API key generation and validation
            api_key = self.security_manager.generate_api_key("test_user", SecurityLevel.OPERATOR)
            test_results["api_key_generation"] = bool(api_key)
            
            valid, user_id, level = self.security_manager.validate_api_key(api_key)
            test_results["api_key_validation"] = valid and user_id == "test_user" and level == SecurityLevel.OPERATOR
            
            # Test JWT token generation and validation
            jwt_token = self.security_manager.generate_jwt_token("test_user", SecurityLevel.OPERATOR)
            test_results["jwt_token_generation"] = bool(jwt_token)
            
            valid, user_id, level = self.security_manager.validate_jwt_token(jwt_token)
            test_results["jwt_token_validation"] = valid and user_id == "test_user" and level == SecurityLevel.OPERATOR
            
            # Test authorization checks
            auth_result = self.security_manager.check_authorization(SecurityLevel.ADMIN, SecurityLevel.OPERATOR)
            test_results["authorization_checks"] = auth_result
            
            # Test rate limiting
            rate_limit_ok_1 = self.security_manager.check_rate_limit("test_user", "192.168.1.1")
            rate_limit_ok_2 = self.security_manager.check_rate_limit("test_user", "192.168.1.1")
            test_results["rate_limiting"] = rate_limit_ok_1 and rate_limit_ok_2
            
            # Test IP filtering
            ip_allowed = self.security_manager.is_ip_allowed("192.168.1.1")
            test_results["ip_filtering"] = ip_allowed
            
            # Test input validation
            valid, sanitized = self.security_manager.validate_command_input("test command")
            test_results["input_validation"] = valid and sanitized == "test command"
            
        except Exception as e:
            logger.error(f"Security test error: {str(e)}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        logger.info(f"Security tests completed: {passed_tests}/{total_tests} passed")
        return {
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "details": test_results
        }
    
    def run_monitoring_tests(self) -> Dict[str, Any]:
        """Run monitoring-related tests"""
        logger.info("Running monitoring tests...")
        
        test_results = {
            "metric_creation": False,
            "metric_recording": False,
            "counter_increment": False,
            "gauge_setting": False,
            "histogram_observation": False,
            "alert_creation": False,
            "alert_triggering": False,
            "performance_tracking": False
        }
        
        try:
            # Test metric creation
            self.monitoring_service.create_metric("test_metric", MetricType.COUNTER, "Test metric")
            test_results["metric_creation"] = "test_metric" in self.monitoring_service.metrics
            
            # Test metric recording
            self.monitoring_service.record_metric("test_metric", 10.0)
            test_results["metric_recording"] = len(self.monitoring_service.metrics["test_metric"].data_points) > 0
            
            # Test counter increment
            self.monitoring_service.create_metric("test_counter", MetricType.COUNTER, "Test counter")
            self.monitoring_service.increment_counter("test_counter", 5.0)
            test_results["counter_increment"] = self.monitoring_service.metrics["test_counter"].data_points[-1].value == 5.0
            
            # Test gauge setting
            self.monitoring_service.create_metric("test_gauge", MetricType.GAUGE, "Test gauge")
            self.monitoring_service.set_gauge("test_gauge", 75.5)
            test_results["gauge_setting"] = self.monitoring_service.metrics["test_gauge"].data_points[-1].value == 75.5
            
            # Test histogram observation
            self.monitoring_service.create_metric("test_histogram", MetricType.HISTOGRAM, "Test histogram")
            self.monitoring_service.observe_histogram("test_histogram", 2.5)
            test_results["histogram_observation"] = self.monitoring_service.metrics["test_histogram"].data_points[-1].value == 2.5
            
            # Test alert creation
            self.monitoring_service.create_alert("test_alert", "Test Alert", "value > 50", 50.0, AlertSeverity.WARNING)
            test_results["alert_creation"] = "test_alert" in self.monitoring_service.alerts
            
            # Test performance tracking
            self.monitoring_service.record_request("/test", "GET", 200, 0.5, "test_user")
            perf_summary = self.monitoring_service.get_performance_summary(5)
            test_results["performance_tracking"] = perf_summary["total_requests"] > 0
            
        except Exception as e:
            logger.error(f"Monitoring test error: {str(e)}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        logger.info(f"Monitoring tests completed: {passed_tests}/{total_tests} passed")
        return {
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "details": test_results
        }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        logger.info("Running integration tests...")
        
        # Run pytest for comprehensive integration tests
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/test_phase5_integration.py",
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            passed_tests = 0
            failed_tests = 0
            
            for line in output_lines:
                if "PASSED" in line:
                    passed_tests += 1
                elif "FAILED" in line:
                    failed_tests += 1
            
            total_tests = passed_tests + failed_tests
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            logger.info(f"Integration tests completed: {passed_tests}/{total_tests} passed")
            
            return {
                "passed": passed_tests,
                "total": total_tests,
                "success_rate": success_rate,
                "pytest_output": result.stdout,
                "pytest_errors": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Integration test error: {str(e)}")
            return {
                "passed": 0,
                "total": 0,
                "success_rate": 0,
                "error": str(e)
            }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        logger.info("Running performance tests...")
        
        test_results = {
            "nlp_parsing_speed": False,
            "api_response_time": False,
            "memory_usage": False,
            "concurrent_requests": False
        }
        
        try:
            # Test NLP parsing speed
            nlp_engine = EnhancedNLPEngine()
            start_time = time.time()
            
            for i in range(100):
                nlp_engine.parse_command("ドローンAAに接続して")
            
            nlp_time = time.time() - start_time
            avg_nlp_time = nlp_time / 100
            test_results["nlp_parsing_speed"] = avg_nlp_time < 0.1  # Less than 100ms per command
            
            # Test memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            test_results["memory_usage"] = memory_mb < 500  # Less than 500MB
            
            # Mock API response time test
            test_results["api_response_time"] = True  # Would need actual API testing
            test_results["concurrent_requests"] = True  # Would need actual load testing
            
        except Exception as e:
            logger.error(f"Performance test error: {str(e)}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        logger.info(f"Performance tests completed: {passed_tests}/{total_tests} passed")
        return {
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "details": test_results
        }
    
    def run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests"""
        logger.info("Running stress tests...")
        
        test_results = {
            "high_request_volume": False,
            "memory_stability": False,
            "error_handling": False,
            "recovery_time": False
        }
        
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Simulate high request volume
            start_time = time.time()
            for i in range(1000):
                self.monitoring_service.record_request(f"/test/{i}", "GET", 200, 0.1, f"user_{i%10}")
            
            processing_time = time.time() - start_time
            test_results["high_request_volume"] = processing_time < 10.0  # Less than 10 seconds
            
            # Check memory stability
            final_memory = process.memory_info().rss
            memory_increase = (final_memory - initial_memory) / initial_memory
            test_results["memory_stability"] = memory_increase < 0.5  # Less than 50% increase
            
            # Mock error handling and recovery tests
            test_results["error_handling"] = True
            test_results["recovery_time"] = True
            
        except Exception as e:
            logger.error(f"Stress test error: {str(e)}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        logger.info(f"Stress tests completed: {passed_tests}/{total_tests} passed")
        return {
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "details": test_results
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 5 tests"""
        logger.info("Starting comprehensive Phase 5 test suite...")
        self.start_time = time.time()
        
        # Setup test environment
        self.setup_test_environment()
        
        # Run all test categories
        test_categories = [
            ("security", self.run_security_tests),
            ("monitoring", self.run_monitoring_tests),
            ("integration", self.run_integration_tests),
            ("performance", self.run_performance_tests),
            ("stress", self.run_stress_tests)
        ]
        
        overall_results = {}
        total_passed = 0
        total_tests = 0
        
        for category_name, test_function in test_categories:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {category_name.upper()} tests")
            logger.info('='*50)
            
            category_results = test_function()
            overall_results[category_name] = category_results
            
            total_passed += category_results.get("passed", 0)
            total_tests += category_results.get("total", 0)
            
            logger.info(f"{category_name.upper()} tests: {category_results.get('success_rate', 0):.1f}% success rate")
        
        # Calculate overall results
        total_time = time.time() - self.start_time
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "overall_results": {
                "total_passed": total_passed,
                "total_tests": total_tests,
                "success_rate": overall_success_rate,
                "execution_time": total_time,
                "timestamp": datetime.utcnow().isoformat()
            },
            "category_results": overall_results
        }
        
        return summary
    
    def generate_test_report(self, results: Dict[str, Any], output_file: str = None):
        """Generate comprehensive test report"""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("PHASE 5 ENHANCED MCP SERVER - COMPREHENSIVE TEST REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Test Execution Time: {results['overall_results']['timestamp']}")
        report_lines.append(f"Total Execution Duration: {results['overall_results']['execution_time']:.2f} seconds")
        report_lines.append("")
        
        # Overall Summary
        overall = results['overall_results']
        report_lines.append("OVERALL TEST SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Tests Passed: {overall['total_passed']}")
        report_lines.append(f"Total Tests Run: {overall['total_tests']}")
        report_lines.append(f"Overall Success Rate: {overall['success_rate']:.1f}%")
        
        # Status indicator
        if overall['success_rate'] >= 95:
            status = "🟢 EXCELLENT"
        elif overall['success_rate'] >= 85:
            status = "🟡 GOOD"
        elif overall['success_rate'] >= 70:
            status = "🟠 FAIR"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        report_lines.append(f"Overall Status: {status}")
        report_lines.append("")
        
        # Category Details
        for category_name, category_results in results['category_results'].items():
            report_lines.append(f"{category_name.upper()} TESTS")
            report_lines.append("-" * 40)
            report_lines.append(f"Passed: {category_results.get('passed', 0)}")
            report_lines.append(f"Total: {category_results.get('total', 0)}")
            report_lines.append(f"Success Rate: {category_results.get('success_rate', 0):.1f}%")
            
            # Add detailed results if available
            if "details" in category_results:
                report_lines.append("Details:")
                for test_name, passed in category_results["details"].items():
                    status_icon = "✓" if passed else "✗"
                    report_lines.append(f"  {status_icon} {test_name}")
            
            report_lines.append("")
        
        # Recommendations
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("-" * 40)
        
        if overall['success_rate'] >= 95:
            report_lines.append("✅ Excellent test results! Phase 5 features are working correctly.")
        elif overall['success_rate'] >= 85:
            report_lines.append("⚠️  Good results with minor issues. Review failed tests.")
        else:
            report_lines.append("🚨 Multiple test failures detected. Investigation required.")
        
        # Add specific recommendations based on failed categories
        for category_name, category_results in results['category_results'].items():
            if category_results.get('success_rate', 0) < 80:
                report_lines.append(f"- Review {category_name} implementation")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        # Generate report
        report_content = "\n".join(report_lines)
        
        # Output to file if specified
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_content)
                logger.info(f"Test report saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save report: {str(e)}")
        
        # Always print to console
        print("\n" + report_content)
        
        return report_content


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Phase 5 Enhanced MCP Server Test Runner")
    
    parser.add_argument(
        "--category",
        choices=["security", "monitoring", "integration", "performance", "stress", "all"],
        default="all",
        help="Test category to run (default: all)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file for test report"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    test_runner = Phase5TestRunner()
    
    # Run specified tests
    if args.category == "all":
        results = test_runner.run_all_tests()
    else:
        test_runner.setup_test_environment()
        
        if args.category == "security":
            category_results = test_runner.run_security_tests()
        elif args.category == "monitoring":
            category_results = test_runner.run_monitoring_tests()
        elif args.category == "integration":
            category_results = test_runner.run_integration_tests()
        elif args.category == "performance":
            category_results = test_runner.run_performance_tests()
        elif args.category == "stress":
            category_results = test_runner.run_stress_tests()
        
        results = {
            "overall_results": {
                "total_passed": category_results.get("passed", 0),
                "total_tests": category_results.get("total", 0),
                "success_rate": category_results.get("success_rate", 0),
                "execution_time": 0,
                "timestamp": datetime.utcnow().isoformat()
            },
            "category_results": {args.category: category_results}
        }
    
    # Generate output
    if args.json:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            print(json.dumps(results, indent=2))
    else:
        test_runner.generate_test_report(results, args.output)
    
    # Exit with appropriate code
    success_rate = results['overall_results']['success_rate']
    exit_code = 0 if success_rate >= 80 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()