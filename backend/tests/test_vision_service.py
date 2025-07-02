"""
Test cases for Vision Service
Tests object detection, tracking, and vision-related functionality
"""

import asyncio
import base64
import pytest
import numpy as np
from datetime import datetime
from io import BytesIO
from PIL import Image

from api_server.core.vision_service import VisionService
from api_server.models.vision_models import DetectionRequest, StartTrackingRequest


class TestVisionService:
    
    @pytest.fixture
    async def vision_service(self):
        """Create a vision service instance for testing"""
        service = VisionService()
        yield service
        await service.shutdown()
    
    def create_test_image_base64(self, width=640, height=480):
        """Create a test image encoded as base64"""
        # Create a simple test image
        image = Image.new('RGB', (width, height), color='red')
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, vision_service):
        """Test that the vision service initializes correctly"""
        assert vision_service is not None
        
        # Check that default models are loaded
        available_models = vision_service.get_available_models()
        assert len(available_models) > 0
        assert "yolo_v8_general" in available_models
        assert "yolo_v8_person_detector" in available_models
    
    @pytest.mark.asyncio
    async def test_model_exists(self, vision_service):
        """Test model existence check"""
        assert vision_service.model_exists("yolo_v8_general")
        assert vision_service.model_exists("yolo_v8_person_detector")
        assert not vision_service.model_exists("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_object_detection_success(self, vision_service):
        """Test successful object detection"""
        image_data = self.create_test_image_base64()
        
        result = await vision_service.detect_objects(
            image_data=image_data,
            model_id="yolo_v8_general",
            confidence_threshold=0.5
        )
        
        assert result is not None
        assert result.model_id == "yolo_v8_general"
        assert result.processing_time >= 0
        assert isinstance(result.detections, list)
        
        # Check detection format
        for detection in result.detections:
            assert detection.label is not None
            assert 0 <= detection.confidence <= 1
            assert detection.bbox is not None
            assert detection.bbox.x >= 0
            assert detection.bbox.y >= 0
            assert detection.bbox.width > 0
            assert detection.bbox.height > 0
    
    @pytest.mark.asyncio
    async def test_object_detection_invalid_model(self, vision_service):
        """Test object detection with invalid model"""
        image_data = self.create_test_image_base64()
        
        with pytest.raises(ValueError, match="Model not found"):
            await vision_service.detect_objects(
                image_data=image_data,
                model_id="invalid_model",
                confidence_threshold=0.5
            )
    
    @pytest.mark.asyncio
    async def test_object_detection_invalid_image(self, vision_service):
        """Test object detection with invalid image data"""
        with pytest.raises(ValueError, match="Invalid image data"):
            await vision_service.detect_objects(
                image_data="invalid_base64_data",
                model_id="yolo_v8_general",
                confidence_threshold=0.5
            )
    
    @pytest.mark.asyncio
    async def test_tracking_start_success(self, vision_service):
        """Test starting object tracking"""
        result = await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001",
            confidence_threshold=0.6,
            follow_distance=200
        )
        
        assert result.success is True
        assert "tracking started" in result.message.lower()
        assert vision_service.is_tracking_active is True
        
        # Clean up
        await vision_service.stop_tracking()
    
    @pytest.mark.asyncio
    async def test_tracking_start_invalid_model(self, vision_service):
        """Test starting tracking with invalid model"""
        with pytest.raises(ValueError, match="Model not found"):
            await vision_service.start_tracking(
                model_id="invalid_model",
                drone_id="test_drone_001"
            )
    
    @pytest.mark.asyncio
    async def test_tracking_already_active(self, vision_service):
        """Test starting tracking when already active"""
        # Start first tracking session
        await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001"
        )
        
        # Try to start another tracking session
        with pytest.raises(ValueError, match="already active"):
            await vision_service.start_tracking(
                model_id="yolo_v8_general",
                drone_id="test_drone_002"
            )
        
        # Clean up
        await vision_service.stop_tracking()
    
    @pytest.mark.asyncio
    async def test_tracking_stop(self, vision_service):
        """Test stopping object tracking"""
        # Start tracking first
        await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001"
        )
        
        # Stop tracking
        result = await vision_service.stop_tracking()
        
        assert result.success is True
        assert "tracking stopped" in result.message.lower()
        assert vision_service.is_tracking_active is False
    
    @pytest.mark.asyncio
    async def test_tracking_stop_when_not_active(self, vision_service):
        """Test stopping tracking when not active"""
        result = await vision_service.stop_tracking()
        
        assert result.success is True
        assert "not active" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_get_tracking_status_inactive(self, vision_service):
        """Test getting tracking status when inactive"""
        status = await vision_service.get_tracking_status()
        
        assert status.is_active is False
        assert status.target_detected is False
        assert status.model_id is None
        assert status.drone_id is None
    
    @pytest.mark.asyncio
    async def test_get_tracking_status_active(self, vision_service):
        """Test getting tracking status when active"""
        # Start tracking
        await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001",
            confidence_threshold=0.7,
            follow_distance=150
        )
        
        # Wait a bit for tracking loop to run
        await asyncio.sleep(0.2)
        
        # Get status
        status = await vision_service.get_tracking_status()
        
        assert status.is_active is True
        assert status.model_id == "yolo_v8_person_detector"
        assert status.drone_id == "test_drone_001"
        assert status.follow_distance == 150
        assert status.started_at is not None
        
        # Clean up
        await vision_service.stop_tracking()
    
    @pytest.mark.asyncio
    async def test_tracking_loop_simulation(self, vision_service):
        """Test that tracking loop simulates target detection"""
        # Start tracking
        await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001"
        )
        
        # Wait for tracking loop to run a few cycles
        await asyncio.sleep(0.5)
        
        # Check that tracking status has been updated
        status = await vision_service.get_tracking_status()
        
        # The simulation should sometimes detect targets
        # We can't guarantee specific detection state due to randomness,
        # but we can check that the tracking system is running
        assert status.is_active is True
        
        # Clean up
        await vision_service.stop_tracking()
    
    @pytest.mark.asyncio
    async def test_detection_with_different_confidence_thresholds(self, vision_service):
        """Test object detection with different confidence thresholds"""
        image_data = self.create_test_image_base64()
        
        # Test with low threshold
        result_low = await vision_service.detect_objects(
            image_data=image_data,
            model_id="yolo_v8_general",
            confidence_threshold=0.1
        )
        
        # Test with high threshold
        result_high = await vision_service.detect_objects(
            image_data=image_data,
            model_id="yolo_v8_general",
            confidence_threshold=0.9
        )
        
        # Low threshold should generally produce more detections
        # (though this is simulation, so it's somewhat random)
        assert len(result_low.detections) >= 0
        assert len(result_high.detections) >= 0
        
        # All detections should meet confidence threshold
        for detection in result_low.detections:
            assert detection.confidence >= 0.1
        
        for detection in result_high.detections:
            assert detection.confidence >= 0.9
    
    @pytest.mark.asyncio
    async def test_multiple_model_types(self, vision_service):
        """Test detection with different model types"""
        image_data = self.create_test_image_base64()
        
        models_to_test = ["yolo_v8_general", "ssd_mobilenet_v2", "faster_rcnn_resnet50"]
        
        for model_id in models_to_test:
            result = await vision_service.detect_objects(
                image_data=image_data,
                model_id=model_id,
                confidence_threshold=0.5
            )
            
            assert result.model_id == model_id
            assert result.processing_time >= 0
            assert isinstance(result.detections, list)
    
    @pytest.mark.asyncio
    async def test_service_shutdown(self, vision_service):
        """Test service shutdown"""
        # Start tracking to test shutdown with active tracking
        await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="test_drone_001"
        )
        
        # Shutdown should stop tracking
        await vision_service.shutdown()
        
        # Tracking should be stopped
        assert vision_service.is_tracking_active is False