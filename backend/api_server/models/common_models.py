"""
Common Pydantic models for API responses
Based on OpenAPI specification schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SuccessResponse(BaseModel):
    """成功レスポンス"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "操作が正常に完了しました",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()


class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": True,
                "error_code": "DRONE_NOT_FOUND",
                "message": "指定されたドローンが見つかりません",
                "details": "ドローンID 'drone_001' は存在しません",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }
    )
    
    error: bool = True
    error_code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = datetime.now()