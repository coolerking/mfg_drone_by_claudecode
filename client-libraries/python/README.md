# MCPドローンクライアントSDK (Python)

MCPドローン制御サーバー用のPython SDK。自然言語コマンドとダイレクトAPI呼び出しによる完全なドローン制御インターフェースを提供します。

## 概要（Description）

MCP Drone Client SDK (Python) は、MCPドローン制御サーバー向けのPython SDKです。日本語自然言語コマンドによる直感的なドローン操作、完全なドローン制御機能、カメラ・ビジョンAI、システム監視、WebSocketリアルタイム通信、API Key・JWT認証をサポートします。async/await構文、Pydanticモデルによる完全型安全性、コンテキストマネージャー対応により、モダンPython開発に最適な85%以上のテストカバレッジを持つ高品質SDKです。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### pipインストール

```bash
pip install mcp-drone-client
```

### 開発環境セットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/python

# 開発モードでインストール
pip install -e .[dev]

# テスト依存関係インストール
pip install -e .[test]
```

## 使い方（Usage）

### 基本セットアップ

```python
import asyncio
from mcp_drone_client import MCPClient, MCPClientConfig, NaturalLanguageCommand

async def main():
    # クライアント設定
    config = MCPClientConfig(
        base_url="http://localhost:8001",
        api_key="your-api-key",  # または bearer_token
        timeout=30.0,
    )
    
    # 非同期コンテキストマネージャーとして使用
    async with MCPClient(config) as client:
        # 自然言語コマンド実行
        response = await client.execute_command(
            NaturalLanguageCommand(command="ドローンAAに接続して")
        )
        print(f"コマンド結果: {response.message}")

# 非同期関数実行
asyncio.run(main())
```

### 自然言語コマンド実行

```python
from mcp_drone_client.models import NaturalLanguageCommand, BatchCommand

# 単一コマンド
command = NaturalLanguageCommand(
    command="ドローンAAに接続して",
    context={"drone_id": "drone_001", "language": "ja"},
    options={"confirm_before_execution": False, "dry_run": False}
)
response = await client.execute_command(command)

# バッチコマンド
batch = BatchCommand(
    commands=[
        NaturalLanguageCommand(command="ドローンAAに接続して"),
        NaturalLanguageCommand(command="離陸して"),
        NaturalLanguageCommand(command="写真を撮って"),
    ],
    execution_mode="sequential",
    stop_on_error=True,
)
batch_response = await client.execute_batch_command(batch)
```

### ダイレクトAPI呼び出し

```python
from mcp_drone_client.models import (
    TakeoffCommand, MoveCommand, RotateCommand, AltitudeCommand
)

# ドローン管理
await client.connect_drone("drone_001")
await client.disconnect_drone("drone_001")

# 飛行制御
await client.takeoff("drone_001", TakeoffCommand(target_height=100))
await client.land("drone_001")
await client.emergency_stop("drone_001")

# 移動制御
await client.move_drone("drone_001", MoveCommand(
    direction="forward", distance=100, speed=50
))

await client.rotate_drone("drone_001", RotateCommand(
    direction="clockwise", angle=90
))

await client.set_altitude("drone_001", AltitudeCommand(
    target_height=150, mode="absolute"
))
```

### カメラ・ビジョン操作

```python
from mcp_drone_client.models import (
    PhotoCommand, StreamingCommand, LearningDataCommand,
    DetectionCommand, TrackingCommand
)

# 写真撮影
photo_result = await client.take_photo("drone_001", PhotoCommand(
    filename="photo.jpg", quality="high"
))

# ストリーミング制御
await client.control_streaming("drone_001", StreamingCommand(
    action="start", quality="high", resolution="720p"
))

# 学習データ収集
learning_result = await client.collect_learning_data("drone_001", LearningDataCommand(
    object_name="product_sample",
    capture_positions=["front", "back", "left", "right"],
    photos_per_position=3,
))

# 物体検出
detections = await client.detect_objects(DetectionCommand(
    drone_id="drone_001",
    model_id="yolo_v8",
    confidence_threshold=0.7,
))

# 物体追跡
await client.control_tracking(TrackingCommand(
    action="start",
    drone_id="drone_001",
    model_id="yolo_v8",
    follow_distance=200,
))
```

### WebSocketリアルタイム通信

```python
async def on_message(data):
    print(f"受信: {data}")

async def on_error(error):
    print(f"WebSocketエラー: {error}")

async def on_connect():
    print("WebSocket接続")

async def on_disconnect():
    print("WebSocket切断")

# WebSocket接続
await client.connect_websocket(
    on_message=on_message,
    on_error=on_error,
    on_connect=on_connect,
    on_disconnect=on_disconnect,
)

# メッセージ送信
await client.send_websocket_message({"type": "ping"})

# 切断
await client.disconnect_websocket()
```

### エラーハンドリング

```python
from mcp_drone_client import MCPClientError

try:
    await client.connect_drone("invalid_drone")
except MCPClientError as e:
    print(f"MCPエラー: {e.error_code}")
    print(f"メッセージ: {e.message}")
    print(f"詳細: {e.details}")
    print(f"タイムスタンプ: {e.timestamp}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## 動作環境・要件（Requirements）

### システム要件

- **Python**: 3.8+
- **OS**: Linux, Windows, macOS
- **メモリ**: 1GB以上推奨

### 必須依存関係

- **aiohttp**: 3.8.0+ (HTTP クライアント)
- **httpx**: 0.24.0+ (HTTP クライアント)
- **websockets**: 11.0.0+ (WebSocket クライアント)
- **pydantic**: 2.0.0+ (データモデル・型検証)
- **typing-extensions**: 4.0.0+ (型ヒント拡張)

### 開発依存関係

- **pytest**: テストフレームワーク
- **black**: コードフォーマッター
- **flake8**: コード品質チェック
- **mypy**: 型チェック
- **sphinx**: ドキュメント生成

### ネットワーク要件

- **MCPサーバー**: ポート8001での通信
- **WebSocket**: リアルタイム通信用
- **SSL/TLS**: HTTPS通信対応

## ディレクトリ構成（Directory Structure）

```
python/
├── setup.py                       # Pythonパッケージ定義
├── requirements.txt               # 依存関係
├── mcp_drone_client/              # メインパッケージ
│   ├── __init__.py               # パッケージ初期化
│   ├── client.py                 # メインSDKクライアント
│   └── models.py                 # Pydanticデータモデル
├── tests/                         # テストスイート
│   └── test_client.py            # 包括的テストスイート
├── pytest.ini                    # pytestテスト設定
└── README.md                      # SDKドキュメント
```

### Pydantic型定義

```python
from mcp_drone_client.models import MCPClientConfig

config = MCPClientConfig(
    base_url="http://localhost:8001",      # MCPサーバーURL
    api_key="your-api-key",                # API Key認証
    bearer_token="your-jwt-token",         # JWT Bearer Token認証
    timeout=30.0,                          # リクエストタイムアウト(秒)
)
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

### 開発・テスト・品質管理

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=mcp_drone_client --cov-report=html

# 特定テストファイル実行
pytest tests/test_client.py

# マーカー付きテスト
pytest -m "not slow"
pytest -m "integration"

# コードフォーマット
black mcp_drone_client tests

# スタイルチェック
flake8 mcp_drone_client tests

# 型チェック
mypy mcp_drone_client

# ドキュメント生成
sphinx-build -b html docs docs/_build/html
```

## 更新履歴（Changelog/History）

### 1.0.0: 初期リリース（最新）
- **完全なMCP API対応**: 50+ APIエンドポイント対応
- **自然言語処理**: 日本語コマンド認識・解析
- **WebSocketサポート**: リアルタイム通信対応
- **包括的テスト**: 85%以上のテストカバレッジ
- **Pydantic型安全性**: 完全な型検証・モデル対応

### 0.9.0: ベータ版
- **コア機能実装**: 基本ドローン制御API
- **認証システム**: API Key・JWT Bearer Token対応
- **エラーハンドリング**: 包括的エラー処理

### 0.8.0: アルファ版
- **プロトタイプ実装**: 基本HTTP クライアント
- **async/await対応**: 非同期処理基盤
- **テスト環境**: pytest テストフレームワーク

---

**ライセンス**: MIT License

**サポート**: 問題・質問は[GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)までお寄せください。