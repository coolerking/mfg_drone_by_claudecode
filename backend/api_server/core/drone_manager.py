"""
Drone Manager - Core business logic for drone management
Supports both simulation and real drone management using DroneFactory
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4

from ...src.core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, DroneState, Vector3D
)
from ..models.drone_models import Drone, DroneStatus, Attitude, Photo
from ..models.common_models import SuccessResponse, ErrorResponse
from .camera_service import CameraService
from .drone_factory import DroneFactory, DroneConfig, DroneMode, DroneConfigLoader
from .tello_edu_controller import TelloEDUController
from .config_service import ConfigService
from .network_service import NetworkService, get_network_service

logger = logging.getLogger(__name__)


class DroneManager:
    """ドローン管理システム（Phase 6: 実機・シミュレーション統合対応）"""
    
    def __init__(self, config_path: Optional[str] = None, space_bounds: Optional[Tuple[float, float, float]] = None):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス
            space_bounds: シミュレーション空間境界（デフォルト設定で上書き可能）
        """
        # 設定サービス初期化
        self.config_service = ConfigService(config_path)
        config_data = self.config_service.get_all_config()
        
        # 空間境界の設定
        if space_bounds is None:
            space_bounds = tuple(config_data.get("global", {}).get("space_bounds", [20.0, 20.0, 10.0]))
        
        # ドローンファクトリー初期化
        self.drone_factory = DroneFactory(space_bounds)
        
        # 従来のシミュレーター（下位互換性のため）
        self.multi_drone_simulator = MultiDroneSimulator(space_bounds)
        
        # ドローン管理
        self.connected_drones: Dict[str, Union[DroneSimulator, TelloEDUController]] = {}
        self.drone_info: Dict[str, Drone] = {}
        
        # サービス初期化
        self.camera_service = CameraService()
        self.network_service = get_network_service()
        
        # 設定からドローン情報を初期化
        self._initialize_from_config(config_data)
        
        logger.info("DroneManager initialized with Phase 6 integration")
    
    def _initialize_from_config(self, config_data: Dict) -> None:
        """
        設定ファイルからドローン情報を初期化
        
        Args:
            config_data: 設定データ
        """
        try:
            # 設定からドローン設定をロード
            drone_configs = DroneConfigLoader.load_from_dict(config_data)
            
            # デフォルト設定が空の場合はフォールバック
            if not drone_configs:
                drone_configs = DroneConfigLoader.create_default_config()
                logger.info("Using default drone configuration")
            
            # ドローンファクトリーに設定を登録
            for config in drone_configs:
                self.drone_factory.register_drone_config(config)
                
                # ドローン情報を作成
                drone_type = "real" if config.mode == DroneMode.REAL else "hybrid"
                if config.mode == DroneMode.SIMULATION:
                    drone_type = "simulation"
                
                drone_info = Drone(
                    id=config.id,
                    name=config.name,
                    type=drone_type,
                    ip_address=config.ip_address or "auto-detect",
                    status="disconnected",
                    last_seen=None
                )
                self.drone_info[config.id] = drone_info
                logger.info(f"Drone initialized from config: {config.id} ({config.mode.value})")
            
            logger.info(f"Initialized {len(drone_configs)} drones from configuration")
            
        except Exception as e:
            logger.error(f"Failed to initialize from config: {e}")
            # フォールバック：デフォルト設定を使用
            self._initialize_fallback_drones()
    
    def _initialize_fallback_drones(self) -> None:
        """フォールバック：デフォルトドローン設定を初期化"""
        default_configs = DroneConfigLoader.create_default_config()
        
        for config in default_configs:
            self.drone_factory.register_drone_config(config)
            
            drone_info = Drone(
                id=config.id,
                name=config.name,
                type="hybrid",
                ip_address=config.ip_address or "auto-detect",
                status="disconnected",
                last_seen=None
            )
            self.drone_info[config.id] = drone_info
            logger.info(f"Fallback drone initialized: {config.id}")
        
        logger.info("Fallback drone initialization completed")
    
    async def get_available_drones(self) -> List[Drone]:
        """利用可能なドローン一覧を取得"""
        return list(self.drone_info.values())
    
    async def connect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンに接続（実機・シミュレーション対応）"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id in self.connected_drones:
            raise ValueError(f"Drone {drone_id} already connected")
        
        try:
            # ドローンファクトリーを使用してドローンインスタンスを作成
            drone_instance = self.drone_factory.create_drone(drone_id)
            self.connected_drones[drone_id] = drone_instance
            
            # ドローン情報を更新
            self.drone_info[drone_id].status = "connected"
            self.drone_info[drone_id].last_seen = datetime.now()
            
            # 実機の場合の追加処理
            if isinstance(drone_instance, TelloEDUController):
                # 実機の場合：IPアドレス情報を更新
                if drone_instance.ip_address:
                    self.drone_info[drone_id].ip_address = drone_instance.ip_address
                self.drone_info[drone_id].type = "real"
                
                # 状態監視を開始
                drone_instance.start_simulation()
                
                logger.info(f"Real drone {drone_id} connected at {drone_instance.ip_address}")
                return SuccessResponse(
                    message=f"実機ドローン {drone_id} に正常に接続しました（IP: {drone_instance.ip_address}）"
                )
                
            elif isinstance(drone_instance, DroneSimulator):
                # シミュレーションの場合：従来通りの処理
                self.drone_info[drone_id].type = "simulation"
                
                # シミュレーション開始
                drone_instance.start_simulation()
                
                logger.info(f"Simulation drone {drone_id} connected and simulation started")
                return SuccessResponse(
                    message=f"シミュレーションドローン {drone_id} に正常に接続しました"
                )
            
            else:
                raise ValueError(f"Unknown drone type: {type(drone_instance)}")
                
        except Exception as e:
            logger.error(f"Drone connection failed: {drone_id}, Error: {e}")
            # 接続失敗時は情報をクリア
            if drone_id in self.connected_drones:
                del self.connected_drones[drone_id]
            raise ValueError(f"ドローン {drone_id} への接続に失敗しました: {str(e)}")
    
    async def disconnect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンから切断（実機・シミュレーション対応）"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id in self.connected_drones:
            drone_instance = self.connected_drones[drone_id]
            
            try:
                # 実機の場合の切断処理
                if isinstance(drone_instance, TelloEDUController):
                    drone_instance.stop_simulation()
                    drone_instance.disconnect()
                    logger.info(f"Real drone {drone_id} disconnected")
                    message = f"実機ドローン {drone_id} から正常に切断しました"
                    
                elif isinstance(drone_instance, DroneSimulator):
                    # シミュレーションの場合：従来通りの処理
                    drone_instance.stop_simulation()
                    logger.info(f"Simulation drone {drone_id} disconnected")
                    message = f"シミュレーションドローン {drone_id} から正常に切断しました"
                    
                else:
                    logger.warning(f"Unknown drone type for disconnect: {type(drone_instance)}")
                    message = f"ドローン {drone_id} から切断しました"
                
                # 接続状態をクリア
                del self.connected_drones[drone_id]
                
                # ドローン情報を更新
                self.drone_info[drone_id].status = "disconnected"
                self.drone_info[drone_id].last_seen = datetime.now()
                
                return SuccessResponse(message=message)
                
            except Exception as e:
                logger.error(f"Drone disconnection error: {drone_id}, Error: {e}")
                # エラーが発生してもステータスは更新
                self.drone_info[drone_id].status = "disconnected"
                raise ValueError(f"ドローン {drone_id} の切断中にエラーが発生しました: {str(e)}")
        
        return SuccessResponse(
            message=f"ドローン {drone_id} は既に切断されています"
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
        """ドローン状態を取得（実機・シミュレーション対応）"""
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
        drone_instance = self.connected_drones[drone_id]
        
        if isinstance(drone_instance, TelloEDUController):
            # 実機ドローンの状態取得
            return await self._get_real_drone_status(drone_id, drone_instance)
        elif isinstance(drone_instance, DroneSimulator):
            # シミュレーションドローンの状態取得
            return await self._get_simulation_drone_status(drone_id, drone_instance)
        else:
            # 未知のドローンタイプ
            logger.warning(f"Unknown drone type for status: {type(drone_instance)}")
            return DroneStatus(
                drone_id=drone_id,
                connection_status="connected",
                flight_status="unknown",
                battery_level=0,
                last_updated=datetime.now()
            )
    
    async def _get_real_drone_status(self, drone_id: str, drone: TelloEDUController) -> DroneStatus:
        """実機ドローンの詳細状態を取得"""
        try:
            stats = drone.get_statistics()
            position = drone.get_current_position()
            velocity = drone.get_current_velocity()
            
            # 実機固有の詳細情報を取得
            real_info = drone.get_real_drone_info()
            
            # 飛行状態のマッピング
            flight_state_map = {
                "idle": "landed",
                "flying": "flying",
                "landed": "landed",
                "emergency": "emergency"
            }
            
            flight_status = flight_state_map.get(stats.get("flight_state", "idle"), "landed")
            
            # 姿勢情報（実機から取得、フォールバック付き）
            attitude_data = real_info.get("attitude", {})
            attitude = Attitude(
                pitch=attitude_data.get("pitch", 0.0),
                roll=attitude_data.get("roll", 0.0),
                yaw=attitude_data.get("yaw", 0.0)
            )
            
            # 速度計算
            speed_data = real_info.get("speed", {})
            if speed_data:
                speed_cms = ((speed_data.get("x", 0)**2 + speed_data.get("y", 0)**2 + speed_data.get("z", 0)**2)**0.5) * 100
            else:
                speed_ms = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
                speed_cms = speed_ms * 100
            
            return DroneStatus(
                drone_id=drone_id,
                connection_status="connected",
                flight_status=flight_status,
                battery_level=int(stats.get("battery_level", 0)),
                flight_time=int(stats.get("total_flight_time", 0)),
                height=real_info.get("height", int(position[2] * 100)),
                temperature=real_info.get("temperature", 25.0),
                speed=speed_cms,
                wifi_signal=real_info.get("wifi_signal", 90),
                attitude=attitude,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to get real drone status: {drone_id}, Error: {e}")
            # エラー時は基本状態を返す
            return DroneStatus(
                drone_id=drone_id,
                connection_status="connected",
                flight_status="unknown",
                battery_level=int(drone.get_battery_level()),
                last_updated=datetime.now()
            )
    
    async def _get_simulation_drone_status(self, drone_id: str, drone_sim: DroneSimulator) -> DroneStatus:
        """シミュレーションドローンの詳細状態を取得"""
        try:
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
            
        except Exception as e:
            logger.error(f"Failed to get simulation drone status: {drone_id}, Error: {e}")
            # エラー時は基本状態を返す
            return DroneStatus(
                drone_id=drone_id,
                connection_status="connected",
                flight_status="unknown",
                battery_level=100,
                last_updated=datetime.now()
            )
    
    def _get_connected_drone(self, drone_id: str) -> Union[DroneSimulator, TelloEDUController]:
        """接続されたドローンを取得（実機・シミュレーション対応）"""
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

    # Phase 6: 実機対応の新機能

    async def scan_for_real_drones(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        実機ドローンをスキャン
        
        Args:
            timeout: スキャンタイムアウト（秒）
            
        Returns:
            List[Dict[str, Any]]: 検出された実機ドローンリスト
        """
        try:
            logger.info("Starting real drone network scan...")
            
            # ネットワークサービスを使用してスキャン
            detected_drones = await self.network_service.scan_network()
            
            # ドローンファクトリーでも検索実行
            factory_detected = self.drone_factory.scan_for_real_drones(timeout)
            
            # 結果をマージして整理
            real_drones = []
            processed_ips = set()
            
            # ネットワークサービスの結果
            for detected in detected_drones:
                if detected.is_verified and detected.ip_address not in processed_ips:
                    real_drones.append({
                        "ip_address": detected.ip_address,
                        "battery_level": detected.battery_level,
                        "signal_strength": detected.signal_strength,
                        "response_time_ms": detected.response_time_ms,
                        "detected_at": detected.detected_at.isoformat(),
                        "detection_method": detected.detection_method.value,
                        "hostname": detected.hostname,
                        "is_available": True
                    })
                    processed_ips.add(detected.ip_address)
            
            # ファクトリーの結果を追加
            for ip in factory_detected:
                if ip not in processed_ips:
                    real_drones.append({
                        "ip_address": ip,
                        "battery_level": None,
                        "signal_strength": None,
                        "response_time_ms": 0.0,
                        "detected_at": datetime.now().isoformat(),
                        "detection_method": "factory_scan",
                        "hostname": None,
                        "is_available": True
                    })
                    processed_ips.add(ip)
            
            logger.info(f"Real drone scan completed: {len(real_drones)} drones found")
            return real_drones
            
        except Exception as e:
            logger.error(f"Real drone scan failed: {e}")
            return []

    async def get_network_status(self) -> Dict[str, Any]:
        """
        ネットワーク状態を取得
        
        Returns:
            Dict[str, Any]: ネットワーク統計情報
        """
        try:
            network_stats = self.network_service.get_network_statistics()
            factory_stats = self.drone_factory.get_drone_statistics()
            
            return {
                "network_service": network_stats,
                "drone_factory": factory_stats,
                "total_detected_real_drones": len(self.network_service.get_detected_drones(verified_only=True)),
                "total_connected_drones": len(self.connected_drones),
                "real_connected_count": sum(1 for d in self.connected_drones.values() 
                                           if isinstance(d, TelloEDUController)),
                "simulation_connected_count": sum(1 for d in self.connected_drones.values() 
                                                 if isinstance(d, DroneSimulator)),
                "auto_scan_enabled": self.network_service.auto_scan_enabled,
                "last_scan_time": network_stats.get("scan_statistics", {}).get("last_scan_time")
            }
            
        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return {
                "error": str(e),
                "network_service": {},
                "drone_factory": {},
                "total_detected_real_drones": 0,
                "total_connected_drones": len(self.connected_drones)
            }

    async def verify_real_drone_connection(self, ip_address: str) -> Dict[str, Any]:
        """
        実機ドローン接続を検証
        
        Args:
            ip_address: 検証するIPアドレス
            
        Returns:
            Dict[str, Any]: 検証結果
        """
        try:
            logger.info(f"Verifying real drone connection: {ip_address}")
            
            # ネットワークサービスで検証
            is_reachable = await self.network_service.verify_drone_connection(ip_address)
            
            if is_reachable:
                # 詳細情報を取得
                detected_drones = self.network_service.get_detected_drones(verified_only=True)
                drone_info = next((d for d in detected_drones if d.ip_address == ip_address), None)
                
                return {
                    "ip_address": ip_address,
                    "is_reachable": True,
                    "battery_level": drone_info.battery_level if drone_info else None,
                    "signal_strength": drone_info.signal_strength if drone_info else None,
                    "response_time_ms": drone_info.response_time_ms if drone_info else 0.0,
                    "verified_at": datetime.now().isoformat(),
                    "is_available_for_connection": True
                }
            else:
                return {
                    "ip_address": ip_address,
                    "is_reachable": False,
                    "verified_at": datetime.now().isoformat(),
                    "is_available_for_connection": False,
                    "error": "Connection verification failed"
                }
                
        except Exception as e:
            logger.error(f"Real drone connection verification failed: {ip_address}, Error: {e}")
            return {
                "ip_address": ip_address,
                "is_reachable": False,
                "verified_at": datetime.now().isoformat(),
                "is_available_for_connection": False,
                "error": str(e)
            }

    def get_drone_type_info(self, drone_id: str) -> Dict[str, Any]:
        """
        ドローンタイプ情報を取得
        
        Args:
            drone_id: ドローンID
            
        Returns:
            Dict[str, Any]: ドローンタイプ情報
        """
        try:
            if drone_id not in self.drone_info:
                raise ValueError(f"Drone {drone_id} not found")
            
            drone_info = self.drone_info[drone_id]
            is_connected = drone_id in self.connected_drones
            
            result = {
                "drone_id": drone_id,
                "name": drone_info.name,
                "type": drone_info.type,
                "ip_address": drone_info.ip_address,
                "is_connected": is_connected,
                "connection_status": drone_info.status,
                "last_seen": drone_info.last_seen.isoformat() if drone_info.last_seen else None
            }
            
            if is_connected:
                drone_instance = self.connected_drones[drone_id]
                
                if isinstance(drone_instance, TelloEDUController):
                    result.update({
                        "drone_class": "real",
                        "is_real_drone": True,
                        "connection_state": drone_instance.get_connection_state().value,
                        "real_ip_address": drone_instance.ip_address
                    })
                elif isinstance(drone_instance, DroneSimulator):
                    result.update({
                        "drone_class": "simulation",
                        "is_real_drone": False,
                        "simulation_running": True
                    })
            else:
                # ファクトリーから設定情報を取得
                is_real = self.drone_factory.is_real_drone(drone_id)
                result.update({
                    "drone_class": "real" if is_real else "simulation",
                    "is_real_drone": is_real
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get drone type info: {drone_id}, Error: {e}")
            return {
                "drone_id": drone_id,
                "error": str(e)
            }

    async def start_auto_scan(self, interval_seconds: float = 60.0) -> SuccessResponse:
        """
        自動スキャンを開始
        
        Args:
            interval_seconds: スキャン間隔（秒）
            
        Returns:
            SuccessResponse: 開始結果
        """
        try:
            self.network_service.start_auto_scan(interval_seconds)
            logger.info(f"Auto scan started with {interval_seconds}s interval")
            
            return SuccessResponse(
                message=f"自動スキャンを開始しました（間隔: {interval_seconds}秒）"
            )
            
        except Exception as e:
            logger.error(f"Failed to start auto scan: {e}")
            raise ValueError(f"自動スキャンの開始に失敗しました: {str(e)}")

    async def stop_auto_scan(self) -> SuccessResponse:
        """
        自動スキャンを停止
        
        Returns:
            SuccessResponse: 停止結果
        """
        try:
            self.network_service.stop_auto_scan()
            logger.info("Auto scan stopped")
            
            return SuccessResponse(
                message="自動スキャンを停止しました"
            )
            
        except Exception as e:
            logger.error(f"Failed to stop auto scan: {e}")
            raise ValueError(f"自動スキャンの停止に失敗しました: {str(e)}")

    async def shutdown(self) -> None:
        """シャットダウン処理（Phase 6対応）"""
        logger.info("Shutting down DroneManager...")
        
        # 自動スキャンを停止
        try:
            self.network_service.stop_auto_scan()
        except Exception as e:
            logger.warning(f"Failed to stop auto scan: {e}")
        
        # カメラサービスをシャットダウン
        await self.camera_service.shutdown()
        
        # 全ドローンの接続を切断
        for drone_id in list(self.connected_drones.keys()):
            await self.disconnect_drone(drone_id)
        
        # ドローンファクトリーをシャットダウン
        self.drone_factory.shutdown_all()
        
        # マルチドローンシミュレータを停止（下位互換性のため）
        self.multi_drone_simulator.stop_all_simulations()
        
        # ネットワークサービスをシャットダウン
        self.network_service.shutdown()
        
        logger.info("DroneManager shutdown complete")
    
    @staticmethod
    def get_current_timestamp() -> datetime:
        """現在のタイムスタンプを取得"""
        return datetime.now()