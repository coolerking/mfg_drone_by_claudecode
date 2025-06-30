"""
Test suite for Phase 2: Dynamic Camera Stream Generation

Tests for VirtualCameraStream, tracking objects, and scenario configurations.
"""

import unittest
import time
import numpy as np
from unittest.mock import Mock, patch

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

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


class TestTrackingObject(unittest.TestCase):
    """Test TrackingObject configuration"""
    
    def test_tracking_object_creation(self):
        """Test basic tracking object creation"""
        obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(100, 200),
            size=(40, 60),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.LINEAR,
            movement_speed=10.0
        )
        
        self.assertEqual(obj.object_type, TrackingObjectType.PERSON)
        self.assertEqual(obj.position, (100, 200))
        self.assertEqual(obj.size, (40, 60))
        self.assertEqual(obj.color, (0, 255, 0))
        self.assertEqual(obj.movement_pattern, MovementPattern.LINEAR)
        self.assertEqual(obj.movement_speed, 10.0)
        self.assertEqual(obj.movement_params, {})  # Default empty dict
    
    def test_tracking_object_with_params(self):
        """Test tracking object with movement parameters"""
        params = {'direction': [1, 0], 'speed_modifier': 1.5}
        obj = TrackingObject(
            object_type=TrackingObjectType.VEHICLE,
            position=(300, 400),
            size=(80, 40),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.CIRCULAR,
            movement_speed=5.0,
            movement_params=params
        )
        
        self.assertEqual(obj.movement_params, params)


class TestVirtualCameraStream(unittest.TestCase):
    """Test VirtualCameraStream functionality"""
    
    def setUp(self):
        """Set up test camera stream"""
        self.stream = VirtualCameraStream(width=320, height=240, fps=10)
    
    def tearDown(self):
        """Clean up after tests"""
        if self.stream._streaming:
            self.stream.stop_stream()
    
    def test_stream_initialization(self):
        """Test camera stream initialization"""
        self.assertEqual(self.stream.width, 320)
        self.assertEqual(self.stream.height, 240)
        self.assertEqual(self.stream.fps, 10)
        self.assertFalse(self.stream._streaming)
        self.assertEqual(len(self.stream.tracking_objects), 0)
    
    def test_add_tracking_object(self):
        """Test adding tracking objects"""
        obj = TrackingObject(
            object_type=TrackingObjectType.BALL,
            position=(160, 120),
            size=(20, 20),
            color=(0, 0, 255),
            movement_pattern=MovementPattern.STATIC
        )
        
        object_id = self.stream.add_tracking_object(obj)
        
        self.assertEqual(len(self.stream.tracking_objects), 1)
        self.assertIn(object_id, self.stream._object_states)
        self.assertTrue(object_id.startswith('ball_'))
    
    def test_remove_tracking_object(self):
        """Test removing tracking objects"""
        obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(100, 100),
            size=(30, 50),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.STATIC
        )
        
        object_id = self.stream.add_tracking_object(obj)
        self.assertEqual(len(self.stream.tracking_objects), 1)
        
        removed = self.stream.remove_tracking_object(object_id)
        self.assertTrue(removed)
        self.assertEqual(len(self.stream.tracking_objects), 0)
        self.assertNotIn(object_id, self.stream._object_states)
    
    def test_stream_start_stop(self):
        """Test stream start/stop functionality"""
        self.assertFalse(self.stream._streaming)
        
        self.stream.start_stream()
        self.assertTrue(self.stream._streaming)
        self.assertIsNotNone(self.stream._stream_thread)
        
        # Give it a moment to start
        time.sleep(0.1)
        
        self.stream.stop_stream()
        self.assertFalse(self.stream._streaming)
    
    def test_frame_generation(self):
        """Test frame generation"""
        # Add a simple object
        obj = TrackingObject(
            object_type=TrackingObjectType.BOX,
            position=(160, 120),
            size=(40, 40),
            color=(255, 255, 0),
            movement_pattern=MovementPattern.STATIC
        )
        self.stream.add_tracking_object(obj)
        
        self.stream.start_stream()
        time.sleep(0.2)  # Let it generate some frames
        
        frame = self.stream.get_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (240, 320, 3))  # height, width, channels
        self.assertEqual(frame.dtype, np.uint8)
        
    def test_stream_stats(self):
        """Test stream statistics"""
        stats = self.stream.get_stream_stats()
        self.assertEqual(stats['status'], 'not_started')
        
        self.stream.start_stream()
        time.sleep(0.1)
        
        stats = self.stream.get_stream_stats()
        self.assertEqual(stats['status'], 'running')
        self.assertIn('frame_count', stats)
        self.assertIn('actual_fps', stats)
        self.assertEqual(stats['objects_count'], 0)


class TestVirtualCameraStreamManager(unittest.TestCase):
    """Test VirtualCameraStreamManager functionality"""
    
    def setUp(self):
        """Set up test manager"""
        self.manager = VirtualCameraStreamManager()
    
    def tearDown(self):
        """Clean up after tests"""
        self.manager.stop_all_streams()
    
    def test_create_stream(self):
        """Test stream creation"""
        stream = self.manager.create_stream('test_stream', width=640, height=480)
        
        self.assertIsInstance(stream, VirtualCameraStream)
        self.assertEqual(stream.width, 640)
        self.assertEqual(stream.height, 480)
        self.assertIn('test_stream', self.manager.streams)
    
    def test_duplicate_stream_error(self):
        """Test error when creating duplicate stream"""
        self.manager.create_stream('test_stream')
        
        with self.assertRaises(ValueError):
            self.manager.create_stream('test_stream')
    
    def test_get_stream(self):
        """Test getting existing stream"""
        created_stream = self.manager.create_stream('test_stream')
        retrieved_stream = self.manager.get_stream('test_stream')
        
        self.assertIs(created_stream, retrieved_stream)
        
        non_existent = self.manager.get_stream('non_existent')
        self.assertIsNone(non_existent)
    
    def test_remove_stream(self):
        """Test stream removal"""
        self.manager.create_stream('test_stream')
        self.assertIn('test_stream', self.manager.streams)
        
        removed = self.manager.remove_stream('test_stream')
        self.assertTrue(removed)
        self.assertNotIn('test_stream', self.manager.streams)
        
        # Try to remove non-existent stream
        removed_again = self.manager.remove_stream('test_stream')
        self.assertFalse(removed_again)
    
    def test_stop_all_streams(self):
        """Test stopping all streams"""
        stream1 = self.manager.create_stream('stream1')
        stream2 = self.manager.create_stream('stream2')
        
        stream1.start_stream()
        stream2.start_stream()
        time.sleep(0.1)
        
        self.assertTrue(stream1._streaming)
        self.assertTrue(stream2._streaming)
        
        self.manager.stop_all_streams()
        time.sleep(0.1)
        
        self.assertFalse(stream1._streaming)
        self.assertFalse(stream2._streaming)
    
    def test_get_all_stream_stats(self):
        """Test getting statistics for all streams"""
        self.manager.create_stream('stream1')
        self.manager.create_stream('stream2')
        
        stats = self.manager.get_all_stream_stats()
        
        self.assertIn('stream1', stats)
        self.assertIn('stream2', stats)
        self.assertEqual(stats['stream1']['status'], 'not_started')
        self.assertEqual(stats['stream2']['status'], 'not_started')


class TestCameraScenarios(unittest.TestCase):
    """Test pre-configured camera scenarios"""
    
    def test_indoor_tracking_scenario(self):
        """Test indoor tracking scenario configuration"""
        scenario = DynamicCameraScenarios.get_indoor_tracking_scenario()
        
        self.assertEqual(scenario.name, 'indoor_tracking')
        self.assertIsInstance(scenario.description, str)
        self.assertEqual(scenario.width, 640)
        self.assertEqual(scenario.height, 480)
        self.assertEqual(len(scenario.tracking_objects), 2)  # Person and box
    
    def test_outdoor_vehicle_scenario(self):
        """Test outdoor vehicle scenario configuration"""
        scenario = DynamicCameraScenarios.get_outdoor_vehicle_scenario()
        
        self.assertEqual(scenario.name, 'outdoor_vehicle')
        self.assertEqual(len(scenario.tracking_objects), 2)  # Two vehicles
        
        # Check first vehicle is circular movement
        vehicle1 = scenario.tracking_objects[0]
        self.assertEqual(vehicle1['object_type'], TrackingObjectType.VEHICLE)
        self.assertEqual(vehicle1['movement_pattern'], MovementPattern.CIRCULAR)
    
    def test_all_scenarios(self):
        """Test getting all scenarios"""
        scenarios = DynamicCameraScenarios.get_all_scenarios()
        
        expected_scenarios = ['indoor_tracking', 'outdoor_vehicle', 'sports_ball', 
                            'warehouse', 'emergency']
        
        for scenario_name in expected_scenarios:
            self.assertIn(scenario_name, scenarios)
            self.assertIsInstance(scenarios[scenario_name].tracking_objects, list)
    
    def test_configure_stream_from_scenario(self):
        """Test configuring stream from scenario"""
        stream = VirtualCameraStream()
        scenario = DynamicCameraScenarios.get_sports_ball_scenario()
        
        configured_stream = configure_stream_from_scenario(stream, scenario)
        
        self.assertIs(configured_stream, stream)
        self.assertEqual(len(stream.tracking_objects), len(scenario.tracking_objects))


class TestSampleScenario(unittest.TestCase):
    """Test the create_sample_scenario function"""
    
    def test_create_sample_scenario(self):
        """Test sample scenario creation"""
        stream = create_sample_scenario()
        
        self.assertIsInstance(stream, VirtualCameraStream)
        self.assertEqual(stream.width, 640)
        self.assertEqual(stream.height, 480)
        self.assertEqual(stream.fps, 30)
        self.assertEqual(len(stream.tracking_objects), 3)  # Person, ball, vehicle
        
        # Test that we can start and get frames
        stream.start_stream()
        time.sleep(0.2)
        
        frame = stream.get_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))
        
        stream.stop_stream()


class TestMovementPatterns(unittest.TestCase):
    """Test different movement patterns"""
    
    def setUp(self):
        """Set up test stream"""
        self.stream = VirtualCameraStream(width=320, height=240, fps=10)
    
    def tearDown(self):
        """Clean up"""
        if self.stream._streaming:
            self.stream.stop_stream()
    
    def test_static_movement(self):
        """Test static movement pattern"""
        obj = TrackingObject(
            object_type=TrackingObjectType.BOX,
            position=(100, 100),
            size=(20, 20),
            color=(255, 0, 0),
            movement_pattern=MovementPattern.STATIC
        )
        
        object_id = self.stream.add_tracking_object(obj)
        initial_pos = self.stream._object_states[object_id]['current_position']
        
        # Simulate time passing
        self.stream._update_object_position(obj, object_id, time.time() + 1)
        final_pos = self.stream._object_states[object_id]['current_position']
        
        # Position should not change for static objects
        self.assertEqual(initial_pos, final_pos)
    
    def test_linear_movement(self):
        """Test linear movement pattern"""
        obj = TrackingObject(
            object_type=TrackingObjectType.PERSON,
            position=(50, 50),
            size=(30, 50),
            color=(0, 255, 0),
            movement_pattern=MovementPattern.LINEAR,
            movement_speed=10,
            movement_params={'direction': [1, 0]}
        )
        
        object_id = self.stream.add_tracking_object(obj)
        initial_pos = self.stream._object_states[object_id]['current_position'][0]
        
        # Simulate 1 second passing
        self.stream._update_object_position(obj, object_id, time.time() + 1)
        final_pos = self.stream._object_states[object_id]['current_position'][0]
        
        # X position should increase
        self.assertGreater(final_pos, initial_pos)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests
    
    # Run the tests
    unittest.main(verbosity=2)