"""
Flask ルートハンドラの高度機能単体テスト
物体追跡・モデル管理・設定・エラーハンドリングのテスト
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


class TestTrackingRoutes:
    """物体追跡 API のテスト"""
    
    def test_start_tracking_route(self, flask_client, backend_mock):
        """追跡開始プロキシ"""
        test_data = {'target_object': 'person', 'tracking_mode': 'center'}
        response = flask_client.post('/api/tracking/start', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['target_object'] == 'person'
        assert request_data['tracking_mode'] == 'center'
    
    def test_start_tracking_route_default_mode(self, flask_client, backend_mock):
        """追跡開始プロキシ - デフォルトモード"""
        test_data = {'target_object': 'car'}
        response = flask_client.post('/api/tracking/start', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルトモード'center'が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['target_object'] == 'car'
        assert request_data['tracking_mode'] == 'center'
    
    def test_start_tracking_route_missing_target(self, flask_client):
        """追跡開始プロキシ - ターゲット未指定"""
        test_data = {'tracking_mode': 'center'}
        response = flask_client.post('/api/tracking/start', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Target object not specified' in data['error']
    
    def test_start_tracking_route_empty_target(self, flask_client):
        """追跡開始プロキシ - 空のターゲット"""
        test_data = {'target_object': '', 'tracking_mode': 'center'}
        response = flask_client.post('/api/tracking/start', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Target object not specified' in data['error']
    
    def test_stop_tracking_route(self, flask_client, backend_mock):
        """追跡停止プロキシ"""
        response = flask_client.post('/api/tracking/stop')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_get_tracking_status_route(self, flask_client, backend_mock):
        """追跡ステータス取得プロキシ"""
        response = flask_client.get('/api/tracking/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tracking' in data
        assert 'target' in data


class TestModelManagementRoutes:
    """モデル管理 API のテスト"""
    
    def test_train_model_route_success(self, flask_client, backend_mock):
        """モデル訓練プロキシ - 成功"""
        # ファイルアップロードのモック
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'model_name': 'test_model',
                'accuracy': 0.95
            }
            mock_post.return_value = mock_response
            
            # マルチパートフォームデータを作成
            data = {
                'file': (io.BytesIO(b'fake image data'), 'test_image.jpg'),
                'object_name': 'test_object'
            }
            
            response = flask_client.post('/api/model/train', 
                                       data=data,
                                       content_type='multipart/form-data')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'success'
            assert result['model_name'] == 'test_model'
    
    def test_train_model_route_no_file(self, flask_client):
        """モデル訓練プロキシ - ファイルなし"""
        data = {'object_name': 'test_object'}
        response = flask_client.post('/api/model/train', 
                                   data=data,
                                   content_type='multipart/form-data')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'No file provided' in result['error']
    
    def test_train_model_route_no_object_name(self, flask_client):
        """モデル訓練プロキシ - オブジェクト名なし"""
        data = {
            'file': (io.BytesIO(b'fake image data'), 'test_image.jpg')
        }
        response = flask_client.post('/api/model/train', 
                                   data=data,
                                   content_type='multipart/form-data')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Object name required' in result['error']
    
    def test_train_model_route_backend_error(self, flask_client):
        """モデル訓練プロキシ - バックエンドエラー"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response
            
            data = {
                'file': (io.BytesIO(b'fake image data'), 'test_image.jpg'),
                'object_name': 'test_object'
            }
            
            response = flask_client.post('/api/model/train', 
                                       data=data,
                                       content_type='multipart/form-data')
            
            assert response.status_code == 500
            result = json.loads(response.data)
            assert 'error' in result
            assert 'Model training failed' in result['error']
    
    def test_train_model_route_exception(self, flask_client):
        """モデル訓練プロキシ - 例外発生"""
        with patch('requests.post', side_effect=Exception('Network error')):
            data = {
                'file': (io.BytesIO(b'fake image data'), 'test_image.jpg'),
                'object_name': 'test_object'
            }
            
            response = flask_client.post('/api/model/train', 
                                       data=data,
                                       content_type='multipart/form-data')
            
            assert response.status_code == 500
            result = json.loads(response.data)
            assert 'error' in result
            assert 'File upload failed' in result['error']
    
    def test_get_model_list_route(self, flask_client, backend_mock):
        """モデル一覧プロキシ"""
        response = flask_client.get('/api/model/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert isinstance(data['models'], list)
        assert 'person' in data['models']
    
    def test_delete_model_route(self, flask_client, backend_mock):
        """モデル削除プロキシ"""
        model_name = 'test_model'
        response = flask_client.delete(f'/api/model/{model_name}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['endpoint'] == f'/model/{model_name}'


class TestSettingsRoutes:
    """設定管理 API のテスト"""
    
    def test_set_wifi_settings_route(self, flask_client, backend_mock):
        """WiFi設定プロキシ"""
        test_data = {'ssid': 'TestWiFi', 'password': 'password123'}
        response = flask_client.put('/api/settings/wifi', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['ssid'] == 'TestWiFi'
        assert request_data['password'] == 'password123'
    
    def test_set_wifi_settings_route_missing_ssid(self, flask_client):
        """WiFi設定プロキシ - SSID未指定"""
        test_data = {'password': 'password123'}
        response = flask_client.put('/api/settings/wifi', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'SSID and password required' in data['error']
    
    def test_set_wifi_settings_route_missing_password(self, flask_client):
        """WiFi設定プロキシ - パスワード未指定"""
        test_data = {'ssid': 'TestWiFi'}
        response = flask_client.put('/api/settings/wifi', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'SSID and password required' in data['error']
    
    def test_set_wifi_settings_route_empty_values(self, flask_client):
        """WiFi設定プロキシ - 空の値"""
        test_data = {'ssid': '', 'password': ''}
        response = flask_client.put('/api/settings/wifi', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'SSID and password required' in data['error']
    
    @pytest.mark.parametrize("speed", [1.0, 5.0, 10.0, 15.0])
    def test_set_flight_speed_route_valid(self, flask_client, backend_mock, speed):
        """飛行速度設定プロキシ - 有効値"""
        test_data = {'speed': speed}
        response = flask_client.put('/api/settings/speed', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['speed'] == speed
    
    @pytest.mark.parametrize("speed", [0.0, 0.5, 15.1, 20.0, -1.0])
    def test_set_flight_speed_route_invalid(self, flask_client, speed):
        """飛行速度設定プロキシ - 無効値"""
        test_data = {'speed': speed}
        response = flask_client.put('/api/settings/speed', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid speed value (1.0-15.0 m/s)' in data['error']
    
    def test_set_flight_speed_route_missing_speed(self, flask_client):
        """飛行速度設定プロキシ - 速度未指定"""
        test_data = {}
        response = flask_client.put('/api/settings/speed', 
                                  json=test_data,
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid speed value (1.0-15.0 m/s)' in data['error']
    
    def test_send_custom_command_route(self, flask_client, backend_mock):
        """カスタムコマンドプロキシ"""
        test_data = {'command': 'battery?', 'timeout': 10}
        response = flask_client.post('/api/settings/command', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        history = backend_mock.get_request_history()
        assert len(history) == 1
        request_data = history[0]['kwargs']['json']
        assert request_data['command'] == 'battery?'
        assert request_data['timeout'] == 10
    
    def test_send_custom_command_route_default_timeout(self, flask_client, backend_mock):
        """カスタムコマンドプロキシ - デフォルトタイムアウト"""
        test_data = {'command': 'height?'}
        response = flask_client.post('/api/settings/command', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 200
        
        # デフォルトタイムアウト7が使用されることを確認
        history = backend_mock.get_request_history()
        assert len(history) == 1
        assert history[0]['kwargs']['json']['timeout'] == 7
    
    def test_send_custom_command_route_missing_command(self, flask_client):
        """カスタムコマンドプロキシ - コマンド未指定"""
        test_data = {'timeout': 10}
        response = flask_client.post('/api/settings/command', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Command required' in data['error']
    
    def test_send_custom_command_route_empty_command(self, flask_client):
        """カスタムコマンドプロキシ - 空のコマンド"""
        test_data = {'command': '', 'timeout': 10}
        response = flask_client.post('/api/settings/command', 
                                   json=test_data,
                                   content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Command required' in data['error']


class TestErrorHandlers:
    """エラーハンドラのテスト"""
    
    def test_404_error_handler(self, flask_client):
        """404エラーハンドラ"""
        response = flask_client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Endpoint not found' in data['error']
    
    def test_500_error_handler(self, flask_app):
        """500エラーハンドラ"""
        # 意図的に500エラーを発生させるルートを追加
        @flask_app.route('/test-500-error')
        def test_500_error():
            raise Exception("Test internal server error")
        
        with flask_app.test_client() as client:
            response = client.get('/test-500-error')
            
            assert response.status_code == 500
            assert response.content_type == 'application/json'
            
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Internal server error' in data['error']
    
    def test_503_error_handler_sensor_failure(self, flask_client):
        """503エラーハンドラ - センサーデータ取得失敗"""
        with patch('main.api_client') as mock_client:
            # api_clientのメソッドがNoneを返すようにモック
            mock_client.get_battery.return_value = None
            
            response = flask_client.get('/api/drone/battery')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Battery data unavailable' in data['error']


class TestErrorResponseHandling:
    """エラーレスポンス処理のテスト"""
    
    def test_backend_error_handling_connect(self, flask_client):
        """バックエンドエラー処理 - 接続失敗"""
        with patch('main.api_client') as mock_client:
            # api_clientのメソッドがNoneを返すようにモック（バックエンドエラー）
            mock_client.connect_drone.return_value = None
            
            response = flask_client.post('/api/drone/connect')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Connection failed' in data['error']
    
    def test_backend_error_handling_takeoff(self, flask_client):
        """バックエンドエラー処理 - 離陸失敗"""
        with patch('main.api_client') as mock_client:
            mock_client.takeoff.return_value = None
            
            response = flask_client.post('/api/drone/takeoff')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Takeoff failed' in data['error']
    
    def test_backend_error_handling_movement(self, flask_client):
        """バックエンドエラー処理 - 移動失敗"""
        with patch('main.api_client') as mock_client:
            mock_client.move_forward.return_value = None
            
            test_data = {'distance': 50}
            response = flask_client.post('/api/drone/move/forward', 
                                       json=test_data,
                                       content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'forward movement failed' in data['error']
    
    def test_backend_error_handling_camera(self, flask_client):
        """バックエンドエラー処理 - カメラ失敗"""
        with patch('main.api_client') as mock_client:
            mock_client.take_photo.return_value = None
            
            response = flask_client.post('/api/camera/photo')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Photo capture failed' in data['error']
    
    def test_backend_error_handling_tracking(self, flask_client):
        """バックエンドエラー処理 - 追跡失敗"""
        with patch('main.api_client') as mock_client:
            mock_client.start_tracking.return_value = None
            
            test_data = {'target_object': 'person', 'tracking_mode': 'center'}
            response = flask_client.post('/api/tracking/start', 
                                       json=test_data,
                                       content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Tracking start failed' in data['error']
    
    def test_backend_error_handling_mission_pad(self, flask_client):
        """バックエンドエラー処理 - ミッションパッド失敗"""
        with patch('main.api_client') as mock_client:
            mock_client.enable_mission_pad.return_value = None
            
            response = flask_client.post('/api/mission_pad/enable')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Mission pad enable failed' in data['error']
    
    def test_video_stream_error_handling(self, flask_client):
        """ビデオストリーミングエラー処理"""
        with patch('requests.get', side_effect=Exception('Network error')):
            response = flask_client.get('/api/camera/stream')
            
            assert response.status_code == 503
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Video stream unavailable' in data['error']


class TestJSONRequestHandling:
    """JSONリクエスト処理のテスト"""
    
    def test_malformed_json_request(self, flask_client):
        """不正なJSONリクエスト"""
        response = flask_client.post('/api/drone/move/forward', 
                                   data='{"invalid": json}',
                                   content_type='application/json')
        
        # Flaskは不正なJSONに対して400エラーを返す
        assert response.status_code == 400
    
    def test_missing_content_type_json(self, flask_client, backend_mock):
        """Content-Type未指定でのJSONリクエスト"""
        test_data = {'distance': 50}
        response = flask_client.post('/api/drone/move/forward', 
                                   json=test_data)  # content_type指定なし
        
        # Flask が自動的に application/json を設定するので成功する
        assert response.status_code == 200
    
    def test_empty_json_request(self, flask_client, backend_mock):
        """空のJSONリクエスト"""
        response = flask_client.post('/api/drone/move/forward', 
                                   json={},
                                   content_type='application/json')
        
        # デフォルト値が使用されて成功する
        assert response.status_code == 200
    
    def test_null_json_request(self, flask_client):
        """null JSONリクエスト"""
        response = flask_client.post('/api/drone/move/forward', 
                                   json=None,
                                   content_type='application/json')
        
        # request.get_json() が None を返すため、デフォルト処理される
        assert response.status_code == 200  # デフォルト距離30で処理される