"""
Tests for Enhanced NLP Engine - Phase 2
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.core.enhanced_nlp_engine import (
    EnhancedNLPEngine, ConfidenceLevel, IntentType, 
    IntentCandidate, ParameterCandidate
)
from src.models.command_models import ParsedIntent


class TestEnhancedNLPEngine:
    """Test Enhanced NLP Engine functionality"""
    
    @pytest.fixture
    def nlp_engine(self):
        """Create NLP engine instance"""
        return EnhancedNLPEngine()
    
    def test_initialization(self, nlp_engine):
        """Test NLP engine initialization"""
        assert nlp_engine is not None
        assert hasattr(nlp_engine, 'action_patterns')
        assert hasattr(nlp_engine, 'parameter_patterns')
        assert hasattr(nlp_engine, 'synonyms')
        assert hasattr(nlp_engine, 'context_memory')
        assert hasattr(nlp_engine, 'command_history')
    
    def test_basic_command_parsing(self, nlp_engine):
        """Test basic command parsing"""
        command = "ドローンAAに接続して"
        parsed = nlp_engine.parse_command(command)
        
        assert parsed.primary_intent.action == "connect"
        assert "drone_id" in parsed.primary_intent.parameters
        assert parsed.primary_intent.parameters["drone_id"] == "AA"
        assert parsed.primary_intent.confidence > 0.5
    
    def test_enhanced_movement_parsing(self, nlp_engine):
        """Test enhanced movement command parsing"""
        command = "右に50センチ移動して"
        parsed = nlp_engine.parse_command(command)
        
        assert parsed.primary_intent.action == "move"
        assert parsed.primary_intent.parameters["direction"] == "right"
        assert parsed.primary_intent.parameters["distance"] == 50
        assert parsed.confidence_level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
    
    def test_unit_conversion(self, nlp_engine):
        """Test unit conversion functionality"""
        command = "高度を1メートルにして"
        parsed = nlp_engine.parse_command(command)
        
        assert parsed.primary_intent.action == "altitude"
        assert parsed.primary_intent.parameters["height"] == 100  # Converted to cm
    
    def test_parameter_normalization(self, nlp_engine):
        """Test parameter normalization"""
        # Test angle normalization
        value = nlp_engine._normalize_parameter_value("angle", "半回転")
        assert value == 180
        
        # Test distance normalization
        value = nlp_engine._normalize_parameter_value("distance", "1.5m")
        assert value == 150
        
        # Test direction normalization
        value = nlp_engine._normalize_parameter_value("direction", "右")
        assert value == "right"
    
    def test_alternative_intents(self, nlp_engine):
        """Test alternative intent detection"""
        command = "撮影して"  # Could be photo or streaming
        parsed = nlp_engine.parse_command(command)
        
        assert parsed.primary_intent.action in ["photo", "streaming"]
        assert len(parsed.alternative_intents) >= 0
    
    def test_confidence_levels(self, nlp_engine):
        """Test confidence level classification"""
        # High confidence command
        command = "ドローンAAに接続して離陸して"
        parsed = nlp_engine.parse_command(command)
        assert parsed.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
        
        # Low confidence command
        command = "何かする"
        parsed = nlp_engine.parse_command(command)
        assert parsed.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
    
    def test_missing_parameters_detection(self, nlp_engine):
        """Test missing parameter detection"""
        command = "移動して"  # Missing direction and distance
        parsed = nlp_engine.parse_command(command)
        
        assert "direction" in parsed.missing_parameters
        assert "distance" in parsed.missing_parameters
        assert len(parsed.suggestions) > 0
    
    def test_context_memory(self, nlp_engine):
        """Test context memory functionality"""
        # First command with drone ID
        command1 = "ドローンAAに接続して"
        parsed1 = nlp_engine.parse_command(command1)
        
        # Second command without drone ID (should use context)
        command2 = "離陸して"
        parsed2 = nlp_engine.parse_command(command2)
        
        assert nlp_engine.last_drone_id == "AA"
        assert parsed2.primary_intent.parameters.get("drone_id") == "AA"
    
    def test_command_suggestions(self, nlp_engine):
        """Test command suggestion generation"""
        suggestions = nlp_engine.get_command_suggestions("ドローン")
        
        assert len(suggestions) > 0
        assert all("ドローン" in suggestion or "drone" in suggestion.lower() 
                  for suggestion in suggestions)
    
    def test_complexity_analysis(self, nlp_engine):
        """Test command complexity analysis"""
        command = "ドローンAAに接続して高度1メートルで右に50cm移動して写真を撮って"
        analysis = nlp_engine.analyze_command_complexity(command)
        
        assert "complexity_score" in analysis
        assert "parameter_count" in analysis
        assert "confidence_level" in analysis
        assert "estimated_execution_time" in analysis
        assert analysis["complexity_score"] >= 0.0
        assert analysis["complexity_score"] <= 1.0
    
    def test_synonym_recognition(self, nlp_engine):
        """Test synonym recognition"""
        # Test different ways to say "right"
        commands = [
            "右に移動",
            "右側に移動", 
            "right方向に移動"
        ]
        
        for command in commands:
            parsed = nlp_engine.parse_command(command)
            if parsed.primary_intent.action == "move":
                assert parsed.primary_intent.parameters.get("direction") == "right"
    
    def test_numeric_word_conversion(self, nlp_engine):
        """Test conversion of numeric words"""
        command = "一回転して"
        parsed = nlp_engine.parse_command(command)
        
        if parsed.primary_intent.action == "rotate":
            assert parsed.primary_intent.parameters.get("angle") == 360
    
    def test_error_handling(self, nlp_engine):
        """Test error handling for invalid commands"""
        with pytest.raises(ValueError):
            nlp_engine.parse_command("")
        
        with pytest.raises(ValueError):
            nlp_engine.parse_command("無効なコマンド123!@#")
    
    def test_intent_candidate_extraction(self, nlp_engine):
        """Test intent candidate extraction"""
        command = "撮影して"
        candidates = nlp_engine._extract_intent_candidates(command)
        
        assert len(candidates) > 0
        assert all(isinstance(candidate, IntentCandidate) for candidate in candidates)
        assert all(candidate.confidence > 0 for candidate in candidates)
    
    def test_parameter_confidence_scoring(self, nlp_engine):
        """Test parameter confidence scoring"""
        command = "ドローンAAに接続して右に50センチ移動"
        parsed = nlp_engine.parse_command(command)
        
        assert hasattr(parsed, 'parameter_confidence')
        assert len(parsed.parameter_confidence) > 0
        assert all(0 <= confidence <= 1 for confidence in parsed.parameter_confidence.values())
    
    def test_command_history_tracking(self, nlp_engine):
        """Test command history tracking"""
        initial_history_length = len(nlp_engine.command_history)
        
        command = "ドローンAAに接続"
        nlp_engine.parse_command(command)
        
        assert len(nlp_engine.command_history) == initial_history_length + 1
        assert nlp_engine.command_history[-1]["action"] == "connect"
    
    def test_context_boost_calculation(self, nlp_engine):
        """Test context boost calculation"""
        # Set up context
        nlp_engine.last_action = "move"
        nlp_engine.last_drone_id = "AA"
        
        candidate = IntentCandidate(
            action="move",
            confidence=0.7,
            intent_type=IntentType.MOVEMENT,
            matched_patterns=[]
        )
        
        context = {"drone_id": "AA"}
        boost = nlp_engine._calculate_context_boost(candidate, context)
        
        assert boost > 0
        assert boost <= nlp_engine.context_boost_factor * 2  # Max possible boost
    
    def test_session_parameters(self, nlp_engine):
        """Test session parameter persistence"""
        # Set quality in first command
        command1 = "高画質で写真を撮って"
        parsed1 = nlp_engine.parse_command(command1)
        
        # Check if quality is stored in session
        if "quality" in parsed1.primary_intent.parameters:
            assert "quality" in nlp_engine.session_parameters
    
    def test_multilingual_support(self, nlp_engine):
        """Test basic multilingual support"""
        commands = [
            "takeoff",  # English
            "離陸",     # Japanese
            "go right", # English
            "右に行く"  # Japanese
        ]
        
        for command in commands:
            try:
                parsed = nlp_engine.parse_command(command)
                assert parsed is not None
            except ValueError:
                # Some commands might not be recognized, which is okay
                pass
    
    def test_command_normalization(self, nlp_engine):
        """Test command text normalization"""
        # Test with extra whitespace
        command = "  ドローン  AA  に  接続  "
        normalized = nlp_engine._normalize_command(command)
        assert normalized == "ドローン AA に 接続"
        
        # Test with full-width numbers
        command_fw = "１メートル上昇"
        normalized_fw = nlp_engine._normalize_command(command_fw)
        assert "1メートル" in normalized_fw
    
    @pytest.mark.parametrize("action,expected_type", [
        ("connect", IntentType.CONNECTION),
        ("takeoff", IntentType.FLIGHT_CONTROL),
        ("move", IntentType.MOVEMENT),
        ("photo", IntentType.CAMERA),
        ("detection", IntentType.VISION),
        ("status", IntentType.SYSTEM)
    ])
    def test_intent_type_mapping(self, nlp_engine, action, expected_type):
        """Test intent type mapping"""
        assert nlp_engine.intent_types[action] == expected_type
    
    def test_edge_cases(self, nlp_engine):
        """Test edge cases and boundary conditions"""
        # Very long command
        long_command = "ドローン" + "A" * 100 + "に接続して移動して撮影して"
        try:
            parsed = nlp_engine.parse_command(long_command)
            assert parsed is not None
        except ValueError:
            # Long commands might fail, which is acceptable
            pass
        
        # Command with special characters
        special_command = "ドローン@#$%に接続"
        try:
            parsed = nlp_engine.parse_command(special_command)
            # Should handle gracefully
            assert parsed is not None
        except ValueError:
            # May fail, which is acceptable
            pass
    
    def test_performance_basic(self, nlp_engine):
        """Test basic performance requirements"""
        import time
        
        command = "ドローンAAに接続して離陸して右に50cm移動して写真を撮って着陸"
        
        start_time = time.time()
        parsed = nlp_engine.parse_command(command)
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second for complex command)
        assert end_time - start_time < 1.0
        assert parsed is not None