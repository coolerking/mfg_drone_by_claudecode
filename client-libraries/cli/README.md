# MCPドローンCLI

MCPドローン制御サーバー用のコマンドラインインターフェース。自然言語コマンドやダイレクトAPI呼び出しでドローンを操作できる便利なツールです。

## 概要（Description）

MCP Drone CLI は、MCPドローン制御サーバー向けのコマンドラインインターフェースです。日本語自然言語コマンドによる直感的なドローン操作、完全なドローン制御機能、カメラ・システム監視、WebSocketリアルタイム通信をサポートします。対話的設定、バッチ処理、並列実行、美しいカラー出力により、効率的なドローン制御体験を提供し、開発者・研究者・業務利用者に最適なCLIツールです。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### グローバルインストール

```bash
npm install -g mcp-drone-cli
```

### ローカルインストール

```bash
npm install mcp-drone-cli
npx mcp-drone --help
```

### ソースからインストール

```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/cli
npm install
npm run build
npm link
```

## 使い方（Usage）

### 基本セットアップ

```bash
# CLI設定
mcp-drone configure
```

設定項目：
- MCPサーバーURL (デフォルト: http://localhost:8001)
- API Key (オプション)
- Bearer Token (オプション)
- リクエストタイムアウト (デフォルト: 30000ms)

### システム状態確認

```bash
mcp-drone system
mcp-drone health
```

### ドローン一覧表示

```bash
mcp-drone drones
mcp-drone drones --available
```

### 自然言語コマンド実行

```bash
mcp-drone exec "ドローンAAに接続して"
mcp-drone exec "離陸して"
mcp-drone exec "右に50センチ移動して"
mcp-drone exec "写真を撮って"
mcp-drone exec "着陸して"
```

### ダイレクトコマンド実行

```bash
# ドローン管理
mcp-drone connect drone_001
mcp-drone status drone_001
mcp-drone disconnect drone_001

# 飛行制御
mcp-drone takeoff drone_001 --height 100
mcp-drone move drone_001 forward 100
mcp-drone rotate drone_001 clockwise 90
mcp-drone land drone_001
mcp-drone emergency drone_001

# カメラ操作
mcp-drone photo drone_001 --filename "photo.jpg" --quality high
```

### バッチコマンド実行

```bash
# 順次実行
mcp-drone batch "ドローンAAに接続して" "離陸して" "写真を撮って"

# 並列実行
mcp-drone batch "写真を撮って" "高度を確認して" --mode parallel

# エラー時続行
mcp-drone batch "command1" "command2" --no-stop-on-error
```

### 高度な使用法

```bash
# ドライラン実行
mcp-drone exec "緊急停止して" --dry-run

# コンテキスト指定
mcp-drone exec "離陸して" --context '{"drone_id": "drone_001"}'

# 実行前確認
mcp-drone exec "離陸して" --confirm

# リアルタイム監視
mcp-drone watch
```

## 動作環境・要件（Requirements）

### システム要件

- **Node.js**: 16+
- **npm**: 6+
- **OS**: Linux, Windows, macOS
- **ターミナル**: UTF-8対応コマンドライン環境

### ネットワーク要件

- **MCPサーバー**: ポート8001での通信
- **WebSocket**: リアルタイム通信用
- **ファイアウォール**: localhost通信許可

### 依存関係

- **TypeScript**: 5.0+
- **Commander.js**: CLI フレームワーク
- **Inquirer.js**: 対話的プロンプト
- **Chalk**: カラー出力
- **WebSocket**: リアルタイム通信

## ディレクトリ構成（Directory Structure）

```
cli/
├── package.json           # NPMパッケージ定義
├── src/                   # ソースコード
│   └── index.ts          # メインCLIアプリケーション
├── bin/                   # 実行可能ファイル
│   └── mcp-drone         # CLIエントリーポイント
├── tsconfig.json         # TypeScript設定
└── README.md             # CLIドキュメント
```

### 主要機能

#### 自然言語処理
- **日本語コマンドサポート**: 自然な日本語フレーズでドローン操作
- **意図認識**: コマンドの自動解析と信頼度スコアリング
- **パラメータ抽出**: 距離・角度・高度の自動抽出
- **エラー修正提案**: 誤解されたコマンドの修正支援

#### ドローン制御
- **接続管理**: ドローン接続・切断・状態監視
- **飛行制御**: 安全チェック付き離着陸・緊急停止
- **移動制御**: cm精度での正確な位置決め
- **回転制御**: 度単位精度での回転制御
- **高度制御**: 絶対・相対高度調整

#### システム機能
- **バッチ処理**: 複数コマンドの順次・並列実行
- **リアルタイム監視**: WebSocketによるイベント監視
- **設定管理**: YAML・環境変数による設定
- **エラーハンドリング**: 詳細エラーメッセージと終了コード

### 自然言語コマンド例

| コマンドタイプ | 例 |
|-------------|---|
| 接続 | `ドローンAAに接続して`, `ドローンに繋げて` |
| 離陸 | `離陸して`, `ドローンを起動して`, `飛び立って` |
| 移動 | `右に50センチ移動して`, `前に1メートル進んで` |
| 回転 | `右に90度回転して`, `左に45度向きを変えて` |
| 高度 | `高度を1メートルにして`, `2メートルの高さまで上がって` |
| カメラ | `写真を撮って`, `撮影して`, `カメラで撮って` |
| 着陸 | `着陸して`, `降りて`, `ドローンを着陸させて` |
| 緊急 | `緊急停止して`, `止まって`, `ストップ` |

## 更新履歴（Changelog/History）

### 1.0.0: 初期リリース（最新）
- **MCPサーバー統合**: 完全なMCP API対応
- **自然言語処理**: 日本語コマンド認識・解析
- **リアルタイム監視**: WebSocketイベント監視
- **設定管理**: YAML・環境変数対応
- **美しいCLI**: カラー出力・プログレス表示

### 0.9.0: ベータ版
- **コア機能実装**: 基本ドローン制御コマンド
- **バッチ処理**: 複数コマンド実行機能
- **エラーハンドリング**: 包括的エラー処理

### 0.8.0: アルファ版
- **プロトタイプ実装**: 基本CLI フレームワーク
- **TypeScript対応**: 型安全な実装
- **テスト環境**: 単体テスト基盤

---

**ライセンス**: MIT License

**サポート**: 問題・質問は[GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)までお寄せください。