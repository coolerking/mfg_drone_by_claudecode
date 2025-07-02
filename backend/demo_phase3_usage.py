#!/usr/bin/env python3
"""
Demo script showing Phase 3 API usage
Demonstrates vision, model management, and dashboard functionality
"""

import asyncio
import base64
import tempfile
import shutil
from datetime import datetime
from io import BytesIO
from PIL import Image

# Add current directory to path
import sys
sys.path.append('.')

from api_server.core.vision_service import VisionService
from api_server.core.dataset_service import DatasetService
from api_server.core.model_service import ModelService
from api_server.core.system_service import SystemService
from api_server.core.drone_manager import DroneManager

from api_server.models.vision_models import CreateDatasetRequest
from api_server.models.model_models import TrainModelRequest, TrainingParams


def create_test_image_base64(width=100, height=100, color='red'):
    """Helper function to create test image as base64"""
    image = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode('utf-8')


def create_test_image_bytes(width=100, height=100, color='blue'):
    """Helper function to create test image as bytes"""
    image = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()


async def demo_vision_service():
    """Demonstrate vision service functionality"""
    print("\n🔍 === Vision Service Demo ===")
    
    # Initialize vision service
    vision_service = VisionService()
    print(f"✅ Vision service initialized with {len(vision_service.get_available_models())} models")
    print(f"   Available models: {vision_service.get_available_models()}")
    
    # 1. Object Detection Demo
    print("\n📸 Testing object detection...")
    test_image = create_test_image_base64(640, 480, 'green')
    
    try:
        detection_result = await vision_service.detect_objects(
            image_data=test_image,
            model_id="yolo_v8_general",
            confidence_threshold=0.5
        )
        
        print(f"✅ Detection completed in {detection_result.processing_time:.3f}s")
        print(f"   Found {len(detection_result.detections)} objects")
        
        for i, detection in enumerate(detection_result.detections):
            print(f"   Object {i+1}: {detection.label} (confidence: {detection.confidence:.3f})")
            
    except Exception as e:
        print(f"❌ Detection failed: {str(e)}")
    
    # 2. Object Tracking Demo
    print("\n🎯 Testing object tracking...")
    try:
        # Start tracking
        start_result = await vision_service.start_tracking(
            model_id="yolo_v8_person_detector",
            drone_id="demo_drone_001",
            confidence_threshold=0.6,
            follow_distance=200
        )
        print(f"✅ Tracking started: {start_result.message}")
        
        # Wait a bit for tracking simulation
        await asyncio.sleep(0.5)
        
        # Check tracking status
        tracking_status = await vision_service.get_tracking_status()
        print(f"✅ Tracking status: Active={tracking_status.is_active}, Target detected={tracking_status.target_detected}")
        
        # Stop tracking
        stop_result = await vision_service.stop_tracking()
        print(f"✅ Tracking stopped: {stop_result.message}")
        
    except Exception as e:
        print(f"❌ Tracking failed: {str(e)}")
    
    await vision_service.shutdown()
    print("✅ Vision service demo completed")


async def demo_dataset_service():
    """Demonstrate dataset service functionality"""
    print("\n📊 === Dataset Service Demo ===")
    
    # Initialize dataset service with temporary directory
    temp_dir = tempfile.mkdtemp()
    dataset_service = DatasetService(data_root=temp_dir)
    
    try:
        # 1. List existing datasets
        datasets = await dataset_service.get_datasets()
        print(f"✅ Found {len(datasets)} existing datasets")
        for dataset in datasets:
            print(f"   - {dataset.name} ({dataset.image_count} images)")
        
        # 2. Create new dataset
        print("\n📝 Creating new dataset...")
        create_request = CreateDatasetRequest(
            name="Demo Dataset",
            description="A demonstration dataset for Phase 3"
        )
        
        new_dataset = await dataset_service.create_dataset(create_request)
        print(f"✅ Created dataset: {new_dataset.id} - {new_dataset.name}")
        
        # 3. Add images to dataset
        print("\n🖼️  Adding images to dataset...")
        colors = ['red', 'green', 'blue']
        for i, color in enumerate(colors):
            image_data = create_test_image_bytes(100, 100, color)
            
            dataset_image = await dataset_service.add_image_to_dataset(
                dataset_id=new_dataset.id,
                file_data=image_data,
                filename=f"demo_{color}_{i}.jpg",
                label=color
            )
            print(f"✅ Added {color} image: {dataset_image.filename}")
        
        # 4. Get dataset statistics
        stats = await dataset_service.get_dataset_statistics(new_dataset.id)
        print(f"\n📈 Dataset statistics:")
        print(f"   Total images: {stats['total_images']}")
        print(f"   Total labels: {stats['total_labels']}")
        print(f"   Label distribution: {stats['label_distribution']}")
        print(f"   Size: {stats['total_size_mb']} MB")
        
        # 5. Clean up
        await dataset_service.delete_dataset(new_dataset.id)
        print(f"✅ Cleaned up dataset: {new_dataset.id}")
        
    except Exception as e:
        print(f"❌ Dataset demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await dataset_service.shutdown()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("✅ Dataset service demo completed")


async def demo_model_service():
    """Demonstrate model service functionality"""
    print("\n🧠 === Model Service Demo ===")
    
    # Initialize services
    model_service = ModelService()
    temp_dir = tempfile.mkdtemp()
    dataset_service = DatasetService(data_root=temp_dir)
    
    try:
        # 1. List existing models
        models = await model_service.get_models()
        print(f"✅ Found {len(models)} existing models")
        for model in models:
            print(f"   - {model.name} ({model.model_type}, accuracy: {model.accuracy})")
        
        # 2. Start model training
        print("\n🏋️  Starting model training...")
        train_request = TrainModelRequest(
            name="Demo Training Model",
            description="A demo model for Phase 3 testing",
            dataset_id="person_detection_v1",  # Use existing sample dataset
            model_type="yolo",
            training_params=TrainingParams(
                epochs=10,  # Short training for demo
                batch_size=8,
                learning_rate=0.001
            )
        )
        
        training_job = await model_service.start_training(train_request, dataset_service)
        print(f"✅ Training job started: {training_job.id}")
        print(f"   Model: {training_job.model_name}")
        print(f"   Status: {training_job.status}")
        print(f"   Total epochs: {training_job.total_epochs}")
        
        # 3. Monitor training progress
        print("\n⏱️  Monitoring training progress...")
        for i in range(20):  # Wait up to 2 seconds
            await asyncio.sleep(0.1)
            
            job = await model_service.get_training_job(training_job.id)
            print(f"   Epoch {job.current_epoch or 0}/{job.total_epochs}, "
                  f"Progress: {job.progress:.1f}%, "
                  f"Status: {job.status}")
            
            if job.status in ["completed", "failed", "cancelled"]:
                break
        
        # 4. Check final status
        final_job = await model_service.get_training_job(training_job.id)
        print(f"\n✅ Training completed!")
        print(f"   Final status: {final_job.status}")
        print(f"   Final progress: {final_job.progress:.1f}%")
        if final_job.accuracy:
            print(f"   Final accuracy: {final_job.accuracy:.3f}")
        
        # 5. Get training statistics
        stats = await model_service.get_model_statistics()
        print(f"\n📊 Model service statistics:")
        print(f"   Total models: {stats['total_models']}")
        print(f"   Active training jobs: {stats['active_training_jobs']}")
        print(f"   Model types: {stats['model_types']}")
        
    except Exception as e:
        print(f"❌ Model demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await model_service.shutdown()
        await dataset_service.shutdown()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("✅ Model service demo completed")


async def demo_system_service():
    """Demonstrate system service functionality"""
    print("\n💻 === System Service Demo ===")
    
    # Initialize all services for comprehensive demo
    system_service = SystemService()
    drone_manager = DroneManager()
    vision_service = VisionService()
    model_service = ModelService()
    temp_dir = tempfile.mkdtemp()
    dataset_service = DatasetService(data_root=temp_dir)
    
    try:
        # 1. Get system status
        print("\n📊 System status:")
        system_status = await system_service.get_system_status(
            drone_manager, vision_service, model_service
        )
        
        print(f"   CPU usage: {system_status.cpu_usage}%")
        print(f"   Memory usage: {system_status.memory_usage}%")
        print(f"   Disk usage: {system_status.disk_usage}%")
        print(f"   Connected drones: {system_status.connected_drones}")
        print(f"   Active tracking: {system_status.active_tracking}")
        print(f"   Running training jobs: {system_status.running_training_jobs}")
        print(f"   Uptime: {system_status.uptime} seconds")
        
        # 2. Check service health
        print("\n🏥 Service health check:")
        health_status = await system_service.get_service_health_status(
            drone_manager, vision_service, model_service, dataset_service
        )
        
        print(f"   Overall status: {health_status['overall_status']}")
        for service_name, health_info in health_status['services'].items():
            status_emoji = "✅" if health_info['status'] == 'healthy' else "❌"
            print(f"   {status_emoji} {service_name}: {health_info['status']}")
        
        # 3. Get performance metrics
        print("\n⚡ Performance metrics:")
        performance = await system_service.get_performance_metrics()
        
        print(f"   CPU cores: {performance['cpu']['count']}")
        print(f"   Memory total: {performance['memory']['total_gb']} GB")
        print(f"   Memory available: {performance['memory']['available_gb']} GB")
        print(f"   Disk total: {performance['disk']['total_gb']} GB")
        print(f"   Disk free: {performance['disk']['free_gb']} GB")
        print(f"   Process count: {performance['processes']['count']}")
        
        # 4. Get metrics history (simulated)
        print("\n📈 Metrics history (last 10 minutes):")
        history = await system_service.get_system_metrics_history(duration_minutes=10)
        print(f"   Data points: {len(history['timestamps'])}")
        print(f"   Average CPU: {sum(history['cpu_usage'])/len(history['cpu_usage']):.1f}%")
        print(f"   Average Memory: {sum(history['memory_usage'])/len(history['memory_usage']):.1f}%")
        
    except Exception as e:
        print(f"❌ System demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await system_service.shutdown()
        await vision_service.shutdown()
        await model_service.shutdown()
        await dataset_service.shutdown()
        await drone_manager.shutdown()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("✅ System service demo completed")


async def demo_complete_workflow():
    """Demonstrate complete ML workflow"""
    print("\n🔄 === Complete ML Workflow Demo ===")
    print("Demonstrating: Dataset creation → Image upload → Model training → Object detection")
    
    # Initialize services
    temp_dir = tempfile.mkdtemp()
    dataset_service = DatasetService(data_root=temp_dir)
    model_service = ModelService()
    vision_service = VisionService()
    
    try:
        # 1. Create dataset
        print("\n📝 Step 1: Creating dataset...")
        dataset_request = CreateDatasetRequest(
            name="Workflow Demo Dataset",
            description="Dataset for complete workflow demonstration"
        )
        dataset = await dataset_service.create_dataset(dataset_request)
        print(f"✅ Created dataset: {dataset.id}")
        
        # 2. Add training images
        print("\n🖼️  Step 2: Adding training images...")
        for i, color in enumerate(['red', 'green', 'blue', 'yellow']):
            for j in range(2):  # 2 images per color
                image_data = create_test_image_bytes(100, 100, color)
                await dataset_service.add_image_to_dataset(
                    dataset_id=dataset.id,
                    file_data=image_data,
                    filename=f"{color}_{j}.jpg",
                    label="colored_object"
                )
        print(f"✅ Added 8 training images")
        
        # 3. Start model training (short for demo)
        print("\n🏋️  Step 3: Starting model training...")
        train_request = TrainModelRequest(
            name="Workflow Demo Model",
            description="Model trained in complete workflow demo",
            dataset_id=dataset.id,
            model_type="yolo",
            training_params=TrainingParams(epochs=5, batch_size=4)
        )
        
        training_job = await model_service.start_training(train_request, dataset_service)
        print(f"✅ Training started: {training_job.id}")
        
        # 4. Wait for training completion
        print("\n⏳ Step 4: Waiting for training completion...")
        for i in range(50):  # Wait up to 5 seconds
            await asyncio.sleep(0.1)
            job = await model_service.get_training_job(training_job.id)
            if i % 10 == 0:  # Print every second
                print(f"   Progress: {job.progress:.1f}% (Status: {job.status})")
            
            if job.status in ["completed", "failed"]:
                break
        
        final_job = await model_service.get_training_job(training_job.id)
        if final_job.status == "completed":
            print(f"✅ Training completed successfully!")
        else:
            print(f"⚠️  Training ended with status: {final_job.status}")
        
        # 5. Test object detection with existing model
        print("\n🔍 Step 5: Testing object detection...")
        test_image = create_test_image_base64(200, 200, 'purple')
        
        detection_result = await vision_service.detect_objects(
            image_data=test_image,
            model_id="yolo_v8_general",  # Use existing model for detection
            confidence_threshold=0.5
        )
        
        print(f"✅ Detection completed!")
        print(f"   Processing time: {detection_result.processing_time:.3f}s")
        print(f"   Objects detected: {len(detection_result.detections)}")
        
        # 6. Clean up
        print("\n🧹 Step 6: Cleaning up...")
        await dataset_service.delete_dataset(dataset.id)
        print(f"✅ Cleaned up dataset")
        
        print("\n🎉 Complete workflow demonstration finished successfully!")
        
    except Exception as e:
        print(f"❌ Workflow demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await dataset_service.shutdown()
        await model_service.shutdown()
        await vision_service.shutdown()
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """Run all Phase 3 demos"""
    print("🚀 Starting Phase 3 Comprehensive Demo")
    print("=" * 50)
    
    demos = [
        ("Vision Service", demo_vision_service),
        ("Dataset Service", demo_dataset_service),
        ("Model Service", demo_model_service),
        ("System Service", demo_system_service),
        ("Complete ML Workflow", demo_complete_workflow)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n🎯 Starting {demo_name} Demo...")
            await demo_func()
            print(f"✅ {demo_name} Demo completed successfully")
        except Exception as e:
            print(f"❌ {demo_name} Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("-" * 30)
    
    print("\n🎉 Phase 3 Comprehensive Demo Completed!")
    print("All major Phase 3 functionalities have been demonstrated.")


if __name__ == "__main__":
    asyncio.run(main())