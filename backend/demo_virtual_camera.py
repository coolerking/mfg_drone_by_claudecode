#!/usr/bin/env python3
"""
Demo script for Phase 2: Dynamic Camera Stream Generation

This script demonstrates the usage of the VirtualCameraStream system
with various scenarios and configurations.
"""

import sys
import os
import time
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.virtual_camera import (
    VirtualCameraStream,
    VirtualCameraStreamManager,
    TrackingObject,
    TrackingObjectType,
    MovementPattern,
    create_sample_scenario
)
from config.camera_config import (
    DynamicCameraScenarios,
    configure_stream_from_scenario
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_stream():
    """Demonstrate basic virtual camera stream functionality"""
    print("\n=== Demo 1: Basic Virtual Camera Stream ===")
    
    # Create a basic stream
    stream = VirtualCameraStream(width=640, height=480, fps=30)
    
    # Add a simple moving object
    person = TrackingObject(
        object_type=TrackingObjectType.PERSON,
        position=(100, 240),
        size=(40, 80),
        color=(0, 255, 0),  # Green
        movement_pattern=MovementPattern.LINEAR,
        movement_speed=20,
        movement_params={'direction': [1, 0]}
    )
    
    object_id = stream.add_tracking_object(person)
    print(f"Added tracking object: {object_id}")
    
    # Start the stream
    stream.start_stream()
    print("Stream started")
    
    # Monitor for a few seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        frame = stream.get_frame()
        if frame is not None:
            print(f"Got frame: {frame.shape}, dtype: {frame.dtype}")
        time.sleep(1)
    
    # Show statistics
    stats = stream.get_stream_stats()
    print(f"Stream statistics: {stats}")
    
    # Stop the stream
    stream.stop_stream()
    print("Stream stopped\n")


def demo_multiple_objects():
    """Demonstrate multiple tracking objects with different movement patterns"""
    print("\n=== Demo 2: Multiple Tracking Objects ===")
    
    stream = VirtualCameraStream(width=800, height=600, fps=24)
    
    # Add various objects with different movement patterns
    objects = [
        TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(100, 300),
            size=(40, 80),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.LINEAR,
            movement_speed=15,
            movement_params={'direction': [1, 0.2]}
        ),
        TrackingObject(
            object_type=TrackingObjectType.BALL,
            position=(400, 200),
            size=(30, 30),
            color=(0, 0, 255),
            movement_pattern=MovementPattern.SINE_WAVE,
            movement_speed=2.0,
            movement_params={'amplitude': 60, 'frequency': 1.5}
        ),
        TrackingObject(
            object_type=TrackingObjectType.VEHICLE,
            position=(600, 400),
            size=(80, 40),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.CIRCULAR,
            movement_speed=1.0,
            movement_params={'radius': 80, 'center_x': 600, 'center_y': 400}
        ),
        TrackingObject(
            object_type=TrackingObjectType.ANIMAL,
            position=(200, 500),
            size=(50, 30),
            color=(255, 165, 0),
            movement_pattern=MovementPattern.RANDOM_WALK,
            movement_speed=10,
            movement_params={}
        )
    ]
    
    # Add all objects to the stream
    object_ids = []
    for obj in objects:
        obj_id = stream.add_tracking_object(obj)
        object_ids.append(obj_id)
        print(f"Added {obj.object_type.value}: {obj_id}")
    
    # Start streaming
    stream.start_stream()
    print(f"Started stream with {len(objects)} objects")
    
    # Run for a while and show periodic stats
    for i in range(8):
        time.sleep(1)
        stats = stream.get_stream_stats()
        print(f"Second {i+1}: Frame {stats['frame_count']}, "
              f"FPS: {stats['actual_fps']:.1f}")
    
    # Stop the stream
    stream.stop_stream()
    final_stats = stream.get_stream_stats()
    print(f"Final statistics: {final_stats}\n")


def demo_scenario_configurations():
    """Demonstrate pre-configured scenarios"""
    print("\n=== Demo 3: Pre-configured Scenarios ===")
    
    # Get all available scenarios
    scenarios = DynamicCameraScenarios.get_all_scenarios()
    print(f"Available scenarios: {list(scenarios.keys())}")
    
    # Demonstrate indoor tracking scenario
    print("\n--- Indoor Tracking Scenario ---")
    scenario = scenarios['indoor_tracking']
    print(f"Scenario: {scenario.name} - {scenario.description}")
    print(f"Resolution: {scenario.width}x{scenario.height}@{scenario.fps}fps")
    print(f"Objects: {len(scenario.tracking_objects)}")
    
    # Create and configure stream from scenario
    stream = VirtualCameraStream(
        width=scenario.width,
        height=scenario.height,
        fps=scenario.fps,
        background_color=scenario.background_color
    )
    
    configured_stream = configure_stream_from_scenario(stream, scenario)
    
    # Run the scenario
    configured_stream.start_stream()
    time.sleep(3)
    
    stats = configured_stream.get_stream_stats()
    print(f"Scenario stats: {stats}")
    
    configured_stream.stop_stream()
    
    # Demonstrate another scenario
    print("\n--- Sports Ball Scenario ---")
    sports_scenario = scenarios['sports_ball']
    sports_stream = VirtualCameraStream(
        width=sports_scenario.width,
        height=sports_scenario.height,
        fps=sports_scenario.fps,
        background_color=sports_scenario.background_color
    )
    
    configure_stream_from_scenario(sports_stream, sports_scenario)
    sports_stream.start_stream()
    time.sleep(3)
    
    sports_stats = sports_stream.get_stream_stats()
    print(f"Sports scenario stats: {sports_stats}")
    
    sports_stream.stop_stream()
    print()


def demo_stream_manager():
    """Demonstrate the stream manager functionality"""
    print("\n=== Demo 4: Stream Manager ===")
    
    manager = VirtualCameraStreamManager()
    
    # Create multiple streams
    stream_configs = [
        ('camera_1', 640, 480, 30),
        ('camera_2', 320, 240, 15),
        ('camera_3', 800, 600, 24)
    ]
    
    for stream_id, width, height, fps in stream_configs:
        stream = manager.create_stream(stream_id, width, height, fps)
        print(f"Created stream: {stream_id} ({width}x{height}@{fps}fps)")
        
        # Add a simple object to each stream
        obj = TrackingObject(
            object_type=TrackingObjectType.BOX,
            position=(width//2, height//2),
            size=(30, 30),
            color=(255, 255, 0),
            movement_pattern=MovementPattern.CIRCULAR,
            movement_speed=1.0,
            movement_params={'radius': 50, 'center_x': width//2, 'center_y': height//2}
        )
        stream.add_tracking_object(obj)
        stream.start_stream()
    
    print(f"Created {len(manager.streams)} streams")
    
    # Monitor all streams
    for i in range(5):
        time.sleep(1)
        all_stats = manager.get_all_stream_stats()
        
        print(f"\nSecond {i+1} - All stream statistics:")
        for stream_id, stats in all_stats.items():
            print(f"  {stream_id}: Frame {stats['frame_count']}, "
                  f"FPS: {stats['actual_fps']:.1f}")
    
    # Stop all streams
    manager.stop_all_streams()
    print("\nAll streams stopped")
    
    # Show final statistics
    final_stats = manager.get_all_stream_stats()
    print("\nFinal statistics:")
    for stream_id, stats in final_stats.items():
        print(f"  {stream_id}: {stats}")
    
    print()


def demo_sample_scenario():
    """Demonstrate the built-in sample scenario"""
    print("\n=== Demo 5: Sample Scenario ===")
    
    # Create the sample scenario
    stream = create_sample_scenario()
    print("Created sample scenario with multiple objects")
    
    # Start streaming
    stream.start_stream()
    
    # Monitor the sample scenario
    start_time = time.time()
    frame_samples = []
    
    while time.time() - start_time < 6:
        frame = stream.get_frame()
        if frame is not None:
            frame_samples.append(frame.shape)
        time.sleep(0.5)
    
    # Show frame information
    if frame_samples:
        print(f"Captured {len(frame_samples)} frame samples")
        print(f"Frame shape: {frame_samples[0]}")
        print(f"Consistent shapes: {all(shape == frame_samples[0] for shape in frame_samples)}")
    
    # Final statistics
    final_stats = stream.get_stream_stats()
    print(f"Sample scenario final stats: {final_stats}")
    
    stream.stop_stream()
    print()


def main():
    """Run all demonstrations"""
    print("🎥 Virtual Camera Stream Phase 2 Demonstration")
    print("=" * 50)
    
    try:
        # Run all demos
        demo_basic_stream()
        demo_multiple_objects()
        demo_scenario_configurations()
        demo_stream_manager()
        demo_sample_scenario()
        
        print("✅ All demonstrations completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        logger.exception("Demonstration failed")
    
    print("\n🎬 Phase 2 Dynamic Camera Stream Generation Demo Complete")


if __name__ == "__main__":
    main()