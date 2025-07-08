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
        
        logger.info("Security Manager initialized")
    
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