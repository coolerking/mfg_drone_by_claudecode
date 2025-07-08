"""
Enhanced Drone Manager - Phase 3
Advanced drone control with precision flight, safety features, and detailed monitoring
"""

import asyncio
import logging
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4
from dataclasses import dataclass, field
from enum import Enum

from ...src.core.drone_simulator import (
    DroneSimulator, MultiDroneSimulator, DroneState, Vector3D
)
from ..models.drone_models import Drone, DroneStatus, Attitude, Photo
from ..models.common_models import SuccessResponse, ErrorResponse
from .camera_service import CameraService
from .vision_service import VisionService
from .enhanced_vision_service import EnhancedVisionService

logger = logging.getLogger(__name__)


class FlightMode(Enum):
    """飛行モード"""
    MANUAL = "manual"
    AUTO = "auto"
    GUIDED = "guided"
    TRACKING = "tracking"
    LEARNING_DATA_COLLECTION = "learning_data_collection"
    EMERGENCY = "emergency"


class SafetyLevel(Enum):
    """安全レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FlightBounds:
    """飛行境界"""
    min_x: float = -10.0
    max_x: float = 10.0
    min_y: float = -10.0
    max_y: float = 10.0
    min_z: float = 0.2
    max_z: float = 5.0


@dataclass
class SafetyConfig:
    """安全設定"""
    flight_bounds: FlightBounds = field(default_factory=FlightBounds)
    min_battery_level: int = 15
    max_flight_time: int = 1200  # 20分
    emergency_landing_battery: int = 10
    collision_avoidance: bool = True
    wind_speed_limit: float = 5.0  # m/s
    max_velocity: float = 2.0  # m/s


@dataclass
class FlightPlan:
    """飛行計画"""
    waypoints: List[Tuple[float, float, float]]
    speed: float = 1.0
    altitude_mode: str = "absolute"  # absolute, relative
    completion_timeout: float = 300.0
    safety_checks: bool = True


@dataclass
class LearningDataCollectionConfig:
    """学習データ収集設定"""
    object_name: str
    capture_positions: List[str] = field(default_factory=lambda: ["front", "back", "left", "right"])
    movement_distance: int = 50  # cm
    photos_per_position: int = 3
    altitude_levels: List[int] = field(default_factory=lambda: [100, 150, 200])  # cm
    rotation_angles: List[int] = field(default_factory=lambda: [0, 45, 90, 135])  # degrees
    quality: str = "high"


@dataclass
class DroneMetrics:
    """ドローンメトリクス"""
    total_flight_time: float = 0.0
    total_distance: float = 0.0
    total_photos: int = 0
    emergency_stops: int = 0
    safety_violations: int = 0
    last_maintenance: Optional[datetime] = None
    performance_score: float = 100.0


class EnhancedDroneManager:
    """強化されたドローン管理システム - Phase 3"""
    
    def __init__(self, space_bounds: Tuple[float, float, float] = (20.0, 20.0, 10.0)):
        """初期化"""
        self.multi_drone_simulator = MultiDroneSimulator(space_bounds)
        self.connected_drones: Dict[str, DroneSimulator] = {}
        self.drone_info: Dict[str, Drone] = {}
        self.drone_metrics: Dict[str, DroneMetrics] = {}
        
        # 飛行管理
        self.flight_modes: Dict[str, FlightMode] = {}
        self.flight_plans: Dict[str, Optional[FlightPlan]] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
        # 安全設定
        self.safety_config = SafetyConfig()
        self.safety_violations: Dict[str, List[Dict[str, Any]]] = {}
        
        # サービス
        self.camera_service = CameraService()
        self.vision_service = VisionService()
        self.enhanced_vision_service = EnhancedVisionService()
        
        # 監視とログ
        self.flight_logs: Dict[str, List[Dict[str, Any]]] = {}
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # ダミードローンを自動生成
        self._initialize_dummy_drones()
        
        # 監視を開始
        self.start_monitoring()
        
        logger.info("EnhancedDroneManager initialized with Phase 3 features")
    
    def _initialize_dummy_drones(self) -> None:
        """ダミードローンを初期化"""
        dummy_drones = [
            ("drone_001", "Tello EDU #1", (0.0, 0.0, 0.0)),
            ("drone_002", "Tello EDU #2", (2.0, 2.0, 0.0)),
            ("drone_003", "Tello EDU #3", (-2.0, 2.0, 0.0)),
            ("drone_004", "Tello EDU #4", (0.0, -2.0, 0.0))  # 追加ドローン
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
            self.drone_metrics[drone_id] = DroneMetrics()
            self.flight_modes[drone_id] = FlightMode.MANUAL
            self.flight_plans[drone_id] = None
            self.safety_violations[drone_id] = []
            self.flight_logs[drone_id] = []
            logger.info(f"Enhanced dummy drone initialized: {drone_id}")
    
    # ===== 基本ドローン制御 =====
    
    async def connect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンに接続（強化版）"""
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
        
        # 飛行モードを初期化
        self.flight_modes[drone_id] = FlightMode.MANUAL
        
        # シミュレーション開始
        drone_sim.start_simulation()
        
        # 接続ログ記録
        await self._log_flight_event(drone_id, "connection", {"status": "connected"})
        
        logger.info(f"Enhanced drone {drone_id} connected and simulation started")
        return SuccessResponse(
            message=f"ドローン {drone_id} に正常に接続しました（強化版）"
        )
    
    async def set_flight_mode(self, drone_id: str, mode: str) -> SuccessResponse:
        """飛行モードを設定"""
        drone_sim = self._get_connected_drone(drone_id)
        
        try:
            flight_mode = FlightMode(mode)
            self.flight_modes[drone_id] = flight_mode
            
            await self._log_flight_event(drone_id, "flight_mode_change", {
                "new_mode": mode,
                "previous_mode": self.flight_modes.get(drone_id, FlightMode.MANUAL).value
            })
            
            logger.info(f"Flight mode set to {mode} for drone {drone_id}")
            return SuccessResponse(
                message=f"ドローン {drone_id} の飛行モードを {mode} に設定しました"
            )
        except ValueError:
            raise ValueError(f"Invalid flight mode: {mode}")
    
    # ===== 高度制御システム =====
    
    async def set_altitude_precise(
        self, 
        drone_id: str, 
        target_height: int, 
        mode: str = "absolute",
        speed: Optional[float] = None,
        timeout: float = 30.0
    ) -> SuccessResponse:
        """精密高度制御"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 安全チェック
        if not await self._check_safety(drone_id, "altitude_change", {"target_height": target_height}):
            raise ValueError("安全チェックに失敗しました")
        
        # 高度をm単位に変換
        target_height_m = target_height / 100.0
        
        # 境界チェック
        if target_height_m < self.safety_config.flight_bounds.min_z:
            raise ValueError(f"Target height too low: {target_height_m}m < {self.safety_config.flight_bounds.min_z}m")
        if target_height_m > self.safety_config.flight_bounds.max_z:
            raise ValueError(f"Target height too high: {target_height_m}m > {self.safety_config.flight_bounds.max_z}m")
        
        current_pos = drone_sim.get_current_position()
        
        if mode == "relative":
            target_height_m = current_pos[2] + target_height_m
        
        # 速度設定
        if speed is None:
            speed = 0.5  # デフォルト速度
        
        # 高度変更開始
        start_time = time.time()
        success = drone_sim.move_to_position(current_pos[0], current_pos[1], target_height_m)
        
        if not success:
            raise ValueError("高度変更に失敗しました")
        
        # 完了まで待機（タイムアウトあり）
        while time.time() - start_time < timeout:
            current_altitude = drone_sim.get_current_position()[2]
            if abs(current_altitude - target_height_m) < 0.05:  # 5cm精度
                break
            await asyncio.sleep(0.1)
        
        # ログ記録
        await self._log_flight_event(drone_id, "altitude_change", {
            "target_height": target_height,
            "mode": mode,
            "speed": speed,
            "execution_time": time.time() - start_time
        })
        
        logger.info(f"Precise altitude set for drone {drone_id}: {target_height}cm ({mode})")
        return SuccessResponse(
            message=f"ドローン {drone_id} の高度を精密に {target_height}cm に設定しました"
        )
    
    # ===== 飛行計画実行 =====
    
    async def execute_flight_plan(self, drone_id: str, flight_plan: Dict[str, Any]) -> SuccessResponse:
        """飛行計画を実行"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 飛行計画を作成
        plan = FlightPlan(
            waypoints=flight_plan.get("waypoints", []),
            speed=flight_plan.get("speed", 1.0),
            altitude_mode=flight_plan.get("altitude_mode", "absolute"),
            completion_timeout=flight_plan.get("timeout", 300.0),
            safety_checks=flight_plan.get("safety_checks", True)
        )
        
        # 安全チェック
        if plan.safety_checks and not await self._check_flight_plan_safety(drone_id, plan):
            raise ValueError("飛行計画の安全チェックに失敗しました")
        
        # 飛行計画を保存
        self.flight_plans[drone_id] = plan
        
        # 飛行モードを自動に設定
        self.flight_modes[drone_id] = FlightMode.AUTO
        
        # 飛行計画実行タスクを開始
        if drone_id in self.active_tasks:
            self.active_tasks[drone_id].cancel()
        
        self.active_tasks[drone_id] = asyncio.create_task(
            self._execute_flight_plan_task(drone_id, plan)
        )
        
        logger.info(f"Flight plan execution started for drone {drone_id}")
        return SuccessResponse(
            message=f"ドローン {drone_id} の飛行計画実行を開始しました"
        )
    
    async def _execute_flight_plan_task(self, drone_id: str, plan: FlightPlan) -> None:
        """飛行計画実行タスク"""
        drone_sim = self._get_connected_drone(drone_id)
        start_time = time.time()
        
        try:
            await self._log_flight_event(drone_id, "flight_plan_start", {
                "waypoints_count": len(plan.waypoints),
                "speed": plan.speed
            })
            
            for i, (x, y, z) in enumerate(plan.waypoints):
                # タイムアウトチェック
                if time.time() - start_time > plan.completion_timeout:
                    raise asyncio.TimeoutError("Flight plan execution timeout")
                
                # 安全チェック
                if plan.safety_checks and not await self._check_safety(drone_id, "waypoint_navigation", {"waypoint": (x, y, z)}):
                    raise ValueError(f"Safety check failed at waypoint {i}")
                
                # ウェイポイントに移動
                success = drone_sim.move_to_position(x, y, z)
                if not success:
                    raise ValueError(f"Failed to move to waypoint {i}: ({x}, {y}, {z})")
                
                # 到着まで待機
                while True:
                    current_pos = drone_sim.get_current_position()
                    distance = math.sqrt(
                        (current_pos[0] - x)**2 + 
                        (current_pos[1] - y)**2 + 
                        (current_pos[2] - z)**2
                    )
                    if distance < 0.1:  # 10cm精度
                        break
                    await asyncio.sleep(0.1)
                
                await self._log_flight_event(drone_id, "waypoint_reached", {
                    "waypoint_index": i,
                    "position": (x, y, z)
                })
                
                logger.debug(f"Drone {drone_id} reached waypoint {i}: ({x}, {y}, {z})")
            
            # 飛行計画完了
            execution_time = time.time() - start_time
            await self._log_flight_event(drone_id, "flight_plan_complete", {
                "execution_time": execution_time,
                "waypoints_completed": len(plan.waypoints)
            })
            
            # 飛行モードをマニュアルに戻す
            self.flight_modes[drone_id] = FlightMode.MANUAL
            self.flight_plans[drone_id] = None
            
            logger.info(f"Flight plan completed for drone {drone_id} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Flight plan execution failed for drone {drone_id}: {str(e)}")
            await self._log_flight_event(drone_id, "flight_plan_error", {
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            
            # エラー時は緊急モードに設定
            self.flight_modes[drone_id] = FlightMode.EMERGENCY
            raise
    
    # ===== 学習データ収集 =====
    
    async def collect_learning_data_enhanced(
        self, 
        drone_id: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """強化された学習データ収集"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 設定を作成
        collection_config = LearningDataCollectionConfig(
            object_name=config["object_name"],
            capture_positions=config.get("capture_positions", ["front", "back", "left", "right"]),
            movement_distance=config.get("movement_distance", 50),
            photos_per_position=config.get("photos_per_position", 3),
            altitude_levels=config.get("altitude_levels", [100, 150, 200]),
            rotation_angles=config.get("rotation_angles", [0, 45, 90, 135]),
            quality=config.get("quality", "high")
        )
        
        # 飛行モードを学習データ収集に設定
        self.flight_modes[drone_id] = FlightMode.LEARNING_DATA_COLLECTION
        
        # データ収集実行
        if drone_id in self.active_tasks:
            self.active_tasks[drone_id].cancel()
        
        self.active_tasks[drone_id] = asyncio.create_task(
            self._collect_learning_data_task(drone_id, collection_config)
        )
        
        # タスク完了を待機
        result = await self.active_tasks[drone_id]
        
        return result
    
    async def _collect_learning_data_task(
        self, 
        drone_id: str, 
        config: LearningDataCollectionConfig
    ) -> Dict[str, Any]:
        """学習データ収集タスク"""
        drone_sim = self._get_connected_drone(drone_id)
        start_time = time.time()
        
        collected_photos = []
        total_moves = 0
        dataset_id = str(uuid4())
        
        try:
            await self._log_flight_event(drone_id, "learning_data_collection_start", {
                "object_name": config.object_name,
                "dataset_id": dataset_id
            })
            
            # 初期位置を記録
            initial_pos = drone_sim.get_current_position()
            
            # 各高度レベルで撮影
            for altitude_cm in config.altitude_levels:
                altitude_m = altitude_cm / 100.0
                
                # 高度設定
                success = drone_sim.move_to_position(initial_pos[0], initial_pos[1], altitude_m)
                if not success:
                    raise ValueError(f"Failed to set altitude to {altitude_cm}cm")
                
                # 高度到達まで待機
                while abs(drone_sim.get_current_position()[2] - altitude_m) > 0.05:
                    await asyncio.sleep(0.1)
                
                # 各位置での撮影
                for position in config.capture_positions:
                    # 位置に移動
                    target_x, target_y = self._calculate_position_offset(
                        initial_pos[0], initial_pos[1], position, config.movement_distance / 100.0
                    )
                    
                    success = drone_sim.move_to_position(target_x, target_y, altitude_m)
                    if not success:
                        logger.warning(f"Failed to move to position {position}")
                        continue
                    
                    # 位置到達まで待機
                    while True:
                        current_pos = drone_sim.get_current_position()
                        distance = math.sqrt(
                            (current_pos[0] - target_x)**2 + 
                            (current_pos[1] - target_y)**2
                        )
                        if distance < 0.1:
                            break
                        await asyncio.sleep(0.1)
                    
                    total_moves += 1
                    
                    # 各角度で撮影
                    for angle in config.rotation_angles:
                        # 回転
                        success = drone_sim.rotate_to_yaw(angle)
                        if not success:
                            logger.warning(f"Failed to rotate to {angle} degrees")
                            continue
                        
                        # 回転完了まで待機
                        while abs(drone_sim.current_state.rotation.z - angle) > 2.0:  # 2度精度
                            await asyncio.sleep(0.1)
                        
                        # 複数枚撮影
                        for photo_idx in range(config.photos_per_position):
                            try:
                                photo = await self.camera_service.capture_photo(drone_id)
                                if photo:
                                    # メタデータを追加
                                    photo_metadata = {
                                        "dataset_id": dataset_id,
                                        "object_name": config.object_name,
                                        "position": position,
                                        "altitude_cm": altitude_cm,
                                        "rotation_angle": angle,
                                        "photo_index": photo_idx,
                                        "world_position": drone_sim.get_current_position(),
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    photo.metadata = photo_metadata
                                    collected_photos.append(photo)
                                    
                                    logger.debug(f"Photo captured: {position}, {altitude_cm}cm, {angle}°, #{photo_idx}")
                                
                            except Exception as e:
                                logger.error(f"Failed to capture photo: {str(e)}")
                                continue
                            
                            # 写真間の小さな間隔
                            await asyncio.sleep(0.5)
            
            # 初期位置に戻る
            success = drone_sim.move_to_position(*initial_pos)
            
            execution_time = time.time() - start_time
            
            # 結果をまとめる
            result = {
                "dataset": {
                    "id": dataset_id,
                    "name": f"{config.object_name}_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "image_count": len(collected_photos),
                    "positions_captured": config.capture_positions,
                    "altitude_levels": config.altitude_levels,
                    "rotation_angles": config.rotation_angles
                },
                "execution_summary": {
                    "total_moves": total_moves,
                    "total_photos": len(collected_photos),
                    "execution_time": execution_time,
                    "average_time_per_photo": execution_time / len(collected_photos) if collected_photos else 0
                }
            }
            
            await self._log_flight_event(drone_id, "learning_data_collection_complete", {
                "dataset_id": dataset_id,
                "photos_collected": len(collected_photos),
                "execution_time": execution_time
            })
            
            # メトリクス更新
            self.drone_metrics[drone_id].total_photos += len(collected_photos)
            
            # 飛行モードをマニュアルに戻す
            self.flight_modes[drone_id] = FlightMode.MANUAL
            
            logger.info(f"Learning data collection completed for drone {drone_id}: {len(collected_photos)} photos")
            
            return result
            
        except Exception as e:
            logger.error(f"Learning data collection failed for drone {drone_id}: {str(e)}")
            await self._log_flight_event(drone_id, "learning_data_collection_error", {
                "error": str(e),
                "execution_time": time.time() - start_time
            })
            
            # エラー時は緊急モードに設定
            self.flight_modes[drone_id] = FlightMode.EMERGENCY
            raise
    
    def _calculate_position_offset(self, base_x: float, base_y: float, position: str, distance: float) -> Tuple[float, float]:
        """位置オフセットを計算"""
        position_offsets = {
            "front": (0, distance),
            "back": (0, -distance),
            "left": (-distance, 0),
            "right": (distance, 0),
            "front_left": (-distance * 0.707, distance * 0.707),
            "front_right": (distance * 0.707, distance * 0.707),
            "back_left": (-distance * 0.707, -distance * 0.707),
            "back_right": (distance * 0.707, -distance * 0.707)
        }
        
        offset_x, offset_y = position_offsets.get(position, (0, 0))
        return base_x + offset_x, base_y + offset_y
    
    # ===== 安全システム =====
    
    async def _check_safety(self, drone_id: str, operation: str, params: Dict[str, Any]) -> bool:
        """安全チェック"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # バッテリーチェック
        battery_level = drone_sim.get_battery_level()
        if battery_level < self.safety_config.min_battery_level:
            await self._record_safety_violation(drone_id, "low_battery", {
                "battery_level": battery_level,
                "min_required": self.safety_config.min_battery_level
            })
            return False
        
        # 飛行境界チェック
        current_pos = drone_sim.get_current_position()
        bounds = self.safety_config.flight_bounds
        
        if operation == "altitude_change":
            target_height = params.get("target_height", 0) / 100.0
            if target_height < bounds.min_z or target_height > bounds.max_z:
                await self._record_safety_violation(drone_id, "altitude_bounds", {
                    "target_height": target_height,
                    "bounds": (bounds.min_z, bounds.max_z)
                })
                return False
        
        if (current_pos[0] < bounds.min_x or current_pos[0] > bounds.max_x or
            current_pos[1] < bounds.min_y or current_pos[1] > bounds.max_y):
            await self._record_safety_violation(drone_id, "position_bounds", {
                "current_position": current_pos,
                "bounds": bounds.__dict__
            })
            return False
        
        # 最大飛行時間チェック
        stats = drone_sim.get_statistics()
        if stats["total_flight_time"] > self.safety_config.max_flight_time:
            await self._record_safety_violation(drone_id, "max_flight_time", {
                "flight_time": stats["total_flight_time"],
                "max_allowed": self.safety_config.max_flight_time
            })
            return False
        
        return True
    
    async def _check_flight_plan_safety(self, drone_id: str, plan: FlightPlan) -> bool:
        """飛行計画の安全チェック"""
        bounds = self.safety_config.flight_bounds
        
        for i, (x, y, z) in enumerate(plan.waypoints):
            if (x < bounds.min_x or x > bounds.max_x or
                y < bounds.min_y or y > bounds.max_y or
                z < bounds.min_z or z > bounds.max_z):
                await self._record_safety_violation(drone_id, "flight_plan_bounds", {
                    "waypoint_index": i,
                    "waypoint": (x, y, z),
                    "bounds": bounds.__dict__
                })
                return False
        
        return True
    
    async def _record_safety_violation(self, drone_id: str, violation_type: str, details: Dict[str, Any]) -> None:
        """安全違反を記録"""
        violation = {
            "type": violation_type,
            "timestamp": datetime.now(),
            "details": details,
            "severity": self._determine_violation_severity(violation_type)
        }
        
        self.safety_violations[drone_id].append(violation)
        self.drone_metrics[drone_id].safety_violations += 1
        
        await self._log_flight_event(drone_id, "safety_violation", violation)
        
        logger.warning(f"Safety violation recorded for drone {drone_id}: {violation_type}")
    
    def _determine_violation_severity(self, violation_type: str) -> str:
        """違反の重要度を判定"""
        critical_violations = ["low_battery", "collision_detected", "emergency_landing"]
        high_violations = ["altitude_bounds", "position_bounds", "max_flight_time"]
        
        if violation_type in critical_violations:
            return SafetyLevel.CRITICAL.value
        elif violation_type in high_violations:
            return SafetyLevel.HIGH.value
        else:
            return SafetyLevel.MEDIUM.value
    
    # ===== 監視とログ =====
    
    def start_monitoring(self) -> None:
        """監視を開始"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Enhanced drone monitoring started")
    
    async def stop_monitoring(self) -> None:
        """監視を停止"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Enhanced drone monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """監視ループ"""
        while self.monitoring_active:
            try:
                # 接続されたドローンを監視
                for drone_id in list(self.connected_drones.keys()):
                    await self._monitor_drone(drone_id)
                
                await asyncio.sleep(1.0)  # 1秒間隔
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5.0)  # エラー時は少し長めの間隔
    
    async def _monitor_drone(self, drone_id: str) -> None:
        """個別ドローンの監視"""
        try:
            drone_sim = self.connected_drones[drone_id]
            stats = drone_sim.get_statistics()
            
            # 緊急バッテリーレベルチェック
            battery_level = stats["battery_level"]
            if battery_level <= self.safety_config.emergency_landing_battery:
                if self.flight_modes[drone_id] != FlightMode.EMERGENCY:
                    logger.critical(f"Emergency battery level for drone {drone_id}: {battery_level}%")
                    await self.emergency_land_drone(drone_id)
            
            # パフォーマンススコア更新
            await self._update_performance_score(drone_id, stats)
            
        except Exception as e:
            logger.error(f"Error monitoring drone {drone_id}: {str(e)}")
    
    async def _update_performance_score(self, drone_id: str, stats: Dict[str, Any]) -> None:
        """パフォーマンススコアを更新"""
        metrics = self.drone_metrics[drone_id]
        
        # 基本スコア
        score = 100.0
        
        # バッテリー効率
        if stats["total_flight_time"] > 0:
            battery_efficiency = stats["battery_level"] / stats["total_flight_time"] * 100
            if battery_efficiency < 50:
                score -= 10
        
        # 安全違反による減点
        score -= len(self.safety_violations[drone_id]) * 5
        
        # 緊急停止による減点
        score -= metrics.emergency_stops * 15
        
        # スコアを0-100の範囲に制限
        metrics.performance_score = max(0.0, min(100.0, score))
    
    async def _log_flight_event(self, drone_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """飛行イベントをログに記録"""
        log_entry = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "data": data
        }
        
        self.flight_logs[drone_id].append(log_entry)
        
        # ログサイズ制限（最新1000件まで）
        if len(self.flight_logs[drone_id]) > 1000:
            self.flight_logs[drone_id] = self.flight_logs[drone_id][-1000:]
    
    # ===== 緊急処理 =====
    
    async def emergency_land_drone(self, drone_id: str) -> SuccessResponse:
        """緊急着陸（強化版）"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 飛行モードを緊急に設定
        self.flight_modes[drone_id] = FlightMode.EMERGENCY
        
        # 進行中のタスクをキャンセル
        if drone_id in self.active_tasks:
            self.active_tasks[drone_id].cancel()
        
        # 緊急着陸実行
        drone_sim.emergency_land()
        
        # メトリクス更新
        self.drone_metrics[drone_id].emergency_stops += 1
        
        # ログ記録
        await self._log_flight_event(drone_id, "emergency_landing", {
            "trigger": "manual",
            "flight_mode": self.flight_modes[drone_id].value
        })
        
        logger.critical(f"Emergency landing executed for drone {drone_id}")
        return SuccessResponse(
            message=f"ドローン {drone_id} の緊急着陸を実行しました"
        )
    
    # ===== ユーティリティメソッド =====
    
    def _get_connected_drone(self, drone_id: str) -> DroneSimulator:
        """接続されたドローンを取得"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id not in self.connected_drones:
            raise ValueError(f"Drone {drone_id} not connected")
        
        return self.connected_drones[drone_id]
    
    async def get_enhanced_drone_status(self, drone_id: str) -> Dict[str, Any]:
        """強化されたドローン状態を取得"""
        basic_status = await self.get_drone_status(drone_id)
        
        # 追加情報
        enhanced_info = {
            "flight_mode": self.flight_modes.get(drone_id, FlightMode.MANUAL).value,
            "active_flight_plan": self.flight_plans.get(drone_id) is not None,
            "safety_violations_count": len(self.safety_violations.get(drone_id, [])),
            "performance_score": self.drone_metrics.get(drone_id, DroneMetrics()).performance_score,
            "total_flight_time": self.drone_metrics.get(drone_id, DroneMetrics()).total_flight_time,
            "total_photos": self.drone_metrics.get(drone_id, DroneMetrics()).total_photos
        }
        
        # 基本ステータスに追加情報をマージ
        status_dict = basic_status.dict()
        status_dict.update(enhanced_info)
        
        return status_dict
    
    async def get_flight_logs(self, drone_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """飛行ログを取得"""
        if drone_id not in self.flight_logs:
            return []
        
        logs = self.flight_logs[drone_id]
        return logs[-limit:] if len(logs) > limit else logs
    
    async def get_safety_violations(self, drone_id: str) -> List[Dict[str, Any]]:
        """安全違反履歴を取得"""
        return self.safety_violations.get(drone_id, [])
    
    # ===== 基本メソッドの継承 =====
    
    async def get_available_drones(self) -> List[Drone]:
        """利用可能なドローン一覧を取得"""
        return list(self.drone_info.values())
    
    async def disconnect_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンから切断"""
        if drone_id not in self.drone_info:
            raise ValueError(f"Drone {drone_id} not found")
        
        if drone_id in self.connected_drones:
            # 進行中のタスクをキャンセル
            if drone_id in self.active_tasks:
                self.active_tasks[drone_id].cancel()
            
            # シミュレーション停止
            drone_sim = self.connected_drones[drone_id]
            drone_sim.stop_simulation()
            
            # 接続状態をクリア
            del self.connected_drones[drone_id]
            
            # ドローン情報を更新
            self.drone_info[drone_id].status = "disconnected"
            self.drone_info[drone_id].last_seen = datetime.now()
            
            # 飛行モードをリセット
            self.flight_modes[drone_id] = FlightMode.MANUAL
            self.flight_plans[drone_id] = None
            
            # 切断ログ記録
            await self._log_flight_event(drone_id, "disconnection", {"status": "disconnected"})
            
            logger.info(f"Enhanced drone {drone_id} disconnected")
        
        return SuccessResponse(
            message=f"ドローン {drone_id} から正常に切断しました"
        )
    
    async def takeoff_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンを離陸（強化版）"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 安全チェック
        if not await self._check_safety(drone_id, "takeoff", {}):
            raise ValueError("安全チェックに失敗しました")
        
        # バッテリーレベルチェック
        if drone_sim.get_battery_level() < self.safety_config.min_battery_level:
            raise ValueError("バッテリー残量不足です")
        
        # 離陸実行
        success = drone_sim.takeoff()
        if not success:
            raise ValueError("離陸に失敗しました")
        
        # ログ記録
        await self._log_flight_event(drone_id, "takeoff", {
            "flight_mode": self.flight_modes[drone_id].value
        })
        
        # 状態更新を待つ
        await asyncio.sleep(0.1)
        
        logger.info(f"Enhanced drone {drone_id} takeoff initiated")
        return SuccessResponse(
            message=f"ドローン {drone_id} の離陸を開始しました（強化版）"
        )
    
    async def land_drone(self, drone_id: str) -> SuccessResponse:
        """ドローンを着陸（強化版）"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 進行中のタスクをキャンセル
        if drone_id in self.active_tasks:
            self.active_tasks[drone_id].cancel()
        
        # 着陸実行
        success = drone_sim.land()
        if not success:
            raise ValueError("着陸に失敗しました")
        
        # 飛行モードをマニュアルに戻す
        self.flight_modes[drone_id] = FlightMode.MANUAL
        self.flight_plans[drone_id] = None
        
        # ログ記録
        await self._log_flight_event(drone_id, "landing", {
            "flight_mode": self.flight_modes[drone_id].value
        })
        
        # 状態更新を待つ
        await asyncio.sleep(0.1)
        
        logger.info(f"Enhanced drone {drone_id} landing initiated")
        return SuccessResponse(
            message=f"ドローン {drone_id} の着陸を開始しました（強化版）"
        )
    
    async def move_drone(self, drone_id: str, direction: str, distance: int) -> SuccessResponse:
        """ドローンを移動（強化版）"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 安全チェック
        if not await self._check_safety(drone_id, "move", {"direction": direction, "distance": distance}):
            raise ValueError("安全チェックに失敗しました")
        
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
        
        # 境界チェック
        bounds = self.safety_config.flight_bounds
        if (x < bounds.min_x or x > bounds.max_x or
            y < bounds.min_y or y > bounds.max_y or
            z < bounds.min_z or z > bounds.max_z):
            raise ValueError("移動先が飛行境界外です")
        
        # 移動実行
        success = drone_sim.move_to_position(x, y, z)
        if not success:
            raise ValueError("移動に失敗しました")
        
        # ログ記録
        await self._log_flight_event(drone_id, "move", {
            "direction": direction,
            "distance": distance,
            "target_position": (x, y, z)
        })
        
        # メトリクス更新
        self.drone_metrics[drone_id].total_distance += distance_m
        
        logger.info(f"Enhanced drone {drone_id} moving {direction} by {distance}cm")
        return SuccessResponse(
            message=f"ドローン {drone_id} の移動を開始しました（強化版）"
        )
    
    async def rotate_drone(self, drone_id: str, direction: str, angle: int) -> SuccessResponse:
        """ドローンを回転（強化版）"""
        drone_sim = self._get_connected_drone(drone_id)
        
        # 安全チェック
        if not await self._check_safety(drone_id, "rotate", {"direction": direction, "angle": angle}):
            raise ValueError("安全チェックに失敗しました")
        
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
        
        # ログ記録
        await self._log_flight_event(drone_id, "rotate", {
            "direction": direction,
            "angle": angle,
            "target_yaw": target_yaw
        })
        
        logger.info(f"Enhanced drone {drone_id} rotating {direction} by {angle} degrees")
        return SuccessResponse(
            message=f"ドローン {drone_id} の回転を開始しました（強化版）"
        )
    
    async def get_drone_status(self, drone_id: str) -> DroneStatus:
        """ドローン状態を取得（基本実装から継承）"""
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
    
    # ===== カメラ関連（継承） =====
    
    async def start_camera_stream(self, drone_id: str) -> SuccessResponse:
        """カメラストリーミングを開始"""
        self._get_connected_drone(drone_id)
        
        try:
            result = await self.camera_service.start_camera_stream(drone_id)
            await self._log_flight_event(drone_id, "camera_stream_start", {})
            logger.info(f"Camera stream started for drone {drone_id}")
            return SuccessResponse(
                message=f"ドローン {drone_id} のカメラストリーミングを開始しました"
            )
        except Exception as e:
            logger.error(f"Error starting camera stream for drone {drone_id}: {e}")
            raise ValueError(f"カメラストリーミング開始に失敗しました: {str(e)}")
    
    async def stop_camera_stream(self, drone_id: str) -> SuccessResponse:
        """カメラストリーミングを停止"""
        self._get_connected_drone(drone_id)
        
        try:
            result = await self.camera_service.stop_camera_stream(drone_id)
            await self._log_flight_event(drone_id, "camera_stream_stop", {})
            logger.info(f"Camera stream stopped for drone {drone_id}")
            return SuccessResponse(
                message=f"ドローン {drone_id} のカメラストリーミングを停止しました"
            )
        except Exception as e:
            logger.error(f"Error stopping camera stream for drone {drone_id}: {e}")
            raise ValueError(f"カメラストリーミング停止に失敗しました: {str(e)}")
    
    async def capture_photo(self, drone_id: str) -> Photo:
        """写真を撮影"""
        self._get_connected_drone(drone_id)
        
        try:
            photo = await self.camera_service.capture_photo(drone_id)
            await self._log_flight_event(drone_id, "photo_capture", {"photo_id": photo.id})
            self.drone_metrics[drone_id].total_photos += 1
            logger.info(f"Photo captured for drone {drone_id}: {photo.id}")
            return photo
        except Exception as e:
            logger.error(f"Error capturing photo for drone {drone_id}: {e}")
            raise ValueError(f"写真撮影に失敗しました: {str(e)}")
    
    async def get_camera_stream_info(self, drone_id: str) -> Optional[dict]:
        """カメラストリーム情報を取得"""
        return await self.camera_service.get_stream_info(drone_id)
    
    # ===== シャットダウン =====
    
    async def shutdown(self) -> None:
        """シャットダウン処理"""
        logger.info("Shutting down EnhancedDroneManager...")
        
        # 監視を停止
        await self.stop_monitoring()
        
        # 全てのアクティブタスクをキャンセル
        for task in self.active_tasks.values():
            task.cancel()
        
        # タスクの完了を待機
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        # カメラサービスをシャットダウン
        await self.camera_service.shutdown()
        
        # ビジョンサービスをシャットダウン
        await self.vision_service.shutdown()
        await self.enhanced_vision_service.shutdown()
        
        # 全ドローンのシミュレーションを停止
        for drone_id in list(self.connected_drones.keys()):
            await self.disconnect_drone(drone_id)
        
        # マルチドローンシミュレータを停止
        self.multi_drone_simulator.stop_all_simulations()
        
        logger.info("EnhancedDroneManager shutdown complete")
    
    @staticmethod
    def get_current_timestamp() -> datetime:
        """現在のタイムスタンプを取得"""
        return datetime.now()