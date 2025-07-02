"""
Test cases for Vision API endpoints
Tests vision-related HTTP endpoints and API functionality
"""

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
from api_server.api.vision import initialize_vision_router


class TestVisionAPI:
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create a test client with initialized services"""
        # Create temporary directory for datasets
        temp_dir = tempfile.mkdtemp()
        
        # Initialize services
        vision_service = VisionService()
        dataset_service = DatasetService(data_root=temp_dir)
        
        # Initialize router with services
        initialize_vision_router(vision_service, dataset_service)
        
        with TestClient(app) as test_client:
            yield test_client
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_test_image_base64(self, width=100, height=100):
        """Create a test image encoded as base64"""
        image = Image.new('RGB', (width, height), color='green')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def create_test_image_file(self, width=100, height=100):
        """Create a test image file for upload"""
        image = Image.new('RGB', (width, height), color='blue')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return ("test.jpg", buffer, "image/jpeg")
    
    # Dataset Management API Tests
    
    def test_get_datasets(self, client):
        """Test GET /api/vision/datasets"""
        response = client.get("/api/vision/datasets")
        
        assert response.status_code == 200
        datasets = response.json()
        assert isinstance(datasets, list)
        assert len(datasets) >= 3  # Sample datasets
        
        # Check dataset structure
        for dataset in datasets:
            assert "id" in dataset
            assert "name" in dataset
            assert "image_count" in dataset
            assert "labels" in dataset
            assert "created_at" in dataset
    
    def test_create_dataset(self, client):
        """Test POST /api/vision/datasets"""
        dataset_data = {
            "name": "API Test Dataset",
            "description": "A test dataset created via API"
        }
        
        response = client.post("/api/vision/datasets", json=dataset_data)
        
        assert response.status_code == 200
        dataset = response.json()
        assert dataset["name"] == "API Test Dataset"
        assert dataset["description"] == "A test dataset created via API"
        assert dataset["image_count"] == 0
        assert dataset["labels"] == []
        assert "id" in dataset
        assert "created_at" in dataset
    
    def test_create_dataset_invalid_data(self, client):
        """Test POST /api/vision/datasets with invalid data"""
        # Missing required field
        response = client.post("/api/vision/datasets", json={})
        assert response.status_code == 422
        
        # Name too long
        response = client.post("/api/vision/datasets", json={
            "name": "x" * 101,  # Max length is 100
            "description": "Test"
        })
        assert response.status_code == 422
    
    def test_get_dataset_by_id(self, client):
        """Test GET /api/vision/datasets/{dataset_id}"""
        # Use a known sample dataset
        response = client.get("/api/vision/datasets/person_detection_v1")
        
        assert response.status_code == 200
        dataset = response.json()
        assert dataset["id"] == "person_detection_v1"
        assert dataset["name"] == "Person Detection Dataset v1"
        assert "person" in dataset["labels"]
    
    def test_get_nonexistent_dataset(self, client):
        """Test GET /api/vision/datasets/{dataset_id} with nonexistent ID"""
        response = client.get("/api/vision/datasets/nonexistent_dataset")
        
        assert response.status_code == 404
        error = response.json()
        assert "見つかりません" in error["detail"]
    
    def test_delete_dataset(self, client):
        """Test DELETE /api/vision/datasets/{dataset_id}"""
        # Create a dataset first
        dataset_data = {"name": "Dataset to Delete"}
        create_response = client.post("/api/vision/datasets", json=dataset_data)
        assert create_response.status_code == 200
        dataset_id = create_response.json()["id"]
        
        # Delete the dataset
        response = client.delete(f"/api/vision/datasets/{dataset_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "deleted successfully" in result["message"].lower()
        
        # Verify it's gone
        get_response = client.get(f"/api/vision/datasets/{dataset_id}")
        assert get_response.status_code == 404
    
    def test_add_image_to_dataset(self, client):
        """Test POST /api/vision/datasets/{dataset_id}/images"""
        # Create a dataset first
        dataset_data = {"name": "Image Upload Test Dataset"}
        create_response = client.post("/api/vision/datasets", json=dataset_data)
        dataset_id = create_response.json()["id"]
        
        # Create test image file
        filename, file_data, content_type = self.create_test_image_file()
        
        # Upload image
        response = client.post(
            f"/api/vision/datasets/{dataset_id}/images",
            files={"file": (filename, file_data, content_type)},
            data={"label": "test_object"}
        )
        
        assert response.status_code == 200
        image = response.json()
        assert image["label"] == "test_object"
        assert image["dataset_id"] == dataset_id
        assert image["filename"].endswith(".jpg")
        assert "uploaded_at" in image
    
    def test_add_image_invalid_dataset(self, client):
        """Test POST /api/vision/datasets/{dataset_id}/images with invalid dataset"""
        filename, file_data, content_type = self.create_test_image_file()
        
        response = client.post(
            "/api/vision/datasets/nonexistent_dataset/images",
            files={"file": (filename, file_data, content_type)}
        )
        
        assert response.status_code == 404
    
    def test_add_invalid_file_to_dataset(self, client):
        """Test POST /api/vision/datasets/{dataset_id}/images with invalid file"""
        # Create a dataset first
        dataset_data = {"name": "Invalid File Test"}
        create_response = client.post("/api/vision/datasets", json=dataset_data)
        dataset_id = create_response.json()["id"]
        
        # Try to upload a text file
        response = client.post(
            f"/api/vision/datasets/{dataset_id}/images",
            files={"file": ("test.txt", BytesIO(b"not an image"), "text/plain")}
        )
        
        assert response.status_code == 400
    
    # Object Detection API Tests
    
    def test_object_detection_success(self, client):
        """Test POST /api/vision/detection"""
        image_data = self.create_test_image_base64()
        
        detection_request = {
            "image": image_data,
            "model_id": "yolo_v8_general",
            "confidence_threshold": 0.5
        }
        
        response = client.post("/api/vision/detection", json=detection_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["model_id"] == "yolo_v8_general"
        assert result["processing_time"] >= 0
        assert "detections" in result
        
        # Check detection structure
        for detection in result["detections"]:
            assert "label" in detection
            assert "confidence" in detection
            assert "bbox" in detection
            assert 0 <= detection["confidence"] <= 1
    
    def test_object_detection_invalid_model(self, client):
        """Test POST /api/vision/detection with invalid model"""
        image_data = self.create_test_image_base64()
        
        detection_request = {
            "image": image_data,
            "model_id": "nonexistent_model",
            "confidence_threshold": 0.5
        }
        
        response = client.post("/api/vision/detection", json=detection_request)
        
        assert response.status_code == 404
        error = response.json()
        assert "見つかりません" in error["detail"]
    
    def test_object_detection_invalid_image(self, client):
        """Test POST /api/vision/detection with invalid image"""
        detection_request = {
            "image": "invalid_base64_data",
            "model_id": "yolo_v8_general",
            "confidence_threshold": 0.5
        }
        
        response = client.post("/api/vision/detection", json=detection_request)
        
        assert response.status_code == 400
        error = response.json()
        assert "無効" in error["detail"]
    
    def test_object_detection_validation(self, client):
        """Test POST /api/vision/detection with validation errors"""
        # Missing required fields
        response = client.post("/api/vision/detection", json={})
        assert response.status_code == 422
        
        # Invalid confidence threshold
        response = client.post("/api/vision/detection", json={
            "image": self.create_test_image_base64(),
            "model_id": "yolo_v8_general",
            "confidence_threshold": 1.5  # > 1.0
        })
        assert response.status_code == 422
    
    # Object Tracking API Tests
    
    def test_start_tracking_success(self, client):
        """Test POST /api/vision/tracking/start"""
        tracking_request = {
            "model_id": "yolo_v8_person_detector",
            "drone_id": "test_drone_001",
            "confidence_threshold": 0.6,
            "follow_distance": 200
        }
        
        response = client.post("/api/vision/tracking/start", json=tracking_request)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "tracking started" in result["message"].lower()
        
        # Clean up - stop tracking
        client.post("/api/vision/tracking/stop")
    
    def test_start_tracking_invalid_model(self, client):
        """Test POST /api/vision/tracking/start with invalid model"""
        tracking_request = {
            "model_id": "nonexistent_model",
            "drone_id": "test_drone_001"
        }
        
        response = client.post("/api/vision/tracking/start", json=tracking_request)
        
        assert response.status_code == 404
        error = response.json()
        assert "見つかりません" in error["detail"]
    
    def test_start_tracking_already_active(self, client):
        """Test POST /api/vision/tracking/start when already active"""
        tracking_request = {
            "model_id": "yolo_v8_person_detector",
            "drone_id": "test_drone_001"
        }
        
        # Start first tracking session
        response1 = client.post("/api/vision/tracking/start", json=tracking_request)
        assert response1.status_code == 200
        
        # Try to start another session
        response2 = client.post("/api/vision/tracking/start", json=tracking_request)
        assert response2.status_code == 409
        error = response2.json()
        assert "既に" in error["detail"]
        
        # Clean up
        client.post("/api/vision/tracking/stop")
    
    def test_stop_tracking(self, client):
        """Test POST /api/vision/tracking/stop"""
        # Start tracking first
        tracking_request = {
            "model_id": "yolo_v8_person_detector",
            "drone_id": "test_drone_001"
        }
        client.post("/api/vision/tracking/start", json=tracking_request)
        
        # Stop tracking
        response = client.post("/api/vision/tracking/stop")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "tracking stopped" in result["message"].lower()
    
    def test_stop_tracking_when_not_active(self, client):
        """Test POST /api/vision/tracking/stop when not active"""
        response = client.post("/api/vision/tracking/stop")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "not active" in result["message"].lower()
    
    def test_get_tracking_status_inactive(self, client):
        """Test GET /api/vision/tracking/status when inactive"""
        response = client.get("/api/vision/tracking/status")
        
        assert response.status_code == 200
        status = response.json()
        assert status["is_active"] is False
        assert status["target_detected"] is False
        assert status["model_id"] is None
        assert status["drone_id"] is None
    
    def test_get_tracking_status_active(self, client):
        """Test GET /api/vision/tracking/status when active"""
        # Start tracking
        tracking_request = {
            "model_id": "yolo_v8_person_detector",
            "drone_id": "test_drone_001",
            "confidence_threshold": 0.7,
            "follow_distance": 150
        }
        client.post("/api/vision/tracking/start", json=tracking_request)
        
        # Get status
        response = client.get("/api/vision/tracking/status")
        
        assert response.status_code == 200
        status = response.json()
        assert status["is_active"] is True
        assert status["model_id"] == "yolo_v8_person_detector"
        assert status["drone_id"] == "test_drone_001"
        assert status["follow_distance"] == 150
        assert "started_at" in status
        
        # Clean up
        client.post("/api/vision/tracking/stop")
    
    def test_tracking_validation(self, client):
        """Test tracking API validation"""
        # Invalid confidence threshold
        response = client.post("/api/vision/tracking/start", json={
            "model_id": "yolo_v8_general",
            "drone_id": "test_drone",
            "confidence_threshold": -0.1  # < 0
        })
        assert response.status_code == 422
        
        # Invalid follow distance
        response = client.post("/api/vision/tracking/start", json={
            "model_id": "yolo_v8_general",
            "drone_id": "test_drone",
            "follow_distance": 10  # < 50
        })
        assert response.status_code == 422
    
    # Edge Cases and Error Handling
    
    def test_invalid_dataset_id_format(self, client):
        """Test endpoints with invalid dataset ID format"""
        # Test with invalid characters
        response = client.get("/api/vision/datasets/invalid@id")
        assert response.status_code == 422
        
        response = client.delete("/api/vision/datasets/invalid@id")
        assert response.status_code == 422
    
    def test_empty_image_upload(self, client):
        """Test uploading empty image file"""
        # Create a dataset first
        dataset_data = {"name": "Empty File Test"}
        create_response = client.post("/api/vision/datasets", json=dataset_data)
        dataset_id = create_response.json()["id"]
        
        # Try to upload empty file
        response = client.post(
            f"/api/vision/datasets/{dataset_id}/images",
            files={"file": ("empty.jpg", BytesIO(b""), "image/jpeg")}
        )
        
        assert response.status_code == 400
    
    def test_detection_with_different_confidence_thresholds(self, client):
        """Test detection with various confidence thresholds"""
        image_data = self.create_test_image_base64()
        
        thresholds = [0.1, 0.5, 0.9]
        for threshold in thresholds:
            response = client.post("/api/vision/detection", json={
                "image": image_data,
                "model_id": "yolo_v8_general",
                "confidence_threshold": threshold
            })
            
            assert response.status_code == 200
            result = response.json()
            
            # All detections should meet the threshold
            for detection in result["detections"]:
                assert detection["confidence"] >= threshold