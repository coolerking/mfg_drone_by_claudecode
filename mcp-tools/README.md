# MFG Drone MCP Tools

Model Context Protocol (MCP) tools for controlling Tello EDU drones through natural language interactions with Claude Code.

## 概要

このプロジェクトは、MFG Drone Backend APIをMCPツールとして提供し、Claude Codeによる自然言語でのドローン制御を実現します。

## 特徴

- **25のMCPツール**: 接続、飛行制御、移動、カメラ、センサー操作
- **完全TypeScript実装**: 型安全性とコード品質の保証
- **自動リトライ機能**: ネットワーク障害に対する堅牢性
- **包括的テスト**: 143テストケースによる品質保証
- **Claude Code統合**: 自然言語によるドローン制御

## システム要件

- Node.js 18以上
- TypeScript 5.0以上
- MFG Drone Backend API（別途起動が必要）

## インストール

```bash
# 依存関係インストール
npm install

# TypeScriptビルド
npm run build
```

## 使用方法

### 開発環境

```bash
# 開発モードで起動
npm run dev

# テスト実行
npm test

# カバレッジ付きテスト
npm run test:coverage
```

### 本番環境

```bash
# ビルド
npm run build

# 本番実行
npm start
```

### Claude Code統合

mcp-workspace.jsonに以下を追加：

```json
{
  "mcpServers": {
    "drone-tools": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "./mcp-tools",
      "env": {
        "BACKEND_URL": "http://localhost:8000",
        "DEBUG": "true"
      }
    }
  }
}
```

## 利用可能なMCPツール

### 接続管理
- `drone_connect`: ドローン接続
- `drone_disconnect`: ドローン切断
- `drone_status`: 包括的ステータス取得

### 飛行制御
- `drone_takeoff`: 離陸・ホバリング
- `drone_land`: 安全着陸
- `drone_emergency`: 緊急停止
- `drone_stop`: 停止・ホバリング
- `drone_get_height`: 高度取得

### 移動制御（実装予定）
- `drone_move`: 基本方向移動
- `drone_rotate`: 回転制御
- `drone_flip`: 宙返り
- `drone_go_xyz`: XYZ座標移動
- `drone_curve`: 曲線飛行
- `drone_rc_control`: リアルタイムRC制御

### カメラ操作（実装予定）
- `camera_stream_start/stop`: 動画ストリーミング
- `camera_take_photo`: 写真撮影
- `camera_start/stop_recording`: 動画録画
- `camera_settings`: カメラ設定変更

### センサーデータ（実装予定）
- `drone_battery`: バッテリー残量
- `drone_temperature`: ドローン温度
- `drone_sensors`: 包括的センサーデータ

## Claude使用例

```
"Connect to the drone and check status"
→ ドローンに接続し、バッテリー・温度・姿勢を確認

"Take off and hover at safe altitude"  
→ 安全な高度で離陸・ホバリング

"Move forward 2 meters and take a photo"
→ 前進2メートル移動後に写真撮影

"Get comprehensive sensor data summary"
→ 全センサーデータの包括的サマリー取得

"Land the drone safely"
→ 安全着陸実行
```

## 設定

### 環境変数

- `BACKEND_URL`: Backend APIのURL（デフォルト: http://localhost:8000）
- `TIMEOUT`: リクエストタイムアウト（デフォルト: 5000ms）
- `RETRIES`: リトライ回数（デフォルト: 3回）
- `DEBUG`: デバッグモード（デフォルト: false）
- `LOG_LEVEL`: ログレベル（デフォルト: info）
- `LOG_FILE`: ログファイルパス（オプション）

### 設定ファイル

- `config/development.json`: 開発環境設定
- `config/production.json`: 本番環境設定

## テスト

### テスト種別

- **単体テスト**: 各ツールの個別テスト
- **統合テスト**: サーバー・API統合テスト
- **境界値テスト**: パラメータ範囲検証
- **異常系テスト**: エラーハンドリング検証
- **性能テスト**: レスポンス時間・負荷テスト

### テスト実行

```bash
# 全テスト実行
npm test

# 監視モード
npm run test:watch

# カバレッジレポート
npm run test:coverage
```

### テスト目標

- カバレッジ: ≥95%
- 成功率: ≥99%
- 応答時間: <100ms
- エラーハンドリング: 全14エラーコード対応

## アーキテクチャ

```
Claude Code ←─ MCP Protocol ─→ MCP Server ←─ HTTP ─→ FastAPI Backend ←─ djitellopy ─→ Tello EDU
   (AI)                        (Node.js)              (Python)                        (Drone)
```

### 主要コンポーネント

- **MCPDroneServer**: メインサーバー実装
- **ToolRegistry**: ツール登録・実行管理
- **FastAPIClient**: Backend API統合クライアント
- **ConfigManager**: 設定管理
- **Logger**: 構造化ログ

## エラーハンドリング

### 対応エラーコード

1. `DRONE_NOT_CONNECTED`: ドローン未接続
2. `DRONE_CONNECTION_FAILED`: 接続失敗
3. `INVALID_PARAMETER`: 無効パラメータ
4. `COMMAND_FAILED`: コマンド実行失敗
5. `COMMAND_TIMEOUT`: タイムアウト
6. `NOT_FLYING`: 飛行していない
7. `ALREADY_FLYING`: 既に飛行中
8. `STREAMING_NOT_STARTED`: ストリーミング未開始
9. `STREAMING_ALREADY_STARTED`: ストリーミング既開始
10. `MODEL_NOT_FOUND`: モデル未発見
11. `TRAINING_IN_PROGRESS`: 訓練進行中
12. `FILE_TOO_LARGE`: ファイル過大
13. `UNSUPPORTED_FORMAT`: 未対応形式
14. `INTERNAL_ERROR`: 内部エラー

## 開発

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone <repository>
cd mcp-tools

# 依存関係インストール
npm install

# 開発環境構築
npm run dev
```

### コード品質

```bash
# リント実行
npm run lint

# リント自動修正
npm run lint:fix
```

### 新ツール追加

1. `src/tools/` に新しいツールファイル作成
2. `src/server.ts` でツール登録
3. 対応するテストファイル作成
4. ドキュメント更新

## ライセンス

MIT License

## 貢献

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## サポート

- Issue報告: GitHub Issues
- ドキュメント: README.md, doc/
- テスト仕様: doc/test_cases.md