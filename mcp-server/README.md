# MCPサーバー（Python版・レガシー） - 自然言語ドローン制御システム

**⚠️ 重要: この Python版MCPサーバーはレガシーです。新規利用・開発には [Node.js版MCPサーバー](../mcp-server-nodejs) をご利用ください。**

Claude統合による自然言語処理を活用したドローン制御APIサーバーです（Python版・保守のみ）。

## 概要（Description）

MCPサーバーは、MFG ドローン自動追従撮影システムの重要な構成要素として、Claude Code AI アシスタントと連携し、自然言語によるドローン制御を可能にします。Model Context Protocol（MCP）に準拠した高性能サーバーとして実装され、日本語の自然言語処理エンジンを内蔵し、複雑なドローン操作を直感的な日本語コマンドで実行できます。

### 主な特徴
- **自然言語処理**: 日本語によるドローン制御コマンドの理解と実行
- **Claude統合**: AI支援による高度なコマンド解釈
- **バックエンド連携**: メインAPIサーバーとのシームレスな通信
- **バッチ処理**: 複数コマンドの一括実行と依存関係管理
- **リアルタイム制御**: WebSocketによる即座のドローン応答

### 解決する課題
- ドローン制御の技術的障壁を自然言語で解決
- 複雑な操作手順の簡素化
- AI支援による直感的なユーザーインターフェース
- プログラミング知識なしでの高度なドローン制御

## 目次（Table of Contents）

1. [概要（Description）](#概要description)
2. [インストール方法（Installation）](#インストール方法installation)
3. [使い方（Usage）](#使い方usage)
4. [動作環境・要件（Requirements）](#動作環境要件requirements)
5. [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
6. [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### 前提条件
- **Python 3.9以上**: 自然言語処理機能に必要
- **バックエンドAPIサーバー**: メインドローン制御システムが稼働していること

### 基本セットアップ

#### 1. 依存関係のインストール
```bash
cd mcp-server
pip install -r requirements.txt
```

#### 2. 環境設定ファイルの作成
```bash
cp .env.example .env
# .env ファイルを編集して必要な設定値を入力
```

#### 3. サーバーの起動
```bash
python start_mcp_server_unified.py
```

### デバッグモード起動
```bash
python start_mcp_server_unified.py --log-level DEBUG
```

## 使い方（Usage）

### 基本的な使用方法

#### 1. サーバーの起動
```bash
# MCPサーバーを起動
python start_mcp_server_unified.py
```

#### 2. MCPクライアントとの接続

MCPサーバーはModel Context Protocolに準拠しており、Claude Desktop、VS Code、その他のMCPクライアントから利用できます。

サーバーが起動すると、以下のツールが利用可能になります：
- `connect_drone`: ドローンへの接続
- `takeoff_drone`: ドローンの離陸
- `land_drone`: ドローンの着陸
- `move_drone`: ドローンの移動
- `rotate_drone`: ドローンの回転
- `take_photo`: 写真撮影
- `execute_natural_language_command`: 自然言語コマンドの実行
- `emergency_stop`: 緊急停止

#### 3. 自然言語コマンドの使用例

MCPクライアントから `execute_natural_language_command` ツールを使用して、日本語でドローンを制御できます：

```json
{
  "command": "ドローンを離陸させて前に50センチ進んでください",
  "drone_id": "drone_AA"
}
```

### サンプルコマンド

#### 基本操作
- "ドローンを離陸させて"
- "ドローンを着陸させて"

#### 移動制御
- "前進して"
- "後退して"
- "左に移動して"

#### 高度制御
- "高度50センチで飛行して"
- "上に1メートル移動"
- "高度90センチで飛行"
- "下に2メートル移動"

#### 撮影機能
- "写真を撮って"
- "動画撮影を開始して"
- "学習データを収集して"

#### システム操作
- "ドローンの状態を確認"
- "システムの状態を確認"
- "バッテリー残量を確認"

### MCP仕様

MCPサーバーは標準入出力を使用してModel Context Protocolに準拠した通信を行います。HTTP APIは提供されません。MCPクライアント（Claude Desktop、VS Code拡張など）から利用してください。

## 動作環境・要件（Requirements）

### ハードウェア要件
- **CPU**: Intel i3 / AMD Ryzen 3 以上
- **メモリ**: 4GB RAM以上（自然言語処理のため）
- **ストレージ**: 2GB以上の空き容量
- **ネットワーク**: バックエンドAPIサーバーとの通信可能な環境

### ソフトウェア要件

#### Python環境
- **Python**: 3.9以上
- **主要ライブラリ**:
  - mcp 1.0.0+ (Model Context Protocol SDK)
  - spaCy 3.7.2+ (自然言語処理)
  - mecab-python3 1.0.6+ (日本語形態素解析)
  - pydantic 2.5.0+ (データ検証)
  - structlog 23.2.0+ (ロギング)

#### 外部サービス
- **バックエンドAPIサーバー**: http://localhost:8000 (デフォルト)
- **Claude Code API**: Claude統合機能使用時

### 環境変数設定

| 変数名 | デフォルト値 | 説明 |
|--------|------------|------|
| `BACKEND_API_URL` | http://localhost:8000 | バックエンドAPIのURL |
| `BACKEND_API_TIMEOUT` | 30 | バックエンドAPI通信タイムアウト |
| `BACKEND_API_KEY` | - | バックエンドAPIキー |
| `DEFAULT_LANGUAGE` | ja | デフォルト言語 |
| `NLP_CONFIDENCE_THRESHOLD` | 0.7 | 自然言語処理の信頼度閾値 |
| `LOG_LEVEL` | INFO | ログレベル |

## ディレクトリ構成（Directory Structure）

```
mcp-server/
├── src/                        # ソースコード
│   ├── core/                   # コアサービス
│   │   ├── backend_client.py       # バックエンドAPIクライアント
│   │   ├── nlp_engine.py           # 自然言語処理エンジン
│   │   └── command_router.py       # コマンドルーティングロジック
│   ├── models/                 # データモデル
│   │   ├── command_models.py       # コマンドモデル
│   │   ├── drone_models.py         # ドローンモデル
│   │   ├── camera_models.py        # カメラモデル
│   │   └── system_models.py        # システムモデル
│   └── mcp_main.py             # MCPサーバーメイン実装
├── config/                     # 設定ファイル
│   ├── settings.py             # アプリケーション設定
│   └── logging.py              # ロギング設定
├── tests/                      # テストファイル
├── docs/                       # ドキュメント
├── requirements.txt            # Python依存関係
├── start_mcp_server_unified.py # 統合起動スクリプト
├── .env.example                # 環境変数テンプレート
└── README.md                   # このファイル
```

### 主要コンポーネント

- **src/mcp_main.py**: MCPサーバーメイン実装
- **src/core/nlp_engine.py**: 日本語自然言語処理エンジン
- **src/core/backend_client.py**: バックエンドAPI通信クライアント
- **src/core/command_router.py**: コマンドルーティングシステム
- **config/settings.py**: 設定管理システム

### テスト構成

- **tests/test_nlp_engine.py**: 自然言語処理テスト
- **tests/test_mcp_server.py**: MCPサーバーテスト
- **tests/test_backend_client.py**: バックエンド通信テスト

## 更新履歴（Changelog/History）

### Version 2.0.0 - Phase 6 統合完了 (2025-01-15)
- ✅ **実機統合**: Tello EDU実機制御との完全統合
- ✅ **ハイブリッド運用**: 実機・シミュレーション環境対応
- ✅ **セキュリティ強化**: API認証・レート制限・セキュリティヘッダー
- ✅ **監視システム**: Prometheus・Grafana統合
- ✅ **Docker対応**: 本番環境コンテナ構成

### Version 1.5.0 - Phase 5 Webダッシュボード統合 (2024-12-20)
- ✅ **Webダッシュボード連携**: リアルタイム監視インターフェース対応
- ✅ **WebSocket拡張**: 双方向リアルタイム通信
- ✅ **バッチ処理改善**: 依存関係分析と最適化
- ✅ **エラー処理強化**: スマート回復機能

### Version 1.2.0 - Phase 4 セキュリティ・監視強化 (2024-12-10)
- ✅ **セキュリティ**: API認証・レート制限実装
- ✅ **監視・アラート**: 閾値ベース監視システム
- ✅ **パフォーマンス最適化**: システム監視・最適化
- ✅ **ビジョンAI連携**: YOLOv8物体検出統合

### Version 1.0.0 - Phase 2 拡張機能実装 (2024-11-25)
- ✅ **拡張NLP**: 高度な自然言語処理エンジン
- ✅ **コンテキスト理解**: 文脈を考慮したコマンド解釈
- ✅ **インテリジェントバッチ**: 依存関係を考慮した最適実行
- ✅ **実行分析**: コマンド実行統計・分析機能

### Version 0.8.0 - Phase 1 基盤実装 (2024-11-10)
- ✅ **基盤システム**: MCPベースサーバー構築
- ✅ **基本NLP**: 日本語自然言語処理（spaCy + MeCab）
- ✅ **コマンドルーティング**: 基本的なコマンド解釈・実行
- ✅ **バックエンド連携**: RESTful API通信実装
- ✅ **基本バッチ処理**: 複数コマンド順次実行

---

**🤖 Claude統合による直感的なドローン制御を実現**