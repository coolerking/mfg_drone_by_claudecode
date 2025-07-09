"""
Phase 5: Security Manager for MCP Server
Provides enhanced security features including:
- Advanced authentication and authorization
- Rate limiting and access control
- Security auditing and threat detection
- Input validation and sanitization
"""

import hashlib
import hmac
import time
import json
import re
import secrets
import base64
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import jwt
from functools import wraps

import logging
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security access levels"""
    PUBLIC = "public"
    READ_ONLY = "read_only"
    OPERATOR = "operator"
    ADMIN = "admin"
    SYSTEM = "system"


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MFAMethod(Enum):
    """Multi-factor authentication methods"""
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"    # SMS verification
    EMAIL = "email"  # Email verification
    BACKUP_CODES = "backup_codes"


class Permission(Enum):
    """Granular permissions"""
    READ_SYSTEM = "read_system"
    WRITE_SYSTEM = "write_system"
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    READ_LOGS = "read_logs"
    WRITE_LOGS = "write_logs"
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    EXECUTE_COMMANDS = "execute_commands"
    MANAGE_SECURITY = "manage_security"
    AUDIT_ACCESS = "audit_access"
    SYSTEM_ADMIN = "system_admin"


class APIKeyScope(Enum):
    """API key scopes"""
    READ_ONLY = "read_only"
    WRITE_ONLY = "write_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: datetime
    event_type: str
    severity: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessAttempt:
    """Access attempt record"""
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    endpoint: str
    success: bool
    failure_reason: Optional[str] = None


@dataclass
class MFASetup:
    """Multi-factor authentication setup"""
    user_id: str
    method: MFAMethod
    secret: str
    backup_codes: List[str] = field(default_factory=list)
    verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExtendedAPIKey:
    """Extended API key with scopes and permissions"""
    key_id: str
    user_id: str
    security_level: SecurityLevel
    scope: APIKeyScope
    permissions: List[Permission]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    rate_limit_override: Optional[int] = None
    ip_restrictions: List[str] = field(default_factory=list)
    active: bool = True


@dataclass
class UserRole:
    """User role with permissions"""
    role_name: str
    permissions: List[Permission]
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserSession:
    """Enhanced user session"""
    session_id: str
    user_id: str
    security_level: SecurityLevel
    permissions: List[Permission]
    created_at: datetime
    last_activity: datetime
    source_ip: str
    user_agent: str = ""
    mfa_verified: bool = False
    requires_mfa: bool = False


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: Optional[str] = None
    jwt_expiry_minutes: int = 60
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    allowed_ips: List[str] = field(default_factory=list)
    blocked_ips: List[str] = field(default_factory=list)
    enable_audit_logging: bool = True
    
    # MFA configuration
    mfa_required: bool = False
    mfa_methods: List[MFAMethod] = field(default_factory=lambda: [MFAMethod.TOTP])
    mfa_issuer: str = "MCP-Server"
    backup_codes_count: int = 10
    
    # API key configuration
    api_key_default_expiry_days: int = 30
    api_key_max_expiry_days: int = 365
    api_key_require_ip_restriction: bool = False
    
    # Session configuration
    session_timeout_minutes: int = 1440  # 24 hours
    session_idle_timeout_minutes: int = 60
    max_concurrent_sessions: int = 5
    
    # Role-based access control
    enable_rbac: bool = True
    default_user_role: str = "user"
    
    # Advanced security features
    enable_anomaly_detection: bool = True
    enable_brute_force_protection: bool = True
    enable_session_fingerprinting: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.jwt_secret:
            raise ValueError(
                "JWT secret is required. Set JWT_SECRET environment variable or provide jwt_secret parameter. "
                "Secret must be at least 32 characters long for security."
            )
        if len(self.jwt_secret) < 32:
            raise ValueError(
                "JWT secret must be at least 32 characters long for security. "
                f"Current length: {len(self.jwt_secret)}"
            )
        # Ensure secret is not a default/weak value
        weak_secrets = [
            "your-secret-key",
            "your-secure-secret-key", 
            "your-secure-secret-key-change-in-production",
            "secret",
            "password",
            "admin",
            "test"
        ]
        if self.jwt_secret.lower() in [s.lower() for s in weak_secrets]:
            raise ValueError(
                f"JWT secret cannot be a default or weak value. "
                f"Please use a strong, randomly generated secret."
            )


class SecurityManager:
    """Enhanced security manager for MCP Server"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.security_events: List[SecurityEvent] = []
        self.access_attempts: List[AccessAttempt] = []
        self.rate_limit_data: Dict[str, List[float]] = {}
        self.failed_attempts: Dict[str, int] = {}
        self.locked_accounts: Dict[str, datetime] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Extended authentication features
        self.mfa_setups: Dict[str, MFASetup] = {}
        self.extended_api_keys: Dict[str, ExtendedAPIKey] = {}
        self.user_roles: Dict[str, UserRole] = {}
        self.enhanced_sessions: Dict[str, UserSession] = {}
        self.session_fingerprints: Dict[str, str] = {}
        
        # Initialize default roles
        self._initialize_default_roles()
        
        logger.info("Security Manager initialized with enhanced authentication features")
    
    def _initialize_default_roles(self):
        """Initialize default user roles"""
        # Public role
        self.user_roles["public"] = UserRole(
            role_name="public",
            permissions=[Permission.READ_SYSTEM],
            description="Public access with read-only system permissions"
        )
        
        # User role
        self.user_roles["user"] = UserRole(
            role_name="user",
            permissions=[Permission.READ_SYSTEM, Permission.READ_USERS],
            description="Standard user with basic read permissions"
        )
        
        # Operator role
        self.user_roles["operator"] = UserRole(
            role_name="operator",
            permissions=[
                Permission.READ_SYSTEM, Permission.WRITE_SYSTEM,
                Permission.READ_USERS, Permission.EXECUTE_COMMANDS
            ],
            description="Operator with system write and command execution permissions"
        )
        
        # Admin role
        self.user_roles["admin"] = UserRole(
            role_name="admin",
            permissions=[
                Permission.READ_SYSTEM, Permission.WRITE_SYSTEM,
                Permission.READ_USERS, Permission.WRITE_USERS,
                Permission.READ_LOGS, Permission.WRITE_LOGS,
                Permission.READ_CONFIG, Permission.WRITE_CONFIG,
                Permission.EXECUTE_COMMANDS, Permission.MANAGE_SECURITY,
                Permission.AUDIT_ACCESS
            ],
            description="Administrator with full system access except system admin"
        )
        
        # System admin role
        self.user_roles["system_admin"] = UserRole(
            role_name="system_admin",
            permissions=list(Permission),
            description="System administrator with all permissions"
        )
    
    # Authentication and Authorization
    
    def generate_api_key(self, user_id: str, security_level: SecurityLevel) -> str:
        """Generate secure API key"""
        timestamp = str(int(time.time()))
        payload = f"{user_id}:{security_level.value}:{timestamp}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.config.jwt_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        api_key = f"{payload}:{signature}"
        logger.info(f"Generated API key for user {user_id} with level {security_level.value}")
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str], Optional[SecurityLevel]]:
        """Validate API key and return user info"""
        try:
            parts = api_key.split(":")
            if len(parts) != 4:
                return False, None, None
            
            user_id, security_level_str, timestamp, signature = parts
            payload = f"{user_id}:{security_level_str}:{timestamp}"
            
            # Verify signature
            expected_signature = hmac.new(
                self.config.jwt_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                self.log_security_event(
                    "INVALID_API_KEY_SIGNATURE",
                    ThreatLevel.MEDIUM,
                    description=f"Invalid API key signature for user {user_id}"
                )
                return False, None, None
            
            # Check timestamp (optional expiry)
            key_age_hours = (time.time() - int(timestamp)) / 3600
            if key_age_hours > 24 * 7:  # 7 days expiry
                self.log_security_event(
                    "EXPIRED_API_KEY",
                    ThreatLevel.LOW,
                    description=f"Expired API key for user {user_id}"
                )
                return False, None, None
            
            security_level = SecurityLevel(security_level_str)
            return True, user_id, security_level
            
        except Exception as e:
            self.log_security_event(
                "API_KEY_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                description=f"API key validation error: {str(e)}"
            )
            return False, None, None
    
    def generate_jwt_token(self, user_id: str, security_level: SecurityLevel) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "security_level": security_level.value,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=self.config.jwt_expiry_minutes)
        }
        
        token = jwt.encode(payload, self.config.jwt_secret, algorithm="HS256")
        
        # Store active session
        self.active_sessions[token] = {
            "user_id": user_id,
            "security_level": security_level,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        logger.info(f"Generated JWT token for user {user_id}")
        return token
    
    def validate_jwt_token(self, token: str) -> Tuple[bool, Optional[str], Optional[SecurityLevel]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=["HS256"])
            user_id = payload["user_id"]
            security_level = SecurityLevel(payload["security_level"])
            
            # Update session activity
            if token in self.active_sessions:
                self.active_sessions[token]["last_activity"] = datetime.utcnow()
            
            return True, user_id, security_level
            
        except jwt.ExpiredSignatureError:
            self.log_security_event(
                "EXPIRED_JWT_TOKEN",
                ThreatLevel.LOW,
                description="Expired JWT token"
            )
            # Remove from active sessions
            if token in self.active_sessions:
                del self.active_sessions[token]
            return False, None, None
            
        except jwt.InvalidTokenError as e:
            self.log_security_event(
                "INVALID_JWT_TOKEN",
                ThreatLevel.MEDIUM,
                description=f"Invalid JWT token: {str(e)}"
            )
            return False, None, None
    
    def check_authorization(self, user_security_level: SecurityLevel, required_level: SecurityLevel) -> bool:
        """Check if user has required authorization level"""
        level_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.READ_ONLY: 1,
            SecurityLevel.OPERATOR: 2,
            SecurityLevel.ADMIN: 3,
            SecurityLevel.SYSTEM: 4
        }
        
        user_level = level_hierarchy.get(user_security_level, 0)
        required_level_num = level_hierarchy.get(required_level, 0)
        
        authorized = user_level >= required_level_num
        
        if not authorized:
            self.log_security_event(
                "AUTHORIZATION_FAILED",
                ThreatLevel.MEDIUM,
                description=f"User level {user_security_level.value} insufficient for required level {required_level.value}"
            )
        
        return authorized
    
    # Multi-Factor Authentication (MFA)
    
    def setup_mfa(self, user_id: str, method: MFAMethod) -> Tuple[bool, str, Optional[str]]:
        """Setup multi-factor authentication for a user"""
        try:
            if method == MFAMethod.TOTP:
                # Generate secret for TOTP
                secret = base64.b32encode(secrets.token_bytes(32)).decode()
                
                # Generate backup codes
                backup_codes = [secrets.token_hex(8) for _ in range(self.config.backup_codes_count)]
                
                mfa_setup = MFASetup(
                    user_id=user_id,
                    method=method,
                    secret=secret,
                    backup_codes=backup_codes,
                    verified=False
                )
                
                self.mfa_setups[user_id] = mfa_setup
                
                # Generate QR code data
                qr_data = f"otpauth://totp/{self.config.mfa_issuer}:{user_id}?secret={secret}&issuer={self.config.mfa_issuer}"
                
                self.log_security_event(
                    "MFA_SETUP_INITIATED",
                    ThreatLevel.LOW,
                    user_id=user_id,
                    description=f"MFA setup initiated for user {user_id} with method {method.value}"
                )
                
                return True, qr_data, secret
                
            elif method in [MFAMethod.SMS, MFAMethod.EMAIL]:
                # For SMS/Email, we would typically send a verification code
                # This is a placeholder implementation
                verification_code = secrets.token_hex(6)
                
                mfa_setup = MFASetup(
                    user_id=user_id,
                    method=method,
                    secret=verification_code,
                    verified=False
                )
                
                self.mfa_setups[user_id] = mfa_setup
                
                self.log_security_event(
                    "MFA_SETUP_INITIATED",
                    ThreatLevel.LOW,
                    user_id=user_id,
                    description=f"MFA setup initiated for user {user_id} with method {method.value}"
                )
                
                return True, f"Verification code sent via {method.value}", verification_code
                
            else:
                return False, "Unsupported MFA method", None
                
        except Exception as e:
            self.log_security_event(
                "MFA_SETUP_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error setting up MFA: {str(e)}"
            )
            return False, f"MFA setup error: {str(e)}", None
    
    def verify_mfa(self, user_id: str, code: str) -> bool:
        """Verify MFA code"""
        try:
            if user_id not in self.mfa_setups:
                return False
            
            mfa_setup = self.mfa_setups[user_id]
            
            if mfa_setup.method == MFAMethod.TOTP:
                # For TOTP, we would typically use a library like pyotp
                # This is a simplified implementation
                return self._verify_totp_code(mfa_setup.secret, code)
                
            elif mfa_setup.method in [MFAMethod.SMS, MFAMethod.EMAIL]:
                # For SMS/Email, verify the code directly
                if code == mfa_setup.secret:
                    mfa_setup.verified = True
                    self.log_security_event(
                        "MFA_VERIFICATION_SUCCESS",
                        ThreatLevel.LOW,
                        user_id=user_id,
                        description=f"MFA verification successful for user {user_id}"
                    )
                    return True
                    
            elif mfa_setup.method == MFAMethod.BACKUP_CODES:
                # Check if code is in backup codes
                if code in mfa_setup.backup_codes:
                    mfa_setup.backup_codes.remove(code)  # Use backup code only once
                    self.log_security_event(
                        "MFA_BACKUP_CODE_USED",
                        ThreatLevel.LOW,
                        user_id=user_id,
                        description=f"MFA backup code used for user {user_id}"
                    )
                    return True
            
            self.log_security_event(
                "MFA_VERIFICATION_FAILED",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"MFA verification failed for user {user_id}"
            )
            return False
            
        except Exception as e:
            self.log_security_event(
                "MFA_VERIFICATION_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error verifying MFA: {str(e)}"
            )
            return False
    
    def _verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code (simplified implementation)"""
        # In a real implementation, use pyotp library
        # This is a placeholder that accepts any 6-digit code
        return len(code) == 6 and code.isdigit()
    
    def is_mfa_required(self, user_id: str, security_level: SecurityLevel) -> bool:
        """Check if MFA is required for user"""
        if not self.config.mfa_required:
            return False
        
        # MFA required for admin and system levels
        if security_level in [SecurityLevel.ADMIN, SecurityLevel.SYSTEM]:
            return True
        
        # Check if user has MFA setup
        return user_id in self.mfa_setups and self.mfa_setups[user_id].verified
    
    # Extended API Key Management
    
    def create_extended_api_key(self, user_id: str, security_level: SecurityLevel,
                               scope: APIKeyScope, permissions: List[Permission],
                               expiry_days: Optional[int] = None,
                               ip_restrictions: List[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Create extended API key with advanced features"""
        try:
            # Generate unique key ID
            key_id = secrets.token_hex(16)
            
            # Set expiry
            if expiry_days is None:
                expiry_days = self.config.api_key_default_expiry_days
            
            if expiry_days > self.config.api_key_max_expiry_days:
                return False, f"Expiry exceeds maximum allowed ({self.config.api_key_max_expiry_days} days)", None
            
            expires_at = datetime.utcnow() + timedelta(days=expiry_days)
            
            # Create API key data
            api_key_data = ExtendedAPIKey(
                key_id=key_id,
                user_id=user_id,
                security_level=security_level,
                scope=scope,
                permissions=permissions,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                ip_restrictions=ip_restrictions or [],
                active=True
            )
            
            # Generate the actual API key
            payload = f"{key_id}:{user_id}:{security_level.value}:{scope.value}:{int(expires_at.timestamp())}"
            signature = hmac.new(
                self.config.jwt_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            api_key = f"{payload}:{signature}"
            
            # Store the API key data
            self.extended_api_keys[key_id] = api_key_data
            
            self.log_security_event(
                "EXTENDED_API_KEY_CREATED",
                ThreatLevel.LOW,
                user_id=user_id,
                description=f"Extended API key created for user {user_id} with scope {scope.value}"
            )
            
            return True, "API key created successfully", api_key
            
        except Exception as e:
            self.log_security_event(
                "API_KEY_CREATION_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error creating API key: {str(e)}"
            )
            return False, f"API key creation error: {str(e)}", None
    
    def validate_extended_api_key(self, api_key: str, source_ip: str = None,
                                 required_permissions: List[Permission] = None) -> Tuple[bool, Optional[str], Optional[ExtendedAPIKey]]:
        """Validate extended API key with advanced checks"""
        try:
            parts = api_key.split(":")
            if len(parts) != 6:
                return False, None, None
            
            key_id, user_id, security_level_str, scope_str, expires_timestamp, signature = parts
            
            # Verify signature
            payload = f"{key_id}:{user_id}:{security_level_str}:{scope_str}:{expires_timestamp}"
            expected_signature = hmac.new(
                self.config.jwt_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                self.log_security_event(
                    "INVALID_EXTENDED_API_KEY_SIGNATURE",
                    ThreatLevel.MEDIUM,
                    source_ip=source_ip,
                    description=f"Invalid extended API key signature for user {user_id}"
                )
                return False, None, None
            
            # Check if key exists and is active
            if key_id not in self.extended_api_keys:
                self.log_security_event(
                    "UNKNOWN_API_KEY",
                    ThreatLevel.MEDIUM,
                    source_ip=source_ip,
                    description=f"Unknown API key ID: {key_id}"
                )
                return False, None, None
            
            api_key_data = self.extended_api_keys[key_id]
            
            # Check if key is active
            if not api_key_data.active:
                self.log_security_event(
                    "INACTIVE_API_KEY",
                    ThreatLevel.MEDIUM,
                    source_ip=source_ip,
                    description=f"Inactive API key used: {key_id}"
                )
                return False, None, None
            
            # Check expiry
            if api_key_data.expires_at and datetime.utcnow() > api_key_data.expires_at:
                self.log_security_event(
                    "EXPIRED_EXTENDED_API_KEY",
                    ThreatLevel.LOW,
                    source_ip=source_ip,
                    description=f"Expired extended API key for user {user_id}"
                )
                return False, None, None
            
            # Check IP restrictions
            if api_key_data.ip_restrictions and source_ip:
                ip_allowed = False
                for allowed_ip in api_key_data.ip_restrictions:
                    try:
                        if ipaddress.ip_address(source_ip) in ipaddress.ip_network(allowed_ip, strict=False):
                            ip_allowed = True
                            break
                    except ValueError:
                        continue
                
                if not ip_allowed:
                    self.log_security_event(
                        "API_KEY_IP_RESTRICTION_VIOLATION",
                        ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        description=f"API key used from restricted IP: {source_ip}"
                    )
                    return False, None, None
            
            # Check permissions
            if required_permissions:
                if not all(perm in api_key_data.permissions for perm in required_permissions):
                    self.log_security_event(
                        "INSUFFICIENT_API_KEY_PERMISSIONS",
                        ThreatLevel.MEDIUM,
                        source_ip=source_ip,
                        user_id=user_id,
                        description=f"API key lacks required permissions: {required_permissions}"
                    )
                    return False, None, None
            
            # Update usage stats
            api_key_data.last_used = datetime.utcnow()
            api_key_data.usage_count += 1
            
            return True, user_id, api_key_data
            
        except Exception as e:
            self.log_security_event(
                "API_KEY_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                source_ip=source_ip,
                description=f"Error validating extended API key: {str(e)}"
            )
            return False, None, None
    
    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        try:
            if key_id in self.extended_api_keys:
                api_key_data = self.extended_api_keys[key_id]
                
                # Check if user owns the key
                if api_key_data.user_id != user_id:
                    self.log_security_event(
                        "UNAUTHORIZED_API_KEY_REVOCATION",
                        ThreatLevel.HIGH,
                        user_id=user_id,
                        description=f"Unauthorized attempt to revoke API key {key_id}"
                    )
                    return False
                
                api_key_data.active = False
                
                self.log_security_event(
                    "API_KEY_REVOKED",
                    ThreatLevel.LOW,
                    user_id=user_id,
                    description=f"API key revoked: {key_id}"
                )
                
                return True
            
            return False
            
        except Exception as e:
            self.log_security_event(
                "API_KEY_REVOCATION_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error revoking API key: {str(e)}"
            )
            return False
    
    # Enhanced Permission Management
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        try:
            if not self.config.enable_rbac:
                return True  # RBAC disabled, allow all
            
            # Check if user has a role
            user_role = self.get_user_role(user_id)
            if not user_role:
                return False
            
            return permission in user_role.permissions
            
        except Exception as e:
            self.log_security_event(
                "PERMISSION_CHECK_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error checking permission: {str(e)}"
            )
            return False
    
    def get_user_role(self, user_id: str) -> Optional[UserRole]:
        """Get user role"""
        # In a real implementation, this would query a database
        # For now, return default role
        return self.user_roles.get(self.config.default_user_role)
    
    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user"""
        try:
            if role_name not in self.user_roles:
                return False
            
            # In a real implementation, this would update a database
            # For now, just log the event
            self.log_security_event(
                "ROLE_ASSIGNED",
                ThreatLevel.LOW,
                user_id=user_id,
                description=f"Role '{role_name}' assigned to user {user_id}"
            )
            
            return True
            
        except Exception as e:
            self.log_security_event(
                "ROLE_ASSIGNMENT_ERROR",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"Error assigning role: {str(e)}"
            )
            return False
    
    # Enhanced Session Management
    
    def create_enhanced_session(self, user_id: str, security_level: SecurityLevel,
                               source_ip: str, user_agent: str = "",
                               requires_mfa: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Create enhanced session with fingerprinting"""
        try:
            # Check concurrent session limit
            user_sessions = [s for s in self.enhanced_sessions.values() if s.user_id == user_id]
            if len(user_sessions) >= self.config.max_concurrent_sessions:
                # Remove oldest session
                oldest_session = min(user_sessions, key=lambda s: s.created_at)
                del self.enhanced_sessions[oldest_session.session_id]
                
                self.log_security_event(
                    "SESSION_LIMIT_EXCEEDED",
                    ThreatLevel.LOW,
                    user_id=user_id,
                    description=f"Session limit exceeded, removed oldest session"
                )
            
            # Generate session ID
            session_id = secrets.token_hex(32)
            
            # Get user permissions
            user_role = self.get_user_role(user_id)
            permissions = user_role.permissions if user_role else []
            
            # Create session
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                security_level=security_level,
                permissions=permissions,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                source_ip=source_ip,
                user_agent=user_agent,
                mfa_verified=not requires_mfa,
                requires_mfa=requires_mfa
            )
            
            self.enhanced_sessions[session_id] = session
            
            # Generate session fingerprint
            if self.config.enable_session_fingerprinting:
                fingerprint = self._generate_session_fingerprint(source_ip, user_agent)
                self.session_fingerprints[session_id] = fingerprint
            
            self.log_security_event(
                "ENHANCED_SESSION_CREATED",
                ThreatLevel.LOW,
                source_ip=source_ip,
                user_id=user_id,
                description=f"Enhanced session created for user {user_id}"
            )
            
            return True, "Session created successfully", session_id
            
        except Exception as e:
            self.log_security_event(
                "SESSION_CREATION_ERROR",
                ThreatLevel.MEDIUM,
                source_ip=source_ip,
                user_id=user_id,
                description=f"Error creating session: {str(e)}"
            )
            return False, f"Session creation error: {str(e)}", None
    
    def validate_enhanced_session(self, session_id: str, source_ip: str = None,
                                 user_agent: str = "") -> Tuple[bool, Optional[UserSession]]:
        """Validate enhanced session"""
        try:
            if session_id not in self.enhanced_sessions:
                return False, None
            
            session = self.enhanced_sessions[session_id]
            
            # Check session timeout
            now = datetime.utcnow()
            if now - session.created_at > timedelta(minutes=self.config.session_timeout_minutes):
                del self.enhanced_sessions[session_id]
                self.log_security_event(
                    "SESSION_TIMEOUT",
                    ThreatLevel.LOW,
                    user_id=session.user_id,
                    description=f"Session timeout for user {session.user_id}"
                )
                return False, None
            
            # Check idle timeout
            if now - session.last_activity > timedelta(minutes=self.config.session_idle_timeout_minutes):
                del self.enhanced_sessions[session_id]
                self.log_security_event(
                    "SESSION_IDLE_TIMEOUT",
                    ThreatLevel.LOW,
                    user_id=session.user_id,
                    description=f"Session idle timeout for user {session.user_id}"
                )
                return False, None
            
            # Check session fingerprint
            if self.config.enable_session_fingerprinting and session_id in self.session_fingerprints:
                current_fingerprint = self._generate_session_fingerprint(source_ip or "", user_agent)
                stored_fingerprint = self.session_fingerprints[session_id]
                
                if current_fingerprint != stored_fingerprint:
                    self.log_security_event(
                        "SESSION_FINGERPRINT_MISMATCH",
                        ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=session.user_id,
                        description=f"Session fingerprint mismatch for user {session.user_id}"
                    )
                    return False, None
            
            # Check MFA requirement
            if session.requires_mfa and not session.mfa_verified:
                return False, None
            
            # Update last activity
            session.last_activity = now
            
            return True, session
            
        except Exception as e:
            self.log_security_event(
                "SESSION_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                source_ip=source_ip,
                description=f"Error validating session: {str(e)}"
            )
            return False, None
    
    def _generate_session_fingerprint(self, source_ip: str, user_agent: str) -> str:
        """Generate session fingerprint"""
        fingerprint_data = f"{source_ip}:{user_agent}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    # Rate Limiting
    
    def check_rate_limit(self, identifier: str, source_ip: str = None) -> bool:
        """Check rate limiting for identifier (user_id or IP)"""
        if not self.config.rate_limiting.enabled:
            return True
        
        current_time = time.time()
        
        # Clean old entries
        if identifier in self.rate_limit_data:
            self.rate_limit_data[identifier] = [
                timestamp for timestamp in self.rate_limit_data[identifier]
                if current_time - timestamp < 3600  # Keep last hour
            ]
        else:
            self.rate_limit_data[identifier] = []
        
        # Check per-minute rate limit
        recent_requests = [
            timestamp for timestamp in self.rate_limit_data[identifier]
            if current_time - timestamp < 60  # Last minute
        ]
        
        if len(recent_requests) >= self.config.rate_limiting.requests_per_minute:
            self.log_security_event(
                "RATE_LIMIT_EXCEEDED",
                ThreatLevel.MEDIUM,
                source_ip=source_ip or "unknown",
                description=f"Rate limit exceeded for {identifier}: {len(recent_requests)} requests/minute"
            )
            return False
        
        # Check per-hour rate limit
        if len(self.rate_limit_data[identifier]) >= self.config.rate_limiting.requests_per_hour:
            self.log_security_event(
                "HOURLY_RATE_LIMIT_EXCEEDED",
                ThreatLevel.HIGH,
                source_ip=source_ip or "unknown",
                description=f"Hourly rate limit exceeded for {identifier}"
            )
            return False
        
        # Record this request
        self.rate_limit_data[identifier].append(current_time)
        return True
    
    # Access Control
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        # Check if IP is blocked
        for blocked_ip in self.config.blocked_ips:
            try:
                if ipaddress.ip_address(ip_address) in ipaddress.ip_network(blocked_ip, strict=False):
                    self.log_security_event(
                        "BLOCKED_IP_ACCESS",
                        ThreatLevel.HIGH,
                        source_ip=ip_address,
                        description=f"Access attempt from blocked IP: {ip_address}"
                    )
                    return False
            except ValueError:
                continue
        
        # If allow list is configured, check if IP is allowed
        if self.config.allowed_ips:
            for allowed_ip in self.config.allowed_ips:
                try:
                    if ipaddress.ip_address(ip_address) in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                except ValueError:
                    continue
            
            # IP not in allow list
            self.log_security_event(
                "UNAUTHORIZED_IP_ACCESS",
                ThreatLevel.MEDIUM,
                source_ip=ip_address,
                description=f"Access attempt from non-whitelisted IP: {ip_address}"
            )
            return False
        
        return True
    
    def record_access_attempt(self, source_ip: str, user_id: Optional[str], 
                            endpoint: str, success: bool, failure_reason: Optional[str] = None):
        """Record access attempt"""
        attempt = AccessAttempt(
            timestamp=datetime.utcnow(),
            source_ip=source_ip,
            user_id=user_id,
            endpoint=endpoint,
            success=success,
            failure_reason=failure_reason
        )
        
        self.access_attempts.append(attempt)
        
        # Handle failed attempts
        if not success and user_id:
            self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1
            
            if self.failed_attempts[user_id] >= self.config.max_failed_attempts:
                self.lock_account(user_id)
                self.log_security_event(
                    "ACCOUNT_LOCKED",
                    ThreatLevel.HIGH,
                    source_ip=source_ip,
                    user_id=user_id,
                    description=f"Account locked due to {self.failed_attempts[user_id]} failed attempts"
                )
        elif success and user_id:
            # Reset failed attempts on successful login
            self.failed_attempts[user_id] = 0
        
        # Keep only recent attempts (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.access_attempts = [
            attempt for attempt in self.access_attempts
            if attempt.timestamp > cutoff_time
        ]
    
    def lock_account(self, user_id: str):
        """Lock user account"""
        lockout_until = datetime.utcnow() + timedelta(minutes=self.config.lockout_duration_minutes)
        self.locked_accounts[user_id] = lockout_until
        logger.warning(f"Account {user_id} locked until {lockout_until}")
    
    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked"""
        if user_id not in self.locked_accounts:
            return False
        
        lockout_until = self.locked_accounts[user_id]
        if datetime.utcnow() > lockout_until:
            # Unlock account
            del self.locked_accounts[user_id]
            self.failed_attempts[user_id] = 0
            logger.info(f"Account {user_id} unlocked")
            return False
        
        return True
    
    # Input Validation and Sanitization
    
    def validate_command_input(self, command: str) -> Tuple[bool, str]:
        """Validate and sanitize command input"""
        # Check length
        if len(command) > 1000:
            return False, "Command too long"
        
        # Check for potential injection attempts
        sql_injection_patterns = [
            r"('|(\\')|(;)|(--)|(\/\*)|(\*\/)",  # SQL injection
            r"<[^>]*>",  # HTML/XML tags
            r"javascript:",  # JavaScript protocol
            r"eval\s*\(",  # JavaScript eval
            r"exec\s*\(",  # Code execution
            r"\$\{.*\}",  # Template injection
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                self.log_security_event(
                    "MALICIOUS_INPUT_DETECTED",
                    ThreatLevel.HIGH,
                    description=f"Potential injection attempt detected: {pattern}"
                )
                return False, "Potentially malicious input detected"
        
        # Sanitize command
        sanitized_command = self.sanitize_input(command)
        return True, sanitized_command
    
    def validate_comprehensive_input(self, input_data: Any, input_type: str = "string", 
                                   max_length: int = 1000, allowed_patterns: List[str] = None) -> Tuple[bool, str, Any]:
        """Comprehensive input validation with type checking"""
        try:
            # Type validation
            if input_type == "string":
                if not isinstance(input_data, str):
                    return False, "Invalid input type, expected string", None
                
                # Length check
                if len(input_data) > max_length:
                    return False, f"Input too long, maximum {max_length} characters", None
                
                # Pattern validation
                if allowed_patterns:
                    pattern_matched = False
                    for pattern in allowed_patterns:
                        if re.match(pattern, input_data):
                            pattern_matched = True
                            break
                    
                    if not pattern_matched:
                        self.log_security_event(
                            "INVALID_INPUT_PATTERN",
                            ThreatLevel.MEDIUM,
                            description=f"Input doesn't match allowed patterns: {input_data[:50]}..."
                        )
                        return False, "Input format not allowed", None
                
                # Enhanced injection detection
                if not self._check_advanced_injection_patterns(input_data):
                    return False, "Potentially malicious input detected", None
                
                sanitized = self.sanitize_input(input_data)
                return True, "Valid input", sanitized
            
            elif input_type == "email":
                if not isinstance(input_data, str):
                    return False, "Invalid input type, expected string", None
                
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, input_data):
                    return False, "Invalid email format", None
                
                if len(input_data) > 254:  # RFC 5321 limit
                    return False, "Email address too long", None
                
                return True, "Valid email", input_data.lower().strip()
            
            elif input_type == "number":
                if isinstance(input_data, str):
                    try:
                        input_data = float(input_data)
                    except ValueError:
                        return False, "Invalid number format", None
                
                if not isinstance(input_data, (int, float)):
                    return False, "Invalid input type, expected number", None
                
                return True, "Valid number", input_data
            
            elif input_type == "json":
                if isinstance(input_data, str):
                    try:
                        parsed_data = json.loads(input_data)
                        # Check for dangerous JSON content
                        if self._check_dangerous_json(parsed_data):
                            return False, "JSON contains potentially dangerous content", None
                        return True, "Valid JSON", parsed_data
                    except json.JSONDecodeError:
                        return False, "Invalid JSON format", None
                
                return True, "Valid JSON", input_data
            
            else:
                return False, f"Unsupported input type: {input_type}", None
                
        except Exception as e:
            self.log_security_event(
                "INPUT_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                description=f"Error during input validation: {str(e)}"
            )
            return False, "Validation error", None
    
    def _check_advanced_injection_patterns(self, input_str: str) -> bool:
        """Check for advanced injection patterns"""
        advanced_patterns = [
            # SQL injection patterns
            r"(union\s+select|union\s+all\s+select)",
            r"(insert\s+into|update\s+set|delete\s+from)",
            r"(drop\s+table|truncate\s+table|alter\s+table)",
            r"(exec\s*\(|execute\s*\(|sp_executesql)",
            r"(xp_cmdshell|xp_regread|xp_regwrite)",
            
            # NoSQL injection patterns
            r"(\$where|\$ne|\$in|\$nin|\$regex)",
            r"(this\s*\.\s*constructor|prototype\s*\[)",
            
            # Command injection patterns
            r"(;\s*cat\s+|;\s*ls\s+|;\s*pwd|;\s*id\s*;)",
            r"(\|\s*nc\s+|\|\s*netcat\s+|\|\s*telnet\s+)",
            r"(&&\s*curl\s+|&&\s*wget\s+|&&\s*python\s+)",
            r"(`.*`|\$\(.*\))",
            
            # XSS patterns
            r"(on\w+\s*=|javascript\s*:|vbscript\s*:)",
            r"(<\s*script|<\s*iframe|<\s*object)",
            r"(expression\s*\(|url\s*\(|import\s*\()",
            
            # Path traversal patterns
            r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c)",
            r"(\/etc\/passwd|\/etc\/shadow|\/windows\/system32)",
            
            # LDAP injection patterns
            r"(\(\s*\|\s*\(|\)\s*\(\s*\|)",
            r"(\*\s*\)\s*\(\s*\||=\s*\*\s*\))",
            
            # XML/XXE injection patterns
            r"(<!ENTITY|<!DOCTYPE|SYSTEM\s+[\"'])",
            r"(&\w+;|%\w+;)",
            
            # Template injection patterns
            r"(\{\{\s*.*\s*\}\}|\{%\s*.*\s*%\})",
            r"(\$\{.*\}|#\{.*\})",
        ]
        
        for pattern in advanced_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self.log_security_event(
                    "ADVANCED_INJECTION_DETECTED",
                    ThreatLevel.HIGH,
                    description=f"Advanced injection pattern detected: {pattern}"
                )
                return False
        
        return True
    
    def _check_dangerous_json(self, json_data: Any) -> bool:
        """Check for dangerous content in JSON data"""
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(key, str) and self._is_dangerous_key(key):
                    return True
                if self._check_dangerous_json(value):
                    return True
        elif isinstance(json_data, list):
            for item in json_data:
                if self._check_dangerous_json(item):
                    return True
        elif isinstance(json_data, str):
            return not self._check_advanced_injection_patterns(json_data)
        
        return False
    
    def _is_dangerous_key(self, key: str) -> bool:
        """Check if JSON key is potentially dangerous"""
        dangerous_keys = [
            "__proto__", "constructor", "prototype", 
            "eval", "exec", "function", "require",
            "import", "module", "exports", "global",
            "process", "Buffer", "child_process"
        ]
        return key.lower() in [k.lower() for k in dangerous_keys]
    
    def validate_file_upload(self, file_data: bytes, filename: str, 
                           max_size: int = 10 * 1024 * 1024,  # 10MB default
                           allowed_extensions: List[str] = None) -> Tuple[bool, str]:
        """Validate uploaded file"""
        try:
            # Check file size
            if len(file_data) > max_size:
                self.log_security_event(
                    "FILE_SIZE_EXCEEDED",
                    ThreatLevel.MEDIUM,
                    description=f"File size {len(file_data)} exceeds limit {max_size}"
                )
                return False, f"File too large, maximum size is {max_size} bytes"
            
            # Check filename
            if not filename or len(filename) > 255:
                return False, "Invalid filename"
            
            # Sanitize filename
            sanitized_filename = self._sanitize_filename(filename)
            if not sanitized_filename:
                return False, "Invalid filename after sanitization"
            
            # Check file extension
            if allowed_extensions:
                file_ext = sanitized_filename.split('.')[-1].lower()
                if file_ext not in [ext.lower() for ext in allowed_extensions]:
                    return False, f"File extension not allowed: {file_ext}"
            
            # Check for dangerous file types
            if self._is_dangerous_file_type(sanitized_filename):
                self.log_security_event(
                    "DANGEROUS_FILE_UPLOAD",
                    ThreatLevel.HIGH,
                    description=f"Dangerous file type detected: {sanitized_filename}"
                )
                return False, "Dangerous file type detected"
            
            # Check file content
            if not self._scan_file_content(file_data, sanitized_filename):
                return False, "File content validation failed"
            
            return True, "File validation successful"
            
        except Exception as e:
            self.log_security_event(
                "FILE_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                description=f"Error during file validation: {str(e)}"
            )
            return False, "File validation error"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\.\.+', '.', sanitized)
        sanitized = sanitized.strip('. ')
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        
        # Limit length
        if len(sanitized) > 255:
            name_part, ext_part = sanitized.rsplit('.', 1)
            sanitized = name_part[:250] + '.' + ext_part
        
        return sanitized
    
    def _is_dangerous_file_type(self, filename: str) -> bool:
        """Check if file type is potentially dangerous"""
        dangerous_extensions = [
            'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jse',
            'jar', 'msi', 'dll', 'sh', 'bash', 'ps1', 'php', 'jsp', 'asp',
            'aspx', 'py', 'pl', 'rb', 'go', 'rs', 'c', 'cpp', 'java',
            'class', 'dex', 'apk', 'ipa', 'dmg', 'pkg', 'deb', 'rpm'
        ]
        
        file_ext = filename.split('.')[-1].lower()
        return file_ext in dangerous_extensions
    
    def _scan_file_content(self, file_data: bytes, filename: str) -> bool:
        """Scan file content for malicious patterns"""
        try:
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'\xCA\xFE\xBA\xBE',  # Java class file
                b'\xDE\xAD\xBE\xEF',  # Some malware signatures
                b'<!DOCTYPE html',  # HTML (could be XSS)
                b'<script',  # JavaScript
                b'<?php',  # PHP
                b'#!/bin/sh',  # Shell script
                b'#!/bin/bash',  # Bash script
            ]
            
            for signature in executable_signatures:
                if file_data.startswith(signature):
                    self.log_security_event(
                        "EXECUTABLE_FILE_DETECTED",
                        ThreatLevel.HIGH,
                        description=f"Executable file signature detected in: {filename}"
                    )
                    return False
            
            # Check for malicious patterns in text files
            if self._is_text_file(filename):
                text_content = file_data.decode('utf-8', errors='ignore')
                if not self._check_advanced_injection_patterns(text_content):
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error scanning file content: {str(e)}")
            return True  # Allow if scanning fails
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is a text file"""
        text_extensions = [
            'txt', 'csv', 'json', 'xml', 'yaml', 'yml', 'md', 'rst',
            'log', 'conf', 'cfg', 'ini', 'properties', 'sql'
        ]
        
        file_ext = filename.split('.')[-1].lower()
        return file_ext in text_extensions
    
    def validate_parameter_dict(self, params: Dict[str, Any], 
                              validation_rules: Dict[str, Dict[str, Any]]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a dictionary of parameters against validation rules"""
        validated_params = {}
        
        try:
            for param_name, rules in validation_rules.items():
                # Check if required parameter is present
                if rules.get('required', False) and param_name not in params:
                    return False, f"Required parameter '{param_name}' missing", {}
                
                # Skip validation if parameter is not present and not required
                if param_name not in params:
                    continue
                
                param_value = params[param_name]
                
                # Validate parameter
                valid, message, validated_value = self.validate_comprehensive_input(
                    param_value,
                    rules.get('type', 'string'),
                    rules.get('max_length', 1000),
                    rules.get('allowed_patterns', None)
                )
                
                if not valid:
                    self.log_security_event(
                        "PARAMETER_VALIDATION_FAILED",
                        ThreatLevel.MEDIUM,
                        description=f"Parameter '{param_name}' validation failed: {message}"
                    )
                    return False, f"Parameter '{param_name}': {message}", {}
                
                validated_params[param_name] = validated_value
            
            return True, "All parameters validated successfully", validated_params
            
        except Exception as e:
            self.log_security_event(
                "PARAMETER_VALIDATION_ERROR",
                ThreatLevel.MEDIUM,
                description=f"Error during parameter validation: {str(e)}"
            )
            return False, "Parameter validation error", {}
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input string"""
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Remove control characters except whitespace
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        # Limit length
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
        
        return sanitized.strip()
    
    # Security Auditing and Monitoring
    
    def log_security_event(self, event_type: str, severity: ThreatLevel, 
                          source_ip: str = "unknown", user_id: Optional[str] = None,
                          description: str = "", metadata: Dict[str, Any] = None):
        """Log security event"""
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            metadata=metadata or {}
        )
        
        self.security_events.append(event)
        
        # Log to system logger based on severity
        if severity == ThreatLevel.CRITICAL:
            logger.critical(f"SECURITY CRITICAL: {event_type} - {description}")
        elif severity == ThreatLevel.HIGH:
            logger.error(f"SECURITY HIGH: {event_type} - {description}")
        elif severity == ThreatLevel.MEDIUM:
            logger.warning(f"SECURITY MEDIUM: {event_type} - {description}")
        else:
            logger.info(f"SECURITY LOW: {event_type} - {description}")
        
        # Keep only recent events (last 30 days)
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        self.security_events = [
            event for event in self.security_events
            if event.timestamp > cutoff_time
        ]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_hour = now - timedelta(hours=1)
        
        # Count events by severity in last 24h
        events_24h = [event for event in self.security_events if event.timestamp > last_24h]
        events_1h = [event for event in self.security_events if event.timestamp > last_hour]
        
        severity_counts_24h = {}
        severity_counts_1h = {}
        
        for severity in ThreatLevel:
            severity_counts_24h[severity.value] = len([
                event for event in events_24h if event.severity == severity
            ])
            severity_counts_1h[severity.value] = len([
                event for event in events_1h if event.severity == severity
            ])
        
        # Count access attempts
        attempts_24h = [attempt for attempt in self.access_attempts if attempt.timestamp > last_24h]
        failed_attempts_24h = [attempt for attempt in attempts_24h if not attempt.success]
        
        return {
            "security_events_24h": len(events_24h),
            "security_events_1h": len(events_1h),
            "severity_counts_24h": severity_counts_24h,
            "severity_counts_1h": severity_counts_1h,
            "access_attempts_24h": len(attempts_24h),
            "failed_attempts_24h": len(failed_attempts_24h),
            "locked_accounts": len(self.locked_accounts),
            "active_sessions": len(self.active_sessions),
            "blocked_ips": len(self.config.blocked_ips),
            "allowed_ips": len(self.config.allowed_ips)
        }
    
    def get_threat_analysis(self) -> Dict[str, Any]:
        """Analyze current threat landscape"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Recent high/critical events
        critical_events = [
            event for event in self.security_events
            if event.timestamp > last_24h and event.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]
        
        # IP addresses with failed attempts
        failed_ips = {}
        for attempt in self.access_attempts:
            if not attempt.success and attempt.timestamp > last_24h:
                failed_ips[attempt.source_ip] = failed_ips.get(attempt.source_ip, 0) + 1
        
        # Suspicious patterns
        suspicious_ips = {ip: count for ip, count in failed_ips.items() if count >= 5}
        
        return {
            "threat_level": "HIGH" if critical_events else "MEDIUM" if suspicious_ips else "LOW",
            "critical_events_24h": len(critical_events),
            "suspicious_ips": suspicious_ips,
            "recommendations": self._get_security_recommendations(critical_events, suspicious_ips)
        }
    
    def _get_security_recommendations(self, critical_events: List[SecurityEvent], 
                                    suspicious_ips: Dict[str, int]) -> List[str]:
        """Get security recommendations"""
        recommendations = []
        
        if critical_events:
            recommendations.append("Investigate critical security events immediately")
        
        if suspicious_ips:
            recommendations.append(f"Consider blocking suspicious IPs: {list(suspicious_ips.keys())}")
        
        if len(self.locked_accounts) > 5:
            recommendations.append("High number of locked accounts - investigate potential attack")
        
        # Check rate limiting effectiveness
        recent_rate_limit_events = [
            event for event in self.security_events
            if event.event_type in ["RATE_LIMIT_EXCEEDED", "HOURLY_RATE_LIMIT_EXCEEDED"]
            and event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        if len(recent_rate_limit_events) > 10:
            recommendations.append("Consider tightening rate limits due to high volume of violations")
        
        if not recommendations:
            recommendations.append("Security posture is good")
        
        return recommendations
    
    # Session Management
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired_sessions = []
        
        for token, session_data in self.active_sessions.items():
            last_activity = session_data["last_activity"]
            if now - last_activity > timedelta(hours=24):  # 24 hour session timeout
                expired_sessions.append(token)
        
        for token in expired_sessions:
            del self.active_sessions[token]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def revoke_session(self, token: str):
        """Revoke a specific session"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            self.log_security_event(
                "SESSION_REVOKED",
                ThreatLevel.LOW,
                description=f"Session revoked"
            )
    
    def revoke_all_user_sessions(self, user_id: str):
        """Revoke all sessions for a user"""
        tokens_to_revoke = []
        
        for token, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                tokens_to_revoke.append(token)
        
        for token in tokens_to_revoke:
            del self.active_sessions[token]
        
        if tokens_to_revoke:
            self.log_security_event(
                "ALL_USER_SESSIONS_REVOKED",
                ThreatLevel.MEDIUM,
                user_id=user_id,
                description=f"All sessions revoked for user {user_id}"
            )


# Security decorators

def require_security_level(required_level: SecurityLevel):
    """Decorator to require specific security level"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependency injection
            # For now, it's a placeholder for the concept
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(requests_per_minute: int = 60):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependency injection
            # For now, it's a placeholder for the concept
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Create security manager
    config = SecurityConfig(
        jwt_secret="your-secure-secret-key",
        max_failed_attempts=3,
        lockout_duration_minutes=10
    )
    
    security_manager = SecurityManager(config)
    
    # Generate API key
    api_key = security_manager.generate_api_key("user123", SecurityLevel.OPERATOR)
    print(f"Generated API key: {api_key}")
    
    # Validate API key
    valid, user_id, level = security_manager.validate_api_key(api_key)
    print(f"Validation result: valid={valid}, user={user_id}, level={level}")
    
    # Generate JWT token
    jwt_token = security_manager.generate_jwt_token("user123", SecurityLevel.OPERATOR)
    print(f"Generated JWT: {jwt_token}")
    
    # Security summary
    summary = security_manager.get_security_summary()
    print(f"Security summary: {summary}")