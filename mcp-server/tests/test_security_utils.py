"""
Security utilities tests
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.security_utils import (
    SecurityError,
    PathValidator,
    InputValidator,
    DataSanitizer,
    SecurityValidator,
    security_validator
)

class TestPathValidator:
    """Test PathValidator class"""
    
    def test_validate_path_valid(self):
        """Test valid path validation"""
        path = Path("test/file.txt")
        result = PathValidator.validate_path(path)
        assert result == path
    
    def test_validate_path_empty(self):
        """Test empty path validation"""
        with pytest.raises(SecurityError, match="パスが空です"):
            PathValidator.validate_path("")
    
    def test_validate_path_traversal(self):
        """Test path traversal detection"""
        with pytest.raises(SecurityError, match="パス トラバーサル攻撃が検出されました"):
            PathValidator.validate_path("../../../etc/passwd")
    
    def test_validate_path_invalid_extension(self):
        """Test invalid file extension"""
        with pytest.raises(SecurityError, match="許可されていないファイル拡張子です"):
            PathValidator.validate_path("test.exe", allowed_extensions=[".txt", ".py"])
    
    def test_safe_join_valid(self):
        """Test safe path joining"""
        result = PathValidator.safe_join("base", "sub", "file.txt")
        assert result == Path("base/sub/file.txt")
    
    def test_safe_join_invalid_part(self):
        """Test safe path joining with invalid part"""
        with pytest.raises(SecurityError, match="不正なパス コンポーネント"):
            PathValidator.safe_join("base", "../evil", "file.txt")

class TestInputValidator:
    """Test InputValidator class"""
    
    def test_validate_drone_id_valid(self):
        """Test valid drone ID validation"""
        valid_ids = ["drone1", "drone-2", "drone_3", "DroNe123"]
        for drone_id in valid_ids:
            result = InputValidator.validate_drone_id(drone_id)
            assert result == drone_id
    
    def test_validate_drone_id_empty(self):
        """Test empty drone ID validation"""
        with pytest.raises(SecurityError, match="ドローンIDが空です"):
            InputValidator.validate_drone_id("")
    
    def test_validate_drone_id_invalid_format(self):
        """Test invalid drone ID format"""
        with pytest.raises(SecurityError, match="無効なドローンID形式です"):
            InputValidator.validate_drone_id("drone@123")
    
    def test_validate_drone_id_too_long(self):
        """Test drone ID too long"""
        with pytest.raises(SecurityError, match="ドローンIDが長すぎます"):
            InputValidator.validate_drone_id("a" * 51)
    
    def test_validate_filename_valid(self):
        """Test valid filename validation"""
        valid_names = ["test.txt", "file-2.py", "data_file.json"]
        for filename in valid_names:
            result = InputValidator.validate_filename(filename)
            assert result == filename
    
    def test_validate_filename_empty(self):
        """Test empty filename validation"""
        with pytest.raises(SecurityError, match="ファイル名が空です"):
            InputValidator.validate_filename("")
    
    def test_validate_filename_invalid_chars(self):
        """Test filename with invalid characters"""
        with pytest.raises(SecurityError, match="ファイル名に無効な文字が含まれています"):
            InputValidator.validate_filename("file<>.txt")
    
    def test_validate_filename_reserved_name(self):
        """Test reserved filename"""
        with pytest.raises(SecurityError, match="予約されたファイル名です"):
            InputValidator.validate_filename("CON")
    
    def test_validate_filename_too_long(self):
        """Test filename too long"""
        with pytest.raises(SecurityError, match="ファイル名が長すぎます"):
            InputValidator.validate_filename("a" * 256)
    
    def test_validate_command_string_valid(self):
        """Test valid command string validation"""
        command = "ドローンを前に進めて"
        result = InputValidator.validate_command_string(command)
        assert result == command
    
    def test_validate_command_string_empty(self):
        """Test empty command string validation"""
        with pytest.raises(SecurityError, match="コマンドが空です"):
            InputValidator.validate_command_string("")
    
    def test_validate_command_string_too_long(self):
        """Test command string too long"""
        with pytest.raises(SecurityError, match="コマンドが長すぎます"):
            InputValidator.validate_command_string("a" * 1001)
    
    def test_validate_command_string_dangerous_pattern(self):
        """Test command string with dangerous patterns"""
        dangerous_commands = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "eval(malicious_code)",
            "exec(dangerous_code)"
        ]
        for command in dangerous_commands:
            with pytest.raises(SecurityError, match="危険なパターンが検出されました"):
                InputValidator.validate_command_string(command)
    
    def test_validate_json_schema_valid(self):
        """Test valid JSON schema validation"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        data = {"name": "test", "age": 25}
        # Should not raise an exception
        InputValidator.validate_json_schema(data, schema)
    
    def test_validate_json_schema_invalid(self):
        """Test invalid JSON schema validation"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        data = {"age": 25}  # Missing required field
        with pytest.raises(SecurityError, match="スキーマ検証エラー"):
            InputValidator.validate_json_schema(data, schema)

class TestDataSanitizer:
    """Test DataSanitizer class"""
    
    def test_sanitize_output_dict(self):
        """Test dictionary sanitization"""
        data = {
            "username": "test_user",
            "password": "secret123",
            "api_key": "key123",
            "data": "normal_data"
        }
        result = DataSanitizer.sanitize_output(data)
        assert result["username"] == "test_user"
        assert result["password"] == "***"
        assert result["api_key"] == "***"
        assert result["data"] == "normal_data"
    
    def test_sanitize_output_list(self):
        """Test list sanitization"""
        data = [
            {"password": "secret1"},
            {"data": "normal1"},
            {"secret": "secret2"}
        ]
        result = DataSanitizer.sanitize_output(data)
        assert result[0]["password"] == "***"
        assert result[1]["data"] == "normal1"
        assert result[2]["secret"] == "***"
    
    def test_sanitize_output_string(self):
        """Test string sanitization"""
        data = "Normal text with <script>alert('xss')</script> tags"
        result = DataSanitizer.sanitize_output(data)
        assert "<script>" not in result
        assert "alert('xss')" not in result
        assert "Normal text with" in result
    
    def test_sanitize_output_primitive(self):
        """Test primitive type sanitization"""
        assert DataSanitizer.sanitize_output(123) == 123
        assert DataSanitizer.sanitize_output(True) is True
        assert DataSanitizer.sanitize_output(None) is None

class TestSecurityValidator:
    """Test SecurityValidator class"""
    
    def test_validate_tool_arguments_connect_drone(self):
        """Test connect_drone argument validation"""
        args = {"drone_id": "test_drone"}
        result = security_validator.validate_tool_arguments("connect_drone", args)
        assert result["drone_id"] == "test_drone"
    
    def test_validate_tool_arguments_invalid_drone_id(self):
        """Test invalid drone ID in arguments"""
        args = {"drone_id": "invalid@drone"}
        with pytest.raises(SecurityError, match="無効なドローンID形式です"):
            security_validator.validate_tool_arguments("connect_drone", args)
    
    def test_validate_tool_arguments_move_drone(self):
        """Test move_drone argument validation"""
        args = {
            "drone_id": "test_drone",
            "direction": "forward",
            "distance": 100,
            "speed": 50
        }
        result = security_validator.validate_tool_arguments("move_drone", args)
        assert result["drone_id"] == "test_drone"
        assert result["direction"] == "forward"
        assert result["distance"] == 100
        assert result["speed"] == 50
    
    def test_validate_tool_arguments_move_drone_invalid_distance(self):
        """Test move_drone with invalid distance"""
        args = {
            "drone_id": "test_drone",
            "direction": "forward",
            "distance": 600  # Too large
        }
        with pytest.raises(SecurityError, match="移動距離が無効です"):
            security_validator.validate_tool_arguments("move_drone", args)
    
    def test_validate_tool_arguments_move_drone_invalid_direction(self):
        """Test move_drone with invalid direction"""
        args = {
            "drone_id": "test_drone",
            "direction": "invalid_direction",
            "distance": 100
        }
        with pytest.raises(SecurityError, match="無効な方向です"):
            security_validator.validate_tool_arguments("move_drone", args)
    
    def test_validate_tool_arguments_rotate_drone(self):
        """Test rotate_drone argument validation"""
        args = {
            "drone_id": "test_drone",
            "direction": "clockwise",
            "angle": 90
        }
        result = security_validator.validate_tool_arguments("rotate_drone", args)
        assert result["drone_id"] == "test_drone"
        assert result["direction"] == "clockwise"
        assert result["angle"] == 90
    
    def test_validate_tool_arguments_rotate_drone_invalid_angle(self):
        """Test rotate_drone with invalid angle"""
        args = {
            "drone_id": "test_drone",
            "direction": "clockwise",
            "angle": 400  # Too large
        }
        with pytest.raises(SecurityError, match="回転角度が無効です"):
            security_validator.validate_tool_arguments("rotate_drone", args)
    
    def test_validate_tool_arguments_takeoff_drone(self):
        """Test takeoff_drone argument validation"""
        args = {
            "drone_id": "test_drone",
            "target_height": 2.0
        }
        result = security_validator.validate_tool_arguments("takeoff_drone", args)
        assert result["drone_id"] == "test_drone"
        assert result["target_height"] == 2.0
    
    def test_validate_tool_arguments_takeoff_drone_invalid_height(self):
        """Test takeoff_drone with invalid height"""
        args = {
            "drone_id": "test_drone",
            "target_height": 15.0  # Too high
        }
        with pytest.raises(SecurityError, match="目標高度が無効です"):
            security_validator.validate_tool_arguments("takeoff_drone", args)
    
    def test_validate_tool_arguments_take_photo(self):
        """Test take_photo argument validation"""
        args = {
            "drone_id": "test_drone",
            "filename": "test.jpg",
            "quality": "high"
        }
        result = security_validator.validate_tool_arguments("take_photo", args)
        assert result["drone_id"] == "test_drone"
        assert result["filename"] == "test.jpg"
        assert result["quality"] == "high"
    
    def test_validate_tool_arguments_take_photo_invalid_quality(self):
        """Test take_photo with invalid quality"""
        args = {
            "drone_id": "test_drone",
            "quality": "invalid_quality"
        }
        with pytest.raises(SecurityError, match="無効な画質設定です"):
            security_validator.validate_tool_arguments("take_photo", args)
    
    def test_validate_tool_arguments_natural_language_command(self):
        """Test natural language command argument validation"""
        args = {
            "drone_id": "test_drone",
            "command": "前に進んで"
        }
        result = security_validator.validate_tool_arguments("execute_natural_language_command", args)
        assert result["drone_id"] == "test_drone"
        assert result["command"] == "前に進んで"

if __name__ == "__main__":
    pytest.main([__file__])