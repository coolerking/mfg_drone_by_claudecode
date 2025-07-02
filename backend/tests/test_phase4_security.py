"""
Test Phase 4 Security Features
Tests for API authentication, rate limiting, and security middleware
"""

import pytest
import time
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.api_server.security import (
    APIKeyManager,
    SecurityMiddleware,
    validate_input_security,
    api_key_manager
)

class TestAPIKeyManager:
    """Test API key management"""
    
    def test_validate_valid_api_key(self):
        """Test validating a valid API key"""
        manager = APIKeyManager()
        
        # Use one of the default keys
        valid_key = "mfg-drone-admin-key-2024"
        result = manager.validate_api_key(valid_key)
        
        assert result is not None
        assert result["name"] == "Admin Key"
        assert "admin" in result["permissions"]
        assert result["usage_count"] == 1
        
    def test_validate_invalid_api_key(self):
        """Test validating an invalid API key"""
        manager = APIKeyManager()
        
        result = manager.validate_api_key("invalid-key")
        assert result is None
        
    def test_validate_empty_api_key(self):
        """Test validating empty API key"""
        manager = APIKeyManager()
        
        result = manager.validate_api_key("")
        assert result is None
        
        result = manager.validate_api_key(None)
        assert result is None
        
    def test_generate_api_key(self):
        """Test generating new API key"""
        manager = APIKeyManager()
        
        api_key = manager.generate_api_key("Test Key", ["read", "write"])
        
        assert api_key.startswith("mfg-drone-")
        assert len(api_key) > 20
        
        # Validate the generated key
        key_info = manager.validate_api_key(api_key)
        assert key_info is not None
        assert key_info["name"] == "Test Key"
        assert key_info["permissions"] == ["read", "write"]
        
    def test_revoke_api_key(self):
        """Test revoking API key"""
        manager = APIKeyManager()
        
        # Generate a key
        api_key = manager.generate_api_key("Temp Key", ["read"])
        
        # Verify it exists
        assert manager.validate_api_key(api_key) is not None
        
        # Revoke it
        success = manager.revoke_api_key(api_key)
        assert success is True
        
        # Verify it's gone
        assert manager.validate_api_key(api_key) is None
        
    def test_revoke_nonexistent_key(self):
        """Test revoking non-existent key"""
        manager = APIKeyManager()
        
        success = manager.revoke_api_key("nonexistent-key")
        assert success is False
        
    def test_list_api_keys(self):
        """Test listing API keys"""
        manager = APIKeyManager()
        
        keys = manager.list_api_keys()
        assert len(keys) >= 2  # Should have at least the default keys
        
        # Check that sensitive data is hidden
        for key_preview, info in keys.items():
            assert len(key_preview) <= 11  # Should be truncated with "..."
            assert "name" in info
            assert "permissions" in info
            assert "created_at" in info

class TestSecurityMiddleware:
    """Test security middleware"""
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        middleware = SecurityMiddleware()
        
        test_ip = "192.168.1.100"
        
        # Initially not blocked
        assert not middleware.is_ip_blocked(test_ip)
        
        # Record multiple failed attempts
        for _ in range(12):
            middleware.record_failed_attempt(test_ip)
            
        # Should be blocked now
        assert middleware.is_ip_blocked(test_ip)
        
    def test_failed_attempts_cleanup(self):
        """Test cleanup of old failed attempts"""
        middleware = SecurityMiddleware()
        
        test_ip = "192.168.1.101"
        
        # Mock time to simulate old attempts
        with patch('time.time', return_value=1000):
            for _ in range(5):
                middleware.record_failed_attempt(test_ip)
                
        # Current time (3601 seconds later)
        with patch('time.time', return_value=4601):
            middleware.record_failed_attempt(test_ip)
            
        # Should only have 1 recent attempt
        assert len(middleware.failed_attempts[test_ip]) == 1
        
    def test_clear_failed_attempts(self):
        """Test clearing failed attempts"""
        middleware = SecurityMiddleware()
        
        test_ip = "192.168.1.102"
        
        # Record some attempts
        for _ in range(3):
            middleware.record_failed_attempt(test_ip)
            
        assert len(middleware.failed_attempts[test_ip]) == 3
        
        # Clear attempts
        middleware.clear_failed_attempts(test_ip)
        
        assert test_ip not in middleware.failed_attempts

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_validate_normal_input(self):
        """Test validating normal input"""
        test_data = "Normal test input"
        result = validate_input_security(test_data)
        assert result == test_data
        
    def test_validate_empty_input(self):
        """Test validating empty input"""
        result = validate_input_security("")
        assert result == ""
        
        result = validate_input_security(None)
        assert result is None
        
    def test_validate_long_input(self):
        """Test validating input that's too long"""
        long_input = "a" * 1001
        
        with pytest.raises(HTTPException) as exc_info:
            validate_input_security(long_input)
            
        assert exc_info.value.status_code == 400
        assert "too long" in str(exc_info.value.detail)
        
    def test_validate_dangerous_sql_input(self):
        """Test validating potentially dangerous SQL input"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "'; DELETE FROM data; --",
            "'; UPDATE users SET password = 'hacked'; --"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(HTTPException) as exc_info:
                validate_input_security(dangerous_input)
                
            assert exc_info.value.status_code == 400
            assert "Invalid input detected" in str(exc_info.value.detail)
            
    def test_validate_dangerous_xss_input(self):
        """Test validating potentially dangerous XSS input"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<div onload=alert('xss')></div>"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(HTTPException) as exc_info:
                validate_input_security(dangerous_input)
                
            assert exc_info.value.status_code == 400
            assert "Invalid input detected" in str(exc_info.value.detail)
            
    def test_validate_custom_max_length(self):
        """Test validating with custom max length"""
        test_input = "a" * 50
        
        # Should pass with max_length 100
        result = validate_input_security(test_input, max_length=100)
        assert result == test_input
        
        # Should fail with max_length 10
        with pytest.raises(HTTPException):
            validate_input_security(test_input, max_length=10)

@pytest.fixture
def client():
    """Create test client with Phase 4 security"""
    from backend.api_server.main import app
    return TestClient(app)

class TestSecurityIntegration:
    """Test security integration with API endpoints"""
    
    def test_api_key_required(self, client):
        """Test that API key is required for protected endpoints"""
        # Try accessing dashboard without API key
        response = client.get("/api/dashboard/system")
        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]
        
    def test_valid_api_key_access(self, client):
        """Test accessing endpoint with valid API key"""
        headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
        
        # Should be able to access with valid key
        response = client.get("/api/dashboard/system", headers=headers)
        # Note: Might return 503 if services not initialized in test, but auth should pass
        assert response.status_code in [200, 503]
        
    def test_invalid_api_key_access(self, client):
        """Test accessing endpoint with invalid API key"""
        headers = {"X-API-Key": "invalid-key"}
        
        response = client.get("/api/dashboard/system", headers=headers)
        assert response.status_code == 401
        assert "Invalid or expired API key" in response.json()["detail"]
        
    def test_permission_enforcement(self, client):
        """Test that permissions are enforced"""
        headers = {"X-API-Key": "mfg-drone-readonly-2024"}
        
        # Read-only key trying to access admin endpoint
        response = client.get("/api/security/api-keys", headers=headers)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
        
    def test_rate_limiting(self, client):
        """Test rate limiting on endpoints"""
        # Test rate limiting on root endpoint (100/minute)
        responses = []
        
        # Make many requests quickly
        for _ in range(10):
            response = client.get("/")
            responses.append(response)
            
        # Most should succeed, but if we hit the limit, we'll get 429
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # Should have some successful requests
        assert success_count > 0
        
        # If any are rate limited, they should have the right error
        if rate_limited_count > 0:
            rate_limited_response = next(r for r in responses if r.status_code == 429)
            assert "rate limit exceeded" in rate_limited_response.text.lower()
            
    def test_security_headers(self, client):
        """Test that security headers are added"""
        response = client.get("/")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
    def test_cors_configuration(self, client):
        """Test CORS configuration"""
        # Test preflight request
        response = client.options(
            "/api/dashboard/system",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-API-Key"
            }
        )
        
        # Should allow the origin
        assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"
        assert "X-API-Key" in response.headers.get("Access-Control-Expose-Headers", "")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])