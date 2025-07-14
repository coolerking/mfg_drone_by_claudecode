"""
Configuration Service - Drone configuration management
Handles loading and managing drone configurations from YAML files
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from .drone_factory import DroneConfig, DroneMode

logger = logging.getLogger(__name__)


@dataclass
class GlobalConfig:
    """グローバル設定"""
    default_mode: str = "auto"
    space_bounds: List[float] = None
    auto_detection: Dict[str, Any] = None
    fallback: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.space_bounds is None:
            self.space_bounds = [20.0, 20.0, 10.0]
        if self.auto_detection is None:
            self.auto_detection = {
                "enabled": True,
                "timeout": 5.0,
                "scan_interval": 30.0
            }
        if self.fallback is None:
            self.fallback = {
                "enabled": True,
                "simulation_on_failure": True
            }


@dataclass
class NetworkConfig:
    """ネットワーク設定"""
    discovery: Dict[str, Any] = None
    security: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.discovery is None:
            self.discovery = {
                "default_ips": ["192.168.10.1", "192.168.1.1", "192.168.4.1"],
                "scan_ranges": ["192.168.1.0/24", "192.168.10.0/24"],
                "connection_timeout": 3.0,
                "retry_attempts": 3,
                "retry_delay": 1.0
            }
        if self.security is None:
            self.security = {
                "allowed_ip_ranges": ["192.168.0.0/16", "10.0.0.0/8"],
                "max_concurrent_connections": 5,
                "connection_rate_limit": 10
            }


@dataclass 
class MonitoringConfig:
    """監視設定"""
    update_intervals: Dict[str, float] = None
    alerts: Dict[str, Any] = None
    logging: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.update_intervals is None:
            self.update_intervals = {
                "real_drone_state": 0.1,
                "simulation_state": 0.01,
                "health_check": 5.0
            }
        if self.alerts is None:
            self.alerts = {
                "battery_low": 15,
                "connection_lost": True,
                "collision_detected": True
            }
        if self.logging is None:
            self.logging = {
                "level": "INFO",
                "real_drone_events": True,
                "simulation_events": False,
                "network_events": True
            }


@dataclass
class PerformanceConfig:
    """パフォーマンス設定"""
    threading: Dict[str, int] = None
    cache: Dict[str, float] = None
    limits: Dict[str, int] = None
    
    def __post_init__(self):
        if self.threading is None:
            self.threading = {
                "max_worker_threads": 10,
                "state_update_workers": 2,
                "network_scan_workers": 2
            }
        if self.cache is None:
            self.cache = {
                "drone_state_ttl": 1.0,
                "network_scan_ttl": 30.0
            }
        if self.limits is None:
            self.limits = {
                "max_flight_time": 900,
                "max_simultaneous_drones": 5
            }


class DroneConfigService:
    """
    ドローン設定サービス
    YAML設定ファイルの読み込み・管理を行う
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初期化
        
        Args:
            config_dir: 設定ディレクトリパス
        """
        if config_dir is None:
            # デフォルトの設定ディレクトリを設定
            current_dir = Path(__file__).parent.parent.parent
            config_dir = current_dir / "config"
        
        self.config_dir = Path(config_dir)
        self.drone_config_file = self.config_dir / "drone_config.yaml"
        
        # 設定データ
        self.global_config: GlobalConfig = GlobalConfig()
        self.network_config: NetworkConfig = NetworkConfig()
        self.monitoring_config: MonitoringConfig = MonitoringConfig()
        self.performance_config: PerformanceConfig = PerformanceConfig()
        self.drone_configs: Dict[str, DroneConfig] = {}
        
        # 環境変数オーバーライド
        self._load_env_overrides()
        
        logger.info(f"DroneConfigService initialized: {self.config_dir}")
    
    def _load_env_overrides(self) -> None:
        """環境変数による設定オーバーライド"""
        # DRONE_MODE環境変数
        drone_mode = os.getenv("DRONE_MODE")
        if drone_mode:
            self.global_config.default_mode = drone_mode
            logger.info(f"DRONE_MODE override: {drone_mode}")
        
        # TELLO_AUTO_DETECT環境変数
        auto_detect = os.getenv("TELLO_AUTO_DETECT")
        if auto_detect:
            self.global_config.auto_detection["enabled"] = auto_detect.lower() == "true"
            logger.info(f"TELLO_AUTO_DETECT override: {auto_detect}")
        
        # TELLO_CONNECTION_TIMEOUT環境変数
        timeout = os.getenv("TELLO_CONNECTION_TIMEOUT")
        if timeout:
            try:
                self.network_config.discovery["connection_timeout"] = float(timeout)
                logger.info(f"TELLO_CONNECTION_TIMEOUT override: {timeout}")
            except ValueError:
                logger.warning(f"Invalid TELLO_CONNECTION_TIMEOUT value: {timeout}")
    
    def load_config(self) -> bool:
        """
        設定ファイルを読み込み
        
        Returns:
            bool: 読み込み成功フラグ
        """
        try:
            if not self.drone_config_file.exists():
                logger.warning(f"Config file not found: {self.drone_config_file}")
                logger.info("Using default configuration")
                self._create_default_config()
                return True
            
            with open(self.drone_config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            self._parse_config_data(config_data)
            logger.info(f"Configuration loaded successfully: {self.drone_config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Falling back to default configuration")
            self._create_default_config()
            return False
    
    def _parse_config_data(self, config_data: Dict[str, Any]) -> None:
        """設定データを解析"""
        # グローバル設定
        if "global" in config_data:
            global_data = config_data["global"]
            self.global_config = GlobalConfig(
                default_mode=global_data.get("default_mode", "auto"),
                space_bounds=global_data.get("space_bounds", [20.0, 20.0, 10.0]),
                auto_detection=global_data.get("auto_detection", {}),
                fallback=global_data.get("fallback", {})
            )
        
        # ネットワーク設定
        if "network" in config_data:
            network_data = config_data["network"]
            self.network_config = NetworkConfig(
                discovery=network_data.get("discovery", {}),
                security=network_data.get("security", {})
            )
        
        # 監視設定
        if "monitoring" in config_data:
            monitoring_data = config_data["monitoring"]
            self.monitoring_config = MonitoringConfig(
                update_intervals=monitoring_data.get("update_intervals", {}),
                alerts=monitoring_data.get("alerts", {}),
                logging=monitoring_data.get("logging", {})
            )
        
        # パフォーマンス設定
        if "performance" in config_data:
            performance_data = config_data["performance"]
            self.performance_config = PerformanceConfig(
                threading=performance_data.get("threading", {}),
                cache=performance_data.get("cache", {}),
                limits=performance_data.get("limits", {})
            )
        
        # ドローン設定
        if "drones" in config_data:
            self._parse_drone_configs(config_data["drones"])
    
    def _parse_drone_configs(self, drones_data: List[Dict[str, Any]]) -> None:
        """ドローン設定を解析"""
        self.drone_configs.clear()
        
        for drone_data in drones_data:
            try:
                config = DroneConfig(
                    id=drone_data["id"],
                    name=drone_data.get("name", f"Drone {drone_data['id']}"),
                    mode=DroneMode(drone_data.get("mode", self.global_config.default_mode)),
                    ip_address=drone_data.get("ip_address"),
                    auto_detect=drone_data.get("auto_detect", True),
                    initial_position=tuple(drone_data.get("initial_position", [0.0, 0.0, 0.0])),
                    fallback_to_simulation=drone_data.get("fallback_to_simulation", True)
                )
                
                self.drone_configs[config.id] = config
                logger.debug(f"Drone config loaded: {config.id}")
                
            except Exception as e:
                logger.error(f"Failed to parse drone config: {drone_data}, Error: {e}")
    
    def _create_default_config(self) -> None:
        """デフォルト設定を作成"""
        # デフォルトドローン設定
        default_configs = [
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
        
        for config in default_configs:
            self.drone_configs[config.id] = config
        
        logger.info("Default configuration created")
    
    def save_config(self) -> bool:
        """
        設定をファイルに保存
        
        Returns:
            bool: 保存成功フラグ
        """
        try:
            # 設定ディレクトリを作成
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # 設定データを構築
            config_data = {
                "global": asdict(self.global_config),
                "network": asdict(self.network_config),
                "monitoring": asdict(self.monitoring_config),
                "performance": asdict(self.performance_config),
                "drones": [asdict(config) for config in self.drone_configs.values()]
            }
            
            with open(self.drone_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Configuration saved: {self.drone_config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    # 設定取得メソッド
    
    def get_drone_config(self, drone_id: str) -> Optional[DroneConfig]:
        """ドローン設定を取得"""
        return self.drone_configs.get(drone_id)
    
    def get_all_drone_configs(self) -> Dict[str, DroneConfig]:
        """全ドローン設定を取得"""
        return self.drone_configs.copy()
    
    def get_global_config(self) -> GlobalConfig:
        """グローバル設定を取得"""
        return self.global_config
    
    def get_network_config(self) -> NetworkConfig:
        """ネットワーク設定を取得"""
        return self.network_config
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """監視設定を取得"""
        return self.monitoring_config
    
    def get_performance_config(self) -> PerformanceConfig:
        """パフォーマンス設定を取得"""
        return self.performance_config
    
    # 設定更新メソッド
    
    def add_drone_config(self, config: DroneConfig) -> None:
        """ドローン設定を追加"""
        self.drone_configs[config.id] = config
        logger.info(f"Drone config added: {config.id}")
    
    def remove_drone_config(self, drone_id: str) -> bool:
        """ドローン設定を削除"""
        if drone_id in self.drone_configs:
            del self.drone_configs[drone_id]
            logger.info(f"Drone config removed: {drone_id}")
            return True
        return False
    
    def update_drone_config(self, drone_id: str, **kwargs) -> bool:
        """ドローン設定を更新"""
        if drone_id not in self.drone_configs:
            return False
        
        config = self.drone_configs[drone_id]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        logger.info(f"Drone config updated: {drone_id}")
        return True
    
    # ユーティリティメソッド
    
    def get_default_ips(self) -> List[str]:
        """デフォルトIPアドレスリストを取得"""
        return self.network_config.discovery.get("default_ips", [])
    
    def get_connection_timeout(self) -> float:
        """接続タイムアウトを取得"""
        return self.network_config.discovery.get("connection_timeout", 3.0)
    
    def get_space_bounds(self) -> tuple:
        """空間境界を取得"""
        bounds = self.global_config.space_bounds
        return tuple(bounds) if bounds else (20.0, 20.0, 10.0)
    
    def is_auto_detection_enabled(self) -> bool:
        """自動検出が有効かチェック"""
        return self.global_config.auto_detection.get("enabled", True)
    
    def get_auto_detection_timeout(self) -> float:
        """自動検出タイムアウトを取得"""
        return self.global_config.auto_detection.get("timeout", 5.0)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """設定サマリーを取得"""
        return {
            "config_file": str(self.drone_config_file),
            "config_exists": self.drone_config_file.exists(),
            "total_drones": len(self.drone_configs),
            "default_mode": self.global_config.default_mode,
            "space_bounds": self.global_config.space_bounds,
            "auto_detection_enabled": self.is_auto_detection_enabled(),
            "drone_configs": [
                {
                    "id": config.id,
                    "name": config.name,
                    "mode": config.mode.value,
                    "ip_address": config.ip_address,
                    "auto_detect": config.auto_detect
                }
                for config in self.drone_configs.values()
            ]
        }