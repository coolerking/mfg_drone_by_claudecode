"""
Drone Factory - Factory pattern for creating drone instances
Supports both simulation and real drone creation based on configuration
"""

import logging
from typing import Dict, Optional, Union, List, Any
from enum import Enum
from dataclasses import dataclass

from ...src.core.drone_simulator import DroneSimulator
from .tello_edu_controller import TelloEDUController, TelloNetworkService

logger = logging.getLogger(__name__)


class DroneMode(Enum):
    """ドローン動作モード"""
    AUTO = "auto"                    # 自動検出（実機優先、フォールバック）
    SIMULATION = "simulation"        # シミュレーションのみ
    REAL = "real"                   # 実機のみ
    HYBRID = "hybrid"               # 実機・シミュレーション混在


@dataclass
class DroneConfig:
    """ドローン設定"""
    id: str
    name: str
    mode: DroneMode
    ip_address: Optional[str] = None
    auto_detect: bool = True
    initial_position: tuple = (0.0, 0.0, 0.0)
    fallback_to_simulation: bool = True


class DroneFactory:
    """
    ドローンファクトリークラス
    設定に基づいてシミュレーションドローンまたは実機ドローンを作成
    """
    
    def __init__(self, space_bounds: tuple = (20.0, 20.0, 10.0)):
        """
        初期化
        
        Args:
            space_bounds: シミュレーション空間の境界
        """
        self.space_bounds = space_bounds
        self.created_drones: Dict[str, Union[DroneSimulator, TelloEDUController]] = {}
        self.drone_configs: Dict[str, DroneConfig] = {}
        self.detected_real_drones: List[str] = []
        
        logger.info("DroneFactory initialized")
    
    def register_drone_config(self, config: DroneConfig) -> None:
        """
        ドローン設定を登録
        
        Args:
            config: ドローン設定
        """
        self.drone_configs[config.id] = config
        logger.info(f"Drone config registered: {config.id} ({config.mode.value})")
    
    def scan_for_real_drones(self, timeout: float = 5.0) -> List[str]:
        """
        実機ドローンを検索
        
        Args:
            timeout: 検索タイムアウト
        
        Returns:
            List[str]: 検出された実機のIPアドレス
        """
        try:
            self.detected_real_drones = TelloNetworkService.scan_for_tello_drones(timeout)
            logger.info(f"Real drones detected: {len(self.detected_real_drones)} units")
            return self.detected_real_drones
        except Exception as e:
            logger.error(f"Real drone scan failed: {e}")
            return []
    
    def create_drone(self, drone_id: str, config: Optional[DroneConfig] = None) -> Union[DroneSimulator, TelloEDUController]:
        """
        ドローンインスタンスを作成
        
        Args:
            drone_id: ドローンID
            config: ドローン設定（Noneの場合は登録済み設定を使用）
        
        Returns:
            Union[DroneSimulator, TelloEDUController]: ドローンインスタンス
        
        Raises:
            ValueError: 作成に失敗した場合
        """
        if drone_id in self.created_drones:
            logger.info(f"Drone already exists: {drone_id}")
            return self.created_drones[drone_id]
        
        # 設定を取得
        if config is None:
            config = self.drone_configs.get(drone_id)
            if config is None:
                # デフォルト設定でAUTOモード
                config = DroneConfig(
                    id=drone_id,
                    name=f"Drone {drone_id}",
                    mode=DroneMode.AUTO
                )
        
        drone_instance = None
        
        try:
            if config.mode == DroneMode.SIMULATION:
                # シミュレーションドローンを作成
                drone_instance = self._create_simulation_drone(drone_id, config)
                
            elif config.mode == DroneMode.REAL:
                # 実機ドローンを作成
                drone_instance = self._create_real_drone(drone_id, config)
                
            elif config.mode == DroneMode.AUTO:
                # 自動モード：実機優先、フォールバック
                drone_instance = self._create_auto_drone(drone_id, config)
                
            elif config.mode == DroneMode.HYBRID:
                # ハイブリッドモード（今回は実装しない）
                raise NotImplementedError("Hybrid mode not implemented yet")
            
            if drone_instance:
                self.created_drones[drone_id] = drone_instance
                logger.info(f"Drone created successfully: {drone_id} ({type(drone_instance).__name__})")
                return drone_instance
            else:
                raise ValueError(f"Failed to create drone: {drone_id}")
                
        except Exception as e:
            logger.error(f"Drone creation failed: {drone_id}, Error: {e}")
            raise ValueError(f"Failed to create drone {drone_id}: {str(e)}")
    
    def _create_simulation_drone(self, drone_id: str, config: DroneConfig) -> DroneSimulator:
        """
        シミュレーションドローンを作成
        
        Args:
            drone_id: ドローンID
            config: ドローン設定
        
        Returns:
            DroneSimulator: シミュレーションドローン
        """
        try:
            drone = DroneSimulator(drone_id, self.space_bounds)
            
            # 初期位置を設定
            drone.current_state.position.x = config.initial_position[0]
            drone.current_state.position.y = config.initial_position[1]
            drone.current_state.position.z = config.initial_position[2]
            
            logger.info(f"Simulation drone created: {drone_id}")
            return drone
            
        except Exception as e:
            logger.error(f"Simulation drone creation failed: {drone_id}, Error: {e}")
            raise
    
    def _create_real_drone(self, drone_id: str, config: DroneConfig) -> TelloEDUController:
        """
        実機ドローンを作成
        
        Args:
            drone_id: ドローンID
            config: ドローン設定
        
        Returns:
            TelloEDUController: 実機ドローン
        """
        try:
            ip_address = config.ip_address
            
            # 自動検出が有効な場合
            if config.auto_detect and not ip_address:
                if not self.detected_real_drones:
                    self.scan_for_real_drones()
                
                if self.detected_real_drones:
                    ip_address = self.detected_real_drones[0]  # 最初に見つかったドローンを使用
                    logger.info(f"Auto-detected IP used: {ip_address}")
            
            # IPアドレスが指定されていない場合はエラー
            if not ip_address:
                raise ValueError("No IP address specified and auto-detection failed")
            
            # 接続確認
            if not TelloNetworkService.verify_tello_connection(ip_address):
                raise ValueError(f"Cannot connect to Tello at {ip_address}")
            
            # Tello EDUコントローラーを作成
            tello_controller = TelloEDUController(drone_id, ip_address)
            
            # 接続試行
            if not tello_controller.connect():
                raise ValueError(f"Failed to connect to Tello at {ip_address}")
            
            logger.info(f"Real drone created: {drone_id} at {ip_address}")
            return tello_controller
            
        except Exception as e:
            logger.error(f"Real drone creation failed: {drone_id}, Error: {e}")
            raise
    
    def _create_auto_drone(self, drone_id: str, config: DroneConfig) -> Union[DroneSimulator, TelloEDUController]:
        """
        自動モードでドローンを作成
        
        Args:
            drone_id: ドローンID
            config: ドローン設定
        
        Returns:
            Union[DroneSimulator, TelloEDUController]: ドローンインスタンス
        """
        try:
            # まず実機での作成を試行
            try:
                return self._create_real_drone(drone_id, config)
            except Exception as real_error:
                logger.warning(f"Real drone creation failed: {real_error}")
                
                # フォールバックが有効な場合はシミュレーションを作成
                if config.fallback_to_simulation:
                    logger.info(f"Falling back to simulation for drone: {drone_id}")
                    return self._create_simulation_drone(drone_id, config)
                else:
                    raise real_error
                    
        except Exception as e:
            logger.error(f"Auto drone creation failed: {drone_id}, Error: {e}")
            raise
    
    def get_drone(self, drone_id: str) -> Optional[Union[DroneSimulator, TelloEDUController]]:
        """
        作成済みドローンを取得
        
        Args:
            drone_id: ドローンID
        
        Returns:
            Optional[Union[DroneSimulator, TelloEDUController]]: ドローンインスタンス
        """
        return self.created_drones.get(drone_id)
    
    def remove_drone(self, drone_id: str) -> bool:
        """
        ドローンを削除
        
        Args:
            drone_id: ドローンID
        
        Returns:
            bool: 削除成功フラグ
        """
        if drone_id not in self.created_drones:
            logger.warning(f"Drone not found for removal: {drone_id}")
            return False
        
        try:
            drone = self.created_drones[drone_id]
            
            # 接続を切断
            if isinstance(drone, TelloEDUController):
                drone.stop_simulation()
                drone.disconnect()
            elif isinstance(drone, DroneSimulator):
                drone.stop_simulation()
            
            del self.created_drones[drone_id]
            logger.info(f"Drone removed: {drone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Drone removal failed: {drone_id}, Error: {e}")
            return False
    
    def get_all_drones(self) -> Dict[str, Union[DroneSimulator, TelloEDUController]]:
        """全ドローンを取得"""
        return self.created_drones.copy()
    
    def get_drone_statistics(self) -> Dict[str, Any]:
        """
        ファクトリー統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        real_count = sum(1 for drone in self.created_drones.values() 
                        if isinstance(drone, TelloEDUController))
        sim_count = sum(1 for drone in self.created_drones.values() 
                       if isinstance(drone, DroneSimulator))
        
        return {
            "total_drones": len(self.created_drones),
            "real_drones": real_count,
            "simulation_drones": sim_count,
            "detected_real_drones": len(self.detected_real_drones),
            "configured_drones": len(self.drone_configs),
            "space_bounds": self.space_bounds
        }
    
    def is_real_drone(self, drone_id: str) -> bool:
        """
        実機ドローンかどうか確認
        
        Args:
            drone_id: ドローンID
        
        Returns:
            bool: 実機フラグ
        """
        drone = self.get_drone(drone_id)
        return isinstance(drone, TelloEDUController)
    
    def shutdown_all(self) -> None:
        """全ドローンをシャットダウン"""
        logger.info("Shutting down all drones...")
        
        for drone_id in list(self.created_drones.keys()):
            self.remove_drone(drone_id)
        
        logger.info("All drones shutdown complete")


# 設定ローダー
class DroneConfigLoader:
    """ドローン設定ローダー"""
    
    @staticmethod
    def load_from_dict(config_data: Dict[str, Any]) -> List[DroneConfig]:
        """
        辞書からドローン設定を読み込み
        
        Args:
            config_data: 設定データ
        
        Returns:
            List[DroneConfig]: ドローン設定リスト
        """
        configs = []
        
        for drone_data in config_data.get("drones", []):
            config = DroneConfig(
                id=drone_data["id"],
                name=drone_data.get("name", f"Drone {drone_data['id']}"),
                mode=DroneMode(drone_data.get("mode", "auto")),
                ip_address=drone_data.get("ip_address"),
                auto_detect=drone_data.get("auto_detect", True),
                initial_position=tuple(drone_data.get("initial_position", [0.0, 0.0, 0.0])),
                fallback_to_simulation=drone_data.get("fallback_to_simulation", True)
            )
            configs.append(config)
        
        return configs
    
    @staticmethod
    def create_default_config() -> List[DroneConfig]:
        """
        デフォルト設定を作成
        
        Returns:
            List[DroneConfig]: デフォルトドローン設定
        """
        return [
            DroneConfig(
                id="drone_001",
                name="Tello EDU #1",
                mode=DroneMode.AUTO,
                auto_detect=True,
                initial_position=(0.0, 0.0, 0.0),
                fallback_to_simulation=True
            ),
            DroneConfig(
                id="drone_002",
                name="Tello EDU #2",
                mode=DroneMode.AUTO,
                auto_detect=True,
                initial_position=(2.0, 2.0, 0.0),
                fallback_to_simulation=True
            ),
            DroneConfig(
                id="drone_003",
                name="Simulator #1",
                mode=DroneMode.SIMULATION,
                initial_position=(-2.0, 2.0, 0.0),
                fallback_to_simulation=False
            )
        ]