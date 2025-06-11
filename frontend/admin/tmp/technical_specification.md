# 管理用フロントエンド 技術仕様書

## 1. システム構成

### 1.1 アプリケーション構造

```
frontend/admin/
├── app.py                    # メインアプリケーション
├── config.py                 # 環境設定
├── requirements.txt          # 依存関係
├── blueprints/               # 機能別ブループリント
│   ├── __init__.py
│   ├── dashboard.py          # ダッシュボード
│   ├── drone_control.py      # ドローン制御
│   ├── model_training.py     # モデル訓練
│   ├── tracking.py           # 追跡制御
│   └── settings.py           # 設定管理
├── services/                 # バックエンド連携サービス
│   ├── __init__.py
│   ├── api_client.py         # REST API クライアント
│   ├── websocket_service.py  # WebSocket サービス
│   └── file_service.py       # ファイル操作サービス
├── models/                   # データモデル
│   ├── __init__.py
│   ├── drone_state.py        # ドローン状態モデル
│   ├── tracking_state.py     # 追跡状態モデル
│   └── model_info.py         # AIモデル情報
├── utils/                    # ユーティリティ
│   ├── __init__.py
│   ├── validators.py         # バリデーション
│   ├── formatters.py         # データフォーマット
│   └── exceptions.py         # カスタム例外
├── templates/                # HTMLテンプレート
│   ├── base.html            # 基底テンプレート
│   ├── index.html           # ダッシュボード
│   ├── drone_control.html   # ドローン制御
│   ├── model_training.html  # モデル訓練
│   ├── tracking.html        # 追跡制御
│   └── settings.html        # 設定
└── static/                  # 静的ファイル
    ├── css/
    │   ├── main.css
    │   └── components.css
    ├── js/
    │   ├── main.js
    │   ├── drone-control.js
    │   ├── model-training.js
    │   ├── tracking.js
    │   └── websocket.js
    └── images/
```

## 2. API設計仕様

### 2.1 バックエンドAPI統合

#### 2.1.1 APIクライアント基底クラス

```python
# services/api_client.py
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from utils.exceptions import APIException

class DroneAPIClient:
    def __init__(self, base_url: str = "http://192.168.1.100:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=10)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """共通リクエスト処理"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise APIException(
                        message=error_data.get('error', 'API Error'),
                        code=error_data.get('code', 'UNKNOWN_ERROR'),
                        status_code=response.status
                    )
                return await response.json()
        except aiohttp.ClientError as e:
            raise APIException(f"Network error: {str(e)}", "NETWORK_ERROR")
    
    # ドローン制御API
    async def connect_drone(self) -> Dict[str, Any]:
        return await self._request('POST', '/drone/connect')
    
    async def disconnect_drone(self) -> Dict[str, Any]:
        return await self._request('POST', '/drone/disconnect')
    
    async def takeoff(self) -> Dict[str, Any]:
        return await self._request('POST', '/drone/takeoff')
    
    async def land(self) -> Dict[str, Any]:
        return await self._request('POST', '/drone/land')
    
    async def emergency_stop(self) -> Dict[str, Any]:
        return await self._request('POST', '/drone/emergency')
    
    async def move_drone(self, direction: str, distance: int) -> Dict[str, Any]:
        data = {"direction": direction, "distance": distance}
        return await self._request('POST', '/drone/move', json=data)
    
    async def rotate_drone(self, direction: str, angle: int) -> Dict[str, Any]:
        data = {"direction": direction, "angle": angle}
        return await self._request('POST', '/drone/rotate', json=data)
    
    # センサー情報取得
    async def get_drone_status(self) -> Dict[str, Any]:
        return await self._request('GET', '/drone/status')
    
    async def get_battery_level(self) -> Dict[str, Any]:
        return await self._request('GET', '/drone/battery')
    
    # カメラ制御
    async def start_camera_stream(self) -> Dict[str, Any]:
        return await self._request('POST', '/camera/stream/start')
    
    async def stop_camera_stream(self) -> Dict[str, Any]:
        return await self._request('POST', '/camera/stream/stop')
    
    # 追跡制御
    async def start_tracking(self, target_object: str, tracking_mode: str = "center") -> Dict[str, Any]:
        data = {"target_object": target_object, "tracking_mode": tracking_mode}
        return await self._request('POST', '/tracking/start', json=data)
    
    async def stop_tracking(self) -> Dict[str, Any]:
        return await self._request('POST', '/tracking/stop')
    
    async def get_tracking_status(self) -> Dict[str, Any]:
        return await self._request('GET', '/tracking/status')
    
    # モデル管理
    async def train_model(self, object_name: str, image_files: list) -> Dict[str, Any]:
        data = aiohttp.FormData()
        data.add_field('object_name', object_name)
        for i, image_file in enumerate(image_files):
            data.add_field('images', image_file, filename=f'image_{i}.jpg')
        return await self._request('POST', '/model/train', data=data)
    
    async def list_models(self) -> Dict[str, Any]:
        return await self._request('GET', '/model/list')
```

### 2.2 WebSocket/Socket.IO実装

#### 2.2.1 リアルタイム通信サービス

```python
# services/websocket_service.py
from flask_socketio import SocketIO, emit
import asyncio
from threading import Thread
import time

class RealtimeService:
    def __init__(self, socketio: SocketIO, api_client: DroneAPIClient):
        self.socketio = socketio
        self.api_client = api_client
        self.is_monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """センサーデータ監視開始"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = Thread(target=self._monitor_loop)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """センサーデータ監視停止"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """監視ループ（バックグラウンドスレッド）"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.is_monitoring:
            try:
                # ドローン状態取得
                status_task = loop.create_task(self._get_status_data())
                tracking_task = loop.create_task(self._get_tracking_data())
                
                status_data, tracking_data = loop.run_until_complete(
                    asyncio.gather(status_task, tracking_task, return_exceptions=True)
                )
                
                # クライアントに送信
                if not isinstance(status_data, Exception):
                    self.socketio.emit('drone_status', status_data)
                
                if not isinstance(tracking_data, Exception):
                    self.socketio.emit('tracking_status', tracking_data)
                
            except Exception as e:
                self.socketio.emit('error', {'message': str(e)})
            
            time.sleep(1)  # 1秒間隔
        
        loop.close()
    
    async def _get_status_data(self):
        async with self.api_client as client:
            return await client.get_drone_status()
    
    async def _get_tracking_data(self):
        async with self.api_client as client:
            return await client.get_tracking_status()
```

## 3. フロントエンド実装

### 3.1 JavaScript/WebSocket クライアント

```javascript
// static/js/websocket.js
class DroneWebSocketClient {
    constructor() {
        this.socket = io();
        this.isConnected = false;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('drone_status', (data) => {
            this.updateDroneStatus(data);
        });
        
        this.socket.on('tracking_status', (data) => {
            this.updateTrackingStatus(data);
        });
        
        this.socket.on('error', (data) => {
            this.showError(data.message);
        });
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? '接続中' : '切断';
            statusElement.className = connected ? 'status-connected' : 'status-disconnected';
        }
    }
    
    updateDroneStatus(data) {
        // バッテリー表示更新
        const batteryElement = document.getElementById('battery-level');
        if (batteryElement && data.battery !== undefined) {
            batteryElement.textContent = `${data.battery}%`;
            batteryElement.className = data.battery < 20 ? 'battery-low' : 'battery-normal';
        }
        
        // 高度表示更新
        const heightElement = document.getElementById('height-display');
        if (heightElement && data.height !== undefined) {
            heightElement.textContent = `${data.height}cm`;
        }
        
        // 温度表示更新
        const tempElement = document.getElementById('temperature-display');
        if (tempElement && data.temperature !== undefined) {
            tempElement.textContent = `${data.temperature}°C`;
        }
    }
    
    updateTrackingStatus(data) {
        const trackingElement = document.getElementById('tracking-status');
        if (trackingElement) {
            trackingElement.textContent = data.is_tracking ? '追跡中' : '停止中';
            trackingElement.className = data.is_tracking ? 'tracking-active' : 'tracking-inactive';
        }
        
        if (data.target_detected) {
            const positionElement = document.getElementById('target-position');
            if (positionElement && data.target_position) {
                positionElement.textContent = 
                    `X:${data.target_position.x}, Y:${data.target_position.y}`;
            }
        }
    }
    
    showError(message) {
        // Bootstrap Toastを使用してエラー表示
        const toastContainer = document.getElementById('toast-container');
        const toastHtml = `
            <div class="toast" role="alert">
                <div class="toast-header">
                    <strong class="me-auto">エラー</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            </div>
        `;
        toastContainer.innerHTML = toastHtml;
        const toast = new bootstrap.Toast(toastContainer.querySelector('.toast'));
        toast.show();
    }
    
    startMonitoring() {
        this.socket.emit('start_monitoring');
    }
    
    stopMonitoring() {
        this.socket.emit('stop_monitoring');
    }
}

// グローバルインスタンス
const droneWS = new DroneWebSocketClient();
```

### 3.2 ドローン制御UI実装

```javascript
// static/js/drone-control.js
class DroneController {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.isConnected = false;
        this.isFlying = false;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 接続/切断ボタン
        document.getElementById('btn-connect').addEventListener('click', () => {
            this.toggleConnection();
        });
        
        // 離陸/着陸ボタン
        document.getElementById('btn-takeoff').addEventListener('click', () => {
            this.takeoff();
        });
        
        document.getElementById('btn-land').addEventListener('click', () => {
            this.land();
        });
        
        // 緊急停止ボタン
        document.getElementById('btn-emergency').addEventListener('click', () => {
            this.emergencyStop();
        });
        
        // 移動制御ボタン
        const directions = ['up', 'down', 'left', 'right', 'forward', 'back'];
        directions.forEach(direction => {
            document.getElementById(`btn-move-${direction}`).addEventListener('click', () => {
                const distance = parseInt(document.getElementById('move-distance').value) || 50;
                this.move(direction, distance);
            });
        });
        
        // 回転制御ボタン
        document.getElementById('btn-rotate-cw').addEventListener('click', () => {
            const angle = parseInt(document.getElementById('rotate-angle').value) || 90;
            this.rotate('clockwise', angle);
        });
        
        document.getElementById('btn-rotate-ccw').addEventListener('click', () => {
            const angle = parseInt(document.getElementById('rotate-angle').value) || 90;
            this.rotate('counter_clockwise', angle);
        });
    }
    
    async toggleConnection() {
        try {
            if (this.isConnected) {
                await this.disconnect();
            } else {
                await this.connect();
            }
        } catch (error) {
            this.showError(`接続操作に失敗しました: ${error.message}`);
        }
    }
    
    async connect() {
        const response = await fetch('/api/drone/connect', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            this.isConnected = true;
            this.updateConnectionUI(true);
            this.showSuccess('ドローンに接続しました');
        } else {
            throw new Error(data.message);
        }
    }
    
    async disconnect() {
        const response = await fetch('/api/drone/disconnect', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            this.isConnected = false;
            this.isFlying = false;
            this.updateConnectionUI(false);
            this.updateFlightUI(false);
            this.showSuccess('ドローンから切断しました');
        } else {
            throw new Error(data.message);
        }
    }
    
    async takeoff() {
        if (!this.isConnected) {
            this.showError('ドローンが接続されていません');
            return;
        }
        
        try {
            const response = await fetch('/api/drone/takeoff', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.isFlying = true;
                this.updateFlightUI(true);
                this.showSuccess('離陸しました');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`離陸に失敗しました: ${error.message}`);
        }
    }
    
    async land() {
        if (!this.isFlying) {
            this.showError('ドローンが飛行していません');
            return;
        }
        
        try {
            const response = await fetch('/api/drone/land', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.isFlying = false;
                this.updateFlightUI(false);
                this.showSuccess('着陸しました');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`着陸に失敗しました: ${error.message}`);
        }
    }
    
    async emergencyStop() {
        try {
            const response = await fetch('/api/drone/emergency', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.isFlying = false;
                this.updateFlightUI(false);
                this.showWarning('緊急停止しました');
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`緊急停止に失敗しました: ${error.message}`);
        }
    }
    
    async move(direction, distance) {
        if (!this.isFlying) {
            this.showError('ドローンが飛行していません');
            return;
        }
        
        try {
            const response = await fetch('/api/drone/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction, distance })
            });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`${direction}方向に${distance}cm移動しました`);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`移動に失敗しました: ${error.message}`);
        }
    }
    
    async rotate(direction, angle) {
        if (!this.isFlying) {
            this.showError('ドローンが飛行していません');
            return;
        }
        
        try {
            const response = await fetch('/api/drone/rotate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction, angle })
            });
            const data = await response.json();
            
            if (data.success) {
                const dirText = direction === 'clockwise' ? '時計回り' : '反時計回り';
                this.showSuccess(`${dirText}に${angle}度回転しました`);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            this.showError(`回転に失敗しました: ${error.message}`);
        }
    }
    
    updateConnectionUI(connected) {
        const connectBtn = document.getElementById('btn-connect');
        const statusText = document.getElementById('connection-status-text');
        
        connectBtn.textContent = connected ? '切断' : '接続';
        connectBtn.className = connected ? 'btn btn-danger' : 'btn btn-success';
        statusText.textContent = connected ? '接続中' : '切断';
        statusText.className = connected ? 'text-success' : 'text-danger';
        
        // 制御ボタンの有効/無効切り替え
        const controlButtons = document.querySelectorAll('.control-btn');
        controlButtons.forEach(btn => {
            btn.disabled = !connected;
        });
    }
    
    updateFlightUI(flying) {
        const takeoffBtn = document.getElementById('btn-takeoff');
        const landBtn = document.getElementById('btn-land');
        const moveButtons = document.querySelectorAll('.move-btn');
        
        takeoffBtn.disabled = flying;
        landBtn.disabled = !flying;
        
        moveButtons.forEach(btn => {
            btn.disabled = !flying;
        });
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showWarning(message) {
        this.showToast(message, 'warning');
    }
    
    showToast(message, type) {
        const toastContainer = document.getElementById('toast-container');
        const bgClass = type === 'success' ? 'bg-success' : 
                       type === 'error' ? 'bg-danger' : 'bg-warning';
        
        const toastHtml = `
            <div class="toast ${bgClass} text-white" role="alert">
                <div class="toast-header">
                    <strong class="me-auto">${type.toUpperCase()}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">${message}</div>
            </div>
        `;
        
        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHtml;
        toastContainer.appendChild(toastElement.firstElementChild);
        
        const toast = new bootstrap.Toast(toastContainer.lastElementChild);
        toast.show();
        
        // 5秒後に自動削除
        setTimeout(() => {
            toastElement.remove();
        }, 5000);
    }
}

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', () => {
    const droneController = new DroneController();
});
```

## 4. データ検証・セキュリティ

### 4.1 入力検証

```python
# utils/validators.py
from typing import Any, Dict, List
import re

class InputValidator:
    @staticmethod
    def validate_distance(distance: int) -> bool:
        """移動距離の検証 (20-500cm)"""
        return 20 <= distance <= 500
    
    @staticmethod
    def validate_angle(angle: int) -> bool:
        """回転角度の検証 (1-360度)"""
        return 1 <= angle <= 360
    
    @staticmethod
    def validate_direction(direction: str, valid_directions: List[str]) -> bool:
        """方向の検証"""
        return direction in valid_directions
    
    @staticmethod
    def validate_object_name(name: str) -> bool:
        """オブジェクト名の検証"""
        return bool(re.match(r'^[a-zA-Z0-9_-]{1,50}$', name))
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
        """ファイルサイズの検証"""
        return file_size <= (max_size_mb * 1024 * 1024)
    
    @staticmethod
    def validate_image_format(filename: str) -> bool:
        """画像フォーマットの検証"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
```

### 4.2 エラーハンドリング

```python
# utils/exceptions.py
class DroneAPIException(Exception):
    """ドローンAPI関連例外"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(Exception):
    """バリデーション例外"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NetworkException(DroneAPIException):
    """ネットワーク関連例外"""
    def __init__(self, message: str):
        super().__init__(message, "NETWORK_ERROR", 503)
```

## 5. 設定管理

### 5.1 環境設定

```python
# config.py
import os
from typing import Dict, Any

class Config:
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # バックエンドAPI設定
    BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://192.168.1.100:8000')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '10'))
    
    # ファイルアップロード設定
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '50')) * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}
    
    # WebSocket設定
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # モニタリング設定
    SENSOR_UPDATE_INTERVAL = float(os.environ.get('SENSOR_UPDATE_INTERVAL', '1.0'))
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {k: v for k, v in Config.__dict__.items() if not k.startswith('_')}

class DevelopmentConfig(Config):
    DEBUG = True
    BACKEND_API_URL = 'http://localhost:8000'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

# 環境別設定選択
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

この技術仕様書に基づいて実装を進めることで、堅牢で保守性の高い管理用フロントエンドシステムを構築できます。