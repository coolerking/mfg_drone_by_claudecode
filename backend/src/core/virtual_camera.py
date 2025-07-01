"""
Phase 2: Dynamic Camera Stream Generation for Tello EDU Dummy System

Virtual camera stream with dynamic content generation using OpenCV.
Supports real-time tracking target composition and frame rate control.
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class TrackingObjectType(Enum):
    """Types of tracking objects that can be generated"""
    PERSON = "person"
    VEHICLE = "vehicle"
    BALL = "ball"
    BOX = "box"
    ANIMAL = "animal"


class MovementPattern(Enum):
    """Movement patterns for tracking objects"""
    STATIC = "static"
    LINEAR = "linear"
    CIRCULAR = "circular"
    RANDOM_WALK = "random_walk"
    SINE_WAVE = "sine_wave"


@dataclass
class TrackingObject:
    """Configuration for a tracking object in the virtual scene"""
    object_type: TrackingObjectType
    position: Tuple[float, float]  # x, y in pixels
    size: Tuple[int, int]  # width, height in pixels
    color: Tuple[int, int, int]  # BGR color
    movement_pattern: MovementPattern
    movement_speed: float = 1.0
    movement_params: Dict[str, Any] = None  # Pattern-specific parameters
    
    def __post_init__(self):
        if self.movement_params is None:
            self.movement_params = {}


class VirtualCameraStream:
    """
    Dynamic camera stream generator for Tello EDU dummy system.
    
    Creates real-time video streams with dynamic tracking objects,
    simulating realistic drone camera footage for testing and development.
    """
    
    def __init__(self, 
                 width: int = 640,
                 height: int = 480,
                 fps: int = 30,
                 background_color: Tuple[int, int, int] = (50, 100, 50)):
        """
        Initialize virtual camera stream.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels  
            fps: Target frames per second
            background_color: Background color (BGR)
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.background_color = background_color
        
        # Stream control
        self._streaming = False
        self._stream_thread = None
        self._frame_lock = threading.Lock()
        self._current_frame = None
        
        # Frame timing
        self._frame_interval = 1.0 / fps
        self._last_frame_time = 0
        
        # Tracking objects
        self.tracking_objects: List[TrackingObject] = []
        self._object_states = {}  # Runtime state for each object
        
        # Performance monitoring
        self._frame_count = 0
        self._start_time = None
        
        logger.info(f"VirtualCameraStream initialized: {width}x{height}@{fps}fps")
    
    def add_tracking_object(self, tracking_object: TrackingObject) -> str:
        """
        Add a tracking object to the virtual scene.
        
        Args:
            tracking_object: Object configuration
            
        Returns:
            object_id: Unique identifier for the object
        """
        object_id = f"{tracking_object.object_type.value}_{len(self.tracking_objects)}"
        self.tracking_objects.append(tracking_object)
        
        # Initialize object state
        self._object_states[object_id] = {
            'current_position': list(tracking_object.position),
            'time_offset': time.time(),
            'angle': 0.0,  # For circular/sine wave movement
            'direction': [random.uniform(-1, 1), random.uniform(-1, 1)]  # For random walk
        }
        
        logger.info(f"Added tracking object: {object_id}")
        return object_id
    
    def remove_tracking_object(self, object_id: str) -> bool:
        """Remove a tracking object by ID"""
        for i, obj in enumerate(self.tracking_objects):
            if f"{obj.object_type.value}_{i}" == object_id:
                del self.tracking_objects[i]
                del self._object_states[object_id]
                logger.info(f"Removed tracking object: {object_id}")
                return True
        return False
    
    def start_stream(self):
        """Start the dynamic video stream"""
        if self._streaming:
            logger.warning("Stream is already running")
            return
        
        self._streaming = True
        self._start_time = time.time()
        self._frame_count = 0
        
        self._stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._stream_thread.start()
        
        logger.info("Virtual camera stream started")
    
    def stop_stream(self):
        """Stop the video stream"""
        if not self._streaming:
            return
        
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=1.0)
        
        # Calculate final stats
        if self._start_time:
            duration = time.time() - self._start_time
            actual_fps = self._frame_count / duration if duration > 0 else 0
            logger.info(f"Stream stopped. Actual FPS: {actual_fps:.2f}")
        
        logger.info("Virtual camera stream stopped")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame from the stream.
        
        Returns:
            Current frame as numpy array, or None if stream not active
        """
        with self._frame_lock:
            return self._current_frame.copy() if self._current_frame is not None else None
    
    def _stream_loop(self):
        """Main streaming loop (runs in separate thread)"""
        while self._streaming:
            start_time = time.time()
            
            # Generate new frame
            frame = self._generate_frame()
            
            # Update current frame
            with self._frame_lock:
                self._current_frame = frame
            
            self._frame_count += 1
            
            # Frame rate control
            elapsed = time.time() - start_time
            sleep_time = max(0, self._frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            # Log performance every 100 frames
            if self._frame_count % 100 == 0:
                duration = time.time() - self._start_time
                actual_fps = self._frame_count / duration
                logger.debug(f"Frame {self._frame_count}, FPS: {actual_fps:.2f}")
    
    def _generate_frame(self) -> np.ndarray:
        """Generate a single frame with dynamic content"""
        # Create background
        frame = np.full((self.height, self.width, 3), self.background_color, dtype=np.uint8)
        
        # Add grid pattern for depth perception
        self._add_grid_pattern(frame)
        
        # Update and draw tracking objects
        current_time = time.time()
        for i, obj in enumerate(self.tracking_objects):
            object_id = f"{obj.object_type.value}_{i}"
            self._update_object_position(obj, object_id, current_time)
            self._draw_tracking_object(frame, obj, object_id)
        
        # Add timestamp
        self._add_timestamp(frame, current_time)
        
        # Add frame counter
        self._add_frame_counter(frame)
        
        return frame
    
    def _add_grid_pattern(self, frame: np.ndarray):
        """Add subtle grid pattern for depth perception"""
        grid_size = 50
        grid_color = tuple(int(c * 1.2) for c in self.background_color)
        
        # Vertical lines
        for x in range(0, self.width, grid_size):
            cv2.line(frame, (x, 0), (x, self.height), grid_color, 1)
        
        # Horizontal lines
        for y in range(0, self.height, grid_size):
            cv2.line(frame, (0, y), (self.width, y), grid_color, 1)
    
    def _update_object_position(self, obj: TrackingObject, object_id: str, current_time: float):
        """Update object position based on movement pattern"""
        state = self._object_states[object_id]
        elapsed = current_time - state['time_offset']
        
        if obj.movement_pattern == MovementPattern.STATIC:
            # No movement
            return
        
        elif obj.movement_pattern == MovementPattern.LINEAR:
            # Linear movement
            direction = obj.movement_params.get('direction', [1, 0])
            dx = direction[0] * obj.movement_speed * elapsed
            dy = direction[1] * obj.movement_speed * elapsed
            
            state['current_position'][0] = (obj.position[0] + dx) % self.width
            state['current_position'][1] = (obj.position[1] + dy) % self.height
        
        elif obj.movement_pattern == MovementPattern.CIRCULAR:
            # Circular movement
            radius = obj.movement_params.get('radius', 50)
            center_x = obj.movement_params.get('center_x', obj.position[0])
            center_y = obj.movement_params.get('center_y', obj.position[1])
            
            angle = elapsed * obj.movement_speed * 0.5  # Slow down rotation
            state['current_position'][0] = center_x + radius * math.cos(angle)
            state['current_position'][1] = center_y + radius * math.sin(angle)
        
        elif obj.movement_pattern == MovementPattern.SINE_WAVE:
            # Sine wave movement
            amplitude = obj.movement_params.get('amplitude', 30)
            frequency = obj.movement_params.get('frequency', 1.0)
            
            offset_y = amplitude * math.sin(elapsed * frequency * obj.movement_speed)
            state['current_position'][0] = (obj.position[0] + elapsed * obj.movement_speed) % self.width
            state['current_position'][1] = obj.position[1] + offset_y
        
        elif obj.movement_pattern == MovementPattern.RANDOM_WALK:
            # Random walk movement
            if elapsed - state.get('last_direction_change', 0) > 2.0:  # Change direction every 2 seconds
                state['direction'] = [random.uniform(-1, 1), random.uniform(-1, 1)]
                state['last_direction_change'] = elapsed
            
            dx = state['direction'][0] * obj.movement_speed * 0.5
            dy = state['direction'][1] * obj.movement_speed * 0.5
            
            # Keep within bounds
            new_x = max(0, min(self.width, state['current_position'][0] + dx))
            new_y = max(0, min(self.height, state['current_position'][1] + dy))
            
            state['current_position'] = [new_x, new_y]
    
    def _draw_tracking_object(self, frame: np.ndarray, obj: TrackingObject, object_id: str):
        """Draw a tracking object on the frame"""
        state = self._object_states[object_id]
        pos = state['current_position']
        x, y = int(pos[0]), int(pos[1])
        
        # Ensure object is within frame bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        
        if obj.object_type == TrackingObjectType.PERSON:
            self._draw_person(frame, x, y, obj.size, obj.color)
        elif obj.object_type == TrackingObjectType.VEHICLE:
            self._draw_vehicle(frame, x, y, obj.size, obj.color)
        elif obj.object_type == TrackingObjectType.BALL:
            self._draw_ball(frame, x, y, obj.size, obj.color)
        elif obj.object_type == TrackingObjectType.BOX:
            self._draw_box(frame, x, y, obj.size, obj.color)
        elif obj.object_type == TrackingObjectType.ANIMAL:
            self._draw_animal(frame, x, y, obj.size, obj.color)
    
    def _draw_person(self, frame: np.ndarray, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a simplified person figure"""
        w, h = size
        # Head
        cv2.circle(frame, (x, y - h//3), w//4, color, -1)
        # Body
        cv2.rectangle(frame, (x - w//4, y - h//3), (x + w//4, y + h//3), color, -1)
        # Arms
        cv2.line(frame, (x - w//4, y - h//6), (x - w//2, y), color, 3)
        cv2.line(frame, (x + w//4, y - h//6), (x + w//2, y), color, 3)
        # Legs
        cv2.line(frame, (x, y + h//3), (x - w//4, y + h//2), color, 3)
        cv2.line(frame, (x, y + h//3), (x + w//4, y + h//2), color, 3)
    
    def _draw_vehicle(self, frame: np.ndarray, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a simplified vehicle"""
        w, h = size
        # Main body
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), color, -1)
        # Wheels
        wheel_color = tuple(int(c * 0.3) for c in color)  # Darker wheels
        cv2.circle(frame, (x - w//3, y + h//3), h//6, wheel_color, -1)
        cv2.circle(frame, (x + w//3, y + h//3), h//6, wheel_color, -1)
    
    def _draw_ball(self, frame: np.ndarray, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a ball"""
        radius = min(size) // 2
        cv2.circle(frame, (x, y), radius, color, -1)
        # Add highlight
        highlight_color = tuple(min(255, int(c * 1.5)) for c in color)
        cv2.circle(frame, (x - radius//3, y - radius//3), radius//3, highlight_color, -1)
    
    def _draw_box(self, frame: np.ndarray, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a box"""
        w, h = size
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), color, -1)
        # Add edge lines for 3D effect
        edge_color = tuple(int(c * 0.7) for c in color)
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), edge_color, 2)
    
    def _draw_animal(self, frame: np.ndarray, x: int, y: int, size: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a simplified animal (cat/dog-like)"""
        w, h = size
        # Body (ellipse)
        cv2.ellipse(frame, (x, y), (w//2, h//4), 0, 0, 360, color, -1)
        # Head
        cv2.circle(frame, (x - w//3, y - h//6), h//5, color, -1)
        # Tail
        cv2.ellipse(frame, (x + w//3, y), (w//4, h//8), 45, 0, 180, color, -1)
    
    def _add_timestamp(self, frame: np.ndarray, current_time: float):
        """Add timestamp to frame"""
        timestamp = time.strftime("%H:%M:%S", time.localtime(current_time))
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def _add_frame_counter(self, frame: np.ndarray):
        """Add frame counter to frame"""
        counter_text = f"Frame: {self._frame_count}"
        cv2.putText(frame, counter_text, (10, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """Get current stream statistics"""
        if self._start_time is None:
            return {"status": "not_started"}
        
        current_time = time.time()
        duration = current_time - self._start_time
        actual_fps = self._frame_count / duration if duration > 0 else 0
        
        return {
            "status": "running" if self._streaming else "stopped",
            "frame_count": self._frame_count,
            "duration": duration,
            "target_fps": self.fps,
            "actual_fps": actual_fps,
            "objects_count": len(self.tracking_objects)
        }


class VirtualCameraStreamManager:
    """
    Manager class for multiple virtual camera streams.
    Supports different camera configurations for various drone scenarios.
    """
    
    def __init__(self):
        self.streams: Dict[str, VirtualCameraStream] = {}
        self.logger = logging.getLogger(__name__ + ".Manager")
    
    def create_stream(self, 
                     stream_id: str,
                     width: int = 640,
                     height: int = 480,
                     fps: int = 30,
                     background_color: Tuple[int, int, int] = (50, 100, 50)) -> VirtualCameraStream:
        """Create a new virtual camera stream"""
        if stream_id in self.streams:
            raise ValueError(f"Stream '{stream_id}' already exists")
        
        stream = VirtualCameraStream(width, height, fps, background_color)
        self.streams[stream_id] = stream
        self.logger.info(f"Created stream: {stream_id}")
        return stream
    
    def get_stream(self, stream_id: str) -> Optional[VirtualCameraStream]:
        """Get an existing stream by ID"""
        return self.streams.get(stream_id)
    
    def remove_stream(self, stream_id: str) -> bool:
        """Remove a stream by ID"""
        if stream_id not in self.streams:
            return False
        
        stream = self.streams[stream_id]
        stream.stop_stream()
        del self.streams[stream_id]
        self.logger.info(f"Removed stream: {stream_id}")
        return True
    
    def stop_all_streams(self):
        """Stop all active streams"""
        for stream in self.streams.values():
            stream.stop_stream()
        self.logger.info("Stopped all streams")
    
    def get_all_stream_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all streams"""
        return {stream_id: stream.get_stream_stats() 
                for stream_id, stream in self.streams.items()}


# Example usage and testing functions
def create_sample_scenario() -> VirtualCameraStream:
    """Create a sample scenario for testing"""
    stream = VirtualCameraStream(width=640, height=480, fps=30)
    
    # Add a moving person
    person = TrackingObject(
        object_type=TrackingObjectType.PERSON,
        position=(100, 200),
        size=(40, 60),
        color=(0, 255, 0),  # Green
        movement_pattern=MovementPattern.LINEAR,
        movement_speed=20,
        movement_params={'direction': [1, 0]}
    )
    stream.add_tracking_object(person)
    
    # Add a bouncing ball
    ball = TrackingObject(
        object_type=TrackingObjectType.BALL,
        position=(300, 150),
        size=(30, 30),
        color=(0, 0, 255),  # Red
        movement_pattern=MovementPattern.SINE_WAVE,
        movement_speed=1.5,
        movement_params={'amplitude': 50, 'frequency': 2.0}
    )
    stream.add_tracking_object(ball)
    
    # Add a circling vehicle
    vehicle = TrackingObject(
        object_type=TrackingObjectType.VEHICLE,
        position=(400, 300),
        size=(60, 30),
        color=(255, 0, 0),  # Blue
        movement_pattern=MovementPattern.CIRCULAR,
        movement_speed=1.0,
        movement_params={'radius': 80, 'center_x': 400, 'center_y': 300}
    )
    stream.add_tracking_object(vehicle)
    
    return stream


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create and start a sample stream
    stream = create_sample_scenario()
    stream.start_stream()
    
    try:
        # Run for 10 seconds
        time.sleep(10)
        
        # Get some frames
        for i in range(5):
            frame = stream.get_frame()
            if frame is not None:
                print(f"Got frame {i}: {frame.shape}")
            time.sleep(0.5)
        
        # Show stats
        stats = stream.get_stream_stats()
        print(f"Stream stats: {stats}")
        
    finally:
        stream.stop_stream()
        print("Stream stopped")