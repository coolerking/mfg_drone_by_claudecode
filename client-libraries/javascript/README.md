# MCPドローンクライアントSDK (JavaScript/TypeScript)

MCPドローン制御サーバー用のJavaScript/TypeScript SDK。自然言語コマンドとダイレクトAPI呼び出しによる完全なドローン制御インターフェースを提供します。

## 概要（Description）

MCP Drone Client SDK は、MCPドローン制御サーバー向けのJavaScript/TypeScript SDKです。日本語自然言語コマンドによる直感的なドローン操作、完全なドローン制御機能、カメラ・ビジョンAI、システム監視、WebSocketリアルタイム通信、API Key・JWT認証をサポートします。TypeScript完全対応、90%以上のテストカバレッジにより、Node.js・ブラウザ両環境で動作する高品質SDKとして、モダンWeb開発に最適なソリューションです。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### NPMインストール

```bash
npm install mcp-drone-client
```

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/javascript

# 依存関係インストール
npm install

# SDK ビルド
npm run build
```

## 使い方（Usage）

### 基本セットアップ

```javascript
import { MCPClient } from 'mcp-drone-client';

// クライアント初期化
const client = new MCPClient({
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key', // または bearerToken
});
```

### 自然言語コマンド実行

```javascript
// 単一コマンド実行
const response = await client.executeCommand({
  command: 'ドローンAAに接続して',
  context: {
    drone_id: 'drone_001',
    language: 'ja'
  },
  options: {
    confirm_before_execution: false,
    dry_run: false
  }
});

// バッチコマンド実行
await client.executeBatchCommand({
  commands: [
    { command: 'ドローンAAに接続して' },
    { command: '離陸して' },
    { command: '写真を撮って' }
  ],
  execution_mode: 'sequential',
  stop_on_error: true
});
```

### ダイレクトAPI呼び出し

```javascript
// ドローン管理
const drones = await client.getDrones();
await client.connectDrone('drone_001');
await client.disconnectDrone('drone_001');

// 飛行制御
await client.takeoff('drone_001', { target_height: 100 });
await client.land('drone_001');
await client.emergencyStop('drone_001');

// 移動制御
await client.moveDrone('drone_001', {
  direction: 'forward',
  distance: 100,
  speed: 50
});

await client.rotateDrone('drone_001', {
  direction: 'clockwise',
  angle: 90
});

await client.setAltitude('drone_001', {
  target_height: 150,
  mode: 'absolute'
});
```

### カメラ・ビジョン操作

```javascript
// 写真撮影
const photo = await client.takePhoto('drone_001', {
  filename: 'photo.jpg',
  quality: 'high'
});

// ストリーミング制御
await client.controlStreaming('drone_001', {
  action: 'start',
  quality: 'high',
  resolution: '720p'
});

// 学習データ収集
await client.collectLearningData('drone_001', {
  object_name: 'product_sample',
  capture_positions: ['front', 'back', 'left', 'right'],
  photos_per_position: 3
});

// 物体検出
const detections = await client.detectObjects({
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  confidence_threshold: 0.7
});

// 物体追跡
await client.controlTracking({
  action: 'start',
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  follow_distance: 200
});
```

### WebSocketリアルタイム通信

```javascript
// WebSocket接続
client.connectWebSocket(
  (data) => {
    console.log('受信:', data);
  },
  (error) => {
    console.error('WebSocketエラー:', error);
  }
);

// WebSocket切断
client.disconnectWebSocket();
```

### エラーハンドリング

```javascript
import { MCPClientError } from 'mcp-drone-client';

try {
  await client.connectDrone('invalid_drone');
} catch (error) {
  if (error instanceof MCPClientError) {
    console.error('MCPエラー:', error.errorCode, error.message);
    console.error('詳細:', error.details);
    console.error('タイムスタンプ:', error.timestamp);
  } else {
    console.error('予期しないエラー:', error);
  }
}
```

## 動作環境・要件（Requirements）

### システム要件

- **Node.js**: 16+
- **ブラウザ**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **TypeScript**: 4.9+ (TypeScript使用時)
- **メモリ**: 1GB以上推奨

### 必須依存関係

- **axios**: HTTP クライアント
- **ws**: WebSocket クライアント
- **eventemitter3**: イベント管理

### 開発依存関係

- **TypeScript**: 型安全性
- **Jest**: テストフレームワーク
- **ESLint**: コード品質管理
- **Prettier**: コードフォーマット

### ネットワーク要件

- **MCPサーバー**: ポート8001での通信
- **WebSocket**: リアルタイム通信用
- **CORS**: ブラウザ環境での通信許可

## ディレクトリ構成（Directory Structure）

```
javascript/
├── package.json           # NPMパッケージ定義
├── src/                   # ソースコード
│   ├── index.ts          # メインSDKファイル
│   └── index.test.ts     # 包括的テストスイート
├── tsconfig.json         # TypeScript設定
├── jest.config.js        # Jestテスト設定
├── jest.setup.js         # Jestセットアップ
└── README.md             # SDKドキュメント
```

### TypeScript型定義

```typescript
interface MCPClientConfig {
  baseURL: string;          // MCPサーバーURL
  apiKey?: string;          // API Key認証
  bearerToken?: string;     // JWT Bearer Token認証
  timeout?: number;         // リクエストタイムアウト(ms、デフォルト: 30000)
}
```

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

### 開発・テスト

```bash
# 依存関係インストール
npm install

# SDKビルド
npm run build

# テスト実行
npm test

# ウォッチモードテスト
npm run test:watch

# コード検証
npm run lint

# ドキュメント生成
npm run docs
```

## 更新履歴（Changelog/History）

### 1.0.0: 初期リリース（最新）
- **完全なMCP API対応**: 50+ APIエンドポイント対応
- **自然言語処理**: 日本語コマンド認識・解析
- **TypeScript対応**: 完全な型定義・IntelliSense
- **WebSocket統合**: リアルタイム通信対応
- **包括的テスト**: 90%以上のテストカバレッジ

### 0.9.0: ベータ版
- **コア機能実装**: 基本ドローン制御API
- **認証システム**: API Key・JWT Bearer Token対応
- **エラーハンドリング**: 包括的エラー処理

### 0.8.0: アルファ版
- **プロトタイプ実装**: 基本HTTP クライアント
- **TypeScript基盤**: 型安全な実装基盤
- **テスト環境**: Jest テストフレームワーク

---

**ライセンス**: MIT License

**サポート**: 問題・質問は[GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)までお寄せください。