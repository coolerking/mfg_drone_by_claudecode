"""
Tello EDUドローンのスタブ実装
実機がない環境でのテストに使用
"""

import asyncio
import random
import time
from typing import Optional, Dict, Any
from unittest.mock import MagicMock


class TelloStub:
    """djitellopyのTelloクラスのスタブ実装"""
    
    def __init__(self):
        self._connected = False
        self._streaming = False
        self._flying = False
        self._battery = 100
        self._height = 0
        self._temperature = 25
        self._flight_time = 0
        self._speed = 10.0
        self._mission_pads_enabled = False
        self._mission_pad_detection_direction = 0
        self._last_command_time = time.time()
        
        # センサー値のシミュレーション
        self._barometer = 1013.25
        self._distance_tof = 500
        self._acceleration = {"x": 0.0, "y": 0.0, "z": 1.0}
        self._velocity = {"x": 0, "y": 0, "z": 0}
        self._attitude = {"pitch": 0, "roll": 0, "yaw": 0}
        self._mission_pad_id = -1
        self._mission_pad_distance = {"x": 0, "y": 0, "z": 0}
        
        # 追跡関連の状態
        self._tracking = False
        self._target_object = None
        self._tracking_mode = None
        
        # エラーシミュレーション用フラグ
        self._simulate_connection_error = False
        self._simulate_command_error = False
        self._simulate_timeout = False
        
    def connect(self) -> bool:
        """ドローン接続をシミュレート"""
        if self._simulate_connection_error:
            raise Exception("Connection failed")
        
        if self._simulate_timeout:
            time.sleep(10)  # タイムアウトをシミュレート
            
        self._connected = True
        return True
    
    def disconnect(self) -> bool:
        """ドローン切断をシミュレート"""
        self._connected = False
        self._streaming = False
        self._flying = False
        return True
    
    def takeoff(self) -> bool:
        """離陸をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if self._flying:
            raise Exception("Already flying")
        if self._simulate_command_error:
            return False
            
        self._flying = True
        self._height = 120  # 1.2m
        self._battery = max(0, self._battery - 5)
        return True
    
    def land(self) -> bool:
        """着陸をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if not self._flying:
            raise Exception("Not flying")
        if self._simulate_command_error:
            return False
            
        self._flying = False
        self._height = 0
        self._battery = max(0, self._battery - 2)
        return True
    
    def emergency(self) -> bool:
        """緊急停止をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if self._simulate_command_error:
            return False
            
        self._flying = False
        self._height = 0
        return True
    
    def stop(self) -> bool:
        """ホバリングをシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if not self._flying:
            raise Exception("Not flying")
        if self._simulate_command_error:
            return False
        return True
    
    def move_up(self, distance: int) -> bool:
        """上移動をシミュレート"""
        return self._move_command(distance)
    
    def move_down(self, distance: int) -> bool:
        """下移動をシミュレート"""
        return self._move_command(distance)
    
    def move_left(self, distance: int) -> bool:
        """左移動をシミュレート"""
        return self._move_command(distance)
    
    def move_right(self, distance: int) -> bool:
        """右移動をシミュレート"""
        return self._move_command(distance)
    
    def move_forward(self, distance: int) -> bool:
        """前進をシミュレート"""
        return self._move_command(distance)
    
    def move_back(self, distance: int) -> bool:
        """後退をシミュレート"""
        return self._move_command(distance)
    
    def rotate_clockwise(self, angle: int) -> bool:
        """時計回り回転をシミュレート"""
        return self._move_command(angle)
    
    def rotate_counter_clockwise(self, angle: int) -> bool:
        """反時計回り回転をシミュレート"""
        return self._move_command(angle)
    
    def flip_left(self) -> bool:
        """左宙返りをシミュレート"""
        return self._move_command(0)
    
    def flip_right(self) -> bool:
        """右宙返りをシミュレート"""
        return self._move_command(0)
    
    def flip_forward(self) -> bool:
        """前宙返りをシミュレート"""
        return self._move_command(0)
    
    def flip_back(self) -> bool:
        """後宙返りをシミュレート"""
        return self._move_command(0)
    
    def go_xyz_speed(self, x: int, y: int, z: int, speed: int) -> bool:
        """座標移動をシミュレート"""
        if not self._connected or not self._flying:
            return False
        if self._simulate_command_error:
            return False
        self._battery = max(0, self._battery - 3)
        return True
    
    def curve_xyz_speed(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int) -> bool:
        """曲線飛行をシミュレート"""
        if not self._connected or not self._flying:
            return False
        if self._simulate_command_error:
            return False
        self._battery = max(0, self._battery - 5)
        return True
    
    def send_rc_control(self, left_right: int, forward_backward: int, up_down: int, yaw: int) -> bool:
        """リアルタイム制御をシミュレート"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        # バッテリー消費をシミュレート
        if any([left_right, forward_backward, up_down, yaw]):
            self._battery = max(0, self._battery - 1)
        return True
    
    def streamon(self) -> bool:
        """ビデオストリーミング開始をシミュレート"""
        if not self._connected:
            return False
        if self._streaming:
            return False
        if self._simulate_command_error:
            return False
        self._streaming = True
        return True
    
    def streamoff(self) -> bool:
        """ビデオストリーミング停止をシミュレート"""
        if not self._connected:
            return False
        if not self._streaming:
            return False
        self._streaming = False
        return True
    
    def get_frame_read(self):
        """フレーム読み取りオブジェクトをシミュレート"""
        if not self._streaming:
            return None
        return MagicMock()
    
    def take_picture(self) -> bool:
        """写真撮影をシミュレート"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def start_video_capture(self) -> bool:
        """動画録画開始をシミュレート"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def stop_video_capture(self) -> bool:
        """動画録画停止をシミュレート"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def set_video_resolution(self, resolution: str) -> bool:
        """ビデオ解像度設定をシミュレート"""
        if not self._connected:
            return False
        if resolution not in ["high", "low"]:
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def set_video_fps(self, fps: str) -> bool:
        """ビデオFPS設定をシミュレート"""
        if not self._connected:
            return False
        if fps not in ["high", "middle", "low"]:
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def set_video_bitrate(self, bitrate: int) -> bool:
        """ビデオビットレート設定をシミュレート"""
        if not self._connected:
            return False
        if not (1 <= bitrate <= 5):
            return False
        if self._simulate_command_error:
            return False
        return True
    
    def set_camera_settings(self, resolution: str = None, fps: str = None, bitrate: int = None) -> bool:
        """カメラ設定統合メソッド"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        
        if resolution and resolution not in ["high", "low"]:
            return False
        if fps and fps not in ["high", "middle", "low"]:
            return False
        if bitrate and not (1 <= bitrate <= 5):
            return False
        
        return True
    
    def set_speed(self, speed: int) -> bool:
        """飛行速度設定をシミュレート（cm/s単位）"""
        if not self._connected:
            return False
        # DroneServiceはm/sをcm/sに変換して渡すので、100-1500の範囲をチェック
        if not (100 <= speed <= 1500):
            return False
        if self._flying:
            return False
        self._speed = speed / 100.0  # 内部ではm/s単位で保存
        return True
    
    def set_wifi_credentials(self, ssid: str, password: str) -> bool:
        """WiFi設定をシミュレート"""
        if not self._connected:
            return False
        if len(ssid) > 32 or len(password) > 64:
            return False
        return True
    
    def send_command_with_return(self, command: str, timeout: int = 7) -> str:
        """コマンド送信（レスポンス付き）をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if self._simulate_timeout:
            time.sleep(timeout + 1)
            raise Exception("Timeout")
        if self._simulate_command_error:
            return "error"
        return "ok"
    
    def send_command_without_return(self, command: str):
        """コマンド送信（レスポンス無し）をシミュレート"""
        if not self._connected:
            return
        # ノンブロッキング
        pass
    
    def enable_mission_pads(self) -> bool:
        """ミッションパッド有効化をシミュレート"""
        if not self._connected:
            return False
        self._mission_pads_enabled = True
        return True
    
    def disable_mission_pads(self) -> bool:
        """ミッションパッド無効化をシミュレート"""
        if not self._connected:
            return False
        self._mission_pads_enabled = False
        return True
    
    def set_mission_pad_detection_direction(self, direction: int) -> bool:
        """ミッションパッド検出方向設定をシミュレート"""
        if not self._connected:
            return False
        if direction not in [0, 1, 2]:
            return False
        self._mission_pad_detection_direction = direction
        return True
    
    def go_xyz_speed_mid(self, x: int, y: int, z: int, speed: int, mid: int) -> bool:
        """ミッションパッド基準移動をシミュレート"""
        if not self._connected or not self._flying:
            return False
        if not self._mission_pads_enabled:
            return False
        if not (1 <= mid <= 8):
            return False
        if self._simulate_command_error:
            return False
        return True
    
    # センサー値取得メソッド
    def get_battery(self) -> int:
        """バッテリー残量取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        # 時間経過でバッテリー減少をシミュレート
        elapsed = time.time() - self._last_command_time
        self._battery = max(0, self._battery - int(elapsed / 60))
        self._last_command_time = time.time()
        return self._battery
    
    def get_height(self) -> int:
        """高度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._height + random.randint(-5, 5)  # ノイズをシミュレート
    
    def get_temperature(self) -> int:
        """温度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._temperature + random.randint(-2, 2)
    
    def get_flight_time(self) -> int:
        """飛行時間取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return int(time.time() - self._last_command_time)
    
    def get_speed(self) -> float:
        """現在速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._speed + random.uniform(-1.0, 1.0)
    
    def get_barometer(self) -> float:
        """気圧取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._barometer + random.uniform(-5.0, 5.0)
    
    def get_distance_tof(self) -> int:
        """ToF距離取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._distance_tof + random.randint(-50, 50)
    
    def get_acceleration_x(self) -> float:
        """X軸加速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._acceleration["x"] + random.uniform(-0.1, 0.1)
    
    def get_acceleration_y(self) -> float:
        """Y軸加速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._acceleration["y"] + random.uniform(-0.1, 0.1)
    
    def get_acceleration_z(self) -> float:
        """Z軸加速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._acceleration["z"] + random.uniform(-0.1, 0.1)
    
    def get_speed_x(self) -> int:
        """X軸速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._velocity["x"] + random.randint(-5, 5)
    
    def get_speed_y(self) -> int:
        """Y軸速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._velocity["y"] + random.randint(-5, 5)
    
    def get_speed_z(self) -> int:
        """Z軸速度取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._velocity["z"] + random.randint(-5, 5)
    
    def get_pitch(self) -> int:
        """ピッチ角取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._attitude["pitch"] + random.randint(-2, 2)
    
    def get_roll(self) -> int:
        """ロール角取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._attitude["roll"] + random.randint(-2, 2)
    
    def get_yaw(self) -> int:
        """ヨー角取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._attitude["yaw"] + random.randint(-2, 2)
    
    def get_mission_pad_id(self) -> int:
        """ミッションパッドID取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        if not self._mission_pads_enabled:
            return -1
        return self._mission_pad_id
    
    def get_mission_pad_distance_x(self) -> int:
        """ミッションパッドX距離取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._mission_pad_distance["x"]
    
    def get_mission_pad_distance_y(self) -> int:
        """ミッションパッドY距離取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._mission_pad_distance["y"]
    
    def get_mission_pad_distance_z(self) -> int:
        """ミッションパッドZ距離取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        return self._mission_pad_distance["z"]
    
    def _move_command(self, distance: int) -> bool:
        """移動コマンドの共通処理"""
        if not self._connected:
            return False
        if not self._flying:
            return False
        if self._simulate_command_error:
            return False
        if not (20 <= distance <= 500):
            return False
        self._battery = max(0, self._battery - 2)
        return True
    
    # エラーシミュレーション制御メソッド
    def set_simulate_connection_error(self, simulate: bool):
        """接続エラーシミュレーションを設定"""
        self._simulate_connection_error = simulate
    
    def set_simulate_command_error(self, simulate: bool):
        """コマンドエラーシミュレーションを設定"""
        self._simulate_command_error = simulate
    
    def set_simulate_timeout(self, simulate: bool):
        """タイムアウトシミュレーションを設定"""
        self._simulate_timeout = simulate
    
    # 物体追跡関連メソッド
    def start_tracking(self, target_object: str, tracking_mode: str = "center") -> bool:
        """物体追跡開始をシミュレート"""
        if not self._connected:
            return False
        if tracking_mode not in ["center", "follow"]:
            return False
        if self._simulate_command_error:
            return False
        
        self._tracking = True
        self._target_object = target_object
        self._tracking_mode = tracking_mode
        return True
    
    def stop_tracking(self) -> bool:
        """物体追跡停止をシミュレート"""
        if not self._connected:
            return False
        if self._simulate_command_error:
            return False
        
        self._tracking = False
        self._target_object = None
        self._tracking_mode = None
        return True
    
    def get_tracking_status(self) -> dict:
        """追跡状態取得をシミュレート"""
        if not self._connected:
            raise Exception("Not connected")
        
        return {
            "is_tracking": getattr(self, '_tracking', False),
            "target_object": getattr(self, '_target_object', None),
            "target_detected": random.choice([True, False]),
            "target_position": {
                "x": random.randint(0, 960),
                "y": random.randint(0, 720),
                "width": random.randint(50, 200),
                "height": random.randint(50, 200)
            } if getattr(self, '_tracking', False) else None
        }
    
    # AIモデル管理関連メソッド
    def train_model(self, object_name: str, images: list) -> dict:
        """モデル訓練をシミュレート"""
        if not images or len(images) == 0:
            return {"error": "No images provided"}
        if len(images) > 100:
            return {"error": "Too many images"}
        if self._simulate_command_error:
            return {"error": "Training failed"}
        
        # ランダムなタスクIDを生成
        task_id = f"task_{random.randint(1000, 9999)}"
        return {"task_id": task_id}
    
    def get_model_list(self) -> dict:
        """モデル一覧取得をシミュレート"""
        return {
            "models": [
                {
                    "name": "person_model",
                    "created_at": "2024-01-01T00:00:00Z",
                    "accuracy": 0.95
                },
                {
                    "name": "car_model",
                    "created_at": "2024-01-02T00:00:00Z",
                    "accuracy": 0.87
                }
            ]
        }
    
    def reset_state(self):
        """状態をリセット"""
        self._connected = False
        self._streaming = False
        self._flying = False
        self._battery = 100
        self._height = 0
        self._temperature = 25
        self._flight_time = 0
        self._simulate_connection_error = False
        self._simulate_command_error = False
        self._simulate_timeout = False
        # 追跡関連の状態もリセット
        self._tracking = False
        self._target_object = None
        self._tracking_mode = None
    
    # Generic wrapper methods for DroneService compatibility
    def move(self, direction: str, distance: int) -> bool:
        """Generic move method for DroneService compatibility"""
        direction_map = {
            "up": self.move_up,
            "down": self.move_down,
            "left": self.move_left,
            "right": self.move_right,
            "forward": self.move_forward,
            "back": self.move_back
        }
        if direction not in direction_map:
            return False
        return direction_map[direction](distance)
    
    def rotate(self, direction: str, angle: int) -> bool:
        """Generic rotate method for DroneService compatibility"""
        if direction == "clockwise":
            return self.rotate_clockwise(angle)
        elif direction == "counter_clockwise":
            return self.rotate_counter_clockwise(angle)
        else:
            return False
    
    def flip(self, direction: str) -> bool:
        """Generic flip method for DroneService compatibility"""
        direction_map = {
            "left": self.flip_left,
            "right": self.flip_right,
            "forward": self.flip_forward,
            "back": self.flip_back
        }
        if direction not in direction_map:
            return False
        return direction_map[direction]()
    
    def start_video(self) -> bool:
        """Alias for start_video_capture for DroneService compatibility"""
        return self.start_video_capture()
    
    def stop_video(self) -> bool:
        """Alias for stop_video_capture for DroneService compatibility"""
        return self.stop_video_capture()