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


# グローバルインスタンス
drone_service = DroneService()