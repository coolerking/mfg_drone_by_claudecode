"""
Test suite for Week 3 authentication and audit enhancements
Tests the enhanced security manager and audit service implementations
"""

import pytest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add the src directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.security_manager import (
    SecurityManager, SecurityConfig, SecurityLevel, MFAMethod, 
    Permission, APIKeyScope, RateLimitConfig
)
from core.audit_service import (
    AuditService, AuditEvent, ComplianceFramework, AuditLevel
)


class TestEnhancedSecurityManager:
    """Test enhanced security manager features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = SecurityConfig(
            jwt_secret="test-secret-key-that-is-long-enough-for-security-requirements",
            mfa_required=True,
            mfa_methods=[MFAMethod.TOTP, MFAMethod.EMAIL],
            api_key_default_expiry_days=30,
            session_timeout_minutes=60,
            enable_rbac=True
        )
        self.security_manager = SecurityManager(self.config)
    
    def test_default_roles_initialization(self):
        """Test that default roles are properly initialized"""
        assert "public" in self.security_manager.user_roles
        assert "user" in self.security_manager.user_roles
        assert "operator" in self.security_manager.user_roles
        assert "admin" in self.security_manager.user_roles
        assert "system_admin" in self.security_manager.user_roles
        
        # Check permissions
        admin_role = self.security_manager.user_roles["admin"]
        assert Permission.MANAGE_SECURITY in admin_role.permissions
        assert Permission.SYSTEM_ADMIN not in admin_role.permissions
        
        system_admin_role = self.security_manager.user_roles["system_admin"]
        assert Permission.SYSTEM_ADMIN in system_admin_role.permissions
    
    def test_mfa_setup_totp(self):
        """Test TOTP MFA setup"""
        success, qr_data, secret = self.security_manager.setup_mfa("user123", MFAMethod.TOTP)
        
        assert success is True
        assert qr_data.startswith("otpauth://totp/")
        assert "user123" in qr_data
        assert secret is not None
        assert len(secret) == 52  # Base32 encoded 32 bytes
        
        # Check that MFA setup is stored
        assert "user123" in self.security_manager.mfa_setups
        mfa_setup = self.security_manager.mfa_setups["user123"]
        assert mfa_setup.method == MFAMethod.TOTP
        assert mfa_setup.secret == secret
        assert len(mfa_setup.backup_codes) == 10
    
    def test_mfa_setup_email(self):
        """Test email MFA setup"""
        success, message, verification_code = self.security_manager.setup_mfa("user123", MFAMethod.EMAIL)
        
        assert success is True
        assert "email" in message.lower()
        assert verification_code is not None
        assert len(verification_code) == 12  # secrets.token_hex(6)
        
        # Check that MFA setup is stored
        assert "user123" in self.security_manager.mfa_setups
        mfa_setup = self.security_manager.mfa_setups["user123"]
        assert mfa_setup.method == MFAMethod.EMAIL
        assert mfa_setup.secret == verification_code
    
    def test_mfa_verification(self):
        """Test MFA verification"""
        # Setup Email MFA first
        self.security_manager.setup_mfa("user123", MFAMethod.EMAIL)
        mfa_setup = self.security_manager.mfa_setups["user123"]
        
        # Test correct code for email
        assert self.security_manager.verify_mfa("user123", mfa_setup.secret) is True
        assert mfa_setup.verified is True
        
        # Test incorrect code
        assert self.security_manager.verify_mfa("user123", "wrong_code") is False
        
        # Test non-existent user
        assert self.security_manager.verify_mfa("nonexistent", "code") is False
        
        # Test TOTP verification (more realistic test)
        success, qr_data, secret = self.security_manager.setup_mfa("user456", MFAMethod.TOTP)
        assert success is True
        
        # Generate a valid TOTP code for testing
        totp_code = self.security_manager._generate_totp_code(secret, int(time.time() // 30))
        assert self.security_manager.verify_mfa("user456", totp_code) is True
        
        # Test invalid TOTP code
        assert self.security_manager.verify_mfa("user456", "123456") is False
        assert self.security_manager.verify_mfa("user456", "abcdef") is False
    
    def test_mfa_backup_codes(self):
        """Test MFA backup codes"""
        # Setup TOTP MFA
        self.security_manager.setup_mfa("user123", MFAMethod.TOTP)
        mfa_setup = self.security_manager.mfa_setups["user123"]
        
        # Test backup code
        backup_code = mfa_setup.backup_codes[0]
        original_backup_count = len(mfa_setup.backup_codes)
        
        # Verify backup code
        mfa_setup.method = MFAMethod.BACKUP_CODES
        assert self.security_manager.verify_mfa("user123", backup_code) is True
        
        # Check that backup code was removed
        assert len(mfa_setup.backup_codes) == original_backup_count - 1
        assert backup_code not in mfa_setup.backup_codes
    
    def test_mfa_requirement_check(self):
        """Test MFA requirement checking"""
        # Test without MFA setup
        assert self.security_manager.is_mfa_required("user123", SecurityLevel.ADMIN) is True
        assert self.security_manager.is_mfa_required("user123", SecurityLevel.SYSTEM) is True
        assert self.security_manager.is_mfa_required("user123", SecurityLevel.OPERATOR) is False
        
        # Test with MFA setup
        self.security_manager.setup_mfa("user123", MFAMethod.EMAIL)
        mfa_setup = self.security_manager.mfa_setups["user123"]
        mfa_setup.verified = True
        
        assert self.security_manager.is_mfa_required("user123", SecurityLevel.OPERATOR) is True
    
    def test_extended_api_key_creation(self):
        """Test extended API key creation"""
        permissions = [Permission.READ_SYSTEM, Permission.WRITE_SYSTEM]
        
        success, message, api_key = self.security_manager.create_extended_api_key(
            "user123",
            SecurityLevel.OPERATOR,
            APIKeyScope.READ_WRITE,
            permissions,
            expiry_days=30,
            ip_restrictions=["192.168.1.0/24"]
        )
        
        assert success is True
        assert "successfully" in message
        assert api_key is not None
        
        # Check API key format
        parts = api_key.split(":")
        assert len(parts) == 6
        
        # Check that key is stored
        key_id = parts[0]
        assert key_id in self.security_manager.extended_api_keys
        
        api_key_data = self.security_manager.extended_api_keys[key_id]
        assert api_key_data.user_id == "user123"
        assert api_key_data.scope == APIKeyScope.READ_WRITE
        assert api_key_data.permissions == permissions
        assert api_key_data.ip_restrictions == ["192.168.1.0/24"]
    
    def test_extended_api_key_validation(self):
        """Test extended API key validation"""
        # Create API key
        permissions = [Permission.READ_SYSTEM]
        success, message, api_key = self.security_manager.create_extended_api_key(
            "user123",
            SecurityLevel.OPERATOR,
            APIKeyScope.READ_ONLY,
            permissions,
            ip_restrictions=["192.168.1.100"]
        )
        
        assert success is True
        
        # Test valid key with correct IP
        valid, user_id, api_key_data = self.security_manager.validate_extended_api_key(
            api_key,
            source_ip="192.168.1.100",
            required_permissions=[Permission.READ_SYSTEM]
        )
        
        assert valid is True
        assert user_id == "user123"
        assert api_key_data.usage_count == 1
        
        # Test key with wrong IP
        valid, user_id, api_key_data = self.security_manager.validate_extended_api_key(
            api_key,
            source_ip="192.168.2.100"
        )
        
        assert valid is False
        assert user_id is None
        
        # Test key with insufficient permissions
        valid, user_id, api_key_data = self.security_manager.validate_extended_api_key(
            api_key,
            source_ip="192.168.1.100",
            required_permissions=[Permission.WRITE_SYSTEM]
        )
        
        assert valid is False
        assert user_id is None
    
    def test_api_key_revocation(self):
        """Test API key revocation"""
        # Create API key
        permissions = [Permission.READ_SYSTEM]
        success, message, api_key = self.security_manager.create_extended_api_key(
            "user123",
            SecurityLevel.OPERATOR,
            APIKeyScope.READ_ONLY,
            permissions
        )
        
        key_id = api_key.split(":")[0]
        
        # Revoke key
        assert self.security_manager.revoke_api_key(key_id, "user123") is True
        
        # Check that key is inactive
        api_key_data = self.security_manager.extended_api_keys[key_id]
        assert api_key_data.active is False
        
        # Test unauthorized revocation
        assert self.security_manager.revoke_api_key(key_id, "other_user") is False
    
    def test_permission_checking(self):
        """Test permission checking"""
        # Test with RBAC enabled
        assert self.security_manager.check_permission("user123", Permission.READ_SYSTEM) is True
        assert self.security_manager.check_permission("user123", Permission.SYSTEM_ADMIN) is False
        
        # Test with RBAC disabled
        self.config.enable_rbac = False
        assert self.security_manager.check_permission("user123", Permission.SYSTEM_ADMIN) is True
    
    def test_role_assignment(self):
        """Test role assignment"""
        # Test valid role assignment
        assert self.security_manager.assign_role("user123", "admin") is True
        
        # Test invalid role assignment
        assert self.security_manager.assign_role("user123", "nonexistent_role") is False
    
    def test_enhanced_session_creation(self):
        """Test enhanced session creation"""
        success, message, session_id = self.security_manager.create_enhanced_session(
            "user123",
            SecurityLevel.OPERATOR,
            "192.168.1.100",
            "Mozilla/5.0 (Test Browser)",
            requires_mfa=True
        )
        
        assert success is True
        assert "successfully" in message
        assert session_id is not None
        assert len(session_id) == 64  # secrets.token_hex(32)
        
        # Check session data
        assert session_id in self.security_manager.enhanced_sessions
        session = self.security_manager.enhanced_sessions[session_id]
        assert session.user_id == "user123"
        assert session.security_level == SecurityLevel.OPERATOR
        assert session.source_ip == "192.168.1.100"
        assert session.requires_mfa is True
        assert session.mfa_verified is False
    
    def test_enhanced_session_validation(self):
        """Test enhanced session validation"""
        # Create session
        success, message, session_id = self.security_manager.create_enhanced_session(
            "user123",
            SecurityLevel.OPERATOR,
            "192.168.1.100",
            "Mozilla/5.0 (Test Browser)",
            requires_mfa=False
        )
        
        # Test valid session
        valid, session = self.security_manager.validate_enhanced_session(
            session_id,
            "192.168.1.100",
            "Mozilla/5.0 (Test Browser)"
        )
        
        assert valid is True
        assert session is not None
        assert session.user_id == "user123"
        
        # Test session with wrong fingerprint
        if self.config.enable_session_fingerprinting:
            valid, session = self.security_manager.validate_enhanced_session(
                session_id,
                "192.168.1.200",  # Different IP
                "Mozilla/5.0 (Test Browser)"
            )
            
            assert valid is False
            assert session is None
    
    def test_session_timeout(self):
        """Test session timeout"""
        # Create session
        success, message, session_id = self.security_manager.create_enhanced_session(
            "user123",
            SecurityLevel.OPERATOR,
            "192.168.1.100",
            "Mozilla/5.0 (Test Browser)"
        )
        
        # Manually set old timestamp
        session = self.security_manager.enhanced_sessions[session_id]
        session.created_at = datetime.utcnow() - timedelta(minutes=self.config.session_timeout_minutes + 1)
        
        # Test expired session
        valid, session_data = self.security_manager.validate_enhanced_session(
            session_id,
            "192.168.1.100",
            "Mozilla/5.0 (Test Browser)"
        )
        
        assert valid is False
        assert session_data is None
        assert session_id not in self.security_manager.enhanced_sessions
    
    def test_concurrent_session_limit(self):
        """Test concurrent session limit"""
        # Create maximum number of sessions
        session_ids = []
        for i in range(self.config.max_concurrent_sessions):
            success, message, session_id = self.security_manager.create_enhanced_session(
                "user123",
                SecurityLevel.OPERATOR,
                "192.168.1.100",
                f"Browser {i}"
            )
            assert success is True
            session_ids.append(session_id)
        
        # Create one more session (should remove oldest)
        success, message, new_session_id = self.security_manager.create_enhanced_session(
            "user123",
            SecurityLevel.OPERATOR,
            "192.168.1.100",
            "Browser Extra"
        )
        
        assert success is True
        
        # Check that oldest session was removed
        user_sessions = [s for s in self.security_manager.enhanced_sessions.values() if s.user_id == "user123"]
        assert len(user_sessions) == self.config.max_concurrent_sessions


class TestAuditService:
    """Test audit service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.audit_service = AuditService(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test environment"""
        self.audit_service.stop_continuous_monitoring()
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Check that tables exist
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert "audit_logs" in tables
            assert "compliance_reports" in tables
            assert "access_patterns" in tables
            assert "configuration_changes" in tables
    
    def test_audit_log_entry_integrity(self):
        """Test audit log entry integrity"""
        from core.audit_service import AuditLogEntry
        
        entry = AuditLogEntry(
            event_type=AuditEvent.USER_LOGIN,
            user_id="user123",
            source_ip="192.168.1.100",
            details={"test": "data"}
        )
        
        # Check that checksum is generated
        assert entry.checksum is not None
        assert len(entry.checksum) == 64  # SHA-256 hex
        
        # Check integrity verification
        assert entry.verify_integrity() is True
        
        # Test tampered entry
        entry.details["test"] = "modified"
        assert entry.verify_integrity() is False
    
    def test_log_audit_event(self):
        """Test audit event logging"""
        success = self.audit_service.log_audit_event(
            AuditEvent.USER_LOGIN,
            user_id="user123",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Test)",
            resource="login_page",
            action="authenticate",
            outcome="success",
            details={"method": "password"},
            metadata={"session_id": "sess123"},
            level=AuditLevel.INFO
        )
        
        assert success is True
        
        # Check that event was stored
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs")
            row = cursor.fetchone()
            
            assert row is not None
            assert row[2] == "user_login"  # event_type
            assert row[4] == "user123"     # user_id
            assert row[6] == "192.168.1.100"  # source_ip
    
    def test_track_configuration_change(self):
        """Test configuration change tracking"""
        success = self.audit_service.track_configuration_change(
            user_id="admin",
            component="security_config",
            old_value={"mfa_required": False},
            new_value={"mfa_required": True},
            change_type="update",
            approval_required=True
        )
        
        assert success is True
        
        # Check that change was stored
        import sqlite3
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM configuration_changes")
            row = cursor.fetchone()
            
            assert row is not None
            assert row[2] == "admin"  # user_id
            assert row[3] == "security_config"  # component
            assert row[6] == "update"  # change_type
            assert row[7] == "pending"  # approval_status
    
    def test_compliance_rules_loading(self):
        """Test compliance rules loading"""
        # Check that rules are loaded
        assert len(self.audit_service.compliance_rules) > 0
        
        # Check specific rules
        assert "sox_001" in self.audit_service.compliance_rules
        assert "hipaa_001" in self.audit_service.compliance_rules
        assert "pci_001" in self.audit_service.compliance_rules
        assert "gdpr_001" in self.audit_service.compliance_rules
        
        # Check rule properties
        sox_rule = self.audit_service.compliance_rules["sox_001"]
        assert sox_rule.framework == ComplianceFramework.SOX
        assert sox_rule.control_id == "SOX-404"
        assert AuditEvent.CONFIG_CHANGED in sox_rule.required_events
    
    def test_compliance_report_generation(self):
        """Test compliance report generation"""
        # Add some test data
        self.audit_service.log_audit_event(
            AuditEvent.CONFIG_CHANGED,
            user_id="admin",
            action="update",
            outcome="success"
        )
        
        # Generate report
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        report = self.audit_service.generate_compliance_report(
            ComplianceFramework.SOX,
            start_date,
            end_date
        )
        
        assert report is not None
        assert report.framework == ComplianceFramework.SOX
        assert report.total_rules > 0
        assert report.compliance_percentage >= 0
        assert report.compliance_percentage <= 100
        assert len(report.findings) > 0
        assert len(report.recommendations) > 0
    
    def test_access_pattern_analysis(self):
        """Test access pattern analysis"""
        # Add test data
        user_id = "user123"
        for i in range(10):
            self.audit_service.log_audit_event(
                AuditEvent.DATA_ACCESS,
                user_id=user_id,
                source_ip=f"192.168.1.{100 + i % 3}",
                user_agent="Mozilla/5.0 (Test)",
                resource="data:sensitive",
                action="read",
                outcome="success"
            )
        
        # Analyze patterns
        patterns = self.audit_service.analyze_access_patterns(user_id)
        
        assert len(patterns) > 0
        
        pattern = patterns[0]
        assert pattern.user_id == user_id
        assert pattern.access_frequency == 10
        assert len(pattern.locations) == 3  # 3 different IPs
        assert pattern.risk_score >= 0
        assert pattern.risk_score <= 1
        
        # Test with pagination limit
        patterns_limited = self.audit_service.analyze_access_patterns(user_id, limit=5)
        assert len(patterns_limited) > 0
        
        # The access frequency should be limited by the pagination
        limited_pattern = patterns_limited[0]
        assert limited_pattern.access_frequency <= 5
    
    def test_audit_log_export(self):
        """Test audit log export"""
        # Add test data
        self.audit_service.log_audit_event(
            AuditEvent.USER_LOGIN,
            user_id="user123",
            source_ip="192.168.1.100",
            outcome="success"
        )
        
        # Test JSON export
        json_data = self.audit_service.export_audit_logs(format="json")
        assert json_data is not None
        
        data = json.loads(json_data)
        assert len(data) > 0
        assert data[0]["event_type"] == "user_login"
        assert data[0]["user_id"] == "user123"
        
        # Test CSV export
        csv_data = self.audit_service.export_audit_logs(format="csv")
        assert csv_data is not None
        assert "event_type" in csv_data
        assert "user_login" in csv_data
    
    def test_audit_statistics(self):
        """Test audit statistics"""
        # Add test data
        self.audit_service.log_audit_event(
            AuditEvent.USER_LOGIN,
            user_id="user123",
            level=AuditLevel.INFO
        )
        
        self.audit_service.log_audit_event(
            AuditEvent.SECURITY_EVENT,
            user_id="user123",
            level=AuditLevel.WARNING
        )
        
        # Get statistics
        stats = self.audit_service.get_audit_statistics()
        
        assert stats["total_logs"] >= 2
        assert "user_login" in stats["logs_by_type"]
        assert "security_event" in stats["logs_by_type"]
        assert "info" in stats["logs_by_level"]
        assert "warning" in stats["logs_by_level"]
        assert stats["recent_activity_24h"] >= 2
    
    def test_continuous_monitoring(self):
        """Test continuous monitoring"""
        # Start monitoring
        self.audit_service.start_continuous_monitoring()
        assert self.audit_service.monitoring_active is True
        
        # Stop monitoring
        self.audit_service.stop_continuous_monitoring()
        assert self.audit_service.monitoring_active is False


class TestIntegration:
    """Integration tests for security manager and audit service"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.config = SecurityConfig(
            jwt_secret="test-secret-key-that-is-long-enough-for-security-requirements",
            enable_audit_logging=True
        )
        
        self.security_manager = SecurityManager(self.config)
        self.audit_service = AuditService(db_path=self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test environment"""
        self.audit_service.stop_continuous_monitoring()
        os.unlink(self.temp_db.name)
    
    def test_security_events_to_audit_logs(self):
        """Test integration between security events and audit logs"""
        # Generate security event
        api_key = self.security_manager.generate_api_key("user123", SecurityLevel.OPERATOR)
        
        # Log to audit service
        self.audit_service.log_audit_event(
            AuditEvent.API_KEY_CREATED,
            user_id="user123",
            resource="api_key",
            action="generate",
            outcome="success",
            details={"security_level": SecurityLevel.OPERATOR.value}
        )
        
        # Verify audit log
        stats = self.audit_service.get_audit_statistics()
        assert stats["total_logs"] >= 1
        assert "api_key_created" in stats["logs_by_type"]
    
    def test_compliance_with_security_features(self):
        """Test compliance checking with security features"""
        # Create configuration change
        self.audit_service.track_configuration_change(
            user_id="admin",
            component="mfa_settings",
            old_value={"required": False},
            new_value={"required": True},
            change_type="update"
        )
        
        # Generate compliance report
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()
        
        report = self.audit_service.generate_compliance_report(
            ComplianceFramework.SOX,
            start_date,
            end_date
        )
        
        # Check that configuration change impacts compliance
        assert report.total_rules > 0
        config_related_findings = [
            f for f in report.findings 
            if f.get("rule_id") == "sox_001"
        ]
        assert len(config_related_findings) > 0


def run_tests():
    """Run all tests"""
    print("Running Week 3 Authentication and Audit Tests...")
    print("=" * 50)
    
    try:
        # Test Enhanced Security Manager
        print("\n1. Testing Enhanced Security Manager...")
        test_security = TestEnhancedSecurityManager()
        test_security.setup_method()
        
        test_security.test_default_roles_initialization()
        print("   ✓ Default roles initialization")
        
        test_security.test_mfa_setup_totp()
        print("   ✓ MFA TOTP setup")
        
        test_security.test_mfa_setup_email()
        print("   ✓ MFA email setup")
        
        test_security.test_mfa_verification()
        print("   ✓ MFA verification")
        
        test_security.test_extended_api_key_creation()
        print("   ✓ Extended API key creation")
        
        test_security.test_extended_api_key_validation()
        print("   ✓ Extended API key validation")
        
        test_security.test_enhanced_session_creation()
        print("   ✓ Enhanced session creation")
        
        test_security.test_enhanced_session_validation()
        print("   ✓ Enhanced session validation")
        
        # Test Audit Service
        print("\n2. Testing Audit Service...")
        test_audit = TestAuditService()
        test_audit.setup_method()
        
        test_audit.test_database_initialization()
        print("   ✓ Database initialization")
        
        test_audit.test_audit_log_entry_integrity()
        print("   ✓ Audit log entry integrity")
        
        test_audit.test_log_audit_event()
        print("   ✓ Audit event logging")
        
        test_audit.test_track_configuration_change()
        print("   ✓ Configuration change tracking")
        
        test_audit.test_compliance_rules_loading()
        print("   ✓ Compliance rules loading")
        
        test_audit.test_compliance_report_generation()
        print("   ✓ Compliance report generation")
        
        test_audit.test_access_pattern_analysis()
        print("   ✓ Access pattern analysis")
        
        test_audit.test_audit_log_export()
        print("   ✓ Audit log export")
        
        test_audit.teardown_method()
        
        # Test Integration
        print("\n3. Testing Integration...")
        test_integration = TestIntegration()
        test_integration.setup_method()
        
        test_integration.test_security_events_to_audit_logs()
        print("   ✓ Security events to audit logs")
        
        test_integration.test_compliance_with_security_features()
        print("   ✓ Compliance with security features")
        
        test_integration.teardown_method()
        
        print("\n" + "=" * 50)
        print("✅ All Week 3 tests passed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)