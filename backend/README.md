# MFG Drone Backend API Server

FastAPI-based comprehensive backend system for autonomous drone control, computer vision, and machine learning model management.

## 🎯 概要

MFG Drone Backend API Server は、Tello EDU ドローンを使った自動追従撮影システムのバックエンドAPI。OpenAPI仕様に準拠したRESTful APIとWebSocket通信でドローン制御、物体認識・追跡、モデル管理機能を提供します。

## 🚀 主要機能

### Phase 1: 基盤実装
- **基本ドローン制御**: 接続・離着陸・移動・回転
- **3D物理シミュレーション**: DroneSimulatorによる仮想環境
- **リアルタイム状態監視**: ドローン状態の即座確認
- **RESTful API**: OpenAPI仕様に準拠したAPI設計

### Phase 2: 高度制御 & WebSocket通信
- **WebSocketリアルタイム通信**: 双方向データ交換
- **高度なカメラ制御**: VirtualCameraStreamによる映像配信
- **並行処理対応**: 複数ドローンの同時制御
- **パフォーマンス最適化**: 1秒間隔の自動状態配信

### Phase 3: ビジョン & ML機能
- **物体検出**: YOLOv8、SSD、Faster R-CNN対応
- **自動追跡**: リアルタイム物体追跡・ドローン自動追従
- **データセット管理**: 学習データの作成・管理
- **モデル学習管理**: 非同期学習ジョブ処理

### ✅ Phase 4: プロダクション対応
- **🔐 API認証システム**: API Key認証・権限管理
- **🛡️ セキュリティ強化**: レート制限・セキュリティヘッダー・入力検証
- **⚠️ 高度なアラートシステム**: 閾値ベース監視・自動通知・リアルタイム監視
- **📊 パフォーマンス監視**: システム監視・キャッシュ最適化・パフォーマンス分析
- **🚀 プロダクション対応**: 包括的テスト・エラーハンドリング・本番環境対応

## 📁 プロジェクト構造

```
backend/
├── api_server/                    # メインAPIサーバー
│   ├── main.py                   # FastAPIアプリケーション
│   ├── security.py               # 認証・セキュリティ (Phase 4)
│   ├── api/                      # APIルーター
│   │   ├── drones.py            # ドローン制御API
│   │   ├── vision.py            # ビジョンAPI (Phase 3)
│   │   ├── models.py            # モデルAPI (Phase 3)
│   │   ├── dashboard.py         # ダッシュボードAPI (Phase 3)
│   │   ├── phase4.py            # Phase 4専用API
│   │   └── websocket.py         # WebSocket API
│   ├── core/                     # コアサービス
│   │   ├── drone_manager.py     # ドローン管理
│   │   ├── camera_service.py    # カメラサービス
│   │   ├── vision_service.py    # ビジョンサービス (Phase 3)
│   │   ├── dataset_service.py   # データセット管理 (Phase 3)
│   │   ├── model_service.py     # モデル管理サービス (Phase 3)
│   │   ├── system_service.py    # システム監視サービス (Phase 3)
│   │   ├── alert_service.py     # アラートサービス (Phase 4)
│   │   └── performance_service.py # パフォーマンスサービス (Phase 4)
│   └── models/                   # Pydanticモデル
├── src/                          # 既存ダミーシステム
├── tests/                        # テストスイート
└── docs/                         # ドキュメント
```

## 🛠️ セットアップ

### 前提条件
- Python 3.8+
- 依存関係: `requirements.txt`参照

### インストール & 起動
```bash
# 1. リポジトリクローン
git clone <repository-url>
cd backend

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. サーバー起動
python start_api_server.py
```

### アクセスポイント
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws
- **Health Check**: http://localhost:8000/health

## 📡 API エンドポイント

### ドローン制御 (Phase 1&2)
```bash
# ドローン一覧
GET /api/drones

# ドローン制御
POST /api/drones/{droneId}/connect
POST /api/drones/{droneId}/takeoff
POST /api/drones/{droneId}/land
POST /api/drones/{droneId}/move
POST /api/drones/{droneId}/rotate

# カメラ制御
POST /api/drones/{droneId}/camera/stream/start
POST /api/drones/{droneId}/camera/photo

# 状態監視
GET /api/drones/{droneId}/status
```

### ビジョンAPI (Phase 3)
```bash
# データセット管理
GET /api/vision/datasets
POST /api/vision/datasets
GET /api/vision/datasets/{datasetId}
DELETE /api/vision/datasets/{datasetId}
POST /api/vision/datasets/{datasetId}/images

# 物体検出
POST /api/vision/detection

# 物体追跡
POST /api/vision/tracking/start
POST /api/vision/tracking/stop
GET /api/vision/tracking/status
```

### モデルAPI (Phase 3)
```bash
# モデル管理
GET /api/models
POST /api/models                    # モデル学習開始
GET /api/models/{modelId}
DELETE /api/models/{modelId}

# 学習ジョブ管理
GET /api/models/training/{jobId}
POST /api/models/training/{jobId}/cancel
GET /api/models/training           # 全ジョブ取得
GET /api/models/training/active    # アクティブジョブ
```

### ダッシュボードAPI (Phase 3)
```bash
# システム監視
GET /api/dashboard/system          # システム状態
GET /api/dashboard/drones          # ドローン群状態
GET /api/dashboard/health          # サービス健全性
GET /api/dashboard/performance     # パフォーマンス指標
GET /api/dashboard/overview        # 総合ダッシュボード
```

### Phase 4: セキュリティ・監視API
```bash
# セキュリティ管理 (Admin権限)
GET /api/security/api-keys
POST /api/security/api-keys
DELETE /api/security/api-keys/{apiKey}
GET /api/security/config

# アラート管理 (Dashboard権限)
GET /api/alerts
POST /api/alerts/{alertId}/acknowledge
POST /api/alerts/{alertId}/resolve
GET /api/alerts/summary
GET /api/alerts/rules

# パフォーマンス監視 (Dashboard権限)
GET /api/performance/summary
GET /api/performance/metrics
GET /api/performance/api
POST /api/performance/optimize     # Admin権限
GET /api/performance/cache/stats
DELETE /api/performance/cache      # Admin権限

# 詳細ヘルスチェック (Dashboard権限)
GET /api/health/detailed
```

## 🔐 認証システム (Phase 4)

### API Key認証
```bash
# ヘッダーでAPI Keyを指定
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/dashboard/system
```

### デフォルトAPI Keys
- **Admin Key**: `mfg-drone-admin-key-2024`
  - 権限: `admin`, `read`, `write`, `dashboard`
- **Read-Only Key**: `mfg-drone-readonly-2024`
  - 権限: `read`, `dashboard`

### 権限レベル
- `read`: データ読み取り
- `write`: データ作成・更新
- `admin`: システム管理・API Key管理
- `dashboard`: ダッシュボード・監視機能

## 🧪 テスト

### テスト実行
```bash
# 全テスト実行
pytest tests/ -v

# フェーズ別テスト
pytest tests/test_api_basic.py -v              # Phase 1
pytest tests/test_websocket_api.py -v          # Phase 2
pytest tests/test_vision_service.py -v         # Phase 3
pytest tests/test_phase3_integration.py -v     # Phase 3統合
pytest tests/test_phase4_*.py -v               # Phase 4全般

# カバレッジ測定
pytest tests/ --cov=api_server --cov-report=html
```

### テスト対象範囲
- **ドローン制御**: 基本制御・WebSocket通信
- **ビジョン処理**: 物体検出・追跡・データセット管理
- **モデル管理**: 学習・推論・ライフサイクル管理
- **システム監視**: 健全性・パフォーマンス統合
- **セキュリティ**: 認証・認可・入力検証 (Phase 4)
- **アラート**: 監視・通知・ルール管理 (Phase 4)
- **統合テスト**: E2Eワークフロー・負荷テスト

## 💡 使用例

### 1. 基本ドローン制御
```python
import requests

# 認証ヘッダー (Phase 4)
headers = {"X-API-Key": "mfg-drone-admin-key-2024"}

# 接続
response = requests.post('http://localhost:8000/api/drones/drone_001/connect', headers=headers)

# 離陸
response = requests.post('http://localhost:8000/api/drones/drone_001/takeoff', headers=headers)

# 移動
response = requests.post('http://localhost:8000/api/drones/drone_001/move', 
                        json={"direction": "forward", "distance": 100}, 
                        headers=headers)

# 着陸
response = requests.post('http://localhost:8000/api/drones/drone_001/land', headers=headers)
```

### 2. 物体検出・追跡
```python
import base64
import requests

headers = {"X-API-Key": "mfg-drone-readonly-2024"}

# 画像から物体検出
with open('image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post('http://localhost:8000/api/vision/detection', 
                        json={
                            'image': image_data,
                            'model_id': 'yolo_v8_general',
                            'confidence_threshold': 0.5
                        }, headers=headers)

detections = response.json()['detections']
print(f"検出した物体: {len(detections)}")

# 物体追跡開始
response = requests.post('http://localhost:8000/api/vision/tracking/start', 
                        json={
                            'model_id': 'yolo_v8_person_detector',
                            'drone_id': 'drone_001',
                            'follow_distance': 200
                        }, headers=headers)
```

### 3. システム監視・アラート (Phase 4)
```python
# システム健全性チェック
response = requests.get('http://localhost:8000/api/health/detailed', headers=headers)
health = response.json()

# アラート一覧取得
response = requests.get('http://localhost:8000/api/alerts?unresolved_only=true', headers=headers)
alerts = response.json()['alerts']

# パフォーマンス監視
response = requests.get('http://localhost:8000/api/performance/summary', headers=headers)
performance = response.json()

# システム最適化 (Admin権限)
admin_headers = {"X-API-Key": "mfg-drone-admin-key-2024"}
response = requests.post('http://localhost:8000/api/performance/optimize', headers=admin_headers)
```

## ⚙️ 設定

### 環境変数
```bash
# サーバー設定
export HOST=0.0.0.0
export PORT=8000
export LOG_LEVEL=INFO

# データ保存設定
export MFG_DATASETS_ROOT=/path/to/datasets
export MFG_MODELS_ROOT=/path/to/models

# 学習設定
export DEFAULT_EPOCHS=100
export DEFAULT_BATCH_SIZE=16

# WebSocket設定
export WS_HEARTBEAT_INTERVAL=1.0

# カメラ設定
export CAMERA_WIDTH=640
export CAMERA_HEIGHT=480
export CAMERA_FPS=30

# Phase 4: セキュリティ設定
export MFG_DRONE_ADMIN_KEY=your-secure-admin-key
export MFG_DRONE_READONLY_KEY=your-secure-readonly-key
export RATE_LIMIT_ENABLED=true
export MAX_FAILED_ATTEMPTS=10
```

## 📊 パフォーマンス

### レスポンス時間目標
| 機能 | Phase 1&2 | Phase 3 | Phase 4 |
|------|-----------|---------|---------|
| API レスポンス | <0.1秒 | <0.1秒 | <0.1秒 |
| WebSocket接続 | <5秒(10接続) | <5秒(10接続) | <5秒(10接続) |
| カメラストリーム | <2秒起動 | <2秒起動 | <2秒起動 |
| 写真撮影 | <0.5秒/枚 | <0.5秒/枚 | <0.5秒/枚 |
| 物体検出 | - | <0.5秒/画像 | <0.5秒/画像 |
| モデル学習開始 | - | <2秒 | <2秒 |
| データセット作成 | - | <1秒 | <1秒 |
| システム状態監視 | - | <0.1秒 | <0.1秒 |
| 認証処理 | - | - | <50ms |
| アラート生成 | - | - | <100ms |

### メモリ使用量
- **基本動作**: ~50MB
- **Phase 2**: +10MB
- **Phase 3**: +20MB
- **Phase 4**: +30MB
- **学習実行時**: +200-500MB (学習時のみ)
- **CPU使用率**: 通常10-20%、学習時70-90%

## 🔒 セキュリティ (Phase 4)

### セキュリティ機能
- **API Key認証**: すべての保護されたエンドポイント
- **レート制限**: DDoS攻撃防止
- **セキュリティヘッダー**: XSS・CSRF防止
- **入力検証**: SQLインジェクション・XSS防止
- **IP ブロッキング**: 不正アクセス検出・自動ブロック
- **権限管理**: ロールベースアクセス制御

### ファイルアップロード制限
- **対応形式**: JPEG, PNG, BMP
- **最大ファイルサイズ**: 10MB
- **MIMEタイプ検証**: ファイル形式の厳密チェック
- **セキュリティスキャン**: 悪意あるファイルの検出

## 🛠️ トラブルシューティング

### よくある問題

#### 1. サーバー起動失敗
```bash
# ポート使用確認
netstat -an | grep 8000

# 依存関係更新
pip install -r requirements.txt --upgrade
```

#### 2. API認証エラー (Phase 4)
```bash
# 正しいAPI Keyヘッダーを確認
curl -H "X-API-Key: mfg-drone-admin-key-2024" [URL]

# レート制限エラー
# 429 Too Many Requests - リクエスト頻度を下げる
```

#### 3. WebSocket接続失敗
```bash
# CORS設定確認
curl -I http://localhost:8000/ws
```

#### 4. モデル学習エラー
```bash
# データセット確認
curl http://localhost:8000/api/vision/datasets/{datasetId}

# システムリソース確認
curl http://localhost:8000/api/dashboard/performance
```

### デバッグ
```bash
# デバッグモードで起動
LOG_LEVEL=DEBUG python start_api_server.py

# ヘルスチェック
curl http://localhost:8000/api/dashboard/health

# 詳細システム情報 (Phase 4)
curl -H "X-API-Key: mfg-drone-readonly-2024" \
     http://localhost:8000/api/health/detailed
```

## 📚 ドキュメント

- **[Phase 1 README](./API_SERVER_README.md)**: 基本ドローン制御
- **[Phase 2 README](./PHASE2_README.md)**: WebSocket・高度制御
- **[Phase 3 README](./PHASE3_README.md)**: ビジョン・ML機能
- **[Phase 4 README](./PHASE4_README.md)**: セキュリティ・プロダクション対応
- **[OpenAPI Specification](../shared/api-specs/backend-api.yaml)**: API仕様書

## 🎯 開発フェーズ

### ✅ フェーズ1完了: 基盤実装
- FastAPIプロジェクト構築
- 基本ドローン制御API
- OpenAPI仕様準拠
- 既存システム統合

### ✅ フェーズ2完了: 高度機能
- WebSocketリアルタイム通信
- カメラストリーミング
- 強化されたエラーハンドリング
- パフォーマンス最適化

### ✅ フェーズ3完了: ビジョン・ML機能
- 物体検出・追跡API
- データセット管理システム
- モデル学習・管理機能
- ダッシュボードAPI

### ✅ フェーズ4完了: プロダクション対応
- **🔐 API認証システム**: API Key認証・権限管理
- **🛡️ セキュリティ強化**: レート制限・セキュリティヘッダー
- **⚠️ 高度なアラート**: 閾値監視・自動通知
- **📊 パフォーマンス監視**: リアルタイム追跡・最適化
- **🚀 プロダクション対応**: 包括的テスト・エラーハンドリング

### ✅ フェーズ5完了: Webダッシュボード・本番デプロイ
- **🖥️ リアルタイムWebダッシュボード**: 現代的SPA・レスポンシブデザイン
- **🐳 完全Docker化**: 開発・本番環境コンテナ化
- **🚀 CI/CD自動化**: GitHub Actions完全パイプライン
- **⚖️ 負荷分散**: Nginx リバースプロキシ・SSL終端
- **📊 監視システム**: Prometheus/Grafana本格統合
- **🔒 エンタープライズセキュリティ**: 本番環境対応

Phase 5によって、エンタープライズグレードの完全なドローン制御システムが完成しました。

**🎯 完全なMLパイプライン**: データセット作成→学習→推論→制御  
**🖥️ リアルタイムWebダッシュボード**: 現代的SPA・直感的操作  
**🐳 本番環境対応**: Docker化・CI/CD・負荷分散  
**📊 包括的監視**: Prometheus・Grafana・アラート  
**🔒 エンタープライズセキュリティ**: 認証・暗号化・監査  
**⚡ 高性能・高可用性**: スケーラブル・障害耐性  

### 🌟 システム特徴
- **オールインワン**: ドローン制御からAI/MLまで統合
- **プロダクション対応**: 24/7運用可能な堅牢性
- **開発者フレンドリー**: 包括的ドキュメント・テスト
- **拡張可能**: マイクロサービス・API エコシステム
- **最新技術**: FastAPI・Docker・WebSocket・Chart.js

### 🚀 今後の展開
- **モバイルアプリ**: React Native/Flutter対応
- **マルチクラウド**: AWS/Azure/GCP 統合
- **エッジコンピューティング**: Raspberry Pi/Jetson最適化
- **AI強化**: GPU クラスター・分散学習・エッジAI

## 📞 サポート・貢献

1. バグや問題を発見した場合は、詳細情報と再現手順を含めてIssueを作成してください。
2. 機能改善の提案やプルリクエストも歓迎します。
3. OpenAPI仕様への準拠を心がけてください。
4. テストケースの追加と実行も忘れずにお願いします。
5. ドキュメントの更新も併せてお願いします。

## 📄 ライセンス

MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。