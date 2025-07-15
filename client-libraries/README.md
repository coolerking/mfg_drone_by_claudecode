# MCPドローンクライアントライブラリ

MCPドローン制御サーバー用の包括的なクライアントライブラリとツール集

## 概要（Description）

MCP Drone Client Libraries は、MCPドローン制御サーバー向けの包括的なクライアントライブラリスイートです。自然言語コマンドからダイレクトAPI呼び出しまで、複数のプログラミング言語とインターフェースでドローン制御を可能にします。JavaScript SDK、Python SDK、CLI Tool、TypeScript型定義を含む4つの完全機能ライブラリが、WebSocket リアルタイム通信、AI物体追跡、包括的エラーハンドリングをサポートし、初心者から上級者まで対応する産業グレードの品質を提供します。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### ライブラリ別インストール

```bash
# JavaScript/TypeScript SDK
npm install mcp-drone-client

# Python SDK
pip install mcp-drone-client

# CLI Tool
npm install -g mcp-drone-cli

# TypeScript Types (開発用)
npm install @mcp-drone/types
```

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries

# 全プロジェクト依存関係インストール
npm install  # JavaScript SDK
cd python && pip install -e .[dev]  # Python SDK
cd ../cli && npm install  # CLI Tool
cd ../types && npm install  # TypeScript Types
```

### 全ライブラリビルド

```bash
# JavaScript SDK
cd javascript && npm run build

# Python SDK
cd python && python setup.py sdist bdist_wheel

# CLI Tool
cd cli && npm run build

# TypeScript Types
cd types && npm run build
```

## 使い方（Usage）

### JavaScript SDK基本例

```javascript
import { MCPClient } from 'mcp-drone-client';

const client = new MCPClient({
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key'
});

// 自然言語コマンド
const response = await client.executeCommand({
  command: 'ドローンAAに接続して'
});

// ダイレクトAPI呼び出し
const drones = await client.getDrones();
await client.connectDrone('drone_001');
await client.takeoff('drone_001', { target_height: 100 });
```

### Python SDK基本例

```python
import asyncio
from mcp_drone_client import MCPClient, MCPClientConfig, NaturalLanguageCommand

async def main():
    config = MCPClientConfig(
        base_url="http://localhost:8001",
        api_key="your-api-key"
    )
    
    async with MCPClient(config) as client:
        # 自然言語コマンド
        response = await client.execute_command(
            NaturalLanguageCommand(command="ドローンAAに接続して")
        )
        
        # ダイレクトAPI呼び出し
        drones = await client.get_drones()
        await client.connect_drone("drone_001")
        await client.takeoff("drone_001")

asyncio.run(main())
```

### CLI Tool基本例

```bash
# CLI設定
mcp-drone configure

# 自然言語コマンド
mcp-drone exec "ドローンAAに接続して"
mcp-drone exec "離陸して"
mcp-drone exec "写真を撮って"

# ダイレクトコマンド
mcp-drone connect drone_001
mcp-drone takeoff drone_001 --height 100
mcp-drone photo drone_001 --quality high

# バッチコマンド
mcp-drone batch "ドローンAAに接続して" "離陸して" "写真を撮って"
```

### 共通自然言語コマンド

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

### テスト実行

```bash
# 全テスト実行
node test_all.js

# 特定ライブラリテスト
node test_all.js javascript
node test_all.js python
node test_all.js cli
node test_all.js types

# 複数ライブラリテスト
node test_all.js javascript python
```

## 動作環境・要件（Requirements）

### システム要件

- **Node.js**: 16+ (JavaScript SDK・CLI用)
- **Python**: 3.8+ (Python SDK用)
- **TypeScript**: 5.0+ (型定義用)
- **OS**: Linux, Windows, macOS
- **メモリ**: 2GB以上推奨

### ライブラリ別要件

#### JavaScript SDK
- **ブラウザサポート**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Node.js環境**: Node.js 16+ + npm/yarn
- **WebSocket**: WSS/WS通信サポート

#### Python SDK
- **Python**: 3.8+
- **必須ライブラリ**: aiohttp 3.8+, httpx 0.24+, websockets 11.0+, pydantic 2.0+
- **非同期サポート**: async/await対応

#### CLI Tool
- **グローバルインストール**: npm -g 対応環境
- **対話モード**: ターミナル・コマンドプロンプト
- **設定ファイル**: YAML設定サポート

#### TypeScript Types
- **TypeScript**: 5.0+
- **型検証**: 完全なIntelliSense対応
- **ビルドツール**: tsc、webpack、vite等対応

### ネットワーク要件

- **MCPサーバー**: ポート8001での通信
- **バックエンドAPI**: ポート8000での通信
- **WebSocket**: リアルタイム通信用
- **認証**: API Key または JWT Bearer Token

## ディレクトリ構成（Directory Structure）

```
client-libraries/
├── README.md                          # 統合ドキュメント
├── PHASE6_4_WEBSDK_COMPLETION.md      # Phase 6-4完了報告
├── test_all.js                        # 統合テストランナー
├── javascript/                        # JavaScript/TypeScript SDK
│   ├── package.json                   # NPMパッケージ定義
│   ├── src/
│   │   ├── index.ts                   # メインSDKファイル
│   │   └── index.test.ts              # 包括的テストスイート
│   ├── tsconfig.json                  # TypeScript設定
│   ├── jest.config.js                 # Jestテスト設定
│   ├── jest.setup.js                  # Jestセットアップ
│   └── README.md                      # 詳細ドキュメント
├── python/                            # Python SDK
│   ├── setup.py                       # Pythonパッケージ定義
│   ├── requirements.txt               # 依存関係
│   ├── mcp_drone_client/
│   │   ├── __init__.py                # パッケージ初期化
│   │   ├── client.py                  # メインSDKクライアント
│   │   └── models.py                  # Pydanticデータモデル
│   ├── tests/
│   │   └── test_client.py             # 包括的テストスイート
│   ├── pytest.ini                     # pytestテスト設定
│   └── README.md                      # 詳細ドキュメント
├── cli/                               # CLI Tool
│   ├── package.json                   # NPMパッケージ定義
│   ├── src/
│   │   └── index.ts                   # メインCLIアプリケーション
│   ├── bin/
│   │   └── mcp-drone                  # 実行可能スクリプト
│   ├── tsconfig.json                  # TypeScript設定
│   └── README.md                      # 詳細ドキュメント
└── types/                             # TypeScript Types
    ├── package.json                   # NPMパッケージ定義
    ├── src/
    │   └── index.ts                   # 包括的型定義
    ├── tsconfig.json                  # TypeScript設定
    └── README.md                      # 詳細ドキュメント
```

### ライブラリ機能比較

| 機能 | JavaScript SDK | Python SDK | CLI Tool | TypeScript Types |
|------|---------------|------------|----------|-----------------|
| **自然言語** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **Async/Await** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **WebSocket** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **型安全性** | ✅ | ✅ | ✅ | ✅ |
| **エラーハンドリング** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **認証** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **バッチコマンド** | ✅ | ✅ | ✅ | ✅ (型定義) |
| **対話モード** | ❌ | ❌ | ✅ | ❌ |
| **ブラウザサポート** | ✅ | ❌ | ❌ | ✅ |
| **コマンドライン** | ❌ | ❌ | ✅ | ❌ |
| **インストール** | npm | pip | npm global | npm dev |

## 更新履歴（Changelog/History）

### Phase 6-4: WebSDK・クライアントライブラリ実装（最新）
- **JavaScript SDK**: WebSocket・型安全性・包括的テスト対応
- **Python SDK**: async/await・Pydanticモデル・コンテキストマネージャー
- **CLI Tool**: 対話設定・バッチ処理・リアルタイム監視
- **TypeScript Types**: 完全型定義・型ガード・バリデーション
- **統合テスト**: 全ライブラリ統合テストランナー

### Phase 6-3: MCP自然言語API拡張
- **自然言語処理**: 日本語コマンド認識・意図解析・パラメータ抽出
- **APIカバレッジ**: 50+ APIエンドポイント対応
- **エラーハンドリング**: 包括的エラーメッセージ・修正提案

### Phase 6-2: MCPサーバー基盤実装
- **MCPサーバー**: FastAPIベースサーバー実装
- **バックエンド統合**: ドローン制御API連携
- **認証システム**: API Key・JWT Bearer Token対応

### Phase 6-1: クライアントライブラリ設計
- **アーキテクチャ設計**: マルチプラットフォーム対応設計
- **技術選定**: JavaScript・Python・CLI・TypeScript選択
- **仕様策定**: 統一API仕様・自然言語コマンド仕様

---

**ライセンス**: MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。

**サポート**: 問題・質問は[GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)までお寄せください。