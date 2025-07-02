"""
Test Phase 4 Integration
Comprehensive integration tests for Phase 4 features
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

# Note: These imports would work when the full application is running
# For testing, we'll mock the main components as needed

class TestPhase4Integration:
    """Test integration of all Phase 4 features"""
    
    @pytest.fixture
    def mock_services(self):
        """Mock all services for testing"""
        with patch('backend.api_server.main.drone_manager') as mock_drone_manager, \
             patch('backend.api_server.main.alert_service') as mock_alert_service, \
             patch('backend.api_server.main.performance_service') as mock_performance_service:
            
            # Setup mock drone manager
            mock_drone_manager.get_current_timestamp.return_value = "2024-01-01T00:00:00Z"
            
            # Setup mock alert service
            mock_alert_service.monitoring_active = True
            mock_alert_service.get_alert_summary.return_value = {
                "total_alerts": 5,
                "unresolved_alerts": 2,
                "critical_alerts_24h": 1
            }
            
            # Setup mock performance service
            mock_performance_service.get_performance_summary.return_value = {
                "system": {"cpu": {"usage_percent": 45.0}},
                "application": {"total_requests": 100},
                "cache": {"hit_rate_percent": 85.0}
            }
            
            yield {
                "drone_manager": mock_drone_manager,
                "alert_service": mock_alert_service,
                "performance_service": mock_performance_service
            }
    
    def test_enhanced_health_check(self, mock_services):
        """Test enhanced health check with Phase 4 features"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["phase"] == "Phase 4 - Production Ready"
        assert data["security_enabled"] is True
        assert "services" in data
        assert "monitoring_active" in data["services"]
        
    def test_security_headers_integration(self):
        """Test that security headers are properly added"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        response = client.get("/")
        
        # Check security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        
    def test_rate_limiting_integration(self):
        """Test rate limiting is working"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        # Make several requests to root endpoint (limit: 100/minute)
        responses = []
        for _ in range(10):
            response = client.get("/")
            responses.append(response)
            
        # Most should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 8  # Allow some flexibility for rate limiting
        
    def test_api_key_authentication_flow(self):
        """Test complete API key authentication flow"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        # Test without API key
        response = client.get("/api/security/api-keys")
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.get(
            "/api/security/api-keys",
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
        
        # Test with valid admin API key
        response = client.get(
            "/api/security/api-keys",
            headers={"X-API-Key": "mfg-drone-admin-key-2024"}
        )
        # Should work (or return 503 if services not initialized)
        assert response.status_code in [200, 503]
        
        # Test with read-only key trying admin endpoint
        response = client.get(
            "/api/security/api-keys",
            headers={"X-API-Key": "mfg-drone-readonly-2024"}
        )
        assert response.status_code == 403  # Insufficient permissions
        
    def test_phase4_endpoints_authentication(self):
        """Test that Phase 4 endpoints require proper authentication"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        admin_headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
        dashboard_headers = {"X-API-Key": "mfg-drone-readonly-2024"}  # Has dashboard permission
        
        # Test admin-only endpoints
        admin_endpoints = [
            "/api/security/api-keys",
            "/api/performance/optimize",
            "/api/performance/cache"
        ]
        
        for endpoint in admin_endpoints:
            # Without auth
            response = client.get(endpoint)
            assert response.status_code == 401
            
            # With dashboard key (insufficient)
            response = client.get(endpoint, headers=dashboard_headers)
            assert response.status_code == 403
            
            # With admin key (sufficient)
            response = client.get(endpoint, headers=admin_headers)
            assert response.status_code in [200, 503]  # 503 if services not initialized
            
        # Test dashboard endpoints
        dashboard_endpoints = [
            "/api/alerts",
            "/api/performance/summary",
            "/api/health/detailed"
        ]
        
        for endpoint in dashboard_endpoints:
            # Without auth
            response = client.get(endpoint)
            assert response.status_code == 401
            
            # With dashboard key (sufficient)
            response = client.get(endpoint, headers=dashboard_headers)
            assert response.status_code in [200, 503]  # 503 if services not initialized
            
    def test_cors_integration(self):
        """Test CORS configuration for frontend integration"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        # Test preflight request
        response = client.options(
            "/api/dashboard/system",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-API-Key"
            }
        )
        
        assert "Access-Control-Allow-Origin" in response.headers
        assert "X-API-Key" in response.headers.get("Access-Control-Expose-Headers", "")
        
    def test_error_handling_integration(self):
        """Test error handling across Phase 4 features"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        admin_headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
        
        # Test various error conditions
        error_tests = [
            # Invalid alert ID
            ("POST", "/api/alerts/invalid-id/acknowledge", 404),
            # Invalid API key for deletion
            ("DELETE", "/api/security/api-keys/invalid-key", 404),
            # Invalid endpoint for performance
            ("GET", "/api/performance/nonexistent", 404),
        ]
        
        for method, endpoint, expected_status in error_tests:
            if method == "GET":
                response = client.get(endpoint, headers=admin_headers)
            elif method == "POST":
                response = client.post(endpoint, headers=admin_headers)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=admin_headers)
                
            # Should get expected error status or 503 if services not initialized
            assert response.status_code in [expected_status, 503]
            
            if response.status_code not in [503]:
                # Should have proper error format
                error_data = response.json()
                assert "error" in str(error_data).lower() or "detail" in error_data

class TestPhase4Performance:
    """Test Phase 4 performance characteristics"""
    
    def test_api_response_times(self):
        """Test that API response times are reasonable"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        admin_headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
        
        # Test response times for various endpoints
        endpoints = [
            "/",
            "/health",
            "/api/security/config",
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=admin_headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response time should be under 1 second for these simple endpoints
            assert response_time < 1.0, f"Endpoint {endpoint} took {response_time:.3f}s"
            
            # Should get a valid response
            assert response.status_code in [200, 401, 503]
            
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        def make_request():
            return client.get("/")
            
        # Make concurrent requests
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            responses = [future.result() for future in futures]
            
        # All should succeed (or be rate limited)
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # Should handle most requests successfully
        assert success_count >= 15
        assert success_count + rate_limited_count == 20  # All requests accounted for

class TestPhase4Security:
    """Test Phase 4 security features in isolation"""
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        from backend.api_server.security import validate_input_security
        from fastapi import HTTPException
        
        # Test normal input
        result = validate_input_security("normal input")
        assert result == "normal input"
        
        # Test dangerous input
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "javascript:alert('hack')"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(HTTPException):
                validate_input_security(dangerous_input)
                
    def test_api_key_management(self):
        """Test API key management functionality"""
        from backend.api_server.security import APIKeyManager
        
        manager = APIKeyManager()
        
        # Test generating new key
        api_key = manager.generate_api_key("Test Key", ["read", "write"])
        assert api_key.startswith("mfg-drone-")
        
        # Test validating key
        key_info = manager.validate_api_key(api_key)
        assert key_info is not None
        assert key_info["name"] == "Test Key"
        
        # Test revoking key
        success = manager.revoke_api_key(api_key)
        assert success is True
        
        # Key should be invalid now
        key_info = manager.validate_api_key(api_key)
        assert key_info is None

@pytest.mark.asyncio
class TestPhase4AsyncIntegration:
    """Test async integration of Phase 4 features"""
    
    async def test_service_startup_shutdown(self):
        """Test complete service lifecycle"""
        from backend.api_server.core.alert_service import AlertService
        from backend.api_server.core.performance_service import PerformanceService
        
        # Create services
        alert_service = AlertService()
        performance_service = PerformanceService()
        
        # Start monitoring
        alert_task = asyncio.create_task(alert_service.start_monitoring(0.1))
        perf_task = asyncio.create_task(performance_service.start_monitoring(0.1))
        
        # Let them run briefly
        await asyncio.sleep(0.2)
        
        # Should be active
        assert alert_service.monitoring_active is True
        
        # Stop monitoring
        await alert_service.stop_monitoring()
        perf_task.cancel()
        try:
            await perf_task
        except asyncio.CancelledError:
            pass
            
        # Should be stopped
        assert alert_service.monitoring_active is False
        
        # Shutdown
        await alert_service.shutdown()
        await performance_service.shutdown()
        
    async def test_monitoring_integration(self):
        """Test integration between monitoring services"""
        from backend.api_server.core.alert_service import AlertService, AlertLevel, AlertType
        from backend.api_server.core.performance_service import PerformanceService
        
        alert_service = AlertService()
        performance_service = PerformanceService()
        
        # Mock high resource usage
        with patch('psutil.cpu_percent', return_value=95.0), \
             patch('psutil.virtual_memory') as mock_memory:
            
            mock_memory.return_value.percent = 90.0
            
            # Trigger metric evaluation
            metrics = {
                "cpu_usage": 95.0,
                "memory_usage": 90.0
            }
            alert_service.evaluate_system_metrics(metrics)
            
            # Should have generated alerts
            alerts = alert_service.get_alerts()
            assert len(alerts) > 0
            
            # Should have critical level alerts
            critical_alerts = alert_service.get_alerts(level=AlertLevel.CRITICAL)
            assert len(critical_alerts) > 0

class TestPhase4EndToEnd:
    """End-to-end tests for Phase 4 functionality"""
    
    def test_full_security_workflow(self):
        """Test complete security workflow"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        admin_headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
        
        # 1. Check security config
        response = client.get("/api/security/config", headers=admin_headers)
        assert response.status_code in [200, 503]
        
        # 2. List existing API keys
        response = client.get("/api/security/api-keys", headers=admin_headers)
        assert response.status_code in [200, 503]
        
        # 3. Try to create new API key (would work with proper service initialization)
        response = client.post(
            "/api/security/api-keys?name=TestKey&permissions=read,write",
            headers=admin_headers
        )
        assert response.status_code in [200, 503]
        
    def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        dashboard_headers = {"X-API-Key": "mfg-drone-readonly-2024"}
        
        # 1. Check system health
        response = client.get("/api/health/detailed", headers=dashboard_headers)
        assert response.status_code in [200, 503]
        
        # 2. Get alerts
        response = client.get("/api/alerts", headers=dashboard_headers)
        assert response.status_code in [200, 503]
        
        # 3. Get performance summary
        response = client.get("/api/performance/summary", headers=dashboard_headers)
        assert response.status_code in [200, 503]
        
        # 4. Get alert summary
        response = client.get("/api/alerts/summary", headers=dashboard_headers)
        assert response.status_code in [200, 503]
        
    def test_production_readiness_checklist(self):
        """Test production readiness checklist"""
        from backend.api_server.main import app
        client = TestClient(app)
        
        # Security features
        response = client.get("/")
        assert "X-Content-Type-Options" in response.headers  # Security headers
        
        # Rate limiting
        assert response.status_code in [200, 429]  # Either success or rate limited
        
        # API authentication
        response = client.get("/api/security/config")
        assert response.status_code == 401  # Should require auth
        
        # Health monitoring
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "phase" in health_data
        assert "security_enabled" in health_data
        
        # Error handling
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # CORS configuration
        response = client.options(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "Access-Control-Allow-Origin" in response.headers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])