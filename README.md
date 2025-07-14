# MFG ドローン - 自動追従撮影システム Phase 6 🚁

**Tello EDU実機・シミュレーション統合対応版**

Tello EDU ドローンを使って移動する対象物を自動的に追跡・撮影するシステムです。Phase 6では実機ドローンとシミュレーションの完全統合を実現し、開発・テスト・本番運用をシームレスに切り替え可能です。

## ✨ 主要機能

### 1. 🎮 手動運転機能
- ユーザが指示したとおりにドローンを操作する
- **NEW** 実機・シミュレーション統一制御API
- **NEW** リアルタイム状態監視・WebSocket配信

### 2. 🔍 物体追随機能
#### 追随物体学習データ管理
- ドローンのカメラ機能をつかって、対象の写真を撮る
- 複数撮影し学習データセットとして管理する
- 外部撮影画像の登録・管理機能
- **NEW** 実機カメラからのリアルタイム学習データ収集

#### 追随物体モデル管理
- 学習データセットを選択して追随物体モデルを学習する
- 学習済みのモデルを管理する
- **NEW** ライブカメラフィードによる物体検出

### 3. 🤖 自動運転機能（物体追随）
- ユーザが指示したモデルを使って物体を正面に捉えるように自動的に移動する
- ユーザが指示したら手動運転に戻る
- 追随物体が見当たらない場合の安全な緊急停止
- **NEW** 実機カメラを使用したリアルタイム物体追跡
- **NEW** 高精度位置制御とVPS（Vision Positioning System）対応

### 4. 🔧 ドローン管理機能
- 複数のドローンを登録・管理
- **NEW** 実機・シミュレーション自動検出・切り替え
- **NEW** LAN内ドローン自動スキャン機能
- **NEW** ハイブリッド運用（実機+シミュレーション同時制御）
- 現在の動作状態を確認するダッシュボード画面

### 5. 🌐 Phase 6 新機能
#### 実機統合機能
- **Tello EDU自動検出**: LAN内の実機ドローンを自動発見
- **シームレス切り替え**: 実機↔シミュレーション間の透明な切り替え
- **フォールバック機能**: 実機接続失敗時の自動シミュレーション切り替え
- **ネットワーク監視**: 接続品質・信号強度のリアルタイム監視

#### 統合ビジョンシステム
- **リアルタイム物体検出**: 実機カメラからのライブ検出
- **拡張追跡システム**: ドローン移動制御との統合
- **カメラ統合管理**: 実機・仮想カメラの統一インターフェース

#### 開発・運用支援
- **包括的テストスイート**: API互換性・切り替え機能の自動検証
- **詳細監視・診断**: ネットワーク状態・ドローン健全性監視
- **運用ドキュメント**: トラブルシューティング・設定ガイド完備

## 🏗 システム構成 (Phase 6対応)

### アーキテクチャ概要

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  フロントエンド   │◄──►│  バックエンドAPI  │◄──►│   実機ドローン    │
│  (Web UI)      │    │  (統合制御)      │    │  (Tello EDU)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCPサーバー    │    │ シミュレーション  │    │  ネットワーク監視  │
│  (Claude統合)   │    │  (仮想ドローン)   │    │   (自動検出)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 主要コンポーネント

#### 1. **バックエンドAPI** (Raspberry Pi 5 / サーバー)
**Core機能:**
- 🚁 **統合ドローン制御**: 実機・シミュレーション統一API
- 📷 **ビジョンシステム**: リアルタイム物体検出・追跡
- 🌐 **ネットワーク管理**: 自動検出・接続品質監視
- 🔄 **状態同期**: WebSocketリアルタイム配信

**Phase 6新機能:**
- **DroneFactory**: 実機・シミュレーション透明切り替え
- **NetworkService**: LAN内ドローン自動スキャン
- **EnhancedVisionService**: 実機カメラ統合
- **ConfigService**: YAML駆動設定管理

#### 2. **管理者用フロントエンド** (Windows PC / Web)
**管理機能:**
- 🎛 **統合制御パネル**: 複数ドローン同時制御
- 📊 **リアルタイム監視**: 状態・カメラ・ネットワーク
- 🤖 **AI学習**: 物体認識モデル訓練・管理
- 📈 **ダッシュボード**: パフォーマンス・健全性監視

#### 3. **MCPサーバー** (Windows PC)
- 🤖 **Claude統合**: AI支援による高度な制御
- 📜 **自動スクリプト**: 複雑な飛行パターン生成
- 🧠 **インテリジェント操作**: 自然言語によるドローン制御

#### 4. **ドローンエコシステム**
**実機ドローン (Tello EDU):**
- 📡 **WiFi制御**: 2.4GHz直接通信
- 📹 **720p HDカメラ**: リアルタイムストリーミング
- 🔋 **バッテリー監視**: 自動警告・安全着陸
- 📍 **VPS位置制御**: 高精度ホバリング

**シミュレーション環境:**
- 🎮 **仮想物理エンジン**: リアルな飛行動作
- 🎭 **仮想カメラ**: テスト用映像生成
- 🎯 **デバッグモード**: 開発・テスト支援

### ネットワーク構成

```
┌───────── LAN (192.168.1.0/24) ─────────┐
│                                        │
│  ┌─────────────┐    ┌──────────────┐   │
│  │  開発PC     │    │ Tello EDU #1 │   │
│  │ 192.168.1.10│◄──►│192.168.1.100 │   │
│  └─────────────┘    └──────────────┘   │
│         │                              │
│         ▼                              │
│  ┌─────────────┐    ┌──────────────┐   │
│  │ APIサーバー  │    │ Tello EDU #2 │   │
│  │ 192.168.1.11│◄──►│192.168.1.101 │   │
│  └─────────────┘    └──────────────┘   │
└────────────────────────────────────────┘
```

## 🚀 クイックスタート (Phase 6対応)

### 前提条件
- **Python 3.9+** (バックエンド)
- **Node.js 18+** (フロントエンド)
- **Tello EDU** (実機テスト用、オプション)

### 開発環境セットアップ

#### 1. リポジトリクローン
```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode
```

#### 2. バックエンド環境構築
```bash
cd backend

# 依存関係インストール
pip install -r requirements.txt

# Phase 6設定ファイル作成
cp config/drone_config.yaml.example config/drone_config.yaml

# 環境変数設定
export DRONE_MODE=auto           # auto, simulation, real
export TELLO_AUTO_DETECT=true    # 自動検出有効
export LOG_LEVEL=INFO
```

#### 3. フロントエンド環境構築
```bash
cd ../frontend
npm install
npm run dev
```

#### 4. 起動・確認
```bash
# バックエンド起動（別ターミナル）
cd backend
python main.py

# アクセス確認
curl http://localhost:8000/health
curl http://localhost:8000/api/drones  # ドローン一覧取得
```

### Phase 6: 実機ドローン統合

#### 実機接続モード
```bash
# 実機優先モード
export DRONE_MODE=real
export TELLO_IP_ADDRESS=192.168.1.100  # 手動IP指定

# 自動検出モード（推奨）
export DRONE_MODE=auto
export TELLO_AUTO_DETECT=true

python main.py
```

#### ハイブリッドモード（実機+シミュレーション）
```yaml
# config/drone_config.yaml
global:
  drone_mode: "hybrid"

drones:
  - id: "real_drone_001"
    mode: "real"
    ip_address: "192.168.1.100"
  - id: "sim_drone_001"
    mode: "simulation"
    position: [0, 0, 0]
```

### プロダクション環境
```bash
# 環境設定
cp .env.production .env
# .envファイルを編集（認証情報・ネットワーク設定）

# Phase 6対応設定
cat >> .env << EOF
DRONE_MODE=auto
TELLO_AUTO_DETECT=true
NETWORK_SCAN_ENABLED=true
VISION_ENHANCED_MODE=true
EOF

# 自動デプロイ
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 開発・テスト用コマンド

#### システム状態確認
```bash
# ネットワーク状態
curl http://localhost:8000/api/system/network_status

# ドローン検出
curl -X POST http://localhost:8000/api/drones/scan

# リアルタイム状態（WebSocket）
# ws://localhost:8000/ws
```

#### テスト実行
```bash
# Phase 6統合テスト
cd backend
python -m pytest tests/test_phase6_real_simulation_switching.py -v

# API互換性テスト
python -m pytest tests/test_compatibility.py -v

# 全テスト実行
python -m pytest tests/ -v
```

詳細は [ユーザーガイド](./backend/docs/user_guide.md) をご覧ください。

## 📊 監視・運用

システムは包括的な監視スタックを提供します：

- **Prometheus**: メトリクス収集 (http://localhost:9090)
- **Grafana**: ダッシュボード (http://localhost:3001)
- **アラート**: 自動通知システム
- **ログ集約**: 構造化ログ分析

## 🔧 開発・運用ツール

### CI/CD パイプライン
GitHub Actions による自動テスト・デプロイ：
```bash
# ワークフローファイル設定
cp .github-workflows-templates/* .github/workflows/
```

### 自動デプロイスクリプト
```bash
# 各種操作
./scripts/deploy.sh deploy    # フルデプロイ
./scripts/deploy.sh rollback  # ロールバック
./scripts/deploy.sh status    # 状態確認
./scripts/deploy.sh logs      # ログ表示
```

## 🏗 技術スタック (Phase 6拡張版)

### フロントエンド
- **React 18** + TypeScript
- **Material-UI (MUI)** - UIコンポーネント
- **Redux Toolkit** - 状態管理
- **Vite** - ビルドツール
- **Vitest + Playwright** - テスト
- **WebSocket** - リアルタイム通信

### バックエンド Core
- **FastAPI** - Webフレームワーク
- **asyncio** - 非同期処理
- **Pydantic** - データバリデーション
- **SQLAlchemy** - ORM
- **Alembic** - データベースマイグレーション

### Phase 6: ドローン制御・統合
- **djitellopy 2.5.0** - Tello EDU制御ライブラリ
- **DroneFactory** - 実機・シミュレーション抽象化
- **NetworkService** - 自動検出・ネットワーク管理
- **ConfigService** - YAML駆動設定管理
- **WebSocket Broadcasting** - リアルタイム状態配信

### ビジョン・AI
- **YOLO v8** - 物体検出（MockModel含む）
- **OpenCV 4.8+** - 画像処理・カメラ制御
- **NumPy** - 数値計算
- **Pillow** - 画像操作
- **Enhanced Vision Service** - 実機カメラ統合

### ネットワーク・通信
- **UDP Broadcast** - ドローン自動検出
- **Ping Scan** - ネットワーク診断
- **WebSocket** - リアルタイム双方向通信
- **HTTP/2** - 高性能API通信

### データ・ストレージ
- **PostgreSQL** - メインデータベース
- **Redis** - キャッシュ・セッション
- **YAML** - 設定ファイル
- **JSON** - API通信・ログ

### インフラ・運用
- **Docker + Docker Compose** - コンテナ化
- **nginx** - リバースプロキシ
- **Prometheus + Grafana** - 監視
- **GitHub Actions** - CI/CD

## 📚 Phase 6 ドキュメント

### 実機統合ガイド
- **[ユーザーガイド](./backend/docs/user_guide.md)** - 基本操作・設定手順
- **[API仕様書](./backend/docs/real_drone_api_specification.md)** - 実機対応API詳細
- **[ネットワーク設定ガイド](./backend/docs/network_configuration_guide.md)** - LAN設定・自動検出設定
- **[トラブルシューティング](./backend/docs/troubleshooting_real_drone.md)** - 問題解決・診断手順

### 技術仕様書
- **[Phase 6統合仕様](./backend/docs/plan/PHASE6_TELLO_INTEGRATION_README.md)** - 設計・実装詳細
- **[テスト仕様書](./backend/tests/test_phase6_real_simulation_switching.py)** - 包括的テストスイート

### 設定ファイル
```yaml
# config/drone_config.yaml - メイン設定
global:
  drone_mode: "auto"              # auto, simulation, real, hybrid
  space_bounds: [20.0, 20.0, 10.0]

drones:
  - id: "tello_001" 
    name: "メインドローン"
    mode: "real"                  # real, simulation, auto
    ip_address: "192.168.1.100"  # 手動指定またはnull（自動検出）
    auto_detect: true
```

### 環境変数
```bash
# Phase 6環境変数
DRONE_MODE=auto                   # 動作モード
TELLO_AUTO_DETECT=true           # 自動検出有効
TELLO_CONNECTION_TIMEOUT=10      # 接続タイムアウト（秒）
NETWORK_SCAN_ENABLED=true       # ネットワークスキャン有効
VISION_ENHANCED_MODE=true        # 拡張ビジョンモード
LOG_LEVEL=INFO                   # ログレベル
```

## ディレクトリ構成

このリポジトリは以下のディレクトリ構成で管理されています：

```
/
├── backend/                    # バックエンドAPI (Raspberry Pi)
│   ├── src/
│   │   ├── api/               # FastAPI ルート定義
│   │   │   ├── __init__.py
│   │   │   ├── drone.py       # ドローン操作API (飛行制御、カメラ制御)
│   │   │   ├── vision.py      # 物体認識・追跡API (学習データ管理、推論)
│   │   │   ├── models.py      # モデル管理API (学習、保存、読み込み)
│   │   │   └── dashboard.py   # ダッシュボードAPI (状態監視、制御)
│   │   ├── core/              # コアロジック
│   │   │   ├── drone_control.py   # ドローン制御機能 (djitellopy制御)
│   │   │   ├── vision_engine.py  # 映像処理・物体認識エンジン
│   │   │   ├── model_manager.py  # モデル管理機能 (学習、保存、読み込み)
│   │   │   └── dummy_drone.py    # ダミードローンシステム (テスト用)
│   │   ├── models/            # データモデル
│   │   │   ├── drone.py      # ドローン関連データモデル
│   │   │   ├── tracking.py   # 追跡関連データモデル
│   │   │   └── training.py   # 学習関連データモデル
│   │   ├── utils/             # ユーティリティ関数
│   │   └── config/            # 設定ファイル管理
│   ├── tests/                 # バックエンド単体テスト
│   │   ├── unit/             # 単体テストケース
│   │   ├── fixtures/         # テストデータ・フィクスチャ
│   │   └── conftest.py       # pytest設定
│   ├── requirements.txt       # Python依存関係
│   ├── Dockerfile            # Docker設定
│   └── README.md             # バックエンド開発ガイド
│
├── frontend/                   # 管理者用フロントエンド
│   ├── src/
│   │   ├── components/        # UIコンポーネント (React/Vue等)
│   │   ├── pages/             # ページコンポーネント
│   │   ├── services/          # API呼び出しサービス
│   │   ├── utils/            # フロントエンドユーティリティ
│   │   └── config/           # フロントエンド設定
│   ├── tests/                 # フロントエンド単体テスト
│   ├── public/                # 静的ファイル (HTML、画像等)
│   ├── doc/                   # フロントエンド設計ドキュメント
│   │   └── sample/            # サンプルHTML/CSS
│   │       └── README.md      # 画面設計提案書
│   ├── package.json           # Node.js依存関係 (Node.jsの場合)
│   ├── requirements.txt       # Python依存関係 (Pythonの場合)
│   └── README.md             # フロントエンド開発ガイド
│
├── mcp-server/                # MCPサーバ
│   ├── src/
│   │   ├── server.py          # MCPサーバメイン処理
│   │   ├── handlers/          # MCP要求ハンドラ
│   │   ├── clients/           # バックエンドAPIクライアント
│   │   └── config/           # MCP設定管理
│   ├── tests/                # MCPサーバテスト
│   ├── requirements.txt      # Python依存関係
│   └── README.md            # MCPサーバ開発ガイド
│
├── shared/                    # 共有リソース
│   ├── api-specs/             # OpenAPI定義
│   │   ├── backend-api.yaml  # バックエンドAPI仕様
│   │   └── mcp-api.yaml      # MCP API仕様
│   ├── config/                # 共通設定ファイル
│   │   ├── development.yaml  # 開発環境設定
│   │   ├── production.yaml   # 本番環境設定
│   │   └── test.yaml         # テスト環境設定
│   ├── schemas/               # データスキーマ定義
│   └── utils/                 # 共通ユーティリティ
│
├── tests/                     # 結合・システムテスト
│   ├── integration/           # 結合テスト
│   │   ├── api_integration/  # API結合テスト
│   │   ├── ui_integration/   # UI結合テスト
│   │   └── mcp_integration/  # MCP結合テスト
│   ├── system/                # システムテスト
│   │   ├── with_drone/        # ドローン接続テスト
│   │   └── without_drone/     # ドローンなしテスト
│   ├── fixtures/              # テストデータ・フィクスチャ
│   └── utils/                 # テストユーティリティ
│
├── docs/                      # ドキュメント
│   ├── api/                   # API仕様書・ドキュメント
│   ├── architecture/          # アーキテクチャ設計書
│   ├── deployment/            # デプロイ手順書
│   ├── development/           # 開発手順書
│   └── dummy_drone.md         # ダミードローンシステム設計書
│
├── deployment/                # デプロイ設定
│   ├── raspberry-pi/          # Raspberry Pi用設定
│   ├── windows/               # Windows用設定
│   ├── docker/                # Docker設定ファイル
│   └── kubernetes/            # Kubernetes設定（将来用）
│
├── scripts/                   # ビルド・デプロイスクリプト
│   ├── build.sh              # ビルドスクリプト
│   ├── deploy.sh             # デプロイスクリプト
│   ├── test.sh               # テストスクリプト
│   └── setup/                 # 環境セットアップスクリプト
│
├── .github/                   # GitHub Actions
│   └── workflows/
│       ├── ci.yml            # CI/CDワークフロー
│       ├── deploy-backend.yml # バックエンドデプロイ
│       └── deploy-frontend.yml # フロントエンドデプロイ
│
├── README.md                  # プロジェクト概要（このファイル）
├── CONTRIBUTING.md            # 開発ガイドライン
├── .gitignore                # Git除外設定
└── LICENSE                   # ライセンス
```

### ディレクトリ構成の特徴

1. **明確な分離**: 各コンポーネント（backend, frontend, mcp-server）を独立したディレクトリに配置し、それぞれが独立して開発・デプロイできる構成

2. **テスト階層**: 
   - 単体テストは各コンポーネント内に配置
   - 結合・システムテストは専用ディレクトリで管理
   - ドローンあり/なしテストの両方に対応

3. **共有リソース**: 
   - OpenAPI定義や共通設定を `shared/` で一元管理
   - 各コンポーネント間での重複を排除

4. **開発要件対応**: 
   - OpenAPI定義を `shared/api-specs/` で管理
   - 包括的テスト構造（単体・結合・システム）
   - ドローンなしテスト環境の構築

5. **デプロイ対応**: 
   - プラットフォーム別（Raspberry Pi, Windows）デプロイ設定
   - Docker/Kubernetes対応

6. **ドキュメント管理**: 
   - API仕様書、アーキテクチャ、デプロイ手順を体系的に管理
   - 各コンポーネントごとのREADMEで詳細な開発ガイドを提供

## 非機能要件

- ネットワーク
    - 家庭用ルータに接続するものとする
    - インターネット接続可能
    - 一般ユーザのデバイスは同一ネットワーク上に存在するものとする

- 対象とするドローン
    - [Tello EDU](https://www.ryzerobotics.com/jp/tello-edu)

- ドローンからの画像を受信し、AIモデルをもとに次の行動を決定、指示をドローンに送信するバックエンドシステム（APIサーバ）
    - [Raspberry Pi 5 8MB](https://www.raspberrypi.com/products/raspberry-pi-5/)
        - [Raspberry Pi OS Lite 64bit May 6th 2025](https://www.raspberrypi.com/software/operating-systems/)
            - [Python 3.11](https://www.python.org/downloads/release/python-3110/)
            - [FastAPI](https://fastapi.tiangolo.com/ja/)
            - [djitellopy](https://github.com/damiafuentes/DJITelloPy)

- フロントエンドシステム
    - Windows11 Pro 64bit
        - NodeでもPythonでもよい

- 一般ユーザクライアント
    - iPad Air 13インチ第5世代
        - iOS 17.0.3
          - Safari

## 開発方針

- 作業は冒頭にまず計画をたて、実施許可を受けること
- 作業は完了したら必ずレビューを行う
- APIサーバはかならずOpenAPI定義を設計してから行うこと
- 単体テストは必ず実施
    - パブリック関数を極値・異常値すべてのケースを実施
    - カバレッジテストも別途行う
- 結合テストも必ず実施
    - すべての機能を全網羅
    - 画面操作の場合は、極値・異常値すべてのケースを実施
    - ドローンなしテストとする
        - 基本ドローンがなくてもテストできるようにモック・ドライバを作成する
- システムテストは簡単に実施できるような状態にしておく
    - ドローンを繋いだ状態でのテスト
    - 結合テストとおなじシナリオ、ケースを実施する

<p align="right">以上</p>
