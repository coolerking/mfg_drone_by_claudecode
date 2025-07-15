"""
Improved MCP Server tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListResourcesRequest,
    ReadResourceRequest,
    TextContent,
    McpError,
    ErrorCode
)

# Import the improved MCP server components
from src.mcp_main import (
    TOOLS,
    RESOURCES,
    list_tools,
    call_tool,
    list_resources,
    read_resource,
    _connect_drone,
    _takeoff_drone,
    _execute_natural_language_command,
    setup_secure_paths
)

class TestSecurePaths:
    """Test secure path setup"""
    
    def test_setup_secure_paths(self):
        """Test secure path setup function"""
        original_path = sys.path.copy()
        
        try:
            # Clear relevant paths
            sys.path = [p for p in sys.path if "mcp-server" not in p]
            
            setup_secure_paths()
            
            # Check that secure paths were added
            mcp_server_paths = [p for p in sys.path if "mcp-server" in p]
            assert len(mcp_server_paths) >= 3  # src, config, and current dir
            
        finally:
            # Restore original path
            sys.path = original_path

class TestMCPToolsAndResources:
    """Test MCP tools and resources definitions"""
    
    def test_tools_definition(self):
        """Test that all expected tools are defined"""
        expected_tools = [
            "connect_drone",
            "takeoff_drone",
            "land_drone",
            "move_drone",
            "rotate_drone",
            "take_photo",
            "execute_natural_language_command",
            "emergency_stop"
        ]
        
        tool_names = [tool.name for tool in TOOLS]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_resources_definition(self):
        """Test that all expected resources are defined"""
        expected_resources = [
            "drone://available",
            "drone://status",
            "system://status"
        ]
        
        resource_uris = [resource.uri for resource in RESOURCES]
        
        for expected_resource in expected_resources:
            assert expected_resource in resource_uris
    
    def test_tool_schemas_valid(self):
        """Test that tool schemas are valid"""
        for tool in TOOLS:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert "type" in tool.inputSchema
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema

class TestMCPServerHandlers:
    """Test MCP server handler functions"""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test list_tools handler"""
        request = ListToolsRequest()
        
        result = await list_tools(request)
        
        assert result == TOOLS
        assert len(result) == 8  # Expected number of tools
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test list_resources handler"""
        request = ListResourcesRequest()
        
        result = await list_resources(request)
        
        assert result.resources == RESOURCES
        assert len(result.resources) == 3  # Expected number of resources
    
    @pytest.mark.asyncio
    async def test_read_resource_invalid_uri(self):
        """Test read_resource with invalid URI"""
        request = ReadResourceRequest(uri="invalid://resource")
        
        with pytest.raises(McpError) as exc_info:
            await read_resource(request)
        
        assert exc_info.value.code == ErrorCode.INVALID_REQUEST
        assert "未知のリソース" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_read_resource_empty_uri(self):
        """Test read_resource with empty URI"""
        request = ReadResourceRequest(uri="")
        
        with pytest.raises(McpError) as exc_info:
            await read_resource(request)
        
        assert exc_info.value.code == ErrorCode.INVALID_REQUEST
        assert "無効なリソースURI" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_read_resource_too_long_uri(self):
        """Test read_resource with too long URI"""
        request = ReadResourceRequest(uri="a" * 201)
        
        with pytest.raises(McpError) as exc_info:
            await read_resource(request)
        
        assert exc_info.value.code == ErrorCode.INVALID_REQUEST
        assert "無効なリソースURI" in exc_info.value.message

class TestToolExecution:
    """Test tool execution with security enhancements"""
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling unknown tool"""
        request = CallToolRequest(name="unknown_tool", arguments={})
        
        with pytest.raises(McpError) as exc_info:
            await call_tool(request)
        
        assert exc_info.value.code == ErrorCode.METHOD_NOT_FOUND
        assert "未知のツール" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_call_tool_security_validation_error(self):
        """Test calling tool with security validation error"""
        request = CallToolRequest(
            name="connect_drone",
            arguments={"drone_id": "invalid@drone"}
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "セキュリティ違反が検出されました" in result.content[0].text
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.backend_client')
    async def test_call_tool_connect_drone_success(self, mock_backend_client):
        """Test successful drone connection"""
        mock_backend_client.connect_drone.return_value = AsyncMock()
        mock_backend_client.connect_drone.return_value.message = "Connected successfully"
        
        request = CallToolRequest(
            name="connect_drone",
            arguments={"drone_id": "test_drone"}
        )
        
        result = await call_tool(request)
        
        assert result.isError is not True
        assert "✅ ドローン test_drone に接続しました" in result.content[0].text
        mock_backend_client.connect_drone.assert_called_once_with("test_drone")
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.backend_client')
    async def test_call_tool_connect_drone_failure(self, mock_backend_client):
        """Test drone connection failure"""
        mock_backend_client.connect_drone.side_effect = Exception("Connection failed")
        
        request = CallToolRequest(
            name="connect_drone",
            arguments={"drone_id": "test_drone"}
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "ドローンへの接続に失敗しました" in result.content[0].text
        assert "🔧 解決方法:" in result.content[0].text
        assert "ドローンの電源を確認してください" in result.content[0].text
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.backend_client')
    async def test_call_tool_takeoff_drone_success(self, mock_backend_client):
        """Test successful drone takeoff"""
        mock_backend_client.takeoff_drone.return_value = AsyncMock()
        mock_backend_client.takeoff_drone.return_value.message = "Takeoff successful"
        
        request = CallToolRequest(
            name="takeoff_drone",
            arguments={"drone_id": "test_drone", "target_height": 2.0}
        )
        
        result = await call_tool(request)
        
        assert result.isError is not True
        assert "🛫 ドローン test_drone が離陸しました" in result.content[0].text
        assert "目標高度: 2.0m" in result.content[0].text
        mock_backend_client.takeoff_drone.assert_called_once_with("test_drone", 2.0)
    
    @pytest.mark.asyncio
    async def test_call_tool_move_drone_invalid_distance(self):
        """Test move_drone with invalid distance"""
        request = CallToolRequest(
            name="move_drone",
            arguments={
                "drone_id": "test_drone",
                "direction": "forward",
                "distance": 600  # Too large
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "セキュリティ違反が検出されました" in result.content[0].text
        assert "移動距離が無効です" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_rotate_drone_invalid_direction(self):
        """Test rotate_drone with invalid direction"""
        request = CallToolRequest(
            name="rotate_drone",
            arguments={
                "drone_id": "test_drone",
                "direction": "invalid_direction",
                "angle": 90
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "セキュリティ違反が検出されました" in result.content[0].text
        assert "無効な回転方向です" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_take_photo_invalid_quality(self):
        """Test take_photo with invalid quality"""
        request = CallToolRequest(
            name="take_photo",
            arguments={
                "drone_id": "test_drone",
                "quality": "invalid_quality"
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "セキュリティ違反が検出されました" in result.content[0].text
        assert "無効な画質設定です" in result.content[0].text

class TestNaturalLanguageCommand:
    """Test natural language command execution"""
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.nlp_engine')
    @patch('src.mcp_main.command_router')
    async def test_execute_natural_language_command_success(self, mock_command_router, mock_nlp_engine):
        """Test successful natural language command execution"""
        # Mock NLP engine
        mock_parsed_intent = MagicMock()
        mock_parsed_intent.confidence = 0.85
        mock_nlp_engine.parse_command.return_value = mock_parsed_intent
        
        # Mock command router
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = "Command executed successfully"
        mock_command_router.execute_command.return_value = mock_result
        
        request = CallToolRequest(
            name="execute_natural_language_command",
            arguments={
                "drone_id": "test_drone",
                "command": "前に進んで"
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is not True
        assert "🤖 自然言語コマンドを実行しました" in result.content[0].text
        assert "📝 コマンド: 前に進んで" in result.content[0].text
        assert "🎯 ドローン: test_drone" in result.content[0].text
        assert "📊 信頼度: 0.85" in result.content[0].text
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.nlp_engine')
    @patch('src.mcp_main.settings')
    async def test_execute_natural_language_command_low_confidence(self, mock_settings, mock_nlp_engine):
        """Test natural language command with low confidence"""
        # Mock settings
        mock_settings.nlp_confidence_threshold = 0.7
        
        # Mock NLP engine with low confidence
        mock_parsed_intent = MagicMock()
        mock_parsed_intent.confidence = 0.5
        mock_nlp_engine.parse_command.return_value = mock_parsed_intent
        
        request = CallToolRequest(
            name="execute_natural_language_command",
            arguments={
                "drone_id": "test_drone",
                "command": "あいまいなコマンド"
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "コマンドの解析に失敗しました" in result.content[0].text
        assert "🔧 解決方法:" in result.content[0].text
        assert "コマンドを言い換えてください" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_execute_natural_language_command_dangerous_pattern(self):
        """Test natural language command with dangerous pattern"""
        request = CallToolRequest(
            name="execute_natural_language_command",
            arguments={
                "drone_id": "test_drone",
                "command": "<script>alert('xss')</script>"
            }
        )
        
        result = await call_tool(request)
        
        assert result.isError is True
        assert "セキュリティ違反が検出されました" in result.content[0].text
        assert "危険なパターンが検出されました" in result.content[0].text

class TestToolImplementations:
    """Test individual tool implementations"""
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.backend_client')
    async def test_connect_drone_with_progress(self, mock_backend_client):
        """Test connect_drone with progress indicator"""
        mock_backend_client.connect_drone.return_value = AsyncMock()
        mock_backend_client.connect_drone.return_value.message = "Connected"
        
        result = await _connect_drone({"drone_id": "test_drone"})
        
        assert result.isError is not True
        assert "✅ ドローン test_drone に接続しました" in result.content[0].text
        mock_backend_client.connect_drone.assert_called_once_with("test_drone")
    
    @pytest.mark.asyncio
    @patch('src.mcp_main.backend_client')
    async def test_takeoff_drone_with_progress(self, mock_backend_client):
        """Test takeoff_drone with progress indicator"""
        mock_backend_client.takeoff_drone.return_value = AsyncMock()
        mock_backend_client.takeoff_drone.return_value.message = "Takeoff successful"
        
        result = await _takeoff_drone({"drone_id": "test_drone", "target_height": 1.5})
        
        assert result.isError is not True
        assert "🛫 ドローン test_drone が離陸しました" in result.content[0].text
        assert "目標高度: 1.5m" in result.content[0].text
        mock_backend_client.takeoff_drone.assert_called_once_with("test_drone", 1.5)

class TestErrorHandling:
    """Test enhanced error handling"""
    
    @pytest.mark.asyncio
    async def test_tool_execution_error_context(self):
        """Test that tool execution errors include context"""
        request = CallToolRequest(
            name="connect_drone",
            arguments={"drone_id": "test_drone"}
        )
        
        with patch('src.mcp_main.backend_client') as mock_backend_client:
            mock_backend_client.connect_drone.side_effect = Exception("Connection timeout")
            
            result = await call_tool(request)
            
            assert result.isError is True
            assert "ドローンへの接続に失敗しました" in result.content[0].text
            assert "📋 詳細情報:" in result.content[0].text
            assert "ツール: connect_drone" in result.content[0].text
            assert "ドローンID: test_drone" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_resource_read_error_context(self):
        """Test that resource read errors include context"""
        request = ReadResourceRequest(uri="drone://available")
        
        with patch('src.mcp_main._get_available_drones') as mock_get_drones:
            mock_get_drones.side_effect = Exception("Backend error")
            
            with pytest.raises(McpError) as exc_info:
                await read_resource(request)
            
            assert exc_info.value.code == ErrorCode.INTERNAL_ERROR
            # The error should be handled by the enhanced error handler

class TestSecurityEnhancements:
    """Test security enhancements"""
    
    @pytest.mark.asyncio
    async def test_argument_validation_prevents_injection(self):
        """Test that argument validation prevents injection attacks"""
        malicious_inputs = [
            {"drone_id": "'; DROP TABLE drones; --"},
            {"drone_id": "../../../etc/passwd"},
            {"drone_id": "drone<script>alert('xss')</script>"}
        ]
        
        for malicious_input in malicious_inputs:
            request = CallToolRequest(
                name="connect_drone",
                arguments=malicious_input
            )
            
            result = await call_tool(request)
            
            assert result.isError is True
            assert "セキュリティ違反が検出されました" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_filename_validation_prevents_path_traversal(self):
        """Test that filename validation prevents path traversal"""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "file<script>alert('xss')</script>.jpg"
        ]
        
        for malicious_filename in malicious_filenames:
            request = CallToolRequest(
                name="take_photo",
                arguments={
                    "drone_id": "test_drone",
                    "filename": malicious_filename
                }
            )
            
            result = await call_tool(request)
            
            assert result.isError is True
            assert "セキュリティ違反が検出されました" in result.content[0].text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])