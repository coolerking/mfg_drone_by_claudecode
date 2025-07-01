"""
Phase 3: シミュレーション設定モジュール
ドローンシミュレーションの設定とシナリオ管理
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
import logging

logger = logging.getLogger(__name__)


class SimulationMode(Enum):
    """シミュレーションモード"""
    BASIC = "basic"                    # 基本シミュレーション
    PHYSICS = "physics"                # 物理シミュレーション
    MULTI_DRONE = "multi_drone"        # 複数ドローンシミュレーション
    CAMERA_INTEGRATED = "camera_integrated"  # カメラ統合シミュレーション


@dataclass
class DroneConfig:
    """ドローン設定"""
    drone_id: str
    initial_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    initial_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    battery_level: float = 100.0
    max_speed: float = 8.0
    max_acceleration: float = 4.0
    enable_camera: bool = True
    camera_resolution: Tuple[int, int] = (640, 480)
    camera_fps: int = 30


@dataclass
class ObstacleConfig:
    """障害物設定"""
    obstacle_id: str
    obstacle_type: str              # wall, ceiling, floor, column, dynamic
    position: Tuple[float, float, float]
    size: Tuple[float, float, float]
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_static: bool = True
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class SimulationConfig:
    """シミュレーション設定"""
    simulation_mode: SimulationMode = SimulationMode.PHYSICS
    space_bounds: Tuple[float, float, float] = (20.0, 20.0, 10.0)
    simulation_dt: float = 0.01         # シミュレーション時間ステップ
    physics_enabled: bool = True
    collision_detection: bool = True
    battery_simulation: bool = True
    weather_effects: bool = False
    
    # ドローン設定
    drones: List[DroneConfig] = field(default_factory=list)
    
    # 障害物設定
    obstacles: List[ObstacleConfig] = field(default_factory=list)
    
    # カメラ設定
    camera_integration: bool = True
    generate_dynamic_content: bool = True
    
    # ログ設定
    log_level: str = "INFO"
    log_simulation_data: bool = True
    log_file_path: str = "simulation.log"


class PresetScenarios:
    """プリセットシナリオ集"""
    
    @staticmethod
    def get_empty_room_scenario() -> SimulationConfig:
        """空の部屋シナリオ"""
        config = SimulationConfig()
        config.space_bounds = (10.0, 10.0, 5.0)
        
        # 単一ドローン
        drone = DroneConfig(
            drone_id="test_drone",
            initial_position=(0.0, 0.0, 0.1),
            enable_camera=True
        )
        config.drones = [drone]
        
        return config
    
    @staticmethod
    def get_obstacle_course_scenario() -> SimulationConfig:
        """障害物コースシナリオ"""
        config = SimulationConfig()
        config.space_bounds = (15.0, 15.0, 8.0)
        
        # ドローン設定
        drone = DroneConfig(
            drone_id="obstacle_drone",
            initial_position=(-5.0, -5.0, 0.1),
            enable_camera=True
        )
        config.drones = [drone]
        
        # 障害物設定
        obstacles = [
            # 中央の柱
            ObstacleConfig(
                obstacle_id="center_pillar",
                obstacle_type="column",
                position=(0.0, 0.0, 2.5),
                size=(0.5, 0.5, 5.0)
            ),
            # 複数の箱
            ObstacleConfig(
                obstacle_id="box_1",
                obstacle_type="dynamic",
                position=(3.0, 3.0, 0.5),
                size=(1.0, 1.0, 1.0)
            ),
            ObstacleConfig(
                obstacle_id="box_2",
                obstacle_type="dynamic",
                position=(-3.0, 2.0, 0.5),
                size=(1.5, 1.0, 1.0)
            ),
            ObstacleConfig(
                obstacle_id="box_3",
                obstacle_type="dynamic",
                position=(2.0, -3.0, 0.75),
                size=(1.0, 1.5, 1.5)
            ),
            # 天井の低い部分
            ObstacleConfig(
                obstacle_id="low_ceiling",
                obstacle_type="ceiling",
                position=(0.0, 5.0, 3.0),
                size=(6.0, 4.0, 0.2)
            )
        ]
        config.obstacles = obstacles
        
        return config
    
    @staticmethod
    def get_multi_drone_scenario() -> SimulationConfig:
        """複数ドローンシナリオ"""
        config = SimulationConfig()
        config.simulation_mode = SimulationMode.MULTI_DRONE
        config.space_bounds = (25.0, 25.0, 12.0)
        
        # 複数ドローン
        drones = [
            DroneConfig(
                drone_id="drone_001",
                initial_position=(-8.0, -8.0, 0.1),
                enable_camera=True,
                camera_resolution=(640, 480)
            ),
            DroneConfig(
                drone_id="drone_002",
                initial_position=(8.0, -8.0, 0.1),
                enable_camera=True,
                camera_resolution=(320, 240)
            ),
            DroneConfig(
                drone_id="drone_003",
                initial_position=(0.0, 8.0, 0.1),
                enable_camera=False
            )
        ]
        config.drones = drones
        
        # 散らばった障害物
        obstacles = [
            ObstacleConfig(
                obstacle_id="warehouse_rack_1",
                obstacle_type="dynamic",
                position=(5.0, 0.0, 2.0),
                size=(2.0, 8.0, 4.0)
            ),
            ObstacleConfig(
                obstacle_id="warehouse_rack_2",
                obstacle_type="dynamic",
                position=(-5.0, 0.0, 2.0),
                size=(2.0, 8.0, 4.0)
            ),
            ObstacleConfig(
                obstacle_id="central_conveyor",
                obstacle_type="dynamic",
                position=(0.0, 0.0, 0.5),
                size=(1.0, 12.0, 1.0)
            )
        ]
        config.obstacles = obstacles
        
        return config
    
    @staticmethod
    def get_emergency_scenario() -> SimulationConfig:
        """緊急事態シナリオ"""
        config = SimulationConfig()
        config.space_bounds = (12.0, 12.0, 6.0)
        config.weather_effects = True
        
        # 緊急事態対応ドローン
        drone = DroneConfig(
            drone_id="emergency_drone",
            initial_position=(0.0, 0.0, 0.1),
            battery_level=30.0,  # 低バッテリー
            max_speed=12.0,      # 高速モード
            enable_camera=True
        )
        config.drones = [drone]
        
        # 複雑な障害物環境
        obstacles = [
            # 倒れた障害物
            ObstacleConfig(
                obstacle_id="fallen_tree",
                obstacle_type="dynamic",
                position=(2.0, 3.0, 0.5),
                size=(5.0, 0.5, 1.0),
                rotation=(0.0, 0.0, 45.0)
            ),
            # 煙突や高い構造物
            ObstacleConfig(
                obstacle_id="tower",
                obstacle_type="column",
                position=(-3.0, -2.0, 3.0),
                size=(1.0, 1.0, 6.0)
            )
        ]
        config.obstacles = obstacles
        
        return config


class ConfigurationManager:
    """設定管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.current_config: Optional[SimulationConfig] = None
        self.preset_scenarios = PresetScenarios()
        
    def load_config_from_file(self, filepath: str) -> SimulationConfig:
        """ファイルから設定を読み込み"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # 設定データを SimulationConfig に変換
            config = self._parse_config_data(config_data)
            self.current_config = config
            
            logger.info(f"設定ファイル読み込み完了: {filepath}")
            return config
            
        except Exception as e:
            logger.error(f"設定ファイル読み込み失敗: {e}")
            raise
    
    def save_config_to_file(self, config: SimulationConfig, filepath: str) -> None:
        """設定をファイルに保存"""
        try:
            config_data = self._serialize_config(config)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"設定ファイル保存完了: {filepath}")
            
        except Exception as e:
            logger.error(f"設定ファイル保存失敗: {e}")
            raise
    
    def get_preset_scenario(self, scenario_name: str) -> SimulationConfig:
        """プリセットシナリオを取得"""
        scenarios = {
            "empty_room": self.preset_scenarios.get_empty_room_scenario,
            "obstacle_course": self.preset_scenarios.get_obstacle_course_scenario,
            "multi_drone": self.preset_scenarios.get_multi_drone_scenario,
            "emergency": self.preset_scenarios.get_emergency_scenario
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"未知のシナリオ: {scenario_name}")
        
        config = scenarios[scenario_name]()
        self.current_config = config
        
        logger.info(f"プリセットシナリオ読み込み: {scenario_name}")
        return config
    
    def _parse_config_data(self, config_data: Dict[str, Any]) -> SimulationConfig:
        """設定データをパース"""
        # 基本設定
        config = SimulationConfig()
        
        if 'simulation_mode' in config_data:
            config.simulation_mode = SimulationMode(config_data['simulation_mode'])
        
        if 'space_bounds' in config_data:
            config.space_bounds = tuple(config_data['space_bounds'])
        
        if 'simulation_dt' in config_data:
            config.simulation_dt = config_data['simulation_dt']
        
        # ドローン設定
        if 'drones' in config_data:
            config.drones = []
            for drone_data in config_data['drones']:
                drone = DroneConfig(
                    drone_id=drone_data['drone_id'],
                    initial_position=tuple(drone_data.get('initial_position', (0, 0, 0))),
                    initial_rotation=tuple(drone_data.get('initial_rotation', (0, 0, 0))),
                    battery_level=drone_data.get('battery_level', 100.0),
                    max_speed=drone_data.get('max_speed', 8.0),
                    enable_camera=drone_data.get('enable_camera', True),
                    camera_resolution=tuple(drone_data.get('camera_resolution', (640, 480))),
                    camera_fps=drone_data.get('camera_fps', 30)
                )
                config.drones.append(drone)
        
        # 障害物設定
        if 'obstacles' in config_data:
            config.obstacles = []
            for obs_data in config_data['obstacles']:
                obstacle = ObstacleConfig(
                    obstacle_id=obs_data['obstacle_id'],
                    obstacle_type=obs_data['obstacle_type'],
                    position=tuple(obs_data['position']),
                    size=tuple(obs_data['size']),
                    rotation=tuple(obs_data.get('rotation', (0, 0, 0))),
                    is_static=obs_data.get('is_static', True),
                    velocity=tuple(obs_data.get('velocity', (0, 0, 0)))
                )
                config.obstacles.append(obstacle)
        
        return config
    
    def _serialize_config(self, config: SimulationConfig) -> Dict[str, Any]:
        """設定をシリアライズ"""
        config_data = {
            'simulation_mode': config.simulation_mode.value,
            'space_bounds': list(config.space_bounds),
            'simulation_dt': config.simulation_dt,
            'physics_enabled': config.physics_enabled,
            'collision_detection': config.collision_detection,
            'camera_integration': config.camera_integration,
            'drones': [],
            'obstacles': []
        }
        
        # ドローン設定
        for drone in config.drones:
            drone_data = {
                'drone_id': drone.drone_id,
                'initial_position': list(drone.initial_position),
                'initial_rotation': list(drone.initial_rotation),
                'battery_level': drone.battery_level,
                'max_speed': drone.max_speed,
                'enable_camera': drone.enable_camera,
                'camera_resolution': list(drone.camera_resolution),
                'camera_fps': drone.camera_fps
            }
            config_data['drones'].append(drone_data)
        
        # 障害物設定
        for obstacle in config.obstacles:
            obs_data = {
                'obstacle_id': obstacle.obstacle_id,
                'obstacle_type': obstacle.obstacle_type,
                'position': list(obstacle.position),
                'size': list(obstacle.size),
                'rotation': list(obstacle.rotation),
                'is_static': obstacle.is_static,
                'velocity': list(obstacle.velocity)
            }
            config_data['obstacles'].append(obs_data)
        
        return config_data
    
    def create_sample_configs(self, output_dir: str) -> None:
        """サンプル設定ファイルを作成"""
        import os
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 各プリセットシナリオをファイルに保存
        scenarios = [
            ("empty_room", "empty_room_scenario.yaml"),
            ("obstacle_course", "obstacle_course_scenario.yaml"),
            ("multi_drone", "multi_drone_scenario.yaml"),
            ("emergency", "emergency_scenario.yaml")
        ]
        
        for scenario_name, filename in scenarios:
            config = self.get_preset_scenario(scenario_name)
            filepath = os.path.join(output_dir, filename)
            self.save_config_to_file(config, filepath)
        
        logger.info(f"サンプル設定ファイルを作成: {output_dir}")


# グローバル設定マネージャーインスタンス
config_manager = ConfigurationManager()