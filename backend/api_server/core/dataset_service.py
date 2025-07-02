"""
Dataset Service
Handles dataset management for machine learning model training
"""

import asyncio
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models.vision_models import Dataset, DatasetImage, CreateDatasetRequest
from ..models.common_models import SuccessResponse

logger = logging.getLogger(__name__)


class DatasetService:
    """Dataset management service for ML training data"""
    
    def __init__(self, data_root: str = "/tmp/mfg_drone_datasets"):
        self.data_root = Path(data_root)
        self.datasets: Dict[str, Dataset] = {}
        self.dataset_images: Dict[str, List[DatasetImage]] = {}
        
        # Create data directory
        self.data_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize with sample datasets
        self._initialize_sample_datasets()
        
    def _initialize_sample_datasets(self):
        """Initialize sample datasets for demonstration"""
        sample_datasets = [
            {
                "id": "person_detection_v1",
                "name": "Person Detection Dataset v1",
                "description": "General person detection training dataset",
                "labels": ["person", "background"],
                "image_count": 1500
            },
            {
                "id": "vehicle_detection_v1", 
                "name": "Vehicle Detection Dataset v1",
                "description": "Car, truck, and motorcycle detection dataset",
                "labels": ["car", "truck", "motorcycle", "bicycle", "background"],
                "image_count": 2300
            },
            {
                "id": "multi_object_v1",
                "name": "Multi-Object Detection Dataset v1", 
                "description": "General purpose multi-object detection dataset",
                "labels": ["person", "car", "bicycle", "motorbike", "bus", "truck", "bird", "cat", "dog", "background"],
                "image_count": 5000
            }
        ]
        
        for dataset_config in sample_datasets:
            dataset = Dataset(
                id=dataset_config["id"],
                name=dataset_config["name"],
                description=dataset_config["description"],
                image_count=dataset_config["image_count"],
                labels=dataset_config["labels"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.datasets[dataset.id] = dataset
            self.dataset_images[dataset.id] = []
            
            # Create dataset directory
            dataset_dir = self.data_root / dataset.id
            dataset_dir.mkdir(exist_ok=True)
            (dataset_dir / "images").mkdir(exist_ok=True)
            (dataset_dir / "annotations").mkdir(exist_ok=True)
        
        logger.info(f"Initialized {len(self.datasets)} sample datasets")
    
    async def get_datasets(self) -> List[Dataset]:
        """Get all datasets"""
        return list(self.datasets.values())
    
    async def get_dataset(self, dataset_id: str) -> Dataset:
        """
        Get a specific dataset by ID
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dataset object
            
        Raises:
            ValueError: If dataset not found
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        return self.datasets[dataset_id]
    
    async def create_dataset(self, request: CreateDatasetRequest) -> Dataset:
        """
        Create a new dataset
        
        Args:
            request: Dataset creation request
            
        Returns:
            Created Dataset object
        """
        dataset_id = f"dataset_{uuid.uuid4().hex[:8]}"
        
        dataset = Dataset(
            id=dataset_id,
            name=request.name,
            description=request.description,
            image_count=0,
            labels=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create dataset directory structure
        dataset_dir = self.data_root / dataset_id
        dataset_dir.mkdir(exist_ok=True)
        (dataset_dir / "images").mkdir(exist_ok=True)
        (dataset_dir / "annotations").mkdir(exist_ok=True)
        
        # Store dataset
        self.datasets[dataset_id] = dataset
        self.dataset_images[dataset_id] = []
        
        logger.info(f"Created dataset: {dataset_id} - {request.name}")
        
        return dataset
    
    async def delete_dataset(self, dataset_id: str) -> SuccessResponse:
        """
        Delete a dataset and all its data
        
        Args:
            dataset_id: ID of the dataset to delete
            
        Returns:
            SuccessResponse
            
        Raises:
            ValueError: If dataset not found
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        # Remove dataset directory
        dataset_dir = self.data_root / dataset_id
        if dataset_dir.exists():
            shutil.rmtree(dataset_dir)
        
        # Remove from memory
        dataset_name = self.datasets[dataset_id].name
        del self.datasets[dataset_id]
        del self.dataset_images[dataset_id]
        
        logger.info(f"Deleted dataset: {dataset_id} - {dataset_name}")
        
        return SuccessResponse(
            message=f"Dataset {dataset_name} deleted successfully",
            timestamp=datetime.now()
        )
    
    async def add_image_to_dataset(self, dataset_id: str, file_data: bytes, filename: str, label: Optional[str] = None) -> DatasetImage:
        """
        Add an image to a dataset
        
        Args:
            dataset_id: ID of the target dataset
            file_data: Binary image data
            filename: Original filename
            label: Image label/annotation
            
        Returns:
            DatasetImage object
            
        Raises:
            ValueError: If dataset not found or invalid image data
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        # Generate unique image ID and filename
        image_id = f"img_{uuid.uuid4().hex[:12]}"
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp']:
            raise ValueError(f"Unsupported image format: {file_ext}")
        
        new_filename = f"{image_id}{file_ext}"
        
        # Save image file
        dataset_dir = self.data_root / dataset_id / "images"
        image_path = dataset_dir / new_filename
        
        try:
            with open(image_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            raise ValueError(f"Failed to save image: {str(e)}")
        
        # Create dataset image record
        dataset_image = DatasetImage(
            id=image_id,
            filename=new_filename,
            path=str(image_path),
            label=label,
            dataset_id=dataset_id,
            uploaded_at=datetime.now()
        )
        
        # Update dataset
        self.dataset_images[dataset_id].append(dataset_image)
        self.datasets[dataset_id].image_count += 1
        self.datasets[dataset_id].updated_at = datetime.now()
        
        # Update labels if new label provided
        if label and label not in self.datasets[dataset_id].labels:
            self.datasets[dataset_id].labels.append(label)
        
        logger.info(f"Added image to dataset {dataset_id}: {new_filename}")
        
        return dataset_image
    
    async def get_dataset_images(self, dataset_id: str) -> List[DatasetImage]:
        """
        Get all images for a dataset
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            List of DatasetImage objects
            
        Raises:
            ValueError: If dataset not found
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        return self.dataset_images[dataset_id]
    
    def dataset_exists(self, dataset_id: str) -> bool:
        """Check if a dataset exists"""
        return dataset_id in self.datasets
    
    async def get_dataset_statistics(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get statistics for a dataset
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dictionary with dataset statistics
            
        Raises:
            ValueError: If dataset not found
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        dataset = self.datasets[dataset_id]
        images = self.dataset_images[dataset_id]
        
        # Calculate label distribution
        label_counts = {}
        for image in images:
            if image.label:
                label_counts[image.label] = label_counts.get(image.label, 0) + 1
        
        # Calculate total size (simulated)
        total_size_mb = len(images) * 0.5  # Assume 500KB per image average
        
        return {
            "dataset_id": dataset_id,
            "name": dataset.name,
            "total_images": len(images),
            "total_labels": len(dataset.labels),
            "label_distribution": label_counts,
            "total_size_mb": round(total_size_mb, 2),
            "created_at": dataset.created_at,
            "updated_at": dataset.updated_at
        }
    
    async def cleanup_empty_datasets(self):
        """Remove datasets with no images (maintenance function)"""
        empty_datasets = [
            dataset_id for dataset_id, images in self.dataset_images.items()
            if len(images) == 0 and dataset_id not in ["person_detection_v1", "vehicle_detection_v1", "multi_object_v1"]
        ]
        
        for dataset_id in empty_datasets:
            await self.delete_dataset(dataset_id)
        
        if empty_datasets:
            logger.info(f"Cleaned up {len(empty_datasets)} empty datasets")
    
    async def shutdown(self):
        """Shutdown the dataset service"""
        await self.cleanup_empty_datasets()
        logger.info("Dataset service shutdown complete")