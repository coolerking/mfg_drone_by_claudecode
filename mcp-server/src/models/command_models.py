"""
Command models for natural language processing
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """Execution mode for batch commands"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class NaturalLanguageCommand(BaseModel):
    """Natural language command model"""
    command: str = Field(..., description="自然言語コマンド")
    context: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="追加のコンテキスト情報"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="実行オプション"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "command": "ドローンAAに接続して高さ1メートルまで上昇して",
                "context": {
                    "drone_id": "drone-001",
                    "language": "ja"
                },
                "options": {
                    "confirm_before_execution": False,
                    "dry_run": False
                }
            }
        }


class BatchCommand(BaseModel):
    """Batch command model"""
    commands: List[NaturalLanguageCommand] = Field(..., description="実行するコマンド一覧")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL, description="実行モード")
    stop_on_error: bool = Field(default=True, description="エラー時停止")
    
    class Config:
        schema_extra = {
            "example": {
                "commands": [
                    {
                        "command": "ドローンAAに接続して"
                    },
                    {
                        "command": "高さ1メートルまで上昇して"
                    }
                ],
                "execution_mode": "sequential",
                "stop_on_error": True
            }
        }


class ParsedIntent(BaseModel):
    """Parsed intent from natural language command"""
    action: str = Field(..., description="実行アクション")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="抽出されたパラメータ")
    confidence: float = Field(..., ge=0, le=1, description="解析信頼度")


class ExecutionDetails(BaseModel):
    """Execution details"""
    backend_calls: List[Dict[str, Any]] = Field(default_factory=list, description="実行されたバックエンドAPI呼び出し")
    execution_time: float = Field(..., description="実行時間（秒）")


class CommandResponse(BaseModel):
    """Command response model"""
    success: bool = Field(..., description="実行成功フラグ")
    message: str = Field(..., description="実行結果メッセージ")
    parsed_intent: Optional[ParsedIntent] = Field(default=None, description="解析された意図")
    execution_details: Optional[ExecutionDetails] = Field(default=None, description="実行詳細")
    result: Optional[Dict[str, Any]] = Field(default=None, description="実行結果データ")
    timestamp: datetime = Field(default_factory=datetime.now, description="実行時刻")


class BatchCommandSummary(BaseModel):
    """Batch command execution summary"""
    total_commands: int = Field(..., description="総コマンド数")
    successful_commands: int = Field(..., description="成功コマンド数")
    failed_commands: int = Field(..., description="失敗コマンド数")
    total_execution_time: float = Field(..., description="総実行時間（秒）")


class BatchCommandResponse(BaseModel):
    """Batch command response model"""
    success: bool = Field(..., description="全体成功フラグ")
    message: str = Field(..., description="全体結果メッセージ")
    results: List[CommandResponse] = Field(..., description="各コマンドの実行結果")
    summary: BatchCommandSummary = Field(..., description="実行サマリー")
    timestamp: datetime = Field(default_factory=datetime.now, description="実行時刻")


class CommandError(BaseModel):
    """Command error model"""
    error: bool = Field(default=True, description="エラーフラグ")
    error_code: str = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(default=None, description="エラー詳細")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生時刻")
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "error_code": "PARSING_ERROR",
                "message": "コマンドの解析に失敗しました",
                "details": {
                    "parsing_error": "動詞が見つかりません",
                    "suggested_corrections": ["動詞を追加してください"],
                    "original_command": "ドローン上昇"
                },
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }