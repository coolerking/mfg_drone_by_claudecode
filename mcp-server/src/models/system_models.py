"""
System models for MCP Server
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ServerStatus(str, Enum):
    """Server status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class ConnectionStatus(str, Enum):
    """Connection status enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class SystemHealth(str, Enum):
    """System health enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class CheckStatus(str, Enum):
    """Check status enumeration"""
    PASS = "pass"
    FAIL = "fail"


class McpServerStatus(BaseModel):
    """MCP Server status model"""
    status: ServerStatus = Field(..., description="サーバー状態")
    uptime: int = Field(..., description="稼働時間（秒）")
    version: str = Field(..., description="バージョン")
    active_connections: int = Field(..., description="アクティブ接続数")


class BackendSystemStatus(BaseModel):
    """Backend system status model"""
    connection_status: ConnectionStatus = Field(..., description="接続状態")
    api_endpoint: str = Field(..., description="APIエンドポイント")
    response_time: Optional[float] = Field(default=None, description="レスポンス時間（ms）")


class SystemStatusResponse(BaseModel):
    """System status response model"""
    mcp_server: McpServerStatus = Field(..., description="MCPサーバー状態")
    backend_system: BackendSystemStatus = Field(..., description="バックエンドシステム状態")
    connected_drones: int = Field(..., description="接続中ドローン数")
    active_operations: int = Field(..., description="アクティブ操作数")
    system_health: SystemHealth = Field(..., description="システムヘルス")
    timestamp: datetime = Field(default_factory=datetime.now, description="取得時刻")


class HealthCheck(BaseModel):
    """Health check model"""
    name: str = Field(..., description="チェック名")
    status: CheckStatus = Field(..., description="チェック結果")
    message: str = Field(..., description="チェック詳細")
    response_time: Optional[float] = Field(default=None, description="レスポンス時間（ms）")


class HealthResponse(BaseModel):
    """Health response model"""
    status: HealthStatus = Field(..., description="ヘルス状態")
    checks: List[HealthCheck] = Field(..., description="ヘルスチェック詳細")
    timestamp: datetime = Field(default_factory=datetime.now, description="チェック時刻")


class ErrorDetails(BaseModel):
    """Error details model"""
    parsing_error: Optional[str] = Field(default=None, description="解析エラー詳細")
    suggested_corrections: Optional[List[str]] = Field(default=None, description="修正提案")
    original_command: Optional[str] = Field(default=None, description="元のコマンド")


class ApiError(BaseModel):
    """API error model"""
    error: bool = Field(default=True, description="エラーフラグ")
    error_code: str = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[ErrorDetails] = Field(default=None, description="エラー詳細")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生時刻")


# Error code constants
class ErrorCodes:
    """Error code constants"""
    # Command errors
    PARSING_ERROR = "PARSING_ERROR"
    COMMAND_NOT_UNDERSTOOD = "COMMAND_NOT_UNDERSTOOD"
    INVALID_COMMAND = "INVALID_COMMAND"
    
    # Drone errors
    DRONE_NOT_FOUND = "DRONE_NOT_FOUND"
    DRONE_NOT_READY = "DRONE_NOT_READY"
    DRONE_ALREADY_CONNECTED = "DRONE_ALREADY_CONNECTED"
    DRONE_UNAVAILABLE = "DRONE_UNAVAILABLE"
    
    # Vision errors
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    TRACKING_ALREADY_ACTIVE = "TRACKING_ALREADY_ACTIVE"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BACKEND_CONNECTION_ERROR = "BACKEND_CONNECTION_ERROR"
    BACKEND_TIMEOUT = "BACKEND_TIMEOUT"