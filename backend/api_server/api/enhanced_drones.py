"""
Enhanced Drone Control API - Phase 3
Advanced drone control endpoints with precision flight, safety features, and learning data collection
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBearer

from ..models.drone_models import (
    Drone, DroneStatus, TakeoffCommand, MoveCommand, RotateCommand, 
    AltitudeCommand, OperationResponse, Photo, FlightPlanRequest,
    LearningDataCollectionRequest, EnhancedDroneStatus, FlightLog,
    SafetyViolation, DroneMetrics
)
from ..models.vision_models import DetectionResult, TrackingStatus
from ..models.common_models import SuccessResponse, ErrorResponse
from ..core.enhanced_drone_manager import EnhancedDroneManager
from ..core.enhanced_vision_service import EnhancedVisionService
from ..security import get_api_key_header, api_key_manager

logger = logging.getLogger(__name__)

# Global service instances (will be initialized in main.py)
enhanced_drone_manager: Optional[EnhancedDroneManager] = None
enhanced_vision_service: Optional[EnhancedVisionService] = None

router = APIRouter()
security = HTTPBearer()


def initialize_enhanced_drones_router(
    drone_mgr: EnhancedDroneManager,
    vision_svc: EnhancedVisionService
):
    """Initialize the router with service instances"""
    global enhanced_drone_manager, enhanced_vision_service
    enhanced_drone_manager = drone_mgr
    enhanced_vision_service = vision_svc
    logger.info("Enhanced drones router initialized")


def get_enhanced_drone_manager() -> EnhancedDroneManager:
    """Get enhanced drone manager instance"""
    if enhanced_drone_manager is None:
        raise HTTPException(status_code=503, detail="Enhanced drone manager not initialized")
    return enhanced_drone_manager


def get_enhanced_vision_service() -> EnhancedVisionService:
    """Get enhanced vision service instance"""
    if enhanced_vision_service is None:
        raise HTTPException(status_code=503, detail="Enhanced vision service not initialized")
    return enhanced_vision_service


# ===== Enhanced Drone Management =====

@router.get("/drones/enhanced", response_model=List[Drone], tags=["enhanced-drones"])
async def get_enhanced_drones(
    api_key: str = Depends(get_api_key_header)
):
    """Get all available drones with enhanced information"""
    try:
        drone_manager = get_enhanced_drone_manager()
        drones = await drone_manager.get_available_drones()
        return drones
    except Exception as e:
        logger.error(f"Error getting enhanced drones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drones/{drone_id}/status/enhanced", response_model=Dict[str, Any], tags=["enhanced-drones"])
async def get_enhanced_drone_status(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Get enhanced drone status with additional information"""
    try:
        drone_manager = get_enhanced_drone_manager()
        status = await drone_manager.get_enhanced_drone_status(drone_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting enhanced drone status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/connect/enhanced", response_model=SuccessResponse, tags=["enhanced-drones"])
async def connect_drone_enhanced(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Connect to drone with enhanced features"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.connect_drone(drone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error connecting enhanced drone: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/flight_mode", response_model=SuccessResponse, tags=["enhanced-drones"])
async def set_flight_mode(
    drone_id: str,
    mode: str = Body(..., embed=True),
    api_key: str = Depends(get_api_key_header)
):
    """Set drone flight mode (manual, auto, guided, tracking, learning_data_collection, emergency)"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.set_flight_mode(drone_id, mode)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting flight mode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Flight Control =====

@router.post("/drones/{drone_id}/takeoff/enhanced", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def takeoff_drone_enhanced(
    drone_id: str,
    command: Optional[TakeoffCommand] = None,
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced takeoff with safety checks"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.takeoff_drone(drone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced takeoff: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/land/enhanced", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def land_drone_enhanced(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced landing with safety checks"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.land_drone(drone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced landing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/altitude/precise", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def set_altitude_precise(
    drone_id: str,
    target_height: int = Body(..., description="Target height in cm"),
    mode: str = Body("absolute", description="Altitude mode: absolute or relative"),
    speed: Optional[float] = Body(None, description="Climb/descent speed in m/s"),
    timeout: float = Body(30.0, description="Timeout in seconds"),
    api_key: str = Depends(get_api_key_header)
):
    """Precise altitude control with speed and timeout settings"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.set_altitude_precise(
            drone_id, target_height, mode, speed, timeout
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in precise altitude control: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/move/enhanced", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def move_drone_enhanced(
    drone_id: str,
    command: MoveCommand,
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced movement with safety boundary checks"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.move_drone(
            drone_id, command.direction, command.distance
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced movement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/rotate/enhanced", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def rotate_drone_enhanced(
    drone_id: str,
    command: RotateCommand,
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced rotation with precision control"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.rotate_drone(
            drone_id, command.direction, command.angle
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced rotation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drones/{drone_id}/emergency/enhanced", response_model=SuccessResponse, tags=["enhanced-flight-control"])
async def emergency_stop_enhanced(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced emergency stop with logging and metrics"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.emergency_land_drone(drone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced emergency stop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Flight Planning =====

@router.post("/drones/{drone_id}/flight_plan", response_model=SuccessResponse, tags=["flight-planning"])
async def execute_flight_plan(
    drone_id: str,
    flight_plan: Dict[str, Any] = Body(..., description="Flight plan configuration"),
    api_key: str = Depends(get_api_key_header)
):
    """Execute a predefined flight plan"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.execute_flight_plan(drone_id, flight_plan)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing flight plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drones/{drone_id}/flight_plan/status", response_model=Dict[str, Any], tags=["flight-planning"])
async def get_flight_plan_status(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Get current flight plan execution status"""
    try:
        drone_manager = get_enhanced_drone_manager()
        
        # Check if drone has an active flight plan
        flight_plan = drone_manager.flight_plans.get(drone_id)
        flight_mode = drone_manager.flight_modes.get(drone_id)
        active_task = drone_manager.active_tasks.get(drone_id)
        
        status = {
            "has_active_plan": flight_plan is not None,
            "flight_mode": flight_mode.value if flight_mode else "unknown",
            "task_running": active_task is not None and not active_task.done(),
            "plan_details": flight_plan.__dict__ if flight_plan else None
        }
        
        return status
    except Exception as e:
        logger.error(f"Error getting flight plan status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Learning Data Collection =====

@router.post("/drones/{drone_id}/learning_data/collect/enhanced", response_model=Dict[str, Any], tags=["learning-data"])
async def collect_learning_data_enhanced(
    drone_id: str,
    config: Dict[str, Any] = Body(..., description="Learning data collection configuration"),
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced learning data collection with multi-angle and multi-altitude capture"""
    try:
        drone_manager = get_enhanced_drone_manager()
        result = await drone_manager.collect_learning_data_enhanced(drone_id, config)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced learning data collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning_data/session/start", response_model=Dict[str, str], tags=["learning-data"])
async def start_learning_session(
    object_name: str = Body(..., description="Name of the object to learn"),
    session_config: Optional[Dict[str, Any]] = Body(None, description="Session configuration"),
    api_key: str = Depends(get_api_key_header)
):
    """Start a learning data collection session"""
    try:
        vision_service = get_enhanced_vision_service()
        session_id = await vision_service.start_learning_session(object_name, session_config)
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error starting learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning_data/session/{session_id}/add_sample", response_model=Dict[str, bool], tags=["learning-data"])
async def add_learning_sample(
    session_id: str,
    image_data: str = Body(..., description="Base64 encoded image data"),
    annotation: Dict[str, Any] = Body(..., description="Annotation data"),
    quality_score: Optional[float] = Body(None, description="Quality score (0-1)"),
    api_key: str = Depends(get_api_key_header)
):
    """Add a sample to an active learning session"""
    try:
        vision_service = get_enhanced_vision_service()
        success = await vision_service.add_learning_sample(
            session_id, image_data, annotation, quality_score
        )
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding learning sample: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learning_data/session/{session_id}/finish", response_model=Dict[str, Any], tags=["learning-data"])
async def finish_learning_session(
    session_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Finish a learning session and get summary"""
    try:
        vision_service = get_enhanced_vision_service()
        summary = await vision_service.finish_learning_session(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error finishing learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Enhanced Vision and Detection =====

@router.post("/vision/detection/enhanced", response_model=DetectionResult, tags=["enhanced-vision"])
async def detect_objects_enhanced(
    image_data: str = Body(..., description="Base64 encoded image data"),
    model_id: str = Body(..., description="Detection model ID"),
    confidence_threshold: float = Body(0.5, description="Confidence threshold"),
    filter_labels: Optional[List[str]] = Body(None, description="Filter by specific labels"),
    max_detections: Optional[int] = Body(None, description="Maximum number of detections"),
    api_key: str = Depends(get_api_key_header)
):
    """Enhanced object detection with filtering and optimization"""
    try:
        vision_service = get_enhanced_vision_service()
        result = await vision_service.detect_objects_enhanced(
            image_data, model_id, confidence_threshold, filter_labels, max_detections
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in enhanced object detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/tracking/start/enhanced", response_model=SuccessResponse, tags=["enhanced-vision"])
async def start_tracking_enhanced(
    model_id: str = Body(..., description="Detection model ID"),
    drone_id: str = Body(..., description="Drone ID to control"),
    config: Optional[Dict[str, Any]] = Body(None, description="Tracking configuration"),
    api_key: str = Depends(get_api_key_header)
):
    """Start enhanced object tracking with configurable algorithms"""
    try:
        vision_service = get_enhanced_vision_service()
        result = await vision_service.start_tracking_enhanced(model_id, drone_id, config)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting enhanced tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/tracking/stop/enhanced", response_model=SuccessResponse, tags=["enhanced-vision"])
async def stop_tracking_enhanced(
    api_key: str = Depends(get_api_key_header)
):
    """Stop enhanced object tracking"""
    try:
        vision_service = get_enhanced_vision_service()
        result = await vision_service.stop_tracking_enhanced()
        return result
    except Exception as e:
        logger.error(f"Error stopping enhanced tracking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/tracking/status/enhanced", response_model=Dict[str, Any], tags=["enhanced-vision"])
async def get_tracking_status_enhanced(
    api_key: str = Depends(get_api_key_header)
):
    """Get enhanced tracking status with detailed metrics"""
    try:
        vision_service = get_enhanced_vision_service()
        status = await vision_service.get_tracking_status_enhanced()
        return status
    except Exception as e:
        logger.error(f"Error getting enhanced tracking status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vision/models/enhanced", response_model=List[Dict[str, Any]], tags=["enhanced-vision"])
async def get_enhanced_vision_models(
    api_key: str = Depends(get_api_key_header)
):
    """Get list of available enhanced vision models"""
    try:
        vision_service = get_enhanced_vision_service()
        models = vision_service.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error getting enhanced vision models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Safety and Monitoring =====

@router.get("/drones/{drone_id}/safety/violations", response_model=List[Dict[str, Any]], tags=["safety-monitoring"])
async def get_safety_violations(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Get safety violation history for a drone"""
    try:
        drone_manager = get_enhanced_drone_manager()
        violations = await drone_manager.get_safety_violations(drone_id)
        return violations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting safety violations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drones/{drone_id}/logs/flight", response_model=List[Dict[str, Any]], tags=["safety-monitoring"])
async def get_flight_logs(
    drone_id: str,
    limit: int = Query(100, description="Maximum number of log entries"),
    api_key: str = Depends(get_api_key_header)
):
    """Get flight logs for a drone"""
    try:
        drone_manager = get_enhanced_drone_manager()
        logs = await drone_manager.get_flight_logs(drone_id, limit)
        return logs
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting flight logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/safety/config", response_model=Dict[str, Any], tags=["safety-monitoring"])
async def get_safety_config(
    api_key: str = Depends(get_api_key_header)
):
    """Get current safety configuration"""
    try:
        drone_manager = get_enhanced_drone_manager()
        config = {
            "flight_bounds": drone_manager.safety_config.flight_bounds.__dict__,
            "min_battery_level": drone_manager.safety_config.min_battery_level,
            "max_flight_time": drone_manager.safety_config.max_flight_time,
            "emergency_landing_battery": drone_manager.safety_config.emergency_landing_battery,
            "collision_avoidance": drone_manager.safety_config.collision_avoidance,
            "wind_speed_limit": drone_manager.safety_config.wind_speed_limit,
            "max_velocity": drone_manager.safety_config.max_velocity
        }
        return config
    except Exception as e:
        logger.error(f"Error getting safety config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/system/safety/config", response_model=SuccessResponse, tags=["safety-monitoring"])
async def update_safety_config(
    config: Dict[str, Any] = Body(..., description="Updated safety configuration"),
    api_key: str = Depends(get_api_key_header)
):
    """Update safety configuration"""
    try:
        drone_manager = get_enhanced_drone_manager()
        
        # Update safety configuration
        if "min_battery_level" in config:
            drone_manager.safety_config.min_battery_level = config["min_battery_level"]
        if "max_flight_time" in config:
            drone_manager.safety_config.max_flight_time = config["max_flight_time"]
        if "emergency_landing_battery" in config:
            drone_manager.safety_config.emergency_landing_battery = config["emergency_landing_battery"]
        if "collision_avoidance" in config:
            drone_manager.safety_config.collision_avoidance = config["collision_avoidance"]
        if "wind_speed_limit" in config:
            drone_manager.safety_config.wind_speed_limit = config["wind_speed_limit"]
        if "max_velocity" in config:
            drone_manager.safety_config.max_velocity = config["max_velocity"]
        
        # Update flight bounds if provided
        if "flight_bounds" in config:
            bounds = config["flight_bounds"]
            if "min_x" in bounds:
                drone_manager.safety_config.flight_bounds.min_x = bounds["min_x"]
            if "max_x" in bounds:
                drone_manager.safety_config.flight_bounds.max_x = bounds["max_x"]
            if "min_y" in bounds:
                drone_manager.safety_config.flight_bounds.min_y = bounds["min_y"]
            if "max_y" in bounds:
                drone_manager.safety_config.flight_bounds.max_y = bounds["max_y"]
            if "min_z" in bounds:
                drone_manager.safety_config.flight_bounds.min_z = bounds["min_z"]
            if "max_z" in bounds:
                drone_manager.safety_config.flight_bounds.max_z = bounds["max_z"]
        
        logger.info("Safety configuration updated")
        return SuccessResponse(
            message="Safety configuration updated successfully",
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error updating safety config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Analytics and Performance =====

@router.get("/drones/{drone_id}/metrics", response_model=Dict[str, Any], tags=["analytics"])
async def get_drone_metrics(
    drone_id: str,
    api_key: str = Depends(get_api_key_header)
):
    """Get comprehensive drone metrics"""
    try:
        drone_manager = get_enhanced_drone_manager()
        
        if drone_id not in drone_manager.drone_metrics:
            raise ValueError(f"Drone {drone_id} not found")
        
        metrics = drone_manager.drone_metrics[drone_id]
        return {
            "total_flight_time": metrics.total_flight_time,
            "total_distance": metrics.total_distance,
            "total_photos": metrics.total_photos,
            "emergency_stops": metrics.emergency_stops,
            "safety_violations": metrics.safety_violations,
            "performance_score": metrics.performance_score,
            "last_maintenance": metrics.last_maintenance
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting drone metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/analytics/vision", response_model=Dict[str, Any], tags=["analytics"])
async def get_vision_analytics(
    api_key: str = Depends(get_api_key_header)
):
    """Get comprehensive vision system analytics"""
    try:
        vision_service = get_enhanced_vision_service()
        analytics = await vision_service.get_vision_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting vision analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/analytics/overall", response_model=Dict[str, Any], tags=["analytics"])
async def get_overall_analytics(
    api_key: str = Depends(get_api_key_header)
):
    """Get overall system analytics combining drone and vision metrics"""
    try:
        drone_manager = get_enhanced_drone_manager()
        vision_service = get_enhanced_vision_service()
        
        # Combine analytics from both services
        vision_analytics = await vision_service.get_vision_analytics()
        
        # Aggregate drone metrics
        total_flight_time = sum(m.total_flight_time for m in drone_manager.drone_metrics.values())
        total_distance = sum(m.total_distance for m in drone_manager.drone_metrics.values())
        total_photos = sum(m.total_photos for m in drone_manager.drone_metrics.values())
        total_emergency_stops = sum(m.emergency_stops for m in drone_manager.drone_metrics.values())
        total_safety_violations = sum(m.safety_violations for m in drone_manager.drone_metrics.values())
        avg_performance_score = (
            sum(m.performance_score for m in drone_manager.drone_metrics.values()) /
            len(drone_manager.drone_metrics) if drone_manager.drone_metrics else 0
        )
        
        overall_analytics = {
            "drone_fleet": {
                "total_drones": len(drone_manager.drone_info),
                "connected_drones": len(drone_manager.connected_drones),
                "total_flight_time": total_flight_time,
                "total_distance": total_distance,
                "total_photos": total_photos,
                "total_emergency_stops": total_emergency_stops,
                "total_safety_violations": total_safety_violations,
                "average_performance_score": avg_performance_score
            },
            "vision_system": vision_analytics,
            "system_health": {
                "monitoring_active": drone_manager.monitoring_active,
                "active_flight_plans": len([p for p in drone_manager.flight_plans.values() if p]),
                "active_tasks": len(drone_manager.active_tasks),
                "safety_violations_24h": len([
                    v for violations in drone_manager.safety_violations.values()
                    for v in violations
                    if (datetime.now() - v["timestamp"]).total_seconds() < 86400
                ])
            }
        }
        
        return overall_analytics
    except Exception as e:
        logger.error(f"Error getting overall analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== System Management =====

@router.post("/system/cleanup", response_model=Dict[str, Any], tags=["system-management"])
async def cleanup_system(
    max_age_hours: int = Body(24, description="Maximum age in hours for data to keep"),
    api_key: str = Depends(get_api_key_header)
):
    """Clean up old data and optimize system performance"""
    try:
        vision_service = get_enhanced_vision_service()
        
        # Cleanup old learning sessions
        cleaned_sessions = await vision_service.cleanup_old_sessions(max_age_hours)
        
        # Could add more cleanup operations here for drone logs, etc.
        
        return {
            "cleaned_learning_sessions": cleaned_sessions,
            "cleanup_completed": True,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error in system cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health/enhanced", response_model=Dict[str, Any], tags=["system-management"])
async def get_enhanced_system_health(
    api_key: str = Depends(get_api_key_header)
):
    """Get comprehensive system health status"""
    try:
        drone_manager = get_enhanced_drone_manager()
        vision_service = get_enhanced_vision_service()
        
        # Get system health information
        health_status = {
            "timestamp": datetime.now(),
            "overall_status": "healthy",  # This would be calculated based on various factors
            "components": {
                "enhanced_drone_manager": {
                    "status": "running",
                    "monitoring_active": drone_manager.monitoring_active,
                    "connected_drones": len(drone_manager.connected_drones),
                    "active_tasks": len(drone_manager.active_tasks)
                },
                "enhanced_vision_service": {
                    "status": "running",
                    "tracking_active": vision_service.is_tracking_active,
                    "active_trackers": len(vision_service.active_trackers),
                    "available_models": len(vision_service.models)
                }
            },
            "performance_metrics": {
                "total_flight_time": sum(m.total_flight_time for m in drone_manager.drone_metrics.values()),
                "average_performance_score": (
                    sum(m.performance_score for m in drone_manager.drone_metrics.values()) /
                    len(drone_manager.drone_metrics) if drone_manager.drone_metrics else 0
                ),
                "recent_safety_violations": len([
                    v for violations in drone_manager.safety_violations.values()
                    for v in violations
                    if (datetime.now() - v["timestamp"]).total_seconds() < 3600  # Last hour
                ])
            }
        }
        
        return health_status
    except Exception as e:
        logger.error(f"Error getting enhanced system health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))