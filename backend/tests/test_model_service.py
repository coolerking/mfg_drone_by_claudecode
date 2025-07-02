"""
Test cases for Model Service
Tests model management, training jobs, and ML model operations
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path

from api_server.core.model_service import ModelService
from api_server.core.dataset_service import DatasetService
from api_server.models.model_models import TrainModelRequest, TrainingParams


class TestModelService:
    
    @pytest.fixture
    async def model_service(self):
        """Create a model service instance for testing"""
        service = ModelService()
        yield service
        await service.shutdown()
    
    @pytest.fixture
    async def dataset_service(self):
        """Create a dataset service instance for testing"""
        temp_dir = tempfile.mkdtemp()
        service = DatasetService(data_root=temp_dir)
        yield service
        await service.shutdown()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, model_service):
        """Test that the model service initializes correctly"""
        assert model_service is not None
        
        # Check that sample models are loaded
        models = await model_service.get_models()
        assert len(models) >= 3  # Should have sample models
        
        # Check for specific sample models
        model_ids = [m.id for m in models]
        assert "yolo_v8_general" in model_ids
        assert "yolo_v8_person_detector" in model_ids
        assert "ssd_mobilenet_v2" in model_ids
    
    @pytest.mark.asyncio
    async def test_get_models(self, model_service):
        """Test getting all models"""
        models = await model_service.get_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Check model structure
        for model in models:
            assert model.id is not None
            assert model.name is not None
            assert model.dataset_id is not None
            assert model.model_type in ["yolo", "ssd", "faster_rcnn"]
            assert model.status in ["training", "completed", "failed"]
            assert model.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_model_by_id(self, model_service):
        """Test getting a specific model by ID"""
        model = await model_service.get_model("yolo_v8_general")
        
        assert model.id == "yolo_v8_general"
        assert model.name == "YOLOv8 General Detection"
        assert model.model_type == "yolo"
        assert model.status == "completed"
        assert model.accuracy is not None
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_model(self, model_service):
        """Test getting a nonexistent model"""
        with pytest.raises(ValueError, match="Model not found"):
            await model_service.get_model("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_model_exists(self, model_service):
        """Test model existence check"""
        assert model_service.model_exists("yolo_v8_general")
        assert not model_service.model_exists("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_delete_model(self, model_service, dataset_service):
        """Test deleting a model"""
        # Start a training job to create a new model
        request = TrainModelRequest(
            name="Model to Delete",
            dataset_id="person_detection_v1",
            model_type="yolo"
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        
        # Wait for training to complete (it's fast in simulation)
        await asyncio.sleep(0.5)
        
        # Find the created model
        models = await model_service.get_models()
        created_model = None
        for model in models:
            if model.name == "Model to Delete":
                created_model = model
                break
        
        assert created_model is not None
        model_id = created_model.id
        
        # Delete the model
        result = await model_service.delete_model(model_id)
        
        assert result.success is True
        assert "deleted successfully" in result.message.lower()
        assert not model_service.model_exists(model_id)
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_model(self, model_service):
        """Test deleting a nonexistent model"""
        with pytest.raises(ValueError, match="Model not found"):
            await model_service.delete_model("nonexistent_model")
    
    @pytest.mark.asyncio
    async def test_start_training_success(self, model_service, dataset_service):
        """Test starting a training job successfully"""
        request = TrainModelRequest(
            name="Test Training Model",
            description="A test model for unit testing",
            dataset_id="person_detection_v1",
            model_type="yolo",
            training_params=TrainingParams(
                epochs=10,
                batch_size=8,
                learning_rate=0.001
            )
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        
        assert training_job.id is not None
        assert training_job.model_name == "Test Training Model"
        assert training_job.dataset_id == "person_detection_v1"
        assert training_job.status == "queued"
        assert training_job.progress == 0.0
        assert training_job.total_epochs == 10
    
    @pytest.mark.asyncio
    async def test_start_training_invalid_dataset(self, model_service, dataset_service):
        """Test starting training with invalid dataset"""
        request = TrainModelRequest(
            name="Invalid Dataset Training",
            dataset_id="nonexistent_dataset",
            model_type="yolo"
        )
        
        with pytest.raises(ValueError, match="Dataset not found"):
            await model_service.start_training(request, dataset_service)
    
    @pytest.mark.asyncio
    async def test_get_training_job(self, model_service, dataset_service):
        """Test getting a training job by ID"""
        # Start a training job
        request = TrainModelRequest(
            name="Get Job Test",
            dataset_id="person_detection_v1"
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        job_id = training_job.id
        
        # Get the job
        retrieved_job = await model_service.get_training_job(job_id)
        
        assert retrieved_job.id == job_id
        assert retrieved_job.model_name == "Get Job Test"
        assert retrieved_job.dataset_id == "person_detection_v1"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_training_job(self, model_service):
        """Test getting a nonexistent training job"""
        with pytest.raises(ValueError, match="Training job not found"):
            await model_service.get_training_job("nonexistent_job")
    
    @pytest.mark.asyncio
    async def test_get_all_training_jobs(self, model_service, dataset_service):
        """Test getting all training jobs"""
        # Start a few training jobs
        for i in range(3):
            request = TrainModelRequest(
                name=f"Training Job {i}",
                dataset_id="person_detection_v1"
            )
            await model_service.start_training(request, dataset_service)
        
        # Get all jobs
        all_jobs = await model_service.get_all_training_jobs()
        
        assert len(all_jobs) >= 3
        job_names = [job.model_name for job in all_jobs]
        assert "Training Job 0" in job_names
        assert "Training Job 1" in job_names
        assert "Training Job 2" in job_names
    
    @pytest.mark.asyncio
    async def test_get_active_training_jobs(self, model_service, dataset_service):
        """Test getting active training jobs"""
        # Start a training job
        request = TrainModelRequest(
            name="Active Job Test",
            dataset_id="person_detection_v1"
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        
        # Get active jobs immediately (should be queued or running)
        active_jobs = await model_service.get_active_training_jobs()
        
        active_job_ids = [job.id for job in active_jobs]
        assert training_job.id in active_job_ids
    
    @pytest.mark.asyncio
    async def test_cancel_training_job(self, model_service, dataset_service):
        """Test cancelling a training job"""
        # Start a training job
        request = TrainModelRequest(
            name="Cancel Test Job",
            dataset_id="person_detection_v1",
            training_params=TrainingParams(epochs=100)  # Long training
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        job_id = training_job.id
        
        # Wait a bit for it to start
        await asyncio.sleep(0.1)
        
        # Cancel the job
        result = await model_service.cancel_training_job(job_id)
        
        assert result.success is True
        assert "cancelled" in result.message.lower()
        
        # Wait a bit for cancellation to process
        await asyncio.sleep(0.2)
        
        # Check job status
        cancelled_job = await model_service.get_training_job(job_id)
        assert cancelled_job.status == "cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_job(self, model_service):
        """Test cancelling a nonexistent job"""
        with pytest.raises(ValueError, match="Training job not found"):
            await model_service.cancel_training_job("nonexistent_job")
    
    @pytest.mark.asyncio
    async def test_training_job_completion(self, model_service, dataset_service):
        """Test that training jobs complete and create models"""
        # Start a short training job
        request = TrainModelRequest(
            name="Completion Test Model",
            dataset_id="person_detection_v1",
            training_params=TrainingParams(epochs=5)  # Short training
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        job_id = training_job.id
        
        # Wait for training to complete
        max_wait = 50  # 5 seconds max
        for _ in range(max_wait):
            job = await model_service.get_training_job(job_id)
            if job.status == "completed":
                break
            await asyncio.sleep(0.1)
        
        # Check final job status
        completed_job = await model_service.get_training_job(job_id)
        assert completed_job.status == "completed"
        assert completed_job.progress == 100.0
        assert completed_job.completed_at is not None
        
        # Check that a model was created
        models = await model_service.get_models()
        created_model = None
        for model in models:
            if model.name == "Completion Test Model":
                created_model = model
                break
        
        assert created_model is not None
        assert created_model.status == "completed"
        assert created_model.accuracy is not None
    
    @pytest.mark.asyncio
    async def test_training_progress_updates(self, model_service, dataset_service):
        """Test that training jobs update progress correctly"""
        # Start a training job
        request = TrainModelRequest(
            name="Progress Test Model",
            dataset_id="person_detection_v1",
            training_params=TrainingParams(epochs=20)
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        job_id = training_job.id
        
        # Wait a bit and check progress
        await asyncio.sleep(0.3)
        
        job = await model_service.get_training_job(job_id)
        assert job.current_epoch is not None
        assert job.current_epoch > 0
        assert 0 <= job.progress <= 100
        
        if job.status == "running":
            assert job.loss is not None
            assert job.accuracy is not None
            assert job.estimated_remaining_time is not None
    
    @pytest.mark.asyncio
    async def test_model_statistics(self, model_service, dataset_service):
        """Test getting model service statistics"""
        # Start a training job
        request = TrainModelRequest(
            name="Statistics Test Model",
            dataset_id="person_detection_v1"
        )
        
        await model_service.start_training(request, dataset_service)
        
        # Get statistics
        stats = await model_service.get_model_statistics()
        
        assert "total_models" in stats
        assert "model_types" in stats
        assert "total_training_jobs" in stats
        assert "active_training_jobs" in stats
        assert "job_statuses" in stats
        assert "last_updated" in stats
        
        assert stats["total_models"] >= 3  # Sample models
        assert stats["total_training_jobs"] >= 1  # Our test job
        assert stats["active_training_jobs"] >= 0
        
        # Check model type distribution
        assert "yolo" in stats["model_types"]
        assert stats["model_types"]["yolo"] >= 1
    
    @pytest.mark.asyncio
    async def test_cleanup_completed_jobs(self, model_service, dataset_service):
        """Test cleanup of old completed jobs"""
        # Start and complete a training job
        request = TrainModelRequest(
            name="Cleanup Test Model",
            dataset_id="person_detection_v1",
            training_params=TrainingParams(epochs=3)
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        job_id = training_job.id
        
        # Wait for completion
        for _ in range(30):
            job = await model_service.get_training_job(job_id)
            if job.status in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        # Manually set completion time to old date for testing
        job = await model_service.get_training_job(job_id)
        if job_id in model_service.training_jobs:
            from datetime import datetime, timedelta
            model_service.training_jobs[job_id].completed_at = datetime.now() - timedelta(days=10)
        
        # Run cleanup with 7-day cutoff
        await model_service.cleanup_completed_jobs(max_age_days=7)
        
        # Job should be cleaned up
        with pytest.raises(ValueError, match="Training job not found"):
            await model_service.get_training_job(job_id)
    
    @pytest.mark.asyncio
    async def test_default_training_params(self, model_service, dataset_service):
        """Test training with default parameters"""
        request = TrainModelRequest(
            name="Default Params Test",
            dataset_id="person_detection_v1"
            # No training_params provided
        )
        
        training_job = await model_service.start_training(request, dataset_service)
        
        # Should use default parameters
        assert training_job.total_epochs == 100  # Default epochs
    
    @pytest.mark.asyncio
    async def test_service_shutdown_with_active_jobs(self, model_service, dataset_service):
        """Test service shutdown with active training jobs"""
        # Start multiple training jobs
        for i in range(3):
            request = TrainModelRequest(
                name=f"Shutdown Test {i}",
                dataset_id="person_detection_v1",
                training_params=TrainingParams(epochs=100)  # Long training
            )
            await model_service.start_training(request, dataset_service)
        
        # Shutdown should cancel all active jobs
        await model_service.shutdown()
        
        # All jobs should be cancelled or completed
        all_jobs = await model_service.get_all_training_jobs()
        active_jobs = [job for job in all_jobs if job.status in ["queued", "running"]]
        assert len(active_jobs) == 0