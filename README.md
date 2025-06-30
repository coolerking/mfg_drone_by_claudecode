# MFG ドローン - 自動追従撮影システム

Tello EDU ドローンを使って移動する対象物を自動的に追跡・撮影するシステムです。

## 機能

1. 手動運転機能
    - ユーザが指示したとおりにドローンを操作する

2. 物体追随機能
    1. 追随物体学習データ管理
        - ドローンのカメラ機能をつかって、対象の写真を撮る
        - 複数撮影し学習データセットとして管理する
        - 外部で殺青した複数の写真を登録して学習データセットとして管理できるようにする
    2. 追随物体モデル管理
    - 学習データセットを選択して追随物体モデルを学習する
    - 学習済みのモデルを管理する

3. 自動運転機能（物体追随）
    - ユーザが指示したモデルを使って物体を正面に捉えるように自動的に移動する
    - ユーザが指示したら手動運転に戻る
    - 追随物体がみあたらないなどの問題が発生したら安全に緊急停止する
    - 緊急停止したらユーザの指示で再度手動運転できるようにする

4. ドローン管理機能
    - 複数のドローンを登録できるようにする
    - 登録ドローンがない場合はダミードローンシステムに接続される
    - 現在の動作状態を確認するダッシュボード画面

## システム構成

このシステムは以下の3つの主要コンポーネントで構成されています:

1. **バックエンドAPI** (Raspberry Pi 5)
   - ドローン制御
   - ビデオ処理
   - 物体認識と追跡
   - ダミードローン(実機がない場合)

2. **管理者用フロントエンド** (Windows PC)
   - 物体認識モデルのトレーニング
   - ドローン制御
   - 追跡開始/停止
   - Web UIからバックエンドAPIサーバのAPIを呼び出す

3. **MCPサーバ** (Windows PC)
   - MCPクライアントからMCPサーバ経由でバックエンドAPIを呼び出して操作できるようにする

4. **ドローン**
  - Tello EDU のみを使用する
  - 同じネットワーク上にIPアドレス指定で呼び出せる状態とする
  - 複数台の可能性あり、ゼロの場合もあり

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
│   └── development/           # 開発手順書
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
