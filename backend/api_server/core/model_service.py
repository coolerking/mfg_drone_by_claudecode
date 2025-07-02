"""
Model Service
Handles machine learning model management and training operations
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models.model_models import Model, TrainModelRequest, TrainingJob, TrainingParams
from ..models.common_models import SuccessResponse

logger = logging.getLogger(__name__)


class MockTrainingRunner:
    """
    Mock training runner that simulates model training
    In production, this would interface with actual ML training frameworks
    """
    
    def __init__(self, job: TrainingJob, training_params: TrainingParams):
        self.job = job
        self.training_params = training_params
        self.is_running = False
        self.is_cancelled = False
        
    async def run_training(self, model_service, dataset_service):
        """Run the training simulation"""
        self.is_running = True
        
        try:
            # Update job status to running
            self.job.status = "running"
            self.job.started_at = datetime.now()
            self.job.progress = 0.0
            self.job.current_epoch = 0
            self.job.total_epochs = self.training_params.epochs
            
            logger.info(f"Starting training job {self.job.id}")
            
            # Simulate training epochs
            for epoch in range(1, self.training_params.epochs + 1):
                if self.is_cancelled:
                    self.job.status = "cancelled"
                    self.job.completed_at = datetime.now()
                    logger.info(f"Training job {self.job.id} cancelled at epoch {epoch}")
                    return
                
                # Simulate epoch processing time
                await asyncio.sleep(0.1)  # Fast simulation
                
                # Update progress
                self.job.current_epoch = epoch
                self.job.progress = (epoch / self.training_params.epochs) * 100
                
                # Simulate improving metrics
                self.job.loss = max(0.01, 1.0 - (epoch / self.training_params.epochs) * 0.8 + 
                                  (epoch % 10) * 0.02)  # Some noise
                self.job.accuracy = min(0.95, (epoch / self.training_params.epochs) * 0.9 + 
                                      (epoch % 7) * 0.01)  # Some noise
                
                # Estimate remaining time
                elapsed = (datetime.now() - self.job.started_at).total_seconds()
                remaining_epochs = self.training_params.epochs - epoch
                if epoch > 0:
                    time_per_epoch = elapsed / epoch
                    self.job.estimated_remaining_time = int(remaining_epochs * time_per_epoch)
                
                # Log progress every 10 epochs or at the end
                if epoch % 10 == 0 or epoch == self.training_params.epochs:
                    logger.info(f"Training job {self.job.id}: Epoch {epoch}/{self.training_params.epochs}, "
                              f"Loss: {self.job.loss:.4f}, Accuracy: {self.job.accuracy:.4f}")
            
            # Complete training
            self.job.status = "completed"
            self.job.progress = 100.0
            self.job.completed_at = datetime.now()
            self.job.estimated_remaining_time = 0
            
            # Create final model
            model_id = f"model_{uuid.uuid4().hex[:8]}"
            final_model = Model(
                id=model_id,
                name=self.job.model_name,
                description=f"Model trained from dataset {self.job.dataset_id}",
                dataset_id=self.job.dataset_id,
                model_type="yolo",  # Default for now
                status="completed",
                accuracy=self.job.accuracy,
                file_path=f"/models/{model_id}/best.pt",
                created_at=datetime.now(),
                trained_at=datetime.now()
            )
            
            # Add model to service
            model_service.models[model_id] = final_model
            
            logger.info(f"Training job {self.job.id} completed successfully. Model ID: {model_id}")
            
        except Exception as e:
            self.job.status = "failed"
            self.job.error_message = str(e)
            self.job.completed_at = datetime.now()
            logger.error(f"Training job {self.job.id} failed: {str(e)}")
        
        finally:
            self.is_running = False
    
    def cancel(self):
        """Cancel the training job"""
        self.is_cancelled = True


class ModelService:
    """Model management service for ML models and training"""
    
    def __init__(self):
        self.models: Dict[str, Model] = {}
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.training_runners: Dict[str, MockTrainingRunner] = {}
        self.model_root = Path("/tmp/mfg_drone_models")
        
        # Create model directory
        self.model_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize with sample models
        self._initialize_sample_models()
        
    def _initialize_sample_models(self):
        """Initialize sample pre-trained models"""
        sample_models = [
            {
                "id": "yolo_v8_general",
                "name": "YOLOv8 General Detection",
                "description": "Pre-trained YOLOv8 model for general object detection",
                "dataset_id": "coco_dataset",
                "model_type": "yolo",
                "status": "completed",
                "accuracy": 0.89,
                "file_path": "/models/yolo_v8_general/yolov8n.pt"
            },
            {
                "id": "yolo_v8_person_detector",
                "name": "YOLOv8 Person Detector",
                "description": "Specialized YOLOv8 model for person detection",
                "dataset_id": "person_detection_v1",
                "model_type": "yolo",
                "status": "completed",
                "accuracy": 0.93,
                "file_path": "/models/yolo_v8_person_detector/best.pt"
            },
            {
                "id": "ssd_mobilenet_v2",
                "name": "SSD MobileNet v2",
                "description": "Lightweight SSD model for mobile deployment",
                "dataset_id": "coco_dataset",
                "model_type": "ssd",
                "status": "completed",
                "accuracy": 0.76,
                "file_path": "/models/ssd_mobilenet_v2/model.pb"
            }
        ]
        
        for model_config in sample_models:
            model = Model(
                id=model_config["id"],
                name=model_config["name"],
                description=model_config["description"],
                dataset_id=model_config["dataset_id"],
                model_type=model_config["model_type"],
                status=model_config["status"],
                accuracy=model_config["accuracy"],
                file_path=model_config["file_path"],
                created_at=datetime.now() - timedelta(days=30),
                trained_at=datetime.now() - timedelta(days=30)
            )
            
            self.models[model.id] = model
            
            # Create model directory
            model_dir = self.model_root / model.id
            model_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized {len(self.models)} sample models")
    
    async def get_models(self) -> List[Model]:
        """Get all models"""
        return list(self.models.values())
    
    async def get_model(self, model_id: str) -> Model:
        """
        Get a specific model by ID
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model object
            
        Raises:
            ValueError: If model not found
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        return self.models[model_id]
    
    async def delete_model(self, model_id: str) -> SuccessResponse:
        """
        Delete a model
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            SuccessResponse
            
        Raises:
            ValueError: If model not found or model is being used
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        # Check if model is being used in active training
        active_jobs = [job for job in self.training_jobs.values() 
                      if job.status in ["queued", "running"]]
        
        for job in active_jobs:
            if model_id in job.model_name:  # Simple check, could be more sophisticated
                raise ValueError(f"Cannot delete model {model_id}: it is being used in active training")
        
        model_name = self.models[model_id].name
        del self.models[model_id]
        
        logger.info(f"Deleted model: {model_id} - {model_name}")
        
        return SuccessResponse(
            message=f"Model {model_name} deleted successfully",
            timestamp=datetime.now()
        )
    
    def model_exists(self, model_id: str) -> bool:
        """Check if a model exists"""
        return model_id in self.models
    
    async def start_training(self, request: TrainModelRequest, dataset_service) -> TrainingJob:
        """
        Start a new model training job
        
        Args:
            request: Training request parameters
            dataset_service: Dataset service instance for validation
            
        Returns:
            TrainingJob object
            
        Raises:
            ValueError: If dataset not found or invalid parameters
        """
        # Validate dataset exists
        if not dataset_service.dataset_exists(request.dataset_id):
            raise ValueError(f"Dataset not found: {request.dataset_id}")
        
        # Create training job
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Use default training params if not provided
        training_params = request.training_params or TrainingParams()
        
        training_job = TrainingJob(
            id=job_id,
            model_name=request.name,
            dataset_id=request.dataset_id,
            status="queued",
            progress=0.0,
            current_epoch=None,
            total_epochs=training_params.epochs,
            loss=None,
            accuracy=None,
            estimated_remaining_time=None,
            started_at=None,
            completed_at=None,
            error_message=None
        )
        
        self.training_jobs[job_id] = training_job
        
        # Create and start training runner
        runner = MockTrainingRunner(training_job, training_params)
        self.training_runners[job_id] = runner
        
        # Start training in background
        asyncio.create_task(runner.run_training(self, dataset_service))
        
        logger.info(f"Started training job: {job_id} for model {request.name}")
        
        return training_job
    
    async def get_training_job(self, job_id: str) -> TrainingJob:
        """
        Get training job status
        
        Args:
            job_id: ID of the training job
            
        Returns:
            TrainingJob object
            
        Raises:
            ValueError: If job not found
        """
        if job_id not in self.training_jobs:
            raise ValueError(f"Training job not found: {job_id}")
        
        return self.training_jobs[job_id]
    
    async def cancel_training_job(self, job_id: str) -> SuccessResponse:
        """
        Cancel a training job
        
        Args:
            job_id: ID of the training job to cancel
            
        Returns:
            SuccessResponse
            
        Raises:
            ValueError: If job not found or cannot be cancelled
        """
        if job_id not in self.training_jobs:
            raise ValueError(f"Training job not found: {job_id}")
        
        job = self.training_jobs[job_id]
        
        if job.status not in ["queued", "running"]:
            raise ValueError(f"Cannot cancel job {job_id}: status is {job.status}")
        
        # Cancel the runner
        if job_id in self.training_runners:
            self.training_runners[job_id].cancel()
        
        logger.info(f"Cancelled training job: {job_id}")
        
        return SuccessResponse(
            message=f"Training job {job_id} cancelled",
            timestamp=datetime.now()
        )
    
    async def get_all_training_jobs(self) -> List[TrainingJob]:
        """Get all training jobs"""
        return list(self.training_jobs.values())
    
    async def get_active_training_jobs(self) -> List[TrainingJob]:
        """Get active (queued or running) training jobs"""
        return [job for job in self.training_jobs.values() 
                if job.status in ["queued", "running"]]
    
    async def cleanup_completed_jobs(self, max_age_days: int = 7):
        """
        Clean up old completed training jobs
        
        Args:
            max_age_days: Maximum age in days for completed jobs
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        jobs_to_remove = []
        for job_id, job in self.training_jobs.items():
            if (job.status in ["completed", "failed", "cancelled"] and 
                job.completed_at and job.completed_at < cutoff_date):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.training_jobs[job_id]
            if job_id in self.training_runners:
                del self.training_runners[job_id]
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old training jobs")
    
    async def get_model_statistics(self) -> Dict[str, Any]:
        """Get model service statistics"""
        total_models = len(self.models)
        total_jobs = len(self.training_jobs)
        active_jobs = len([job for job in self.training_jobs.values() 
                          if job.status in ["queued", "running"]])
        
        # Model type distribution
        model_types = {}
        for model in self.models.values():
            model_types[model.model_type] = model_types.get(model.model_type, 0) + 1
        
        # Job status distribution
        job_statuses = {}
        for job in self.training_jobs.values():
            job_statuses[job.status] = job_statuses.get(job.status, 0) + 1
        
        return {
            "total_models": total_models,
            "model_types": model_types,
            "total_training_jobs": total_jobs,
            "active_training_jobs": active_jobs,
            "job_statuses": job_statuses,
            "last_updated": datetime.now()
        }
    
    async def shutdown(self):
        """Shutdown the model service"""
        # Cancel all active training jobs
        active_jobs = await self.get_active_training_jobs()
        for job in active_jobs:
            try:
                await self.cancel_training_job(job.id)
            except Exception as e:
                logger.error(f"Error cancelling job {job.id} during shutdown: {str(e)}")
        
        # Clean up old jobs
        await self.cleanup_completed_jobs()
        
        logger.info("Model service shutdown complete")