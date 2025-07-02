"""
Test cases for Dataset Service
Tests dataset management, image upload, and dataset operations
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from api_server.core.dataset_service import DatasetService
from api_server.models.vision_models import CreateDatasetRequest


class TestDatasetService:
    
    @pytest.fixture
    async def dataset_service(self):
        """Create a dataset service instance for testing"""
        # Use a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        service = DatasetService(data_root=temp_dir)
        yield service
        await service.shutdown()
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_test_image_bytes(self, width=100, height=100):
        """Create test image bytes (JPEG format)"""
        from PIL import Image
        from io import BytesIO
        
        # Create a simple test image
        image = Image.new('RGB', (width, height), color='blue')
        
        # Convert to bytes
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        return buffer.getvalue()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, dataset_service):
        """Test that the dataset service initializes correctly"""
        assert dataset_service is not None
        
        # Check that sample datasets are loaded
        datasets = await dataset_service.get_datasets()
        assert len(datasets) >= 3  # Should have sample datasets
        
        # Check for specific sample datasets
        dataset_ids = [d.id for d in datasets]
        assert "person_detection_v1" in dataset_ids
        assert "vehicle_detection_v1" in dataset_ids
        assert "multi_object_v1" in dataset_ids
    
    @pytest.mark.asyncio
    async def test_get_datasets(self, dataset_service):
        """Test getting all datasets"""
        datasets = await dataset_service.get_datasets()
        
        assert isinstance(datasets, list)
        assert len(datasets) > 0
        
        # Check dataset structure
        for dataset in datasets:
            assert dataset.id is not None
            assert dataset.name is not None
            assert dataset.image_count >= 0
            assert isinstance(dataset.labels, list)
            assert dataset.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_dataset_by_id(self, dataset_service):
        """Test getting a specific dataset by ID"""
        # Get a known dataset
        dataset = await dataset_service.get_dataset("person_detection_v1")
        
        assert dataset.id == "person_detection_v1"
        assert dataset.name == "Person Detection Dataset v1"
        assert "person" in dataset.labels
        assert dataset.image_count >= 0
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_dataset(self, dataset_service):
        """Test getting a nonexistent dataset"""
        with pytest.raises(ValueError, match="Dataset not found"):
            await dataset_service.get_dataset("nonexistent_dataset")
    
    @pytest.mark.asyncio
    async def test_create_dataset(self, dataset_service):
        """Test creating a new dataset"""
        request = CreateDatasetRequest(
            name="Test Dataset",
            description="A test dataset for unit testing"
        )
        
        dataset = await dataset_service.create_dataset(request)
        
        assert dataset.id is not None
        assert dataset.name == "Test Dataset"
        assert dataset.description == "A test dataset for unit testing"
        assert dataset.image_count == 0
        assert dataset.labels == []
        assert dataset.created_at is not None
        assert dataset.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_dataset_exists(self, dataset_service):
        """Test dataset existence check"""
        assert dataset_service.dataset_exists("person_detection_v1")
        assert not dataset_service.dataset_exists("nonexistent_dataset")
    
    @pytest.mark.asyncio
    async def test_delete_dataset(self, dataset_service):
        """Test deleting a dataset"""
        # Create a test dataset first
        request = CreateDatasetRequest(name="Dataset to Delete")
        dataset = await dataset_service.create_dataset(request)
        dataset_id = dataset.id
        
        # Verify it exists
        assert dataset_service.dataset_exists(dataset_id)
        
        # Delete it
        result = await dataset_service.delete_dataset(dataset_id)
        
        assert result.success is True
        assert "deleted successfully" in result.message.lower()
        assert not dataset_service.dataset_exists(dataset_id)
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_dataset(self, dataset_service):
        """Test deleting a nonexistent dataset"""
        with pytest.raises(ValueError, match="Dataset not found"):
            await dataset_service.delete_dataset("nonexistent_dataset")
    
    @pytest.mark.asyncio
    async def test_add_image_to_dataset(self, dataset_service):
        """Test adding an image to a dataset"""
        # Create a test dataset
        request = CreateDatasetRequest(name="Image Test Dataset")
        dataset = await dataset_service.create_dataset(request)
        
        # Create test image data
        image_data = self.create_test_image_bytes()
        
        # Add image to dataset
        dataset_image = await dataset_service.add_image_to_dataset(
            dataset_id=dataset.id,
            file_data=image_data,
            filename="test_image.jpg",
            label="test_object"
        )
        
        assert dataset_image.id is not None
        assert dataset_image.filename.endswith(".jpg")
        assert dataset_image.label == "test_object"
        assert dataset_image.dataset_id == dataset.id
        assert dataset_image.uploaded_at is not None
        assert Path(dataset_image.path).exists()
        
        # Check that dataset was updated
        updated_dataset = await dataset_service.get_dataset(dataset.id)
        assert updated_dataset.image_count == 1
        assert "test_object" in updated_dataset.labels
    
    @pytest.mark.asyncio
    async def test_add_image_invalid_dataset(self, dataset_service):
        """Test adding image to nonexistent dataset"""
        image_data = self.create_test_image_bytes()
        
        with pytest.raises(ValueError, match="Dataset not found"):
            await dataset_service.add_image_to_dataset(
                dataset_id="nonexistent_dataset",
                file_data=image_data,
                filename="test.jpg"
            )
    
    @pytest.mark.asyncio
    async def test_add_image_invalid_format(self, dataset_service):
        """Test adding image with invalid format"""
        # Create a test dataset
        request = CreateDatasetRequest(name="Invalid Format Test")
        dataset = await dataset_service.create_dataset(request)
        
        # Try to add invalid image data
        with pytest.raises(ValueError, match="Unsupported image format"):
            await dataset_service.add_image_to_dataset(
                dataset_id=dataset.id,
                file_data=b"not_an_image",
                filename="test.txt"
            )
    
    @pytest.mark.asyncio
    async def test_get_dataset_images(self, dataset_service):
        """Test getting images for a dataset"""
        # Create a test dataset
        request = CreateDatasetRequest(name="Images Test Dataset")
        dataset = await dataset_service.create_dataset(request)
        
        # Add some test images
        for i in range(3):
            image_data = self.create_test_image_bytes()
            await dataset_service.add_image_to_dataset(
                dataset_id=dataset.id,
                file_data=image_data,
                filename=f"test_image_{i}.jpg",
                label=f"label_{i}"
            )
        
        # Get images
        images = await dataset_service.get_dataset_images(dataset.id)
        
        assert len(images) == 3
        assert all(img.dataset_id == dataset.id for img in images)
        assert all(img.filename.startswith("test_image_") for img in images)
    
    @pytest.mark.asyncio
    async def test_get_images_nonexistent_dataset(self, dataset_service):
        """Test getting images for nonexistent dataset"""
        with pytest.raises(ValueError, match="Dataset not found"):
            await dataset_service.get_dataset_images("nonexistent_dataset")
    
    @pytest.mark.asyncio
    async def test_get_dataset_statistics(self, dataset_service):
        """Test getting dataset statistics"""
        # Create a test dataset
        request = CreateDatasetRequest(name="Statistics Test Dataset")
        dataset = await dataset_service.create_dataset(request)
        
        # Add test images with different labels
        labels = ["person", "person", "car", "bicycle"]
        for i, label in enumerate(labels):
            image_data = self.create_test_image_bytes()
            await dataset_service.add_image_to_dataset(
                dataset_id=dataset.id,
                file_data=image_data,
                filename=f"test_{i}.jpg",
                label=label
            )
        
        # Get statistics
        stats = await dataset_service.get_dataset_statistics(dataset.id)
        
        assert stats["dataset_id"] == dataset.id
        assert stats["name"] == "Statistics Test Dataset"
        assert stats["total_images"] == 4
        assert stats["total_labels"] == 3  # person, car, bicycle
        assert stats["label_distribution"]["person"] == 2
        assert stats["label_distribution"]["car"] == 1
        assert stats["label_distribution"]["bicycle"] == 1
        assert stats["total_size_mb"] > 0
    
    @pytest.mark.asyncio
    async def test_statistics_nonexistent_dataset(self, dataset_service):
        """Test getting statistics for nonexistent dataset"""
        with pytest.raises(ValueError, match="Dataset not found"):
            await dataset_service.get_dataset_statistics("nonexistent_dataset")
    
    @pytest.mark.asyncio
    async def test_multiple_images_same_label(self, dataset_service):
        """Test adding multiple images with the same label"""
        # Create a test dataset
        request = CreateDatasetRequest(name="Same Label Test")
        dataset = await dataset_service.create_dataset(request)
        
        # Add multiple images with same label
        for i in range(3):
            image_data = self.create_test_image_bytes()
            await dataset_service.add_image_to_dataset(
                dataset_id=dataset.id,
                file_data=image_data,
                filename=f"person_{i}.jpg",
                label="person"
            )
        
        # Check dataset
        updated_dataset = await dataset_service.get_dataset(dataset.id)
        assert updated_dataset.image_count == 3
        assert updated_dataset.labels == ["person"]  # Should not duplicate labels
    
    @pytest.mark.asyncio
    async def test_cleanup_empty_datasets(self, dataset_service):
        """Test cleanup of empty datasets"""
        # Create an empty dataset
        request = CreateDatasetRequest(name="Empty Dataset")
        empty_dataset = await dataset_service.create_dataset(request)
        empty_dataset_id = empty_dataset.id
        
        # Create a dataset with images
        request2 = CreateDatasetRequest(name="Non-empty Dataset")
        non_empty_dataset = await dataset_service.create_dataset(request2)
        
        image_data = self.create_test_image_bytes()
        await dataset_service.add_image_to_dataset(
            dataset_id=non_empty_dataset.id,
            file_data=image_data,
            filename="test.jpg"
        )
        
        # Run cleanup
        await dataset_service.cleanup_empty_datasets()
        
        # Empty dataset should be removed (except sample datasets)
        # Non-empty dataset should remain
        assert not dataset_service.dataset_exists(empty_dataset_id)
        assert dataset_service.dataset_exists(non_empty_dataset.id)
        
        # Sample datasets should remain even if empty
        assert dataset_service.dataset_exists("person_detection_v1")
    
    @pytest.mark.asyncio
    async def test_add_image_without_label(self, dataset_service):
        """Test adding image without label"""
        # Create a test dataset
        request = CreateDatasetRequest(name="No Label Test")
        dataset = await dataset_service.create_dataset(request)
        
        # Add image without label
        image_data = self.create_test_image_bytes()
        dataset_image = await dataset_service.add_image_to_dataset(
            dataset_id=dataset.id,
            file_data=image_data,
            filename="unlabeled.jpg",
            label=None
        )
        
        assert dataset_image.label is None
        
        # Dataset labels should not be updated
        updated_dataset = await dataset_service.get_dataset(dataset.id)
        assert updated_dataset.labels == []