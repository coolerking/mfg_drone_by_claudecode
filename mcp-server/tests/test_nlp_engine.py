"""
Tests for NLP Engine
"""

import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.nlp_engine import NLPEngine


class TestNLPEngine:
    """Test NLP Engine"""
    
    def setup_method(self):
        """Setup for each test"""
        self.nlp_engine = NLPEngine()
    
    def test_parse_connect_command(self):
        """Test parsing connect command"""
        command = "ドローンAAに接続して"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "connect"
        assert parsed.parameters.get("drone_id") == "AA"
        assert parsed.confidence > 0.7
    
    def test_parse_move_command(self):
        """Test parsing move command"""
        command = "右に50センチ移動して"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "move"
        assert parsed.parameters.get("direction") == "right"
        assert parsed.parameters.get("distance") == 50
        assert parsed.confidence > 0.7
    
    def test_parse_takeoff_command(self):
        """Test parsing takeoff command"""
        command = "ドローンを離陸させて"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "takeoff"
        assert parsed.confidence > 0.7
    
    def test_parse_photo_command(self):
        """Test parsing photo command"""
        command = "写真を撮って"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "photo"
        assert parsed.confidence > 0.7
    
    def test_parse_rotate_command(self):
        """Test parsing rotate command"""
        command = "右に90度回転して"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "rotate"
        assert parsed.parameters.get("direction") == "right"
        assert parsed.parameters.get("angle") == 90
        assert parsed.confidence > 0.7
    
    def test_parse_height_command(self):
        """Test parsing height command"""
        command = "高度を1メートルにして"
        parsed = self.nlp_engine.parse_command(command)
        
        assert parsed.action == "altitude"
        assert parsed.parameters.get("height") == 100  # Converted to cm
        assert parsed.confidence > 0.7
    
    def test_unit_conversion(self):
        """Test unit conversion"""
        # Test meter to cm conversion
        distance_m = self.nlp_engine._extract_distance("1メートル移動")
        assert distance_m == 100
        
        # Test cm
        distance_cm = self.nlp_engine._extract_distance("50センチ移動")
        assert distance_cm == 50
    
    def test_direction_mapping(self):
        """Test direction mapping"""
        direction = self.nlp_engine._extract_direction("右に移動")
        assert direction == "right"
        
        direction = self.nlp_engine._extract_direction("時計回りに回転")
        assert direction == "clockwise"
    
    def test_drone_id_extraction(self):
        """Test drone ID extraction"""
        drone_id = self.nlp_engine._extract_drone_id("ドローンAAに接続")
        assert drone_id == "AA"
        
        drone_id = self.nlp_engine._extract_drone_id("drone-001を起動")
        assert drone_id == "001"
    
    def test_error_handling(self):
        """Test error handling for invalid commands"""
        with pytest.raises(ValueError):
            self.nlp_engine.parse_command("意味不明なコマンド")
    
    def test_suggestions(self):
        """Test correction suggestions"""
        suggestions = self.nlp_engine.suggest_corrections("移動")
        assert "ドローンIDを指定してください" in suggestions
        assert "移動距離を指定してください" in suggestions


if __name__ == "__main__":
    pytest.main([__file__])