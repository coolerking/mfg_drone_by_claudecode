"""
Enhanced Natural Language Processing Engine for MCP Server - Phase 2
Advanced Japanese command parsing with context awareness and multiple interpretations
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple, NamedTuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..models.command_models import ParsedIntent
from ..models.system_models import ErrorCodes, ApiError
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class IntentType(Enum):
    """Intent type classifications"""
    CONNECTION = "connection"
    FLIGHT_CONTROL = "flight_control"
    MOVEMENT = "movement"
    CAMERA = "camera"
    VISION = "vision"
    SYSTEM = "system"


class ConfidenceLevel(Enum):
    """Confidence level classifications"""
    HIGH = "high"      # 0.8-1.0
    MEDIUM = "medium"  # 0.6-0.8
    LOW = "low"        # 0.4-0.6
    VERY_LOW = "very_low"  # 0.0-0.4


@dataclass
class IntentCandidate:
    """Intent candidate with confidence score"""
    action: str
    confidence: float
    intent_type: IntentType
    matched_patterns: List[str]
    context_boost: float = 0.0
    synonym_match: bool = False


@dataclass
class ParameterCandidate:
    """Parameter candidate with confidence"""
    name: str
    value: Any
    confidence: float
    source_pattern: str
    unit: Optional[str] = None
    normalized_value: Optional[Any] = None


@dataclass
class ParsedCommand:
    """Enhanced parsed command with multiple interpretations"""
    primary_intent: ParsedIntent
    alternative_intents: List[ParsedIntent]
    confidence_level: ConfidenceLevel
    parameter_confidence: Dict[str, float]
    missing_parameters: List[str]
    suggestions: List[str]


class EnhancedNLPEngine:
    """Enhanced context-aware Natural Language Processing Engine"""
    
    def __init__(self):
        """Initialize enhanced NLP engine"""
        self.confidence_threshold = settings.nlp_confidence_threshold
        self.default_language = settings.default_language
        
        # Enhanced features
        self.context_memory = {}  # Store conversation context
        self.last_drone_id = None
        self.last_action = None
        self.session_parameters = {}  # Parameters that persist across commands
        self.command_history = []  # Track recent commands
        
        # Advanced confidence settings
        self.min_confidence_threshold = 0.3
        self.high_confidence_threshold = 0.8
        self.context_boost_factor = 0.2
        self.synonym_boost_factor = 0.1
        
        # Enhanced action patterns with synonyms and variations
        self.action_patterns = {
            # Connection - Enhanced with more variations
            "connect": [
                r"(.*?)に?接続", r"(.*?)に?繋げ", r"(.*?)に?つなが", r"(.*?)に?コネクト",
                r"(.*?)と?接続", r"(.*?)へ?接続", r"(.*?)に?つなぐ",
                r"(.*?)に?リンク", r"(.*?)に?アクセス", r"(.*?)を?起動",
                r"(.*?)に?ログイン", r"(.*?)を?オン"
            ],
            "disconnect": [
                r"(.*?)から?切断", r"接続を?切", r"ディスコネクト",
                r"(.*?)を?切断", r"(.*?)から?離れ", r"(.*?)を?オフ",
                r"(.*?)を?停止", r"(.*?)から?ログアウト",
                r"切る", r"終了"
            ],
            
            # Flight control - Enhanced with natural expressions
            "takeoff": [
                r"離陸", r"起動", r"飛び立", r"テイクオフ",
                r"上昇", r"浮上", r"飛ぶ", r"浮く",
                r"立ち上が", r"舞い上が", r"空に", r"飛行開始",
                r"hover", r"上がれ", r"上がって"
            ],
            "land": [
                r"着陸", r"降り", r"ランディング", r"着地",
                r"下降", r"降下", r"下りる", r"降りる",
                r"地面に", r"床に", r"降ろす", r"着く",
                r"landing", r"下がって", r"戻って"
            ],
            "emergency": [
                r"緊急停止", r"止ま", r"ストップ", r"停止",
                r"緊急", r"危険", r"やばい", r"止めて",
                r"emergency", r"STOP", r"help", r"助けて",
                r"中止", r"キャンセル", r"abort"
            ],
            
            # Movement - More comprehensive patterns
            "move": [
                r"移動", r"進", r"動", r"移", r"行",
                r"向か", r"進む", r"動く", r"移る",
                r"go", r"move", r"fly", r"travel",
                r"行って", r"進んで", r"動いて"
            ],
            "rotate": [
                r"回転", r"回", r"向き", r"回る",
                r"向く", r"向ける", r"回す", r"旋回",
                r"rotate", r"turn", r"spin",
                r"振り向", r"方向転換", r"向きを変え"
            ],
            "altitude": [
                r"高度", r"高さ", r"上昇", r"下降",
                r"altitude", r"height", r"level",
                r"上げ", r"下げ", r"高く", r"低く",
                r"空中", r"レベル"
            ],
            
            # Camera - Enhanced with casual expressions
            "photo": [
                r"写真", r"撮影", r"撮", r"フォト",
                r"photo", r"picture", r"pic", r"shot",
                r"写", r"カメラ", r"シャッター",
                r"記録", r"capture", r"snap"
            ],
            "streaming": [
                r"ストリーミング", r"配信", r"映像",
                r"streaming", r"stream", r"video",
                r"生中継", r"ライブ", r"リアルタイム",
                r"放送", r"中継"
            ],
            "learning": [
                r"学習", r"データ収集", r"学習データ",
                r"learning", r"training", r"data",
                r"トレーニング", r"訓練", r"教育",
                r"覚え", r"記憶"
            ],
            
            # Vision - More natural queries
            "detection": [
                r"物体検出", r"検出", r"物体認識", r"何が見える",
                r"detection", r"detect", r"recognize", r"find",
                r"探", r"見つけ", r"認識", r"識別",
                r"何がある", r"見える", r"確認", r"チェック"
            ],
            "tracking": [
                r"追跡", r"追従", r"トラッキング",
                r"tracking", r"track", r"follow",
                r"追いかけ", r"付いて", r"後を",
                r"監視", r"見守"
            ],
            
            # System - More conversational
            "status": [
                r"状態", r"ステータス", r"様子",
                r"status", r"state", r"condition",
                r"どう", r"調子", r"具合",
                r"情報", r"確認", r"チェック"
            ],
            "health": [
                r"正常", r"ヘルス", r"健康",
                r"health", r"healthy", r"ok",
                r"大丈夫", r"元気", r"問題",
                r"動作", r"機能"
            ]
        }
        
        # Intent type mapping
        self.intent_types = {
            "connect": IntentType.CONNECTION,
            "disconnect": IntentType.CONNECTION,
            "takeoff": IntentType.FLIGHT_CONTROL,
            "land": IntentType.FLIGHT_CONTROL,
            "emergency": IntentType.FLIGHT_CONTROL,
            "move": IntentType.MOVEMENT,
            "rotate": IntentType.MOVEMENT,
            "altitude": IntentType.MOVEMENT,
            "photo": IntentType.CAMERA,
            "streaming": IntentType.CAMERA,
            "learning": IntentType.CAMERA,
            "detection": IntentType.VISION,
            "tracking": IntentType.VISION,
            "status": IntentType.SYSTEM,
            "health": IntentType.SYSTEM
        }
        
        # Enhanced parameter extraction with multiple formats
        self.parameter_patterns = {
            "drone_id": [
                r"ドローン([A-Za-z0-9_-]+)", r"drone[-_]?([A-Za-z0-9_-]+)",
                r"([A-Za-z0-9_-]+)番目", r"([A-Za-z0-9_-]+)番",
                r"([A-Z]+)号機", r"([A-Z]+)機",
                r"ID([A-Za-z0-9_-]+)", r"([A-Za-z0-9_-]+)を",
                r"([A-Za-z0-9_-]+)に", r"([A-Za-z0-9_-]+)で"
            ],
            "distance": [
                r"(\d+\.?\d*)\s*(?:cm|センチ|センチメートル)",
                r"(\d+\.?\d*)\s*(?:m|メートル)",
                r"(\d+\.?\d*)\s*(?:mm|ミリ|ミリメートル)",
                r"(\d+\.?\d*)\s*(?:km|キロ|キロメートル)",
                r"(\d+\.?\d*)\s*(?:inch|インチ)",
                r"(\d+\.?\d*)\s*(?:feet|フィート|ft)"
            ],
            "angle": [
                r"(\d+\.?\d*)\s*(?:度|°)",
                r"(\d+\.?\d*)\s*(?:度|°)\s*(?:回転|回)",
                r"(\d+\.?\d*)\s*(?:rad|ラジアン)",
                r"(半|180)\s*(?:回転|°)",
                r"(一|1)\s*(?:回転|周|°)"
            ],
            "height": [
                r"高さ\s*(\d+\.?\d*)\s*(?:cm|センチ|センチメートル)",
                r"高さ\s*(\d+\.?\d*)\s*(?:m|メートル)",
                r"高度\s*(\d+\.?\d*)\s*(?:cm|センチ|センチメートル)",
                r"高度\s*(\d+\.?\d*)\s*(?:m|メートル)",
                r"(\d+\.?\d*)\s*(?:cm|センチ|センチメートル)\s*(?:の高さ|まで|に)",
                r"(\d+\.?\d*)\s*(?:m|メートル)\s*(?:の高さ|まで|に)"
            ],
            "direction": [
                r"(右|左|前|後|上|下|forward|back|left|right|up|down)",
                r"(時計回り|反時計回り|clockwise|counter_clockwise)",
                r"(北|南|東|西|north|south|east|west)",
                r"(正面|背面|側面|真上|真下)",
                r"(右側|左側|前方|後方|上方|下方)"
            ],
            "quality": [
                r"(高|中|低|high|medium|low)\s*(?:画質|品質)",
                r"(?:画質|品質)\s*(高|中|低|high|medium|low)",
                r"(最高|最低|普通|standard|premium)",
                r"(HD|4K|720p|1080p)"
            ],
            "filename": [
                r"ファイル名\s*[：:]\s*([^\s]+)",
                r"名前\s*[：:]\s*([^\s]+)",
                r"([^\s]+\.(?:jpg|png|mp4|avi))\s*(?:で|に|として)",
                r"([A-Za-z0-9_-]+)\s*(?:という名前|として|で保存)"
            ],
            "speed": [
                r"速度\s*(\d+\.?\d*)\s*(?:cm/s|センチ毎秒)",
                r"スピード\s*(\d+\.?\d*)\s*(?:cm/s|センチ毎秒)",
                r"(ゆっくり|普通|速く|slow|normal|fast)",
                r"(\d+\.?\d*)\s*(?:%|パーセント)\s*(?:の速度|で)"
            ],
            "count": [
                r"(\d+)\s*(?:回|枚|個|つ)",
                r"(\d+)\s*(?:times|pieces)",
                r"(一|二|三|四|五|六|七|八|九|十)\s*(?:回|枚|個|つ)"
            ]
        }
        
        # Synonym groups for better understanding
        self.synonyms = {
            "right": ["右", "right", "右側", "右方向"],
            "left": ["左", "left", "左側", "左方向"],
            "forward": ["前", "forward", "前方", "正面"],
            "back": ["後", "back", "後方", "背面"],
            "up": ["上", "up", "上方", "真上"],
            "down": ["下", "down", "下方", "真下"],
            "clockwise": ["時計回り", "clockwise", "右回り"],
            "counter_clockwise": ["反時計回り", "counter_clockwise", "左回り"]
        }
        
        # Direction mappings
        self.direction_mappings = {
            "右": "right", "左": "left", "前": "forward", "後": "back",
            "上": "up", "下": "down", "時計回り": "clockwise", "反時計回り": "counter_clockwise"
        }
        
        # Enhanced unit conversions
        self.unit_conversions = {
            "m": 100, "メートル": 100,     # meters to cm
            "mm": 0.1, "ミリ": 0.1, "ミリメートル": 0.1,  # mm to cm
            "cm": 1, "センチ": 1, "センチメートル": 1,     # cm to cm
            "km": 100000, "キロ": 100000, "キロメートル": 100000,  # km to cm
            "inch": 2.54, "インチ": 2.54,  # inch to cm
            "feet": 30.48, "フィート": 30.48, "ft": 30.48  # feet to cm
        }
        
        # Numeric word mappings
        self.numeric_words = {
            "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "半": 0.5, "倍": 2
        }
        
        logger.info("Enhanced NLP engine initialized with advanced features")
    
    def parse_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        """Parse natural language command with enhanced analysis"""
        try:
            logger.debug(f"Parsing enhanced command: {command}")
            
            # Clean and normalize command
            command = self._normalize_command(command)
            
            # Extract all intent candidates
            intent_candidates = self._extract_intent_candidates(command, context)
            
            if not intent_candidates:
                raise ValueError("Could not identify any action in command")
            
            # Sort by confidence
            intent_candidates.sort(key=lambda x: x.confidence, reverse=True)
            
            # Create primary and alternative intents
            primary_candidate = intent_candidates[0]
            alternative_candidates = intent_candidates[1:3]  # Top 2 alternatives
            
            # Extract parameters with confidence scoring
            parameters, param_confidence = self._extract_parameters_with_confidence(command, context)
            
            # Apply context boosting
            if context:
                primary_candidate.confidence += self._calculate_context_boost(primary_candidate, context)
                parameters.update(context)
            
            # Create primary intent
            primary_intent = ParsedIntent(
                action=primary_candidate.action,
                parameters=parameters,
                confidence=min(primary_candidate.confidence, 1.0)
            )
            
            # Create alternative intents
            alternative_intents = []
            for candidate in alternative_candidates:
                alt_params = parameters.copy()
                alt_intent = ParsedIntent(
                    action=candidate.action,
                    parameters=alt_params,
                    confidence=min(candidate.confidence, 1.0)
                )
                alternative_intents.append(alt_intent)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(primary_intent.confidence)
            
            # Identify missing parameters
            missing_parameters = self._identify_missing_parameters(primary_intent.action, parameters)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(command, primary_intent, missing_parameters)
            
            # Create enhanced parsed command
            parsed_command = ParsedCommand(
                primary_intent=primary_intent,
                alternative_intents=alternative_intents,
                confidence_level=confidence_level,
                parameter_confidence=param_confidence,
                missing_parameters=missing_parameters,
                suggestions=suggestions
            )
            
            # Update context memory
            self._update_context_memory(parsed_command)
            
            logger.debug(f"Enhanced parsing completed: {parsed_command}")
            return parsed_command
            
        except Exception as e:
            logger.error(f"Error in enhanced parsing: {str(e)}")
            raise ValueError(f"Could not parse command: {str(e)}")
    
    def _normalize_command(self, command: str) -> str:
        """Normalize command text"""
        # Remove extra whitespace
        command = re.sub(r'\s+', ' ', command.strip())
        
        # Convert full-width numbers to half-width
        command = command.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        # Convert full-width punctuation
        command = command.replace('，', ',').replace('．', '.')
        
        return command
    
    def _extract_intent_candidates(self, command: str, context: Optional[Dict[str, Any]] = None) -> List[IntentCandidate]:
        """Extract all possible intent candidates with confidence scores"""
        candidates = []
        
        for action, patterns in self.action_patterns.items():
            matched_patterns = []
            confidence_scores = []
            
            for pattern in patterns:
                if re.search(pattern, command):
                    matched_patterns.append(pattern)
                    
                    # Calculate base confidence based on match quality
                    match = re.search(pattern, command)
                    if match:
                        # Exact match gets higher confidence
                        if match.group(0).strip() == command.strip():
                            confidence_scores.append(0.95)
                        # Longer matches get higher confidence
                        elif len(match.group(0)) > len(command) * 0.8:
                            confidence_scores.append(0.85)
                        else:
                            confidence_scores.append(0.7)
            
            if matched_patterns:
                # Use highest confidence among matched patterns
                base_confidence = max(confidence_scores)
                
                # Apply intent-specific boosting
                intent_type = self.intent_types.get(action, IntentType.SYSTEM)
                
                candidate = IntentCandidate(
                    action=action,
                    confidence=base_confidence,
                    intent_type=intent_type,
                    matched_patterns=matched_patterns
                )
                
                candidates.append(candidate)
        
        return candidates
    
    def _extract_parameters_with_confidence(self, command: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """Extract parameters with confidence scoring"""
        parameters = {}
        param_confidence = {}
        
        # Extract each parameter type
        for param_type, patterns in self.parameter_patterns.items():
            if param_type in (context or {}):
                continue  # Skip if already in context
            
            candidates = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, command)
                for match in matches:
                    value = match.group(1)
                    confidence = 0.8  # Base confidence
                    
                    # Normalize value
                    normalized_value = self._normalize_parameter_value(param_type, value)
                    
                    candidates.append(ParameterCandidate(
                        name=param_type,
                        value=value,
                        confidence=confidence,
                        source_pattern=pattern,
                        normalized_value=normalized_value
                    ))
            
            # Select best candidate
            if candidates:
                best_candidate = max(candidates, key=lambda x: x.confidence)
                parameters[param_type] = best_candidate.normalized_value or best_candidate.value
                param_confidence[param_type] = best_candidate.confidence
        
        # Use context memory for missing parameters
        if self.last_drone_id and "drone_id" not in parameters:
            parameters["drone_id"] = self.last_drone_id
            param_confidence["drone_id"] = 0.6  # Lower confidence for inferred
        
        return parameters, param_confidence
    
    def _normalize_parameter_value(self, param_type: str, value: str) -> Any:
        """Normalize parameter values"""
        if param_type == "distance" or param_type == "height":
            # Extract numeric value and unit
            match = re.search(r'(\d+\.?\d*)\s*([^\d]*)', value)
            if match:
                num_value = float(match.group(1))
                unit = match.group(2).strip()
                
                # Convert to cm
                if unit in self.unit_conversions:
                    return int(num_value * self.unit_conversions[unit])
                return int(num_value)
        
        elif param_type == "angle":
            # Handle angle conversions
            if "半" in value or "180" in value:
                return 180
            elif "一" in value or "1" in value:
                return 360
            else:
                match = re.search(r'(\d+\.?\d*)', value)
                if match:
                    return int(float(match.group(1)))
        
        elif param_type == "direction":
            # Map to standard directions
            return self.direction_mappings.get(value, value)
        
        elif param_type == "quality":
            # Map quality levels
            quality_map = {
                "高": "high", "中": "medium", "低": "low",
                "最高": "high", "普通": "medium", "最低": "low"
            }
            return quality_map.get(value, value)
        
        elif param_type == "speed":
            # Handle speed mappings
            if value in ["ゆっくり", "slow"]:
                return 20
            elif value in ["普通", "normal"]:
                return 50
            elif value in ["速く", "fast"]:
                return 80
            else:
                match = re.search(r'(\d+\.?\d*)', value)
                if match:
                    return int(float(match.group(1)))
        
        elif param_type == "count":
            # Convert text numbers
            if value in self.numeric_words:
                return self.numeric_words[value]
            else:
                match = re.search(r'(\d+)', value)
                if match:
                    return int(match.group(1))
        
        return value
    
    def _calculate_context_boost(self, candidate: IntentCandidate, context: Dict[str, Any]) -> float:
        """Calculate context-based confidence boost"""
        boost = 0.0
        
        # Same action type as previous command
        if self.last_action and candidate.action == self.last_action:
            boost += self.context_boost_factor
        
        # Same intent type as previous command
        if self.last_action and self.intent_types.get(self.last_action) == candidate.intent_type:
            boost += self.context_boost_factor * 0.5
        
        # Drone ID consistency
        if context.get("drone_id") == self.last_drone_id:
            boost += self.context_boost_factor * 0.3
        
        return boost
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level category"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _identify_missing_parameters(self, action: str, parameters: Dict[str, Any]) -> List[str]:
        """Identify missing required parameters for an action"""
        required_params = {
            "connect": ["drone_id"],
            "disconnect": ["drone_id"],
            "takeoff": ["drone_id"],
            "land": ["drone_id"],
            "emergency": ["drone_id"],
            "move": ["drone_id", "direction", "distance"],
            "rotate": ["drone_id", "direction", "angle"],
            "altitude": ["drone_id", "height"],
            "photo": ["drone_id"],
            "streaming": ["drone_id"],
            "learning": ["drone_id", "object_name"],
            "detection": ["drone_id"],
            "tracking": ["drone_id"],
            "status": [],  # drone_id is optional
            "health": []
        }
        
        required = required_params.get(action, [])
        missing = [param for param in required if param not in parameters]
        
        return missing
    
    def _generate_suggestions(self, command: str, intent: ParsedIntent, missing_params: List[str]) -> List[str]:
        """Generate suggestions for improving the command"""
        suggestions = []
        
        # Low confidence suggestions
        if intent.confidence < 0.6:
            suggestions.append("コマンドをより具体的に表現してください")
            
            # Suggest specific actions if very low confidence
            if intent.confidence < 0.4:
                suggestions.append("例：「ドローンAAに接続して」「右に50cm移動して」")
        
        # Missing parameter suggestions
        for param in missing_params:
            if param == "drone_id":
                suggestions.append("ドローンIDを指定してください（例：ドローンAA）")
            elif param == "direction":
                suggestions.append("方向を指定してください（例：右、左、前、後）")
            elif param == "distance":
                suggestions.append("距離を指定してください（例：50cm、1m）")
            elif param == "angle":
                suggestions.append("角度を指定してください（例：90度、180度）")
            elif param == "height":
                suggestions.append("高度を指定してください（例：1m、100cm）")
            elif param == "object_name":
                suggestions.append("物体名を指定してください（例：ボール、人）")
        
        # Action-specific suggestions
        if intent.action == "move" and "speed" not in intent.parameters:
            suggestions.append("速度を指定することもできます（例：ゆっくり、普通、速く）")
        
        if intent.action == "photo" and "quality" not in intent.parameters:
            suggestions.append("画質を指定することもできます（例：高画質、中画質）")
        
        return suggestions
    
    def _update_context_memory(self, parsed_command: ParsedCommand):
        """Update context memory with current command"""
        intent = parsed_command.primary_intent
        
        # Update last action and drone ID
        self.last_action = intent.action
        if "drone_id" in intent.parameters:
            self.last_drone_id = intent.parameters["drone_id"]
        
        # Add to command history
        self.command_history.append({
            "action": intent.action,
            "parameters": intent.parameters,
            "timestamp": datetime.now(),
            "confidence": intent.confidence
        })
        
        # Keep only recent history
        if len(self.command_history) > 10:
            self.command_history = self.command_history[-10:]
        
        # Update session parameters
        persistent_params = ["drone_id", "quality", "speed"]
        for param in persistent_params:
            if param in intent.parameters:
                self.session_parameters[param] = intent.parameters[param]
    
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions based on partial input"""
        suggestions = []
        
        # Common command patterns
        common_commands = [
            "ドローンAAに接続して",
            "離陸して",
            "右に50cm移動して",
            "90度右に回転して",
            "写真を撮って",
            "着陸して"
        ]
        
        # Filter based on partial input
        for cmd in common_commands:
            if any(word in cmd for word in partial_command.split()):
                suggestions.append(cmd)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def analyze_command_complexity(self, command: str) -> Dict[str, Any]:
        """Analyze command complexity and provide detailed breakdown"""
        parsed = self.parse_command(command)
        
        analysis = {
            "complexity_score": self._calculate_complexity_score(parsed),
            "parameter_count": len(parsed.primary_intent.parameters),
            "confidence_level": parsed.confidence_level.value,
            "has_alternatives": len(parsed.alternative_intents) > 0,
            "missing_parameters": parsed.missing_parameters,
            "suggestions": parsed.suggestions,
            "estimated_execution_time": self._estimate_execution_time(parsed.primary_intent.action)
        }
        
        return analysis
    
    def _calculate_complexity_score(self, parsed_command: ParsedCommand) -> float:
        """Calculate command complexity score (0-1)"""
        score = 0.0
        
        # Base score from confidence
        score += (1.0 - parsed_command.primary_intent.confidence) * 0.4
        
        # Parameter complexity
        param_count = len(parsed_command.primary_intent.parameters)
        score += min(param_count / 5.0, 0.3)  # Max 0.3 for parameters
        
        # Missing parameters penalty
        missing_count = len(parsed_command.missing_parameters)
        score += min(missing_count / 3.0, 0.3)  # Max 0.3 for missing params
        
        return min(score, 1.0)
    
    def _estimate_execution_time(self, action: str) -> float:
        """Estimate execution time in seconds"""
        time_estimates = {
            "connect": 2.0,
            "disconnect": 1.0,
            "takeoff": 5.0,
            "land": 3.0,
            "emergency": 0.5,
            "move": 3.0,
            "rotate": 2.0,
            "altitude": 4.0,
            "photo": 1.0,
            "streaming": 1.0,
            "learning": 30.0,
            "detection": 2.0,
            "tracking": 1.0,
            "status": 0.5,
            "health": 0.5
        }
        
        return time_estimates.get(action, 2.0)


# Create enhanced global instance
enhanced_nlp_engine = EnhancedNLPEngine()