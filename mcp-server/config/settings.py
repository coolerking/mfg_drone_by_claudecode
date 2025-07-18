"""
Settings and configuration for MCP Server
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
import logging


class Settings(BaseSettings):
    """Application settings with enhanced security configuration"""
    
    # MCP Server Settings
    server_title: str = "MCP Drone Control Server"
    server_version: str = "1.0.0"
    server_description: str = "MCP (Model Context Protocol) server for drone control"
    
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
    
    # HTTP server related settings removed for pure MCP server
    
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
    
    # HTTP server performance and hybrid system settings removed for pure MCP server
    
    # Note: FastAPI-related settings have been removed as FastAPI server functionality 
    # has been eliminated from the MCP server implementation
    
    # HTTP server related validators removed
    
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
    
    # trusted_hosts validator removed
    
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
            # Check for strong JWT secret
            if not self.jwt_secret or len(self.jwt_secret) < 32:
                errors.append("JWT secret must be at least 32 characters long in production")
            
            # Check for authentication passwords
            if not self.admin_password:
                errors.append("Admin password must be set in production")
        
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