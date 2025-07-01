"""
Phase 3: ドローン物理シミュレーションモジュール
Tello EDU ダミーシステム用の3D空間物理シミュレーション実装
"""

import numpy as np
import time
import threading
import logging
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from scipy.spatial.distance import cdist
from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from .virtual_camera import VirtualCameraStream, TrackingObject, TrackingObjectType, MovementPattern

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DroneState(Enum):
    """ドローンの状態"""
    IDLE = "idle"                  # 待機中
    TAKEOFF = "takeoff"           # 離陸中
    FLYING = "flying"             # 飛行中
    LANDING = "landing"           # 着陸中
    LANDED = "landed"             # 着陸済み
    EMERGENCY = "emergency"       # 緊急停止
    COLLISION = "collision"       # 衝突


class ObstacleType(Enum):
    """障害物の種類"""
    WALL = "wall"                 # 壁
    CEILING = "ceiling"           # 天井
    FLOOR = "floor"               # 床
    COLUMN = "column"             # 柱
    DYNAMIC = "dynamic"           # 動的障害物


@dataclass
class Vector3D:
    """3Dベクトルクラス"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        """ベクトルの大きさを計算"""
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3D':
        """正規化されたベクトルを返す"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """タプルに変換"""
        return (self.x, self.y, self.z)


@dataclass
class DronePhysics:
    """ドローンの物理パラメータ"""
    mass: float = 0.087           # 質量 (kg) - Tello EDUの実際の値
    max_speed: float = 8.0        # 最大速度 (m/s)
    max_acceleration: float = 4.0  # 最大加速度 (m/s²)
    max_angular_velocity: float = 180.0  # 最大角速度 (度/秒)
    drag_coefficient: float = 0.05  # 空気抵抗係数
    lift_coefficient: float = 1.0   # 揚力係数
    battery_drain_rate: float = 0.1  # バッテリー消費率 (%/秒)


@dataclass
class Obstacle:
    """障害物クラス"""
    id: str
    obstacle_type: ObstacleType
    position: Vector3D
    size: Vector3D               # 幅, 奥行き, 高さ
    rotation: Vector3D = field(default_factory=Vector3D)  # 回転角度
    is_static: bool = True       # 静的障害物かどうか
    velocity: Vector3D = field(default_factory=Vector3D)  # 動的障害物の速度
    
    def get_bounding_box(self) -> List[Vector3D]:
        """バウンディングボックスの頂点を取得"""
        # 簡単のため回転は考慮せず、軸に平行な直方体として扱う
        min_point = Vector3D(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.position.z - self.size.z / 2
        )
        max_point = Vector3D(
            self.position.x + self.size.x / 2,
            self.position.y + self.size.y / 2,
            self.position.z + self.size.z / 2
        )
        return [min_point, max_point]
    
    def contains_point(self, point: Vector3D) -> bool:
        """点が障害物内に含まれるかチェック"""
        bbox = self.get_bounding_box()
        return (bbox[0].x <= point.x <= bbox[1].x and
                bbox[0].y <= point.y <= bbox[1].y and
                bbox[0].z <= point.z <= bbox[1].z)


@dataclass
class DroneState3D:
    """ドローンの3D状態情報"""
    position: Vector3D = field(default_factory=Vector3D)
    velocity: Vector3D = field(default_factory=Vector3D)
    acceleration: Vector3D = field(default_factory=Vector3D)
    rotation: Vector3D = field(default_factory=Vector3D)  # ピッチ、ロール、ヨー
    angular_velocity: Vector3D = field(default_factory=Vector3D)
    battery_level: float = 100.0
    state: DroneState = DroneState.IDLE
    timestamp: float = field(default_factory=time.time)


class Virtual3DSpace:
    """3D仮想空間クラス"""
    
    def __init__(self, bounds: Tuple[float, float, float] = (20.0, 20.0, 10.0)):
        """
        初期化
        
        Args:
            bounds: 空間の境界 (幅, 奥行き, 高さ) メートル
        """
        self.bounds = Vector3D(*bounds)
        self.obstacles: Dict[str, Obstacle] = {}
        self.no_fly_zones: List[Polygon] = []
        
        # デフォルトの境界壁を追加
        self._create_boundary_walls()
        
        logger.info(f"3D仮想空間初期化: {bounds}")
    
    def _create_boundary_walls(self) -> None:
        """境界壁を作成"""
        # 床
        self.add_obstacle(Obstacle(
            id="floor",
            obstacle_type=ObstacleType.FLOOR,
            position=Vector3D(0, 0, -0.1),
            size=Vector3D(self.bounds.x, self.bounds.y, 0.2)
        ))
        
        # 天井
        self.add_obstacle(Obstacle(
            id="ceiling",
            obstacle_type=ObstacleType.CEILING,
            position=Vector3D(0, 0, self.bounds.z + 0.1),
            size=Vector3D(self.bounds.x, self.bounds.y, 0.2)
        ))
        
        # 壁（4面）
        wall_thickness = 0.2
        walls = [
            ("wall_north", Vector3D(0, self.bounds.y/2 + wall_thickness/2, self.bounds.z/2), 
             Vector3D(self.bounds.x, wall_thickness, self.bounds.z)),
            ("wall_south", Vector3D(0, -self.bounds.y/2 - wall_thickness/2, self.bounds.z/2), 
             Vector3D(self.bounds.x, wall_thickness, self.bounds.z)),
            ("wall_east", Vector3D(self.bounds.x/2 + wall_thickness/2, 0, self.bounds.z/2), 
             Vector3D(wall_thickness, self.bounds.y, self.bounds.z)),
            ("wall_west", Vector3D(-self.bounds.x/2 - wall_thickness/2, 0, self.bounds.z/2), 
             Vector3D(wall_thickness, self.bounds.y, self.bounds.z))
        ]
        
        for wall_id, pos, size in walls:
            self.add_obstacle(Obstacle(
                id=wall_id,
                obstacle_type=ObstacleType.WALL,
                position=pos,
                size=size
            ))
    
    def add_obstacle(self, obstacle: Obstacle) -> None:
        """障害物を追加"""
        self.obstacles[obstacle.id] = obstacle
        logger.info(f"障害物追加: {obstacle.id} at {obstacle.position.to_tuple()}")
    
    def remove_obstacle(self, obstacle_id: str) -> bool:
        """障害物を削除"""
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            logger.info(f"障害物削除: {obstacle_id}")
            return True
        return False
    
    def check_collision(self, position: Vector3D, drone_size: Vector3D = Vector3D(0.2, 0.2, 0.1)) -> Tuple[bool, Optional[str]]:
        """衝突判定"""
        # ドローンのバウンディングボックス
        drone_min = Vector3D(
            position.x - drone_size.x / 2,
            position.y - drone_size.y / 2,
            position.z - drone_size.z / 2
        )
        drone_max = Vector3D(
            position.x + drone_size.x / 2,
            position.y + drone_size.y / 2,
            position.z + drone_size.z / 2
        )
        
        for obstacle_id, obstacle in self.obstacles.items():
            obstacle_bbox = obstacle.get_bounding_box()
            
            # AABB (Axis-Aligned Bounding Box) 衝突判定
            if (drone_max.x >= obstacle_bbox[0].x and drone_min.x <= obstacle_bbox[1].x and
                drone_max.y >= obstacle_bbox[0].y and drone_min.y <= obstacle_bbox[1].y and
                drone_max.z >= obstacle_bbox[0].z and drone_min.z <= obstacle_bbox[1].z):
                return True, obstacle_id
        
        return False, None
    
    def is_position_valid(self, position: Vector3D) -> bool:
        """位置が有効かチェック（境界内かつ衝突なし）"""
        # 境界チェック
        if (abs(position.x) > self.bounds.x / 2 or
            abs(position.y) > self.bounds.y / 2 or
            position.z < 0 or position.z > self.bounds.z):
            return False
        
        # 衝突チェック
        collision, _ = self.check_collision(position)
        return not collision
    
    def get_safe_landing_positions(self, num_positions: int = 10) -> List[Vector3D]:
        """安全な着陸位置を取得"""
        safe_positions = []
        attempts = 0
        max_attempts = num_positions * 10
        
        while len(safe_positions) < num_positions and attempts < max_attempts:
            # ランダムな位置を生成（地上付近）
            x = np.random.uniform(-self.bounds.x/2 + 1, self.bounds.x/2 - 1)
            y = np.random.uniform(-self.bounds.y/2 + 1, self.bounds.y/2 - 1)
            z = 0.5  # 地上50cm
            
            position = Vector3D(x, y, z)
            if self.is_position_valid(position):
                safe_positions.append(position)
            
            attempts += 1
        
        return safe_positions


class DronePhysicsEngine:
    """ドローン物理エンジン"""
    
    def __init__(self, physics_params: DronePhysics):
        """初期化"""
        self.physics = physics_params
        self.gravity = Vector3D(0, 0, -9.81)  # 重力加速度
        self.air_density = 1.225  # 空気密度 (kg/m³)
        
    def apply_forces(self, state: DroneState3D, thrust: Vector3D, dt: float) -> DroneState3D:
        """物理法則を適用して新しい状態を計算"""
        new_state = DroneState3D(
            position=Vector3D(*state.position.to_tuple()),
            velocity=Vector3D(*state.velocity.to_tuple()),
            acceleration=Vector3D(*state.acceleration.to_tuple()),
            rotation=Vector3D(*state.rotation.to_tuple()),
            angular_velocity=Vector3D(*state.angular_velocity.to_tuple()),
            battery_level=state.battery_level,
            state=state.state,
            timestamp=time.time()
        )
        
        # 推力制限
        thrust_magnitude = thrust.magnitude()
        if thrust_magnitude > self.physics.max_acceleration * self.physics.mass:
            thrust = thrust.normalize() * (self.physics.max_acceleration * self.physics.mass)
        
        # 力の計算
        total_force = thrust + self.gravity * self.physics.mass
        
        # 空気抵抗
        drag_force = self._calculate_drag(state.velocity)
        total_force = total_force - drag_force
        
        # 加速度の計算
        new_state.acceleration = total_force * (1.0 / self.physics.mass)
        
        # 速度の更新
        new_state.velocity = state.velocity + new_state.acceleration * dt
        
        # 速度制限
        velocity_magnitude = new_state.velocity.magnitude()
        if velocity_magnitude > self.physics.max_speed:
            new_state.velocity = new_state.velocity.normalize() * self.physics.max_speed
        
        # 位置の更新
        new_state.position = state.position + new_state.velocity * dt
        
        # バッテリー消費
        battery_drain = self.physics.battery_drain_rate * dt
        if thrust_magnitude > 0:
            battery_drain *= (1 + thrust_magnitude / (self.physics.max_acceleration * self.physics.mass))
        new_state.battery_level = max(0, state.battery_level - battery_drain)
        
        return new_state
    
    def _calculate_drag(self, velocity: Vector3D) -> Vector3D:
        """空気抵抗を計算"""
        velocity_magnitude = velocity.magnitude()
        if velocity_magnitude == 0:
            return Vector3D(0, 0, 0)
        
        # 簡単な二次抵抗モデル
        drag_magnitude = 0.5 * self.air_density * self.physics.drag_coefficient * velocity_magnitude**2
        drag_direction = velocity.normalize() * -1  # 速度と逆方向
        
        return drag_direction * drag_magnitude


class DroneSimulator:
    """ドローンシミュレータメインクラス"""
    
    def __init__(self, drone_id: str = "drone_001", space_bounds: Tuple[float, float, float] = (20.0, 20.0, 10.0)):
        """
        初期化
        
        Args:
            drone_id: ドローンID
            space_bounds: 3D空間の境界 (幅, 奥行き, 高さ)
        """
        self.drone_id = drone_id
        self.virtual_world = Virtual3DSpace(space_bounds)
        self.physics_engine = DronePhysicsEngine(DronePhysics())
        
        # ドローン状態
        self.current_state = DroneState3D()
        self.target_position: Optional[Vector3D] = None
        self.flight_path: List[Vector3D] = []
        
        # カメラストリーム統合
        self.camera_stream: Optional[VirtualCameraStream] = None
        self.camera_integration_enabled = False
        
        # シミュレーション制御
        self.is_running = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.simulation_dt = 0.01  # シミュレーション時間ステップ (10ms)
        self.last_update_time = time.time()
        
        # 統計情報
        self.total_flight_time = 0.0
        self.total_distance_traveled = 0.0
        self.collision_count = 0
        
        logger.info(f"ドローンシミュレータ初期化: {drone_id}")
    
    def set_camera_stream(self, camera_stream: VirtualCameraStream) -> None:
        """仮想カメラストリームを設定"""
        self.camera_stream = camera_stream
        self.camera_integration_enabled = True
        logger.info("仮想カメラストリーム統合を有効化")
    
    def start_simulation(self) -> None:
        """シミュレーション開始"""
        if self.is_running:
            logger.warning("シミュレーションは既に実行中です")
            return
        
        self.is_running = True
        self.last_update_time = time.time()
        
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        if self.camera_stream and self.camera_integration_enabled:
            self.camera_stream.start_stream()
        
        logger.info("ドローンシミュレーション開始")
    
    def stop_simulation(self) -> None:
        """シミュレーション停止"""
        if not self.is_running:
            logger.warning("シミュレーションは既に停止しています")
            return
        
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
        
        if self.camera_stream:
            self.camera_stream.stop_stream()
        
        logger.info("ドローンシミュレーション停止")
    
    def _simulation_loop(self) -> None:
        """シミュレーションメインループ"""
        while self.is_running:
            current_time = time.time()
            dt = current_time - self.last_update_time
            
            if dt >= self.simulation_dt:
                self._update_simulation(dt)
                self._update_camera_stream()
                self.last_update_time = current_time
            
            # CPU使用率を下げるため短時間スリープ
            time.sleep(0.001)
    
    def _update_simulation(self, dt: float) -> None:
        """シミュレーションの1ステップ更新"""
        if self.current_state.state == DroneState.IDLE:
            return
        
        # 目標位置への制御入力を計算
        thrust = self._calculate_control_input()
        
        # 物理エンジンで新しい状態を計算
        new_state = self.physics_engine.apply_forces(self.current_state, thrust, dt)
        
        # 衝突判定
        collision, obstacle_id = self.virtual_world.check_collision(new_state.position)
        if collision:
            self._handle_collision(obstacle_id)
            return
        
        # 状態を更新
        old_position = self.current_state.position
        self.current_state = new_state
        
        # 統計情報更新
        distance = (new_state.position - old_position).magnitude()
        self.total_distance_traveled += distance
        self.total_flight_time += dt
        
        # バッテリー切れチェック
        if self.current_state.battery_level <= 0:
            self._handle_battery_empty()
    
    def _calculate_control_input(self) -> Vector3D:
        """制御入力（推力）を計算"""
        if self.target_position is None:
            # 目標位置がない場合はホバリング
            hover_thrust = Vector3D(0, 0, 9.81 * self.physics_engine.physics.mass)
            return hover_thrust
        
        # PID制御による位置制御
        position_error = self.target_position - self.current_state.position
        velocity_error = Vector3D(0, 0, 0) - self.current_state.velocity  # 目標速度は0（位置保持）
        
        # 制御ゲイン
        kp = 10.0  # 位置比例ゲイン
        kd = 5.0   # 速度微分ゲイン
        
        # 制御入力計算
        control_force = position_error * kp + velocity_error * kd
        
        # 重力補償
        gravity_compensation = Vector3D(0, 0, 9.81 * self.physics_engine.physics.mass)
        
        total_thrust = control_force + gravity_compensation
        
        return total_thrust
    
    def _update_camera_stream(self) -> None:
        """カメラストリームを更新"""
        if not (self.camera_stream and self.camera_integration_enabled):
            return
        
        # ドローンの位置に基づいてカメラの視点を更新
        # この実装では簡単のため、ドローンの高度に応じて追跡対象のスケールを調整
        altitude_factor = max(0.1, min(2.0, self.current_state.position.z / 5.0))
        
        # カメラストリーム内の追跡対象のサイズを動的に調整
        for obj in self.camera_stream.tracking_objects:
            base_size = 40  # ベースサイズ
            new_size = int(base_size / altitude_factor)
            obj.size = (new_size, new_size)
    
    def _handle_collision(self, obstacle_id: Optional[str]) -> None:
        """衝突処理"""
        self.current_state.state = DroneState.COLLISION
        self.current_state.velocity = Vector3D(0, 0, 0)
        self.collision_count += 1
        
        logger.warning(f"衝突検出: {obstacle_id} との衝突")
        
        # 緊急着陸
        self.emergency_land()
    
    def _handle_battery_empty(self) -> None:
        """バッテリー切れ処理"""
        self.current_state.state = DroneState.EMERGENCY
        logger.warning("バッテリー切れ - 緊急着陸実行")
        self.emergency_land()
    
    # ドローン制御メソッド（djitellopy互換インターフェース用）
    
    def takeoff(self) -> bool:
        """離陸"""
        if self.current_state.state != DroneState.IDLE:
            logger.warning("離陸失敗: ドローンが待機状態ではありません")
            return False
        
        if self.current_state.battery_level < 10:
            logger.warning("離陸失敗: バッテリー残量不足")
            return False
        
        # 離陸目標位置（現在位置から1.5m上昇）
        takeoff_position = Vector3D(
            self.current_state.position.x,
            self.current_state.position.y,
            1.5
        )
        
        if not self.virtual_world.is_position_valid(takeoff_position):
            logger.warning("離陸失敗: 離陸位置が無効です")
            return False
        
        self.current_state.state = DroneState.TAKEOFF
        self.target_position = takeoff_position
        
        logger.info("離陸開始")
        return True
    
    def land(self) -> bool:
        """着陸"""
        if self.current_state.state not in [DroneState.FLYING, DroneState.TAKEOFF]:
            logger.warning("着陸失敗: ドローンが飛行状態ではありません")
            return False
        
        # 着陸目標位置（現在位置の真下、地上10cm）
        landing_position = Vector3D(
            self.current_state.position.x,
            self.current_state.position.y,
            0.1
        )
        
        self.current_state.state = DroneState.LANDING
        self.target_position = landing_position
        
        logger.info("着陸開始")
        return True
    
    def emergency_land(self) -> None:
        """緊急着陸"""
        self.current_state.state = DroneState.EMERGENCY
        emergency_position = Vector3D(
            self.current_state.position.x,
            self.current_state.position.y,
            0.1
        )
        self.target_position = emergency_position
        logger.warning("緊急着陸実行")
    
    def move_to_position(self, x: float, y: float, z: float) -> bool:
        """指定座標に移動"""
        if self.current_state.state != DroneState.FLYING:
            logger.warning("移動失敗: ドローンが飛行状態ではありません")
            return False
        
        target = Vector3D(x, y, z)
        if not self.virtual_world.is_position_valid(target):
            logger.warning(f"移動失敗: 目標位置が無効です {target.to_tuple()}")
            return False
        
        self.target_position = target
        self.flight_path.append(target)
        
        logger.info(f"目標位置設定: {target.to_tuple()}")
        return True
    
    def rotate_to_yaw(self, yaw_degrees: float) -> bool:
        """指定角度に回転"""
        if self.current_state.state != DroneState.FLYING:
            logger.warning("回転失敗: ドローンが飛行状態ではありません")
            return False
        
        # 回転制限を適用
        max_yaw_rate = self.physics_engine.physics.max_angular_velocity
        current_yaw = self.current_state.rotation.z
        yaw_diff = yaw_degrees - current_yaw
        
        # 最短回転方向を計算
        if yaw_diff > 180:
            yaw_diff -= 360
        elif yaw_diff < -180:
            yaw_diff += 360
        
        self.current_state.rotation.z = yaw_degrees
        logger.info(f"目標角度設定: {yaw_degrees}度")
        return True
    
    # 状態取得メソッド
    
    def get_current_position(self) -> Tuple[float, float, float]:
        """現在位置を取得"""
        return self.current_state.position.to_tuple()
    
    def get_current_velocity(self) -> Tuple[float, float, float]:
        """現在速度を取得"""
        return self.current_state.velocity.to_tuple()
    
    def get_battery_level(self) -> float:
        """バッテリー残量を取得"""
        return self.current_state.battery_level
    
    def get_flight_state(self) -> str:
        """飛行状態を取得"""
        return self.current_state.state.value
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            "drone_id": self.drone_id,
            "current_position": self.get_current_position(),
            "current_velocity": self.get_current_velocity(),
            "battery_level": self.get_battery_level(),
            "flight_state": self.get_flight_state(),
            "total_flight_time": self.total_flight_time,
            "total_distance_traveled": self.total_distance_traveled,
            "collision_count": self.collision_count,
            "obstacle_count": len(self.virtual_world.obstacles)
        }
    
    # シナリオ設定メソッド
    
    def load_scenario_from_file(self, filepath: str) -> bool:
        """ファイルからシナリオを読み込み"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            # 障害物の追加
            if 'obstacles' in scenario_data:
                for obs_data in scenario_data['obstacles']:
                    obstacle = Obstacle(
                        id=obs_data['id'],
                        obstacle_type=ObstacleType(obs_data['type']),
                        position=Vector3D(**obs_data['position']),
                        size=Vector3D(**obs_data['size']),
                        is_static=obs_data.get('is_static', True)
                    )
                    self.virtual_world.add_obstacle(obstacle)
            
            # 初期位置の設定
            if 'initial_position' in scenario_data:
                pos_data = scenario_data['initial_position']
                self.current_state.position = Vector3D(**pos_data)
            
            logger.info(f"シナリオ読み込み完了: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"シナリオ読み込み失敗: {e}")
            return False
    
    def add_sample_obstacles(self) -> None:
        """サンプル障害物を追加"""
        # 部屋の中央に柱を追加
        self.virtual_world.add_obstacle(Obstacle(
            id="center_column",
            obstacle_type=ObstacleType.COLUMN,
            position=Vector3D(0, 0, 2.5),
            size=Vector3D(0.5, 0.5, 5.0)
        ))
        
        # いくつかの箱を配置
        boxes = [
            ("box_1", Vector3D(3, 3, 0.5), Vector3D(1, 1, 1)),
            ("box_2", Vector3D(-3, 2, 0.5), Vector3D(1.5, 1, 1)),
            ("box_3", Vector3D(2, -3, 0.75), Vector3D(1, 1.5, 1.5))
        ]
        
        for box_id, pos, size in boxes:
            self.virtual_world.add_obstacle(Obstacle(
                id=box_id,
                obstacle_type=ObstacleType.DYNAMIC,
                position=pos,
                size=size
            ))
        
        logger.info("サンプル障害物を追加しました")
    
    def visualize_3d_space(self, save_path: Optional[str] = None) -> None:
        """3D空間を可視化"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # ドローンの位置をプロット
        drone_pos = self.current_state.position
        ax.scatter([drone_pos.x], [drone_pos.y], [drone_pos.z], 
                  c='red', s=100, marker='^', label='Drone')
        
        # 障害物をプロット
        for obstacle in self.virtual_world.obstacles.values():
            bbox = obstacle.get_bounding_box()
            # 簡単のため障害物の中心点のみプロット
            ax.scatter([obstacle.position.x], [obstacle.position.y], [obstacle.position.z],
                      c='blue', s=50, marker='s', alpha=0.6)
        
        # 飛行経路をプロット
        if self.flight_path:
            path_x = [p.x for p in self.flight_path]
            path_y = [p.y for p in self.flight_path]
            path_z = [p.z for p in self.flight_path]
            ax.plot(path_x, path_y, path_z, 'g--', alpha=0.7, label='Flight Path')
        
        # 空間境界を設定
        bounds = self.virtual_world.bounds
        ax.set_xlim([-bounds.x/2, bounds.x/2])
        ax.set_ylim([-bounds.y/2, bounds.y/2])
        ax.set_zlim([0, bounds.z])
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'Drone Simulator 3D Space - {self.drone_id}')
        ax.legend()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"3D可視化を保存: {save_path}")
        else:
            plt.show()


# 統合クラス（複数ドローンのシミュレーション管理）
class MultiDroneSimulator:
    """複数ドローンシミュレーションマネージャー"""
    
    def __init__(self, space_bounds: Tuple[float, float, float] = (30.0, 30.0, 15.0)):
        """初期化"""
        self.space_bounds = space_bounds
        self.drones: Dict[str, DroneSimulator] = {}
        self.shared_virtual_world = Virtual3DSpace(space_bounds)
        
        logger.info("複数ドローンシミュレーター初期化")
    
    def add_drone(self, drone_id: str, initial_position: Tuple[float, float, float] = (0, 0, 0)) -> DroneSimulator:
        """ドローンを追加"""
        if drone_id in self.drones:
            logger.warning(f"ドローン {drone_id} は既に存在します")
            return self.drones[drone_id]
        
        drone = DroneSimulator(drone_id, self.space_bounds)
        drone.virtual_world = self.shared_virtual_world  # 共有仮想世界を使用
        drone.current_state.position = Vector3D(*initial_position)
        
        self.drones[drone_id] = drone
        logger.info(f"ドローン追加: {drone_id} at {initial_position}")
        
        return drone
    
    def start_all_simulations(self) -> None:
        """全ドローンのシミュレーション開始"""
        for drone in self.drones.values():
            drone.start_simulation()
        logger.info("全ドローンシミュレーション開始")
    
    def stop_all_simulations(self) -> None:
        """全ドローンのシミュレーション停止"""
        for drone in self.drones.values():
            drone.stop_simulation()
        logger.info("全ドローンシミュレーション停止")
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """全ドローンの統計情報を取得"""
        return {drone_id: drone.get_statistics() for drone_id, drone in self.drones.items()}