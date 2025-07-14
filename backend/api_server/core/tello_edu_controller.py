"""
Tello EDU Controller - Real drone control implementation
Provides the same interface as DroneSimulator but controls actual Tello EDU drones
"""

import asyncio
import logging
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

try:
    from djitellopy import Tello
except ImportError:
    # Fallback for environments where djitellopy is not available
    Tello = None

logger = logging.getLogger(__name__)


class TelloConnectionState(Enum):
    """Tello接続状態"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class TelloEDUController:
    """
    Tello EDU実機制御クラス
    DroneSimulatorと同じインターフェースを提供し、実機制御を行う
    """
    
    def __init__(self, drone_id: str = "tello_001", ip_address: Optional[str] = None):
        """
        初期化
        
        Args:
            drone_id: ドローンID
            ip_address: Tello EDUのIPアドレス（Noneの場合は自動検出）
        """
        if Tello is None:
            raise ImportError("djitellopy library is required for TelloEDUController")
        
        self.drone_id = drone_id
        self.ip_address = ip_address
        self.tello: Optional[Tello] = None
        self.connection_state = TelloConnectionState.DISCONNECTED
        
        # 状態管理
        self._current_position = (0.0, 0.0, 0.0)  # x, y, z (m)
        self._current_velocity = (0.0, 0.0, 0.0)  # vx, vy, vz (m/s)
        self._battery_level = 100.0
        self._flight_state = "idle"
        self._is_flying = False
        self._connection_established = False
        
        # 統計情報
        self.total_flight_time = 0.0
        self.total_distance_traveled = 0.0
        self.collision_count = 0
        self.connection_start_time: Optional[float] = None
        
        # スレッド制御
        self._state_update_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._state_update_interval = 0.1  # 100ms
        
        logger.info(f"TelloEDUController initialized: {drone_id}")
    
    def connect(self) -> bool:
        """
        Tello EDUに接続
        
        Returns:
            bool: 接続成功フラグ
        """
        try:
            self.connection_state = TelloConnectionState.CONNECTING
            
            if self.ip_address:
                self.tello = Tello(host=self.ip_address)
            else:
                self.tello = Tello()
            
            # 接続試行
            self.tello.connect()
            
            # 接続確認
            battery = self.tello.get_battery()
            if battery is not None:
                self._battery_level = float(battery)
                self.connection_state = TelloConnectionState.CONNECTED
                self._connection_established = True
                self.connection_start_time = time.time()
                
                logger.info(f"Tello EDU connected: {self.drone_id}, Battery: {battery}%")
                return True
            else:
                raise Exception("Failed to get battery status")
                
        except Exception as e:
            logger.error(f"Tello EDU connection failed: {self.drone_id}, Error: {e}")
            self.connection_state = TelloConnectionState.ERROR
            self._connection_established = False
            return False
    
    def disconnect(self) -> bool:
        """
        Tello EDUから切断
        
        Returns:
            bool: 切断成功フラグ
        """
        try:
            if self.tello and self._connection_established:
                self.tello.end()
            
            self.connection_state = TelloConnectionState.DISCONNECTED
            self._connection_established = False
            self.connection_start_time = None
            
            logger.info(f"Tello EDU disconnected: {self.drone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Tello EDU disconnection failed: {self.drone_id}, Error: {e}")
            return False
    
    def start_simulation(self) -> None:
        """
        シミュレーション開始（状態監視スレッド開始）
        DroneSimulatorとの互換性のため
        """
        if self._is_running:
            logger.warning("State monitoring already running")
            return
        
        self._is_running = True
        self._state_update_thread = threading.Thread(target=self._state_update_loop, daemon=True)
        self._state_update_thread.start()
        
        logger.info("State monitoring started")
    
    def stop_simulation(self) -> None:
        """
        シミュレーション停止（状態監視スレッド停止）
        DroneSimulatorとの互換性のため
        """
        if not self._is_running:
            logger.warning("State monitoring not running")
            return
        
        self._is_running = False
        if self._state_update_thread:
            self._state_update_thread.join(timeout=1.0)
        
        logger.info("State monitoring stopped")
    
    def _state_update_loop(self) -> None:
        """状態更新ループ"""
        while self._is_running:
            try:
                if self._connection_established and self.tello:
                    self._update_state()
            except Exception as e:
                logger.error(f"State update error: {e}")
            
            time.sleep(self._state_update_interval)
    
    def _update_state(self) -> None:
        """Tello EDUから状態情報を更新"""
        try:
            # バッテリー残量更新
            battery = self.tello.get_battery()
            if battery is not None:
                self._battery_level = float(battery)
            
            # 飛行状態更新（簡易実装）
            # 実際のTello EDUでは詳細な状態取得は制限があるため、
            # 基本的な状態のみ追跡
            if self._is_flying:
                self._flight_state = "flying"
            else:
                self._flight_state = "idle"
            
        except Exception as e:
            logger.error(f"Failed to update state from Tello: {e}")
    
    # DroneSimulator互換インターフェース
    
    def takeoff(self) -> bool:
        """
        離陸
        
        Returns:
            bool: 離陸成功フラグ
        """
        if not self._connection_established or not self.tello:
            logger.warning("Takeoff failed: Not connected to Tello")
            return False
        
        if self._battery_level < 10:
            logger.warning("Takeoff failed: Low battery")
            return False
        
        try:
            self.tello.takeoff()
            self._is_flying = True
            self._flight_state = "flying"
            
            # 離陸後の位置を推定（1.5m上昇）
            self._current_position = (
                self._current_position[0],
                self._current_position[1],
                1.5
            )
            
            logger.info(f"Takeoff successful: {self.drone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Takeoff failed: {self.drone_id}, Error: {e}")
            return False
    
    def land(self) -> bool:
        """
        着陸
        
        Returns:
            bool: 着陸成功フラグ
        """
        if not self._connection_established or not self.tello:
            logger.warning("Land failed: Not connected to Tello")
            return False
        
        try:
            self.tello.land()
            self._is_flying = False
            self._flight_state = "landed"
            
            # 着陸後の位置を更新
            self._current_position = (
                self._current_position[0],
                self._current_position[1],
                0.0
            )
            
            logger.info(f"Landing successful: {self.drone_id}")
            return True
            
        except Exception as e:
            logger.error(f"Landing failed: {self.drone_id}, Error: {e}")
            return False
    
    def emergency_land(self) -> None:
        """緊急着陸"""
        if not self._connection_established or not self.tello:
            logger.warning("Emergency land failed: Not connected to Tello")
            return
        
        try:
            self.tello.emergency()
            self._is_flying = False
            self._flight_state = "emergency"
            
            logger.warning(f"Emergency landing executed: {self.drone_id}")
            
        except Exception as e:
            logger.error(f"Emergency landing failed: {self.drone_id}, Error: {e}")
    
    def move_to_position(self, x: float, y: float, z: float) -> bool:
        """
        指定座標に移動
        
        Args:
            x, y, z: 目標位置 (m)
        
        Returns:
            bool: 移動成功フラグ
        """
        if not self._connection_established or not self.tello:
            logger.warning("Move failed: Not connected to Tello")
            return False
        
        if not self._is_flying:
            logger.warning("Move failed: Not flying")
            return False
        
        try:
            # 現在位置からの相対移動量を計算
            current_x, current_y, current_z = self._current_position
            dx = x - current_x
            dy = y - current_y
            dz = z - current_z
            
            # cm単位に変換
            dx_cm = int(dx * 100)
            dy_cm = int(dy * 100)
            dz_cm = int(dz * 100)
            
            # 移動範囲制限（Tello EDUの制限）
            max_move_cm = 500  # 5m
            if abs(dx_cm) > max_move_cm or abs(dy_cm) > max_move_cm or abs(dz_cm) > max_move_cm:
                logger.warning(f"Move distance too large: dx={dx_cm}, dy={dy_cm}, dz={dz_cm}")
                return False
            
            # 移動実行
            if abs(dx_cm) > 20:  # 20cm以上の移動のみ実行
                if dx_cm > 0:
                    self.tello.move_right(abs(dx_cm))
                else:
                    self.tello.move_left(abs(dx_cm))
            
            if abs(dy_cm) > 20:
                if dy_cm > 0:
                    self.tello.move_forward(abs(dy_cm))
                else:
                    self.tello.move_back(abs(dy_cm))
            
            if abs(dz_cm) > 20:
                if dz_cm > 0:
                    self.tello.move_up(abs(dz_cm))
                else:
                    self.tello.move_down(abs(dz_cm))
            
            # 位置を更新
            self._current_position = (x, y, z)
            
            logger.info(f"Move successful: {self.drone_id} to ({x:.2f}, {y:.2f}, {z:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Move failed: {self.drone_id}, Error: {e}")
            return False
    
    def rotate_to_yaw(self, yaw_degrees: float) -> bool:
        """
        指定角度に回転
        
        Args:
            yaw_degrees: 目標角度（度）
        
        Returns:
            bool: 回転成功フラグ
        """
        if not self._connection_established or not self.tello:
            logger.warning("Rotate failed: Not connected to Tello")
            return False
        
        if not self._is_flying:
            logger.warning("Rotate failed: Not flying")
            return False
        
        try:
            # 角度を-180〜180の範囲に正規化
            while yaw_degrees > 180:
                yaw_degrees -= 360
            while yaw_degrees < -180:
                yaw_degrees += 360
            
            # 回転実行
            if abs(yaw_degrees) > 10:  # 10度以上の回転のみ実行
                if yaw_degrees > 0:
                    self.tello.rotate_clockwise(int(abs(yaw_degrees)))
                else:
                    self.tello.rotate_counter_clockwise(int(abs(yaw_degrees)))
            
            logger.info(f"Rotation successful: {self.drone_id} to {yaw_degrees} degrees")
            return True
            
        except Exception as e:
            logger.error(f"Rotation failed: {self.drone_id}, Error: {e}")
            return False
    
    # 状態取得メソッド
    
    def get_current_position(self) -> Tuple[float, float, float]:
        """現在位置を取得"""
        return self._current_position
    
    def get_current_velocity(self) -> Tuple[float, float, float]:
        """現在速度を取得"""
        return self._current_velocity
    
    def get_battery_level(self) -> float:
        """バッテリー残量を取得"""
        return self._battery_level
    
    def get_flight_state(self) -> str:
        """飛行状態を取得"""
        return self._flight_state
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報を取得
        DroneSimulatorとの互換性のため
        """
        flight_time = 0.0
        if self.connection_start_time:
            flight_time = time.time() - self.connection_start_time
        
        return {
            "drone_id": self.drone_id,
            "current_position": self.get_current_position(),
            "current_velocity": self.get_current_velocity(),
            "battery_level": self.get_battery_level(),
            "flight_state": self.get_flight_state(),
            "total_flight_time": flight_time,
            "total_distance_traveled": self.total_distance_traveled,
            "collision_count": self.collision_count,
            "obstacle_count": 0,  # 実機では障害物情報なし
            "is_real_drone": True,  # 実機識別フラグ
            "connection_state": self.connection_state.value,
            "ip_address": self.ip_address
        }
    
    def get_connection_state(self) -> TelloConnectionState:
        """接続状態を取得"""
        return self.connection_state
    
    def is_connected(self) -> bool:
        """接続状態確認"""
        return self._connection_established
    
    def get_real_drone_info(self) -> Dict[str, Any]:
        """
        実機固有の情報を取得
        
        Returns:
            dict: 実機情報
        """
        info = {
            "drone_id": self.drone_id,
            "ip_address": self.ip_address,
            "connection_state": self.connection_state.value,
            "is_connected": self._connection_established,
            "battery_level": self._battery_level,
            "is_flying": self._is_flying
        }
        
        if self._connection_established and self.tello:
            try:
                # Tello固有の情報を取得
                info.update({
                    "height": self.tello.get_height(),
                    "temperature": self.tello.get_temperature(),
                    "attitude": {
                        "pitch": self.tello.get_pitch(),
                        "roll": self.tello.get_roll(),
                        "yaw": self.tello.get_yaw()
                    },
                    "speed": {
                        "x": self.tello.get_speed_x(),
                        "y": self.tello.get_speed_y(),
                        "z": self.tello.get_speed_z()
                    },
                    "barometer": self.tello.get_barometer(),
                    "wifi_signal": self.tello.query_wifi_signal_noise_ratio()
                })
            except Exception as e:
                logger.warning(f"Failed to get detailed Tello info: {e}")
        
        return info


class TelloNetworkService:
    """
    Tello EDUネットワーク検出サービス
    LAN内のTello EDUを自動検出する
    """
    
    @staticmethod
    def scan_for_tello_drones(timeout: float = 5.0) -> List[str]:
        """
        LAN内のTello EDUを検索
        
        Args:
            timeout: 検索タイムアウト（秒）
        
        Returns:
            List[str]: 検出されたTello EDUのIPアドレスリスト
        """
        detected_drones = []
        
        # 簡単な実装：一般的なTello EDUのIPアドレス範囲をスキャン
        # 実際の実装では、より高度なネットワークスキャンが必要
        
        common_tello_ips = [
            "192.168.10.1",  # Tello EDUのデフォルトIP
            "192.168.1.1",
            "192.168.4.1"
        ]
        
        for ip in common_tello_ips:
            try:
                # Telloへの接続テスト
                test_tello = Tello(host=ip) if Tello else None
                if test_tello:
                    test_tello.connect()
                    battery = test_tello.get_battery()
                    if battery is not None:
                        detected_drones.append(ip)
                        logger.info(f"Tello EDU detected at {ip}, Battery: {battery}%")
                    test_tello.end()
            except Exception:
                # 接続失敗は無視
                pass
        
        return detected_drones
    
    @staticmethod
    def verify_tello_connection(ip_address: str, timeout: float = 3.0) -> bool:
        """
        指定IPアドレスのTello EDU接続を確認
        
        Args:
            ip_address: IPアドレス
            timeout: タイムアウト（秒）
        
        Returns:
            bool: 接続可能フラグ
        """
        try:
            if not Tello:
                return False
            
            test_tello = Tello(host=ip_address)
            test_tello.connect()
            battery = test_tello.get_battery()
            test_tello.end()
            
            return battery is not None
            
        except Exception as e:
            logger.debug(f"Tello connection verification failed for {ip_address}: {e}")
            return False