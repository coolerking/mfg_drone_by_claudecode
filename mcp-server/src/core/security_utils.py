"""
Security utilities for MCP Server
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jsonschema import validate, ValidationError
from jsonschema.validators import Draft7Validator

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Security-related error"""
    pass

class PathValidator:
    """Path validation and sanitization utilities"""
    
    @staticmethod
    def validate_path(path: Union[str, Path], allowed_extensions: Optional[List[str]] = None) -> Path:
        """
        Validate and sanitize file paths
        
        Args:
            path: Path to validate
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated Path object
            
        Raises:
            SecurityError: If path is invalid or unsafe
        """
        if not path:
            raise SecurityError("パスが空です")
            
        # Convert to Path object
        path_obj = Path(path)
        
        # Check for path traversal attempts
        if ".." in path_obj.parts:
            raise SecurityError("パス トラバーサル攻撃が検出されました")
            
        # Check for absolute paths that go outside allowed directories
        if path_obj.is_absolute():
            # Only allow paths within the project directory
            project_root = Path(__file__).parent.parent.parent
            try:
                path_obj.resolve().relative_to(project_root.resolve())
            except ValueError:
                raise SecurityError("許可されていないディレクトリへのアクセスです")
        
        # Check file extensions if specified
        if allowed_extensions and path_obj.suffix.lower() not in allowed_extensions:
            raise SecurityError(f"許可されていないファイル拡張子です: {path_obj.suffix}")
            
        return path_obj
    
    @staticmethod
    def safe_join(base: Union[str, Path], *parts: str) -> Path:
        """
        Safely join path components
        
        Args:
            base: Base path
            *parts: Path components to join
            
        Returns:
            Safely joined path
            
        Raises:
            SecurityError: If resulting path is unsafe
        """
        base_path = Path(base)
        
        # Join all parts
        for part in parts:
            if not part:
                continue
                
            # Check for path traversal in each part
            if ".." in part or part.startswith("/"):
                raise SecurityError(f"不正なパス コンポーネント: {part}")
                
            base_path = base_path / part
        
        return PathValidator.validate_path(base_path)

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_drone_id(drone_id: str) -> str:
        """
        Validate drone ID format
        
        Args:
            drone_id: Drone ID to validate
            
        Returns:
            Validated drone ID
            
        Raises:
            SecurityError: If drone ID is invalid
        """
        if not drone_id:
            raise SecurityError("ドローンIDが空です")
            
        # Allow alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', drone_id):
            raise SecurityError("無効なドローンID形式です")
            
        if len(drone_id) > 50:
            raise SecurityError("ドローンIDが長すぎます")
            
        return drone_id
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate filename format
        
        Args:
            filename: Filename to validate
            
        Returns:
            Validated filename
            
        Raises:
            SecurityError: If filename is invalid
        """
        if not filename:
            raise SecurityError("ファイル名が空です")
            
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in filename for char in invalid_chars):
            raise SecurityError("ファイル名に無効な文字が含まれています")
            
        # Check for reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
            'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
            'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        if filename.upper() in reserved_names:
            raise SecurityError("予約されたファイル名です")
            
        if len(filename) > 255:
            raise SecurityError("ファイル名が長すぎます")
            
        return filename
    
    @staticmethod
    def validate_json_schema(data: Any, schema: Dict[str, Any]) -> None:
        """
        Validate data against JSON schema
        
        Args:
            data: Data to validate
            schema: JSON schema
            
        Raises:
            SecurityError: If validation fails
        """
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise SecurityError(f"スキーマ検証エラー: {e.message}")
    
    @staticmethod
    def validate_command_string(command: str) -> str:
        """
        Validate natural language command string
        
        Args:
            command: Command string to validate
            
        Returns:
            Validated command string
            
        Raises:
            SecurityError: If command is invalid
        """
        if not command:
            raise SecurityError("コマンドが空です")
            
        if len(command) > 1000:
            raise SecurityError("コマンドが長すぎます")
            
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript URLs
            r'data:',          # Data URLs
            r'eval\s*\(',      # eval() calls
            r'exec\s*\(',      # exec() calls
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError("危険なパターンが検出されました")
                
        return command.strip()

class DataSanitizer:
    """Data sanitization utilities"""
    
    @staticmethod
    def sanitize_output(data: Any) -> Any:
        """
        Sanitize output data to prevent information disclosure
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Remove sensitive keys
                if key.lower() in ['password', 'secret', 'token', 'key', 'api_key']:
                    sanitized[key] = '***'
                else:
                    sanitized[key] = DataSanitizer.sanitize_output(value)
            return sanitized
        elif isinstance(data, list):
            return [DataSanitizer.sanitize_output(item) for item in data]
        elif isinstance(data, str):
            # Remove potential XSS patterns
            sanitized = re.sub(r'<[^>]*>', '', data)
            return sanitized
        else:
            return data

class SecurityValidator:
    """Main security validation class"""
    
    def __init__(self):
        self.path_validator = PathValidator()
        self.input_validator = InputValidator()
        self.data_sanitizer = DataSanitizer()
    
    def validate_tool_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool arguments with security checks
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Validated arguments
            
        Raises:
            SecurityError: If validation fails
        """
        validated_args = {}
        
        try:
            # Common validations
            if 'drone_id' in arguments:
                validated_args['drone_id'] = self.input_validator.validate_drone_id(arguments['drone_id'])
            
            if 'filename' in arguments:
                validated_args['filename'] = self.input_validator.validate_filename(arguments['filename'])
            
            if 'command' in arguments:
                validated_args['command'] = self.input_validator.validate_command_string(arguments['command'])
            
            # Tool-specific validations
            if tool_name == 'move_drone':
                distance = arguments.get('distance', 0)
                if not isinstance(distance, (int, float)) or distance < 1 or distance > 500:
                    raise SecurityError("移動距離が無効です (1-500cm)")
                validated_args['distance'] = distance
                
                speed = arguments.get('speed', 20)
                if not isinstance(speed, (int, float)) or speed < 10 or speed > 100:
                    raise SecurityError("速度が無効です (10-100cm/s)")
                validated_args['speed'] = speed
                
                direction = arguments.get('direction', '')
                valid_directions = ['forward', 'backward', 'left', 'right', 'up', 'down']
                if direction not in valid_directions:
                    raise SecurityError(f"無効な方向です: {direction}")
                validated_args['direction'] = direction
            
            elif tool_name == 'rotate_drone':
                angle = arguments.get('angle', 0)
                if not isinstance(angle, (int, float)) or angle < 1 or angle > 360:
                    raise SecurityError("回転角度が無効です (1-360度)")
                validated_args['angle'] = angle
                
                direction = arguments.get('direction', '')
                valid_directions = ['clockwise', 'counter_clockwise']
                if direction not in valid_directions:
                    raise SecurityError(f"無効な回転方向です: {direction}")
                validated_args['direction'] = direction
            
            elif tool_name == 'takeoff_drone':
                target_height = arguments.get('target_height', 1.0)
                if not isinstance(target_height, (int, float)) or target_height < 0.1 or target_height > 10.0:
                    raise SecurityError("目標高度が無効です (0.1-10.0m)")
                validated_args['target_height'] = target_height
            
            elif tool_name == 'take_photo':
                quality = arguments.get('quality', 'high')
                valid_qualities = ['low', 'medium', 'high']
                if quality not in valid_qualities:
                    raise SecurityError(f"無効な画質設定です: {quality}")
                validated_args['quality'] = quality
            
            # Copy other arguments that passed validation
            for key, value in arguments.items():
                if key not in validated_args:
                    validated_args[key] = value
                    
        except Exception as e:
            logger.error(f"引数検証エラー: {e}")
            raise SecurityError(f"引数検証エラー: {e}")
        
        return validated_args

# Global security validator instance
security_validator = SecurityValidator()