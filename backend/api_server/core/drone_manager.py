"""
Drone Manager - Core business logic for drone management
Interfaces with the existing DroneSimulator system
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from ...src.core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, DroneState, Vector3D
)
from ..models.drone_models import Drone, DroneStatus, Attitude, Photo
from ..models.common_models import SuccessResponse, ErrorResponse
from .camera_service import CameraService

logger = logging.getLogger(__name__)


class DroneManager:
    """ドローン管理システム"""
    
    def __init__(self, space_bounds: Tuple[float, float, float] = (20.0, 20.0, 10.0)):
        """初期化"""
        self.multi_drone_simulator = MultiDroneSimulator(space_bounds)
        self.connected_drones: Dict[str, DroneSimulator] = {}
        self.drone_info: Dict[str, Drone] = {}
        
        # カメラサービスを初期化
        self.camera_service = CameraService()
        
        # ダミードローンを自動生成
        self._initialize_dummy_drones()
        
        logger.info("DroneManager initialized")
    
    def _initialize_dummy_drones(self) -> None:
        """ダミードローンを初期化"""
        dummy_drones = [
            ("drone_001", "Tello EDU #1", (0.0, 0.0, 0.0)),
            ("drone_002", "Tello EDU #2", (2.0, 2.0, 0.0)),
            ("drone_003", "Tello EDU #3", (-2.0, 2.0, 0.0))
        ]
        
        for drone_id, name, position in dummy_drones:
            drone_info = Drone(
                id=drone_id,
                name=name,
                type="dummy",
                ip_address=f"192.168.1.{100 + len(self.drone_info)}",
                status="disconnected",
                last_seen=None
            )
            self.drone_info[drone_id] = drone_info
            logger.info(f"Dummy drone initialized: {drone_id}")
    
    async def get_available_drones(self) -> List[Drone]:
        """利用可能なドローン一覧を取得"""
        return list(self.drone_info.values())
    
    async def connect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンに接続"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id in self.connected_drones:
            raise ValueError(f"Drone {drone_id} already connected")
        
        # ドローンシミュレータを作成して接続
        drone_sim = self.multi_drone_simulator.add_drone(drone_id)
        self.connected_drones[drone_id] = drone_sim
        
        # ドローン情報を更新
        self.drone_info[drone_id].status = "connected"
        self.drone_info[drone_id].last_seen = datetime.now()
        
        # シミュレーション開始
        drone_sim.start_simulation()
        
        logger.info(f"Drone {drone_id} connected and simulation started")
        return SuccessResponse(
            message=f"ドローン {drone_id} に正常に接続しました"
        )
    
    async def disconnect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンから切断"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id in self.connected_drones:
            # シミュレーション停止
            drone_sim = self.connected_drones[drone_id]
            drone_sim.stop_simulation()
            
            # 接続状態をクリア
            del self.connected_drones[drone_id]
            
            # ドローン情報を更新
            self.drone_info[drone_id].status = "disconnected"
            self.drone_info[drone_id].last_seen = datetime.now()
            
            logger.info(f"Drone {drone_id} disconnected")
        
        return SuccessResponse(
            message=f"ドローン {drone_id} から正常に切断しました"
        )
    
    async def takeoff_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンを離陸"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # バッテリーレベルチェック
        if drone_sim.get_battery_level() < 10:
            raise ValueError("バッテリー残量不足です")
        
        # 離陸実行
        success = drone_sim.takeoff()
        if not success:
            raise ValueError("離陸に失敗しました")
        
        # 状態更新を待つ
        await asyncio.sleep(0.1)
        
        logger.info(f"Drone {drone_id} takeoff initiated")
        return SuccessResponse(
            message=f"ドローン {drone_id} の離陸を開始しました"
        )
    
    async def land_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンを着陸"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 着陸実行
        success = drone_sim.land()
        if not success:
            raise ValueError("着陸に失敗しました")
        
        # 状態更新を待つ
        await asyncio.sleep(0.1)
        
        logger.info(f"Drone {drone_id} landing initiated")
        return SuccessResponse(
            message=f"ドローン {drone_id} の着陸を開始しました"
        )
    
    async def move_drone(self, drone_id: str, direction: str, distance: int) -> SuccessResponse:
        """ドローンを移動"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 現在位置を取得
        current_pos = drone_sim.get_current_position()
        x, y, z = current_pos
        
        # 移動方向に応じて目標位置を計算（距離はcm単位でm単位に変換）
        distance_m = distance / 100.0
        
        if direction == "forward":
            y += distance_m
        elif direction == "back":
            y -= distance_m
        elif direction == "left":
            x -= distance_m
        elif direction == "right":
            x += distance_m
        elif direction == "up":
            z += distance_m
        elif direction == "down":
            z -= distance_m
        else:
            raise ValueError(f"Invalid direction: {direction}")
        
        # 移動実行
        success = drone_sim.move_to_position(x, y, z)
        if not success:
            raise ValueError("移動に失敗しました")
        
        logger.info(f"Drone {drone_id} moving {direction} by {distance}cm")
        return SuccessResponse(
            message=f"ドローン {drone_id} の移動を開始しました"
        )
    
    async def rotate_drone(self, drone_id: str, direction: str, angle: int) -> SuccessResponse:
        """ドローンを回転"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 現在の角度を取得
        current_yaw = drone_sim.current_state.rotation.z
        
        # 回転方向に応じて目標角度を計算
        if direction == "clockwise":
            target_yaw = current_yaw + angle
        elif direction == "counter_clockwise":
            target_yaw = current_yaw - angle
        else:
            raise ValueError(f"Invalid direction: {direction}")
        
        # 角度を-180～180の範囲に正規化
        while target_yaw > 180:
            target_yaw -= 360
        while target_yaw < -180:
            target_yaw += 360
        
        # 回転実行
        success = drone_sim.rotate_to_yaw(target_yaw)
        if not success:
            raise ValueError("回転に失敗しました")
        
        logger.info(f"Drone {drone_id} rotating {direction} by {angle} degrees")
        return SuccessResponse(
            message=f"ドローン {drone_id} の回転を開始しました"
        )
    
    async def emergency_stop_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンを緊急停止"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 緊急着陸実行
        drone_sim.emergency_land()
        
        logger.warning(f"Drone {drone_id} emergency stop executed")
        return SuccessResponse(
            message=f"ドローン {drone_id} の緊急停止を実行しました"
        )
    
    async def get_drone_status(self, drone_id: str) -> DroneStatus:
        """ドローン状態を取得"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        # 接続されていない場合の基本状態
        if drone_id not in self.connected_drones:
            return DroneStatus(
                drone_id=drone_id,
                connection_status="disconnected",
                flight_status="landed",
                battery_level=100,
                last_updated=datetime.now()
            )
        
        # 接続されている場合の詳細状態
        drone_sim = self.connected_drones[drone_id]
        stats = drone_sim.get_statistics()
        position = drone_sim.get_current_position()
        velocity = drone_sim.get_current_velocity()
        
        # DroneStateをAPIの飛行状態に変換
        flight_state_map = {
            "idle": "landed",
            "takeoff": "taking_off",
            "flying": "flying",
            "landing": "landing",
            "landed": "landed",
            "emergency": "landed",
            "collision": "landed"
        }
        
        flight_status = flight_state_map.get(stats["flight_state"], "landed")
        
        # 姿勢情報を作成
        attitude = Attitude(
            pitch=drone_sim.current_state.rotation.x,
            roll=drone_sim.current_state.rotation.y,
            yaw=drone_sim.current_state.rotation.z
        )
        
        # 速度を計算（m/s -> cm/s）
        speed_ms = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
        speed_cms = speed_ms * 100
        
        return DroneStatus(
            drone_id=drone_id,
            connection_status="connected",
            flight_status=flight_status,
            battery_level=int(stats["battery_level"]),
            flight_time=int(stats["total_flight_time"]),
            height=int(position[2] * 100),  # m -> cm
            temperature=25.0,  # 仮の値
            speed=speed_cms,
            wifi_signal=90,  # 仮の値
            attitude=attitude,
            last_updated=datetime.now()
        )
    
    def _get_connected_drone(self, drone_id: str) -> DroneSimulator:
        """接続されたドローンを取得"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id not in self.connected_drones:
            raise ValueError(f"Drone {drone_id} not connected")
        
        return self.connected_drones[drone_id]
    
    # カメラ関連メソッド
    async def start_camera_stream(self, drone_id: str) -> SuccessResponse:
        """カメラストリーミングを開始"""
        # ドローンが接続されているかチェック
        self._get_connected_drone(drone_id)
        
        try:
            result = await self.camera_service.start_camera_stream(drone_id)
            logger.info(f"Camera stream started for drone {drone_id}")
            return SuccessResponse(
                message=f"ドローン {drone_id} のカメラストリーミングを開始しました"
            )
        except Exception as e:
            logger.error(f"Error starting camera stream for drone {drone_id}: {e}")
            raise ValueError(f"カメラストリーミング開始に失敗しました: {str(e)}")
    
    async def stop_camera_stream(self, drone_id: str) -> SuccessResponse:
        """カメラストリーミングを停止"""
        # ドローンが接続されているかチェック
        self._get_connected_drone(drone_id)
        
        try:
            result = await self.camera_service.stop_camera_stream(drone_id)
            logger.info(f"Camera stream stopped for drone {drone_id}")
            return SuccessResponse(
                message=f"ドローン {drone_id} のカメラストリーミングを停止しました"
            )
        except Exception as e:
            logger.error(f"Error stopping camera stream for drone {drone_id}: {e}")
            raise ValueError(f"カメラストリーミング停止に失敗しました: {str(e)}")
    
    async def capture_photo(self, drone_id: str) -> Photo:
        """写真を撮影"""
        # ドローンが接続されているかチェック
        self._get_connected_drone(drone_id)
        
        try:
            photo = await self.camera_service.capture_photo(drone_id)
            logger.info(f"Photo captured for drone {drone_id}: {photo.id}")
            return photo
        except Exception as e:
            logger.error(f"Error capturing photo for drone {drone_id}: {e}")
            raise ValueError(f"写真撮影に失敗しました: {str(e)}")
    
    async def get_camera_stream_info(self, drone_id: str) -> Optional[dict]:
        """カメラストリーム情報を取得"""
        return await self.camera_service.get_stream_info(drone_id)

    async def shutdown(self) -> None:
        """シャットダウン処理"""
        logger.info("Shutting down DroneManager...")
        
        # カメラサービスをシャットダウン
        await self.camera_service.shutdown()
        
        # 全ドローンのシミュレーションを停止
        for drone_id in list(self.connected_drones.keys()):
            await self.disconnect_drone(drone_id)
        
        # マルチドローンシミュレータを停止
        self.multi_drone_simulator.stop_all_simulations()
        
        logger.info("DroneManager shutdown complete")
    
    @staticmethod
    def get_current_timestamp() -> datetime:
        """現在のタイムスタンプを取得"""
        return datetime.now()