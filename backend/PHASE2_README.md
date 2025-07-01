# Phase 2: Enhanced Drone Control & Camera System

## 概要

Phase 2 では、フェーズ1で構築した基盤を拡張し、包括的なドローン制御とカメラ機能を実装しました。WebSocketによるリアルタイム通信、高度なカメラストリーミング、統合されたテストスイートを提供します。

## 📋 新機能

### 🔌 WebSocket サポート
- **リアルタイム通信**: `/ws` エンドポイントでWebSocket接続
- **ドローン状態購読**: 特定ドローンの状態変化をリアルタイム受信
- **自動状態ブロードキャスト**: 1秒間隔での状態更新配信
- **接続管理**: 複数クライアント対応、自動切断処理

### 📹 高度なカメラシステム
- **仮想カメラストリーム**: 既存VirtualCameraStreamとの完全統合
- **動的追跡オブジェクト**: 人物、車両、ボールなど複数タイプ対応
- **リアルタイム写真撮影**: Base64エンコード済み高品質画像
- **並行ストリーミング**: 複数ドローンの同時カメラ制御

### 🚁 強化されたドローン制御
- **精密な移動制御**: 20-500cm範囲での正確な位置制御
- **滑らかな回転**: 1-360度の細かい角度調整
- **リアルタイム状態監視**: バッテリー、高度、姿勢情報の連続取得
- **安全機能**: 緊急停止、衝突検出、バッテリー監視

## 🏗️ アーキテクチャ

```
backend/api_server/
├── main.py                    # FastAPI app + WebSocket endpoint
├── api/
│   ├── drones.py             # Enhanced drone control APIs
│   └── websocket.py          # WebSocket message handling
├── core/
│   ├── drone_manager.py      # Core drone management + camera integration
│   └── camera_service.py     # Camera streaming service
├── models/
│   ├── drone_models.py       # Pydantic models for drone data
│   └── common_models.py      # Shared response models
└── tests/
    ├── test_websocket_api.py      # WebSocket functionality tests
    ├── test_camera_service.py     # Camera service tests
    ├── test_enhanced_drone_api.py # Enhanced API tests
    └── test_phase2_performance.py # Performance benchmarks
```

## 📡 WebSocket API

### 接続
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### メッセージ形式
```json
// ドローン購読
{
  "type": "subscribe_drone",
  "drone_id": "drone_001"
}

// ドローン状態取得
{
  "type": "get_drone_status", 
  "drone_id": "drone_001"
}

// Ping
{
  "type": "ping"
}
```

### レスポンス例
```json
// ドローン状態更新
{
  "type": "drone_status_update",
  "drone_id": "drone_001",
  "status": {
    "connection_status": "connected",
    "flight_status": "flying",
    "battery_level": 85,
    "height": 150,
    "attitude": {"pitch": 0.0, "roll": 0.0, "yaw": 45.0}
  },
  "timestamp": "2023-01-01T12:00:00Z"
}
```

## 📸 カメラ API

### ストリーミング制御
```bash
# カメラストリーミング開始
POST /api/drones/{droneId}/camera/stream/start

# カメラストリーミング停止  
POST /api/drones/{droneId}/camera/stream/stop

# 写真撮影
POST /api/drones/{droneId}/camera/photo
```

### 写真レスポンス例
```json
{
  "id": "photo_001",
  "filename": "drone_photo_20230101_120000.jpg",
  "path": "/photos/drone_photo_20230101_120000.jpg",
  "timestamp": "2023-01-01T12:00:00Z",
  "drone_id": "drone_001",
  "metadata": {
    "resolution": "640x480",
    "format": "JPEG",
    "size_bytes": 245760,
    "base64_data": "iVBORw0KGgoAAAANSUhEUgAAA..."
  }
}
```

## 🧪 テスト

### テスト実行
```bash
# 全テスト実行
pytest backend/tests/ -v

# WebSocketテスト
pytest backend/tests/test_websocket_api.py -v

# カメラテスト
pytest backend/tests/test_camera_service.py -v

# パフォーマンステスト
pytest backend/tests/test_phase2_performance.py -v

# カバレッジレポート
pytest backend/tests/ --cov=backend/api_server --cov-report=html
```

### パフォーマンス指標
- **WebSocket接続**: 10接続で5秒未満
- **カメラストリーム起動**: 2秒未満  
- **写真撮影**: 0.5秒未満/枚
- **API レスポンス**: 0.1秒未満（平均）
- **メモリ使用量**: 100リクエストで20MB未満の増加

## 🚀 使用方法

### 1. サーバー起動
```bash
cd backend
pip install -r requirements.txt
python start_api_server.py
```

### 2. WebSocket クライアント接続
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  // ドローン状態購読
  ws.send(JSON.stringify({
    type: 'subscribe_drone',
    drone_id: 'drone_001'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### 3. カメラ制御ワークフロー
```bash
# 1. ドローン接続
curl -X POST http://localhost:8000/api/drones/drone_001/connect

# 2. カメラストリーミング開始
curl -X POST http://localhost:8000/api/drones/drone_001/camera/stream/start

# 3. 写真撮影
curl -X POST http://localhost:8000/api/drones/drone_001/camera/photo

# 4. カメラストリーミング停止
curl -X POST http://localhost:8000/api/drones/drone_001/camera/stream/stop

# 5. ドローン切断
curl -X POST http://localhost:8000/api/drones/drone_001/disconnect
```

## 🔧 設定

### 環境変数
```bash
# ログレベル設定
export LOG_LEVEL=INFO

# カメラ設定
export CAMERA_WIDTH=640
export CAMERA_HEIGHT=480
export CAMERA_FPS=30

# WebSocket設定
export WS_HEARTBEAT_INTERVAL=1.0
```

### VirtualCameraStream設定
```python
# カスタム追跡オブジェクト追加
object_config = {
    "type": "person",
    "position": [200, 150],
    "size": [40, 80], 
    "color": [255, 0, 0],
    "movement_pattern": "linear",
    "movement_speed": 30.0
}
```

## 📈 監視とデバッグ

### ヘルスチェック
```bash
# API サーバー状態
curl http://localhost:8000/health

# ドローン状態
curl http://localhost:8000/api/drones

# ドローン詳細状態
curl http://localhost:8000/api/drones/drone_001/status
```

### ログ確認
```bash
# アプリケーションログ
tail -f /var/log/drone_api.log

# WebSocketログ  
grep "WebSocket" /var/log/drone_api.log

# カメラログ
grep "Camera" /var/log/drone_api.log
```

## 🔍 トラブルシューティング

### よくある問題

**WebSocket接続エラー**
```
Error: WebSocket connection failed
Solution: ポート8000が使用可能か確認、CORSホワイトリスト確認
```

**カメラストリーム開始失敗**
```
Error: Failed to start camera stream
Solution: ドローンが接続されているか確認、既存ストリームの停止
```

**メモリリーク**
```
Error: Memory usage increasing
Solution: 不要なストリーム停止、ガベージコレクション確認
```

### デバッグコマンド
```bash
# デバッグモード起動
LOG_LEVEL=DEBUG python start_api_server.py

# メモリ使用量監視
python -m memory_profiler start_api_server.py

# パフォーマンス測定
python -m cProfile start_api_server.py
```

## 🚦 次のステップ

Phase 2 の完了により、以下の機能が利用可能になりました：

✅ **リアルタイム通信**: WebSocketベースの双方向通信  
✅ **高度なカメラ機能**: ストリーミング、写真撮影、追跡オブジェクト  
✅ **包括的テスト**: 単体、統合、パフォーマンステスト  
✅ **プロダクション対応**: 堅牢なエラーハンドリング、ログ、監視  

次のPhase 3では、以下の実装を予定：
- ビジョンAPI（物体検出・追跡）
- モデル管理API（学習、デプロイ）
- ダッシュボードAPI（システム監視）
- 高度な非同期ジョブ処理

## 📚 参考

- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [VirtualCameraStream Documentation](../src/core/virtual_camera.py)
- [DroneSimulator Integration](../src/core/drone_simulator.py)