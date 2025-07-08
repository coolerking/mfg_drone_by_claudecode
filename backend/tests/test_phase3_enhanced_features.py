"""
Comprehensive Test Suite for Phase 3 Enhanced Features
Tests for enhanced drone manager, vision service, and API endpoints
"""

import asyncio
import pytest
import json
import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from PIL import Image
import numpy as np
import cv2
from io import BytesIO

from api_server.core.enhanced_drone_manager import (
    EnhancedDroneManager, FlightMode, SafetyLevel, FlightBounds, 
    SafetyConfig, FlightPlan, LearningDataCollectionConfig
)
from api_server.core.enhanced_vision_service import (
    EnhancedVisionService, VisionModel, TrackingAlgorithm, TrackingConfig
)
from api_server.models.drone_models import Drone, DroneStatus
from api_server.models.vision_models import Detection, BoundingBox
from api_server.models.common_models import SuccessResponse


class TestEnhancedDroneManager:
    """Test cases for Enhanced Drone Manager"""
    
    @pytest.fixture
    def drone_manager(self):
        """Create enhanced drone manager instance"""
        return EnhancedDroneManager()
    
    @pytest.fixture
    def sample_drone_id(self):
        """Sample drone ID for testing"""
        return "drone_001"
    
    async def test_drone_initialization(self, drone_manager):
        """Test drone manager initialization"""
        assert drone_manager is not None
        assert len(drone_manager.drone_info) == 4  # 4 dummy drones
        assert drone_manager.monitoring_active == True
        
        # Check safety config defaults
        assert drone_manager.safety_config.min_battery_level == 15
        assert drone_manager.safety_config.max_flight_time == 1200
        
    async def test_enhanced_drone_connection(self, drone_manager, sample_drone_id):
        """Test enhanced drone connection"""
        # Test connection
        result = await drone_manager.connect_drone(sample_drone_id)
        assert isinstance(result, SuccessResponse)
        assert result.success == True
        assert sample_drone_id in drone_manager.connected_drones
        
        # Check flight mode is set to manual
        assert drone_manager.flight_modes[sample_drone_id] == FlightMode.MANUAL
        
        # Test double connection failure
        with pytest.raises(ValueError, match="already connected"):
            await drone_manager.connect_drone(sample_drone_id)
    
    async def test_flight_mode_setting(self, drone_manager, sample_drone_id):
        """Test flight mode setting"""
        await drone_manager.connect_drone(sample_drone_id)
        
        # Test valid mode change
        result = await drone_manager.set_flight_mode(sample_drone_id, "auto")
        assert result.success == True
        assert drone_manager.flight_modes[sample_drone_id] == FlightMode.AUTO
        
        # Test invalid mode
        with pytest.raises(ValueError, match="Invalid flight mode"):
            await drone_manager.set_flight_mode(sample_drone_id, "invalid_mode")
    
    async def test_precise_altitude_control(self, drone_manager, sample_drone_id):
        """Test precise altitude control"""
        await drone_manager.connect_drone(sample_drone_id)
        await drone_manager.takeoff_drone(sample_drone_id)
        
        # Test valid altitude change
        result = await drone_manager.set_altitude_precise(sample_drone_id, 150, "absolute")
        assert result.success == True
        
        # Test altitude too low
        with pytest.raises(ValueError, match="Target height too low"):
            await drone_manager.set_altitude_precise(sample_drone_id, 10, "absolute")
        
        # Test altitude too high
        with pytest.raises(ValueError, match="Target height too high"):
            await drone_manager.set_altitude_precise(sample_drone_id, 600, "absolute")
    
    async def test_safety_checks(self, drone_manager, sample_drone_id):
        """Test safety check functionality"""
        await drone_manager.connect_drone(sample_drone_id)
        
        # Mock low battery
        drone_sim = drone_manager.connected_drones[sample_drone_id]
        with patch.object(drone_sim, 'get_battery_level', return_value=5):
            safety_ok = await drone_manager._check_safety(sample_drone_id, "takeoff", {})
            assert safety_ok == False
            
            # Check that violation was recorded
            violations = await drone_manager.get_safety_violations(sample_drone_id)
            assert len(violations) > 0
            assert violations[-1]["type"] == "low_battery"
    
    async def test_flight_plan_execution(self, drone_manager, sample_drone_id):
        """Test flight plan execution"""
        await drone_manager.connect_drone(sample_drone_id)
        await drone_manager.takeoff_drone(sample_drone_id)
        
        # Create simple flight plan
        flight_plan = {
            "waypoints": [(1.0, 1.0, 1.0), (2.0, 2.0, 1.5)],
            "speed": 0.5,
            "safety_checks": True
        }
        
        result = await drone_manager.execute_flight_plan(sample_drone_id, flight_plan)
        assert result.success == True
        assert drone_manager.flight_modes[sample_drone_id] == FlightMode.AUTO
        
        # Wait a bit for plan to start
        await asyncio.sleep(0.1)
        
        # Check that task is running
        assert sample_drone_id in drone_manager.active_tasks
        assert not drone_manager.active_tasks[sample_drone_id].done()
    
    async def test_learning_data_collection(self, drone_manager, sample_drone_id):
        """Test learning data collection"""
        await drone_manager.connect_drone(sample_drone_id)
        await drone_manager.takeoff_drone(sample_drone_id)
        
        # Create collection config
        config = {
            "object_name": "test_object",
            "capture_positions": ["front", "right"],
            "movement_distance": 30,
            "photos_per_position": 2,
            "altitude_levels": [100, 150],
            "rotation_angles": [0, 90]
        }
        
        # Mock camera service to avoid actual photo capture
        with patch.object(drone_manager.camera_service, 'capture_photo', 
                         return_value=Mock(id="test_photo", metadata={})):
            result = await drone_manager.collect_learning_data_enhanced(sample_drone_id, config)
            
            assert "dataset" in result
            assert "execution_summary" in result
            assert result["dataset"]["name"].startswith("test_object_dataset")
    
    async def test_enhanced_drone_status(self, drone_manager, sample_drone_id):
        """Test enhanced drone status"""
        await drone_manager.connect_drone(sample_drone_id)
        
        status = await drone_manager.get_enhanced_drone_status(sample_drone_id)
        
        assert "flight_mode" in status
        assert "active_flight_plan" in status
        assert "safety_violations_count" in status
        assert "performance_score" in status
        assert status["flight_mode"] == "manual"
        assert status["performance_score"] >= 0
    
    async def test_flight_logs(self, drone_manager, sample_drone_id):
        """Test flight logging"""
        await drone_manager.connect_drone(sample_drone_id)
        
        # Perform some operations
        await drone_manager.takeoff_drone(sample_drone_id)
        await drone_manager.move_drone(sample_drone_id, "forward", 50)
        
        # Check logs
        logs = await drone_manager.get_flight_logs(sample_drone_id, 10)
        assert len(logs) >= 3  # connection, takeoff, move
        
        # Check log structure
        for log in logs:
            assert "timestamp" in log
            assert "event_type" in log
            assert "data" in log
    
    async def test_emergency_procedures(self, drone_manager, sample_drone_id):
        """Test emergency procedures"""
        await drone_manager.connect_drone(sample_drone_id)
        await drone_manager.takeoff_drone(sample_drone_id)
        
        # Test emergency landing
        result = await drone_manager.emergency_land_drone(sample_drone_id)
        assert result.success == True
        assert drone_manager.flight_modes[sample_drone_id] == FlightMode.EMERGENCY
        
        # Check metrics updated
        metrics = drone_manager.drone_metrics[sample_drone_id]
        assert metrics.emergency_stops == 1
    
    async def test_monitoring_system(self, drone_manager, sample_drone_id):
        """Test monitoring system"""
        await drone_manager.connect_drone(sample_drone_id)
        
        # Monitoring should be active
        assert drone_manager.monitoring_active == True
        assert drone_manager.monitoring_task is not None
        
        # Test stopping monitoring
        await drone_manager.stop_monitoring()
        assert drone_manager.monitoring_active == False


class TestEnhancedVisionService:
    """Test cases for Enhanced Vision Service"""
    
    @pytest.fixture
    def vision_service(self):
        """Create enhanced vision service instance"""
        return EnhancedVisionService()
    
    @pytest.fixture
    def sample_image_data(self):
        """Create sample base64 image data"""
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    async def test_vision_service_initialization(self, vision_service):
        """Test vision service initialization"""
        assert vision_service is not None
        assert len(vision_service.models) == 6  # 6 enhanced models
        assert not vision_service.is_tracking_active
        
        # Check model availability
        models = vision_service.get_available_models()
        assert len(models) == 6
        assert any(m["id"] == "yolo_v8_general" for m in models)
    
    async def test_enhanced_object_detection(self, vision_service, sample_image_data):
        """Test enhanced object detection"""
        result = await vision_service.detect_objects_enhanced(
            sample_image_data, "yolo_v8_general", confidence_threshold=0.5
        )
        
        assert hasattr(result, 'detections')
        assert hasattr(result, 'processing_time')
        assert hasattr(result, 'model_id')
        assert result.model_id == "yolo_v8_general"
        assert result.processing_time > 0
    
    async def test_detection_with_filtering(self, vision_service, sample_image_data):
        """Test detection with label filtering"""
        result = await vision_service.detect_objects_enhanced(
            sample_image_data, 
            "yolo_v8_person_detector",
            confidence_threshold=0.3,
            filter_labels=["person"],
            max_detections=3
        )
        
        # All detections should be persons
        for detection in result.detections:
            assert detection.label == "person"
        
        # Should not exceed max detections
        assert len(result.detections) <= 3
    
    async def test_tracking_initialization(self, vision_service):
        """Test tracking initialization"""
        config = {
            "algorithm": "csrt",
            "confidence_threshold": 0.5,
            "follow_distance": 200
        }
        
        result = await vision_service.start_tracking_enhanced(
            "yolo_v8_general", "drone_001", config
        )
        
        assert result.success == True
        assert vision_service.is_tracking_active == True
        
        # Check tracking status
        status = await vision_service.get_tracking_status_enhanced()
        assert status["is_active"] == True
        assert len(status["active_sessions"]) == 1
    
    async def test_learning_session_management(self, vision_service, sample_image_data):
        """Test learning session management"""
        # Start session
        session_id = await vision_service.start_learning_session(
            "test_object", {"quality_threshold": 0.7}
        )
        
        assert session_id is not None
        assert session_id in vision_service.learning_sessions
        
        # Add sample
        annotation = {"label": "test_object", "bbox": [10, 10, 50, 50]}
        success = await vision_service.add_learning_sample(
            session_id, sample_image_data, annotation, 0.8
        )
        
        assert success == True
        
        # Finish session
        summary = await vision_service.finish_learning_session(session_id)
        
        assert "session_id" in summary
        assert "total_samples" in summary
        assert summary["total_samples"] == 1
        assert summary["average_quality"] == 0.8
    
    async def test_image_quality_calculation(self, vision_service):
        """Test image quality calculation"""
        # Create high quality image (good contrast, focus)
        img_array = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.rectangle(img_array, (100, 100), (200, 200), (255, 255, 255), -1)
        
        img = Image.fromarray(img_array)
        quality = await vision_service._calculate_image_quality(img)
        
        assert 0.0 <= quality <= 1.0
    
    async def test_model_performance_tracking(self, vision_service, sample_image_data):
        """Test model performance tracking"""
        model_id = "yolo_v8_general"
        
        # Perform multiple detections
        for _ in range(3):
            await vision_service.detect_objects_enhanced(sample_image_data, model_id)
        
        # Check performance stats
        stats = await vision_service.get_model_performance(model_id)
        
        assert "avg_detection_count" in stats
        assert "avg_confidence" in stats
        assert "total_inferences" in stats
        assert stats["total_inferences"] == 3
    
    async def test_vision_analytics(self, vision_service, sample_image_data):
        """Test comprehensive vision analytics"""
        # Generate some activity
        await vision_service.detect_objects_enhanced(sample_image_data, "yolo_v8_general")
        session_id = await vision_service.start_learning_session("test", {})
        
        analytics = await vision_service.get_vision_analytics()
        
        assert "model_performance" in analytics
        assert "tracking_statistics" in analytics
        assert "learning_statistics" in analytics
        assert "system_status" in analytics
        
        assert analytics["learning_statistics"]["total_sessions"] >= 1
        assert analytics["system_status"]["total_models"] == 6
    
    async def test_tracking_stop(self, vision_service):
        """Test tracking stop functionality"""
        # Start tracking
        await vision_service.start_tracking_enhanced("yolo_v8_general", "drone_001")
        assert vision_service.is_tracking_active == True
        
        # Stop tracking
        result = await vision_service.stop_tracking_enhanced()
        assert result.success == True
        assert vision_service.is_tracking_active == False
        
        # Check status
        status = await vision_service.get_tracking_status_enhanced()
        assert status["is_active"] == False
    
    async def test_cleanup_operations(self, vision_service):
        """Test cleanup operations"""
        # Create old session
        session_id = await vision_service.start_learning_session("old_test", {})
        session = vision_service.learning_sessions[session_id]
        
        # Manually set old timestamp
        session.start_time = datetime.now() - timedelta(hours=25)
        
        # Run cleanup
        cleaned = await vision_service.cleanup_old_sessions(24)
        
        assert cleaned == 1
        assert session_id not in vision_service.learning_sessions


class TestIntegration:
    """Integration tests for enhanced drone and vision systems"""
    
    @pytest.fixture
    def integrated_system(self):
        """Create integrated system with both services"""
        drone_manager = EnhancedDroneManager()
        vision_service = EnhancedVisionService()
        return drone_manager, vision_service
    
    async def test_integrated_learning_workflow(self, integrated_system):
        """Test complete learning data collection workflow"""
        drone_manager, vision_service = integrated_system
        drone_id = "drone_001"
        
        # Connect drone
        await drone_manager.connect_drone(drone_id)
        await drone_manager.takeoff_drone(drone_id)
        
        # Start learning session
        session_id = await vision_service.start_learning_session("integrated_test")
        
        # Configure learning collection
        config = {
            "object_name": "integrated_test",
            "capture_positions": ["front"],
            "photos_per_position": 1,
            "altitude_levels": [100]
        }
        
        # Mock camera service
        with patch.object(drone_manager.camera_service, 'capture_photo') as mock_capture:
            mock_photo = Mock()
            mock_photo.id = "test_photo_123"
            mock_photo.metadata = {}
            mock_capture.return_value = mock_photo
            
            # Execute learning data collection
            result = await drone_manager.collect_learning_data_enhanced(drone_id, config)
            
            assert result["dataset"]["image_count"] >= 1
            assert "execution_summary" in result
    
    async def test_safety_integration(self, integrated_system):
        """Test safety system integration"""
        drone_manager, vision_service = integrated_system
        drone_id = "drone_001"
        
        await drone_manager.connect_drone(drone_id)
        
        # Test safety violation during tracking
        await vision_service.start_tracking_enhanced("yolo_v8_general", drone_id)
        
        # Simulate safety violation
        drone_sim = drone_manager.connected_drones[drone_id]
        with patch.object(drone_sim, 'get_battery_level', return_value=5):
            # This should trigger safety checks and potentially stop tracking
            safety_ok = await drone_manager._check_safety(drone_id, "move", {})
            assert safety_ok == False
    
    async def test_performance_monitoring_integration(self, integrated_system):
        """Test performance monitoring across both systems"""
        drone_manager, vision_service = integrated_system
        
        # Generate some activity
        await drone_manager.connect_drone("drone_001")
        
        # Create sample image for vision testing
        img = Image.new('RGB', (640, 480), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        await vision_service.detect_objects_enhanced(img_data, "yolo_v8_general")
        
        # Check that both systems have performance data
        drone_status = await drone_manager.get_enhanced_drone_status("drone_001")
        vision_analytics = await vision_service.get_vision_analytics()
        
        assert "performance_score" in drone_status
        assert "model_performance" in vision_analytics
        
        # Check metrics are being tracked
        assert drone_status["performance_score"] >= 0


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def drone_manager(self):
        return EnhancedDroneManager()
    
    @pytest.fixture
    def vision_service(self):
        return EnhancedVisionService()
    
    async def test_invalid_drone_operations(self, drone_manager):
        """Test operations on invalid/non-existent drones"""
        invalid_id = "invalid_drone"
        
        with pytest.raises(ValueError, match="not found"):
            await drone_manager.connect_drone(invalid_id)
        
        with pytest.raises(ValueError, match="not found"):
            await drone_manager.get_enhanced_drone_status(invalid_id)
    
    async def test_invalid_vision_operations(self, vision_service):
        """Test invalid vision operations"""
        # Invalid model
        with pytest.raises(ValueError, match="Model not found"):
            await vision_service.detect_objects_enhanced("data", "invalid_model")
        
        # Invalid session
        with pytest.raises(ValueError, match="Learning session not found"):
            await vision_service.add_learning_sample("invalid_session", "data", {})
    
    async def test_malformed_image_data(self, vision_service):
        """Test handling of malformed image data"""
        with pytest.raises(ValueError, match="Invalid image data"):
            await vision_service.detect_objects_enhanced("invalid_base64", "yolo_v8_general")
    
    async def test_safety_boundary_violations(self, drone_manager):
        """Test safety boundary violations"""
        drone_id = "drone_001"
        await drone_manager.connect_drone(drone_id)
        await drone_manager.takeoff_drone(drone_id)
        
        # Try to move beyond safety boundaries
        with pytest.raises(ValueError, match="移動先が飛行境界外"):
            # Move very far (beyond default boundaries)
            await drone_manager.move_drone(drone_id, "forward", 2500)  # 25m
    
    async def test_concurrent_operations(self, drone_manager):
        """Test concurrent operation handling"""
        drone_id = "drone_001"
        await drone_manager.connect_drone(drone_id)
        await drone_manager.takeoff_drone(drone_id)
        
        # Start flight plan
        flight_plan = {"waypoints": [(1, 1, 1), (2, 2, 2)]}
        await drone_manager.execute_flight_plan(drone_id, flight_plan)
        
        # Try to start learning data collection (should handle gracefully)
        config = {"object_name": "test"}
        
        # This should either wait for the flight plan or cancel it
        result = await drone_manager.collect_learning_data_enhanced(drone_id, config)
        assert "dataset" in result


# Fixtures for API testing (if needed)
@pytest.fixture
def sample_base64_image():
    """Create a sample base64 encoded image"""
    img = Image.new('RGB', (100, 100), color='green')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


# Performance benchmarks
class TestPerformance:
    """Performance and stress tests"""
    
    async def test_detection_performance(self, vision_service=None):
        """Test detection performance benchmarks"""
        if vision_service is None:
            vision_service = EnhancedVisionService()
        
        # Create test image
        img = Image.new('RGB', (640, 480), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Benchmark detection speed
        import time
        start_time = time.time()
        
        for _ in range(10):
            await vision_service.detect_objects_enhanced(img_data, "yolo_v8_general")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should be reasonably fast (under 1 second per detection)
        assert avg_time < 1.0
    
    async def test_memory_usage(self, drone_manager=None):
        """Test memory usage during operations"""
        if drone_manager is None:
            drone_manager = EnhancedDroneManager()
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(5):
            drone_id = f"test_drone_{i}"
            if drone_id not in drone_manager.drone_info:
                # Add temporary drone for testing
                from api_server.models.drone_models import Drone
                drone_manager.drone_info[drone_id] = Drone(
                    id=drone_id, name=f"Test Drone {i}", type="test"
                )
            
            try:
                await drone_manager.connect_drone(drone_id)
                await drone_manager.takeoff_drone(drone_id)
                await drone_manager.move_drone(drone_id, "forward", 50)
                await drone_manager.land_drone(drone_id)
                await drone_manager.disconnect_drone(drone_id)
            except:
                pass  # Ignore errors in this test
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (under 50MB)
        assert memory_increase < 50 * 1024 * 1024


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])