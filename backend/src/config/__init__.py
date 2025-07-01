"""
Configuration modules for Tello EDU Dummy System
"""

from .camera_config import (
    CameraScenarioConfig,
    DynamicCameraScenarios,
    configure_stream_from_scenario,
    DEFAULT_CAMERA_CONFIGS
)

__all__ = [
    'CameraScenarioConfig',
    'DynamicCameraScenarios', 
    'configure_stream_from_scenario',
    'DEFAULT_CAMERA_CONFIGS'
]