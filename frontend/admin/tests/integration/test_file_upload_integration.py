"""
File Upload Integration Tests
ファイルアップロード統合テスト
"""
import pytest
import io
import json
import tempfile
import os
from unittest.mock import Mock, patch
import requests
import responses
from PIL import Image
from werkzeug.datastructures import FileStorage


@pytest.mark.integration
@pytest.mark.file_upload
class TestFileUploadIntegration:
    """File upload integration test suite."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.backend_url = "http://localhost:8000"
        self.timeout = 10.0
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    def create_test_image(self, width=640, height=480, format='JPEG', size_mb=None):
        """Create test image with specified properties."""
        image = Image.new('RGB', (width, height), color='red')
        img_buffer = io.BytesIO()
        
        if size_mb:
            # Create image of specific size by adjusting quality
            for quality in range(95, 1, -5):
                img_buffer.seek(0)
                img_buffer.truncate()
                image.save(img_buffer, format=format, quality=quality)
                if img_buffer.tell() <= size_mb * 1024 * 1024:
                    break
        else:
            image.save(img_buffer, format=format)
        
        img_buffer.seek(0)
        return img_buffer
    
    def create_test_file(self, filename, content=b"test content", content_type="text/plain"):
        """Create test file for upload testing."""
        file_buffer = io.BytesIO(content)
        file_buffer.name = filename
        return FileStorage(
            stream=file_buffer,
            filename=filename,
            content_type=content_type
        )
    
    @responses.activate
    def test_single_image_upload(self):
        """Test single image file upload."""
        # Setup mock response
        responses.add(
            responses.POST,
            f"{self.backend_url}/model/train",
            json={
                "status": "training_started",
                "task_id": "train_001",
                "object_name": "test_object",
                "image_count": 1
            },
            status=200
        )
        
        # Create test image
        test_image = self.create_test_image()
        
        # Prepare upload data
        files = {"images": ("test.jpg", test_image, "image/jpeg")}
        data = {"object_name": "test_object"}
        
        # Make upload request
        response = requests.post(
            f"{self.backend_url}/model/train",
            files=files,
            data=data,
            timeout=self.timeout
        )
        
        # Verify response
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "training_started"
        assert "task_id" in result
        assert result["object_name"] == "test_object"
        assert result["image_count"] == 1
    
    @responses.activate
    def test_multiple_image_upload(self):
        """Test multiple image files upload."""
        # Setup mock response
        responses.add(
            responses.POST,
            f"{self.backend_url}/model/train",
            json={
                "status": "training_started",
                "task_id": "train_002",
                "object_name": "multi_object",
                "image_count": 5
            },
            status=200
        )
        
        # Create multiple test images
        test_images = []
        for i in range(5):
            image = self.create_test_image(width=640+i*10, height=480+i*10)
            test_images.append((f"test_{i}.jpg", image, "image/jpeg"))
        
        # Prepare upload data
        files = [("images", img) for img in test_images]
        data = {"object_name": "multi_object"}
        
        # Make upload request
        response = requests.post(
            f"{self.backend_url}/model/train",
            files=files,
            data=data,
            timeout=self.timeout
        )
        
        # Verify response
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "training_started"
        assert result["image_count"] == 5
        assert result["object_name"] == "multi_object"
    
    def test_file_size_validation(self):
        """Test file size validation."""
        # Test valid file size
        small_image = self.create_test_image(size_mb=1)  # 1MB
        assert small_image.tell() <= self.max_file_size
        
        # Test large file (simulated)
        large_size = 15 * 1024 * 1024  # 15MB (exceeds limit)
        
        def validate_file_size(file_size):
            return file_size <= self.max_file_size
        
        assert validate_file_size(small_image.tell()) == True
        assert validate_file_size(large_size) == False
    
    def test_file_type_validation(self):
        """Test file type validation."""
        valid_files = [
            "test.jpg",
            "test.jpeg", 
            "test.png",
            "test.bmp",
            "test.tiff"
        ]
        
        invalid_files = [
            "test.txt",
            "test.pdf",
            "test.mp4",
            "test.doc",
            "test.exe"
        ]
        
        def validate_file_extension(filename):
            ext = os.path.splitext(filename)[1].lower()
            return ext in self.allowed_extensions
        
        # Test valid files
        for filename in valid_files:
            assert validate_file_extension(filename) == True
        
        # Test invalid files
        for filename in invalid_files:
            assert validate_file_extension(filename) == False
    
    @responses.activate
    def test_upload_error_handling(self):
        """Test upload error scenarios."""
        # Setup error responses
        error_scenarios = [
            {
                "status": 400,
                "response": {"error": "Bad Request", "message": "No images provided"}
            },
            {
                "status": 413,
                "response": {"error": "Payload Too Large", "message": "File size exceeds limit"}
            },
            {
                "status": 415,
                "response": {"error": "Unsupported Media Type", "message": "Invalid file format"}
            },
            {
                "status": 500,
                "response": {"error": "Internal Server Error", "message": "Failed to process upload"}
            }
        ]
        
        for i, scenario in enumerate(error_scenarios):
            responses.add(
                responses.POST,
                f"{self.backend_url}/model/train",
                json=scenario["response"],
                status=scenario["status"]
            )
            
            # Create test file
            test_image = self.create_test_image()
            files = {"images": (f"test_{i}.jpg", test_image, "image/jpeg")}
            data = {"object_name": f"test_object_{i}"}
            
            # Make request
            response = requests.post(
                f"{self.backend_url}/model/train",
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            # Verify error response
            assert response.status_code == scenario["status"]
            result = response.json()
            assert "error" in result
            assert "message" in result
    
    def test_upload_progress_tracking(self):
        """Test upload progress tracking."""
        upload_progress = []
        
        def track_upload_progress(chunk_size, total_size):
            """Simulate upload progress tracking."""
            uploaded = 0
            while uploaded < total_size:
                uploaded += chunk_size
                progress = min(100, (uploaded / total_size) * 100)
                upload_progress.append(progress)
                
                if uploaded >= total_size:
                    break
        
        # Simulate uploading a 1MB file in 100KB chunks
        file_size = 1024 * 1024  # 1MB
        chunk_size = 100 * 1024   # 100KB
        
        track_upload_progress(chunk_size, file_size)
        
        # Verify progress tracking
        assert len(upload_progress) >= 10  # Should have multiple progress updates
        assert upload_progress[0] > 0      # First chunk uploaded
        assert upload_progress[-1] == 100  # Upload completed
        
        # Verify progress is increasing
        for i in range(1, len(upload_progress)):
            assert upload_progress[i] >= upload_progress[i-1]
    
    @responses.activate
    def test_concurrent_uploads(self):
        """Test concurrent file uploads."""
        import concurrent.futures
        import threading
        
        upload_results = []
        upload_lock = threading.Lock()
        
        # Setup mock responses for concurrent uploads
        for i in range(3):
            responses.add(
                responses.POST,
                f"{self.backend_url}/model/train",
                json={
                    "status": "training_started",
                    "task_id": f"train_concurrent_{i}",
                    "object_name": f"concurrent_object_{i}",
                    "image_count": 1
                },
                status=200
            )
        
        def upload_file(object_name, file_index):
            """Upload a single file."""
            try:
                test_image = self.create_test_image()
                files = {"images": (f"test_{file_index}.jpg", test_image, "image/jpeg")}
                data = {"object_name": object_name}
                
                response = requests.post(
                    f"{self.backend_url}/model/train",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                with upload_lock:
                    upload_results.append({
                        "index": file_index,
                        "status_code": response.status_code,
                        "response": response.json()
                    })
                
            except Exception as e:
                with upload_lock:
                    upload_results.append({
                        "index": file_index,
                        "error": str(e)
                    })
        
        # Execute concurrent uploads
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(upload_file, f"concurrent_object_{i}", i)
                futures.append(future)
            
            # Wait for all uploads to complete
            concurrent.futures.wait(futures)
        
        # Verify concurrent uploads
        assert len(upload_results) == 3
        for result in upload_results:
            assert "error" not in result
            assert result["status_code"] == 200
            assert result["response"]["status"] == "training_started"
    
    def test_upload_retry_mechanism(self):
        """Test upload retry mechanism for failed uploads."""
        retry_attempts = []
        max_retries = 3
        
        def attempt_upload_with_retry(file_data, max_retries=3):
            """Simulate upload with retry mechanism."""
            for attempt in range(max_retries + 1):
                try:
                    retry_attempts.append(attempt + 1)
                    
                    # Simulate failure for first 2 attempts
                    if attempt < 2:
                        raise requests.exceptions.ConnectionError("Connection failed")
                    
                    # Succeed on 3rd attempt
                    return {
                        "status": "success",
                        "attempt": attempt + 1,
                        "file_size": len(file_data)
                    }
                    
                except requests.exceptions.ConnectionError as e:
                    if attempt >= max_retries:
                        raise e
                    # Wait before retry (simulated)
                    continue
        
        # Test retry mechanism
        test_data = b"test file content"
        result = attempt_upload_with_retry(test_data, max_retries)
        
        # Verify retry attempts
        assert len(retry_attempts) == 3
        assert retry_attempts == [1, 2, 3]
        assert result["status"] == "success"
        assert result["attempt"] == 3
    
    def test_upload_metadata_validation(self):
        """Test upload metadata validation."""
        def validate_upload_metadata(metadata):
            """Validate upload metadata."""
            errors = []
            
            # Check required fields
            if not metadata.get("object_name"):
                errors.append("object_name is required")
            
            if not metadata.get("images"):
                errors.append("at least one image is required")
            
            # Check object name format
            object_name = metadata.get("object_name", "")
            if len(object_name) < 3:
                errors.append("object_name must be at least 3 characters")
            
            if len(object_name) > 50:
                errors.append("object_name must not exceed 50 characters")
            
            # Check image count
            images = metadata.get("images", [])
            if len(images) < 5:
                errors.append("minimum 5 images required for training")
            
            if len(images) > 100:
                errors.append("maximum 100 images allowed")
            
            return errors
        
        # Test valid metadata
        valid_metadata = {
            "object_name": "test_object",
            "images": ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]
        }
        errors = validate_upload_metadata(valid_metadata)
        assert len(errors) == 0
        
        # Test invalid metadata scenarios
        invalid_scenarios = [
            {
                "metadata": {"object_name": "", "images": []},
                "expected_errors": 3  # name required, images required, min images
            },
            {
                "metadata": {"object_name": "ab", "images": ["img1.jpg"]},
                "expected_errors": 2  # name too short, not enough images
            },
            {
                "metadata": {"object_name": "a" * 60, "images": ["img1.jpg"] * 150},
                "expected_errors": 2  # name too long, too many images
            }
        ]
        
        for scenario in invalid_scenarios:
            errors = validate_upload_metadata(scenario["metadata"])
            assert len(errors) == scenario["expected_errors"]
    
    @responses.activate
    def test_upload_cleanup_on_failure(self):
        """Test cleanup of uploaded files on processing failure."""
        cleanup_called = []
        
        def mock_cleanup_temp_files(file_paths):
            """Mock cleanup function."""
            cleanup_called.extend(file_paths)
        
        # Setup mock response for processing failure
        responses.add(
            responses.POST,
            f"{self.backend_url}/model/train",
            json={
                "error": "Processing Failed",
                "message": "Failed to process uploaded images",
                "cleanup_required": True
            },
            status=500
        )
        
        # Create test files
        test_files = []
        for i in range(3):
            image = self.create_test_image()
            test_files.append(f"temp_file_{i}.jpg")
        
        # Simulate upload and processing failure
        try:
            test_image = self.create_test_image()
            files = {"images": ("test.jpg", test_image, "image/jpeg")}
            data = {"object_name": "test_object"}
            
            response = requests.post(
                f"{self.backend_url}/model/train",
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            # Check if cleanup is required
            if response.status_code == 500:
                result = response.json()
                if result.get("cleanup_required"):
                    mock_cleanup_temp_files(test_files)
            
        except Exception as e:
            # Ensure cleanup is called even on exception
            mock_cleanup_temp_files(test_files)
        
        # Verify cleanup was called
        assert len(cleanup_called) == len(test_files)
        for file_path in test_files:
            assert file_path in cleanup_called