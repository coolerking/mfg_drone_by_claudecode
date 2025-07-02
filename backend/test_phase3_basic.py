#!/usr/bin/env python3
"""
Basic test script to verify Phase 3 implementation
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """Test that all Phase 3 modules can be imported"""
    try:
        # Test model imports
        from api_server.models.vision_models import (
            Detection, DetectionResult, Dataset, BoundingBox,
            CreateDatasetRequest, DatasetImage, StartTrackingRequest, TrackingStatus
        )
        from api_server.models.model_models import (
            Model, TrainingJob, TrainModelRequest, TrainingParams, SystemStatus
        )
        print("✅ All Phase 3 model imports successful")
        
        # Test service imports
        from api_server.core.vision_service import VisionService
        from api_server.core.dataset_service import DatasetService  
        from api_server.core.model_service import ModelService
        from api_server.core.system_service import SystemService
        print("✅ All Phase 3 service imports successful")
        
        # Test API imports
        from api_server.api.vision import router as vision_router
        from api_server.api.models import router as models_router
        from api_server.api.dashboard import router as dashboard_router
        print("✅ All Phase 3 API router imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_service_initialization():
    """Test basic service initialization"""
    try:
        from api_server.core.vision_service import VisionService
        from api_server.core.dataset_service import DatasetService
        from api_server.core.model_service import ModelService
        from api_server.core.system_service import SystemService
        
        # Test vision service
        vision_service = VisionService()
        available_models = vision_service.get_available_models()
        print(f"✅ Vision service initialized with {len(available_models)} models")
        print(f"   Available models: {available_models}")
        
        # Test dataset service
        dataset_service = DatasetService()
        print("✅ Dataset service initialized")
        
        # Test model service  
        model_service = ModelService()
        print("✅ Model service initialized")
        
        # Test system service
        system_service = SystemService()
        print("✅ System service initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_models():
    """Test that Pydantic models work correctly"""
    try:
        from api_server.models.vision_models import BoundingBox, Detection, DetectionResult
        from api_server.models.model_models import TrainingParams, SystemStatus
        from datetime import datetime
        
        # Test BoundingBox
        bbox = BoundingBox(x=100.0, y=50.0, width=150.0, height=200.0)
        print(f"✅ BoundingBox model: {bbox}")
        
        # Test Detection
        detection = Detection(
            label="person",
            confidence=0.85,
            bbox=bbox
        )
        print(f"✅ Detection model: {detection}")
        
        # Test DetectionResult
        result = DetectionResult(
            detections=[detection],
            processing_time=0.25,
            model_id="test_model"
        )
        print(f"✅ DetectionResult model: {result}")
        
        # Test TrainingParams
        params = TrainingParams(
            epochs=100,
            batch_size=16,
            learning_rate=0.001,
            validation_split=0.2
        )
        print(f"✅ TrainingParams model: {params}")
        
        # Test SystemStatus
        status = SystemStatus(
            cpu_usage=45.2,
            memory_usage=67.8,
            disk_usage=23.1,
            connected_drones=3,
            active_tracking=1,
            running_training_jobs=2,
            uptime=86400,
            last_updated=datetime.now()
        )
        print(f"✅ SystemStatus model: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests"""
    print("🚀 Starting Phase 3 basic tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Service Initialization Tests", test_service_initialization), 
        ("Data Model Tests", test_data_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 3 basic tests passed! Implementation is ready.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)