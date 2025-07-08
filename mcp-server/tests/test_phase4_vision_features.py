"""
Test cases for Phase 4 Enhanced Vision Features
Comprehensive testing of advanced camera and vision capabilities
"""

import pytest
import asyncio
import base64
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.phase4_vision_processor import Phase4VisionProcessor
from core.enhanced_nlp_engine import EnhancedNLPEngine
from core.backend_client import BackendClient
from models.phase4_vision_models import (
    VisionCommandAnalysis, BatchVisionCommand, BatchVisionResult,
    ExecutionMode, TrackingAlgorithm, VisionModelType
)


@pytest.fixture
def mock_backend_client():
    """Mock backend client for testing"""
    client = AsyncMock(spec=BackendClient)
    
    # Mock response for enhanced detection
    client._request.return_value = {
        "detections": [
            {
                "label": "person",
                "confidence": 0.85,
                "bbox": {"x": 100, "y": 50, "width": 150, "height": 200}
            }
        ],
        "processing_time": 0.123,
        "model_id": "yolo_v8_general"
    }
    
    return client


@pytest.fixture
def mock_nlp_engine():
    """Mock enhanced NLP engine for testing"""
    engine = MagicMock(spec=EnhancedNLPEngine)
    
    # Mock parse result
    mock_result = MagicMock()
    mock_result.confidence = 0.9
    mock_result.intent = "photo"
    mock_result.parameters = {"drone_id": "AA"}
    
    engine.parse_command_enhanced.return_value = mock_result
    
    return engine


@pytest.fixture
def vision_processor(mock_nlp_engine, mock_backend_client):
    """Create vision processor instance for testing"""
    return Phase4VisionProcessor(mock_nlp_engine, mock_backend_client)


class TestVisionCommandAnalysis:
    """Test vision command analysis functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_photo_command(self, vision_processor):
        """Test analysis of photo commands"""
        commands = [
            "写真を撮って",
            "カメラで撮影して",
            "スナップを撮って",
            "take a photo",
            "capture image"
        ]
        
        for command in commands:
            analysis = await vision_processor.analyze_vision_command(command)
            
            assert isinstance(analysis, VisionCommandAnalysis)
            assert analysis.detected_intent == "photo"
            assert analysis.confidence > 0.5
            assert len(analysis.suggested_api_calls) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_detection_command(self, vision_processor):
        """Test analysis of detection commands"""
        commands = [
            "物体を検出して",
            "何が見えるか教えて",
            "オブジェクトを認識して",
            "detect objects",
            "find targets"
        ]
        
        for command in commands:
            analysis = await vision_processor.analyze_vision_command(command)
            
            assert analysis.detected_intent == "detection"
            assert analysis.confidence > 0.5
            assert "detection" in [call["endpoint"].split("/")[-1] for call in analysis.suggested_api_calls]
    
    @pytest.mark.asyncio
    async def test_analyze_tracking_command(self, vision_processor):
        """Test analysis of tracking commands"""
        commands = [
            "物体を追跡して",
            "ターゲットをフォローして",
            "追跡を開始して",
            "track object",
            "start following"
        ]
        
        for command in commands:
            analysis = await vision_processor.analyze_vision_command(command)
            
            assert analysis.detected_intent == "tracking"
            assert analysis.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_learning_command(self, vision_processor):
        """Test analysis of learning data collection commands"""
        commands = [
            "学習データを収集して",
            "多角度で撮影して",
            "データセットを作成して",
            "collect learning data",
            "gather training samples"
        ]
        
        for command in commands:
            analysis = await vision_processor.analyze_vision_command(command)
            
            assert analysis.detected_intent == "learning"
            assert analysis.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_parameter_extraction(self, vision_processor):
        """Test parameter extraction from commands"""
        test_cases = [
            {
                "command": "モデルID yolo_v8_person で物体を検出して",
                "expected_params": {"model_id": "yolo_v8_person"}
            },
            {
                "command": "信頼度0.8で追跡して",
                "expected_params": {"confidence": 0.8}
            },
            {
                "command": "高画質で写真を撮って",
                "expected_params": {"quality": "high"}
            },
            {
                "command": "アルゴリズム csrt で追跡開始",
                "expected_params": {"algorithm": "csrt"}
            }
        ]
        
        for case in test_cases:
            analysis = await vision_processor.analyze_vision_command(case["command"])
            
            for param, expected_value in case["expected_params"].items():
                assert param in analysis.extracted_parameters
                assert analysis.extracted_parameters[param] == expected_value
    
    @pytest.mark.asyncio
    async def test_complexity_scoring(self, vision_processor):
        """Test command complexity scoring"""
        simple_command = "写真を撮って"
        complex_command = "モデルID yolo_v8_person で信頼度0.8、アルゴリズム csrt を使って物体を検出・追跡し、学習データを多角度で収集して"
        
        simple_analysis = await vision_processor.analyze_vision_command(simple_command)
        complex_analysis = await vision_processor.analyze_vision_command(complex_command)
        
        assert simple_analysis.complexity_score < complex_analysis.complexity_score
        assert simple_analysis.complexity_score <= 1.0
        assert complex_analysis.complexity_score <= 1.0


class TestBatchVisionProcessing:
    """Test batch vision command processing"""
    
    @pytest.mark.asyncio
    async def test_sequential_batch_processing(self, vision_processor):
        """Test sequential batch processing"""
        commands = [
            "写真を撮って",
            "物体を検出して",
            "追跡を開始して"
        ]
        
        batch_request = BatchVisionCommand(
            commands=commands,
            execution_mode=ExecutionMode.SEQUENTIAL,
            error_recovery="continue"
        )
        
        result = await vision_processor.process_batch_vision_commands(batch_request)
        
        assert isinstance(result, BatchVisionResult)
        assert len(result.results) == len(commands)
        assert result.performance_metrics["total_commands"] == len(commands)
        assert result.total_execution_time > 0
    
    @pytest.mark.asyncio
    async def test_parallel_batch_processing(self, vision_processor):
        """Test parallel batch processing"""
        commands = [
            "写真を撮って",
            "ビジョン分析を表示して",
            "システム状態をチェックして"
        ]
        
        batch_request = BatchVisionCommand(
            commands=commands,
            execution_mode=ExecutionMode.PARALLEL,
            error_recovery="continue"
        )
        
        result = await vision_processor.process_batch_vision_commands(batch_request)
        
        assert isinstance(result, BatchVisionResult)
        assert len(result.results) == len(commands)
        assert result.performance_metrics["total_commands"] == len(commands)
    
    @pytest.mark.asyncio
    async def test_optimized_batch_processing(self, vision_processor):
        """Test optimized batch processing"""
        commands = [
            "物体を検出して",  # detection
            "追跡を開始して",    # tracking (depends on detection)
            "写真を撮って",      # photo (independent)
            "学習データ収集"     # learning (independent)
        ]
        
        batch_request = BatchVisionCommand(
            commands=commands,
            execution_mode=ExecutionMode.OPTIMIZED,
            optimization_enabled=True
        )
        
        result = await vision_processor.process_batch_vision_commands(batch_request)
        
        assert result.optimization_applied
        assert "grouping" in result.execution_plan
        assert "dependencies" in result.execution_plan
    
    @pytest.mark.asyncio
    async def test_batch_error_handling(self, vision_processor):
        """Test batch processing error handling"""
        # Mock backend to return error for second command
        vision_processor.backend_client._request.side_effect = [
            {"success": True},  # First command succeeds
            Exception("Network error"),  # Second command fails
            {"success": True}   # Third command succeeds
        ]
        
        commands = ["写真を撮って", "無効なコマンド", "物体を検出して"]
        
        batch_request = BatchVisionCommand(
            commands=commands,
            execution_mode=ExecutionMode.SEQUENTIAL,
            error_recovery="continue"
        )
        
        result = await vision_processor.process_batch_vision_commands(batch_request)
        
        assert not result.success  # Overall failure due to one failed command
        assert len(result.results) == len(commands)
        assert result.performance_metrics["failed_commands"] > 0


class TestVisionParameterNormalization:
    """Test vision parameter normalization"""
    
    def test_confidence_normalization(self, vision_processor):
        """Test confidence parameter normalization"""
        test_cases = [
            ("0.8", 0.8),
            ("80", 0.8),  # Percentage to decimal
            ("0.95", 0.95),
            ("invalid", 0.5)  # Default fallback
        ]
        
        for input_val, expected in test_cases:
            result = vision_processor._normalize_parameter_value("confidence", input_val)
            assert result == expected
    
    def test_quality_normalization(self, vision_processor):
        """Test quality parameter normalization"""
        test_cases = [
            ("高", "high"),
            ("中", "medium"),
            ("低", "low"),
            ("high", "high"),
            ("medium", "medium"),
            ("low", "low"),
            ("invalid", "medium")  # Default fallback
        ]
        
        for input_val, expected in test_cases:
            result = vision_processor._normalize_parameter_value("quality", input_val)
            assert result == expected
    
    def test_algorithm_normalization(self, vision_processor):
        """Test tracking algorithm normalization"""
        test_cases = [
            ("csrt", "csrt"),
            ("kcf", "kcf"),
            ("mosse", "mosse"),
            ("invalid", "csrt")  # Default fallback
        ]
        
        for input_val, expected in test_cases:
            result = vision_processor._normalize_parameter_value("algorithm", input_val)
            assert result == expected


class TestVisionCommandSuggestions:
    """Test vision command suggestion generation"""
    
    @pytest.mark.asyncio
    async def test_api_suggestions_photo(self, vision_processor):
        """Test API suggestions for photo commands"""
        intent = {"action": "photo", "confidence": 0.9}
        params = {"quality": "high", "filters": ["sharpen"]}
        
        suggestions = await vision_processor._generate_api_suggestions(intent, params)
        
        assert len(suggestions) > 0
        assert any("photo" in s["endpoint"] for s in suggestions)
        assert any("enhanced" in s["endpoint"] for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_api_suggestions_detection(self, vision_processor):
        """Test API suggestions for detection commands"""
        intent = {"action": "detection", "confidence": 0.8}
        params = {"model_id": "yolo_v8_person", "confidence": 0.7}
        
        suggestions = await vision_processor._generate_api_suggestions(intent, params)
        
        assert len(suggestions) > 0
        assert any("detection" in s["endpoint"] for s in suggestions)
        detection_suggestion = next(s for s in suggestions if "detection" in s["endpoint"])
        assert "model_id" in detection_suggestion["parameters"]
    
    @pytest.mark.asyncio
    async def test_api_suggestions_tracking(self, vision_processor):
        """Test API suggestions for tracking commands"""
        intent = {"action": "tracking", "confidence": 0.9}
        params = {"algorithm": "csrt", "confidence": 0.6}
        
        suggestions = await vision_processor._generate_api_suggestions(intent, params)
        
        assert len(suggestions) > 0
        assert any("tracking" in s["endpoint"] for s in suggestions)
        tracking_suggestion = next(s for s in suggestions if "tracking" in s["endpoint"])
        assert "algorithm" in tracking_suggestion["parameters"]


class TestVisionExecutionPlan:
    """Test vision execution plan generation"""
    
    @pytest.mark.asyncio
    async def test_execution_plan_grouping(self, vision_processor):
        """Test command grouping in execution plan"""
        analyses = [
            VisionCommandAnalysis(
                command="写真を撮って",
                detected_intent="photo",
                extracted_parameters={},
                confidence=0.9,
                suggested_api_calls=[],
                complexity_score=0.2
            ),
            VisionCommandAnalysis(
                command="物体を検出して",
                detected_intent="detection",
                extracted_parameters={},
                confidence=0.8,
                suggested_api_calls=[],
                complexity_score=0.4
            ),
            VisionCommandAnalysis(
                command="もう一枚写真を撮って",
                detected_intent="photo",
                extracted_parameters={},
                confidence=0.9,
                suggested_api_calls=[],
                complexity_score=0.2
            )
        ]
        
        plan = await vision_processor._generate_execution_plan(analyses, ExecutionMode.OPTIMIZED)
        
        assert "grouping" in plan
        assert len(plan["grouping"]) == 2  # photo and detection groups
        
        # Check that photo commands are grouped together
        photo_group = next(g for g in plan["grouping"] if g["type"] == "photo")
        assert len(photo_group["commands"]) == 2
    
    @pytest.mark.asyncio
    async def test_dependency_analysis(self, vision_processor):
        """Test dependency analysis between commands"""
        analyses = [
            VisionCommandAnalysis(
                command="物体を検出して",
                detected_intent="detection",
                extracted_parameters={},
                confidence=0.8,
                suggested_api_calls=[],
                complexity_score=0.4
            ),
            VisionCommandAnalysis(
                command="追跡を開始して",
                detected_intent="tracking",
                extracted_parameters={},
                confidence=0.9,
                suggested_api_calls=[],
                complexity_score=0.6
            )
        ]
        
        dependencies = vision_processor._analyze_dependencies(analyses)
        
        assert len(dependencies) == 1
        assert dependencies[0]["dependent"] == 1  # tracking command
        assert dependencies[0]["depends_on"] == 0  # detection command
        assert dependencies[0]["type"] == "detection_to_tracking"


class TestVisionIntegration:
    """Test integration with backend vision services"""
    
    @pytest.mark.asyncio
    async def test_backend_integration_detection(self, vision_processor, mock_backend_client):
        """Test integration with backend detection service"""
        # Mock backend response
        mock_backend_client._request.return_value = {
            "detections": [
                {
                    "label": "person",
                    "confidence": 0.92,
                    "bbox": {"x": 150, "y": 100, "width": 200, "height": 300}
                }
            ],
            "processing_time": 0.045,
            "model_id": "yolo_v8_person_detector"
        }
        
        # Simulate detection command execution
        analysis = VisionCommandAnalysis(
            command="人を検出して",
            detected_intent="detection",
            extracted_parameters={"model_id": "yolo_v8_person_detector"},
            confidence=0.9,
            suggested_api_calls=[],
            complexity_score=0.4
        )
        
        result = await vision_processor._execute_single_command(analysis)
        
        assert result["success"]
        assert result["action"] == "detection"
    
    @pytest.mark.asyncio
    async def test_vision_analytics_integration(self, vision_processor, mock_backend_client):
        """Test integration with vision analytics"""
        # Mock analytics response
        mock_backend_client._request.return_value = {
            "model_performance": {
                "yolo_v8_general": {
                    "avg_detection_count": 2.5,
                    "avg_confidence": 0.78,
                    "total_inferences": 150
                }
            },
            "tracking_statistics": {
                "total_frames": 1000,
                "successful_tracks": 850,
                "lost_tracks": 150
            },
            "learning_statistics": {
                "total_sessions": 5,
                "total_samples": 250,
                "avg_quality": 0.82
            }
        }
        
        analysis = VisionCommandAnalysis(
            command="ビジョン分析を表示して",
            detected_intent="analytics",
            extracted_parameters={},
            confidence=0.8,
            suggested_api_calls=[],
            complexity_score=0.3
        )
        
        result = await vision_processor._execute_single_command(analysis)
        
        assert result["success"]
        assert result["action"] == "analytics"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])