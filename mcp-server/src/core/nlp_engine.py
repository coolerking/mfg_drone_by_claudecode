"""
Natural Language Processing Engine for MCP Server
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..models.command_models import ParsedIntent
from ..models.system_models import ErrorCodes, ApiError
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class NLPEngine:
    """Natural Language Processing Engine"""
    
    def __init__(self):
        """Initialize NLP engine"""
        self.confidence_threshold = settings.nlp_confidence_threshold
        self.default_language = settings.default_language
        
        # Action patterns (Japanese)
        self.action_patterns = {
            # Connection
            "connect": [
                r"(.*?)に?接続",
                r"(.*?)に?繋げ",
                r"(.*?)に?つなが",
                r"(.*?)に?コネクト"
            ],
            "disconnect": [
                r"(.*?)から?切断",
                r"(.*?)から?切断",
                r"接続を?切",
                r"ディスコネクト"
            ],
            
            # Flight control
            "takeoff": [
                r"離陸",
                r"起動",
                r"飛び立",
                r"テイクオフ"
            ],
            "land": [
                r"着陸",
                r"降り",
                r"ランディング",
                r"着地"
            ],
            "emergency": [
                r"緊急停止",
                r"止ま",
                r"ストップ",
                r"停止"
            ],
            
            # Movement
            "move": [
                r"移動",
                r"進",
                r"動",
                r"移",
                r"行"
            ],
            "rotate": [
                r"回転",
                r"回",
                r"向き",
                r"回る"
            ],
            "altitude": [
                r"高度",
                r"高さ",
                r"上昇",
                r"下降"
            ],
            
            # Camera
            "photo": [
                r"写真",
                r"撮影",
                r"撮",
                r"フォト"
            ],
            "streaming": [
                r"ストリーミング",
                r"配信",
                r"映像"
            ],
            "learning": [
                r"学習",
                r"データ収集",
                r"学習データ"
            ],
            
            # Vision
            "detection": [
                r"物体検出",
                r"検出",
                r"物体認識",
                r"何が見える"
            ],
            "tracking": [
                r"追跡",
                r"追従",
                r"トラッキング"
            ],
            
            # System
            "status": [
                r"状態",
                r"ステータス",
                r"様子"
            ],
            "health": [
                r"正常",
                r"ヘルス",
                r"健康"
            ]
        }
        
        # Parameter extraction patterns
        self.parameter_patterns = {
            "drone_id": [
                r"ドローン([A-Za-z0-9_-]+)",
                r"drone[-_]?([A-Za-z0-9_-]+)",
                r"([A-Za-z0-9_-]+)番目",
                r"([A-Za-z0-9_-]+)番"
            ],
            "distance": [
                r"(\d+)\s*(?:cm|センチ|センチメートル)",
                r"(\d+)\s*(?:m|メートル)",
                r"(\d+)\s*(?:mm|ミリ|ミリメートル)"
            ],
            "angle": [
                r"(\d+)\s*(?:度|°)",
                r"(\d+)\s*(?:度|°)\s*(?:回転|回)"
            ],
            "height": [
                r"高さ\s*(\d+)\s*(?:cm|センチ|センチメートル)",
                r"高さ\s*(\d+)\s*(?:m|メートル)",
                r"高度\s*(\d+)\s*(?:cm|センチ|センチメートル)",
                r"高度\s*(\d+)\s*(?:m|メートル)"
            ],
            "direction": [
                r"(右|左|前|後|上|下|forward|back|left|right|up|down)",
                r"(時計回り|反時計回り|clockwise|counter_clockwise)"
            ],
            "quality": [
                r"(高|中|低|high|medium|low)\s*(?:画質|品質)"
            ],
            "filename": [
                r"ファイル名\s*[：:]\s*([^\s]+)",
                r"名前\s*[：:]\s*([^\s]+)"
            ]
        }
        
        # Direction mappings
        self.direction_mappings = {
            "右": "right",
            "左": "left",
            "前": "forward",
            "後": "back",
            "上": "up",
            "下": "down",
            "時計回り": "clockwise",
            "反時計回り": "counter_clockwise"
        }
        
        # Unit conversions
        self.unit_conversions = {
            "m": 100,  # meters to cm
            "メートル": 100,
            "mm": 0.1,  # mm to cm
            "ミリ": 0.1,
            "ミリメートル": 0.1,
            "cm": 1,
            "センチ": 1,
            "センチメートル": 1
        }
        
        logger.info("NLP engine initialized")
    
    def parse_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> ParsedIntent:
        """Parse natural language command"""
        try:
            logger.debug(f"Parsing command: {command}")
            
            # Clean command
            command = command.strip()
            
            # Extract action
            action, confidence = self._extract_action(command)
            if not action:
                raise ValueError("Could not identify action in command")
            
            # Extract parameters
            parameters = self._extract_parameters(command, context)
            
            # Add context parameters
            if context:
                parameters.update(context)
            
            # Create parsed intent
            parsed_intent = ParsedIntent(
                action=action,
                parameters=parameters,
                confidence=confidence
            )
            
            logger.debug(f"Parsed intent: {parsed_intent}")
            return parsed_intent
            
        except Exception as e:
            logger.error(f"Error parsing command: {str(e)}")
            raise ValueError(f"Could not parse command: {str(e)}")
    
    def _extract_action(self, command: str) -> Tuple[str, float]:
        """Extract action from command"""
        best_action = None
        best_confidence = 0.0
        
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    confidence = 0.8  # Base confidence
                    
                    # Boost confidence for exact matches
                    if pattern in command:
                        confidence = 0.9
                    
                    if confidence > best_confidence:
                        best_action = action
                        best_confidence = confidence
        
        return best_action, best_confidence
    
    def _extract_parameters(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract parameters from command"""
        parameters = {}
        
        # Extract drone ID
        if "drone_id" not in (context or {}):
            drone_id = self._extract_drone_id(command)
            if drone_id:
                parameters["drone_id"] = drone_id
        
        # Extract distance
        distance = self._extract_distance(command)
        if distance:
            parameters["distance"] = distance
        
        # Extract angle
        angle = self._extract_angle(command)
        if angle:
            parameters["angle"] = angle
        
        # Extract height
        height = self._extract_height(command)
        if height:
            parameters["height"] = height
        
        # Extract direction
        direction = self._extract_direction(command)
        if direction:
            parameters["direction"] = direction
        
        # Extract quality
        quality = self._extract_quality(command)
        if quality:
            parameters["quality"] = quality
        
        # Extract filename
        filename = self._extract_filename(command)
        if filename:
            parameters["filename"] = filename
        
        return parameters
    
    def _extract_drone_id(self, command: str) -> Optional[str]:
        """Extract drone ID from command"""
        for pattern in self.parameter_patterns["drone_id"]:
            match = re.search(pattern, command)
            if match:
                return match.group(1)
        return None
    
    def _extract_distance(self, command: str) -> Optional[int]:
        """Extract distance from command"""
        for pattern in self.parameter_patterns["distance"]:
            match = re.search(pattern, command)
            if match:
                value = int(match.group(1))
                
                # Check for unit
                if "m" in match.group(0) or "メートル" in match.group(0):
                    value *= 100  # Convert to cm
                elif "mm" in match.group(0) or "ミリ" in match.group(0):
                    value = int(value * 0.1)  # Convert to cm
                
                return value
        return None
    
    def _extract_angle(self, command: str) -> Optional[int]:
        """Extract angle from command"""
        for pattern in self.parameter_patterns["angle"]:
            match = re.search(pattern, command)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_height(self, command: str) -> Optional[int]:
        """Extract height from command"""
        for pattern in self.parameter_patterns["height"]:
            match = re.search(pattern, command)
            if match:
                value = int(match.group(1))
                
                # Check for unit
                if "m" in match.group(0) or "メートル" in match.group(0):
                    value *= 100  # Convert to cm
                
                return value
        return None
    
    def _extract_direction(self, command: str) -> Optional[str]:
        """Extract direction from command"""
        for pattern in self.parameter_patterns["direction"]:
            match = re.search(pattern, command)
            if match:
                direction = match.group(1)
                return self.direction_mappings.get(direction, direction)
        return None
    
    def _extract_quality(self, command: str) -> Optional[str]:
        """Extract quality from command"""
        for pattern in self.parameter_patterns["quality"]:
            match = re.search(pattern, command)
            if match:
                quality = match.group(1)
                quality_mappings = {
                    "高": "high",
                    "中": "medium",
                    "低": "low"
                }
                return quality_mappings.get(quality, quality)
        return None
    
    def _extract_filename(self, command: str) -> Optional[str]:
        """Extract filename from command"""
        for pattern in self.parameter_patterns["filename"]:
            match = re.search(pattern, command)
            if match:
                return match.group(1)
        return None
    
    def suggest_corrections(self, command: str) -> List[str]:
        """Suggest corrections for unrecognized commands"""
        suggestions = []
        
        # Check for common typos or missing words
        if "ドローン" not in command and "drone" not in command:
            suggestions.append("ドローンIDを指定してください")
        
        if not any(action in command for actions in self.action_patterns.values() for action in actions):
            suggestions.append("動作を明確に指定してください（例：移動、撮影、接続）")
        
        # Check for missing parameters
        if "移動" in command and not any(re.search(pattern, command) for pattern in self.parameter_patterns["distance"]):
            suggestions.append("移動距離を指定してください（例：50cm、1m）")
        
        if "回転" in command and not any(re.search(pattern, command) for pattern in self.parameter_patterns["angle"]):
            suggestions.append("回転角度を指定してください（例：90度、180度）")
        
        return suggestions


# Global NLP engine instance
nlp_engine = NLPEngine()