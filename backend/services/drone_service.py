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


# グローバルインスタンス
drone_service = DroneService()