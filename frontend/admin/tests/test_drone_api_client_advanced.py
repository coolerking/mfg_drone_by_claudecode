"""
DroneAPIClient クラスの高度機能単体テスト
ミッションパッド・物体追跡・モデル管理機能のテスト
"""

import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fixtures.unit_test_fixtures import *


class TestDroneAPIClientMissionPad:
    """ミッションパッド機能テスト"""
    
    def test_enable_mission_pad_success(self, drone_api_client, backend_mock):
        """ミッションパッド有効化成功"""
        result = drone_api_client.enable_mission_pad()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'mission pad enabled' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/mission_pad/enable'
    
    def test_disable_mission_pad_success(self, drone_api_client, backend_mock):
        """ミッションパッド無効化成功"""
        result = drone_api_client.disable_mission_pad()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'mission pad disabled' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/mission_pad/disable'
    
    @pytest.mark.parametrize("direction", [0, 1, 2])
    def test_set_detection_direction_valid(self, drone_api_client, backend_mock, direction):
        """検出方向設定 - 有効値"""
        result = drone_api_client.set_detection_direction(direction)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'PUT'
        assert history[0]['endpoint'] == '/mission_pad/detection_direction'
        assert history[0]['kwargs']['json']['direction'] == direction
    
    @pytest.mark.parametrize("x,y,z,speed,pad_id", [
        (0, 0, 100, 50, 1),
        (100, -100, 200, 30, 2),
        (-200, 200, 150, 70, 8)
    ])
    def test_go_to_mission_pad_success(self, drone_api_client, backend_mock, x, y, z, speed, pad_id):
        """ミッションパッドへの移動成功"""
        result = drone_api_client.go_to_mission_pad(x, y, z, speed, pad_id)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/mission_pad/go_xyz'
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == x
        assert request_data['y'] == y
        assert request_data['z'] == z
        assert request_data['speed'] == speed
        assert request_data['mission_pad_id'] == pad_id
    
    def test_get_mission_pad_status_success(self, drone_api_client, backend_mock):
        """ミッションパッドステータス取得成功"""
        result = drone_api_client.get_mission_pad_status()
        
        assert result is not None
        assert 'enabled' in result
        assert 'detection_direction' in result
        assert isinstance(result['enabled'], bool)
        assert isinstance(result['detection_direction'], int)
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/mission_pad/status'


class TestDroneAPIClientTracking:
    """物体追跡機能テスト"""
    
    @pytest.mark.parametrize("target_object,tracking_mode", [
        ('person', 'center'),
        ('car', 'follow'),
        ('bicycle', 'surround'),
        ('dog', 'center'),
        ('cat', 'follow')
    ])
    def test_start_tracking_success(self, drone_api_client, backend_mock, target_object, tracking_mode):
        """物体追跡開始成功"""
        result = drone_api_client.start_tracking(target_object, tracking_mode)
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'tracking started' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/tracking/start'
        request_data = history[0]['kwargs']['json']
        assert request_data['target_object'] == target_object
        assert request_data['tracking_mode'] == tracking_mode
    
    def test_start_tracking_default_mode(self, drone_api_client, backend_mock):
        """物体追跡開始 - デフォルトモード"""
        target_object = 'person'
        result = drone_api_client.start_tracking(target_object)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['target_object'] == target_object
        assert request_data['tracking_mode'] == 'center'  # デフォルト値
    
    def test_stop_tracking_success(self, drone_api_client, backend_mock):
        """物体追跡停止成功"""
        result = drone_api_client.stop_tracking()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'tracking stopped' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/tracking/stop'
    
    def test_get_tracking_status_success(self, drone_api_client, backend_mock):
        """追跡ステータス取得成功"""
        result = drone_api_client.get_tracking_status()
        
        assert result is not None
        assert 'tracking' in result
        assert 'target' in result
        assert isinstance(result['tracking'], bool)
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/tracking/status'


class TestDroneAPIClientModelManagement:
    """モデル管理機能テスト"""
    
    def test_get_model_list_success(self, drone_api_client, backend_mock):
        """モデル一覧取得成功"""
        result = drone_api_client.get_model_list()
        
        assert result is not None
        assert 'models' in result
        assert isinstance(result['models'], list)
        assert len(result['models']) > 0
        assert 'person' in result['models']
        assert 'car' in result['models']
        assert 'bicycle' in result['models']
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/model/list'
    
    @pytest.mark.parametrize("model_name", ['person', 'car', 'bicycle', 'custom_model'])
    def test_delete_model_success(self, drone_api_client, backend_mock, model_name):
        """モデル削除成功"""
        result = drone_api_client.delete_model(model_name)
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'model deleted' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'DELETE'
        assert history[0]['endpoint'] == f'/model/{model_name}'


class TestDroneAPIClientEdgeCases:
    """境界値・エラーケーステスト"""
    
    @pytest.mark.parametrize("distance", [-1, 0, 3001])
    def test_movement_invalid_distances(self, drone_api_client, backend_mock, distance):
        """移動 - 無効距離値（API レベルでは型チェックのみ）"""
        # DroneAPIClient は引数チェックを行わず、バックエンドに値を渡すだけ
        result = drone_api_client.move_forward(distance)
        
        # モックは成功レスポンスを返すので、結果は成功になる
        # 実際のバリデーションはバックエンド側で行われる
        assert result is not None
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("angle", [-1, 3601])
    def test_rotation_invalid_angles(self, drone_api_client, backend_mock, angle):
        """回転 - 無効角度値"""
        result = drone_api_client.rotate('cw', angle)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['angle'] == angle
    
    @pytest.mark.parametrize("speed", [0.0, 15.1, -1.0])
    def test_speed_setting_invalid_values(self, drone_api_client, backend_mock, speed):
        """速度設定 - 無効値"""
        result = drone_api_client.set_speed(speed)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['speed'] == speed
    
    @pytest.mark.parametrize("ssid,password", [
        ('', 'password123'),      # 空のSSID
        ('TestWiFi', ''),         # 空のパスワード
        ('', ''),                 # 両方空
    ])
    def test_wifi_setting_invalid_values(self, drone_api_client, backend_mock, ssid, password):
        """WiFi設定 - 無効値"""
        result = drone_api_client.set_wifi(ssid, password)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['ssid'] == ssid
        assert request_data['password'] == password
    
    @pytest.mark.parametrize("command,timeout", [
        ('', 5),        # 空コマンド
        ('battery?', 0), # 無効タイムアウト
        ('battery?', -1), # 負のタイムアウト
    ])
    def test_command_invalid_values(self, drone_api_client, backend_mock, command, timeout):
        """カスタムコマンド - 無効値"""
        result = drone_api_client.send_command(command, timeout)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['command'] == command
        assert request_data['timeout'] == timeout
    
    @pytest.mark.parametrize("target", ['', None])
    def test_tracking_invalid_target(self, drone_api_client, backend_mock, target):
        """物体追跡 - 無効ターゲット"""
        result = drone_api_client.start_tracking(target)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['target_object'] == target
    
    @pytest.mark.parametrize("detection_direction", [-1, 3, 10])
    def test_mission_pad_invalid_detection_direction(self, drone_api_client, backend_mock, detection_direction):
        """ミッションパッド - 無効検出方向"""
        result = drone_api_client.set_detection_direction(detection_direction)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['direction'] == detection_direction
    
    def test_mission_pad_invalid_coordinates(self, drone_api_client, backend_mock):
        """ミッションパッド - 無効座標"""
        x, y, z, speed, pad_id = 3000, 3000, -1, 0, 0  # 全て範囲外
        
        result = drone_api_client.go_to_mission_pad(x, y, z, speed, pad_id)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == x
        assert request_data['y'] == y
        assert request_data['z'] == z
        assert request_data['speed'] == speed
        assert request_data['mission_pad_id'] == pad_id
    
    def test_rc_control_invalid_velocities(self, drone_api_client, backend_mock):
        """リアルタイム制御 - 無効速度値"""
        left_right, forward_backward, up_down, yaw = 101, -101, 101, -101  # 全て範囲外
        
        result = drone_api_client.rc_control(left_right, forward_backward, up_down, yaw)
        
        assert result is not None  # モックは成功レスポンスを返す
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['left_right_velocity'] == left_right
        assert request_data['forward_backward_velocity'] == forward_backward
        assert request_data['up_down_velocity'] == up_down
        assert request_data['yaw_velocity'] == yaw


class TestDroneAPIClientExceptionHandling:
    """例外処理テスト"""
    
    def test_timeout_exception_handling(self, timeout_backend_mock, mock_env_vars):
        """タイムアウト例外処理"""
        with patch('requests.Session') as mock_session_class:
            from mocks.backend_mock import MockSession
            mock_session_class.return_value = MockSession(timeout_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            
            # 全てのメソッドがタイムアウト時に None を返すことを確認
            assert client.health_check() is None
            assert client.connect_drone() is None
            assert client.takeoff() is None
            assert client.move_forward(50) is None
            assert client.get_battery() is None
    
    def test_connection_error_handling(self, connection_error_backend_mock, mock_env_vars):
        """接続エラー例外処理"""
        with patch('requests.Session') as mock_session_class:
            from mocks.backend_mock import MockSession
            mock_session_class.return_value = MockSession(connection_error_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            
            # 全てのメソッドが接続エラー時に None を返すことを確認
            assert client.health_check() is None
            assert client.disconnect_drone() is None
            assert client.land() is None
            assert client.take_photo() is None
            assert client.get_altitude() is None
    
    def test_http_error_response_handling(self, error_backend_mock, mock_env_vars):
        """HTTPエラーレスポンス処理"""
        with patch('requests.Session') as mock_session_class:
            from mocks.backend_mock import MockSession
            mock_session_class.return_value = MockSession(error_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            
            # 全てのメソッドがHTTPエラー時に None を返すことを確認
            assert client.health_check() is None
            assert client.emergency_stop() is None
            assert client.rotate('cw', 90) is None
            assert client.start_video_stream() is None
            assert client.get_temperature() is None