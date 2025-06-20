"""
DroneAPIClient クラスの単体テスト
バックエンド API との通信を担当するクライアントクラスの機能テスト
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fixtures.unit_test_fixtures import *
from mocks.backend_mock import BackendAPIMock, MockSession


class TestDroneAPIClientInit:
    """DroneAPIClient 初期化テスト"""
    
    def test_init_with_default_url(self, mock_env_vars):
        """デフォルトURL での初期化"""
        with patch('requests.Session'):
            from main import DroneAPIClient
            client = DroneAPIClient()
            assert client.base_url == 'http://localhost:8000'
            assert hasattr(client, 'session')
            assert client.session.timeout == 10
    
    def test_init_with_custom_url(self, mock_env_vars):
        """カスタムURL での初期化"""
        with patch('requests.Session'):
            from main import DroneAPIClient
            custom_url = 'http://192.168.1.100:8000'
            client = DroneAPIClient(custom_url)
            assert client.base_url == custom_url
    
    def test_init_with_trailing_slash(self, mock_env_vars):
        """末尾スラッシュ付きURL での初期化"""
        with patch('requests.Session'):
            from main import DroneAPIClient
            url_with_slash = 'http://localhost:8000/'
            client = DroneAPIClient(url_with_slash)
            assert client.base_url == 'http://localhost:8000'  # 末尾スラッシュが除去される


class TestDroneAPIClientMakeRequest:
    """_make_request メソッドの単体テスト"""
    
    def test_make_request_get_success(self, drone_api_client, backend_mock):
        """GET リクエスト成功"""
        result = drone_api_client._make_request('GET', '/health')
        
        assert result is not None
        assert result['status'] == 'healthy'
        
        # リクエスト履歴の確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/health'
    
    def test_make_request_post_success(self, drone_api_client, backend_mock):
        """POST リクエスト成功"""
        test_data = {'distance': 50}
        result = drone_api_client._make_request('POST', '/drone/move/forward', test_data)
        
        assert result is not None
        assert result['status'] == 'success'
        
        # リクエスト履歴の確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/forward'
        assert 'json' in history[0]['kwargs']
    
    def test_make_request_put_success(self, drone_api_client, backend_mock):
        """PUT リクエスト成功"""
        test_data = {'speed': 10.0}
        result = drone_api_client._make_request('PUT', '/drone/speed', test_data)
        
        assert result is not None
        assert result['status'] == 'success'
        
        # リクエスト履歴の確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'PUT'
        assert history[0]['endpoint'] == '/drone/speed'
    
    def test_make_request_delete_success(self, drone_api_client, backend_mock):
        """DELETE リクエスト成功"""
        result = drone_api_client._make_request('DELETE', '/model/person')
        
        assert result is not None
        assert result['status'] == 'success'
        
        # リクエスト履歴の確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'DELETE'
        assert history[0]['endpoint'] == '/model/person'
    
    def test_make_request_invalid_method(self, drone_api_client):
        """無効な HTTP メソッド"""
        result = drone_api_client._make_request('INVALID', '/health')
        assert result is None
    
    def test_make_request_http_error(self, error_backend_mock, mock_env_vars):
        """HTTP エラーレスポンス処理"""
        with patch('requests.Session') as mock_session_class:
            mock_session_class.return_value = MockSession(error_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            result = client._make_request('GET', '/health')
            
            assert result is None  # エラー時は None を返す
    
    def test_make_request_timeout_exception(self, timeout_backend_mock, mock_env_vars):
        """タイムアウト例外処理"""
        with patch('requests.Session') as mock_session_class:
            mock_session_class.return_value = MockSession(timeout_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            result = client._make_request('GET', '/health')
            
            assert result is None  # 例外時は None を返す
    
    def test_make_request_connection_error(self, connection_error_backend_mock, mock_env_vars):
        """接続エラー例外処理"""
        with patch('requests.Session') as mock_session_class:
            mock_session_class.return_value = MockSession(connection_error_backend_mock)
            
            from main import DroneAPIClient
            client = DroneAPIClient()
            result = client._make_request('GET', '/health')
            
            assert result is None  # 例外時は None を返す


class TestDroneAPIClientHealthCheck:
    """ヘルスチェック機能テスト"""
    
    def test_health_check_success(self, drone_api_client, backend_mock):
        """ヘルスチェック成功"""
        result = drone_api_client.health_check()
        
        assert result is not None
        assert result['status'] == 'healthy'
        assert 'message' in result
        
        # 正しいエンドポイントが呼ばれることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/health'


class TestDroneAPIClientConnection:
    """ドローン接続管理テスト"""
    
    def test_connect_drone_success(self, drone_api_client, backend_mock):
        """ドローン接続成功"""
        result = drone_api_client.connect_drone()
        
        assert result is not None
        assert result['status'] == 'connected'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/connect'
    
    def test_disconnect_drone_success(self, drone_api_client, backend_mock):
        """ドローン切断成功"""
        result = drone_api_client.disconnect_drone()
        
        assert result is not None
        assert result['status'] == 'disconnected'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/disconnect'


class TestDroneAPIClientFlightControl:
    """基本飛行制御テスト"""
    
    def test_takeoff_success(self, drone_api_client, backend_mock):
        """離陸成功"""
        result = drone_api_client.takeoff()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'takeoff' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/takeoff'
    
    def test_land_success(self, drone_api_client, backend_mock):
        """着陸成功"""
        result = drone_api_client.land()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'landing' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/land'
    
    def test_emergency_stop_success(self, drone_api_client, backend_mock):
        """緊急停止成功"""
        result = drone_api_client.emergency_stop()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'emergency' in result['message'].lower()
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/emergency'


class TestDroneAPIClientMovement:
    """基本移動制御テスト"""
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_forward_valid_distances(self, drone_api_client, backend_mock, distance):
        """前進 - 有効距離"""
        result = drone_api_client.move_forward(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/forward'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_backward_valid_distances(self, drone_api_client, backend_mock, distance):
        """後退 - 有効距離"""
        result = drone_api_client.move_backward(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/back'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_left_valid_distances(self, drone_api_client, backend_mock, distance):
        """左移動 - 有効距離"""
        result = drone_api_client.move_left(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/left'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_right_valid_distances(self, drone_api_client, backend_mock, distance):
        """右移動 - 有効距離"""
        result = drone_api_client.move_right(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/right'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_up_valid_distances(self, drone_api_client, backend_mock, distance):
        """上昇 - 有効距離"""
        result = drone_api_client.move_up(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/up'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("distance", [20, 30, 50, 100, 500])
    def test_move_down_valid_distances(self, drone_api_client, backend_mock, distance):
        """下降 - 有効距離"""
        result = drone_api_client.move_down(distance)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/move/down'
        assert history[0]['kwargs']['json']['distance'] == distance
    
    @pytest.mark.parametrize("direction,angle", [
        ('cw', 90), ('ccw', 90), ('cw', 180), ('ccw', 180), ('cw', 360)
    ])
    def test_rotate_valid_parameters(self, drone_api_client, backend_mock, direction, angle):
        """回転 - 有効パラメータ"""
        result = drone_api_client.rotate(direction, angle)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/rotate'
        assert history[0]['kwargs']['json']['direction'] == direction
        assert history[0]['kwargs']['json']['angle'] == angle
    
    @pytest.mark.parametrize("direction", ['f', 'b', 'l', 'r'])
    def test_flip_valid_directions(self, drone_api_client, backend_mock, direction):
        """フリップ - 有効方向"""
        result = drone_api_client.flip(direction)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/flip'
        assert history[0]['kwargs']['json']['direction'] == direction


class TestDroneAPIClientAdvancedMovement:
    """高度移動制御テスト"""
    
    def test_go_xyz_success(self, drone_api_client, backend_mock):
        """3D座標移動成功"""
        x, y, z, speed = 100, -50, 150, 50
        result = drone_api_client.go_xyz(x, y, z, speed)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/go_xyz'
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == x
        assert request_data['y'] == y
        assert request_data['z'] == z
        assert request_data['speed'] == speed
    
    def test_curve_xyz_success(self, drone_api_client, backend_mock):
        """曲線飛行成功"""
        x1, y1, z1 = 0, 0, 100
        x2, y2, z2 = 100, 100, 150
        speed = 30
        
        result = drone_api_client.curve_xyz(x1, y1, z1, x2, y2, z2, speed)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/curve_xyz'
        request_data = history[0]['kwargs']['json']
        assert request_data['x1'] == x1
        assert request_data['y1'] == y1
        assert request_data['z1'] == z1
        assert request_data['x2'] == x2
        assert request_data['y2'] == y2
        assert request_data['z2'] == z2
        assert request_data['speed'] == speed
    
    def test_rc_control_success(self, drone_api_client, backend_mock):
        """リアルタイム制御成功"""
        left_right, forward_backward, up_down, yaw = 50, -30, 20, -10
        
        result = drone_api_client.rc_control(left_right, forward_backward, up_down, yaw)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/rc_control'
        request_data = history[0]['kwargs']['json']
        assert request_data['left_right_velocity'] == left_right
        assert request_data['forward_backward_velocity'] == forward_backward
        assert request_data['up_down_velocity'] == up_down
        assert request_data['yaw_velocity'] == yaw


class TestDroneAPIClientCamera:
    """カメラ操作テスト"""
    
    def test_start_video_stream_success(self, drone_api_client, backend_mock):
        """ビデオストリーミング開始成功"""
        result = drone_api_client.start_video_stream()
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/camera/stream/start'
    
    def test_stop_video_stream_success(self, drone_api_client, backend_mock):
        """ビデオストリーミング停止成功"""
        result = drone_api_client.stop_video_stream()
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/camera/stream/stop'
    
    def test_take_photo_success(self, drone_api_client, backend_mock):
        """写真撮影成功"""
        result = drone_api_client.take_photo()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'filename' in result
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/camera/photo'
    
    def test_start_recording_success(self, drone_api_client, backend_mock):
        """録画開始成功"""
        result = drone_api_client.start_recording()
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/camera/recording/start'
    
    def test_stop_recording_success(self, drone_api_client, backend_mock):
        """録画停止成功"""
        result = drone_api_client.stop_recording()
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'filename' in result
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/camera/recording/stop'


class TestDroneAPIClientSensors:
    """センサーデータテスト"""
    
    def test_get_battery_success(self, drone_api_client, backend_mock):
        """バッテリー残量取得成功"""
        result = drone_api_client.get_battery()
        
        assert result is not None
        assert 'battery' in result
        assert 'unit' in result
        assert result['battery'] == 85
        assert result['unit'] == '%'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/drone/battery'
    
    def test_get_altitude_success(self, drone_api_client, backend_mock):
        """高度取得成功"""
        result = drone_api_client.get_altitude()
        
        assert result is not None
        assert 'altitude' in result
        assert 'unit' in result
        assert result['altitude'] == 120
        assert result['unit'] == 'cm'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/drone/altitude'
    
    def test_get_temperature_success(self, drone_api_client, backend_mock):
        """温度取得成功"""
        result = drone_api_client.get_temperature()
        
        assert result is not None
        assert 'temperature' in result
        assert 'unit' in result
        assert result['temperature'] == 25.5
        assert result['unit'] == '°C'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/drone/temperature'
    
    def test_get_attitude_success(self, drone_api_client, backend_mock):
        """姿勢情報取得成功"""
        result = drone_api_client.get_attitude()
        
        assert result is not None
        assert 'pitch' in result
        assert 'roll' in result
        assert 'yaw' in result
        assert result['pitch'] == 0
        assert result['roll'] == 0
        assert result['yaw'] == 0
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/drone/attitude'
    
    def test_get_velocity_success(self, drone_api_client, backend_mock):
        """速度情報取得成功"""
        result = drone_api_client.get_velocity()
        
        assert result is not None
        assert 'vx' in result
        assert 'vy' in result
        assert 'vz' in result
        assert result['vx'] == 0
        assert result['vy'] == 0
        assert result['vz'] == 0
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'GET'
        assert history[0]['endpoint'] == '/drone/velocity'


class TestDroneAPIClientSettings:
    """WiFi・設定テスト"""
    
    @pytest.mark.parametrize("ssid,password", [
        ('TestWiFi', 'password123'),
        ('MyDrone', 'secretpass'),
        ('Network_5G', 'complex_password_123!')
    ])
    def test_set_wifi_success(self, drone_api_client, backend_mock, ssid, password):
        """WiFi設定成功"""
        result = drone_api_client.set_wifi(ssid, password)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'PUT'
        assert history[0]['endpoint'] == '/drone/wifi'
        request_data = history[0]['kwargs']['json']
        assert request_data['ssid'] == ssid
        assert request_data['password'] == password
    
    @pytest.mark.parametrize("speed", [1.0, 5.0, 10.0, 15.0])
    def test_set_speed_success(self, drone_api_client, backend_mock, speed):
        """飛行速度設定成功"""
        result = drone_api_client.set_speed(speed)
        
        assert result is not None
        assert result['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'PUT'
        assert history[0]['endpoint'] == '/drone/speed'
        request_data = history[0]['kwargs']['json']
        assert request_data['speed'] == speed
    
    @pytest.mark.parametrize("command,timeout", [
        ('battery?', 5), ('height?', 7), ('speed?', 10)
    ])
    def test_send_command_success(self, drone_api_client, backend_mock, command, timeout):
        """カスタムコマンド送信成功"""
        result = drone_api_client.send_command(command, timeout)
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'response' in result
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['method'] == 'POST'
        assert history[0]['endpoint'] == '/drone/command'
        request_data = history[0]['kwargs']['json']
        assert request_data['command'] == command
        assert request_data['timeout'] == timeout
        assert request_data['expect_response'] == True