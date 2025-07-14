# MFG Drone Backend API Server

ドローンの自律制御、コンピュータビジョン、機械学習モデル管理のためのFastAPIベースの包括的なバックエンドシステム。

## 🎯 概要

MFG Drone Backend API Server は、Tello EDU ドローンを使った自動追従撮影システムのバックエンドAPI。OpenAPI仕様に準拠したRESTful APIとWebSocket通信でドローン制御、物体認識・追跡、モデル管理機能を提供します。

**🆕 Phase 6対応**: シミュレーション環境と実機Tello EDUドローンの**ハイブリッド運用**に対応。既存APIとの100%互換性を維持しながら、実機制御機能を統合しました。

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

### 🆕 Phase 6: Tello EDU実機統合
- **🚁 実機ドローン制御**: Tello EDUとの直接通信・制御
- **🔄 ハイブリッド運用**: 実機・シミュレーション同時制御
- **🔍 自動検出**: LAN内Tello EDU自動発見
- **🔧 設定駆動**: YAML設定による動作モード切り替え
- **🛡️ フォールバック**: 実機接続失敗時の自動シミュレーション切り替え
- **📡 ネットワーク管理**: IP管理・接続状態監視
- **🔌 API互換性**: 既存API 100%互換性維持

## 📁 プロジェクト構造

```
backend/
├── api_server/                    # メインAPIサーバー
│   ├── main.py                   # FastAPIアプリケーション
│   ├── security.py               # 認証・セキュリティ (Phase 4)
│   ├── api/                      # APIルーター
│   │   ├── drones.py            # ドローン制御API
│   │   ├── enhanced_drones.py   # 拡張ドローンAPI
│   │   ├── vision.py            # ビジョンAPI (Phase 3)
│   │   ├── models.py            # モデルAPI (Phase 3)
│   │   ├── dashboard.py         # ダッシュボードAPI (Phase 3)
│   │   ├── phase4.py            # Phase 4専用API
│   │   └── websocket.py         # WebSocket API
│   ├── core/                     # コアサービス
│   │   ├── drone_manager.py     # ドローン管理
│   │   ├── enhanced_drone_manager.py # 拡張ドローン管理
│   │   ├── camera_service.py    # カメラサービス
│   │   ├── vision_service.py    # ビジョンサービス (Phase 3)
│   │   ├── enhanced_vision_service.py # 拡張ビジョンサービス
│   │   ├── dataset_service.py   # データセット管理 (Phase 3)
│   │   ├── model_service.py     # モデル管理サービス (Phase 3)
│   │   ├── system_service.py    # システム監視サービス (Phase 3)
│   │   ├── alert_service.py     # アラートサービス (Phase 4)
│   │   ├── performance_service.py # パフォーマンスサービス (Phase 4)
│   │   ├── tello_edu_controller.py # Tello EDU実機制御 (Phase 6)
│   │   ├── drone_factory.py     # ドローンファクトリー (Phase 6)
│   │   └── config_service.py    # 設定管理サービス (Phase 6)
│   └── models/                   # Pydanticモデル
│       ├── common_models.py     # 共通モデル
│       ├── drone_models.py      # ドローンモデル
│       ├── vision_models.py     # ビジョンモデル
│       └── model_models.py      # MLモデル
├── src/                          # 既存ダミーシステム
│   ├── config/                  # 設定ファイル
│   │   ├── camera_config.py     # カメラ設定
│   │   └── simulation_config.py # シミュレーション設定
│   └── core/                    # コアシステム
│       ├── drone_simulator.py   # ドローンシミュレータ
│       └── virtual_camera.py    # 仮想カメラ
├── tests/                        # テストスイート
│   └── fixtures/                # テスト用データ
├── config/                       # 設定ファイル (Phase 6)
│   └── drone_config.yaml        # ドローン設定
├── docs/                         # ドキュメント
│   ├── user_guide.md            # ユーザガイド
│   └── plan/                    # 各フェーズの計画書
│       └── PHASE6_TELLO_INTEGRATION_README.md # Phase 6技術仕様
├── web_dashboard/               # Webダッシュボード (Phase 5)
│   ├── index.html               # メインページ
│   ├── dashboard.js             # JavaScript
│   └── styles.css               # スタイルシート
├── monitoring/                  # 監視設定
│   └── prometheus.yml           # Prometheus設定
├── Dockerfile                   # Docker設定
├── docker-compose.yml          # 本番用Docker Compose
├── docker-compose.dev.yml      # 開発用Docker Compose
├── nginx.conf                   # Nginx設定
├── requirements.txt             # Python依存関係
├── pytest.ini                  # pytest設定
├── start_api_server.py         # サーバー起動スクリプト
└── run_tests.py                # テスト実行スクリプト
```

## 🛠️ セットアップ

### 基本セットアップ

- [ユーザガイド](docs/user_guide.md)を参照してください。

### 🆕 実機ドローン対応セットアップ (Phase 6)

#### 1. 依存関係インストール

```bash
# djitellopyライブラリを含む全依存関係をインストール
pip install -r requirements.txt
```

#### 2. 動作モード設定

環境変数または設定ファイルで動作モードを指定：

```bash
# 環境変数での設定
export DRONE_MODE=auto              # auto, simulation, real
export TELLO_AUTO_DETECT=true       # 自動検出有効
export TELLO_CONNECTION_TIMEOUT=10  # 接続タイムアウト(秒)
```

```yaml
# config/drone_config.yaml での設定
global:
  default_mode: "auto"  # 実機優先、シミュレーションフォールバック
  auto_detection:
    enabled: true
    timeout: 5.0

drones:
  - id: "drone_001"
    name: "Tello EDU #1"
    mode: "auto"
    ip_address: "192.168.10.1"  # 手動指定またはnull（自動検出）
```

#### 3. ネットワーク設定

Tello EDUとの通信のため、以下を確認：

- **WiFi接続**: Tello EDUのWiFiネットワークに接続、またはLAN内同一セグメント
- **ファイアウォール**: UDP通信（ポート8889）の許可
- **IPアドレス**: Tello EDUのIPアドレス確認（通常192.168.10.1）

#### 4. 動作確認

```bash
# シミュレーションモードで起動（実機なしでテスト可能）
export DRONE_MODE=simulation
python start_api_server.py

# 自動モードで起動（実機検出→フォールバック）
export DRONE_MODE=auto
python start_api_server.py
```

#### 詳細情報

- **技術仕様**: [Phase 6 統合ガイド](docs/plan/PHASE6_TELLO_INTEGRATION_README.md)
- **トラブルシューティング**: 実機接続問題の解決方法
- **API仕様**: 既存API + 実機拡張機能

## 📄 ライセンス

MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。