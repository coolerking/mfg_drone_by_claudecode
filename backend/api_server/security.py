"""
Security and Authentication Module
Implements API Key authentication, rate limiting, and security middleware
"""

import hashlib
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Set

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Security configuration
API_KEYS: Dict[str, Dict] = {
    # Default API keys for testing - in production these should be from environment/database
    "mfg-drone-admin-key-2024": {
        "name": "Admin Key",
        "permissions": ["admin", "read", "write", "dashboard"],
        "created_at": datetime.now(),
        "expires_at": None,
        "usage_count": 0
    },
    "mfg-drone-readonly-2024": {
        "name": "Read-Only Key", 
        "permissions": ["read", "dashboard"],
        "created_at": datetime.now(),
        "expires_at": None,
        "usage_count": 0
    }
}

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class APIKeyManager:
    """Manager for API key operations"""
    
    def __init__(self):
        self.keys = API_KEYS.copy()
        
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return key info"""
        if not api_key or api_key not in self.keys:
            return None
            
        key_info = self.keys[api_key]
        
        # Check if key is expired
        if key_info.get("expires_at") and key_info["expires_at"] < datetime.now():
            logger.warning(f"Expired API key used: {api_key[:8]}...")
            return None
            
        # Update usage count
        key_info["usage_count"] += 1
        key_info["last_used"] = datetime.now()
        
        return key_info
        
    def generate_api_key(self, name: str, permissions: list, expires_days: Optional[int] = None) -> str:
        """Generate a new API key"""
        api_key = f"mfg-drone-{secrets.token_urlsafe(32)}"
        expires_at = datetime.now() + timedelta(days=expires_days) if expires_days else None
        
        self.keys[api_key] = {
            "name": name,
            "permissions": permissions,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "usage_count": 0
        }
        
        logger.info(f"Generated new API key: {name}")
        return api_key
        
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        if api_key in self.keys:
            del self.keys[api_key]
            logger.info(f"Revoked API key: {api_key[:8]}...")
            return True
        return False
        
    def list_api_keys(self) -> Dict[str, Dict]:
        """List all API keys (excluding sensitive info)"""
        return {
            key[:8] + "...": {
                "name": info["name"],
                "permissions": info["permissions"],
                "created_at": info["created_at"],
                "expires_at": info.get("expires_at"),
                "usage_count": info.get("usage_count", 0),
                "last_used": info.get("last_used")
            }
            for key, info in self.keys.items()
        }

# Global API key manager instance
api_key_manager = APIKeyManager()

def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Extract and validate API key from request headers"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header."
        )
    
    key_info = api_key_manager.validate_api_key(api_key)
    if not key_info:
        logger.warning(f"Invalid API key attempted: {api_key[:8] if api_key else 'None'}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    logger.debug(f"API key validated: {key_info['name']}")
    return api_key

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(api_key: str = Depends(get_api_key)) -> str:
        key_info = api_key_manager.validate_api_key(api_key)
        if not key_info or permission not in key_info.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return api_key
    return permission_checker

# Permission-specific dependencies
require_read = require_permission("read")
require_write = require_permission("write") 
require_admin = require_permission("admin")
require_dashboard = require_permission("dashboard")

class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.failed_attempts: Dict[str, list] = {}
        
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
        
    def record_failed_attempt(self, ip: str):
        """Record failed authentication attempt"""
        now = time.time()
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
            
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip] 
            if now - attempt < 3600
        ]
        
        # Add current attempt
        self.failed_attempts[ip].append(now)
        
        # Block IP if too many failures
        if len(self.failed_attempts[ip]) >= 10:
            self.blocked_ips.add(ip)
            logger.warning(f"Blocked IP due to failed attempts: {ip}")
            
    def clear_failed_attempts(self, ip: str):
        """Clear failed attempts for IP"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]

# Global security middleware instance
security_middleware = SecurityMiddleware()

def validate_input_security(data: str, max_length: int = 1000) -> str:
    """Validate input for security (basic sanitization)"""
    if not data:
        return data
        
    # Length check
    if len(data) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input too long. Maximum {max_length} characters allowed."
        )
    
    # Basic SQL injection prevention (simple check)
    dangerous_patterns = [
        "'; DROP TABLE", "'; DELETE FROM", "'; UPDATE",
        "<script>", "</script>", "javascript:",
        "onload=", "onerror=", "onclick="
    ]
    
    data_lower = data.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in data_lower:
            logger.warning(f"Potentially dangerous input detected: {pattern}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input detected"
            )
    
    return data

def get_rate_limiter():
    """Get rate limiter instance"""
    return limiter

# Security utilities
def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging/storage"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def generate_secure_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

# Security configuration for production
SECURITY_CONFIG = {
    "api_key_required": True,
    "rate_limiting_enabled": True,
    "security_headers_enabled": True,
    "input_validation_enabled": True,
    "ip_blocking_enabled": True,
    "max_failed_attempts": 10,
    "failed_attempt_window_hours": 1
}

def get_security_config() -> Dict:
    """Get current security configuration"""
    return SECURITY_CONFIG.copy()

logger.info("Security module initialized with API key authentication")