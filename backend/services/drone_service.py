"""
ドローンサービス層
実機/スタブの切り替えを管理し、ドローン操作のビジネスロジックを提供
"""

from typing import Optional, Dict, Any, Union
from config.test_config import TestConfig
from tests.fixtures.drone_factory import create_drone_instance
from tests.stubs.drone_stub import TelloStub


class DroneService:
    """ドローンサービスクラス"""
    
    def __init__(self):
        self.drone: Optional[Union[TelloStub, object]] = None
        self._is_connected = False
        self._is_streaming = False
        self._is_flying = False
    
    def connect(self) -> Dict[str, Any]:
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
    
    def disconnect(self) -> Dict[str, Any]:
        """ドローン切断"""
        try:
            if self.drone is None:
                return {"success": False, "message": "ドローンが初期化されていません"}
            
            result = self.drone.disconnect()
            if result:
                self._is_connected = False
                self._is_streaming = False
                self._is_flying = False
                return {"success": True, "message": "ドローンから切断しました"}
            else:
                return {"success": False, "message": "ドローン切断に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"切断エラー: {str(e)}"}
    
    def takeoff(self) -> Dict[str, Any]:
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
    
    def land(self) -> Dict[str, Any]:
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
    
    def emergency(self) -> Dict[str, Any]:
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
    
    def stop(self) -> Dict[str, Any]:
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
    
    def get_status(self) -> Dict[str, Any]:
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

    def move(self, direction: str, distance: int) -> Dict[str, Any]:
        """基本移動"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            # 方向に応じてメソッドを呼び分け
            direction_methods = {
                "up": self.drone.move_up,
                "down": self.drone.move_down,
                "left": self.drone.move_left,
                "right": self.drone.move_right,
                "forward": self.drone.move_forward,
                "back": self.drone.move_back
            }
            
            if direction not in direction_methods:
                return {"success": False, "message": f"無効な方向: {direction}"}
            
            result = direction_methods[direction](distance)
            if result:
                return {"success": True, "message": f"{direction}方向に{distance}cm移動しました"}
            else:
                return {"success": False, "message": "移動に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"移動エラー: {str(e)}"}

    def rotate(self, direction: str, angle: int) -> Dict[str, Any]:
        """回転"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            if direction == "clockwise":
                result = self.drone.rotate_clockwise(angle)
            elif direction == "counter_clockwise":
                result = self.drone.rotate_counter_clockwise(angle)
            else:
                return {"success": False, "message": f"無効な回転方向: {direction}"}
            
            if result:
                return {"success": True, "message": f"{direction}方向に{angle}度回転しました"}
            else:
                return {"success": False, "message": "回転に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"回転エラー: {str(e)}"}

    def flip(self, direction: str) -> Dict[str, Any]:
        """宙返り"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            flip_methods = {
                "left": self.drone.flip_left,
                "right": self.drone.flip_right,
                "forward": self.drone.flip_forward,
                "back": self.drone.flip_back
            }
            
            if direction not in flip_methods:
                return {"success": False, "message": f"無効な宙返り方向: {direction}"}
            
            result = flip_methods[direction]()
            if result:
                return {"success": True, "message": f"{direction}方向に宙返りしました"}
            else:
                return {"success": False, "message": "宙返りに失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"宙返りエラー: {str(e)}"}

    def get_battery(self) -> Dict[str, Any]:
        """バッテリー残量取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            battery = self.drone.get_battery()
            return {"battery": battery}
        except Exception as e:
            return {"error": f"バッテリー取得エラー: {str(e)}"}

    def get_height(self) -> Dict[str, Any]:
        """飛行高度取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            height = self.drone.get_height()
            return {"height": height}
        except Exception as e:
            return {"error": f"高度取得エラー: {str(e)}"}

    def get_temperature(self) -> Dict[str, Any]:
        """温度取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            temperature = self.drone.get_temperature()
            return {"temperature": temperature}
        except Exception as e:
            return {"error": f"温度取得エラー: {str(e)}"}

    def get_flight_time(self) -> Dict[str, Any]:
        """累積飛行時間取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            flight_time = self.drone.get_flight_time()
            return {"flight_time": flight_time}
        except Exception as e:
            return {"error": f"飛行時間取得エラー: {str(e)}"}

    def get_barometer(self) -> Dict[str, Any]:
        """気圧センサー取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            barometer = self.drone.get_barometer()
            return {"barometer": barometer}
        except Exception as e:
            return {"error": f"気圧取得エラー: {str(e)}"}

    def get_distance_tof(self) -> Dict[str, Any]:
        """ToFセンサー距離取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            distance_tof = self.drone.get_distance_tof()
            return {"distance_tof": distance_tof}
        except Exception as e:
            return {"error": f"ToF距離取得エラー: {str(e)}"}

    def get_acceleration(self) -> Dict[str, Any]:
        """加速度取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            acceleration = {
                "x": self.drone.get_acceleration_x(),
                "y": self.drone.get_acceleration_y(),
                "z": self.drone.get_acceleration_z()
            }
            return {"acceleration": acceleration}
        except Exception as e:
            return {"error": f"加速度取得エラー: {str(e)}"}

    def get_velocity(self) -> Dict[str, Any]:
        """速度取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            velocity = {
                "x": self.drone.get_speed_x(),
                "y": self.drone.get_speed_y(),
                "z": self.drone.get_speed_z()
            }
            return {"velocity": velocity}
        except Exception as e:
            return {"error": f"速度取得エラー: {str(e)}"}

    def get_attitude(self) -> Dict[str, Any]:
        """姿勢角取得"""
        if not self._is_connected:
            return {"error": "ドローンが接続されていません"}
        
        try:
            attitude = {
                "pitch": self.drone.get_pitch(),
                "roll": self.drone.get_roll(),
                "yaw": self.drone.get_yaw()
            }
            return {"attitude": attitude}
        except Exception as e:
            return {"error": f"姿勢角取得エラー: {str(e)}"}

    def go_xyz(self, x: int, y: int, z: int, speed: int) -> Dict[str, Any]:
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

    def curve_xyz(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int) -> Dict[str, Any]:
        """曲線飛行"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_flying:
            return {"success": False, "message": "ドローンが飛行していません"}
        
        try:
            result = self.drone.curve_xyz_speed(x1, y1, z1, x2, y2, z2, speed)
            if result:
                return {"success": True, "message": f"曲線飛行を実行しました"}
            else:
                return {"success": False, "message": "曲線飛行に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"曲線飛行エラー: {str(e)}"}

    def rc_control(self, left_right: int, forward_backward: int, up_down: int, yaw: int) -> Dict[str, Any]:
        """リアルタイム制御"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            self.drone.send_rc_control(left_right, forward_backward, up_down, yaw)
            return {"success": True, "message": "RC制御コマンドを送信しました"}
        except Exception as e:
            return {"success": False, "message": f"RC制御エラー: {str(e)}"}

    def start_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング開始"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if self._is_streaming:
            return {"success": False, "message": "ストリーミングが既に開始済みです"}
        
        try:
            result = self.drone.streamon()
            if result:
                self._is_streaming = True
                return {"success": True, "message": "ストリーミングを開始しました"}
            else:
                return {"success": False, "message": "ストリーミング開始に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ストリーミング開始エラー: {str(e)}"}

    def stop_stream(self) -> Dict[str, Any]:
        """ビデオストリーミング停止"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if not self._is_streaming:
            return {"success": False, "message": "ストリーミングが未開始です"}
        
        try:
            result = self.drone.streamoff()
            if result:
                self._is_streaming = False
                return {"success": True, "message": "ストリーミングを停止しました"}
            else:
                return {"success": False, "message": "ストリーミング停止に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"ストリーミング停止エラー: {str(e)}"}

    def take_photo(self) -> Dict[str, Any]:
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

    def start_video(self) -> Dict[str, Any]:
        """動画録画開始"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.start_video_capture()
            if result:
                return {"success": True, "message": "動画録画を開始しました"}
            else:
                return {"success": False, "message": "動画録画開始に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"動画録画開始エラー: {str(e)}"}

    def stop_video(self) -> Dict[str, Any]:
        """動画録画停止"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.stop_video_capture()
            if result:
                return {"success": True, "message": "動画録画を停止しました"}
            else:
                return {"success": False, "message": "動画録画停止に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"動画録画停止エラー: {str(e)}"}

    def set_camera_settings(self, resolution: str = None, fps: str = None, bitrate: int = None) -> Dict[str, Any]:
        """カメラ設定変更"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.set_camera_settings(resolution=resolution, fps=fps, bitrate=bitrate)
            if result:
                return {"success": True, "message": "カメラ設定を変更しました"}
            else:
                return {"success": False, "message": "カメラ設定変更に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"カメラ設定エラー: {str(e)}"}

    def set_wifi(self, ssid: str, password: str) -> Dict[str, Any]:
        """WiFi設定"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            result = self.drone.set_wifi_credentials(ssid, password)
            if result:
                return {"success": True, "message": "WiFi設定を変更しました"}
            else:
                return {"success": False, "message": "WiFi設定変更に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"WiFi設定エラー: {str(e)}"}

    def send_command(self, command: str, timeout: int = 7, expect_response: bool = True) -> Dict[str, Any]:
        """任意コマンド送信"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        
        try:
            if expect_response:
                response = self.drone.send_command_with_return(command, timeout)
                if response == "ok":
                    return {"success": True, "message": "コマンドが正常に実行されました", "response": response}
                else:
                    return {"success": False, "message": f"コマンド実行に失敗しました: {response}", "response": response}
            else:
                self.drone.send_command_without_return(command)
                return {"success": True, "message": "コマンドを送信しました", "response": ""}
        except Exception as e:
            if "Timeout" in str(e):
                return {"success": False, "message": "コマンドタイムアウト"}
            else:
                return {"success": False, "message": f"コマンド送信エラー: {str(e)}"}

    def set_speed(self, speed: float) -> Dict[str, Any]:
        """飛行速度設定"""
        if not self._is_connected:
            return {"success": False, "message": "ドローンが接続されていません"}
        if self._is_flying:
            return {"success": False, "message": "ドローンが飛行中です"}
        
        try:
            result = self.drone.set_speed(speed)
            if result:
                return {"success": True, "message": f"飛行速度を{speed}m/sに設定しました"}
            else:
                return {"success": False, "message": "飛行速度設定に失敗しました"}
        except Exception as e:
            return {"success": False, "message": f"飛行速度設定エラー: {str(e)}"}


# グローバルインスタンス
drone_service = DroneService()