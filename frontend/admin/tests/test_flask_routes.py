"""
Flask ルートハンドラの単体テスト
API エンドポイントの動作確認
"""

import pytest
import json
import io
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fixtures.unit_test_fixtures import *


class TestBasicRoutes:
    """基本ルートのテスト"""
    
    def test_index_route(self, flask_client):
        """メインページ表示"""
        response = flask_client.get('/')
        
        assert response.status_code == 200
        assert b'text/html' in response.content_type.encode()
    
    def test_health_check_route(self, flask_client, backend_mock):
        """フロントエンドヘルスチェック"""
        response = flask_client.get('/health')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'frontend' in data
        assert 'MFG Drone Admin' in data['frontend']
        assert 'backend' in data


class TestDroneControlRoutes:
    """ドローン制御 API プロキシのテスト"""
    
    def test_connect_drone_route(self, flask_client, backend_mock):
        """ドローン接続プロキシ"""
        response = flask_client.post('/api/drone/connect')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['status'] == 'connected'
        
        # バックエンドAPIが呼ばれたことを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['endpoint'] == '/drone/connect'
    
    def test_disconnect_drone_route(self, flask_client, backend_mock):
        """ドローン切断プロキシ"""
        response = flask_client.post('/api/drone/disconnect')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'disconnected'
    
    def test_takeoff_route(self, flask_client, backend_mock):
        """離陸プロキシ"""
        response = flask_client.post('/api/drone/takeoff')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_land_route(self, flask_client, backend_mock):
        """着陸プロキシ"""
        response = flask_client.post('/api/drone/land')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_emergency_route(self, flask_client, backend_mock):
        """緊急停止プロキシ"""
        response = flask_client.post('/api/drone/emergency')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestMovementRoutes:
    """移動制御ルートのテスト"""
    
    @pytest.mark.parametrize("direction", ['forward', 'backward', 'left', 'right', 'up', 'down'])
    def test_move_drone_route_valid_directions(self, flask_client, backend_mock, direction):
        """移動プロキシ - 有効方向"""
        test_data = {'distance': 50}
        response = flask_client.post(f'/api/drone/move/{direction}', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # バックエンドAPIに正しい値が渡されたか確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['distance'] == 50
    
    def test_move_drone_route_invalid_direction(self, flask_client):
        """移動プロキシ - 無効方向"""
        test_data = {'distance': 50}
        response = flask_client.post('/api/drone/move/invalid', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid direction' in data['error']
    
    def test_move_drone_route_default_distance(self, flask_client, backend_mock):
        """移動プロキシ - デフォルト距離"""
        response = flask_client.post('/api/drone/move/forward', 
                                   json={},
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト距離30が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['distance'] == 30
    
    def test_rotate_drone_route(self, flask_client, backend_mock):
        """回転プロキシ"""
        test_data = {'direction': 'cw', 'angle': 90}
        response = flask_client.post('/api/drone/rotate', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['direction'] == 'cw'
        assert request_data['angle'] == 90
    
    def test_rotate_drone_route_default_angle(self, flask_client, backend_mock):
        """回転プロキシ - デフォルト角度"""
        test_data = {'direction': 'ccw'}
        response = flask_client.post('/api/drone/rotate', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト角度90が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['angle'] == 90


class TestAdvancedMovementRoutes:
    """高度移動制御ルートのテスト"""
    
    def test_go_xyz_route(self, flask_client, backend_mock):
        """3D座標移動プロキシ"""
        test_data = {'x': 100, 'y': -50, 'z': 150, 'speed': 50}
        response = flask_client.post('/api/drone/go_xyz', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == 100
        assert request_data['y'] == -50
        assert request_data['z'] == 150
        assert request_data['speed'] == 50
    
    def test_go_xyz_route_default_values(self, flask_client, backend_mock):
        """3D座標移動プロキシ - デフォルト値"""
        response = flask_client.post('/api/drone/go_xyz', 
                                   json={},
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト値が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == 0
        assert request_data['y'] == 0
        assert request_data['z'] == 0
        assert request_data['speed'] == 50
    
    def test_curve_xyz_route(self, flask_client, backend_mock):
        """曲線飛行プロキシ"""
        test_data = {
            'x1': 0, 'y1': 0, 'z1': 100,
            'x2': 100, 'y2': 100, 'z2': 150,
            'speed': 30
        }
        response = flask_client.post('/api/drone/curve_xyz', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x1'] == 0
        assert request_data['y1'] == 0
        assert request_data['z1'] == 100
        assert request_data['x2'] == 100
        assert request_data['y2'] == 100
        assert request_data['z2'] == 150
        assert request_data['speed'] == 30
    
    def test_curve_xyz_route_default_values(self, flask_client, backend_mock):
        """曲線飛行プロキシ - デフォルト値"""
        response = flask_client.post('/api/drone/curve_xyz', 
                                   json={},
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト値が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['speed'] == 30  # デフォルト値
    
    def test_rc_control_route(self, flask_client, backend_mock):
        """リアルタイム制御プロキシ"""
        test_data = {
            'left_right_velocity': 50,
            'forward_backward_velocity': -30,
            'up_down_velocity': 20,
            'yaw_velocity': -10
        }
        response = flask_client.post('/api/drone/rc_control', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['left_right_velocity'] == 50
        assert request_data['forward_backward_velocity'] == -30
        assert request_data['up_down_velocity'] == 20
        assert request_data['yaw_velocity'] == -10
    
    def test_rc_control_route_default_values(self, flask_client, backend_mock):
        """リアルタイム制御プロキシ - デフォルト値"""
        response = flask_client.post('/api/drone/rc_control', 
                                   json={},
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト値0が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['left_right_velocity'] == 0
        assert request_data['forward_backward_velocity'] == 0
        assert request_data['up_down_velocity'] == 0
        assert request_data['yaw_velocity'] == 0


class TestSensorRoutes:
    """センサーデータ API のテスト"""
    
    def test_get_all_sensors_route(self, flask_client, backend_mock):
        """全センサーデータ取得"""
        response = flask_client.get('/api/sensors/all')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 各センサーデータが含まれていることを確認
        assert 'battery' in data
        assert 'altitude' in data
        assert 'temperature' in data
        assert 'attitude' in data
        assert 'velocity' in data
        
        # 複数のAPIが呼ばれたことを確認
        history = backend_mock.get_request_history()
        assert len(history) == 5  # 5つのセンサーAPI
    
    def test_get_battery_route(self, flask_client, backend_mock):
        """バッテリー取得プロキシ"""
        response = flask_client.get('/api/drone/battery')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'battery' in data
        assert data['battery'] == 85
        assert data['unit'] == '%'
    
    def test_get_altitude_route(self, flask_client, backend_mock):
        """高度取得プロキシ"""
        response = flask_client.get('/api/drone/altitude')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'altitude' in data
        assert data['altitude'] == 120
        assert data['unit'] == 'cm'
    
    def test_get_temperature_route(self, flask_client, backend_mock):
        """温度取得プロキシ"""
        response = flask_client.get('/api/drone/temperature')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'temperature' in data
        assert data['temperature'] == 25.5
        assert data['unit'] == '°C'
    
    def test_get_attitude_route(self, flask_client, backend_mock):
        """姿勢取得プロキシ"""
        response = flask_client.get('/api/drone/attitude')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pitch' in data
        assert 'roll' in data
        assert 'yaw' in data


class TestCameraRoutes:
    """カメラ制御 API のテスト"""
    
    def test_start_video_stream_route(self, flask_client, backend_mock):
        """ストリーミング開始プロキシ"""
        response = flask_client.post('/api/camera/stream/start')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'video stream started' in data['message'].lower()
    
    def test_stop_video_stream_route(self, flask_client, backend_mock):
        """ストリーミング停止プロキシ"""
        response = flask_client.post('/api/camera/stream/stop')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'video stream stopped' in data['message'].lower()
    
    def test_take_photo_route(self, flask_client, backend_mock):
        """写真撮影プロキシ"""
        response = flask_client.post('/api/camera/photo')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'filename' in data
    
    def test_start_recording_route(self, flask_client, backend_mock):
        """録画開始プロキシ"""
        response = flask_client.post('/api/camera/recording/start')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_stop_recording_route(self, flask_client, backend_mock):
        """録画停止プロキシ"""
        response = flask_client.post('/api/camera/recording/stop')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'filename' in data
    
    def test_video_stream_route(self, flask_client, backend_mock):
        """ビデオストリーミングプロキシ"""
        # requestsモジュールをパッチしてストリーミングレスポンスをモック
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.headers = {'content-type': 'multipart/x-mixed-replace; boundary=frame'}
            mock_response.iter_content.return_value = [b'mock video data']
            mock_get.return_value = mock_response
            
            response = flask_client.get('/api/camera/stream')
            
            assert response.status_code == 200
            assert b'mock video data' in response.data


class TestMissionPadRoutes:
    """ミッションパッド API のテスト"""
    
    def test_enable_mission_pad_route(self, flask_client, backend_mock):
        """ミッションパッド有効化プロキシ"""
        response = flask_client.post('/api/mission_pad/enable')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_disable_mission_pad_route(self, flask_client, backend_mock):
        """ミッションパッド無効化プロキシ"""
        response = flask_client.post('/api/mission_pad/disable')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_set_detection_direction_route(self, flask_client, backend_mock):
        """検出方向設定プロキシ"""
        test_data = {'direction': 1}
        response = flask_client.put('/api/mission_pad/detection_direction', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['direction'] == 1
    
    def test_set_detection_direction_route_default(self, flask_client, backend_mock):
        """検出方向設定プロキシ - デフォルト値"""
        response = flask_client.put('/api/mission_pad/detection_direction', 
                                  json={},
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト値0が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['direction'] == 0
    
    def test_go_to_mission_pad_route(self, flask_client, backend_mock):
        """ミッションパッド移動プロキシ"""
        test_data = {'x': 100, 'y': -50, 'z': 150, 'speed': 50, 'mission_pad_id': 2}
        response = flask_client.post('/api/mission_pad/go_xyz', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == 100
        assert request_data['y'] == -50
        assert request_data['z'] == 150
        assert request_data['speed'] == 50
        assert request_data['mission_pad_id'] == 2
    
    def test_go_to_mission_pad_route_default_values(self, flask_client, backend_mock):
        """ミッションパッド移動プロキシ - デフォルト値"""
        response = flask_client.post('/api/mission_pad/go_xyz', 
                                   json={},
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルト値が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['x'] == 0
        assert request_data['y'] == 0
        assert request_data['z'] == 0
        assert request_data['speed'] == 50
        assert request_data['mission_pad_id'] == 1
    
    def test_get_mission_pad_status_route(self, flask_client, backend_mock):
        """ミッションパッドステータス取得プロキシ"""
        response = flask_client.get('/api/mission_pad/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'enabled' in data
        assert 'detection_direction' in data