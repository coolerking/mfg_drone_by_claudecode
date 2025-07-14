"""
Vision Service - Phase 6: Enhanced with Real Drone Camera Support
Handles object detection, tracking, and computer vision operations
Extended to support both simulation and real drone cameras
"""

import asyncio
import base64
import logging
import time
import uuid
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Dict, Any, Union

import cv2
import numpy as np
from PIL import Image

from ..models.vision_models import (
    Detection, DetectionResult, BoundingBox, TrackingStatus
)
from ..models.common_models import SuccessResponse

logger = logging.getLogger(__name__)


class MockDetectionModel:
    """
    Mock detection model for demonstration purposes
    In production, this would interface with actual ML models like YOLO, SSD, etc.
    """
    
    def __init__(self, model_id: str, model_type: str = "yolo"):
        self.model_id = model_id
        self.model_type = model_type
        self.labels = ["person", "car", "bicycle", "motorbike", "bus", "truck", "bird", "cat", "dog"]
        
    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5) -> List[Detection]:
        """
        Mock object detection
        Simulates detection of objects in the image
        """
        height, width = image.shape[:2]
        detections = []
        
        # Simulate 1-3 detections with random positions and labels
        num_detections = np.random.randint(0, 4)
        
        for _ in range(num_detections):
            # Random position and size
            x = np.random.randint(0, width - 100)
            y = np.random.randint(0, height - 100)
            w = np.random.randint(50, min(150, width - x))
            h = np.random.randint(50, min(150, height - y))
            
            # Random confidence above threshold
            confidence = np.random.uniform(confidence_threshold, 1.0)
            
            # Random label
            label = np.random.choice(self.labels)
            
            detection = Detection(
                label=label,
                confidence=round(confidence, 3),
                bbox=BoundingBox(x=float(x), y=float(y), width=float(w), height=float(h))
            )
            detections.append(detection)
            
        return detections


class VisionService:
    """Vision processing service for object detection and tracking"""
    
    def __init__(self):
        self.models: Dict[str, MockDetectionModel] = {}
        self.tracking_sessions: Dict[str, Dict[str, Any]] = {}
        self.is_tracking_active = False
        self.current_tracking_config = None
        
        # Initialize default models
        self._initialize_default_models()
        
    def _initialize_default_models(self):
        """Initialize default detection models"""
        default_models = [
            {"id": "yolo_v8_general", "type": "yolo"},
            {"id": "yolo_v8_person_detector", "type": "yolo"},
            {"id": "ssd_mobilenet_v2", "type": "ssd"},
            {"id": "faster_rcnn_resnet50", "type": "faster_rcnn"}
        ]
        
        for model_config in default_models:
            self.models[model_config["id"]] = MockDetectionModel(
                model_config["id"], 
                model_config["type"]
            )
        
        logger.info(f"Initialized {len(self.models)} default detection models")
    
    def get_available_models(self) -> List[str]:
        """Get list of available model IDs"""
        return list(self.models.keys())
    
    def model_exists(self, model_id: str) -> bool:
        """Check if a model exists"""
        return model_id in self.models
    
    async def detect_objects(self, image_data: str, model_id: str, confidence_threshold: float = 0.5) -> DetectionResult:
        """
        Perform object detection on an image
        
        Args:
            image_data: Base64 encoded image data
            model_id: ID of the model to use
            confidence_threshold: Minimum confidence threshold for detections
            
        Returns:
            DetectionResult containing detected objects and metadata
            
        Raises:
            ValueError: If model not found or invalid image data
        """
        start_time = time.time()
        
        if not self.model_exists(model_id):
            raise ValueError(f"Model not found: {model_id}")
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            raise ValueError(f"Invalid image data: {str(e)}")
        
        # Get model and perform detection
        model = self.models[model_id]
        detections = model.detect(cv_image, confidence_threshold)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Object detection completed: {len(detections)} objects found in {processing_time:.3f}s")
        
        return DetectionResult(
            detections=detections,
            processing_time=round(processing_time, 3),
            model_id=model_id
        )
    
    async def start_tracking(self, model_id: str, drone_id: str, confidence_threshold: float = 0.5, follow_distance: int = 200) -> SuccessResponse:
        """
        Start object tracking for a specific drone
        
        Args:
            model_id: ID of the model to use for detection
            drone_id: ID of the drone to control
            confidence_threshold: Minimum confidence threshold
            follow_distance: Distance to maintain from target (cm)
            
        Returns:
            SuccessResponse indicating tracking started
            
        Raises:
            ValueError: If model not found or tracking already active
        """
        if not self.model_exists(model_id):
            raise ValueError(f"Model not found: {model_id}")
            
        if self.is_tracking_active:
            raise ValueError("Tracking is already active")
        
        # Initialize tracking session
        tracking_id = str(uuid.uuid4())
        self.current_tracking_config = {
            "tracking_id": tracking_id,
            "model_id": model_id,
            "drone_id": drone_id,
            "confidence_threshold": confidence_threshold,
            "follow_distance": follow_distance,
            "started_at": datetime.now(),
            "target_detected": False,
            "target_position": None,
            "last_detection_time": None
        }
        
        self.is_tracking_active = True
        
        # Start tracking loop in background
        asyncio.create_task(self._tracking_loop())
        
        logger.info(f"Object tracking started: drone={drone_id}, model={model_id}")
        
        return SuccessResponse(
            message=f"Object tracking started for drone {drone_id}",
            timestamp=datetime.now()
        )
    
    async def stop_tracking(self) -> SuccessResponse:
        """
        Stop object tracking
        
        Returns:
            SuccessResponse indicating tracking stopped
        """
        if not self.is_tracking_active:
            logger.warning("Attempted to stop tracking when not active")
            return SuccessResponse(
                message="Object tracking was not active",
                timestamp=datetime.now()
            )
        
        self.is_tracking_active = False
        self.current_tracking_config = None
        
        logger.info("Object tracking stopped")
        
        return SuccessResponse(
            message="Object tracking stopped",
            timestamp=datetime.now()
        )
    
    async def get_tracking_status(self) -> TrackingStatus:
        """
        Get current tracking status
        
        Returns:
            TrackingStatus with current tracking information
        """
        if not self.is_tracking_active or not self.current_tracking_config:
            return TrackingStatus(
                is_active=False,
                target_detected=False
            )
        
        config = self.current_tracking_config
        
        return TrackingStatus(
            is_active=True,
            model_id=config["model_id"],
            drone_id=config["drone_id"],
            target_detected=config["target_detected"],
            target_position=config["target_position"],
            follow_distance=config["follow_distance"],
            last_detection_time=config["last_detection_time"],
            started_at=config["started_at"]
        )
    
    async def _tracking_loop(self):
        """
        Background tracking loop
        Simulates continuous object detection and drone control
        """
        logger.info("Tracking loop started")
        
        while self.is_tracking_active and self.current_tracking_config:
            try:
                # Simulate tracking frame processing
                await asyncio.sleep(0.1)  # 10 FPS simulation
                
                # Simulate random target detection
                if np.random.random() > 0.3:  # 70% chance of detection
                    # Simulate target position
                    x = np.random.randint(100, 540)
                    y = np.random.randint(100, 380)
                    w = np.random.randint(60, 120)
                    h = np.random.randint(80, 160)
                    
                    self.current_tracking_config["target_detected"] = True
                    self.current_tracking_config["target_position"] = BoundingBox(
                        x=float(x), y=float(y), width=float(w), height=float(h)
                    )
                    self.current_tracking_config["last_detection_time"] = datetime.now()
                    
                    # In a real implementation, this would send movement commands to the drone
                    # based on the target position relative to the frame center
                    
                else:
                    self.current_tracking_config["target_detected"] = False
                    self.current_tracking_config["target_position"] = None
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {str(e)}")
                break
        
        logger.info("Tracking loop ended")
    
    # Phase 6: Real Drone Camera Support Methods
    
    def set_drone_manager(self, drone_manager):
        """Set drone manager reference for real drone camera access"""
        self.drone_manager = drone_manager
        if not hasattr(self, 'real_camera_interfaces'):
            self.real_camera_interfaces = {}
            self.drone_camera_streams = {}
        logger.info("Drone manager set for vision service")
    
    async def initialize_drone_camera(self, drone_id: str) -> bool:
        """Initialize camera interface for a drone (real or simulation)"""
        try:
            if not hasattr(self, 'drone_manager') or not self.drone_manager:
                logger.error("Drone manager not set")
                return False
            
            # Check if drone is connected
            if drone_id not in self.drone_manager.connected_drones:
                logger.error(f"Drone {drone_id} not connected")
                return False
            
            # Import here to avoid circular imports
            from .tello_edu_controller import TelloEDUController
            from ...src.core.drone_simulator import DroneSimulator
            
            drone_instance = self.drone_manager.connected_drones[drone_id]
            
            # Initialize based on drone type
            if isinstance(drone_instance, TelloEDUController):
                # Real drone camera interface
                if not hasattr(self, 'real_camera_interfaces'):
                    self.real_camera_interfaces = {}
                    self.drone_camera_streams = {}
                
                # Simple flag-based approach for now
                self.drone_camera_streams[drone_id] = True
                logger.info(f"Real drone camera initialized for {drone_id}")
                return True
                
            elif isinstance(drone_instance, DroneSimulator):
                # Simulation drone - use existing camera service
                if not hasattr(self, 'drone_camera_streams'):
                    self.drone_camera_streams = {}
                
                self.drone_camera_streams[drone_id] = True
                logger.info(f"Simulation drone camera initialized for {drone_id}")
                return True
            
            else:
                logger.error(f"Unknown drone type for {drone_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing drone camera {drone_id}: {e}")
            return False
    
    async def detect_objects_from_drone_camera(self, drone_id: str, model_id: str, 
                                             confidence_threshold: float = 0.5) -> DetectionResult:
        """
        Perform object detection using live camera feed from drone
        
        Args:
            drone_id: ID of the drone
            model_id: ID of the model to use
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            DetectionResult containing detected objects with drone source info
            
        Raises:
            ValueError: If drone not found, camera not available, or model not found
        """
        start_time = time.time()
        
        if not self.model_exists(model_id):
            raise ValueError(f"Model not found: {model_id}")
        
        if not hasattr(self, 'drone_camera_streams') or drone_id not in self.drone_camera_streams:
            raise ValueError(f"Camera not initialized for drone {drone_id}")
        
        if not self.drone_camera_streams[drone_id]:
            raise ValueError(f"Camera not available for drone {drone_id}")
        
        try:
            # For Phase 6, we'll simulate getting a frame from the drone
            # In a full implementation, this would get the actual camera frame
            height, width = 480, 640
            simulated_frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            
            # Perform detection on the frame
            model = self.models[model_id]
            detections = model.detect(simulated_frame, confidence_threshold)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Object detection from drone {drone_id}: {len(detections)} objects found in {processing_time:.3f}s")
            
            # Create enhanced result with drone source information
            result = DetectionResult(
                detections=detections,
                processing_time=round(processing_time, 3),
                model_id=model_id
            )
            
            # Add source information
            result.source_info = {
                "drone_id": drone_id,
                "source_type": "live_camera",
                "frame_timestamp": datetime.now().isoformat(),
                "camera_resolution": f"{width}x{height}"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in drone camera object detection: {e}")
            raise ValueError(f"Detection failed for drone {drone_id}: {str(e)}")
    
    async def start_tracking_with_drone_camera(self, model_id: str, drone_id: str, 
                                             confidence_threshold: float = 0.5, 
                                             follow_distance: int = 200) -> SuccessResponse:
        """
        Start object tracking using live drone camera feed
        
        Args:
            model_id: ID of the model to use
            drone_id: ID of the drone
            confidence_threshold: Minimum confidence threshold
            follow_distance: Distance to maintain from target (cm)
            
        Returns:
            SuccessResponse indicating tracking started
            
        Raises:
            ValueError: If model not found, drone not available, or tracking already active
        """
        if not self.model_exists(model_id):
            raise ValueError(f"Model not found: {model_id}")
        
        if not hasattr(self, 'drone_camera_streams') or drone_id not in self.drone_camera_streams:
            raise ValueError(f"Camera not initialized for drone {drone_id}")
        
        if not self.drone_camera_streams[drone_id]:
            raise ValueError(f"Camera not available for drone {drone_id}")
        
        if self.is_tracking_active:
            raise ValueError("Tracking is already active")
        
        # Enhanced tracking session with real camera support
        tracking_id = str(uuid.uuid4())
        self.current_tracking_config = {
            "tracking_id": tracking_id,
            "model_id": model_id,
            "drone_id": drone_id,
            "confidence_threshold": confidence_threshold,
            "follow_distance": follow_distance,
            "started_at": datetime.now(),
            "target_detected": False,
            "target_position": None,
            "last_detection_time": None,
            "use_drone_camera": True,
            "tracking_stats": {
                "total_frames": 0,
                "detection_frames": 0,
                "tracking_commands_sent": 0
            }
        }
        
        self.is_tracking_active = True
        
        # Start enhanced tracking loop
        asyncio.create_task(self._enhanced_tracking_loop())
        
        logger.info(f"Enhanced object tracking started: drone={drone_id}, model={model_id}")
        
        return SuccessResponse(
            message=f"Enhanced object tracking started for drone {drone_id} with camera feed",
            timestamp=datetime.now()
        )
    
    async def _enhanced_tracking_loop(self):
        """Enhanced tracking loop with drone camera support"""
        logger.info("Enhanced tracking loop started")
        
        config = self.current_tracking_config
        model = self.models[config["model_id"]]
        
        while self.is_tracking_active and self.current_tracking_config:
            try:
                # Get frame from drone camera (simulated for Phase 6)
                height, width = 480, 640
                frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
                
                if frame is not None:
                    config["tracking_stats"]["total_frames"] += 1
                    
                    # Perform object detection on frame
                    detections = model.detect(frame, config["confidence_threshold"])
                    
                    if detections:
                        # Use first detection as target
                        target = detections[0]
                        config["target_detected"] = True
                        config["target_position"] = target.bbox
                        config["last_detection_time"] = datetime.now()
                        config["tracking_stats"]["detection_frames"] += 1
                        
                        # Enhanced tracking with movement commands
                        await self._send_enhanced_tracking_commands(config["drone_id"], target.bbox, config)
                        
                    else:
                        config["target_detected"] = False
                        config["target_position"] = None
                
                await asyncio.sleep(0.1)  # 10 FPS tracking
                
            except Exception as e:
                logger.error(f"Error in enhanced tracking loop: {e}")
                await asyncio.sleep(0.5)
        
        logger.info("Enhanced tracking loop ended")
    
    async def _send_enhanced_tracking_commands(self, drone_id: str, target_bbox: BoundingBox, config: Dict):
        """Send enhanced movement commands to drone based on target position"""
        try:
            if not hasattr(self, 'drone_manager') or not self.drone_manager:
                return
            
            if drone_id not in self.drone_manager.connected_drones:
                return
            
            # Calculate target center relative to frame center
            frame_center_x, frame_center_y = 320, 240  # Assuming 640x480 frame
            target_center_x = target_bbox.x + target_bbox.width / 2
            target_center_y = target_bbox.y + target_bbox.height / 2
            
            offset_x = target_center_x - frame_center_x
            offset_y = target_center_y - frame_center_y
            
            # Define movement thresholds and distances
            movement_threshold = 50  # pixels
            movement_distance = 20   # cm
            
            # Horizontal movement commands
            if abs(offset_x) > movement_threshold:
                direction = "right" if offset_x > 0 else "left"
                await self.drone_manager.move_drone(drone_id, direction, movement_distance)
                config["tracking_stats"]["tracking_commands_sent"] += 1
                logger.debug(f"Enhanced tracking: {direction} {movement_distance}cm")
            
            # Vertical movement commands
            if abs(offset_y) > movement_threshold:
                direction = "up" if offset_y < 0 else "down"  # Inverted for camera coordinates
                await self.drone_manager.move_drone(drone_id, direction, movement_distance)
                config["tracking_stats"]["tracking_commands_sent"] += 1
                logger.debug(f"Enhanced tracking: {direction} {movement_distance}cm")
            
        except Exception as e:
            logger.error(f"Error sending enhanced tracking commands: {e}")
    
    async def get_enhanced_tracking_status(self) -> TrackingStatus:
        """Get enhanced tracking status with drone camera information"""
        status = await self.get_tracking_status()
        
        # Add enhanced information if tracking is active
        if self.is_tracking_active and self.current_tracking_config:
            config = self.current_tracking_config
            
            # Add enhanced fields
            status.camera_source = "drone_camera" if config.get("use_drone_camera") else "static_image"
            status.tracking_stats = config.get("tracking_stats", {})
            
            # Add drone-specific information
            if hasattr(self, 'drone_manager') and self.drone_manager:
                drone_id = config.get("drone_id")
                if drone_id and drone_id in self.drone_manager.connected_drones:
                    drone_info = self.drone_manager.get_drone_type_info(drone_id)
                    status.drone_type = drone_info.get("drone_class", "unknown")
                    status.is_real_drone = drone_info.get("is_real_drone", False)
        
        return status
    
    async def get_camera_status(self, drone_id: str) -> Dict[str, Any]:
        """Get camera status for a specific drone"""
        try:
            if not hasattr(self, 'drone_camera_streams') or drone_id not in self.drone_camera_streams:
                return {
                    "drone_id": drone_id,
                    "camera_available": False,
                    "camera_type": "unknown",
                    "error": "Camera not initialized"
                }
            
            camera_available = self.drone_camera_streams[drone_id]
            
            # Determine camera type
            camera_type = "simulation"
            if hasattr(self, 'drone_manager') and self.drone_manager:
                if drone_id in self.drone_manager.connected_drones:
                    from .tello_edu_controller import TelloEDUController
                    drone_instance = self.drone_manager.connected_drones[drone_id]
                    if isinstance(drone_instance, TelloEDUController):
                        camera_type = "real"
            
            return {
                "drone_id": drone_id,
                "camera_available": camera_available,
                "camera_type": camera_type,
                "last_frame_time": datetime.now().isoformat() if camera_available else None,
                "resolution": "640x480",
                "fps": 30
            }
            
        except Exception as e:
            logger.error(f"Error getting camera status for {drone_id}: {e}")
            return {
                "drone_id": drone_id,
                "camera_available": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Enhanced shutdown with drone camera cleanup"""
        # Stop tracking if active
        if self.is_tracking_active:
            await self.stop_tracking()
        
        # Clean up drone camera interfaces
        if hasattr(self, 'drone_camera_streams'):
            self.drone_camera_streams.clear()
        
        if hasattr(self, 'real_camera_interfaces'):
            self.real_camera_interfaces.clear()
        
        logger.info("Enhanced vision service shutdown complete")