"""
単体テスト用フィクスチャ
DroneAPIClient および Flask アプリケーションのテスト用共通設定
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mocks.backend_mock import BackendAPIMock, create_backend_mock, patch_requests_session


@pytest.fixture
def backend_mock():
    """バックエンドAPIモックのフィクスチャ"""
    return create_backend_mock()


@pytest.fixture
def error_backend_mock():
    """エラーレスポンス用バックエンドモック"""
    mock = BackendAPIMock()
    mock.setup_error_responses(500)
    return mock


@pytest.fixture
def timeout_backend_mock():
    """タイムアウト例外用バックエンドモック"""
    mock = BackendAPIMock()
    mock.setup_timeout_exception()
    return mock


@pytest.fixture
def connection_error_backend_mock():
    """接続エラー例外用バックエンドモック"""
    mock = BackendAPIMock()
    mock.setup_connection_error()
    return mock


@pytest.fixture
def test_config():
    """テスト用設定"""
    return {
        'BACKEND_API_URL': 'http://localhost:8000',
        'SECRET_KEY': 'test-secret-key',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False
    }


@pytest.fixture
def mock_env_vars(test_config):
    """環境変数モック"""
    with patch.dict(os.environ, {
        'BACKEND_API_URL': test_config['BACKEND_API_URL'],
        'SECRET_KEY': test_config['SECRET_KEY'],
        'FLASK_DEBUG': 'False'
    }):
        yield


@pytest.fixture
def drone_api_client(backend_mock, mock_env_vars):
    """DroneAPIClient インスタンス（モック付き）"""
    with patch('requests.Session') as mock_session_class:
        from mocks.backend_mock import MockSession
        mock_session_class.return_value = MockSession(backend_mock)
        
        # main.py から DroneAPIClient をインポート
        from main import DroneAPIClient
        client = DroneAPIClient()
        client._backend_mock = backend_mock  # テスト用に参照を保持
        return client


@pytest.fixture
def flask_app(backend_mock, mock_env_vars):
    """Flask アプリケーション（モック付き）"""
    with patch('requests.Session') as mock_session_class:
        from mocks.backend_mock import MockSession
        mock_session_class.return_value = MockSession(backend_mock)
        
        # main.py から app をインポート
        from main import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            yield app


@pytest.fixture
def flask_client(flask_app):
    """Flask テストクライアント"""
    return flask_app.test_client()


@pytest.fixture
def sample_drone_data():
    """サンプルドローンデータ"""
    return {
        'battery': {'battery': 85, 'unit': '%'},
        'altitude': {'altitude': 120, 'unit': 'cm'},
        'temperature': {'temperature': 25.5, 'unit': '°C'},
        'attitude': {'pitch': 0, 'roll': 0, 'yaw': 0},
        'velocity': {'vx': 0, 'vy': 0, 'vz': 0}
    }


@pytest.fixture
def valid_movement_parameters():
    """有効な移動パラメータ"""
    return {
        'distance_values': [20, 30, 50, 100, 500],  # 境界値と中間値
        'speed_values': [10, 30, 50, 100],
        'angle_values': [15, 30, 45, 90, 180, 360],
        'coordinate_values': [-500, -100, 0, 100, 500],
        'rc_velocity_values': [-100, -50, 0, 50, 100]
    }


@pytest.fixture
def invalid_movement_parameters():
    """無効な移動パラメータ"""
    return {
        'distance_values': [-1, 0, 3001],  # 範囲外値
        'speed_values': [0, 201],
        'angle_values': [-1, 3601],
        'coordinate_values': [-3001, 3001],
        'rc_velocity_values': [-101, 101]
    }


@pytest.fixture
def wifi_test_data():
    """WiFi設定テストデータ"""
    return {
        'valid': [
            {'ssid': 'TestWiFi', 'password': 'password123'},
            {'ssid': 'MyDrone', 'password': 'secretpass'},
            {'ssid': 'Network_5G', 'password': 'complex_password_123!'}
        ],
        'invalid': [
            {'ssid': '', 'password': 'password123'},  # 空のSSID
            {'ssid': 'TestWiFi', 'password': ''},     # 空のパスワード
            {'ssid': '', 'password': ''},             # 両方空
            {'ssid': None, 'password': 'password123'}, # None値
            {'ssid': 'TestWiFi', 'password': None}    # None値
        ]
    }


@pytest.fixture
def speed_test_data():
    """速度設定テストデータ"""
    return {
        'valid': [1.0, 5.0, 10.0, 15.0],     # 有効範囲
        'invalid': [0.0, 0.5, 15.1, 20.0, -1.0]  # 無効範囲
    }


@pytest.fixture
def tracking_test_data():
    """物体追跡テストデータ"""
    return {
        'valid_objects': ['person', 'car', 'bicycle', 'dog', 'cat'],
        'valid_modes': ['center', 'follow', 'surround'],
        'invalid_objects': ['', None, 'invalid_object'],
        'invalid_modes': ['', None, 'invalid_mode']
    }


@pytest.fixture
def model_test_data():
    """モデル管理テストデータ"""
    return {
        'existing_models': ['person', 'car', 'bicycle'],
        'non_existing_models': ['nonexistent', 'fake_model'],
        'new_model_names': ['test_model', 'custom_object', 'new_detection']
    }


@pytest.fixture
def mission_pad_test_data():
    """ミッションパッドテストデータ"""
    return {
        'valid_coordinates': [
            {'x': 0, 'y': 0, 'z': 100, 'speed': 50, 'pad_id': 1},
            {'x': 100, 'y': -100, 'z': 200, 'speed': 30, 'pad_id': 2},
            {'x': -200, 'y': 200, 'z': 150, 'speed': 70, 'pad_id': 8}
        ],
        'invalid_coordinates': [
            {'x': 3000, 'y': 0, 'z': 100, 'speed': 50, 'pad_id': 1},    # x範囲外
            {'x': 0, 'y': 3000, 'z': 100, 'speed': 50, 'pad_id': 1},    # y範囲外
            {'x': 0, 'y': 0, 'z': -1, 'speed': 50, 'pad_id': 1},        # z範囲外
            {'x': 0, 'y': 0, 'z': 100, 'speed': 0, 'pad_id': 1},        # speed範囲外
            {'x': 0, 'y': 0, 'z': 100, 'speed': 50, 'pad_id': 0},       # pad_id範囲外
            {'x': 0, 'y': 0, 'z': 100, 'speed': 50, 'pad_id': 9}        # pad_id範囲外
        ],
        'valid_detection_directions': [0, 1, 2],
        'invalid_detection_directions': [-1, 3, 10]
    }


@pytest.fixture
def http_error_codes():
    """HTTPエラーコードテスト用"""
    return [400, 401, 403, 404, 500, 502, 503, 504]


@pytest.fixture
def curve_flight_test_data():
    """曲線飛行テストデータ"""
    return {
        'valid_curves': [
            {'x1': 0, 'y1': 0, 'z1': 100, 'x2': 100, 'y2': 100, 'z2': 150, 'speed': 30},
            {'x1': -100, 'y1': -100, 'z1': 50, 'x2': 200, 'y2': 200, 'z2': 200, 'speed': 50},
        ],
        'invalid_curves': [
            {'x1': 3000, 'y1': 0, 'z1': 100, 'x2': 100, 'y2': 100, 'z2': 150, 'speed': 30},  # x1範囲外
            {'x1': 0, 'y1': 0, 'z1': 100, 'x2': 100, 'y2': 100, 'z2': 150, 'speed': 0},      # speed範囲外
        ]
    }


@pytest.fixture
def rc_control_test_data():
    """RCコントロールテストデータ"""
    return {
        'valid_velocities': [
            {'left_right': 0, 'forward_backward': 0, 'up_down': 0, 'yaw': 0},
            {'left_right': 50, 'forward_backward': -30, 'up_down': 20, 'yaw': -10},
            {'left_right': -100, 'forward_backward': 100, 'up_down': -100, 'yaw': 100},
        ],
        'invalid_velocities': [
            {'left_right': 101, 'forward_backward': 0, 'up_down': 0, 'yaw': 0},      # left_right範囲外
            {'left_right': 0, 'forward_backward': -101, 'up_down': 0, 'yaw': 0},     # forward_backward範囲外
            {'left_right': 0, 'forward_backward': 0, 'up_down': 101, 'yaw': 0},      # up_down範囲外
            {'left_right': 0, 'forward_backward': 0, 'up_down': 0, 'yaw': -101},     # yaw範囲外
        ]
    }


@pytest.fixture
def command_test_data():
    """カスタムコマンドテストデータ"""
    return {
        'valid_commands': [
            {'command': 'battery?', 'timeout': 5},
            {'command': 'height?', 'timeout': 7},
            {'command': 'speed?', 'timeout': 10},
        ],
        'invalid_commands': [
            {'command': '', 'timeout': 5},        # 空コマンド
            {'command': None, 'timeout': 5},      # Noneコマンド
            {'command': 'battery?', 'timeout': 0}, # 無効タイムアウト
            {'command': 'battery?', 'timeout': -1}, # 負のタイムアウト
        ]
    }