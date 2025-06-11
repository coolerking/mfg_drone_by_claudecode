"""
Phase 1 Unit Tests: DroneService Core Methods
DroneServiceコアメソッドの単体テスト
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.drone_service import DroneService
from models.responses import AccelerationData, VelocityData, AttitudeData, ModelInfo


class TestDroneServiceInitialization:
    """DroneService初期化テスト"""

    def test_drone_service_initialization(self):
        """DroneService初期化テスト"""
        service = DroneService()
        
        assert service.drone is None
        assert service._is_connected is False
        assert service._is_streaming is False
        assert service._is_flying is False
        assert service._is_tracking is False
        assert service._target_object == ""
        assert service._tracking_mode == "center"
        assert service._mission_pad_enabled is False

    def test_drone_service_initial_state_boundaries(self):
        """DroneService初期状態境界値テスト"""
        service = DroneService()
        
        # Boolean値の境界確認
        assert isinstance(service._is_connected, bool)
        assert isinstance(service._is_streaming, bool)
        assert isinstance(service._is_flying, bool)
        assert isinstance(service._is_tracking, bool)
        assert isinstance(service._mission_pad_enabled, bool)
        
        # String値の境界確認
        assert isinstance(service._target_object, str)
        assert isinstance(service._tracking_mode, str)
        assert len(service._target_object) == 0  # 空文字列
        assert len(service._tracking_mode) > 0   # 非空文字列

    def test_drone_service_multiple_instantiation(self):
        """DroneService複数インスタンス化テスト"""
        service1 = DroneService()
        service2 = DroneService()
        
        # 異なるインスタンスであることを確認
        assert service1 is not service2
        assert id(service1) != id(service2)
        
        # 初期状態が同じであることを確認
        assert service1._is_connected == service2._is_connected
        assert service1._is_flying == service2._is_flying


class TestDroneServiceConnectionMethods:
    """DroneService接続関連メソッドテスト"""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """接続成功テスト"""
        service = DroneService()
        
        # モックドローンを設定
        mock_drone = MagicMock()
        mock_drone.connect.return_value = True
        
        with patch('services.drone_service.create_drone_instance', return_value=mock_drone):
            result = await service.connect()
        
        assert result["success"] is True
        assert "接続しました" in result["message"]
        assert service._is_connected is True
        assert service.drone is mock_drone

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """接続失敗テスト"""
        service = DroneService()
        
        # モックドローンを設定（接続失敗）
        mock_drone = MagicMock()
        mock_drone.connect.return_value = False
        
        with patch('services.drone_service.create_drone_instance', return_value=mock_drone):
            result = await service.connect()
        
        assert result["success"] is False
        assert "接続に失敗しました" in result["message"]
        assert service._is_connected is False

    @pytest.mark.asyncio
    async def test_connect_exception(self):
        """接続例外テスト"""
        service = DroneService()
        
        # 例外を発生させるモック
        mock_drone = MagicMock()
        mock_drone.connect.side_effect = Exception("Connection error")
        
        with patch('services.drone_service.create_drone_instance', return_value=mock_drone):
            result = await service.connect()
        
        assert result["success"] is False
        assert "接続エラー:" in result["message"]
        assert "Connection error" in result["message"]

    @pytest.mark.asyncio
    async def test_connect_with_existing_drone(self):
        """既存ドローンでの接続テスト"""
        service = DroneService()
        
        # 既存ドローンを設定
        existing_drone = MagicMock()
        existing_drone.connect.return_value = True
        service.drone = existing_drone
        
        result = await service.connect()
        
        assert result["success"] is True
        assert service.drone is existing_drone
        existing_drone.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """切断成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = True
        service._is_flying = True
        service._is_tracking = True
        
        mock_drone = MagicMock()
        mock_drone.disconnect.return_value = True
        service.drone = mock_drone
        
        result = await service.disconnect()
        
        assert result["success"] is True
        assert "切断しました" in result["message"]
        assert service._is_connected is False
        assert service._is_streaming is False
        assert service._is_flying is False
        assert service._is_tracking is False

    @pytest.mark.asyncio
    async def test_disconnect_no_drone(self):
        """ドローン未初期化での切断テスト"""
        service = DroneService()
        service.drone = None
        
        result = await service.disconnect()
        
        assert result["success"] is False
        assert "初期化されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_disconnect_failure(self):
        """切断失敗テスト"""
        service = DroneService()
        
        mock_drone = MagicMock()
        mock_drone.disconnect.return_value = False
        service.drone = mock_drone
        
        result = await service.disconnect()
        
        assert result["success"] is False
        assert "切断に失敗しました" in result["message"]

    @pytest.mark.asyncio
    async def test_disconnect_exception(self):
        """切断例外テスト"""
        service = DroneService()
        
        mock_drone = MagicMock()
        mock_drone.disconnect.side_effect = Exception("Disconnect error")
        service.drone = mock_drone
        
        result = await service.disconnect()
        
        assert result["success"] is False
        assert "切断エラー:" in result["message"]


class TestDroneServiceFlightControlMethods:
    """DroneService飛行制御メソッドテスト"""

    @pytest.mark.asyncio
    async def test_takeoff_success(self):
        """離陸成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.takeoff.return_value = True
        service.drone = mock_drone
        
        result = await service.takeoff()
        
        assert result["success"] is True
        assert "離陸しました" in result["message"]
        assert service._is_flying is True

    @pytest.mark.asyncio
    async def test_takeoff_not_connected(self):
        """未接続での離陸テスト"""
        service = DroneService()
        service._is_connected = False
        
        result = await service.takeoff()
        
        assert result["success"] is False
        assert "接続されていません" in result["message"]
        assert service._is_flying is False

    @pytest.mark.asyncio
    async def test_takeoff_failure(self):
        """離陸失敗テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.takeoff.return_value = False
        service.drone = mock_drone
        
        result = await service.takeoff()
        
        assert result["success"] is False
        assert "離陸に失敗しました" in result["message"]
        assert service._is_flying is False

    @pytest.mark.asyncio
    async def test_takeoff_exception(self):
        """離陸例外テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.takeoff.side_effect = Exception("Takeoff error")
        service.drone = mock_drone
        
        result = await service.takeoff()
        
        assert result["success"] is False
        assert "離陸エラー:" in result["message"]

    @pytest.mark.asyncio
    async def test_land_success(self):
        """着陸成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.land.return_value = True
        service.drone = mock_drone
        
        result = await service.land()
        
        assert result["success"] is True
        assert "着陸しました" in result["message"]
        assert service._is_flying is False

    @pytest.mark.asyncio
    async def test_land_not_connected(self):
        """未接続での着陸テスト"""
        service = DroneService()
        service._is_connected = False
        
        result = await service.land()
        
        assert result["success"] is False
        assert "接続されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_land_not_flying(self):
        """非飛行時の着陸テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = False
        
        result = await service.land()
        
        assert result["success"] is False
        assert "飛行していません" in result["message"]

    @pytest.mark.asyncio
    async def test_emergency_success(self):
        """緊急停止成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.emergency.return_value = True
        service.drone = mock_drone
        
        result = await service.emergency()
        
        assert result["success"] is True
        assert "緊急停止しました" in result["message"]
        assert service._is_flying is False

    @pytest.mark.asyncio
    async def test_emergency_not_connected(self):
        """未接続での緊急停止テスト"""
        service = DroneService()
        service._is_connected = False
        
        result = await service.emergency()
        
        assert result["success"] is False
        assert "接続されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """ホバリング成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.stop.return_value = True
        service.drone = mock_drone
        
        result = await service.stop()
        
        assert result["success"] is True
        assert "ホバリング中です" in result["message"]


class TestDroneServiceMovementMethods:
    """DroneService移動メソッドテスト"""

    @pytest.mark.asyncio
    async def test_move_success(self):
        """移動成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.move.return_value = True
        service.drone = mock_drone
        
        result = await service.move("forward", 100)
        
        assert result["success"] is True
        assert "forward方向に100cm移動しました" in result["message"]
        mock_drone.move.assert_called_once_with("forward", 100)

    @pytest.mark.asyncio
    async def test_move_not_connected(self):
        """未接続での移動テスト"""
        service = DroneService()
        service._is_connected = False
        
        result = await service.move("forward", 100)
        
        assert result["success"] is False
        assert "接続されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_move_not_flying(self):
        """非飛行時の移動テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = False
        
        result = await service.move("forward", 100)
        
        assert result["success"] is False
        assert "飛行していません" in result["message"]

    @pytest.mark.parametrize("direction,distance", [
        ("forward", 20),   # 最小値
        ("back", 500),     # 最大値
        ("up", 260),       # 中央値
        ("down", 50),      # 通常値
        ("left", 150),     # 通常値
        ("right", 300),    # 通常値
    ])
    @pytest.mark.asyncio
    async def test_move_boundary_values(self, direction, distance):
        """移動境界値テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.move.return_value = True
        service.drone = mock_drone
        
        result = await service.move(direction, distance)
        
        assert result["success"] is True
        assert f"{direction}方向に{distance}cm移動しました" in result["message"]

    @pytest.mark.asyncio
    async def test_rotate_success(self):
        """回転成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.rotate.return_value = True
        service.drone = mock_drone
        
        result = await service.rotate("clockwise", 90)
        
        assert result["success"] is True
        assert "clockwise方向に90度回転しました" in result["message"]
        mock_drone.rotate.assert_called_once_with("clockwise", 90)

    @pytest.mark.parametrize("direction,angle", [
        ("clockwise", 1),       # 最小値
        ("clockwise", 360),     # 最大値
        ("counter_clockwise", 180),  # 中央値
        ("clockwise", 90),      # 通常値
        ("counter_clockwise", 45),   # 通常値
    ])
    @pytest.mark.asyncio
    async def test_rotate_boundary_values(self, direction, angle):
        """回転境界値テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.rotate.return_value = True
        service.drone = mock_drone
        
        result = await service.rotate(direction, angle)
        
        assert result["success"] is True
        assert f"{direction}方向に{angle}度回転しました" in result["message"]

    @pytest.mark.asyncio
    async def test_flip_success(self):
        """宙返り成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.flip.return_value = True
        service.drone = mock_drone
        
        result = await service.flip("forward")
        
        assert result["success"] is True
        assert "forward方向に宙返りしました" in result["message"]

    @pytest.mark.parametrize("direction", ["left", "right", "forward", "back"])
    @pytest.mark.asyncio
    async def test_flip_all_directions(self, direction):
        """全方向宙返りテスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.flip.return_value = True
        service.drone = mock_drone
        
        result = await service.flip(direction)
        
        assert result["success"] is True
        assert f"{direction}方向に宙返りしました" in result["message"]


class TestDroneServiceAdvancedMovementMethods:
    """DroneService高度移動メソッドテスト"""

    @pytest.mark.asyncio
    async def test_go_xyz_success(self):
        """座標移動成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.go_xyz_speed.return_value = True
        service.drone = mock_drone
        
        result = await service.go_xyz(100, -50, 200, 50)
        
        assert result["success"] is True
        assert "座標(100, -50, 200)に移動しました" in result["message"]
        mock_drone.go_xyz_speed.assert_called_once_with(100, -50, 200, 50)

    @pytest.mark.parametrize("x,y,z,speed", [
        (-500, -500, -500, 10),  # 最小値
        (500, 500, 500, 100),    # 最大値
        (0, 0, 0, 55),           # 中央値
        (100, -200, 150, 30),    # 通常値
    ])
    @pytest.mark.asyncio
    async def test_go_xyz_boundary_values(self, x, y, z, speed):
        """座標移動境界値テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.go_xyz_speed.return_value = True
        service.drone = mock_drone
        
        result = await service.go_xyz(x, y, z, speed)
        
        assert result["success"] is True
        assert f"座標({x}, {y}, {z})に移動しました" in result["message"]

    @pytest.mark.asyncio
    async def test_curve_xyz_success(self):
        """曲線飛行成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.curve_xyz_speed.return_value = True
        service.drone = mock_drone
        
        result = await service.curve_xyz(50, 0, 100, 150, 50, 200, 30)
        
        assert result["success"] is True
        assert "曲線飛行が完了しました" in result["message"]
        mock_drone.curve_xyz_speed.assert_called_once_with(50, 0, 100, 150, 50, 200, 30)

    @pytest.mark.asyncio
    async def test_rc_control_success(self):
        """リアルタイム制御成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.send_rc_control.return_value = True
        service.drone = mock_drone
        
        result = await service.rc_control(50, -30, 20, 10)
        
        assert result["success"] is True
        assert "リアルタイム制御コマンドを送信しました" in result["message"]
        mock_drone.send_rc_control.assert_called_once_with(50, -30, 20, 10)

    @pytest.mark.parametrize("lr,fb,ud,yaw", [
        (-100, -100, -100, -100),  # 最小値
        (100, 100, 100, 100),      # 最大値
        (0, 0, 0, 0),              # 中央値
        (50, -30, 20, 10),         # 通常値
    ])
    @pytest.mark.asyncio
    async def test_rc_control_boundary_values(self, lr, fb, ud, yaw):
        """リアルタイム制御境界値テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_flying = True
        
        mock_drone = MagicMock()
        mock_drone.send_rc_control.return_value = True
        service.drone = mock_drone
        
        result = await service.rc_control(lr, fb, ud, yaw)
        
        assert result["success"] is True
        mock_drone.send_rc_control.assert_called_once_with(lr, fb, ud, yaw)


class TestDroneServiceSensorMethods:
    """DroneServiceセンサーメソッドテスト"""

    @pytest.mark.asyncio
    async def test_get_status_connected(self):
        """接続時状態取得テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        # モックデータ設定
        mock_drone.get_battery.return_value = 85
        mock_drone.get_height.return_value = 150
        mock_drone.get_temperature.return_value = 25
        mock_drone.get_flight_time.return_value = 120
        mock_drone.get_speed.return_value = 50.5
        mock_drone.get_barometer.return_value = 1013.25
        mock_drone.get_distance_tof.return_value = 500
        mock_drone.get_acceleration_x.return_value = 0.1
        mock_drone.get_acceleration_y.return_value = 0.2
        mock_drone.get_acceleration_z.return_value = 0.98
        mock_drone.get_speed_x.return_value = 10
        mock_drone.get_speed_y.return_value = -5
        mock_drone.get_speed_z.return_value = 2
        mock_drone.get_pitch.return_value = 5
        mock_drone.get_roll.return_value = -2
        mock_drone.get_yaw.return_value = 90
        service.drone = mock_drone
        
        result = await service.get_status()
        
        assert result["connected"] is True
        assert result["battery"] == 85
        assert result["height"] == 150
        assert result["temperature"] == 25
        assert result["flight_time"] == 120
        assert result["speed"] == 50.5
        assert result["barometer"] == 1013.25
        assert result["distance_tof"] == 500
        assert result["acceleration"]["x"] == 0.1
        assert result["acceleration"]["y"] == 0.2
        assert result["acceleration"]["z"] == 0.98
        assert result["velocity"]["x"] == 10
        assert result["velocity"]["y"] == -5
        assert result["velocity"]["z"] == 2
        assert result["attitude"]["pitch"] == 5
        assert result["attitude"]["roll"] == -2
        assert result["attitude"]["yaw"] == 90

    @pytest.mark.asyncio
    async def test_get_status_not_connected(self):
        """未接続時状態取得テスト"""
        service = DroneService()
        service._is_connected = False
        
        result = await service.get_status()
        
        assert result["connected"] is False
        assert len(result) == 1  # connectedキーのみ

    @pytest.mark.asyncio
    async def test_get_status_exception(self):
        """状態取得例外テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.get_battery.side_effect = Exception("Sensor error")
        service.drone = mock_drone
        
        result = await service.get_status()
        
        assert "error" in result
        assert "状態取得エラー:" in result["error"]

    @pytest.mark.asyncio
    async def test_get_battery_success(self):
        """バッテリー取得成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.get_battery.return_value = 75
        service.drone = mock_drone
        
        result = await service.get_battery()
        
        assert result == 75

    @pytest.mark.asyncio
    async def test_get_battery_not_connected(self):
        """バッテリー取得未接続テスト"""
        service = DroneService()
        service._is_connected = False
        
        with pytest.raises(Exception, match="接続されていません"):
            await service.get_battery()

    @pytest.mark.parametrize("sensor_method,expected_value", [
        ("get_height", 200),
        ("get_temperature", 30),
        ("get_flight_time", 300),
        ("get_barometer", 1015.5),
        ("get_distance_tof", 750),
    ])
    @pytest.mark.asyncio
    async def test_individual_sensor_methods(self, sensor_method, expected_value):
        """個別センサーメソッドテスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        getattr(mock_drone, sensor_method).return_value = expected_value
        service.drone = mock_drone
        
        service_method = getattr(service, sensor_method)
        result = await service_method()
        
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_get_acceleration_success(self):
        """加速度取得成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.get_acceleration_x.return_value = 0.05
        mock_drone.get_acceleration_y.return_value = -0.1
        mock_drone.get_acceleration_z.return_value = 0.98
        service.drone = mock_drone
        
        result = await service.get_acceleration()
        
        assert isinstance(result, AccelerationData)
        assert result.x == 0.05
        assert result.y == -0.1
        assert result.z == 0.98

    @pytest.mark.asyncio
    async def test_get_velocity_success(self):
        """速度取得成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.get_speed_x.return_value = 15
        mock_drone.get_speed_y.return_value = -8
        mock_drone.get_speed_z.return_value = 3
        service.drone = mock_drone
        
        result = await service.get_velocity()
        
        assert isinstance(result, VelocityData)
        assert result.x == 15
        assert result.y == -8
        assert result.z == 3

    @pytest.mark.asyncio
    async def test_get_attitude_success(self):
        """姿勢角取得成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.get_pitch.return_value = 10
        mock_drone.get_roll.return_value = -5
        mock_drone.get_yaw.return_value = 45
        service.drone = mock_drone
        
        result = await service.get_attitude()
        
        assert isinstance(result, AttitudeData)
        assert result.pitch == 10
        assert result.roll == -5
        assert result.yaw == 45


class TestDroneServiceCameraMethods:
    """DroneServiceカメラメソッドテスト"""

    @pytest.mark.asyncio
    async def test_start_stream_success(self):
        """ストリーミング開始成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = False
        
        mock_drone = MagicMock()
        mock_drone.streamon.return_value = True
        service.drone = mock_drone
        
        result = await service.start_stream()
        
        assert result["success"] is True
        assert "ストリーミングを開始しました" in result["message"]
        assert service._is_streaming is True

    @pytest.mark.asyncio
    async def test_start_stream_already_streaming(self):
        """既にストリーミング中でのストリーミング開始テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = True
        
        result = await service.start_stream()
        
        assert result["success"] is False
        assert "既に開始されています" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_stream_success(self):
        """ストリーミング停止成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = True
        
        mock_drone = MagicMock()
        mock_drone.streamoff.return_value = True
        service.drone = mock_drone
        
        result = await service.stop_stream()
        
        assert result["success"] is True
        assert "ストリーミングを停止しました" in result["message"]
        assert service._is_streaming is False

    @pytest.mark.asyncio
    async def test_stop_stream_not_streaming(self):
        """ストリーミング未開始での停止テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = False
        
        result = await service.stop_stream()
        
        assert result["success"] is False
        assert "開始されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_get_stream_not_streaming(self):
        """ストリーミング未開始でのストリーム取得テスト"""
        service = DroneService()
        service._is_streaming = False
        
        result = await service.get_stream()
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_stream_success(self):
        """ストリーム取得成功テスト"""
        service = DroneService()
        service._is_streaming = True
        
        stream_generator = await service.get_stream()
        
        assert stream_generator is not None
        # ジェネレーターであることを確認
        assert hasattr(stream_generator, '__aiter__')

    @pytest.mark.asyncio
    async def test_take_photo_success(self):
        """写真撮影成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.take_picture.return_value = True
        service.drone = mock_drone
        
        result = await service.take_photo()
        
        assert result["success"] is True
        assert "写真を撮影しました" in result["message"]

    @pytest.mark.asyncio
    async def test_start_video_recording_success(self):
        """動画録画開始成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.start_video.return_value = True
        service.drone = mock_drone
        
        result = await service.start_video_recording()
        
        assert result["success"] is True
        assert "動画録画を開始しました" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_video_recording_success(self):
        """動画録画停止成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.stop_video.return_value = True
        service.drone = mock_drone
        
        result = await service.stop_video_recording()
        
        assert result["success"] is True
        assert "動画録画を停止しました" in result["message"]

    @pytest.mark.asyncio
    async def test_update_camera_settings_success(self):
        """カメラ設定変更成功テスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.set_video_resolution.return_value = True
        mock_drone.set_video_fps.return_value = True
        mock_drone.set_video_bitrate.return_value = True
        service.drone = mock_drone
        
        result = await service.update_camera_settings(
            resolution="high", fps="middle", bitrate=3
        )
        
        assert result["success"] is True
        assert "カメラ設定を変更しました" in result["message"]


class TestDroneServiceTrackingMethods:
    """DroneService追跡メソッドテスト"""

    @pytest.mark.asyncio
    async def test_start_tracking_success(self):
        """追跡開始成功テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = True
        
        result = await service.start_tracking("person", "center")
        
        assert result["success"] is True
        assert "'person'の追跡を開始しました" in result["message"]
        assert "centerモード" in result["message"]
        assert service._is_tracking is True
        assert service._target_object == "person"
        assert service._tracking_mode == "center"

    @pytest.mark.asyncio
    async def test_start_tracking_not_streaming(self):
        """ストリーミング未開始での追跡開始テスト"""
        service = DroneService()
        service._is_connected = True
        service._is_streaming = False
        
        result = await service.start_tracking("person")
        
        assert result["success"] is False
        assert "ストリーミングが開始されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_tracking_success(self):
        """追跡停止成功テスト"""
        service = DroneService()
        service._is_tracking = True
        
        result = await service.stop_tracking()
        
        assert result["success"] is True
        assert "物体追跡を停止しました" in result["message"]
        assert service._is_tracking is False
        assert service._target_object == ""

    @pytest.mark.asyncio
    async def test_stop_tracking_not_tracking(self):
        """追跡未開始での停止テスト"""
        service = DroneService()
        service._is_tracking = False
        
        result = await service.stop_tracking()
        
        assert result["success"] is False
        assert "追跡が開始されていません" in result["message"]

    @pytest.mark.asyncio
    async def test_get_tracking_status_tracking(self):
        """追跡中状態取得テスト"""
        service = DroneService()
        service._is_tracking = True
        service._target_object = "car"
        
        result = await service.get_tracking_status()
        
        assert result["is_tracking"] is True
        assert result["target_object"] == "car"
        assert result["target_detected"] is True
        assert result["target_position"] is not None
        assert result["target_position"]["x"] == 320
        assert result["target_position"]["y"] == 240

    @pytest.mark.asyncio
    async def test_get_tracking_status_not_tracking(self):
        """追跡未実行状態取得テスト"""
        service = DroneService()
        service._is_tracking = False
        service._target_object = ""
        
        result = await service.get_tracking_status()
        
        assert result["is_tracking"] is False
        assert result["target_object"] == ""
        assert result["target_position"] is None


class TestDroneServiceModelMethods:
    """DroneServiceモデルメソッドテスト"""

    @pytest.mark.asyncio
    async def test_train_model_success(self):
        """モデル訓練成功テスト"""
        service = DroneService()
        
        mock_images = [MagicMock(), MagicMock()]
        
        result = await service.train_model("test_object", mock_images)
        
        assert result["success"] is True
        assert "task_id" in result
        # UUIDフォーマットであることを確認
        task_id = result["task_id"]
        uuid.UUID(task_id)  # 有効なUUIDでない場合は例外が発生

    @pytest.mark.asyncio
    async def test_list_models_success(self):
        """モデル一覧取得成功テスト"""
        service = DroneService()
        
        result = await service.list_models()
        
        assert "models" in result
        assert isinstance(result["models"], list)
        assert len(result["models"]) >= 1
        
        # 最初のモデル情報をチェック
        first_model = result["models"][0]
        assert isinstance(first_model, ModelInfo)
        assert hasattr(first_model, 'name')
        assert hasattr(first_model, 'created_at')
        assert hasattr(first_model, 'accuracy')


class TestDroneServiceStateManagement:
    """DroneService状態管理テスト"""

    def test_initial_state_consistency(self):
        """初期状態一貫性テスト"""
        service = DroneService()
        
        # 初期状態の確認
        assert service._is_connected is False
        assert service._is_streaming is False
        assert service._is_flying is False
        assert service._is_tracking is False
        assert service._mission_pad_enabled is False

    @pytest.mark.asyncio
    async def test_state_transition_connect_disconnect(self):
        """状態遷移：接続-切断テスト"""
        service = DroneService()
        
        mock_drone = MagicMock()
        mock_drone.connect.return_value = True
        mock_drone.disconnect.return_value = True
        
        with patch('services.drone_service.create_drone_instance', return_value=mock_drone):
            # 接続
            await service.connect()
            assert service._is_connected is True
            
            # 切断
            await service.disconnect()
            assert service._is_connected is False
            assert service._is_streaming is False
            assert service._is_flying is False
            assert service._is_tracking is False

    @pytest.mark.asyncio
    async def test_state_transition_flight_cycle(self):
        """状態遷移：飛行サイクルテスト"""
        service = DroneService()
        service._is_connected = True
        
        mock_drone = MagicMock()
        mock_drone.takeoff.return_value = True
        mock_drone.land.return_value = True
        mock_drone.emergency.return_value = True
        service.drone = mock_drone
        
        # 離陸
        await service.takeoff()
        assert service._is_flying is True
        
        # 着陸
        await service.land()
        assert service._is_flying is False
        
        # 再離陸
        await service.takeoff()
        assert service._is_flying is True
        
        # 緊急停止
        await service.emergency()
        assert service._is_flying is False

    @pytest.mark.asyncio
    async def test_state_boundary_conditions(self):
        """状態境界条件テスト"""
        service = DroneService()
        
        # 未接続状態での各操作確認
        takeoff_result = await service.takeoff()
        assert takeoff_result["success"] is False
        
        move_result = await service.move("forward", 100)
        assert move_result["success"] is False
        
        stream_result = await service.start_stream()
        assert stream_result["success"] is False