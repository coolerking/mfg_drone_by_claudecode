"""
Settings and configuration for MCP Server
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "MCP Drone Control Server"
    api_version: str = "1.0.0"
    api_description: str = "MCP (Model Context Protocol) server for drone control"
    
    # Server Settings
    host: str = Field(default="localhost", env="MCP_HOST")
    port: int = Field(default=8001, env="MCP_PORT")
    debug: bool = Field(default=False, env="MCP_DEBUG")
    
    # Backend API Settings
    backend_api_url: str = Field(default="http://localhost:8000", env="BACKEND_API_URL")
    backend_api_timeout: int = Field(default=30, env="BACKEND_API_TIMEOUT")
    backend_api_key: Optional[str] = Field(default=None, env="BACKEND_API_KEY")
    
    # Security Settings
    api_key: Optional[str] = Field(default=None, env="MCP_API_KEY")
    jwt_secret: Optional[str] = Field(default=None, env="JWT_SECRET")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Natural Language Processing Settings
    default_language: str = Field(default="ja", env="DEFAULT_LANGUAGE")
    nlp_confidence_threshold: float = Field(default=0.7, env="NLP_CONFIDENCE_THRESHOLD")
    
    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Performance Settings
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()