# MCP Drone Server - Node.js/TypeScript版

Tello EDU ドローン制御システム用のMCP (Model Context Protocol) サーバーのNode.js/TypeScript実装です。

## 概要

このプロジェクトは、既存のPython版MCPサーバーをNode.js/TypeScriptに移行したものです。Claude AIとの統合を通じて、自然言語でのドローン制御機能を提供します。

## 主な機能

- **MCP Protocol対応**: Model Context Protocolを使用したClaude統合
- **包括的ドローン制御**: 離陸・着陸・移動・回転・緊急停止
- **カメラ操作**: 写真撮影・ストリーミング制御
- **ビジョンAPI**: 物体検出・追跡・データセット管理
- **モデル管理**: AI学習モデルの作成・管理・学習ジョブ監視
- **ダッシュボード機能**: システム状態・ドローン群監視
- **自動スキャン**: ネットワーク上のドローン自動検出
- **ヘルスチェック**: システム健全性監視
- **接続テスト**: バックエンドAPI連携の自動検証
- **TypeScript厳密設定**: 型安全性を重視した実装
- **包括的テスト**: 単体テスト・統合テスト・接続テストによる品質保証

## 技術スタック

- **ランタイム**: Node.js 18+
- **言語**: TypeScript 5.0+
- **MCP SDK**: @modelcontextprotocol/sdk
- **HTTPクライアント**: axios
- **ログ**: winston
- **バリデーション**: zod
- **テスト**: Jest + ts-jest
- **コード品質**: ESLint + Prettier

## セットアップ

### 前提条件

- Node.js 18.0.0以上
- npm または yarn
- バックエンドAPI（FastAPI）が起動していること

### インストール

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-server-nodejs

# 依存関係インストール
npm install

# TypeScriptビルド
npm run build
```

### 環境設定

環境変数またはプロジェクトルートに`.env`ファイルを作成:

```bash
# MCP server settings
MCP_PORT=3001
BACKEND_URL=http://localhost:8000
LOG_LEVEL=info
TIMEOUT=10000
```

## 使用方法

### 開発モード

```bash
# 開発サーバー起動（ホットリロード付き）
npm run dev
```

### 本番モード

```bash
# ビルドして起動
npm run build
npm start
```

### テスト実行

```bash
# 単体テスト
npm test

# テストウォッチモード
npm run test:watch

# カバレッジレポート
npm run test:coverage

# バックエンドAPI接続テスト
npm run test:connection
```

### コード品質チェック

```bash
# ESLintチェック
npm run lint

# ESLint自動修正
npm run lint:fix

# Prettierフォーマット
npm run format

# フォーマットチェック
npm run format:check
```

## MCPツール

このサーバーは以下のMCPツールを提供します:

### 1. get_drone_status
ドローンの現在状態を取得します。

```json
{
  "name": "get_drone_status",
  "arguments": {
    "droneId": "optional-drone-id"
  }
}
```

### 2. scan_drones
ネットワーク上のドローンをスキャンします。

```json
{
  "name": "scan_drones",
  "arguments": {}
}
```

### 3. health_check
システムの健全性をチェックします。

```json
{
  "name": "health_check",
  "arguments": {}
}
```

### 4. get_system_status
システム全体の状態を取得します。

```json
{
  "name": "get_system_status",
  "arguments": {}
}
```

## アーキテクチャ

### ディレクトリ構造

```
src/
├── index.ts                 # エントリーポイント
├── server/                  # MCPサーバー実装
│   └── MCPDroneServer.ts
├── services/                # ビジネスロジック
│   └── DroneService.ts
├── clients/                 # 外部API通信
│   └── BackendClient.ts
├── types/                   # 型定義
│   ├── index.ts             # 基本型定義
│   └── api_types.ts         # バックエンドAPI型定義
├── utils/                   # ユーティリティ
│   ├── logger.ts
│   └── errors.ts
├── config/                  # 設定管理
│   └── index.ts
└── test/                    # テスト関連
    ├── setup.ts             # テスト共通設定
    └── connection-test.ts   # バックエンド接続テスト
```

### 主要コンポーネント

1. **MCPDroneServer**: MCP Protocolの実装、ツールハンドリング
2. **DroneService**: ドローン関連のビジネスロジック、キャッシュ管理
3. **BackendClient**: FastAPI バックエンドとの通信
4. **ErrorHandler**: 統一されたエラーハンドリング
5. **Logger**: 構造化ログ出力

## 設定

### TypeScript設定

- 厳密な型チェック有効
- ES2022ターゲット
- ESModules使用
- パスエイリアス対応（@/で開始）

### ESLint設定

- TypeScript推奨ルール
- any型の使用禁止
- 明示的な戻り値型指定
- Prettier統合

### Jest設定

- ts-jest使用
- カバレッジ閾値80%
- パスエイリアス対応
- ESModules対応

## トラブルシューティング

### よくある問題

#### 1. バックエンドAPI接続エラー

```bash
Error: Backend connection failed: http://localhost:8000
```

**解決方法**:
- FastAPIサーバーが起動していることを確認
- `BACKEND_URL`環境変数が正しく設定されていることを確認
- ファイアウォールの設定を確認

**接続テストの実行**:
```bash
# バックエンドとの接続を包括的にテスト
npm run test:connection

# 特定のバックエンドURLでテスト
BACKEND_URL=http://localhost:8001 npm run test:connection
```

#### 2. MCP SDK エラー

```bash
Error: Unable to start MCP server
```

**解決方法**:
- Node.js バージョンが18.0.0以上であることを確認
- 依存関係を再インストール: `rm -rf node_modules && npm install`

#### 3. TypeScript コンパイルエラー

```bash
Error: Cannot find module '@/types/index.js'
```

**解決方法**:
- `npm run build`でTypeScriptをコンパイル
- `tsconfig.json`のパス設定を確認

### デバッグ

詳細なログ出力を有効にするには:

```bash
LOG_LEVEL=debug npm run dev
```

ログファイルの確認:

```bash
# エラーログ
tail -f logs/error.log

# 全体ログ  
tail -f logs/combined.log
```

## 開発

### コントリビュート

1. フォークしてブランチを作成
2. 変更を実装
3. テストを追加・実行
4. リントチェック通過
5. プルリクエスト作成

### テスト戦略

- 単体テスト: 各モジュールの動作検証
- 統合テスト: モジュール間の連携検証
- モック: 外部依存関係のモック化
- カバレッジ: 80%以上の維持

### コーディング規約

- TypeScript厳密設定準拠
- ESLint + Prettier使用
- 日本語コメント推奨
- 関数・クラスの単一責任原則
- エラーハンドリング必須

## ライセンス

MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照

## 関連プロジェクト

- [Python版MCPサーバー](../mcp-server/)
- [FastAPIバックエンド](../backend/)
- [Reactフロントエンド](../frontend/)

## サポート

問題や質問がある場合は、GitHub Issuesで報告してください:
https://github.com/coolerking/mfg_drone_by_claudecode/issues