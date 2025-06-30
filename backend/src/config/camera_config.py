"""
Configuration module for dynamic camera stream generation.

Provides pre-configured scenarios and settings for different testing scenarios.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from backend.src.core.virtual_camera import TrackingObject, TrackingObjectType, MovementPattern


@dataclass
class CameraScenarioConfig:
    """Configuration for a complete camera scenario"""
    name: str
    description: str
    width: int = 640
    height: int = 480
    fps: int = 30
    background_color: tuple = (50, 100, 50)
    tracking_objects: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tracking_objects is None:
            self.tracking_objects = []


class DynamicCameraScenarios:
    """Pre-configured scenarios for dynamic camera testing"""
    
    @staticmethod
    def get_indoor_tracking_scenario() -> CameraScenarioConfig:
        """Indoor person tracking scenario"""
        return CameraScenarioConfig(
            name="indoor_tracking",
            description="Indoor environment with person walking",
            background_color=(40, 80, 60),  # Indoor lighting
            tracking_objects=[
                {
                    'object_type': TrackingObjectType.PERSON,
                    'position': (100, 240),
                    'size': (40, 80),
                    'color': (0, 255, 0),
                    'movement_pattern': MovementPattern.LINEAR,
                    'movement_speed': 15,
                    'movement_params': {'direction': [1, 0]}
                },
                {
                    'object_type': TrackingObjectType.BOX,
                    'position': (500, 200),
                    'size': (30, 30),
                    'color': (139, 69, 19),  # Brown
                    'movement_pattern': MovementPattern.STATIC,
                    'movement_speed': 0
                }
            ]
        )
    
    @staticmethod
    def get_outdoor_vehicle_scenario() -> CameraScenarioConfig:
        """Outdoor vehicle tracking scenario"""
        return CameraScenarioConfig(
            name="outdoor_vehicle",
            description="Outdoor parking lot with moving vehicles",
            background_color=(60, 120, 80),  # Outdoor lighting
            tracking_objects=[
                {
                    'object_type': TrackingObjectType.VEHICLE,
                    'position': (320, 240),
                    'size': (80, 40),
                    'color': (255, 0, 0),  # Blue car
                    'movement_pattern': MovementPattern.CIRCULAR,
                    'movement_speed': 0.8,
                    'movement_params': {'radius': 100, 'center_x': 320, 'center_y': 240}
                },
                {
                    'object_type': TrackingObjectType.VEHICLE,
                    'position': (150, 180),
                    'size': (60, 30),
                    'color': (0, 255, 255),  # Yellow car
                    'movement_pattern': MovementPattern.LINEAR,
                    'movement_speed': 25,
                    'movement_params': {'direction': [0.8, 0.3]}
                }
            ]
        )
    
    @staticmethod
    def get_sports_ball_scenario() -> CameraScenarioConfig:
        """Sports ball tracking scenario"""
        return CameraScenarioConfig(
            name="sports_ball",
            description="Sports field with bouncing ball",
            background_color=(34, 139, 34),  # Green field
            tracking_objects=[
                {
                    'object_type': TrackingObjectType.BALL,
                    'position': (320, 200),
                    'size': (25, 25),
                    'color': (0, 165, 255),  # Orange ball
                    'movement_pattern': MovementPattern.SINE_WAVE,
                    'movement_speed': 2.0,
                    'movement_params': {'amplitude': 60, 'frequency': 1.5}
                },
                {
                    'object_type': TrackingObjectType.PERSON,
                    'position': (200, 300),
                    'size': (35, 70),
                    'color': (255, 255, 0),  # Cyan person
                    'movement_pattern': MovementPattern.RANDOM_WALK,
                    'movement_speed': 10,
                    'movement_params': {}
                }
            ]
        )
    
    @staticmethod
    def get_warehouse_scenario() -> CameraScenarioConfig:
        """Warehouse inspection scenario"""
        return CameraScenarioConfig(
            name="warehouse",
            description="Warehouse with boxes and workers",
            background_color=(45, 75, 65),  # Industrial lighting
            tracking_objects=[
                {
                    'object_type': TrackingObjectType.BOX,
                    'position': (150, 200),
                    'size': (40, 40),
                    'color': (139, 69, 19),  # Brown box
                    'movement_pattern': MovementPattern.STATIC,
                    'movement_speed': 0
                },
                {
                    'object_type': TrackingObjectType.BOX,
                    'position': (300, 180),
                    'size': (35, 35),
                    'color': (160, 82, 45),  # Different brown
                    'movement_pattern': MovementPattern.STATIC,
                    'movement_speed': 0
                },
                {
                    'object_type': TrackingObjectType.PERSON,
                    'position': (400, 250),
                    'size': (40, 75),
                    'color': (255, 165, 0),  # Orange uniform
                    'movement_pattern': MovementPattern.LINEAR,
                    'movement_speed': 12,
                    'movement_params': {'direction': [-0.5, 0.2]}
                },
                {
                    'object_type': TrackingObjectType.VEHICLE,
                    'position': (500, 350),
                    'size': (50, 25),
                    'color': (255, 255, 0),  # Yellow forklift
                    'movement_pattern': MovementPattern.RANDOM_WALK,
                    'movement_speed': 8,
                    'movement_params': {}
                }
            ]
        )
    
    @staticmethod
    def get_emergency_scenario() -> CameraScenarioConfig:
        """Emergency response scenario"""
        return CameraScenarioConfig(
            name="emergency",
            description="Emergency scene with multiple moving objects",
            background_color=(30, 60, 80),  # Low light emergency
            fps=24,  # Slightly lower fps for dramatic effect
            tracking_objects=[
                {
                    'object_type': TrackingObjectType.PERSON,
                    'position': (100, 200),
                    'size': (35, 70),
                    'color': (0, 0, 255),  # Red emergency uniform
                    'movement_pattern': MovementPattern.LINEAR,
                    'movement_speed': 30,  # Fast movement
                    'movement_params': {'direction': [1, 0.2]}
                },
                {
                    'object_type': TrackingObjectType.PERSON,
                    'position': (200, 300),
                    'size': (35, 70),
                    'color': (255, 255, 255),  # White medical uniform
                    'movement_pattern': MovementPattern.RANDOM_WALK,
                    'movement_speed': 20,
                    'movement_params': {}
                },
                {
                    'object_type': TrackingObjectType.VEHICLE,
                    'position': (450, 100),
                    'size': (70, 35),
                    'color': (0, 0, 255),  # Red emergency vehicle
                    'movement_pattern': MovementPattern.CIRCULAR,
                    'movement_speed': 1.2,
                    'movement_params': {'radius': 60, 'center_x': 450, 'center_y': 150}
                }
            ]
        )
    
    @staticmethod
    def get_all_scenarios() -> Dict[str, CameraScenarioConfig]:
        """Get all available scenarios"""
        return {
            'indoor_tracking': DynamicCameraScenarios.get_indoor_tracking_scenario(),
            'outdoor_vehicle': DynamicCameraScenarios.get_outdoor_vehicle_scenario(),
            'sports_ball': DynamicCameraScenarios.get_sports_ball_scenario(),
            'warehouse': DynamicCameraScenarios.get_warehouse_scenario(),
            'emergency': DynamicCameraScenarios.get_emergency_scenario()
        }
    
    @staticmethod
    def create_custom_scenario(name: str, 
                              description: str,
                              objects_config: List[Dict[str, Any]],
                              **kwargs) -> CameraScenarioConfig:
        """Create a custom scenario from configuration"""
        return CameraScenarioConfig(
            name=name,
            description=description,
            tracking_objects=objects_config,
            **kwargs
        )


def configure_stream_from_scenario(stream, scenario: CameraScenarioConfig):
    """Configure a VirtualCameraStream from a scenario configuration"""
    from backend.src.core.virtual_camera import TrackingObject
    
    # Add all tracking objects from the scenario
    for obj_config in scenario.tracking_objects:
        tracking_obj = TrackingObject(
            object_type=obj_config['object_type'],
            position=obj_config['position'],
            size=obj_config['size'],
            color=obj_config['color'],
            movement_pattern=obj_config['movement_pattern'],
            movement_speed=obj_config['movement_speed'],
            movement_params=obj_config.get('movement_params', {})
        )
        stream.add_tracking_object(tracking_obj)
    
    return stream


# Configuration constants
DEFAULT_CAMERA_CONFIGS = {
    'resolution': {
        'HD': (1280, 720),
        'VGA': (640, 480),
        'QVGA': (320, 240)
    },
    'fps_options': [15, 24, 30, 60],
    'background_presets': {
        'indoor': (40, 80, 60),
        'outdoor_day': (60, 120, 80),
        'outdoor_night': (20, 40, 50),
        'warehouse': (45, 75, 65),
        'emergency': (30, 60, 80)
    }
}