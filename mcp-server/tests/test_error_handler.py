"""
Error handler tests
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.core.error_handler import (
    ErrorSeverity,
    ErrorCategory,
    RecoveryAction,
    ErrorContext,
    ErrorHandler,
    error_handler
)
from mcp.types import ErrorCode, McpError

class TestErrorContext:
    """Test ErrorContext class"""
    
    def test_error_context_creation(self):
        """Test error context creation"""
        context = ErrorContext(
            error_id="TEST_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            user_message="Test error message",
            technical_message="Technical error details",
            recovery_actions=[RecoveryAction.RETRY],
            recovery_suggestions=["Try again"]
        )
        
        assert context.error_id == "TEST_ERROR"
        assert context.severity == ErrorSeverity.HIGH
        assert context.category == ErrorCategory.SECURITY
        assert context.user_message == "Test error message"
        assert context.technical_message == "Technical error details"
        assert context.recovery_actions == [RecoveryAction.RETRY]
        assert context.recovery_suggestions == ["Try again"]
        assert isinstance(context.timestamp, datetime)

class TestErrorHandler:
    """Test ErrorHandler class"""
    
    def test_get_error_context(self):
        """Test getting error context"""
        handler = ErrorHandler()
        context = handler.get_error_context("DRONE_CONNECTION_FAILED")
        
        assert context is not None
        assert context.error_id == "DRONE_CONNECTION_FAILED"
        assert context.severity == ErrorSeverity.HIGH
        assert context.category == ErrorCategory.NETWORK
    
    def test_get_error_context_unknown(self):
        """Test getting unknown error context"""
        handler = ErrorHandler()
        context = handler.get_error_context("UNKNOWN_ERROR_ID")
        
        assert context is None
    
    def test_register_error(self):
        """Test registering new error"""
        handler = ErrorHandler()
        custom_error = ErrorContext(
            error_id="CUSTOM_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.USER,
            user_message="Custom error",
            technical_message="Custom technical message",
            recovery_actions=[RecoveryAction.RETRY],
            recovery_suggestions=["Custom suggestion"]
        )
        
        handler.register_error(custom_error)
        retrieved = handler.get_error_context("CUSTOM_ERROR")
        
        assert retrieved is not None
        assert retrieved.error_id == "CUSTOM_ERROR"
        assert retrieved.user_message == "Custom error"
    
    def test_classify_error_security(self):
        """Test error classification for security errors"""
        handler = ErrorHandler()
        error = Exception("Security validation failed")
        
        context = handler._classify_error(error)
        
        assert context.error_id == "SECURITY_VIOLATION"
        assert context.category == ErrorCategory.SECURITY
    
    def test_classify_error_connection(self):
        """Test error classification for connection errors"""
        handler = ErrorHandler()
        error = Exception("Connection timeout occurred")
        
        context = handler._classify_error(error)
        
        assert context.error_id == "DRONE_CONNECTION_FAILED"
        assert context.category == ErrorCategory.NETWORK
    
    def test_classify_error_backend(self):
        """Test error classification for backend errors"""
        handler = ErrorHandler()
        error = Exception("Backend API error")
        
        context = handler._classify_error(error)
        
        assert context.error_id == "BACKEND_API_ERROR"
        assert context.category == ErrorCategory.NETWORK
    
    def test_classify_error_hardware(self):
        """Test error classification for hardware errors"""
        handler = ErrorHandler()
        error = Exception("Hardware device malfunction")
        
        context = handler._classify_error(error)
        
        assert context.error_id == "DRONE_HARDWARE_ERROR"
        assert context.category == ErrorCategory.HARDWARE
    
    def test_classify_error_unknown(self):
        """Test error classification for unknown errors"""
        handler = ErrorHandler()
        error = Exception("Some unknown error")
        
        context = handler._classify_error(error)
        
        assert context.error_id == "UNKNOWN_ERROR"
        assert context.category == ErrorCategory.SYSTEM
    
    @patch('src.core.error_handler.logger')
    def test_log_error(self, mock_logger):
        """Test error logging"""
        handler = ErrorHandler()
        error = Exception("Test error")
        context = handler.get_error_context("DRONE_CONNECTION_FAILED")
        test_context = {"test_key": "test_value"}
        
        handler._log_error(error, context, test_context)
        
        # Check that logger was called with appropriate level
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "High severity error occurred" in call_args[0][0]
        assert "error_id" in call_args[1]["extra"]
        assert call_args[1]["extra"]["error_id"] == "DRONE_CONNECTION_FAILED"
    
    @patch('src.core.error_handler.logger')
    def test_log_error_critical(self, mock_logger):
        """Test critical error logging"""
        handler = ErrorHandler()
        error = Exception("Critical test error")
        context = handler.get_error_context("SECURITY_VIOLATION")
        
        handler._log_error(error, context, {})
        
        # Check that logger was called with critical level
        mock_logger.critical.assert_called_once()
        call_args = mock_logger.critical.call_args
        assert "Critical error occurred" in call_args[0][0]
    
    def test_create_error_message(self):
        """Test error message creation"""
        handler = ErrorHandler()
        error = Exception("Test error")
        context = handler.get_error_context("DRONE_CONNECTION_FAILED")
        test_context = {"tool_name": "connect_drone", "drone_id": "test_drone"}
        
        message = handler._create_error_message(error, context, test_context)
        
        assert "❌ エラー: ドローンへの接続に失敗しました" in message
        assert "🔧 解決方法:" in message
        assert "ドローンの電源を確認してください" in message
        assert "📋 詳細情報:" in message
        assert "エラーID: DRONE_CONNECTION_FAILED" in message
        assert "ツール: connect_drone" in message
        assert "ドローンID: test_drone" in message
        assert "🔄 推奨アクション:" in message
        assert "操作を再試行してください" in message
    
    def test_create_error_message_no_context(self):
        """Test error message creation without context"""
        handler = ErrorHandler()
        error = Exception("Test error")
        context = handler.get_error_context("INVALID_DRONE_ID")
        
        message = handler._create_error_message(error, context, None)
        
        assert "❌ エラー: 無効なドローンIDです" in message
        assert "🔧 解決方法:" in message
        assert "📋 詳細情報:" not in message  # Should not have details without context
    
    def test_handle_error_with_error_id(self):
        """Test handling error with specific error ID"""
        handler = ErrorHandler()
        error = Exception("Test error")
        context = {"drone_id": "test_drone"}
        
        result = handler.handle_error(error, context, "DRONE_CONNECTION_FAILED")
        
        assert result.isError is True
        assert len(result.content) == 1
        assert "ドローンへの接続に失敗しました" in result.content[0].text
    
    def test_handle_error_without_error_id(self):
        """Test handling error without specific error ID"""
        handler = ErrorHandler()
        error = Exception("Connection failed")
        context = {"drone_id": "test_drone"}
        
        result = handler.handle_error(error, context)
        
        assert result.isError is True
        assert len(result.content) == 1
        # Should classify as connection error
        assert "ドローンへの接続に失敗しました" in result.content[0].text
    
    def test_create_mcp_error(self):
        """Test creating MCP error"""
        handler = ErrorHandler()
        error = Exception("Test error")
        context = {"drone_id": "test_drone"}
        
        mcp_error = handler.create_mcp_error(error, "SECURITY_VIOLATION", context)
        
        assert isinstance(mcp_error, McpError)
        assert mcp_error.code == ErrorCode.INVALID_REQUEST
        assert "セキュリティ違反が検出されました" in mcp_error.message
    
    def test_map_to_mcp_error_code(self):
        """Test mapping error categories to MCP error codes"""
        handler = ErrorHandler()
        
        # Test all category mappings
        assert handler._map_to_mcp_error_code(ErrorCategory.VALIDATION) == ErrorCode.INVALID_REQUEST
        assert handler._map_to_mcp_error_code(ErrorCategory.SECURITY) == ErrorCode.INVALID_REQUEST
        assert handler._map_to_mcp_error_code(ErrorCategory.NETWORK) == ErrorCode.INTERNAL_ERROR
        assert handler._map_to_mcp_error_code(ErrorCategory.HARDWARE) == ErrorCode.INTERNAL_ERROR
        assert handler._map_to_mcp_error_code(ErrorCategory.SYSTEM) == ErrorCode.INTERNAL_ERROR
        assert handler._map_to_mcp_error_code(ErrorCategory.USER) == ErrorCode.INVALID_REQUEST

class TestErrorHandlerIntegration:
    """Integration tests for error handler"""
    
    def test_predefined_errors_exist(self):
        """Test that all predefined errors exist"""
        handler = ErrorHandler()
        
        expected_errors = [
            "DRONE_CONNECTION_FAILED",
            "INVALID_DRONE_ID",
            "SECURITY_VIOLATION",
            "DRONE_HARDWARE_ERROR",
            "SYSTEM_OVERLOAD",
            "INVALID_COMMAND",
            "BACKEND_API_ERROR",
            "UNKNOWN_ERROR"
        ]
        
        for error_id in expected_errors:
            context = handler.get_error_context(error_id)
            assert context is not None, f"Error {error_id} not found"
            assert context.error_id == error_id
    
    def test_error_severity_levels(self):
        """Test error severity levels"""
        handler = ErrorHandler()
        
        # Test different severity levels
        critical_error = handler.get_error_context("SECURITY_VIOLATION")
        assert critical_error.severity == ErrorSeverity.CRITICAL
        
        high_error = handler.get_error_context("DRONE_CONNECTION_FAILED")
        assert high_error.severity == ErrorSeverity.HIGH
        
        medium_error = handler.get_error_context("INVALID_DRONE_ID")
        assert medium_error.severity == ErrorSeverity.MEDIUM
    
    def test_recovery_actions_exist(self):
        """Test that recovery actions exist for all errors"""
        handler = ErrorHandler()
        
        for error_id in handler.error_registry:
            context = handler.get_error_context(error_id)
            assert len(context.recovery_actions) > 0, f"No recovery actions for {error_id}"
            assert len(context.recovery_suggestions) > 0, f"No recovery suggestions for {error_id}"

if __name__ == "__main__":
    pytest.main([__file__])