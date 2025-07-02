"""
Camera Service - Integration with VirtualCameraStream system
Provides camera streaming functionality for drones
"""

import asyncio
import base64
import cv2
import logging
import numpy as np
from typing import Dict, Optional, List, Any
from datetime import datetime
from uuid import uuid4

from ...src.core.virtual_camera import (
    VirtualCameraStream, VirtualCameraStreamManager, 
    TrackingObject, TrackingObjectType, MovementPattern
)
from ..models.drone_models import Photo

logger = logging.getLogger(__name__)


class CameraService:
    """カメラサービス - ドローンのカメラ機能を管理"""
    
    def __init__(self):
        """初期化"""
        self.camera_manager = VirtualCameraStreamManager()
        self.active_streams: Dict[str, VirtualCameraStream] = {}
        self.photo_storage_path = "/tmp/drone_photos"
        
        # ダミー追跡オブジェクト設定
        self.default_objects = [
            TrackingObject(
                object_type=TrackingObjectType.PERSON,
                position=(200, 150),
                size=(40, 80),
                color=(255, 0, 0),  # Blue person
                movement_pattern=MovementPattern.LINEAR,
                movement_speed=30.0,
                movement_params={"angle": 45}
            ),
            TrackingObject(
                object_type=TrackingObjectType.VEHICLE,
                position=(400, 300),
                size=(60, 30),
                color=(0, 255, 0),  # Green vehicle
                movement_pattern=MovementPattern.CIRCULAR,
                movement_speed=20.0
            ),
            TrackingObject(
                object_type=TrackingObjectType.BALL,
                position=(100, 100),
                size=(30, 30),
                color=(0, 0, 255),  # Red ball
                movement_pattern=MovementPattern.SINE_WAVE,
                movement_speed=50.0
            )
        ]
        
        logger.info("CameraService initialized")
    
    async def start_camera_stream(self, drone_id: str, width: int = 640, height: int = 480, fps: int = 30) -> Dict[str, Any]:
        """カメラストリーミングを開始"""
        if drone_id in self.active_streams:
            logger.warning(f"Camera stream for drone {drone_id} is already active")
            return {
                "success": True,
                "message": f"Camera stream for drone {drone_id} is already active",
                "stream_id": drone_id
            }
        
        try:
            # 仮想カメラストリームを作成
            stream = self.camera_manager.create_stream(
                name=drone_id,
                width=width,
                height=height,
                fps=fps
            )
            
            # デフォルトの追跡オブジェクトを追加
            for obj in self.default_objects:
                stream.add_tracking_object(obj)
            
            # ストリーミング開始
            stream.start_stream()
            self.active_streams[drone_id] = stream
            
            logger.info(f"Camera stream started for drone {drone_id}")
            return {
                "success": True,
                "message": f"Camera stream started for drone {drone_id}",
                "stream_id": drone_id,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "tracking_objects": len(self.default_objects)
            }
            
        except Exception as e:
            logger.error(f"Error starting camera stream for drone {drone_id}: {e}")
            raise
    
    async def stop_camera_stream(self, drone_id: str) -> Dict[str, Any]:
        """カメラストリーミングを停止"""
        if drone_id not in self.active_streams:
            logger.warning(f"No active camera stream for drone {drone_id}")
            return {
                "success": True,
                "message": f"No active camera stream for drone {drone_id}",
                "stream_id": drone_id
            }
        
        try:
            # ストリーミング停止
            stream = self.active_streams[drone_id]
            stream.stop_stream()
            
            # ストリームを削除
            self.camera_manager.remove_stream(drone_id)
            del self.active_streams[drone_id]
            
            logger.info(f"Camera stream stopped for drone {drone_id}")
            return {
                "success": True,
                "message": f"Camera stream stopped for drone {drone_id}",
                "stream_id": drone_id
            }
            
        except Exception as e:
            logger.error(f"Error stopping camera stream for drone {drone_id}: {e}")
            raise
    
    async def capture_photo(self, drone_id: str) -> Photo:
        """写真を撮影"""
        stream = self.active_streams.get(drone_id)
        
        if not stream:
            # ストリームがない場合は一時的に作成
            await self.start_camera_stream(drone_id)
            stream = self.active_streams[drone_id]
            temporary_stream = True
        else:
            temporary_stream = False
        
        try:
            # 現在のフレームを取得
            frame = stream.get_frame()
            if frame is None:
                # フレームが準備されるまで少し待機
                await asyncio.sleep(0.1)
                frame = stream.get_frame()
            
            if frame is None:
                raise ValueError("Unable to capture frame from camera stream")
            
            # 写真情報を生成
            photo_id = str(uuid4())
            timestamp = datetime.now()
            filename = f"drone_photo_{drone_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            photo_path = f"/photos/{filename}"
            
            # フレームをJPEG形式でエンコード
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                raise ValueError("Failed to encode frame as JPEG")
            
            # Base64エンコード（メタデータとして保存）
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            photo = Photo(
                id=photo_id,
                filename=filename,
                path=photo_path,
                timestamp=timestamp,
                drone_id=drone_id,
                metadata={
                    "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                    "format": "JPEG",
                    "size_bytes": len(buffer),
                    "channels": frame.shape[2] if len(frame.shape) > 2 else 1,
                    "base64_data": base64_image[:100] + "..." if len(base64_image) > 100 else base64_image  # 省略表示
                }
            )
            
            logger.info(f"Photo captured for drone {drone_id}: {photo_id}")
            return photo
            
        finally:
            # 一時的なストリームの場合は停止
            if temporary_stream:
                await self.stop_camera_stream(drone_id)
    
    async def get_stream_info(self, drone_id: str) -> Optional[Dict[str, Any]]:
        """ストリーム情報を取得"""
        stream = self.active_streams.get(drone_id)
        if not stream:
            return None
        
        stats = stream.get_statistics()
        return {
            "drone_id": drone_id,
            "is_active": True,
            "width": stream.width,
            "height": stream.height,
            "target_fps": stream.fps,
            "statistics": stats,
            "tracking_objects": len(stream.tracking_objects)
        }
    
    async def get_all_streams_info(self) -> List[Dict[str, Any]]:
        """全ストリーム情報を取得"""
        return [
            await self.get_stream_info(drone_id) 
            for drone_id in self.active_streams.keys()
        ]
    
    async def get_current_frame_base64(self, drone_id: str) -> Optional[str]:
        """現在のフレームをBase64形式で取得"""
        stream = self.active_streams.get(drone_id)
        if not stream:
            return None
        
        frame = stream.get_frame()
        if frame is None:
            return None
        
        try:
            # フレームをJPEG形式でエンコード
            success, buffer = cv2.imencode('.jpg', frame)
            if not success:
                return None
            
            # Base64エンコード
            base64_image = base64.b64encode(buffer).decode('utf-8')
            return base64_image
            
        except Exception as e:
            logger.error(f"Error encoding frame to base64: {e}")
            return None
    
    async def add_tracking_object(self, drone_id: str, object_config: Dict[str, Any]) -> Dict[str, Any]:
        """追跡オブジェクトを追加"""
        stream = self.active_streams.get(drone_id)
        if not stream:
            raise ValueError(f"No active camera stream for drone {drone_id}")
        
        try:
            # オブジェクト設定を解析
            obj_type = TrackingObjectType(object_config.get("type", "person"))
            position = tuple(object_config.get("position", [100, 100]))
            size = tuple(object_config.get("size", [40, 60]))
            color = tuple(object_config.get("color", [255, 0, 0]))
            movement = MovementPattern(object_config.get("movement_pattern", "linear"))
            speed = object_config.get("movement_speed", 30.0)
            
            tracking_obj = TrackingObject(
                object_type=obj_type,
                position=position,
                size=size,
                color=color,
                movement_pattern=movement,
                movement_speed=speed
            )
            
            stream.add_tracking_object(tracking_obj)
            
            logger.info(f"Tracking object added to drone {drone_id} stream")
            return {
                "success": True,
                "message": f"Tracking object added to drone {drone_id}",
                "object_type": obj_type.value,
                "position": position
            }
            
        except Exception as e:
            logger.error(f"Error adding tracking object: {e}")
            raise
    
    async def clear_tracking_objects(self, drone_id: str) -> Dict[str, Any]:
        """追跡オブジェクトをクリア"""
        stream = self.active_streams.get(drone_id)
        if not stream:
            raise ValueError(f"No active camera stream for drone {drone_id}")
        
        stream.clear_tracking_objects()
        
        logger.info(f"Tracking objects cleared for drone {drone_id}")
        return {
            "success": True,
            "message": f"All tracking objects cleared for drone {drone_id}"
        }
    
    async def shutdown(self):
        """シャットダウン処理"""
        logger.info("Shutting down CameraService...")
        
        # 全ストリームを停止
        for drone_id in list(self.active_streams.keys()):
            await self.stop_camera_stream(drone_id)
        
        # カメラマネージャーを停止
        self.camera_manager.stop_all_streams()
        
        logger.info("CameraService shutdown complete")