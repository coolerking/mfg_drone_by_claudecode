"""
バックエンドAPIモック
単体テスト用のHTTPリクエストモック実装
"""

import json
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch
import requests


class MockResponse:
    """モックHTTPレスポンス"""
    
    def __init__(self, json_data: Dict[str, Any], status_code: int = 200, headers: Optional[Dict] = None):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {'Content-Type': 'application/json'}
        self.text = json.dumps(json_data) if json_data else ""
    
    def json(self):
        return self.json_data
    
    def iter_content(self, chunk_size=1024):
        """ストリーミングレスポンス用"""
        yield b"mock video stream data"


class BackendAPIMock:
    """バックエンドAPIモック管理クラス"""
    
    def __init__(self):
        self.mock_responses = {}
        self.request_history = []
        self.should_raise_exception = False
        self.exception_type = requests.exceptions.RequestException
        
    def setup_success_responses(self):
        """成功レスポンスを設定"""
        self.mock_responses = {
            # ヘルスチェック
            ('GET', '/health'): MockResponse({'status': 'healthy', 'message': 'Backend is running'}),
            
            # ドローン接続
            ('POST', '/drone/connect'): MockResponse({'status': 'connected', 'message': 'Drone connected successfully'}),
            ('POST', '/drone/disconnect'): MockResponse({'status': 'disconnected', 'message': 'Drone disconnected'}),
            
            # 基本飛行制御
            ('POST', '/drone/takeoff'): MockResponse({'status': 'success', 'message': 'Takeoff successful'}),
            ('POST', '/drone/land'): MockResponse({'status': 'success', 'message': 'Landing successful'}),
            ('POST', '/drone/emergency'): MockResponse({'status': 'success', 'message': 'Emergency stop successful'}),
            
            # 基本移動制御
            ('POST', '/drone/move/forward'): MockResponse({'status': 'success', 'message': 'Forward movement completed'}),
            ('POST', '/drone/move/back'): MockResponse({'status': 'success', 'message': 'Backward movement completed'}),
            ('POST', '/drone/move/left'): MockResponse({'status': 'success', 'message': 'Left movement completed'}),
            ('POST', '/drone/move/right'): MockResponse({'status': 'success', 'message': 'Right movement completed'}),
            ('POST', '/drone/move/up'): MockResponse({'status': 'success', 'message': 'Up movement completed'}),
            ('POST', '/drone/move/down'): MockResponse({'status': 'success', 'message': 'Down movement completed'}),
            ('POST', '/drone/rotate'): MockResponse({'status': 'success', 'message': 'Rotation completed'}),
            ('POST', '/drone/flip'): MockResponse({'status': 'success', 'message': 'Flip completed'}),
            
            # 高度移動制御
            ('POST', '/drone/go_xyz'): MockResponse({'status': 'success', 'message': 'XYZ movement completed'}),
            ('POST', '/drone/curve_xyz'): MockResponse({'status': 'success', 'message': 'Curve flight completed'}),
            ('POST', '/drone/rc_control'): MockResponse({'status': 'success', 'message': 'RC control active'}),
            
            # カメラ操作
            ('POST', '/camera/stream/start'): MockResponse({'status': 'success', 'message': 'Video stream started'}),
            ('POST', '/camera/stream/stop'): MockResponse({'status': 'success', 'message': 'Video stream stopped'}),
            ('POST', '/camera/photo'): MockResponse({'status': 'success', 'filename': 'photo_001.jpg'}),
            ('POST', '/camera/recording/start'): MockResponse({'status': 'success', 'message': 'Recording started'}),
            ('POST', '/camera/recording/stop'): MockResponse({'status': 'success', 'filename': 'recording_001.mp4'}),
            ('GET', '/camera/stream'): MockResponse({}, headers={'content-type': 'multipart/x-mixed-replace; boundary=frame'}),
            
            # センサーデータ
            ('GET', '/drone/battery'): MockResponse({'battery': 85, 'unit': '%'}),
            ('GET', '/drone/altitude'): MockResponse({'altitude': 120, 'unit': 'cm'}),
            ('GET', '/drone/temperature'): MockResponse({'temperature': 25.5, 'unit': '°C'}),
            ('GET', '/drone/attitude'): MockResponse({'pitch': 0, 'roll': 0, 'yaw': 0}),
            ('GET', '/drone/velocity'): MockResponse({'vx': 0, 'vy': 0, 'vz': 0}),
            
            # WiFi・設定
            ('PUT', '/drone/wifi'): MockResponse({'status': 'success', 'message': 'WiFi settings updated'}),
            ('PUT', '/drone/speed'): MockResponse({'status': 'success', 'message': 'Speed updated'}),
            ('POST', '/drone/command'): MockResponse({'status': 'success', 'response': 'ok'}),
            
            # ミッションパッド
            ('POST', '/mission_pad/enable'): MockResponse({'status': 'success', 'message': 'Mission pad enabled'}),
            ('POST', '/mission_pad/disable'): MockResponse({'status': 'success', 'message': 'Mission pad disabled'}),
            ('PUT', '/mission_pad/detection_direction'): MockResponse({'status': 'success', 'message': 'Detection direction set'}),
            ('POST', '/mission_pad/go_xyz'): MockResponse({'status': 'success', 'message': 'Mission pad navigation completed'}),
            ('GET', '/mission_pad/status'): MockResponse({'enabled': True, 'detection_direction': 0}),
            
            # 物体追跡
            ('POST', '/tracking/start'): MockResponse({'status': 'success', 'message': 'Tracking started'}),
            ('POST', '/tracking/stop'): MockResponse({'status': 'success', 'message': 'Tracking stopped'}),
            ('GET', '/tracking/status'): MockResponse({'tracking': False, 'target': None}),
            
            # モデル管理
            ('GET', '/model/list'): MockResponse({'models': ['person', 'car', 'bicycle']}),
            ('DELETE', '/model/person'): MockResponse({'status': 'success', 'message': 'Model deleted'}),
            ('POST', '/model/train'): MockResponse({'status': 'success', 'model_name': 'test_model', 'accuracy': 0.95}),
        }
    
    def setup_error_responses(self, status_code: int = 500):
        """エラーレスポンスを設定"""
        error_response = MockResponse({'error': 'Internal server error'}, status_code)
        for key in self.mock_responses.keys():
            self.mock_responses[key] = error_response
    
    def setup_timeout_exception(self):
        """タイムアウト例外を設定"""
        self.should_raise_exception = True
        self.exception_type = requests.exceptions.Timeout
    
    def setup_connection_error(self):
        """接続エラー例外を設定"""
        self.should_raise_exception = True
        self.exception_type = requests.exceptions.ConnectionError
    
    def setup_request_exception(self):
        """一般的なリクエスト例外を設定"""
        self.should_raise_exception = True
        self.exception_type = requests.exceptions.RequestException
    
    def mock_request(self, method: str, url: str, **kwargs):
        """リクエストをモック"""
        # リクエスト履歴を保存
        endpoint = url.replace('http://localhost:8000', '')
        self.request_history.append({
            'method': method,
            'url': url,
            'endpoint': endpoint,
            'kwargs': kwargs
        })
        
        # 例外を発生させる場合
        if self.should_raise_exception:
            raise self.exception_type("Mocked exception")
        
        # レスポンスを返す
        key = (method, endpoint)
        if key in self.mock_responses:
            return self.mock_responses[key]
        else:
            # デフォルトの404レスポンス
            return MockResponse({'error': 'Not found'}, 404)
    
    def get_request_history(self):
        """リクエスト履歴を取得"""
        return self.request_history
    
    def clear_request_history(self):
        """リクエスト履歴をクリア"""
        self.request_history = []
    
    def get_last_request(self):
        """最後のリクエストを取得"""
        return self.request_history[-1] if self.request_history else None


class MockSession:
    """requests.Session のモック"""
    
    def __init__(self, backend_mock: BackendAPIMock):
        self.backend_mock = backend_mock
        self.timeout = 10
    
    def get(self, url, **kwargs):
        return self.backend_mock.mock_request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.backend_mock.mock_request('POST', url, **kwargs)
    
    def put(self, url, **kwargs):
        return self.backend_mock.mock_request('PUT', url, **kwargs)
    
    def delete(self, url, **kwargs):
        return self.backend_mock.mock_request('DELETE', url, **kwargs)


def create_backend_mock():
    """バックエンドモック作成のファクトリ関数"""
    mock = BackendAPIMock()
    mock.setup_success_responses()
    return mock


def patch_requests_session(backend_mock: BackendAPIMock):
    """requests.Session をパッチするためのデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('requests.Session') as mock_session_class:
                mock_session_class.return_value = MockSession(backend_mock)
                return func(*args, **kwargs)
        return wrapper
    return decorator