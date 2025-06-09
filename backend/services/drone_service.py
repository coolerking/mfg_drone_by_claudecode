"""
ドローンサービス層
実機/スタブの切り替えを管理し、ドローン操作のビジネスロジックを提供
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Union, List, AsyncGenerator
from fastapi import UploadFile
from config.test_config import TestConfig
from tests.fixtures.drone_factory import create_drone_instance
from tests.stubs.drone_stub import TelloStub
from models.responses import AccelerationData, VelocityData, AttitudeData, ModelInfo


class DroneService:
    """ドローンサービスクラス"""
    
    def __init__(self):
        self.drone: Optional[Union[TelloStub, object]] = None
        self._is_connected = False
        self._is_streaming = False
        self._is_flying = False
        self._is_tracking = False
        self._target_object = ""
        self._tracking_mode = "center"
        self._mission_pad_enabled = False
    
    async def connect(self) -> Dict[str, Any]:
        """ドローン接続"""
        try:
            if self.drone is None:
                self.drone = create_drone_instance()
            
            result = self.drone.connect()
            if result:
                self._is_connected = True
                return {"success": True, "message": "ドローンに接続しました"}
            else:
                return {"success": False, "message": "ドローン接続に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"接続エラー: {str(e)}"}
    
    async def disconnect(self) -> Dict[str, Any]:
        """ドローン切断"""
        try:
            if self.drone is None:
                return {"success": False, "message": "ドローンが初期化されていません"}
            
            result = self.drone.disconnect()
            if result:
                self._is_connected = False
                self._is_streaming = False
                self._is_flying = False
                self._is_tracking = False
                return {"success": True, "message": "ドローンから切断しました"}
            else:
                return {"success": False, "message": "ドローン切断に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"切断エラー: {str(e)}"}
    
    # Flight Control Methods
    async def takeoff(self) -> Dict[str, Any]:
        """離陸"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.takeoff()
            if result:
                self._is_flying = True
                return {"success": True, "message": "離陸しました"}
            else:
                return {"success": False, "message": "離陸に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"離陸エラー: {str(e)}"}
    
    async def land(self) -> Dict[str, Any]:
        """着陸"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.land()
            if result:
                self._is_flying = False
                return {"success": True, "message": "着陸しました"}
            else:
                return {"success": False, "message": "着陸に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"着陸エラー: {str(e)}"}
    
    async def emergency(self) -> Dict[str, Any]:
        """緊急停止"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.emergency()
            if result:
                self._is_flying = False
                return {"success": True, "message": "緊急停止しました"}
            else:
                return {"success": False, "message": "緊急停止に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"緊急停止エラー: {str(e)}"}
    
    async def stop(self) -> Dict[str, Any]:
        """ホバリング"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.stop()
            if result:
                return {"success": True, "message": "ホバリング中です"}
            else:
                return {"success": False, "message": "ホバリングに失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ホバリングエラー: {str(e)}"}
    
    # Movement Methods
    async def move(self, direction: str, distance: int) -> Dict[str, Any]:
        """基本移動"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.move(direction, distance)
            if result:
                return {"success": True, "message": f"{direction}方向に{distance}cm移動しました"}
            else:
                return {"success": False, "message": "移動に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"移動エラー: {str(e)}"}
    
    async def rotate(self, direction: str, angle: int) -> Dict[str, Any]:
        """回転"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.rotate(direction, angle)
            if result:
                return {"success": True, "message": f"{direction}方向に{angle}度回転しました"}
            else:
                return {"success": False, "message": "回転に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"回転エラー: {str(e)}"}
    
    async def flip(self, direction: str) -> Dict[str, Any]:
        """宙返り"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.flip(direction)
            if result:
                return {"success": True, "message": f"{direction}方向に宙返りしました"}
            else:
                return {"success": False, "message": "宙返りに失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"宙返りエラー: {str(e)}"}
    
    # Advanced Movement Methods
    async def go_xyz(self, x: int, y: int, z: int, speed: int) -> Dict[str, Any]:
        """座標移動"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.go_xyz_speed(x, y, z, speed)
            if result:
                return {"success": True, "message": f"座標({x}, {y}, {z})に移動しました"}
            else:
                return {"success": False, "message": "座標移動に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"座標移動エラー: {str(e)}"}
    
    async def curve_xyz(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int) -> Dict[str, Any]:
        """曲線飛行"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)
            if result:
                return {"success": True, "message": f"曲線飛行が完了しました"}
            else:
                return {"success": False, "message": "曲線飛行に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"曲線飛行エラー: {str(e)}"}
    
    async def rc_control(self, left_right_velocity: int, forward_backward_velocity: int, 
                        up_down_velocity: int, yaw_velocity: int) -> Dict[str, Any]:
        """リアルタイム制御"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.send_rc_control(left_right_velocity, forward_backward_velocity, 
                                               up_down_velocity, yaw_velocity)
            if result:
                return {"success": True, "message": "リアルタイム制御コマンドを送信しました"}
            else:
                return {"success": False, "message": "リアルタイム制御に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"リアルタイム制御エラー: {str(e)}"}
    
    # Sensor Methods
    async def get_status(self) -> Dict[str, Any]:
        """ドローン状態取得"""
        if not self._is_connected:
            return {"connected": False}
        
        try:
            return {
                "connected": self._is_connected,
                "battery": self.drone.get_battery(),
                "height": self.drone.get_height(),
                "temperature": self.drone.get_temperature(),
                "flight_time": self.drone.get_flight_time(),
                "speed": self.drone.get_speed(),
                "barometer": self.drone.get_barometer(),
                "distance_tof": self.drone.get_distance_tof(),
                "acceleration": {
                    "x": self.drone.get_acceleration_x(),
                    "y": self.drone.get_acceleration_y(),
                    "z": self.drone.get_acceleration_z()
                },
                "velocity": {
                    "x": self.drone.get_speed_x(),
                    "y": self.drone.get_speed_y(),
                    "z": self.drone.get_speed_z()
                },
                "attitude": {
                    "pitch": self.drone.get_pitch(),
                    "roll": self.drone.get_roll(),
                    "yaw": self.drone.get_yaw()
                }
            }
        except Exception as e:
            return {"error": f"状態取得エラー: {str(e)}"}
    
    async def get_battery(self) -> int:
        """バッテリー残量取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_battery()
    
    async def get_height(self) -> int:
        """飛行高度取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_height()
    
    async def get_temperature(self) -> int:
        """温度取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_temperature()
    
    async def get_flight_time(self) -> int:
        """飛行時間取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_flight_time()
    
    async def get_barometer(self) -> float:
        """気圧取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_barometer()
    
    async def get_distance_tof(self) -> int:
        """ToFセンサー距離取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return self.drone.get_distance_tof()
    
    async def get_acceleration(self) -> AccelerationData:
        """加速度取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return AccelerationData(
            x=self.drone.get_acceleration_x(),
            y=self.drone.get_acceleration_y(),
            z=self.drone.get_acceleration_z()
        )
    
    async def get_velocity(self) -> VelocityData:
        """速度取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return VelocityData(
            x=self.drone.get_speed_x(),
            y=self.drone.get_speed_y(),
            z=self.drone.get_speed_z()
        )
    
    async def get_attitude(self) -> AttitudeData:
        """姿勢角取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        return AttitudeData(
            pitch=self.drone.get_pitch(),
            roll=self.drone.get_roll(),
            yaw=self.drone.get_yaw()
        )
    
    # Camera Methods
    async def start_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング開始"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if self._is_streaming:
            return {"success": False, "message": "ストリーミングは既に開始されています"}
        
        try:
            result = self.drone.streamon()
            if result:
                self._is_streaming = True
                return {"success": True, "message": "ストリーミングを開始しました"}
            else:
                return {"success": False, "message": "ストリーミング開始に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ストリーミング開始エラー: {str(e)}"}
    
    async def stop_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング停止"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_streaming:
            return {"success": False, "message": "ストリーミングは開始されていません"}
        
        try:
            result = self.drone.streamoff()
            if result:
                self._is_streaming = False
                return {"success": True, "message": "ストリーミングを停止しました"}
            else:
                return {"success": False, "message": "ストリーミング停止に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ストリーミング停止エラー: {str(e)}"}
    
    async def get_stream(self) -> Optional[AsyncGenerator[bytes, None]]:
        """ビデオストリーム取得"""
        if not self._is_streaming:
            return None
        
        async def generate_frames():
            try:
                while self._is_streaming:
                    # Mock frame generation for simulation
                    frame_data = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + b"fake_jpeg_data" + b"\r\n"
                    yield frame_data
                    await asyncio.sleep(1/30)  # 30 FPS
            except Exception:
                pass
        
        return generate_frames()
    
    async def take_photo(self) -> Dict[str, Any]:
        """写真撮影"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.take_picture()
            if result:
                return {"success": True, "message": "写真を撮影しました"}
            else:
                return {"success": False, "message": "写真撮影に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"写真撮影エラー: {str(e)}"}
    
    async def start_video_recording(self) -> Dict[str, Any]:
        """動画録画開始"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.start_video()
            if result:
                return {"success": True, "message": "動画録画を開始しました"}
            else:
                return {"success": False, "message": "動画録画開始に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"動画録画開始エラー: {str(e)}"}
    
    async def stop_video_recording(self) -> Dict[str, Any]:
        """動画録画停止"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.stop_video()
            if result:
                return {"success": True, "message": "動画録画を停止しました"}
            else:
                return {"success": False, "message": "動画録画停止に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"動画録画停止エラー: {str(e)}"}
    
    async def update_camera_settings(self, resolution: Optional[str] = None, 
                                   fps: Optional[str] = None, bitrate: Optional[int] = None) -> Dict[str, Any]:
        """カメラ設定変更"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            changes = []
            if resolution:
                result = self.drone.set_video_resolution(resolution)
                if result:
                    changes.append(f"解像度を{resolution}に設定")
            
            if fps:
                result = self.drone.set_video_fps(fps)
                if result:
                    changes.append(f"フレームレートを{fps}に設定")
            
            if bitrate:
                result = self.drone.set_video_bitrate(bitrate)
                if result:
                    changes.append(f"ビットレートを{bitrate}に設定")
            
            if changes:
                return {"success": True, "message": f"カメラ設定を変更しました: {', '.join(changes)}"}
            else:
                return {"success": False, "message": "設定変更に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"カメラ設定エラー: {str(e)}"}
    
    # Settings Methods
    async def set_wifi(self, ssid: str, password: str) -> Dict[str, Any]:
        """WiFi設定"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.set_wifi_credentials(ssid, password)
            if result:
                return {"success": True, "message": f"WiFi設定を更新しました: {ssid}"}
            else:
                return {"success": False, "message": "WiFi設定に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"WiFi設定エラー: {str(e)}"}
    
    async def send_command(self, command: str, timeout: int = 7, expect_response: bool = True) -> Dict[str, Any]:
        """任意コマンド送信"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            response = self.drone.send_command_with_return(command, timeout)
            if response:
                return {"success": True, "response": response}
            else:
                return {"success": False, "response": "コマンド実行に失敗しました"}
        except Exception as e:
            return {"success": False, "response": f"コマンドエラー: {str(e)}"}
    
    async def set_speed(self, speed: float) -> Dict[str, Any]:
        """飛行速度設定"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if self._is_flying:
            return {"success": False, "message": "ドローンが飛行中です"}
        
        try:
            # Convert m/s to cm/s for Tello
            speed_cm_s = int(speed * 100)
            result = self.drone.set_speed(speed_cm_s)
            if result:
                return {"success": True, "message": f"飛行速度を{speed}m/sに設定しました"}
            else:
                return {"success": False, "message": "飛行速度設定に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"飛行速度設定エラー: {str(e)}"}
    
    # Mission Pad Methods
    async def enable_mission_pad(self) -> Dict[str, Any]:
        """ミッションパッド検出有効化"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.enable_mission_pads()
            if result:
                self._mission_pad_enabled = True
                return {"success": True, "message": "ミッションパッド検出を有効化しました"}
            else:
                return {"success": False, "message": "ミッションパッド検出有効化に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ミッションパッド有効化エラー: {str(e)}"}
    
    async def disable_mission_pad(self) -> Dict[str, Any]:
        """ミッションパッド検出無効化"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.disable_mission_pads()
            if result:
                self._mission_pad_enabled = False
                return {"success": True, "message": "ミッションパッド検出を無効化しました"}
            else:
                return {"success": False, "message": "ミッションパッド検出無効化に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ミッションパッド無効化エラー: {str(e)}"}
    
    async def set_mission_pad_detection_direction(self, direction: int) -> Dict[str, Any]:
        """ミッションパッド検出方向設定"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.set_mission_pad_detection_direction(direction)
            if result:
                directions = {0: "下向き", 1: "前向き", 2: "両方"}
                return {"success": True, "message": f"検出方向を{directions.get(direction, '不明')}に設定しました"}
            else:
                return {"success": False, "message": "検出方向設定に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"検出方向設定エラー: {str(e)}"}
    
    async def mission_pad_go_xyz(self, x: int, y: int, z: int, speed: int, mission_pad_id: int) -> Dict[str, Any]:
        """ミッションパッド基準移動"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.go_xyz_speed_mid(x, y, z, speed, mission_pad_id)
            if result:
                return {"success": True, "message": f"ミッションパッド{mission_pad_id}基準で座標({x}, {y}, {z})に移動しました"}
            else:
                return {"success": False, "message": "ミッションパッド基準移動に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ミッションパッド移動エラー: {str(e)}"}
    
    async def get_mission_pad_status(self) -> Dict[str, Any]:
        """ミッションパッド状態取得"""
        if not self._is_connected:
            raise Exception("ドローンが接続されていません")
        
        try:
            return {
                "mission_pad_id": self.drone.get_mission_pad_id(),
                "distance_x": self.drone.get_mission_pad_distance_x(),
                "distance_y": self.drone.get_mission_pad_distance_y(),
                "distance_z": self.drone.get_mission_pad_distance_z()
            }
        except Exception as e:
            raise Exception(f"ミッションパッド状態取得エラー: {str(e)}")
    
    # Object Tracking Methods
    async def start_tracking(self, target_object: str, tracking_mode: str = "center") -> Dict[str, Any]:
        """物体追跡開始"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_streaming:
            return {"success": False, "message": "カメラストリーミングが開始されていません"}
        
        try:
            # Mock tracking start
            self._is_tracking = True
            self._target_object = target_object
            self._tracking_mode = tracking_mode
            return {"success": True, "message": f"'{target_object}'の追跡を開始しました（{tracking_mode}モード）"}
        except Exception as e:
            return {"success": False, "message": f"追跡開始エラー: {str(e)}"}
    
    async def stop_tracking(self) -> Dict[str, Any]:
        """物体追跡停止"""
        if not self._is_tracking:
            return {"success": False, "message": "追跡が開始されていません"}
        
        try:
            self._is_tracking = False
            self._target_object = ""
            return {"success": True, "message": "物体追跡を停止しました"}
        except Exception as e:
            return {"success": False, "message": f"追跡停止エラー: {str(e)}"}
    
    async def get_tracking_status(self) -> Dict[str, Any]:
        """追跡状態取得"""
        try:
            status = {
                "is_tracking": self._is_tracking,
                "target_object": self._target_object,
                "target_detected": self._is_tracking,  # Mock detection
                "target_position": None
            }
            
            if self._is_tracking:
                # Mock position data
                status["target_position"] = {
                    "x": 320,
                    "y": 240,
                    "width": 100,
                    "height": 80
                }
            
            return status
        except Exception as e:
            raise Exception(f"追跡状態取得エラー: {str(e)}")
    
    # Model Management Methods
    async def train_model(self, object_name: str, images: List[UploadFile]) -> Dict[str, Any]:
        """モデル訓練"""
        try:
            # Mock model training
            task_id = str(uuid.uuid4())
            return {"success": True, "task_id": task_id}
        except Exception as e:
            return {"success": False, "message": f"モデル訓練エラー: {str(e)}"}
    
    async def list_models(self) -> Dict[str, Any]:
        """モデル一覧取得"""
        try:
            # Mock model list
            mock_models = [
                ModelInfo(
                    name="person_detector",
                    created_at=datetime.now(),
                    accuracy=0.85
                ),
                ModelInfo(
                    name="car_detector", 
                    created_at=datetime.now(),
                    accuracy=0.92
                )
            ]
            return {"models": mock_models}
        except Exception as e:
            raise Exception(f"モデル一覧取得エラー: {str(e)}")


# グローバルインスタンス
drone_service = DroneService()