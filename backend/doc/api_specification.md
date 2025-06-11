# API仕様書

## 概要

MFG Drone Backend APIの詳細な仕様を定義します。OpenAPI 3.0.3準拠の完全なREST API仕様です。

## APIエンドポイント概要

```mermaid
graph TB
    subgraph "システム管理"
        Health[GET /health]
        Root[GET /]
    end
    
    subgraph "ドローン制御"
        Connect[POST /drone/connect]
        Disconnect[POST /drone/disconnect]
        Takeoff[POST /drone/takeoff]
        Land[POST /drone/land]
        Emergency[POST /drone/emergency]
    end
    
    subgraph "移動制御"
        Move[POST /drone/move/{direction}]
        Rotate[POST /drone/rotate/{direction}]
        GoTo[POST /drone/go_to]
        Curve[POST /drone/curve]
    end
    
    subgraph "カメラ・センサー"
        StreamStart[POST /drone/camera/stream/start]
        StreamStop[POST /drone/camera/stream/stop]
        Photo[POST /drone/camera/photo]
        Battery[GET /drone/sensors/battery]
        Sensors[GET /drone/sensors/all]
    end
    
    subgraph "高度機能"
        TrackStart[POST /drone/tracking/start]
        TrackStop[POST /drone/tracking/stop]
        ModelTrain[POST /drone/models/train]
        MissionPad[POST /drone/mission_pad/enable]
    end
    
    classDef system fill:#e8f5e8
    classDef control fill:#e3f2fd
    classDef movement fill:#fff3e0
    classDef media fill:#ffecb3
    classDef advanced fill:#f3e5f5
    
    class Health,Root system
    class Connect,Disconnect,Takeoff,Land,Emergency control
    class Move,Rotate,GoTo,Curve movement
    class StreamStart,StreamStop,Photo,Battery,Sensors media
    class TrackStart,TrackStop,ModelTrain,MissionPad advanced
```

## ベースURL・認証

```yaml
Base URL: http://localhost:8000 (開発環境)
Base URL: http://192.168.1.100:8000 (本番環境)

認証方式: 現在は認証なし（将来的にJWT実装予定）
Content-Type: application/json
```

## 共通レスポンス形式

### 成功レスポンス

```json
{
  "success": true,
  "message": "操作が正常に完了しました"
}
```

### エラーレスポンス

```json
{
  "error": "エラーメッセージ",
  "code": "ERROR_CODE",
  "details": {
    "additional_info": "追加の詳細情報"
  }
}
```

### エラーコード一覧

| コード | 説明 | HTTPステータス |
|-------|------|---------------|
| DRONE_NOT_CONNECTED | ドローン未接続 | 400 |
| DRONE_CONNECTION_FAILED | 接続失敗 | 500 |
| INVALID_PARAMETER | 無効なパラメータ | 400 |
| COMMAND_FAILED | コマンド実行失敗 | 500 |
| COMMAND_TIMEOUT | コマンドタイムアウト | 408 |
| NOT_FLYING | 飛行していない | 400 |
| ALREADY_FLYING | 既に飛行中 | 400 |
| STREAMING_NOT_STARTED | ストリーミング未開始 | 400 |
| MODEL_NOT_FOUND | モデルが見つからない | 404 |
| INTERNAL_ERROR | 内部エラー | 500 |

## エンドポイント詳細仕様

### 1. システム管理

#### GET /health
**概要**: システムヘルスチェック

**レスポンス**:
```json
{
  "status": "healthy"
}
```

#### GET /
**概要**: API情報取得

**レスポンス**:
```json
{
  "message": "MFG Drone Backend API"
}
```

### 2. ドローン接続管理

#### POST /drone/connect
**概要**: ドローンに接続

**リクエスト**: ボディなし

**レスポンス例**:
```json
{
  "success": true,
  "message": "ドローンに接続しました"
}
```

**エラー例**:
```json
{
  "error": "ドローン接続に失敗しました",
  "code": "DRONE_CONNECTION_FAILED"
}
```

#### POST /drone/disconnect
**概要**: ドローンから切断

**リクエスト**: ボディなし

**レスポンス**: 標準StatusResponse

### 3. 基本飛行制御

#### POST /drone/takeoff
**概要**: ドローン離陸

**前提条件**: ドローン接続済み、地上にいる

**レスポンス例**:
```json
{
  "success": true,
  "message": "離陸しました"
}
```

#### POST /drone/land
**概要**: ドローン着陸

**前提条件**: 飛行中

#### POST /drone/emergency
**概要**: 緊急停止

**説明**: 即座にモーターを停止（墜落リスクあり）

### 4. 移動制御

#### POST /drone/move/{direction}
**概要**: 指定方向への移動

**パラメータ**:
- `direction`: up, down, left, right, forward, back
- `distance`: 移動距離（cm）20-500

**リクエスト例**:
```json
{
  "distance": 100
}
```

#### POST /drone/rotate/{direction}
**概要**: 回転動作

**パラメータ**:
- `direction`: cw（時計回り）, ccw（反時計回り）
- `degrees`: 回転角度（度）1-360

**リクエスト例**:
```json
{
  "degrees": 90
}
```

#### POST /drone/go_to
**概要**: 座標指定移動

**リクエスト例**:
```json
{
  "x": 100,
  "y": 200,
  "z": 150,
  "speed": 50
}
```

#### POST /drone/curve
**概要**: カーブ飛行

**リクエスト例**:
```json
{
  "x1": 100, "y1": 100, "z1": 100,
  "x2": 200, "y2": 200, "z2": 150,
  "speed": 60
}
```

### 5. カメラ制御

#### POST /drone/camera/stream/start
**概要**: 映像ストリーミング開始

**レスポンス例**:
```json
{
  "success": true,
  "message": "ストリーミングを開始しました",
  "stream_url": "ws://localhost:8000/stream"
}
```

#### POST /drone/camera/stream/stop
**概要**: 映像ストリーミング停止

#### POST /drone/camera/photo
**概要**: 写真撮影

**レスポンス例**:
```json
{
  "success": true,
  "message": "写真を撮影しました",
  "filename": "photo_20231201_143022.jpg",
  "file_size": 1024576
}
```

#### POST /drone/camera/video/start
**概要**: 動画録画開始

#### POST /drone/camera/video/stop
**概要**: 動画録画停止

**レスポンス例**:
```json
{
  "success": true,
  "message": "録画を停止しました",
  "filename": "video_20231201_143022.mp4",
  "duration": 120.5,
  "file_size": 15728640
}
```

### 6. センサーデータ

#### GET /drone/sensors/battery
**概要**: バッテリー情報取得

**レスポンス例**:
```json
{
  "percentage": 85,
  "voltage": 4.1,
  "temperature": 28.5
}
```

#### GET /drone/sensors/altitude
**概要**: 高度情報取得

**レスポンス例**:
```json
{
  "altitude": 150.5,
  "barometric_pressure": 1013.25
}
```

#### GET /drone/sensors/attitude
**概要**: 姿勢角取得

**レスポンス例**:
```json
{
  "pitch": 2.5,
  "roll": -1.2,
  "yaw": 45.8
}
```

#### GET /drone/sensors/acceleration
**概要**: 加速度データ取得

**レスポンス例**:
```json
{
  "x": 0.02,
  "y": -0.01,
  "z": 9.81
}
```

#### GET /drone/sensors/velocity
**概要**: 速度データ取得

**レスポンス例**:
```json
{
  "x": 0.5,
  "y": -0.2,
  "z": 0.0
}
```

#### GET /drone/sensors/all
**概要**: 全センサーデータ一括取得

**レスポンス例**:
```json
{
  "battery": {
    "percentage": 85,
    "voltage": 4.1,
    "temperature": 28.5
  },
  "altitude": 150.5,
  "attitude": {
    "pitch": 2.5,
    "roll": -1.2,
    "yaw": 45.8
  },
  "acceleration": {
    "x": 0.02,
    "y": -0.01,
    "z": 9.81
  },
  "velocity": {
    "x": 0.5,
    "y": -0.2,
    "z": 0.0
  },
  "flight_time": 120,
  "temperature": 25.0
}
```

### 7. 物体追跡

#### POST /drone/tracking/start
**概要**: 物体追跡開始

**リクエスト例**:
```json
{
  "target_object": "person",
  "tracking_mode": "center",
  "sensitivity": 0.7
}
```

#### POST /drone/tracking/stop
**概要**: 物体追跡停止

#### GET /drone/tracking/status
**概要**: 追跡状況取得

**レスポンス例**:
```json
{
  "is_tracking": true,
  "target_object": "person",
  "confidence": 0.85,
  "target_position": {
    "x": 320,
    "y": 240,
    "width": 120,
    "height": 180
  },
  "tracking_mode": "center"
}
```

### 8. AIモデル管理

#### GET /drone/models
**概要**: 利用可能モデル一覧取得

**レスポンス例**:
```json
{
  "models": [
    {
      "id": "person_v1",
      "name": "人物検出モデル v1.0",
      "accuracy": 0.95,
      "created_at": "2023-12-01T10:00:00Z",
      "is_active": true
    },
    {
      "id": "vehicle_v1",
      "name": "車両検出モデル v1.0", 
      "accuracy": 0.88,
      "created_at": "2023-11-15T14:30:00Z",
      "is_active": false
    }
  ]
}
```

#### POST /drone/models/train
**概要**: 新しいモデル学習

**リクエスト**: multipart/form-data
- `model_name`: モデル名
- `images`: 学習用画像ファイル（複数）
- `labels`: ラベルファイル

#### POST /drone/models/{model_id}/activate
**概要**: モデル切り替え

### 9. ミッションパッド制御

#### POST /drone/mission_pad/enable
**概要**: ミッションパッド検出有効化

#### GET /drone/mission_pad/status
**概要**: ミッションパッド状況取得

**レスポンス例**:
```json
{
  "detection_enabled": true,
  "detected_pads": [
    {
      "id": "m1",
      "position": {
        "x": 100,
        "y": 150,
        "z": 120
      },
      "distance": 85.2
    }
  ]
}
```

### 10. システム設定

#### GET /drone/settings
**概要**: 現在の設定取得

**レスポンス例**:
```json
{
  "speed": 50,
  "wifi_ssid": "TELLO-ABC123",
  "camera_quality": 720,
  "tracking_sensitivity": 0.5
}
```

#### PUT /drone/settings
**概要**: 設定更新

**リクエスト例**:
```json
{
  "speed": 80,
  "camera_quality": 1080
}
```

#### POST /drone/settings/wifi
**概要**: WiFi設定変更

**リクエスト例**:
```json
{
  "ssid": "HOME_WIFI",
  "password": "password123"
}
```

## WebSocket通信仕様

### 映像ストリーミング

**エンドポイント**: `ws://localhost:8000/stream`

**メッセージ形式**:
```json
{
  "type": "video_frame",
  "timestamp": "2023-12-01T15:30:22.123Z",
  "frame_data": "base64_encoded_image_data",
  "frame_number": 1234,
  "fps": 30
}
```

### リアルタイム状態通知

**エンドポイント**: `ws://localhost:8000/status`

**メッセージ例**:
```json
{
  "type": "drone_status",
  "timestamp": "2023-12-01T15:30:22.123Z",
  "battery": 82,
  "altitude": 120.5,
  "is_flying": true,
  "connection_status": "connected"
}
```

## レート制限

| エンドポイントカテゴリ | 制限 | 説明 |
|---------------------|------|------|
| 制御コマンド | 10req/sec | 安全な制御のため |
| センサーデータ | 50req/sec | データ取得頻度制限 |
| ストリーミング | 1接続/クライアント | 帯域幅制限 |
| ファイルアップロード | 1req/min | リソース保護 |

## HTTPステータスコード

| コード | 用途 | 説明 |
|-------|------|------|
| 200 | 成功 | 要求が正常に処理された |
| 400 | 不正なリクエスト | パラメータエラー・前提条件違反 |
| 404 | 見つからない | リソースが存在しない |
| 408 | タイムアウト | コマンド実行がタイムアウト |
| 429 | レート制限 | リクエスト頻度制限に抵触 |
| 500 | サーバーエラー | 内部エラー・ドローン通信エラー |

## API使用例

### 基本的な飛行フロー

```bash
# 1. ドローン接続
curl -X POST http://localhost:8000/drone/connect

# 2. 離陸
curl -X POST http://localhost:8000/drone/takeoff

# 3. 前進
curl -X POST http://localhost:8000/drone/move/forward \
  -H "Content-Type: application/json" \
  -d '{"distance": 100}'

# 4. 着陸
curl -X POST http://localhost:8000/drone/land

# 5. 切断
curl -X POST http://localhost:8000/drone/disconnect
```

### 物体追跡フロー

```bash
# 1. ストリーミング開始
curl -X POST http://localhost:8000/drone/camera/stream/start

# 2. 追跡開始
curl -X POST http://localhost:8000/drone/tracking/start \
  -H "Content-Type: application/json" \
  -d '{"target_object": "person", "tracking_mode": "center"}'

# 3. 追跡状況確認
curl http://localhost:8000/drone/tracking/status

# 4. 追跡停止
curl -X POST http://localhost:8000/drone/tracking/stop
```