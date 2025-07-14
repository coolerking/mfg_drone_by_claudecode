"""
Drone Control API Router
Implements drone control endpoints from OpenAPI specification
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.responses import JSONResponse

from ..models.drone_models import Drone, DroneStatus, MoveCommand, RotateCommand, Photo
from ..models.common_models import SuccessResponse
from ..core.drone_manager import DroneManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection for DroneManager
def get_drone_manager() -> DroneManager:
    """ドローンマネージャーインスタンスを取得"""
    from ..main import get_drone_manager
    return get_drone_manager()


@router.get("/drones", response_model=List[Drone])
async def get_drones(
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> List[Drone]:
    """
    ドローン一覧取得
    
    接続可能なドローンの一覧を取得します。
    """
    try:
        drones = await drone_manager.get_available_drones()
        logger.info(f"Retrieved {len(drones)} drones")
        return drones
    except Exception as e:
        logger.error(f"Error getting drones: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローン一覧の取得に失敗しました")


@router.post("/drones/{drone_id}/connect", response_model=SuccessResponse)
async def connect_drone(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    ドローン接続
    
    指定されたドローンに接続します。
    """
    try:
        result = await drone_manager.connect_drone(drone_id)
        logger.info(f"Drone {drone_id} connected successfully")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "already connected" in error_msg:
            raise HTTPException(status_code=409, detail="ドローンは既に接続されています")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error connecting drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローン接続に失敗しました")


@router.post("/drones/{drone_id}/disconnect", response_model=SuccessResponse)
async def disconnect_drone(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    ドローン切断
    
    指定されたドローンから切断します。
    """
    try:
        result = await drone_manager.disconnect_drone(drone_id)
        logger.info(f"Drone {drone_id} disconnected successfully")
        return result
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error disconnecting drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローン切断に失敗しました")


@router.post("/drones/{drone_id}/takeoff", response_model=SuccessResponse)
async def takeoff_drone(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    離陸
    
    ドローンを離陸させます。
    """
    try:
        result = await drone_manager.takeoff_drone(drone_id)
        logger.info(f"Drone {drone_id} takeoff initiated")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "バッテリー" in error_msg:
            raise HTTPException(status_code=400, detail="ドローンが操作可能な状態ではありません（バッテリー不足など）")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error taking off drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="離陸に失敗しました")


@router.post("/drones/{drone_id}/land", response_model=SuccessResponse)
async def land_drone(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    着陸
    
    ドローンを着陸させます。
    """
    try:
        result = await drone_manager.land_drone(drone_id)
        logger.info(f"Drone {drone_id} landing initiated")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error landing drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="着陸に失敗しました")


@router.post("/drones/{drone_id}/move", response_model=SuccessResponse)
async def move_drone(
    move_command: MoveCommand,
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    移動
    
    ドローンを指定方向に移動させます。
    """
    try:
        result = await drone_manager.move_drone(
            drone_id, 
            move_command.direction, 
            move_command.distance
        )
        logger.info(f"Drone {drone_id} move command executed: {move_command.direction} {move_command.distance}cm")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "Invalid" in error_msg:
            raise HTTPException(status_code=400, detail="指定されたコマンドは無効です")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error moving drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="移動に失敗しました")


@router.post("/drones/{drone_id}/rotate", response_model=SuccessResponse)
async def rotate_drone(
    rotate_command: RotateCommand,
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    回転
    
    ドローンを回転させます。
    """
    try:
        result = await drone_manager.rotate_drone(
            drone_id,
            rotate_command.direction,
            rotate_command.angle
        )
        logger.info(f"Drone {drone_id} rotate command executed: {rotate_command.direction} {rotate_command.angle}°")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "Invalid" in error_msg:
            raise HTTPException(status_code=400, detail="指定されたコマンドは無効です")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error rotating drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="回転に失敗しました")


@router.post("/drones/{drone_id}/emergency", response_model=SuccessResponse)
async def emergency_stop_drone(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    緊急停止
    
    ドローンを緊急停止させます。
    """
    try:
        result = await drone_manager.emergency_stop_drone(drone_id)
        logger.warning(f"Drone {drone_id} emergency stop executed")
        return result
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error emergency stopping drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="緊急停止に失敗しました")


@router.get("/drones/{drone_id}/status", response_model=DroneStatus)
async def get_drone_status(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> DroneStatus:
    """
    ドローン状態取得
    
    ドローンの現在状態を取得します。
    """
    try:
        status = await drone_manager.get_drone_status(drone_id)
        logger.debug(f"Retrieved status for drone {drone_id}")
        return status
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        else:
            raise HTTPException(status_code=503, detail="ドローンが利用できません")
    except Exception as e:
        logger.error(f"Error getting status for drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローン状態の取得に失敗しました")


# カメラ関連エンドポイント（完全実装）
@router.post("/drones/{drone_id}/camera/stream/start", response_model=SuccessResponse)
async def start_camera_stream(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    カメラストリーミング開始
    
    ドローンのカメラストリーミングを開始します。
    """
    try:
        result = await drone_manager.start_camera_stream(drone_id)
        logger.info(f"Camera stream started for drone {drone_id}")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "not connected" in error_msg:
            raise HTTPException(status_code=400, detail="ドローンが接続されていません")
        else:
            raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        logger.error(f"Error starting camera stream for drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="カメラストリーミング開始に失敗しました")


@router.post("/drones/{drone_id}/camera/stream/stop", response_model=SuccessResponse)
async def stop_camera_stream(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    カメラストリーミング停止
    
    ドローンのカメラストリーミングを停止します。
    """
    try:
        result = await drone_manager.stop_camera_stream(drone_id)
        logger.info(f"Camera stream stopped for drone {drone_id}")
        return result
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "not connected" in error_msg:
            raise HTTPException(status_code=400, detail="ドローンが接続されていません")
        else:
            raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        logger.error(f"Error stopping camera stream for drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="カメラストリーミング停止に失敗しました")


@router.post("/drones/{drone_id}/camera/photo", response_model=Photo)
async def take_photo(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> Photo:
    """
    写真撮影
    
    ドローンで写真を撮影します。
    """
    try:
        photo = await drone_manager.capture_photo(drone_id)
        logger.info(f"Photo captured for drone {drone_id}: {photo.id}")
        return photo
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        elif "not connected" in error_msg:
            raise HTTPException(status_code=400, detail="ドローンが接続されていません")
        else:
            raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        logger.error(f"Error capturing photo for drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="写真撮影に失敗しました")


# Phase 6: Real Drone Detection and Management Endpoints

@router.get("/drones/detect", response_model=List[dict])
async def detect_real_drones(
    timeout: float = 5.0,
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> List[dict]:
    """
    実機ドローン検出
    
    LAN内の実機ドローンを自動検出します。
    """
    try:
        detected_drones = await drone_manager.scan_for_real_drones(timeout)
        logger.info(f"Detected {len(detected_drones)} real drones")
        return detected_drones
    except Exception as e:
        logger.error(f"Error detecting real drones: {str(e)}")
        raise HTTPException(status_code=500, detail="実機ドローンの検出に失敗しました")


@router.get("/drones/{drone_id}/type-info", response_model=dict)
async def get_drone_type_info(
    drone_id: str = Path(..., description="ドローンID", regex="^[a-zA-Z0-9_-]+$"),
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> dict:
    """
    ドローンタイプ情報取得
    
    ドローンが実機かシミュレーションかの詳細情報を取得します。
    """
    try:
        type_info = drone_manager.get_drone_type_info(drone_id)
        logger.debug(f"Retrieved type info for drone {drone_id}")
        return type_info
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail="指定されたドローンが見つかりません")
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting type info for drone {drone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="ドローンタイプ情報の取得に失敗しました")


@router.post("/drones/verify-connection", response_model=dict)
async def verify_real_drone_connection(
    ip_address: str,
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> dict:
    """
    実機ドローン接続検証
    
    指定されたIPアドレスの実機ドローンへの接続を検証します。
    """
    try:
        verification_result = await drone_manager.verify_real_drone_connection(ip_address)
        logger.info(f"Verified connection to {ip_address}: {verification_result['is_reachable']}")
        return verification_result
    except Exception as e:
        logger.error(f"Error verifying connection to {ip_address}: {str(e)}")
        raise HTTPException(status_code=500, detail="接続検証に失敗しました")


@router.get("/system/network-status", response_model=dict)
async def get_network_status(
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> dict:
    """
    ネットワーク状態取得
    
    ドローン検出に関するネットワーク統計情報を取得します。
    """
    try:
        network_status = await drone_manager.get_network_status()
        logger.debug("Retrieved network status")
        return network_status
    except Exception as e:
        logger.error(f"Error getting network status: {str(e)}")
        raise HTTPException(status_code=500, detail="ネットワーク状態の取得に失敗しました")


@router.post("/system/auto-scan/start", response_model=SuccessResponse)
async def start_auto_scan(
    interval_seconds: float = 60.0,
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    自動スキャン開始
    
    実機ドローンの自動検出スキャンを開始します。
    """
    try:
        result = await drone_manager.start_auto_scan(interval_seconds)
        logger.info(f"Auto scan started with {interval_seconds}s interval")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting auto scan: {str(e)}")
        raise HTTPException(status_code=500, detail="自動スキャンの開始に失敗しました")


@router.post("/system/auto-scan/stop", response_model=SuccessResponse)
async def stop_auto_scan(
    drone_manager: DroneManager = Depends(get_drone_manager)
) -> SuccessResponse:
    """
    自動スキャン停止
    
    実機ドローンの自動検出スキャンを停止します。
    """
    try:
        result = await drone_manager.stop_auto_scan()
        logger.info("Auto scan stopped")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping auto scan: {str(e)}")
        raise HTTPException(status_code=500, detail="自動スキャンの停止に失敗しました")