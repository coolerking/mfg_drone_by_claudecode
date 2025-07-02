"""
Dashboard API Router
Implements dashboard and system monitoring endpoints from OpenAPI specification
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ..models.model_models import SystemStatus
from ..models.drone_models import DroneStatus
from ..core.system_service import SystemService
from ..core.drone_manager import DroneManager
from ..core.vision_service import VisionService
from ..core.model_service import ModelService
from ..core.dataset_service import DatasetService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instances (will be injected)
system_service: SystemService = None
drone_manager: DroneManager = None
vision_service: VisionService = None
model_service: ModelService = None
dataset_service: DatasetService = None


def get_system_service() -> SystemService:
    """Get system service instance"""
    global system_service
    if system_service is None:
        raise HTTPException(status_code=503, detail="System service not initialized")
    return system_service


def get_drone_manager() -> DroneManager:
    """Get drone manager instance"""
    global drone_manager
    if drone_manager is None:
        raise HTTPException(status_code=503, detail="Drone manager not initialized")
    return drone_manager


def get_vision_service() -> VisionService:
    """Get vision service instance"""
    global vision_service
    if vision_service is None:
        raise HTTPException(status_code=503, detail="Vision service not initialized")
    return vision_service


def get_model_service() -> ModelService:
    """Get model service instance"""
    global model_service
    if model_service is None:
        raise HTTPException(status_code=503, detail="Model service not initialized")
    return model_service


def get_dataset_service() -> DatasetService:
    """Get dataset service instance"""
    global dataset_service
    if dataset_service is None:
        raise HTTPException(status_code=503, detail="Dataset service not initialized")
    return dataset_service


# Dashboard Endpoints

@router.get("/dashboard/system", response_model=SystemStatus)
async def get_system_status(
    system_svc: SystemService = Depends(get_system_service),
    drone_mgr: DroneManager = Depends(get_drone_manager),
    vision_svc: VisionService = Depends(get_vision_service),
    model_svc: ModelService = Depends(get_model_service)
) -> SystemStatus:
    """
    システム状態取得
    
    システム全体の状態を取得します。
    """
    try:
        system_status = await system_svc.get_system_status(drone_mgr, vision_svc, model_svc)
        logger.debug("Retrieved system status")
        return system_status
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail="システム状態の取得に失敗しました")


@router.get("/dashboard/drones", response_model=List[DroneStatus])
async def get_all_drone_statuses(
    system_svc: SystemService = Depends(get_system_service),
    drone_mgr: DroneManager = Depends(get_drone_manager)
) -> List[DroneStatus]:
    """
    ドローン群状態取得
    
    全ドローンの状態を取得します。
    """
    try:
        drone_statuses = await system_svc.get_all_drone_statuses(drone_mgr)
        logger.info(f"Retrieved status for {len(drone_statuses)} drones")
        return drone_statuses
    except Exception as e:
        logger.error(f"Error getting drone statuses: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローン状態の取得に失敗しました")


@router.get("/dashboard/metrics/history")
async def get_system_metrics_history(
    duration: int = Query(60, ge=1, le=1440, description="履歴期間（分）"),
    system_svc: SystemService = Depends(get_system_service)
):
    """
    システム指標履歴取得
    
    指定期間のシステム指標履歴を取得します。
    """
    try:
        metrics_history = await system_svc.get_system_metrics_history(duration)
        logger.debug(f"Retrieved {duration} minutes of metrics history")
        return metrics_history
    except Exception as e:
        logger.error(f"Error getting metrics history: {str(e)}")
        raise HTTPException(status_code=500, detail="指標履歴の取得に失敗しました")


@router.get("/dashboard/health")
async def get_service_health_status(
    system_svc: SystemService = Depends(get_system_service),
    drone_mgr: DroneManager = Depends(get_drone_manager),
    vision_svc: VisionService = Depends(get_vision_service),
    model_svc: ModelService = Depends(get_model_service),
    dataset_svc: DatasetService = Depends(get_dataset_service)
):
    """
    サービス健全性状態取得
    
    各サービスの健全性状態を取得します。
    """
    try:
        health_status = await system_svc.get_service_health_status(
            drone_mgr, vision_svc, model_svc, dataset_svc
        )
        logger.debug("Retrieved service health status")
        return health_status
    except Exception as e:
        logger.error(f"Error getting service health status: {str(e)}")
        raise HTTPException(status_code=500, detail="健全性状態の取得に失敗しました")


@router.get("/dashboard/performance")
async def get_performance_metrics(
    system_svc: SystemService = Depends(get_system_service)
):
    """
    パフォーマンス指標取得
    
    詳細なパフォーマンス指標を取得します。
    """
    try:
        performance_metrics = await system_svc.get_performance_metrics()
        logger.debug("Retrieved performance metrics")
        return performance_metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="パフォーマンス指標の取得に失敗しました")


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    system_svc: SystemService = Depends(get_system_service),
    drone_mgr: DroneManager = Depends(get_drone_manager),
    vision_svc: VisionService = Depends(get_vision_service),
    model_svc: ModelService = Depends(get_model_service),
    dataset_svc: DatasetService = Depends(get_dataset_service)
):
    """
    ダッシュボード概要取得
    
    ダッシュボード用の概要情報を取得します。
    """
    try:
        # Get system status
        system_status = await system_svc.get_system_status(drone_mgr, vision_svc, model_svc)
        
        # Get model statistics
        model_stats = await model_svc.get_model_statistics()
        
        # Get dataset count
        datasets = await dataset_svc.get_datasets()
        
        # Get tracking status
        tracking_status = await vision_svc.get_tracking_status()
        
        # Get available models count
        available_models = vision_svc.get_available_models()
        
        overview = {
            "system": {
                "cpu_usage": system_status.cpu_usage,
                "memory_usage": system_status.memory_usage,
                "disk_usage": system_status.disk_usage,
                "uptime_seconds": system_status.uptime
            },
            "drones": {
                "connected_count": system_status.connected_drones,
                "tracking_active": tracking_status.is_active
            },
            "models": {
                "total_count": model_stats.get("total_models", 0),
                "available_detection_models": len(available_models),
                "active_training_jobs": model_stats.get("active_training_jobs", 0)
            },
            "datasets": {
                "total_count": len(datasets)
            },
            "last_updated": system_status.last_updated
        }
        
        logger.debug("Retrieved dashboard overview")
        return overview
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        raise HTTPException(status_code=500, detail="ダッシュボード概要の取得に失敗しました")


@router.get("/dashboard/alerts")
async def get_system_alerts(
    system_svc: SystemService = Depends(get_system_service),
    drone_mgr: DroneManager = Depends(get_drone_manager),
    vision_svc: VisionService = Depends(get_vision_service),
    model_svc: ModelService = Depends(get_model_service)
):
    """
    システムアラート取得
    
    システムアラートと警告を取得します。
    """
    try:
        alerts = []
        
        # Check system resource usage
        system_status = await system_svc.get_system_status(drone_mgr, vision_svc, model_svc)
        
        if system_status.cpu_usage > 90:
            alerts.append({
                "level": "critical",
                "type": "system",
                "message": f"CPU使用率が危険レベルです: {system_status.cpu_usage}%",
                "timestamp": system_status.last_updated
            })
        elif system_status.cpu_usage > 80:
            alerts.append({
                "level": "warning",
                "type": "system", 
                "message": f"CPU使用率が高いです: {system_status.cpu_usage}%",
                "timestamp": system_status.last_updated
            })
        
        if system_status.memory_usage > 90:
            alerts.append({
                "level": "critical",
                "type": "system",
                "message": f"メモリ使用率が危険レベルです: {system_status.memory_usage}%",
                "timestamp": system_status.last_updated
            })
        elif system_status.memory_usage > 80:
            alerts.append({
                "level": "warning",
                "type": "system",
                "message": f"メモリ使用率が高いです: {system_status.memory_usage}%",
                "timestamp": system_status.last_updated
            })
        
        if system_status.disk_usage > 90:
            alerts.append({
                "level": "critical",
                "type": "system",
                "message": f"ディスク使用率が危険レベルです: {system_status.disk_usage}%",
                "timestamp": system_status.last_updated
            })
        
        # Check for failed training jobs
        try:
            training_jobs = await model_svc.get_all_training_jobs()
            failed_jobs = [job for job in training_jobs if job.status == "failed"]
            
            for job in failed_jobs[-3:]:  # Last 3 failed jobs
                alerts.append({
                    "level": "error",
                    "type": "training",
                    "message": f"学習ジョブが失敗しました: {job.model_name}",
                    "details": job.error_message,
                    "timestamp": job.completed_at or job.started_at
                })
        except Exception:
            pass  # Ignore errors in this check
        
        # Check for disconnected drones with recent activity
        try:
            drone_statuses = await system_svc.get_all_drone_statuses(drone_mgr)
            disconnected_drones = [d for d in drone_statuses if d.connection_status == "disconnected"]
            
            if len(disconnected_drones) > 0:
                alerts.append({
                    "level": "info",
                    "type": "drones",
                    "message": f"{len(disconnected_drones)}台のドローンが切断されています",
                    "timestamp": system_status.last_updated
                })
        except Exception:
            pass  # Ignore errors in this check
        
        # Sort alerts by timestamp (newest first)
        alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        logger.debug(f"Generated {len(alerts)} system alerts")
        return {"alerts": alerts, "total_count": len(alerts)}
        
    except Exception as e:
        logger.error(f"Error getting system alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="システムアラートの取得に失敗しました")


def initialize_dashboard_router(
    system_svc: SystemService,
    drone_mgr: DroneManager,
    vision_svc: VisionService,
    model_svc: ModelService,
    dataset_svc: DatasetService
):
    """Initialize the dashboard router with service instances"""
    global system_service, drone_manager, vision_service, model_service, dataset_service
    system_service = system_svc
    drone_manager = drone_mgr
    vision_service = vision_svc
    model_service = model_svc
    dataset_service = dataset_svc
    logger.info("Dashboard router initialized with service instances")