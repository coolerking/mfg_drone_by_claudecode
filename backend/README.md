# MFG Drone Backend API Server

ドローンの自律制御、コンピュータビジョン、機械学習モデル管理のためのFastAPIベースの包括的なバックエンドシステム。

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

- [ユーザガイド](docs/user_guide.md)を参照してください。

## 📄 ライセンス

MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。