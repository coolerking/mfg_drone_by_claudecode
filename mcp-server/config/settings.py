"""
Settings and configuration for MCP Server
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
import logging


class Settings(BaseSettings):
    """Application settings with enhanced security configuration"""
    
    # API Settings
    api_title: str = "MCP Drone Control Server"
    api_version: str = "1.0.0"
    api_description: str = "MCP (Model Context Protocol) server for drone control"
    
    # Server Settings
    host: str = Field(default="localhost", env="MCP_HOST")
    port: int = Field(default=8001, env="MCP_PORT")
    debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # Environment Type
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Backend API Settings
    backend_api_url: str = Field(default="http://localhost:8000", env="BACKEND_API_URL")
    backend_api_timeout: int = Field(default=30, env="BACKEND_API_TIMEOUT")
    backend_api_key: Optional[str] = Field(default=None, env="BACKEND_API_KEY")
    
    # Security Settings
    api_key: Optional[str] = Field(default=None, env="MCP_API_KEY")
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    
    # Authentication Settings
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password: Optional[str] = Field(default=None, env="ADMIN_PASSWORD")
    operator_username: str = Field(default="operator", env="OPERATOR_USERNAME")
    operator_password: Optional[str] = Field(default=None, env="OPERATOR_PASSWORD")
    readonly_username: str = Field(default="readonly", env="READONLY_USERNAME")
    readonly_password: Optional[str] = Field(default=None, env="READONLY_PASSWORD")
    
    # Security Configuration
    max_failed_attempts: int = Field(default=5, env="MAX_FAILED_ATTEMPTS")
    lockout_duration: int = Field(default=15, env="LOCKOUT_DURATION")
    allowed_ips: List[str] = Field(default=[], env="ALLOWED_IPS")
    blocked_ips: List[str] = Field(default=[], env="BLOCKED_IPS")
    
    # SSL/TLS Settings
    ssl_enabled: bool = Field(default=False, env="SSL_ENABLED")
    ssl_cert_path: Optional[str] = Field(default=None, env="SSL_CERT_PATH")
    ssl_key_path: Optional[str] = Field(default=None, env="SSL_KEY_PATH")
    ssl_ca_path: Optional[str] = Field(default=None, env="SSL_CA_PATH")
    force_https: bool = Field(default=False, env="FORCE_HTTPS")
    
    # CORS Settings
    cors_enabled: bool = Field(default=True, env="CORS_ENABLED")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_max_age: int = Field(default=86400, env="CORS_MAX_AGE")
    
    # Security Headers
    security_headers_enabled: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")
    content_security_policy: str = Field(
        default="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        env="CONTENT_SECURITY_POLICY"
    )
    x_frame_options: str = Field(default="DENY", env="X_FRAME_OPTIONS")
    x_content_type_options: str = Field(default="nosniff", env="X_CONTENT_TYPE_OPTIONS")
    referrer_policy: str = Field(default="strict-origin-when-cross-origin", env="REFERRER_POLICY")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_requests_per_hour: int = Field(default=1000, env="RATE_LIMIT_REQUESTS_PER_HOUR")
    rate_limit_burst_size: int = Field(default=10, env="RATE_LIMIT_BURST_SIZE")
    
    # Trusted Hosts
    trusted_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="TRUSTED_HOSTS")
    trusted_hosts_enabled: bool = Field(default=True, env="TRUSTED_HOSTS_ENABLED")
    
    # Natural Language Processing Settings
    default_language: str = Field(default="ja", env="DEFAULT_LANGUAGE")
    nlp_confidence_threshold: float = Field(default=0.7, env="NLP_CONFIDENCE_THRESHOLD")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Security Audit Settings
    audit_logging_enabled: bool = Field(default=True, env="AUDIT_LOGGING_ENABLED")
    audit_log_file: Optional[str] = Field(default=None, env="AUDIT_LOG_FILE")
    audit_log_retention_days: int = Field(default=30, env="AUDIT_LOG_RETENTION_DAYS")
    
    # Performance Settings
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    # Hybrid System Settings
    hybrid_monitor_interval: int = Field(default=30, env="HYBRID_MONITOR_INTERVAL")
    hybrid_max_metrics_history: int = Field(default=100, env="HYBRID_MAX_METRICS_HISTORY")
    hybrid_startup_timeout: float = Field(default=30.0, env="HYBRID_STARTUP_TIMEOUT")
    hybrid_shutdown_timeout: float = Field(default=15.0, env="HYBRID_SHUTDOWN_TIMEOUT")
    hybrid_health_check_interval: float = Field(default=10.0, env="HYBRID_HEALTH_CHECK_INTERVAL")
    hybrid_max_restart_attempts: int = Field(default=3, env="HYBRID_MAX_RESTART_ATTEMPTS")
    
    # Hybrid Alert Thresholds
    hybrid_cpu_threshold: float = Field(default=80.0, env="HYBRID_CPU_THRESHOLD")
    hybrid_memory_threshold: float = Field(default=85.0, env="HYBRID_MEMORY_THRESHOLD")
    hybrid_disk_threshold: float = Field(default=90.0, env="HYBRID_DISK_THRESHOLD")
    hybrid_response_time_threshold: float = Field(default=5.0, env="HYBRID_RESPONSE_TIME_THRESHOLD")
    hybrid_error_rate_threshold: float = Field(default=5.0, env="HYBRID_ERROR_RATE_THRESHOLD")
    
    # Note: FastAPI-related settings have been removed as FastAPI server functionality 
    # has been eliminated from the MCP server implementation
    
    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from environment variable"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("allowed_ips", pre=True)
    def parse_allowed_ips(cls, v):
        """Parse allowed IPs from environment variable"""
        if isinstance(v, str):
            return [ip.strip() for ip in v.split(",") if ip.strip()]
        return v
    
    @validator("blocked_ips", pre=True)
    def parse_blocked_ips(cls, v):
        """Parse blocked IPs from environment variable"""
        if isinstance(v, str):
            return [ip.strip() for ip in v.split(",") if ip.strip()]
        return v
    
    @validator("trusted_hosts", pre=True)
    def parse_trusted_hosts(cls, v):
        """Parse trusted hosts from environment variable"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment type"""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_environments}")
        return v
    
    def validate_production_settings(self):
        """Validate settings for production environment"""
        errors = []
        
        if self.environment == "production":
            # Check for wildcard CORS origins
            if "*" in self.allowed_origins:
                errors.append("CORS wildcard (*) is not allowed in production environment")
            
            # Check for SSL/TLS configuration
            if not self.ssl_enabled:
                errors.append("SSL/TLS must be enabled in production environment")
            
            # Check for strong JWT secret
            if not self.jwt_secret or len(self.jwt_secret) < 32:
                errors.append("JWT secret must be at least 32 characters long in production")
            
            # Check for authentication passwords
            if not self.admin_password:
                errors.append("Admin password must be set in production")
            
            # Check for trusted hosts
            if not self.trusted_hosts_enabled or "*" in self.trusted_hosts:
                errors.append("Trusted hosts must be configured and not use wildcard in production")
        
        if errors:
            raise ValueError(f"Production configuration errors: {'; '.join(errors)}")
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def prepare_field(cls, field):
            """Prepare field for parsing"""
            if field.outer_type_ == List[str]:
                field.default = []
            return field


# Global settings instance
settings = Settings()

# Validate production settings on startup
try:
    settings.validate_production_settings()
except ValueError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Configuration validation error: {e}")
    if settings.is_production():
        raise  # Fail fast in production
    else:
        logger.warning("Running with potentially insecure configuration in development mode")