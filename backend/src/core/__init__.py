"""
Core modules for Tello EDU Dummy System

Phase 2: Dynamic Camera Stream Generation
"""

from .virtual_camera import (
    VirtualCameraStream,
    VirtualCameraStreamManager,
    TrackingObject,
    TrackingObjectType,
    MovementPattern,
    create_sample_scenario
)

__all__ = [
    'VirtualCameraStream',
    'VirtualCameraStreamManager', 
    'TrackingObject',
    'TrackingObjectType',
    'MovementPattern',
    'create_sample_scenario'
]