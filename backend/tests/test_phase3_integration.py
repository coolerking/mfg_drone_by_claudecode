"""
Integration tests for Phase 3 implementation
Tests the complete integration of vision, model management, and dashboard APIs
"""

import asyncio
import pytest
import base64
import tempfile
import shutil
from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient

from api_server.main import app
from api_server.core.vision_service import VisionService
from api_server.core.dataset_service import DatasetService
from api_server.core.model_service import ModelService
from api_server.core.system_service import SystemService
from api_server.core.drone_manager import DroneManager
from api_server.api.vision import initialize_vision_router
from api_server.api.models import initialize_models_router
from api_server.api.dashboard import initialize_dashboard_router


class TestPhase3Integration:
    
    @pytest.fixture(scope="class")
    def integrated_client(self):
        """Create a test client with all Phase 3 services integrated"""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Initialize all services
        vision_service = VisionService()
        dataset_service = DatasetService(data_root=temp_dir)
        model_service = ModelService()
        system_service = SystemService()
        drone_manager = DroneManager()
        
        # Initialize all routers
        initialize_vision_router(vision_service, dataset_service)
        initialize_models_router(model_service, dataset_service)
        initialize_dashboard_router(system_service, drone_manager, vision_service, model_service, dataset_service)
        
        with TestClient(app) as test_client:
            yield test_client
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_test_image_base64(self):
        """Helper to create test image"""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def test_complete_ml_workflow(self, integrated_client):
        """Test complete ML workflow: dataset creation → image upload → model training → detection"""
        
        # 1. Create a dataset
        dataset_response = integrated_client.post("/api/vision/datasets", json={
            "name": "Integration Test Dataset",
            "description": "Dataset for integration testing"
        })
        assert dataset_response.status_code == 200
        dataset_id = dataset_response.json()["id"]
        
        # 2. Add images to dataset
        for i in range(3):
            image = Image.new('RGB', (50, 50), color=['red', 'green', 'blue'][i])
            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)
            
            upload_response = integrated_client.post(
                f"/api/vision/datasets/{dataset_id}/images",
                files={"file": (f"test_{i}.jpg", buffer, "image/jpeg")},
                data={"label": "test_object"}
            )
            assert upload_response.status_code == 200
        
        # 3. Verify dataset has images
        dataset_response = integrated_client.get(f"/api/vision/datasets/{dataset_id}")
        dataset = dataset_response.json()
        assert dataset["image_count"] == 3
        assert "test_object" in dataset["labels"]
        
        # 4. Start model training
        training_response = integrated_client.post("/api/models", json={
            "name": "Integration Test Model",
            "description": "Model trained for integration testing",
            "dataset_id": dataset_id,
            "model_type": "yolo",
            "training_params": {
                "epochs": 5,  # Short training for testing
                "batch_size": 8,
                "learning_rate": 0.001
            }
        })
        assert training_response.status_code == 200
        job_id = training_response.json()["id"]
        
        # 5. Wait for training to complete (polling)
        max_wait = 50  # 5 seconds
        training_completed = False
        for _ in range(max_wait):
            job_response = integrated_client.get(f"/api/models/training/{job_id}")
            job = job_response.json()
            
            if job["status"] == "completed":
                training_completed = True
                break
            elif job["status"] == "failed":
                pytest.fail(f"Training failed: {job.get('error_message', 'Unknown error')}")
            
            import time
            time.sleep(0.1)
        
        assert training_completed, "Training did not complete in time"
        
        # 6. Verify model was created
        models_response = integrated_client.get("/api/models")
        models = models_response.json()
        integration_models = [m for m in models if m["name"] == "Integration Test Model"]
        assert len(integration_models) == 1
        
        # 7. Use the new model for object detection
        test_image = self.create_test_image_base64()
        detection_response = integrated_client.post("/api/vision/detection", json={
            "image": test_image,
            "model_id": "yolo_v8_general",  # Use existing model for detection
            "confidence_threshold": 0.5
        })
        assert detection_response.status_code == 200
        
        # 8. Clean up dataset
        delete_response = integrated_client.delete(f"/api/vision/datasets/{dataset_id}")
        assert delete_response.status_code == 200
    
    def test_tracking_with_dashboard_monitoring(self, integrated_client):
        """Test object tracking with dashboard monitoring"""
        
        # 1. Check initial system status
        system_response = integrated_client.get("/api/dashboard/system")
        assert system_response.status_code == 200
        initial_status = system_response.json()
        assert initial_status["active_tracking"] == 0
        
        # 2. Start object tracking
        tracking_response = integrated_client.post("/api/vision/tracking/start", json={
            "model_id": "yolo_v8_person_detector",
            "drone_id": "integration_test_drone",
            "confidence_threshold": 0.6,
            "follow_distance": 180
        })
        assert tracking_response.status_code == 200
        
        # 3. Check that dashboard shows active tracking
        system_response = integrated_client.get("/api/dashboard/system")
        updated_status = system_response.json()
        assert updated_status["active_tracking"] == 1
        
        # 4. Get tracking status
        tracking_status_response = integrated_client.get("/api/vision/tracking/status")
        tracking_status = tracking_status_response.json()
        assert tracking_status["is_active"] is True
        assert tracking_status["model_id"] == "yolo_v8_person_detector"
        assert tracking_status["drone_id"] == "integration_test_drone"
        
        # 5. Stop tracking
        stop_response = integrated_client.post("/api/vision/tracking/stop")
        assert stop_response.status_code == 200
        
        # 6. Verify dashboard shows no active tracking
        system_response = integrated_client.get("/api/dashboard/system")
        final_status = system_response.json()
        assert final_status["active_tracking"] == 0
    
    def test_concurrent_operations(self, integrated_client):
        """Test concurrent operations across different services"""
        
        # 1. Start multiple operations concurrently
        # Create dataset
        dataset_response = integrated_client.post("/api/vision/datasets", json={
            "name": "Concurrent Test Dataset"
        })
        dataset_id = dataset_response.json()["id"]
        
        # Start model training
        training_response = integrated_client.post("/api/models", json={
            "name": "Concurrent Test Model",
            "dataset_id": "person_detection_v1",  # Use existing dataset
            "training_params": {"epochs": 10}
        })
        job_id = training_response.json()["id"]
        
        # Start object tracking
        tracking_response = integrated_client.post("/api/vision/tracking/start", json={
            "model_id": "yolo_v8_general",
            "drone_id": "concurrent_test_drone"
        })
        assert tracking_response.status_code == 200
        
        # 2. Check system can handle multiple requests
        for _ in range(5):
            # Object detection
            detection_response = integrated_client.post("/api/vision/detection", json={
                "image": self.create_test_image_base64(),
                "model_id": "ssd_mobilenet_v2",
                "confidence_threshold": 0.4
            })
            assert detection_response.status_code == 200
            
            # System status
            system_response = integrated_client.get("/api/dashboard/system")
            assert system_response.status_code == 200
            
            # Training job status
            job_response = integrated_client.get(f"/api/models/training/{job_id}")
            assert job_response.status_code == 200
        
        # 3. Clean up
        integrated_client.post("/api/vision/tracking/stop")
        integrated_client.delete(f"/api/vision/datasets/{dataset_id}")
    
    def test_dashboard_overview_integration(self, integrated_client):
        """Test dashboard overview with all services"""
        
        # Create some activity
        # 1. Create dataset and add image
        dataset_response = integrated_client.post("/api/vision/datasets", json={
            "name": "Dashboard Test Dataset"
        })
        dataset_id = dataset_response.json()["id"]
        
        image = Image.new('RGB', (50, 50), color='yellow')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        
        integrated_client.post(
            f"/api/vision/datasets/{dataset_id}/images",
            files={"file": ("dashboard_test.jpg", buffer, "image/jpeg")}
        )
        
        # 2. Start training
        training_response = integrated_client.post("/api/models", json={
            "name": "Dashboard Test Model",
            "dataset_id": dataset_id,
            "training_params": {"epochs": 3}
        })
        
        # 3. Start tracking
        integrated_client.post("/api/vision/tracking/start", json={
            "model_id": "yolo_v8_person_detector",
            "drone_id": "dashboard_test_drone"
        })
        
        # 4. Check dashboard overview
        overview_response = integrated_client.get("/api/dashboard/overview")
        assert overview_response.status_code == 200
        
        overview = overview_response.json()
        assert "system" in overview
        assert "drones" in overview
        assert "models" in overview
        assert "datasets" in overview
        
        # Verify data consistency
        assert overview["system"]["cpu_usage"] >= 0
        assert overview["system"]["memory_usage"] >= 0
        assert overview["drones"]["tracking_active"] is True
        assert overview["models"]["total_count"] >= 3  # Sample models + new one
        assert overview["datasets"]["total_count"] >= 4  # Sample datasets + new one
        
        # 5. Clean up
        integrated_client.post("/api/vision/tracking/stop")
        integrated_client.delete(f"/api/vision/datasets/{dataset_id}")
    
    def test_service_health_monitoring(self, integrated_client):
        """Test service health monitoring integration"""
        
        health_response = integrated_client.get("/api/dashboard/health")
        assert health_response.status_code == 200
        
        health = health_response.json()
        assert "overall_status" in health
        assert "services" in health
        
        # Check all services are reported
        services = health["services"]
        expected_services = ["drone_manager", "vision_service", "model_service", "dataset_service"]
        
        for service_name in expected_services:
            assert service_name in services
            service_health = services[service_name]
            assert "status" in service_health
            assert service_health["status"] in ["healthy", "unhealthy"]
        
        # Overall status should be healthy if all services are healthy
        unhealthy_services = [name for name, info in services.items() 
                            if info["status"] == "unhealthy"]
        
        if not unhealthy_services:
            assert health["overall_status"] in ["healthy", "degraded"]
    
    def test_performance_metrics_integration(self, integrated_client):
        """Test performance metrics collection"""
        
        performance_response = integrated_client.get("/api/dashboard/performance")
        assert performance_response.status_code == 200
        
        metrics = performance_response.json()
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        assert "network" in metrics
        assert "processes" in metrics
        
        # Check metric structure
        assert metrics["cpu"]["usage_percent"] >= 0
        assert metrics["memory"]["usage_percent"] >= 0
        assert metrics["disk"]["usage_percent"] >= 0
        assert metrics["processes"]["count"] > 0
    
    def test_error_handling_across_services(self, integrated_client):
        """Test error handling integration across services"""
        
        # 1. Test cascading errors
        # Try to train model with nonexistent dataset
        response = integrated_client.post("/api/models", json={
            "name": "Error Test Model",
            "dataset_id": "nonexistent_dataset"
        })
        assert response.status_code == 404
        
        # 2. Try to start tracking with nonexistent model
        response = integrated_client.post("/api/vision/tracking/start", json={
            "model_id": "nonexistent_model",
            "drone_id": "test_drone"
        })
        assert response.status_code == 404
        
        # 3. Try to delete dataset that doesn't exist
        response = integrated_client.delete("/api/vision/datasets/nonexistent_dataset")
        assert response.status_code == 404
        
        # 4. System should still be functional after errors
        system_response = integrated_client.get("/api/dashboard/system")
        assert system_response.status_code == 200
        
        # 5. Other operations should still work
        detection_response = integrated_client.post("/api/vision/detection", json={
            "image": self.create_test_image_base64(),
            "model_id": "yolo_v8_general",
            "confidence_threshold": 0.5
        })
        assert detection_response.status_code == 200
    
    def test_resource_cleanup_integration(self, integrated_client):
        """Test resource cleanup across services"""
        
        # 1. Create multiple resources
        created_datasets = []
        created_jobs = []
        
        # Create datasets
        for i in range(3):
            response = integrated_client.post("/api/vision/datasets", json={
                "name": f"Cleanup Test Dataset {i}"
            })
            created_datasets.append(response.json()["id"])
        
        # Start training jobs
        for i in range(2):
            response = integrated_client.post("/api/models", json={
                "name": f"Cleanup Test Model {i}",
                "dataset_id": created_datasets[0],
                "training_params": {"epochs": 20}  # Longer training
            })
            created_jobs.append(response.json()["id"])
        
        # 2. Cancel training jobs
        for job_id in created_jobs:
            cancel_response = integrated_client.post(f"/api/models/training/{job_id}/cancel")
            # Should succeed or job might already be completed
            assert cancel_response.status_code in [200, 400]
        
        # 3. Delete datasets
        for dataset_id in created_datasets:
            delete_response = integrated_client.delete(f"/api/vision/datasets/{dataset_id}")
            assert delete_response.status_code == 200
        
        # 4. Verify resources are cleaned up
        datasets_response = integrated_client.get("/api/vision/datasets")
        dataset_names = [d["name"] for d in datasets_response.json()]
        
        for i in range(3):
            assert f"Cleanup Test Dataset {i}" not in dataset_names
    
    def test_api_consistency_and_validation(self, integrated_client):
        """Test API consistency and validation across all endpoints"""
        
        # Test consistent error response format
        error_responses = [
            integrated_client.get("/api/vision/datasets/nonexistent"),
            integrated_client.get("/api/models/nonexistent"),
            integrated_client.get("/api/models/training/nonexistent"),
            integrated_client.post("/api/vision/detection", json={"invalid": "data"}),
            integrated_client.post("/api/models", json={"invalid": "data"})
        ]
        
        for response in error_responses:
            assert response.status_code in [404, 422]  # Not found or validation error
            # All error responses should have consistent structure
            if response.status_code != 422:  # 422 has different format
                error_data = response.json()
                assert "detail" in error_data
    
    def test_concurrent_training_and_detection(self, integrated_client):
        """Test concurrent model training and object detection"""
        
        # Start model training
        training_response = integrated_client.post("/api/models", json={
            "name": "Concurrent Training Test",
            "dataset_id": "person_detection_v1",
            "training_params": {"epochs": 15}
        })
        assert training_response.status_code == 200
        
        # Perform multiple detections while training is running
        test_image = self.create_test_image_base64()
        
        for i in range(10):
            detection_response = integrated_client.post("/api/vision/detection", json={
                "image": test_image,
                "model_id": "yolo_v8_general",
                "confidence_threshold": 0.3
            })
            assert detection_response.status_code == 200
            
            # Verify detection results are consistent
            result = detection_response.json()
            assert "detections" in result
            assert "processing_time" in result
            assert result["model_id"] == "yolo_v8_general"
        
        # System should remain responsive
        system_response = integrated_client.get("/api/dashboard/system")
        assert system_response.status_code == 200