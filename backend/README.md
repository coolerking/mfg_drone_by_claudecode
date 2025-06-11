# MFG Drone Backend API

Tello EDU自動追従撮影システムのバックエンドAPI

## 📋 プロジェクト概要

MFG Drone Backend API は、DJI Tello EDU ドローンを使用した自動追従撮影システムのコアとなるバックエンドサービスです。AI による物体認識・追跡、リアルタイム映像配信、包括的なドローン制御機能を提供します。

### 🎯 主要機能

- **ドローン制御**: 接続、飛行、移動、回転、緊急停止
- **リアルタイム映像配信**: 30fps HD映像ストリーミング
- **AI物体認識・追跡**: カスタムモデルによる自動追従
- **センサーデータ取得**: バッテリー、高度、姿勢角、温度等
- **カメラ操作**: 写真撮影、動画録画、設定変更
- **高度な移動制御**: 3D座標移動、曲線飛行、リアルタイム制御

### 🏗️ システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                    MFG Drone System                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend Apps          Backend API         Hardware        │
│  ┌─────────────┐       ┌─────────────┐    ┌─────────────┐   │
│  │ Admin UI    │◄─────►│ FastAPI     │◄──►│ Tello EDU   │   │
│  │ (Flask)     │       │ (Python)    │    │ Drone       │   │
│  └─────────────┘       │             │    └─────────────┘   │
│  ┌─────────────┐       │ ┌─────────┐ │    ┌─────────────┐   │
│  │ User UI     │◄─────►│ │AI/CV    │ │    │ Raspberry   │   │
│  │ (Flask)     │       │ │OpenCV   │ │    │ Pi 5        │   │
│  └─────────────┘       │ └─────────┘ │    └─────────────┘   │
│                        └─────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 技術スタック

| 分野 | 技術 | バージョン |
|------|------|-----------|
| **言語** | Python | 3.11+ |
| **Webフレームワーク** | FastAPI | 0.104+ |
| **ASGIサーバー** | Uvicorn | 0.24+ |
| **ドローンSDK** | djitellopy | 2.5.0 |
| **画像処理** | OpenCV | 4.8+ |
| **科学計算** | NumPy | 1.24+ |
| **データ検証** | Pydantic | 2.0+ |
| **テスト** | pytest | 7.0+ |
| **実行環境** | Raspberry Pi OS | 64-bit |

## 🚀 クイックスタート

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend

# 仮想環境作成・アクティベート
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt

# 開発サーバー起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API確認

```bash
# ヘルスチェック
curl http://localhost:8000/health

# APIドキュメント確認
# http://localhost:8000/docs      (Swagger UI)
# http://localhost:8000/redoc     (ReDoc)
```

## 📚 完全ドキュメント

### 🏛️ 設計・仕様書

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| **[システム構成図](doc/system_architecture.md)** | 全体アーキテクチャ、ネットワーク構成、技術スタック | システム設計者、開発者 |
| **[システムコンテキスト図](doc/system_context.md)** | 外部アクター、セキュリティ境界、データ交換フロー | プロジェクトマネージャー、設計者 |
| **[ユースケース設計](doc/use_cases.md)** | 機能要件、シーケンス図、アクター定義 | ビジネスアナリスト、設計者 |
| **[方式設計書](doc/design_specification.md)** | アーキテクチャパターン、品質属性、技術選定理由 | シニア開発者、アーキテクト |

### 📖 API・技術仕様

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| **[API仕様書](doc/api_specification.md)** | REST API、WebSocket、エラーコード、使用例 | フロントエンド開発者、統合担当者 |
| **[用語集](doc/glossary.md)** | ドローン用語、AI用語、技術用語、略語辞典 | 全プロジェクトメンバー |

### 🛠️ 開発・運用ガイド

| ドキュメント | 内容 | 対象者 |
|-------------|------|--------|
| **[セットアップ手順](doc/setup_guide.md)** | 開発環境・本番環境構築、Raspberry Pi設定 | 開発者、インフラ担当者 |
| **[テスト実行手順](doc/testing_guide.md)** | 単体〜E2Eテスト、性能テスト、品質保証 | 開発者、QAエンジニア |
| **[運用手順](doc/operation_guide.md)** | 監視、メンテナンス、トラブルシューティング | 運用担当者、SRE |

## 🔧 開発者向け情報

### プロジェクト構造

```
backend/
├── main.py                 # FastAPIアプリケーションエントリーポイント
├── dependencies.py         # 依存性注入設定
├── openapi.yaml           # OpenAPI仕様書
├── requirements.txt       # 本番依存関係
├── test_requirements.txt  # テスト依存関係
├── pyproject.toml         # プロジェクト設定
├── config/                # 設定ファイル
│   └── test_config.py
├── models/                # Pydanticデータモデル
│   ├── requests.py
│   └── responses.py
├── routers/               # FastAPIルーター
│   ├── connection.py      # ドローン接続管理
│   ├── flight_control.py  # 基本飛行制御
│   ├── movement.py        # 基本移動制御
│   ├── advanced_movement.py # 高度移動制御
│   ├── camera.py          # カメラ操作
│   ├── sensors.py         # センサーデータ
│   ├── settings.py        # 設定管理
│   ├── mission_pad.py     # ミッションパッド
│   ├── tracking.py        # 物体追跡
│   └── model.py           # AIモデル管理
├── services/              # ビジネスロジック層
│   └── drone_service.py   # ドローンサービス（659行）
├── tests/                 # テストスイート
│   ├── conftest.py        # pytest設定
│   ├── fixtures/          # テストフィクスチャ
│   ├── stubs/             # モック・スタブ
│   └── test_*.py          # テストファイル群（21ファイル）
├── doc/                   # プロジェクトドキュメント
└── tmp/                   # 一時作業ディレクトリ
```

### 開発ワークフロー

1. **機能開発**: 新機能実装
2. **単体テスト**: `pytest tests/ -m unit`
3. **統合テスト**: `pytest tests/ -m integration`
4. **コード品質**: `flake8`, `black`, `pylint`
5. **API確認**: Swagger UI でAPI動作確認
6. **E2Eテスト**: 実機ドローンでの動作確認

### テスト実行

```bash
# 全テスト実行
pytest tests/

# 単体テストのみ
pytest tests/ -m unit

# カバレッジ付きテスト
pytest tests/ --cov=. --cov-report=html

# 実機テスト（ドローン接続必要）
pytest tests/ -m e2e
```

## 📊 API エンドポイント概要

### 基本制御 API

| カテゴリ | エンドポイント数 | 主要機能 |
|---------|----------------|----------|
| **システム** | 2 | ヘルスチェック、API情報 |
| **接続管理** | 2 | ドローン接続・切断 |
| **飛行制御** | 4 | 離陸、着陸、緊急停止、ホバリング |
| **移動制御** | 6 | 基本移動、回転、宙返り、座標移動 |
| **カメラ** | 7 | ストリーミング、撮影、設定 |
| **センサー** | 10 | 状態、バッテリー、姿勢角等 |

### 高度機能 API

| カテゴリ | エンドポイント数 | 主要機能 |
|---------|----------------|----------|
| **設定管理** | 3 | WiFi、速度、任意コマンド |
| **ミッションパッド** | 5 | 検出制御、基準移動 |
| **物体追跡** | 3 | 追跡開始・停止・状態 |
| **AIモデル** | 2 | モデル訓練・一覧 |

**総計**: 44 エンドポイント + WebSocket 2接続

## 🎯 実装済み機能

### ✅ 完成機能

- **ドローン制御**: 完全実装（接続〜飛行〜着陸）
- **映像ストリーミング**: WebSocket対応、30fps配信
- **センサーデータ**: 全センサー対応、リアルタイム取得
- **API仕様**: OpenAPI 3.0完全準拠、44エンドポイント
- **テストフレームワーク**: 単体〜E2E、カバレッジ80%+
- **ドキュメント**: 包括的技術文書、運用手順

### 🚧 実装中・今後の予定

- **HTTPS/TLS**: セキュリティ強化
- **ユーザー認証**: JWT ベース認証システム
- **データベース**: 永続化・ログ管理
- **マルチドローン**: 複数機体同時制御
- **クラウド連携**: AWS/Azure統合

## 🔒 セキュリティ

### 現在の実装

- **入力検証**: Pydantic によるデータバリデーション
- **エラーハンドリング**: 包括的例外処理
- **ネットワーク分離**: プライベートネットワーク運用
- **ログ管理**: 構造化ログ、ローテーション

### 今後の強化

- HTTPS/TLS 暗号化
- API キー認証
- レート制限
- セキュリティヘッダー

## 📈 性能仕様

| 項目 | 仕様 | 測定方法 |
|------|------|---------|
| **API応答時間** | < 100ms (95%ile) | 性能テスト |
| **映像遅延** | < 200ms | E2Eテスト |
| **同時接続** | 10クライアント | 負荷テスト |
| **AI処理** | < 50ms/frame | 統合テスト |
| **可用性** | 99.9% target | 監視システム |

## 🤝 コントリビューション

### 開発参加手順

1. **Issue確認**: [Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
2. **ブランチ作成**: `feature/your-feature-name`
3. **実装・テスト**: コード実装 + テスト追加
4. **プルリクエスト**: レビュー依頼
5. **マージ**: レビュー完了後

### コーディング規約

- **Python**: PEP 8 準拠
- **型ヒント**: 必須
- **テスト**: 新機能は100%カバレッジ
- **ドキュメント**: APIの変更は仕様書更新

## 📞 サポート・お問い合わせ

### ドキュメント・参考資料

- **[プロジェクトWiki](https://github.com/coolerking/mfg_drone_by_claudecode/wiki)**: 詳細ガイド
- **[API仕様書](doc/api_specification.md)**: 完全なAPI リファレンス
- **[開発者ガイド](doc/setup_guide.md)**: 環境構築から運用まで

### 技術サポート

- **Issues**: [GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- **Discussion**: [GitHub Discussions](https://github.com/coolerking/mfg_drone_by_claudecode/discussions)

## 📄 ライセンス

このプロジェクトは [MIT License](../LICENSE) の下で公開されています。

---

## 🔗 関連リンク

### 外部ドキュメント

- **[Tello SDK Documentation](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)**: 公式SDK仕様
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**: Webフレームワーク
- **[OpenCV Documentation](https://docs.opencv.org/)**: 画像処理ライブラリ

### プロジェクト構成

- **Backend API**: 📍 **このディレクトリ**
- **[Frontend Admin](../frontend/admin/)**: 管理者向けWebアプリ
- **[Frontend User](../frontend/user/)**: 一般ユーザー向けWebアプリ

---

<div align="center">

**🚁 MFG Drone Backend API**  
*Tello EDU自動追従撮影システム*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Made with ❤️ for autonomous drone filming

</div>