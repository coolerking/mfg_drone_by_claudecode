# フェーズ3 結合テスト実装ロードマップ

## 概要

フェーズ3結合テストの具体的実装手順、技術的詳細、及び実行ガイドを提供する実践的文書です。

---

## 1. 実装フェーズ詳細

### Phase 1: テスト基盤構築 (推定: 10-12時間)

#### 1.1 プロジェクト構造セットアップ

```bash
# ディレクトリ作成
mkdir -p tests/integration/{mock_backend,real_backend}
mkdir -p tests/fixtures/{api_responses,test_data}
mkdir -p tests/mocks/{servers,clients}
mkdir -p tests/utils

# 設定ファイル作成
touch tests/integration/conftest.py
touch tests/integration/pytest.ini
touch tests/integration/test_requirements.txt
```

#### 1.2 コア依存関係

```python
# test_requirements.txt
pytest>=7.4.0
pytest-flask>=1.3.0
pytest-asyncio>=0.21.0
pytest-mock>=3.12.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.0          # 並行実行
pytest-html>=4.1.0           # HTMLレポート

# HTTP/WebSocket テスト
httpx>=0.25.0
websocket-client>=1.7.0
python-socketio[client]>=5.9.0

# モック・スタブ
responses>=0.24.0
requests-mock>=1.11.0
wiremock>=2.5.0

# ファイル・画像処理
Pillow>=10.1.0
opencv-python>=4.8.0

# 実機テスト（オプション）
djitellopy>=2.5.0            # Tello制御
```

#### 1.3 基本設定ファイル

```python
# tests/integration/conftest.py
import pytest
import asyncio
from flask import Flask
from unittest.mock import Mock, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    """イベントループフィクスチャ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_backend_server():
    """モックバックエンドサーバー"""
    from tests.mocks.servers.mock_backend import MockBackendServer
    server = MockBackendServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture
def test_client():
    """フロントエンドテストクライアント"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def websocket_client():
    """WebSocketテストクライアント"""
    import socketio
    client = socketio.Client()
    yield client
    if client.connected:
        client.disconnect()
```

#### 1.4 成果物・確認事項

- [ ] テストディレクトリ構造完成
- [ ] 依存関係インストール完了
- [ ] 基本フィクスチャ動作確認
- [ ] CI/CD設定準備完了

---

### Phase 2: モックバックエンド実装 (推定: 25-30時間)

#### 2.1 HTTPモックサーバー実装

```python
# tests/mocks/servers/mock_backend.py
import json
import threading
import time
from flask import Flask, request, jsonify
from werkzeug.serving import make_server

class MockBackendServer:
    def __init__(self, host='localhost', port=8000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.setup_routes()
        
    def setup_routes(self):
        """全APIエンドポイントのモック実装"""
        
        # システムAPI
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy"})
            
        # 接続管理API
        @self.app.route('/drone/connect', methods=['POST'])
        def drone_connect():
            # 接続シミュレーション（遅延含む）
            time.sleep(0.5)
            return jsonify({"success": True, "message": "接続成功"})
            
        @self.app.route('/drone/disconnect', methods=['POST'])
        def drone_disconnect():
            return jsonify({"success": True, "message": "切断成功"})
            
        # 飛行制御API (略: 4エンドポイント)
        # 移動制御API (略: 3エンドポイント)
        # カメラAPI (略: 6エンドポイント)
        # センサーAPI (略: 10エンドポイント)
        # 設定API (略: 3エンドポイント)
        # 追跡API (略: 3エンドポイント)
        # モデル管理API (略: 2エンドポイント)
```

#### 2.2 WebSocketモック実装

```python
# tests/mocks/servers/websocket_mock.py
import socketio
import asyncio
import json
import random
from threading import Thread

class MockWebSocketServer:
    def __init__(self, host='localhost', port=8001):
        self.sio = socketio.Server(cors_allowed_origins="*")
        self.app = socketio.WSGIApp(self.sio)
        self.host = host
        self.port = port
        self.running = False
        self.setup_handlers()
        
    def setup_handlers(self):
        @self.sio.event
        def connect(sid, environ):
            print(f'WebSocket クライアント接続: {sid}')
            
        @self.sio.event
        def disconnect(sid):
            print(f'WebSocket クライアント切断: {sid}')
            
        @self.sio.event
        def request_sensor_data(sid, data):
            """センサーデータ要求ハンドラ"""
            self.start_sensor_data_stream(sid)
            
    def start_sensor_data_stream(self, sid):
        """センサーデータストリーム開始"""
        def stream_data():
            while self.running:
                # モックセンサーデータ生成
                sensor_data = {
                    "battery": random.randint(20, 100),
                    "height": random.randint(0, 300),
                    "temperature": random.randint(20, 60),
                    "timestamp": time.time()
                }
                self.sio.emit('sensor_data', sensor_data, room=sid)
                time.sleep(1)  # 1秒間隔
                
        Thread(target=stream_data, daemon=True).start()
```

#### 2.3 データ生成・状態管理

```python
# tests/mocks/data_generators.py
import random
import time
import numpy as np
from typing import Dict, Any

class MockDataGenerator:
    def __init__(self):
        self.drone_state = {
            "connected": False,
            "flying": False,
            "streaming": False,
            "tracking": False
        }
        
    def generate_sensor_data(self) -> Dict[str, Any]:
        """リアリスティックなセンサーデータ生成"""
        return {
            "battery": max(0, 100 - random.randint(0, 5)),  # 漸減
            "height": random.randint(0, 300) if self.drone_state["flying"] else 0,
            "temperature": 25 + random.gauss(0, 3),  # 正規分布
            "acceleration": {
                "x": random.gauss(0, 0.1),
                "y": random.gauss(0, 0.1), 
                "z": random.gauss(1.0, 0.1)  # 重力
            },
            "attitude": {
                "pitch": random.randint(-10, 10),
                "roll": random.randint(-10, 10),
                "yaw": random.randint(0, 360)
            }
        }
        
    def generate_tracking_data(self) -> Dict[str, Any]:
        """物体追跡データ生成"""
        if not self.drone_state["tracking"]:
            return {"is_tracking": False}
            
        # 自然な移動パターン生成
        t = time.time()
        x = 320 + 100 * np.sin(t * 0.1)  # 画面中央周辺
        y = 240 + 50 * np.cos(t * 0.15)
        
        return {
            "is_tracking": True,
            "target_detected": random.random() > 0.1,  # 90%検出率
            "target_position": {
                "x": int(x),
                "y": int(y),
                "width": random.randint(80, 120),
                "height": random.randint(60, 100)
            },
            "confidence": random.uniform(0.7, 0.95)
        }
```

#### 2.4 Phase 2 成果物

- [ ] 60+APIエンドポイントのモック実装
- [ ] WebSocketリアルタイム通信模擬
- [ ] リアリスティックなデータ生成
- [ ] 状態管理・整合性確保
- [ ] エラー・異常系シナリオ対応

---

### Phase 3: 基本API統合テスト (推定: 20-25時間)

#### 3.1 接続・飛行制御テスト

```python
# tests/integration/mock_backend/test_basic_apis.py
import pytest
import requests
import time

@pytest.mark.integration
@pytest.mark.mock_backend
class TestDroneBasicControl:
    
    def test_health_check(self, mock_backend_server):
        """ヘルスチェックAPI統合テスト"""
        response = requests.get('http://localhost:8000/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        
    def test_connection_flow(self, mock_backend_server):
        """接続フロー統合テスト"""
        # 接続前状態確認
        status_response = requests.get('http://localhost:8000/drone/status')
        assert status_response.status_code == 503  # 未接続
        
        # 接続実行
        connect_response = requests.post('http://localhost:8000/drone/connect')
        assert connect_response.status_code == 200
        assert connect_response.json()['success'] is True
        
        # 接続後状態確認
        status_response = requests.get('http://localhost:8000/drone/status')
        assert status_response.status_code == 200
        assert status_response.json()['connected'] is True
        
    def test_flight_control_sequence(self, mock_backend_server):
        """飛行制御シーケンステスト"""
        # 前提: ドローン接続済み
        requests.post('http://localhost:8000/drone/connect')
        
        # 離陸
        takeoff_response = requests.post('http://localhost:8000/drone/takeoff')
        assert takeoff_response.status_code == 200
        
        # 基本移動
        move_data = {"direction": "forward", "distance": 100}
        move_response = requests.post(
            'http://localhost:8000/drone/move',
            json=move_data
        )
        assert move_response.status_code == 200
        
        # 着陸
        land_response = requests.post('http://localhost:8000/drone/land')
        assert land_response.status_code == 200
        
    @pytest.mark.parametrize("direction,distance", [
        ("forward", 20),    # 最小距離
        ("back", 500),      # 最大距離
        ("left", 250),      # 中間値
        ("right", 250),
        ("up", 100),
        ("down", 100)
    ])
    def test_movement_parameters(self, mock_backend_server, direction, distance):
        """移動パラメータテスト"""
        requests.post('http://localhost:8000/drone/connect')
        requests.post('http://localhost:8000/drone/takeoff')
        
        move_data = {"direction": direction, "distance": distance}
        response = requests.post('http://localhost:8000/drone/move', json=move_data)
        assert response.status_code == 200
        
    def test_invalid_parameters(self, mock_backend_server):
        """無効パラメータエラーテスト"""
        requests.post('http://localhost:8000/drone/connect')
        requests.post('http://localhost:8000/drone/takeoff')
        
        # 無効な方向
        invalid_direction = {"direction": "invalid", "distance": 100}
        response = requests.post('http://localhost:8000/drone/move', json=invalid_direction)
        assert response.status_code == 400
        
        # 距離範囲外
        invalid_distance = {"direction": "forward", "distance": 600}  # 500超過
        response = requests.post('http://localhost:8000/drone/move', json=invalid_distance)
        assert response.status_code == 400
```

#### 3.2 センサー・状態監視テスト

```python
# tests/integration/mock_backend/test_sensor_apis.py
import pytest
import requests

@pytest.mark.integration 
@pytest.mark.mock_backend
class TestSensorIntegration:
    
    def test_sensor_data_structure(self, mock_backend_server):
        """センサーデータ構造確認"""
        # 接続
        requests.post('http://localhost:8000/drone/connect')
        
        # 各センサーAPIの構造確認
        sensors = [
            ('battery', ['battery']),
            ('height', ['height']),
            ('temperature', ['temperature']),
            ('acceleration', ['acceleration']),
            ('velocity', ['velocity']),
            ('attitude', ['attitude'])
        ]
        
        for sensor_name, expected_keys in sensors:
            response = requests.get(f'http://localhost:8000/drone/{sensor_name}')
            assert response.status_code == 200
            
            data = response.json()
            for key in expected_keys:
                assert key in data
                
    def test_sensor_value_ranges(self, mock_backend_server):
        """センサー値範囲確認"""
        requests.post('http://localhost:8000/drone/connect')
        
        # バッテリー値範囲 (0-100%)
        battery_response = requests.get('http://localhost:8000/drone/battery')
        battery_value = battery_response.json()['battery']
        assert 0 <= battery_value <= 100
        
        # 温度値範囲 (0-90℃)
        temp_response = requests.get('http://localhost:8000/drone/temperature')
        temp_value = temp_response.json()['temperature']
        assert 0 <= temp_value <= 90
        
    def test_comprehensive_status(self, mock_backend_server):
        """総合ステータステスト"""
        requests.post('http://localhost:8000/drone/connect')
        
        status_response = requests.get('http://localhost:8000/drone/status')
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        required_fields = [
            'connected', 'battery', 'height', 'temperature',
            'acceleration', 'velocity', 'attitude'
        ]
        
        for field in required_fields:
            assert field in status_data
```

#### 3.3 Phase 3 成果物

- [ ] 基本API統合テスト実装 (39ケース)
- [ ] パラメータ境界値テスト (15ケース)
- [ ] エラーハンドリングテスト (20ケース)
- [ ] 状態遷移テスト (8シーケンス)
- [ ] 実行・レポート機能確認

---

### Phase 4: WebSocket・リアルタイム統合 (推定: 12-15時間)

#### 4.1 WebSocket基本通信テスト

```python
# tests/integration/mock_backend/test_websocket.py
import pytest
import socketio
import time
import asyncio

@pytest.mark.integration
@pytest.mark.mock_backend
@pytest.mark.asyncio
class TestWebSocketIntegration:
    
    async def test_websocket_connection(self, mock_websocket_server):
        """WebSocket接続・切断テスト"""
        client = socketio.AsyncClient()
        
        # 接続
        await client.connect('http://localhost:8001')
        assert client.connected
        
        # 切断
        await client.disconnect()
        assert not client.connected
        
    async def test_realtime_sensor_data(self, mock_websocket_server):
        """リアルタイムセンサーデータ受信テスト"""
        client = socketio.AsyncClient()
        received_data = []
        
        @client.event
        async def sensor_data(data):
            received_data.append(data)
            
        await client.connect('http://localhost:8001')
        
        # センサーデータストリーム要求
        await client.emit('request_sensor_data', {})
        
        # 3秒間データ受信確認
        await asyncio.sleep(3)
        
        assert len(received_data) >= 2  # 最低2回受信
        
        # データ構造確認
        for data in received_data:
            assert 'battery' in data
            assert 'timestamp' in data
            assert isinstance(data['battery'], int)
            
    async def test_tracking_data_stream(self, mock_websocket_server):
        """追跡データストリームテスト"""
        client = socketio.AsyncClient()
        tracking_data = []
        
        @client.event
        async def tracking_update(data):
            tracking_data.append(data)
            
        await client.connect('http://localhost:8001')
        await client.emit('start_tracking', {'target': 'person'})
        
        # 追跡データ受信確認
        await asyncio.sleep(2)
        assert len(tracking_data) > 0
        
        # 追跡データ構造確認
        latest_data = tracking_data[-1]
        assert 'is_tracking' in latest_data
        assert 'target_detected' in latest_data
        
    async def test_websocket_error_handling(self, mock_websocket_server):
        """WebSocketエラーハンドリングテスト"""
        client = socketio.AsyncClient()
        error_received = False
        
        @client.event
        async def error_message(data):
            nonlocal error_received
            error_received = True
            
        await client.connect('http://localhost:8001')
        
        # 無効なイベント送信
        await client.emit('invalid_event', {})
        await asyncio.sleep(1)
        
        # エラー応答確認 (実装によって異なる)
        # assert error_received  # モック実装次第
```

#### 4.2 リアルタイムUI更新テスト

```python
# tests/integration/mock_backend/test_realtime_ui.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.integration
@pytest.mark.ui
class TestRealtimeUIUpdates:
    
    @pytest.fixture
    def browser(self):
        """ブラウザインスタンス"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
        
    def test_sensor_display_updates(self, browser, mock_websocket_server, frontend_server):
        """センサー表示リアルタイム更新テスト"""
        # フロントエンドページアクセス
        browser.get('http://localhost:5001/dashboard')
        
        # WebSocket接続・センサーデータ受信開始
        browser.execute_script("startSensorDataStream();")
        
        # バッテリー表示要素取得
        battery_element = browser.find_element(By.ID, "battery-value")
        initial_value = battery_element.text
        
        # 3秒待機（リアルタイム更新確認）
        WebDriverWait(browser, 5).until(
            lambda d: d.find_element(By.ID, "battery-value").text != initial_value
        )
        
        # 更新された値取得・確認
        updated_value = battery_element.text
        assert updated_value != initial_value
        assert updated_value.isdigit()
        
    def test_tracking_visualization_updates(self, browser, mock_websocket_server, frontend_server):
        """追跡可視化リアルタイム更新テスト"""
        browser.get('http://localhost:5001/tracking')
        
        # 追跡開始
        browser.find_element(By.ID, "start-tracking-btn").click()
        
        # 追跡矩形表示確認
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tracking-box"))
        )
        
        tracking_box = browser.find_element(By.CLASS_NAME, "tracking-box")
        initial_position = tracking_box.get_attribute("style")
        
        # 位置更新確認 (3秒待機)
        time.sleep(3)
        updated_position = tracking_box.get_attribute("style")
        
        # 位置が変化していることを確認
        assert updated_position != initial_position
```

#### 4.3 Phase 4 成果物

- [ ] WebSocket接続・切断テスト
- [ ] リアルタイムデータ配信テスト
- [ ] UI更新統合テスト
- [ ] エラーハンドリング・復旧テスト
- [ ] 複数クライアント同時接続テスト

---

### Phase 5: ファイルアップロード統合 (推定: 8-10時間)

#### 5.1 画像アップロードテスト

```python
# tests/integration/mock_backend/test_file_upload.py
import pytest
import requests
import io
from PIL import Image

@pytest.mark.integration
@pytest.mark.mock_backend
class TestFileUploadIntegration:
    
    @pytest.fixture
    def sample_image(self):
        """テスト用画像生成"""
        img = Image.new('RGB', (640, 480), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
        
    def test_single_image_upload(self, mock_backend_server, sample_image):
        """単一画像アップロードテスト"""
        files = {
            'images': ('test.jpg', sample_image, 'image/jpeg')
        }
        data = {
            'object_name': 'test_object'
        }
        
        response = requests.post(
            'http://localhost:8000/model/train',
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        assert 'task_id' in response.json()
        
    def test_multiple_images_upload(self, mock_backend_server):
        """複数画像アップロードテスト"""
        files = []
        for i in range(3):
            img = Image.new('RGB', (640, 480), color=(i*80, 0, 0))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files.append(('images', (f'test{i}.jpg', img_bytes, 'image/jpeg')))
            
        data = {'object_name': 'multi_test'}
        
        response = requests.post(
            'http://localhost:8000/model/train',
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        
    def test_invalid_file_upload(self, mock_backend_server):
        """無効ファイルアップロードテスト"""
        # 非画像ファイル
        text_file = io.BytesIO(b'This is not an image')
        files = {
            'images': ('test.txt', text_file, 'text/plain')
        }
        data = {'object_name': 'invalid_test'}
        
        response = requests.post(
            'http://localhost:8000/model/train',
            files=files,
            data=data
        )
        
        assert response.status_code == 400
        assert 'error' in response.json()
        
    def test_oversized_file_upload(self, mock_backend_server):
        """サイズ超過ファイルアップロードテスト"""
        # 大きな画像生成 (制限値を超過)
        large_img = Image.new('RGB', (4000, 4000), color='blue')
        img_bytes = io.BytesIO()
        large_img.save(img_bytes, format='JPEG', quality=100)
        img_bytes.seek(0)
        
        files = {
            'images': ('large.jpg', img_bytes, 'image/jpeg')
        }
        data = {'object_name': 'large_test'}
        
        response = requests.post(
            'http://localhost:8000/model/train',
            files=files,
            data=data
        )
        
        assert response.status_code == 413  # Payload Too Large
```

#### 5.2 フロントエンドファイルアップロードテスト

```python
# tests/integration/mock_backend/test_upload_ui.py
import pytest
import os
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.integration
@pytest.mark.ui
class TestUploadUIIntegration:
    
    def test_drag_drop_upload(self, browser, frontend_server):
        """ドラッグ&ドロップアップロードテスト"""
        browser.get('http://localhost:5001/model/training')
        
        # ファイル入力要素取得
        file_input = browser.find_element(By.ID, "file-upload-input")
        
        # テスト画像ファイルパス
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # 簡単な画像生成・保存
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='green')
            img.save(tmp.name)
            tmp_path = tmp.name
            
        try:
            # ファイル選択
            file_input.send_keys(tmp_path)
            
            # ファイル選択確認 
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "file-preview"))
            )
            
            # プレビュー表示確認
            preview_elements = browser.find_elements(By.CLASS_NAME, "file-preview")
            assert len(preview_elements) == 1
            
        finally:
            # 一時ファイル削除
            os.unlink(tmp_path)
            
    def test_upload_progress_display(self, browser, frontend_server, mock_backend_server):
        """アップロード進捗表示テスト"""
        browser.get('http://localhost:5001/model/training')
        
        # オブジェクト名入力
        object_name_input = browser.find_element(By.ID, "object-name-input")
        object_name_input.send_keys("test_object")
        
        # ファイル選択 (前テスト同様)
        # ...
        
        # アップロード開始
        upload_button = browser.find_element(By.ID, "upload-button")
        upload_button.click()
        
        # 進捗バー表示確認
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "progress-bar"))
        )
        
        # 完了メッセージ表示確認
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-success"))
        )
        
    def test_upload_error_handling(self, browser, frontend_server):
        """アップロードエラー処理テスト"""
        browser.get('http://localhost:5001/model/training')
        
        # 無効ファイル選択
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Not an image')
            tmp_path = tmp.name
            
        try:
            file_input = browser.find_element(By.ID, "file-upload-input")
            file_input.send_keys(tmp_path)
            
            # エラーメッセージ表示確認
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            
            error_message = browser.find_element(By.CLASS_NAME, "error-message")
            assert "無効なファイル形式" in error_message.text
            
        finally:
            os.unlink(tmp_path)
```

#### 5.3 Phase 5 成果物

- [ ] 単一・複数ファイルアップロードテスト
- [ ] バリデーション・エラーハンドリングテスト
- [ ] UI統合・進捗表示テスト
- [ ] 境界値・異常系テスト
- [ ] パフォーマンス・安定性確認

---

### Phase 6: 実機統合テスト (推定: 30-40時間)

#### 6.1 実機テスト環境セットアップ

```python
# tests/integration/real_backend/conftest.py
import pytest
import requests
import time
from djitellopy import Tello

@pytest.fixture(scope="session")
def real_backend_url():
    """実機バックエンドURL"""
    return "http://192.168.1.100:8000"  # Raspberry Pi

@pytest.fixture(scope="session") 
def safety_monitor():
    """安全監視システム"""
    class SafetyMonitor:
        def __init__(self):
            self.emergency_stop = False
            self.max_flight_time = 300  # 5分制限
            self.start_time = None
            
        def start_flight_timer(self):
            self.start_time = time.time()
            
        def check_safety(self):
            if self.start_time and time.time() - self.start_time > self.max_flight_time:
                self.trigger_emergency_stop()
                
        def trigger_emergency_stop(self):
            self.emergency_stop = True
            # 実際のドローン緊急停止実行
            tello = Tello()
            tello.emergency()
            
    return SafetyMonitor()

@pytest.fixture
def ensure_drone_connected(real_backend_url):
    """ドローン接続確保"""
    connect_response = requests.post(f"{real_backend_url}/drone/connect")
    assert connect_response.status_code == 200
    
    # 接続確認
    status_response = requests.get(f"{real_backend_url}/drone/status")
    assert status_response.status_code == 200
    assert status_response.json()["connected"] is True
    
    yield
    
    # テスト後: 安全な切断
    try:
        requests.post(f"{real_backend_url}/drone/land")
        time.sleep(2)
        requests.post(f"{real_backend_url}/drone/disconnect")
    except:
        pass  # エラーでも安全を優先
```

#### 6.2 基本実機制御テスト

```python
# tests/integration/real_backend/test_drone_basic.py
import pytest
import requests
import time

@pytest.mark.integration
@pytest.mark.real_backend
@pytest.mark.requires_hardware
class TestRealDroneBasic:
    
    def test_real_connection_cycle(self, real_backend_url, safety_monitor):
        """実機接続・切断サイクルテスト"""
        # 接続
        connect_response = requests.post(f"{real_backend_url}/drone/connect")
        assert connect_response.status_code == 200
        
        # 状態確認
        status_response = requests.get(f"{real_backend_url}/drone/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["connected"] is True
        assert isinstance(status_data["battery"], int)
        assert 0 <= status_data["battery"] <= 100
        
        # 切断
        disconnect_response = requests.post(f"{real_backend_url}/drone/disconnect")
        assert disconnect_response.status_code == 200
        
    def test_real_flight_basic(self, real_backend_url, ensure_drone_connected, safety_monitor):
        """実機基本飛行テスト"""
        safety_monitor.start_flight_timer()
        
        try:
            # 離陸
            takeoff_response = requests.post(f"{real_backend_url}/drone/takeoff")
            assert takeoff_response.status_code == 200
            
            # 安定化待機
            time.sleep(3)
            safety_monitor.check_safety()
            
            # 高度確認
            height_response = requests.get(f"{real_backend_url}/drone/height")
            assert height_response.status_code == 200
            height = height_response.json()["height"]
            assert height > 50  # 離陸していることを確認
            
            # 短時間ホバリング
            time.sleep(2)
            safety_monitor.check_safety()
            
        finally:
            # 必ず着陸
            land_response = requests.post(f"{real_backend_url}/drone/land")
            assert land_response.status_code == 200
            
            # 着陸確認
            time.sleep(3)
            height_response = requests.get(f"{real_backend_url}/drone/height")
            final_height = height_response.json()["height"]
            assert final_height < 10  # 着陸していることを確認
            
    def test_real_movement_control(self, real_backend_url, ensure_drone_connected, safety_monitor):
        """実機移動制御テスト"""
        safety_monitor.start_flight_timer()
        
        try:
            # 離陸
            requests.post(f"{real_backend_url}/drone/takeoff")
            time.sleep(3)
            
            # 前進移動
            move_data = {"direction": "forward", "distance": 50}
            move_response = requests.post(
                f"{real_backend_url}/drone/move",
                json=move_data
            )
            assert move_response.status_code == 200
            
            # 移動完了待機
            time.sleep(2)
            safety_monitor.check_safety()
            
            # 元位置復帰
            return_data = {"direction": "back", "distance": 50}
            return_response = requests.post(
                f"{real_backend_url}/drone/move", 
                json=return_data
            )
            assert return_response.status_code == 200
            time.sleep(2)
            
        finally:
            requests.post(f"{real_backend_url}/drone/land")
            time.sleep(3)
```

#### 6.3 実機追跡・E2Eテスト

```python
# tests/integration/real_backend/test_tracking_e2e.py
import pytest
import requests
import time

@pytest.mark.integration
@pytest.mark.real_backend
@pytest.mark.requires_hardware
@pytest.mark.slow
class TestRealTrackingE2E:
    
    def test_end_to_end_workflow(self, real_backend_url, ensure_drone_connected, safety_monitor):
        """実機E2Eワークフローテスト"""
        safety_monitor.start_flight_timer()
        
        try:
            # 1. カメラストリーミング開始
            stream_response = requests.post(f"{real_backend_url}/camera/stream/start")
            assert stream_response.status_code == 200
            time.sleep(2)
            
            # 2. 追跡開始
            tracking_data = {
                "target_object": "person",
                "tracking_mode": "center"
            }
            track_response = requests.post(
                f"{real_backend_url}/tracking/start",
                json=tracking_data
            )
            assert track_response.status_code == 200
            
            # 3. 離陸
            requests.post(f"{real_backend_url}/drone/takeoff")
            time.sleep(3)
            
            # 4. 追跡状態監視 (30秒間)
            for i in range(6):  # 5秒間隔で6回確認
                safety_monitor.check_safety()
                
                status_response = requests.get(f"{real_backend_url}/tracking/status")
                assert status_response.status_code == 200
                
                tracking_status = status_response.json()
                print(f"追跡状態 ({i+1}/6): {tracking_status}")
                
                # 追跡中であることを確認
                assert tracking_status["is_tracking"] is True
                
                time.sleep(5)
                
                if safety_monitor.emergency_stop:
                    break
            
            # 5. 追跡停止
            stop_response = requests.post(f"{real_backend_url}/tracking/stop")
            assert stop_response.status_code == 200
            
        finally:
            # 6. 安全な終了処理
            try:
                requests.post(f"{real_backend_url}/tracking/stop")
                requests.post(f"{real_backend_url}/drone/land")
                time.sleep(3)
                requests.post(f"{real_backend_url}/camera/stream/stop")
            except:
                pass  # エラーでも継続
                
    def test_model_training_integration(self, real_backend_url):
        """実機モデル訓練統合テスト"""
        # 訓練用画像準備
        import io
        from PIL import Image
        
        images = []
        for i in range(5):  # 最低5枚必要
            img = Image.new('RGB', (640, 480), color=(i*50, 0, 0))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            images.append(('images', (f'train{i}.jpg', img_bytes, 'image/jpeg')))
            
        data = {'object_name': 'test_real_object'}
        
        # モデル訓練開始
        train_response = requests.post(
            f"{real_backend_url}/model/train",
            files=images,
            data=data
        )
        
        assert train_response.status_code == 200
        task_id = train_response.json()["task_id"]
        
        # 訓練完了待機（タイムアウト: 5分）
        max_wait = 300  # 5分
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # モデル一覧確認
            models_response = requests.get(f"{real_backend_url}/model/list")
            assert models_response.status_code == 200
            
            models = models_response.json()["models"]
            trained_model = next(
                (m for m in models if m["name"] == "test_real_object"), 
                None
            )
            
            if trained_model:
                print(f"訓練完了: {trained_model}")
                assert trained_model["accuracy"] > 0
                break
                
            time.sleep(10)  # 10秒間隔で確認
        else:
            pytest.fail("モデル訓練がタイムアウトしました")
```

#### 6.4 Phase 6 成果物

- [ ] 実機安全プロトコル実装
- [ ] 基本実機制御テスト (10ケース)
- [ ] 実機センサー・テレメトリテスト (8ケース)
- [ ] 実機追跡・E2Eワークフローテスト (5ケース)
- [ ] 実機モデル訓練統合テスト (3ケース)

---

## 2. 実行・デプロイメント

### 2.1 テスト実行コマンド

```bash
# 環境準備
cd frontend/admin
pip install -r test_requirements.txt

# モックバックエンドテストのみ
pytest tests/integration/mock_backend/ -v -m "integration and mock_backend"

# WebSocketテストのみ
pytest tests/integration/mock_backend/test_websocket.py -v

# 実機テスト（安全確保必須）
pytest tests/integration/real_backend/ -v -m "integration and real_backend" --tb=short

# 全統合テスト（実機除外）
pytest tests/integration/ -v -m "integration and not requires_hardware"

# カバレッジ付き実行
pytest tests/integration/mock_backend/ --cov=. --cov-report=html

# 並行実行（モックテストのみ）
pytest tests/integration/mock_backend/ -n 4

# 継続実行（CI/CD）
pytest tests/integration/ -v --junitxml=test_results.xml --html=test_report.html
```

### 2.2 CI/CD統合

```yaml
# .github/workflows/integration_tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  mock-integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd frontend/admin
          pip install -r test_requirements.txt
          
      - name: Start mock servers
        run: |
          cd frontend/admin
          python tests/mocks/servers/mock_backend.py &
          python tests/mocks/servers/websocket_mock.py &
          sleep 5
          
      - name: Run mock backend integration tests
        run: |
          cd frontend/admin
          pytest tests/integration/mock_backend/ -v --tb=short --junitxml=mock_results.xml
          
      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: mock-test-results
          path: frontend/admin/mock_results.xml
          
  real-integration-tests:
    runs-on: self-hosted  # 実機環境必要
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      # 実機テスト実行（安全環境でのみ）
      - name: Run real backend integration tests
        run: |
          cd frontend/admin
          pytest tests/integration/real_backend/ -v --tb=short -m "not slow"
```

### 2.3 実行時間・リソース目安

| テスト種別 | 実行時間 | CPU使用率 | メモリ使用量 | 備考 |
|:---|:---|:---|:---|:---|
| モック基本API | 5-10分 | 30-50% | 200-500MB | 並行実行可能 |
| WebSocket通信 | 3-5分 | 20-40% | 100-300MB | ネットワーク依存 |
| ファイルアップロード | 2-3分 | 40-60% | 300-600MB | ディスクI/O集約 |
| 実機基本制御 | 15-30分 | 10-30% | 100-200MB | ハードウェア待機 |
| 実機E2Eワークフロー | 30-60分 | 20-50% | 200-500MB | 総合的負荷 |

---

## 3. 成功基準・完了条件

### 3.1 定量的成功基準

- **APIカバレッジ**: 60+エンドポイント 100%
- **エラーシナリオ**: 30+パターン 95%以上
- **WebSocket機能**: 全イベント種別 100%
- **実機制御**: 基本機能 90%以上
- **テスト成功率**: 全体 95%以上

### 3.2 定性的成功基準

- **安全性**: 実機テスト中の事故・トラブル 0件
- **信頼性**: 継続実行での安定性確保
- **保守性**: 明確な文書化・コード品質
- **拡張性**: 新機能追加時の容易性

### 3.3 完了チェックリスト

- [ ] 全6フェーズの実装完了
- [ ] テスト実行・成功率95%以上達成
- [ ] CI/CDパイプライン統合完了
- [ ] 実機テスト安全プロトコル確立
- [ ] ドキュメント整備・チーム共有完了

---

この実装ロードマップに基づき、段階的で確実なフェーズ3結合テストの実現を図ります。