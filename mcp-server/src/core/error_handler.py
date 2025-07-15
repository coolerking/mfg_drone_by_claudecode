"""
Enhanced error handling utilities for MCP Server
"""

import logging
import traceback
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from datetime import datetime
from mcp.types import ErrorCode, McpError, TextContent, CallToolResult

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    VALIDATION = "validation"
    SECURITY = "security"
    NETWORK = "network"
    HARDWARE = "hardware"
    SYSTEM = "system"
    USER = "user"

class RecoveryAction(Enum):
    """Recovery action types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    MANUAL_INTERVENTION = "manual_intervention"
    RESTART = "restart"
    NONE = "none"

class ErrorContext:
    """Error context information"""
    
    def __init__(
        self,
        error_id: str,
        severity: ErrorSeverity,
        category: ErrorCategory,
        user_message: str,
        technical_message: str,
        recovery_actions: List[RecoveryAction],
        recovery_suggestions: List[str],
        error_data: Optional[Dict[str, Any]] = None
    ):
        self.error_id = error_id
        self.severity = severity
        self.category = category
        self.user_message = user_message
        self.technical_message = technical_message
        self.recovery_actions = recovery_actions
        self.recovery_suggestions = recovery_suggestions
        self.error_data = error_data or {}
        self.timestamp = datetime.now()
        self.stack_trace = traceback.format_exc()

class ErrorHandler:
    """Enhanced error handling and recovery system"""
    
    def __init__(self):
        self.error_registry = self._initialize_error_registry()
    
    def _initialize_error_registry(self) -> Dict[str, ErrorContext]:
        """Initialize error registry with predefined errors"""
        return {
            # Connection errors
            "DRONE_CONNECTION_FAILED": ErrorContext(
                error_id="DRONE_CONNECTION_FAILED",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.NETWORK,
                user_message="ドローンへの接続に失敗しました",
                technical_message="Drone connection timeout or network error",
                recovery_actions=[RecoveryAction.RETRY, RecoveryAction.FALLBACK],
                recovery_suggestions=[
                    "ドローンの電源を確認してください",
                    "Wi-Fi接続を確認してください",
                    "シミュレーションモードを試してください",
                    "ドローンを再起動してください"
                ]
            ),
            
            # Validation errors
            "INVALID_DRONE_ID": ErrorContext(
                error_id="INVALID_DRONE_ID",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.VALIDATION,
                user_message="無効なドローンIDです",
                technical_message="Drone ID format validation failed",
                recovery_actions=[RecoveryAction.RETRY],
                recovery_suggestions=[
                    "ドローンIDは英数字、ハイフン、アンダースコアのみ使用可能です",
                    "ドローンIDは50文字以内にしてください",
                    "利用可能なドローンIDを確認してください"
                ]
            ),
            
            # Security errors
            "SECURITY_VIOLATION": ErrorContext(
                error_id="SECURITY_VIOLATION",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.SECURITY,
                user_message="セキュリティ違反が検出されました",
                technical_message="Security validation failed",
                recovery_actions=[RecoveryAction.MANUAL_INTERVENTION],
                recovery_suggestions=[
                    "入力内容を確認してください",
                    "危険なパターンが含まれていないか確認してください",
                    "管理者に連絡してください"
                ]
            ),
            
            # Hardware errors
            "DRONE_HARDWARE_ERROR": ErrorContext(
                error_id="DRONE_HARDWARE_ERROR",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.HARDWARE,
                user_message="ドローンのハードウェアエラーが発生しました",
                technical_message="Drone hardware malfunction detected",
                recovery_actions=[RecoveryAction.MANUAL_INTERVENTION, RecoveryAction.RESTART],
                recovery_suggestions=[
                    "ドローンの電源を入れ直してください",
                    "プロペラの状態を確認してください",
                    "バッテリーの状態を確認してください",
                    "安全な場所に移動してください"
                ]
            ),
            
            # System errors
            "SYSTEM_OVERLOAD": ErrorContext(
                error_id="SYSTEM_OVERLOAD",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                user_message="システムが過負荷状態です",
                technical_message="System resource utilization exceeded limits",
                recovery_actions=[RecoveryAction.FALLBACK, RecoveryAction.RESTART],
                recovery_suggestions=[
                    "しばらく待ってから再試行してください",
                    "同時実行数を減らしてください",
                    "システムを再起動してください"
                ]
            ),
            
            # User errors
            "INVALID_COMMAND": ErrorContext(
                error_id="INVALID_COMMAND",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.USER,
                user_message="コマンドの解析に失敗しました",
                technical_message="Natural language command parsing failed",
                recovery_actions=[RecoveryAction.RETRY],
                recovery_suggestions=[
                    "コマンドを言い換えてください",
                    "より具体的な指示を入力してください",
                    "サポートされているコマンドを確認してください"
                ]
            ),
            
            # Backend errors
            "BACKEND_API_ERROR": ErrorContext(
                error_id="BACKEND_API_ERROR",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.NETWORK,
                user_message="バックエンドAPIエラーが発生しました",
                technical_message="Backend API request failed",
                recovery_actions=[RecoveryAction.RETRY, RecoveryAction.FALLBACK],
                recovery_suggestions=[
                    "しばらく待ってから再試行してください",
                    "バックエンドサーバーの状態を確認してください",
                    "管理者に連絡してください"
                ]
            ),
            
            # Generic errors
            "UNKNOWN_ERROR": ErrorContext(
                error_id="UNKNOWN_ERROR",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.SYSTEM,
                user_message="予期しないエラーが発生しました",
                technical_message="Unknown error occurred",
                recovery_actions=[RecoveryAction.RETRY, RecoveryAction.MANUAL_INTERVENTION],
                recovery_suggestions=[
                    "操作を再試行してください",
                    "システムログを確認してください",
                    "管理者に連絡してください"
                ]
            )
        }
    
    def get_error_context(self, error_id: str) -> Optional[ErrorContext]:
        """Get error context by error ID"""
        return self.error_registry.get(error_id)
    
    def register_error(self, error_context: ErrorContext) -> None:
        """Register a new error type"""
        self.error_registry[error_context.error_id] = error_context
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        error_id: Optional[str] = None
    ) -> CallToolResult:
        """
        Handle error with enhanced error information and recovery suggestions
        
        Args:
            error: The exception that occurred
            context: Additional context information
            error_id: Specific error ID to use
            
        Returns:
            CallToolResult with error information and recovery suggestions
        """
        # Determine error ID
        if error_id:
            error_context = self.get_error_context(error_id)
        else:
            error_context = self._classify_error(error)
        
        if not error_context:
            error_context = self.get_error_context("UNKNOWN_ERROR")
        
        # Log error
        self._log_error(error, error_context, context)
        
        # Create user-friendly error message
        error_message = self._create_error_message(error, error_context, context)
        
        # Return CallToolResult with error information
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=error_message
                )
            ],
            isError=True
        )
    
    def _classify_error(self, error: Exception) -> ErrorContext:
        """Classify error based on exception type and message"""
        error_str = str(error).lower()
        
        # Security errors
        if "security" in error_str or "validation" in error_str:
            return self.get_error_context("SECURITY_VIOLATION")
        
        # Connection errors
        if "connection" in error_str or "timeout" in error_str:
            return self.get_error_context("DRONE_CONNECTION_FAILED")
        
        # Backend API errors
        if "backend" in error_str or "api" in error_str:
            return self.get_error_context("BACKEND_API_ERROR")
        
        # Hardware errors
        if "hardware" in error_str or "device" in error_str:
            return self.get_error_context("DRONE_HARDWARE_ERROR")
        
        # Default to unknown error
        return self.get_error_context("UNKNOWN_ERROR")
    
    def _log_error(
        self,
        error: Exception,
        error_context: ErrorContext,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error with structured information"""
        log_data = {
            "error_id": error_context.error_id,
            "severity": error_context.severity.value,
            "category": error_context.category.value,
            "user_message": error_context.user_message,
            "technical_message": error_context.technical_message,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": error_context.timestamp.isoformat(),
            "context": context or {},
            "stack_trace": error_context.stack_trace
        }
        
        # Log with appropriate level based on severity
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical("Critical error occurred", extra=log_data)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error("High severity error occurred", extra=log_data)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning("Medium severity error occurred", extra=log_data)
        else:
            logger.info("Low severity error occurred", extra=log_data)
    
    def _create_error_message(
        self,
        error: Exception,
        error_context: ErrorContext,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create user-friendly error message with recovery suggestions"""
        message_parts = [
            f"❌ エラー: {error_context.user_message}",
            f"",
            f"🔧 解決方法:",
        ]
        
        # Add recovery suggestions
        for i, suggestion in enumerate(error_context.recovery_suggestions, 1):
            message_parts.append(f"  {i}. {suggestion}")
        
        # Add context information if available
        if context:
            message_parts.extend([
                f"",
                f"📋 詳細情報:",
                f"  • エラーID: {error_context.error_id}",
                f"  • カテゴリ: {error_context.category.value}",
                f"  • 発生時刻: {error_context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ])
            
            if context.get("tool_name"):
                message_parts.append(f"  • ツール: {context['tool_name']}")
            
            if context.get("drone_id"):
                message_parts.append(f"  • ドローンID: {context['drone_id']}")
        
        # Add recovery actions
        if error_context.recovery_actions:
            message_parts.extend([
                f"",
                f"🔄 推奨アクション:",
            ])
            
            for action in error_context.recovery_actions:
                if action == RecoveryAction.RETRY:
                    message_parts.append("  • 操作を再試行してください")
                elif action == RecoveryAction.FALLBACK:
                    message_parts.append("  • 代替方法を試してください")
                elif action == RecoveryAction.MANUAL_INTERVENTION:
                    message_parts.append("  • 手動での対処が必要です")
                elif action == RecoveryAction.RESTART:
                    message_parts.append("  • システムの再起動を検討してください")
        
        return "\n".join(message_parts)
    
    def create_mcp_error(
        self,
        error: Exception,
        error_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> McpError:
        """
        Create MCP error with enhanced error information
        
        Args:
            error: The exception that occurred
            error_id: Specific error ID to use
            context: Additional context information
            
        Returns:
            McpError with detailed error information
        """
        # Determine error ID
        if error_id:
            error_context = self.get_error_context(error_id)
        else:
            error_context = self._classify_error(error)
        
        if not error_context:
            error_context = self.get_error_context("UNKNOWN_ERROR")
        
        # Log error
        self._log_error(error, error_context, context)
        
        # Map error category to MCP error code
        error_code = self._map_to_mcp_error_code(error_context.category)
        
        # Create error message
        error_message = self._create_error_message(error, error_context, context)
        
        return McpError(
            code=error_code,
            message=error_message
        )
    
    def _map_to_mcp_error_code(self, category: ErrorCategory) -> ErrorCode:
        """Map error category to MCP error code"""
        mapping = {
            ErrorCategory.VALIDATION: ErrorCode.INVALID_REQUEST,
            ErrorCategory.SECURITY: ErrorCode.INVALID_REQUEST,
            ErrorCategory.NETWORK: ErrorCode.INTERNAL_ERROR,
            ErrorCategory.HARDWARE: ErrorCode.INTERNAL_ERROR,
            ErrorCategory.SYSTEM: ErrorCode.INTERNAL_ERROR,
            ErrorCategory.USER: ErrorCode.INVALID_REQUEST
        }
        return mapping.get(category, ErrorCode.INTERNAL_ERROR)

# Global error handler instance
error_handler = ErrorHandler()