# @mcp-drone/types

MCPドローン制御サーバー用TypeScript型定義。全MCPAPIエンドポイント、モデル、クライアント設定の包括的型定義を提供します。

## 概要（Description）

@mcp-drone/types は、MCPドローン制御サーバー向けのTypeScript型定義パッケージです。全MCPAPIエンドポイント・モデルの完全型カバレッジ、型ガード・バリデーション機能、IntelliSense完全対応、モジュラー設計、WebSocketイベント型定義、ユーティリティ型・定数定義を提供します。開発効率向上とコード品質確保により、TypeScript開発者に最適な包括的型システムソリューションです。

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
npm install @mcp-drone/types
```

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/types

# 依存関係インストール
npm install

# 型定義ビルド
npm run build
```

## 使い方（Usage）

### 基本型定義

```typescript
import { 
  DroneInfo, 
  CommandResponse, 
  NaturalLanguageCommand 
} from '@mcp-drone/types';

// ドローン情報
const drone: DroneInfo = {
  id: 'drone_001',
  name: 'テストドローン',
  type: 'real',
  status: 'available',
  capabilities: ['camera', 'movement'],
  last_seen: '2023-01-01T12:00:00Z'
};

// 自然言語コマンド
const command: NaturalLanguageCommand = {
  command: 'ドローンAAに接続して',
  context: {
    drone_id: 'drone_001',
    language: 'ja'
  },
  options: {
    confirm_before_execution: false,
    dry_run: false
  }
};
```

### クライアント設定

```typescript
import { MCPClientConfig } from '@mcp-drone/types';

const config: MCPClientConfig = {
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key',
  timeout: 30000
};
```

### APIレスポンス型

```typescript
import { 
  DroneListResponse, 
  CommandResponse, 
  BatchCommandResponse 
} from '@mcp-drone/types';

// ドローン一覧レスポンス
const droneList: DroneListResponse = {
  drones: [
    {
      id: 'drone_001',
      name: 'テストドローン',
      type: 'real',
      status: 'available',
      capabilities: ['camera', 'movement']
    }
  ],
  count: 1,
  timestamp: '2023-01-01T12:00:00Z'
};

// コマンドレスポンス
const response: CommandResponse = {
  success: true,
  message: 'コマンドが正常に実行されました',
  parsed_intent: {
    action: 'connect_drone',
    parameters: { drone_id: 'drone_001' },
    confidence: 0.95
  },
  timestamp: '2023-01-01T12:00:00Z'
};
```

### 制御コマンド型

```typescript
import { 
  TakeoffCommand, 
  MoveCommand, 
  RotateCommand, 
  AltitudeCommand 
} from '@mcp-drone/types';

// 離陸コマンド
const takeoff: TakeoffCommand = {
  target_height: 100,
  safety_check: true
};

// 移動コマンド
const move: MoveCommand = {
  direction: 'forward',
  distance: 100,
  speed: 50
};

// 回転コマンド
const rotate: RotateCommand = {
  direction: 'clockwise',
  angle: 90
};

// 高度コマンド
const altitude: AltitudeCommand = {
  target_height: 150,
  mode: 'absolute'
};
```

### カメラ操作型

```typescript
import { 
  PhotoCommand, 
  StreamingCommand, 
  LearningDataCommand 
} from '@mcp-drone/types';

// 写真撮影コマンド
const photo: PhotoCommand = {
  filename: 'aerial_shot.jpg',
  quality: 'high',
  metadata: {
    location: 'outdoor',
    weather: 'sunny'
  }
};

// ストリーミングコマンド
const streaming: StreamingCommand = {
  action: 'start',
  quality: 'high',
  resolution: '720p'
};

// 学習データコマンド
const learning: LearningDataCommand = {
  object_name: 'product_sample',
  capture_positions: ['front', 'back', 'left', 'right'],
  photos_per_position: 3,
  dataset_name: 'products_v1'
};
```

### ビジョン・AI型

```typescript
import { 
  DetectionCommand, 
  TrackingCommand, 
  DetectionResponse 
} from '@mcp-drone/types';

// 物体検出コマンド
const detection: DetectionCommand = {
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  confidence_threshold: 0.7
};

// 物体追跡コマンド
const tracking: TrackingCommand = {
  action: 'start',
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  follow_distance: 200,
  confidence_threshold: 0.8
};

// 検出結果
const detectionResult: DetectionResponse = {
  success: true,
  message: '物体が検出されました',
  detections: [
    {
      label: 'person',
      confidence: 0.95,
      bbox: {
        x: 100,
        y: 100,
        width: 50,
        height: 100
      }
    }
  ],
  processing_time: 0.5,
  timestamp: '2023-01-01T12:00:00Z'
};
```

### 型ガード・バリデーション

```typescript
import { 
  isMCPError, 
  isSuccessResponse, 
  isDroneInfo, 
  isCommandResponse 
} from '@mcp-drone/types';

// 型ガード使用例
function processResponse(response: any) {
  if (isMCPError(response)) {
    console.error('エラー:', response.error_code, response.message);
    return;
  }
  
  if (isSuccessResponse(response)) {
    console.log('成功:', response.message);
  }
  
  if (isCommandResponse(response)) {
    console.log('コマンド結果:', response.parsed_intent);
  }
}

// ドローン情報検証
function validateDrone(data: any): data is DroneInfo {
  return isDroneInfo(data);
}
```

### WebSocketイベント型

```typescript
import { WebSocketEvent, WebSocketEventType } from '@mcp-drone/types';

// WebSocketイベント
const event: WebSocketEvent = {
  type: 'drone_status_changed',
  data: {
    drone_id: 'drone_001',
    old_status: 'available',
    new_status: 'connected'
  },
  timestamp: '2023-01-01T12:00:00Z'
};

// イベントハンドリング
function handleWebSocketEvent(event: WebSocketEvent) {
  switch (event.type) {
    case 'drone_connected':
      console.log('ドローン接続:', event.data);
      break;
    case 'drone_disconnected':
      console.log('ドローン切断:', event.data);
      break;
    case 'command_executed':
      console.log('コマンド実行:', event.data);
      break;
    default:
      console.log('不明なイベント:', event);
  }
}
```

## 動作環境・要件（Requirements）

### システム要件

- **TypeScript**: 5.0+
- **Node.js**: 16+ (開発環境)
- **ビルドツール**: tsc, webpack, vite等

### 開発要件

- **型検証**: 完全なIntelliSense対応
- **モジュラー設計**: 必要な型のみインポート可能
- **拡張性**: カスタム型拡張対応

### サポート対象

- **IDE**: VS Code, WebStorm, Vim/Neovim等
- **フレームワーク**: React, Vue, Angular, Node.js等
- **バンドラー**: webpack, vite, rollup等

## ディレクトリ構成（Directory Structure）

```
types/
├── package.json           # NPMパッケージ定義
├── src/                   # 型定義ソース
│   └── index.ts          # 包括的型定義
├── tsconfig.json         # TypeScript設定
└── README.md             # 型定義ドキュメント
```

### 主要型カテゴリ

#### コア型定義
- **MCPClientConfig**: クライアント設定
- **DroneInfo**: ドローン情報
- **CommandResponse**: コマンドレスポンス
- **ErrorCode**: エラーコード定義

#### 制御コマンド型
- **NaturalLanguageCommand**: 自然言語コマンド
- **TakeoffCommand**: 離陸コマンド
- **MoveCommand**: 移動コマンド
- **RotateCommand**: 回転コマンド

#### ビジョン・AI型
- **DetectionCommand**: 物体検出コマンド
- **TrackingCommand**: 物体追跡コマンド
- **DetectionResponse**: 検出結果

#### システム型
- **SystemStatusResponse**: システム状態
- **HealthResponse**: ヘルスチェック結果
- **WebSocketEvent**: WebSocketイベント

### 定数・エンドポイント

```typescript
import { 
  API_ENDPOINTS, 
  WEBSOCKET_ENDPOINTS, 
  DEFAULT_CONFIG, 
  VALIDATION_CONSTRAINTS 
} from '@mcp-drone/types';

// APIエンドポイント
const droneStatusUrl = API_ENDPOINTS.GET_DRONE_STATUS('drone_001');
const commandUrl = API_ENDPOINTS.EXECUTE_COMMAND;

// WebSocketエンドポイント
const wsUrl = WEBSOCKET_ENDPOINTS.EVENTS;

// デフォルト設定
const config = {
  baseURL: 'http://localhost:8001',
  ...DEFAULT_CONFIG
};

// バリデーション制約
const isValidHeight = (height: number) => {
  return height >= VALIDATION_CONSTRAINTS.TARGET_HEIGHT.min && 
         height <= VALIDATION_CONSTRAINTS.TARGET_HEIGHT.max;
};
```

## 更新履歴（Changelog/History）

### 1.0.0: 初期リリース（最新）
- **完全な型定義**: 全MCP APIの型カバレッジ
- **型ガード・バリデーション**: ランタイム型チェック機能
- **定数・エンドポイント定義**: API・WebSocket定数
- **WebSocketイベント型**: リアルタイムイベント定義
- **包括的ドキュメント**: 詳細な使用例とガイド

### 0.9.0: ベータ版
- **基本型定義**: コアAPI型の実装
- **ユーティリティ型**: 共通パターンのヘルパー型
- **バリデーション**: 基本的な型検証機能

### 0.8.0: アルファ版
- **プロトタイプ実装**: 基本型定義システム
- **TypeScript設定**: 型安全な開発環境
- **ビルドシステム**: npm ビルドパイプライン

---

**ライセンス**: MIT License

**サポート**: 問題・質問は[GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)までお寄せください。