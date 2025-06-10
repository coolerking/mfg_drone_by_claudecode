"""
DroneService単体テスト
services/drone_service.py の個別メソッド単体テスト - Phase 1
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.drone_service import DroneService
from tests.stubs.drone_stub import TelloStub
from tests.fixtures.drone_factory import create_test_drone, DroneTestHelper


class TestDroneServiceInitialization:
    """DroneService初期化単体テスト"""
    
    def test_drone_service_init_default_values(self):
        """DroneService初期化デフォルト値テスト"""
        service = DroneService()
        
        # 初期状態確認
        assert service.drone is None
        assert service._is_connected is False
        assert service._is_streaming is False
        assert service._is_flying is False
        assert service._is_tracking is False
        assert service._target_object == ""
        assert service._tracking_mode == "center"
        assert service._mission_pad_enabled is False
    
    def test_drone_service_init_boundary_values(self):
        """DroneService初期化境界値テスト"""
        # 複数インスタンス作成テスト
        services = []
        for i in range(100):  # 境界値: 100個のインスタンス
            service = DroneService()
            services.append(service)
        
        # 各インスタンスが独立していることを確認
        for i, service in enumerate(services):
            assert service.drone is None
            assert service._is_connected is False
            
            # メモリアドレスが異なることを確認
            if i > 0:
                assert id(service) != id(services[i-1])


class TestConnectionMethods:
    """接続関連メソッド単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """正常接続単体テスト"""
        # モックドローン設定
        mock_drone = create_test_drone()
        DroneTestHelper.setup_disconnected_state(mock_drone)
        
        with patch('tests.fixtures.drone_factory.create_drone_instance', return_value=mock_drone):
            result = await self.service.connect()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "接続" in result["message"]
        assert self.service._is_connected is True
        assert self.service.drone is mock_drone
    
    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """接続失敗単体テスト"""
        # 接続失敗モックドローン
        mock_drone = create_test_drone()
        DroneTestHelper.setup_connection_error(mock_drone)
        
        with patch('tests.fixtures.drone_factory.create_drone_instance', return_value=mock_drone):
            result = await self.service.connect()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "接続" in result["message"] or "エラー" in result["message"]
        assert self.service._is_connected is False
    
    @pytest.mark.asyncio
    async def test_connect_exception_handling(self):
        """接続例外処理単体テスト"""
        # 例外発生モック
        with patch('tests.fixtures.drone_factory.create_drone_instance', side_effect=Exception("Connection exception")):
            result = await self.service.connect()
        
        # エラーハンドリング確認
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "エラー" in result["message"]
        assert "Connection exception" in result["message"]
        assert self.service._is_connected is False
    
    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """正常切断単体テスト"""
        # 接続済み状態設定
        mock_drone = create_test_drone()
        DroneTestHelper.setup_connected_state(mock_drone)
        self.service.drone = mock_drone
        self.service._is_connected = True
        self.service._is_streaming = True
        self.service._is_flying = True
        self.service._is_tracking = True
        
        result = await self.service.disconnect()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "切断" in result["message"]
        assert self.service._is_connected is False
        assert self.service._is_streaming is False
        assert self.service._is_flying is False
        assert self.service._is_tracking is False
    
    @pytest.mark.asyncio
    async def test_disconnect_not_initialized(self):
        """ドローン未初期化時切断テスト"""
        # ドローンがNoneの状態
        result = await self.service.disconnect()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "初期化されていません" in result["message"]
    
    @pytest.mark.asyncio
    async def test_disconnect_boundary_values(self):
        """切断境界値テスト"""
        # 複数回連続切断テスト
        mock_drone = create_test_drone()
        self.service.drone = mock_drone
        
        # 境界値: 10回連続切断
        for i in range(10):
            result = await self.service.disconnect()
            assert isinstance(result, dict)
            assert self.service._is_connected is False


class TestFlightControlMethods:
    """飛行制御メソッド単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
        self.mock_drone = create_test_drone()
        self.service.drone = self.mock_drone
    
    @pytest.mark.asyncio
    async def test_takeoff_success(self):
        """正常離陸単体テスト"""
        # 接続済み状態設定
        self.service._is_connected = True
        DroneTestHelper.setup_connected_state(self.mock_drone)
        
        result = await self.service.takeoff()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "離陸" in result["message"]
        assert self.service._is_flying is True
    
    @pytest.mark.asyncio
    async def test_takeoff_not_connected(self):
        """未接続時離陸テスト"""
        # 未接続状態
        self.service._is_connected = False
        
        result = await self.service.takeoff()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "接続されていません" in result["message"]
        assert self.service._is_flying is False
    
    @pytest.mark.asyncio
    async def test_land_success(self):
        """正常着陸単体テスト"""
        # 飛行中状態設定
        self.service._is_connected = True
        self.service._is_flying = True
        DroneTestHelper.setup_flying_state(self.mock_drone)
        
        result = await self.service.land()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "着陸" in result["message"]
        assert self.service._is_flying is False
    
    @pytest.mark.asyncio
    async def test_land_not_flying(self):
        """非飛行時着陸テスト"""
        # 接続済みだが非飛行状態
        self.service._is_connected = True
        self.service._is_flying = False
        
        result = await self.service.land()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "飛行していません" in result["message"]
    
    @pytest.mark.asyncio
    async def test_emergency_success(self):
        """正常緊急停止単体テスト"""
        # 飛行中状態設定
        self.service._is_connected = True
        self.service._is_flying = True
        DroneTestHelper.setup_flying_state(self.mock_drone)
        
        result = await self.service.emergency()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "緊急停止" in result["message"]
        assert self.service._is_flying is False
    
    @pytest.mark.asyncio
    async def test_stop_hovering_success(self):
        """正常ホバリング単体テスト"""
        # 飛行中状態設定
        self.service._is_connected = True
        self.service._is_flying = True
        DroneTestHelper.setup_flying_state(self.mock_drone)
        
        result = await self.service.stop()
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "ホバリング" in result["message"]
        # ホバリングは飛行状態を維持
        assert self.service._is_flying is True


class TestMovementMethods:
    """移動制御メソッド単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
        self.mock_drone = create_test_drone()
        self.service.drone = self.mock_drone
        # 飛行中状態設定
        self.service._is_connected = True
        self.service._is_flying = True
        DroneTestHelper.setup_flying_state(self.mock_drone)
    
    @pytest.mark.asyncio
    async def test_move_success(self):
        """正常移動単体テスト"""
        result = await self.service.move("forward", 100)
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "forward" in result["message"]
        assert "100cm" in result["message"]
    
    @pytest.mark.asyncio
    async def test_move_boundary_values(self):
        """移動境界値単体テスト"""
        # 境界値テスト: 最小値、中央値、最大値
        boundary_values = [
            ("forward", 20, True),    # 最小値
            ("back", 260, True),      # 中央値
            ("left", 500, True),      # 最大値
        ]
        
        for direction, distance, expected_success in boundary_values:
            result = await self.service.move(direction, distance)
            
            assert isinstance(result, dict)
            assert result["success"] is expected_success
            if expected_success:
                assert direction in result["message"]
                assert f"{distance}cm" in result["message"]
    
    @pytest.mark.asyncio
    async def test_move_invalid_state(self):
        """移動時無効状態単体テスト"""
        # 未接続状態
        self.service._is_connected = False
        result = await self.service.move("forward", 100)
        assert result["success"] is False
        assert "接続されていません" in result["message"]
        
        # 接続済みだが非飛行状態
        self.service._is_connected = True
        self.service._is_flying = False
        result = await self.service.move("forward", 100)
        assert result["success"] is False
        assert "飛行していません" in result["message"]
    
    @pytest.mark.asyncio
    async def test_rotate_success(self):
        """正常回転単体テスト"""
        result = await self.service.rotate("clockwise", 90)
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "clockwise" in result["message"]
        assert "90度" in result["message"]
    
    @pytest.mark.asyncio
    async def test_rotate_boundary_values(self):
        """回転境界値単体テスト"""
        # 境界値テスト: 最小値、中央値、最大値
        boundary_values = [
            ("clockwise", 1, True),       # 最小値
            ("counter_clockwise", 180, True),  # 中央値
            ("clockwise", 360, True),     # 最大値
        ]
        
        for direction, angle, expected_success in boundary_values:
            result = await self.service.rotate(direction, angle)
            
            assert isinstance(result, dict)
            assert result["success"] is expected_success
            if expected_success:
                assert direction in result["message"]
                assert f"{angle}度" in result["message"]
    
    @pytest.mark.asyncio
    async def test_flip_success(self):
        """正常宙返り単体テスト"""
        result = await self.service.flip("forward")
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "forward" in result["message"]
        assert "宙返り" in result["message"]


class TestAdvancedMovementMethods:
    """高度移動メソッド単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
        self.mock_drone = create_test_drone()
        self.service.drone = self.mock_drone
        # 飛行中状態設定
        self.service._is_connected = True
        self.service._is_flying = True
        DroneTestHelper.setup_flying_state(self.mock_drone)
    
    @pytest.mark.asyncio
    async def test_go_xyz_success(self):
        """正常座標移動単体テスト"""
        result = await self.service.go_xyz(100, -50, 200, 50)
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "座標(100, -50, 200)" in result["message"]
    
    @pytest.mark.asyncio
    async def test_go_xyz_boundary_values(self):
        """座標移動境界値単体テスト"""
        # 境界値テスト
        boundary_coordinates = [
            (-500, -500, -500, 10, True),  # 最小値
            (0, 0, 0, 55, True),           # 中央値
            (500, 500, 500, 100, True),    # 最大値
        ]
        
        for x, y, z, speed, expected_success in boundary_coordinates:
            result = await self.service.go_xyz(x, y, z, speed)
            
            assert isinstance(result, dict)
            assert result["success"] is expected_success
            if expected_success:
                assert f"座標({x}, {y}, {z})" in result["message"]
    
    @pytest.mark.asyncio
    async def test_curve_xyz_success(self):
        """正常曲線飛行単体テスト"""
        result = await self.service.curve_xyz(100, 100, 50, 200, 200, 100, 30)
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "曲線飛行" in result["message"]
    
    @pytest.mark.asyncio
    async def test_rc_control_success(self):
        """正常リアルタイム制御単体テスト"""
        result = await self.service.rc_control(20, -30, 10, 15)
        
        # 結果確認
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "リアルタイム制御" in result["message"]
    
    @pytest.mark.asyncio
    async def test_rc_control_boundary_values(self):
        """リアルタイム制御境界値単体テスト"""
        # 境界値テスト
        boundary_values = [
            (-100, -100, -100, -100, True),  # 最小値
            (0, 0, 0, 0, True),              # 中央値
            (100, 100, 100, 100, True),      # 最大値
        ]
        
        for lr, fb, ud, yaw, expected_success in boundary_values:
            result = await self.service.rc_control(lr, fb, ud, yaw)
            
            assert isinstance(result, dict)
            assert result["success"] is expected_success


class TestSensorMethods:
    """センサー関連メソッド単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
        self.mock_drone = create_test_drone()
        self.service.drone = self.mock_drone
        self.service._is_connected = True
        DroneTestHelper.setup_connected_state(self.mock_drone)
    
    @pytest.mark.asyncio
    async def test_get_status_connected(self):
        """接続時状態取得単体テスト"""
        result = await self.service.get_status()
        
        # 結果確認
        assert isinstance(result, dict)
        assert "connected" in result
        assert result["connected"] is True
        assert "battery" in result
        assert "height" in result
        assert "temperature" in result
        assert "acceleration" in result
        assert "velocity" in result
        assert "attitude" in result
        
        # ネストされた構造確認
        assert isinstance(result["acceleration"], dict)
        assert "x" in result["acceleration"]
        assert "y" in result["acceleration"]
        assert "z" in result["acceleration"]
    
    @pytest.mark.asyncio
    async def test_get_status_not_connected(self):
        """未接続時状態取得単体テスト"""
        self.service._is_connected = False
        
        result = await self.service.get_status()
        
        # 結果確認
        assert isinstance(result, dict)
        assert "connected" in result
        assert result["connected"] is False
    
    @pytest.mark.asyncio
    async def test_individual_sensor_methods(self):
        """個別センサーメソッド単体テスト"""
        # バッテリー
        battery = await self.service.get_battery()
        assert isinstance(battery, int)
        assert 0 <= battery <= 100
        
        # 高度
        height = await self.service.get_height()
        assert isinstance(height, int)
        assert height >= 0
        
        # 温度
        temperature = await self.service.get_temperature()
        assert isinstance(temperature, int)
        assert 0 <= temperature <= 90
        
        # 飛行時間
        flight_time = await self.service.get_flight_time()
        assert isinstance(flight_time, int)
        assert flight_time >= 0
        
        # 気圧
        barometer = await self.service.get_barometer()
        assert isinstance(barometer, (int, float))
        assert barometer >= 0
        
        # ToFセンサー距離
        distance_tof = await self.service.get_distance_tof()
        assert isinstance(distance_tof, int)
        assert distance_tof >= 0
    
    @pytest.mark.asyncio
    async def test_sensor_methods_not_connected(self):
        """未接続時センサーメソッドエラーテスト"""
        self.service._is_connected = False
        
        # 各センサーメソッドが例外を発生させることを確認
        sensor_methods = [
            self.service.get_battery,
            self.service.get_height,
            self.service.get_temperature,
            self.service.get_flight_time,
            self.service.get_barometer,
            self.service.get_distance_tof,
        ]
        
        for method in sensor_methods:
            with pytest.raises(Exception) as exc_info:
                await method()
            assert "接続されていません" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_structured_sensor_data(self):
        """構造化センサーデータ単体テスト"""
        # 加速度データ
        acceleration = await self.service.get_acceleration()
        assert hasattr(acceleration, 'x')
        assert hasattr(acceleration, 'y') 
        assert hasattr(acceleration, 'z')
        assert isinstance(acceleration.x, (int, float))
        assert isinstance(acceleration.y, (int, float))
        assert isinstance(acceleration.z, (int, float))
        
        # 速度データ
        velocity = await self.service.get_velocity()
        assert hasattr(velocity, 'x')
        assert hasattr(velocity, 'y')
        assert hasattr(velocity, 'z')
        assert isinstance(velocity.x, int)
        assert isinstance(velocity.y, int)
        assert isinstance(velocity.z, int)
        
        # 姿勢角データ
        attitude = await self.service.get_attitude()
        assert hasattr(attitude, 'pitch')
        assert hasattr(attitude, 'roll')
        assert hasattr(attitude, 'yaw')
        assert isinstance(attitude.pitch, int)
        assert isinstance(attitude.roll, int)
        assert isinstance(attitude.yaw, int)
        assert -180 <= attitude.pitch <= 180
        assert -180 <= attitude.roll <= 180
        assert -180 <= attitude.yaw <= 180


class TestExceptionHandling:
    """例外処理単体テスト"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ"""
        self.service = DroneService()
        self.mock_drone = create_test_drone()
        self.service.drone = self.mock_drone
        self.service._is_connected = True
        self.service._is_flying = True
    
    @pytest.mark.asyncio
    async def test_command_execution_exceptions(self):
        """コマンド実行例外テスト"""
        # エラー発生モックドローン設定
        DroneTestHelper.setup_command_error(self.mock_drone)
        
        # 各種コマンド実行とエラー処理確認
        methods_to_test = [
            ("takeoff", self.service.takeoff, []),
            ("land", self.service.land, []),
            ("move", self.service.move, ["forward", 100]),
            ("rotate", self.service.rotate, ["clockwise", 90]),
        ]
        
        for method_name, method, args in methods_to_test:
            result = await method(*args)
            
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "エラー" in result["message"]
    
    @pytest.mark.asyncio
    async def test_timeout_exceptions(self):
        """タイムアウト例外テスト"""
        # タイムアウトエラーモックドローン設定
        DroneTestHelper.setup_timeout_error(self.mock_drone)
        
        result = await self.service.connect()
        
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "エラー" in result["message"] or "タイムアウト" in result["message"]
    
    @pytest.mark.asyncio
    async def test_sensor_exception_handling(self):
        """センサー例外処理テスト"""
        # センサーエラーシミュレーション
        with patch.object(self.mock_drone, 'get_battery', side_effect=Exception("Sensor error")):
            result = await self.service.get_status()
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "Sensor error" in result["error"]