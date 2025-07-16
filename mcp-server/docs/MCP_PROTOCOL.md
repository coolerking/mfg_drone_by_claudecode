# MCP プロトコル仕様書

**MCP ドローン制御システム - Model Context Protocol 実装詳細**

このドキュメントは、MCPドローン制御システムで実装されているModel Context Protocol（MCP）の詳細仕様を説明します。

## 📋 目次

1. [概要](#概要)
2. [MCP プロトコル基礎](#mcp-プロトコル基礎)
3. [実装アーキテクチャ](#実装アーキテクチャ)
4. [MCPツール仕様](#mcpツール仕様)
5. [MCPリソース仕様](#mcpリソース仕様)
6. [プロトコル通信](#プロトコル通信)
7. [エラーハンドリング](#エラーハンドリング)
8. [セキュリティ](#セキュリティ)
9. [パフォーマンス](#パフォーマンス)
10. [拡張性](#拡張性)

## 🎯 概要

### MCPドローン制御システムとは

MCPドローン制御システムは、Model Context Protocol（MCP）を用いて、Claude Desktop、VS Code、Claude Code、Difyなどの各種MCPホストから自然言語でドローンを制御できるシステムです。

### 主要特徴

- **標準準拠**: MCP仕様に完全準拠
- **双方向通信**: JSONRPC over stdio
- **リアルタイム制御**: 低遅延ドローン制御
- **自然言語処理**: 日本語・英語対応
- **セキュリティ**: 包括的セキュリティ機能
- **拡張性**: プラグイン形式での機能拡張

## 🔌 MCP プロトコル基礎

### プロトコル概要

Model Context Protocol（MCP）は、AIアプリケーションが外部ツールやリソースにアクセスするための標準化されたプロトコルです。

```
┌─────────────────────┐    ┌─────────────────────┐
│    MCP ホスト       │    │    MCP サーバー     │
│  (Claude Desktop)   │◄──►│  (ドローン制御)     │
│                     │    │                     │
│  - Claude AI        │    │  - MCPツール        │
│  - ユーザー対話     │    │  - MCPリソース      │
│  - コマンド送信     │    │  - ドローン制御     │
└─────────────────────┘    └─────────────────────┘
```

### 通信プロトコル

**プロトコル**: JSONRPC 2.0  
**トランスポート**: stdio（標準入出力）  
**データ形式**: JSON  
**文字エンコーディング**: UTF-8  

### 基本通信フロー

```json
// 1. 初期化
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {}
    }
  }
}

// 2. ツール呼び出し
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "takeoff_drone",
    "arguments": {
      "drone_id": "AA"
    }
  }
}

// 3. リソース取得
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/read",
  "params": {
    "uri": "drone://status/AA"
  }
}
```

## 🏗️ 実装アーキテクチャ

### システム構成

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP ホスト                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  Claude Desktop │ │     VS Code     │ │   Claude Code   │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ JSONRPC over stdio
┌─────────────────────────▼───────────────────────────────────────┐
│                     MCP サーバー                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    mcp_main.py                              │ │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │ │
│  │  │   MCP ツール    │ │  MCP リソース   │ │  セキュリティ  │ │ │
│  │  │   (8種類)       │ │   (3種類)       │ │   機能        │ │ │
│  │  └─────────────────┘ └─────────────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 コアモジュール                                │ │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │ │
│  │  │  自然言語処理   │ │  エラーハンドリング │ │  プログレス    │ │ │
│  │  │  エンジン       │ │  システム          │ │  インジケータ  │ │ │
│  │  └─────────────────┘ └─────────────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP API
┌─────────────────────────▼───────────────────────────────────────┐
│                   バックエンドAPI                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  ドローン制御システム                        │ │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │ │
│  │  │  Tello EDU      │ │  シミュレーション │ │  カメラ・      │ │ │
│  │  │  実機制御       │ │  システム        │ │  ビジョン     │ │ │
│  │  └─────────────────┘ └─────────────────┘ └───────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 主要コンポーネント

#### 1. MCP サーバー (`mcp_main.py`)
- **役割**: MCPプロトコル実装のメインエントリーポイント
- **機能**: ツール管理、リソース管理、セキュリティ制御
- **行数**: 500行以上

#### 2. MCPツール (8種類)
- **connect_drone**: ドローン接続
- **takeoff_drone**: ドローン離陸
- **land_drone**: ドローン着陸
- **move_drone**: ドローン移動
- **rotate_drone**: ドローン回転
- **take_photo**: 写真撮影
- **execute_natural_language_command**: 自然言語コマンド実行
- **emergency_stop**: 緊急停止

#### 3. MCPリソース (3種類)
- **drone://available**: 利用可能なドローン一覧
- **drone://status/{drone_id}**: ドローン状態情報
- **system://status**: システム状態情報

## 🛠️ MCPツール仕様

### 1. connect_drone

**説明**: ドローンに接続します

```json
{
  "name": "connect_drone",
  "description": "ドローンに接続します",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_type": {
        "type": "string",
        "enum": ["tello", "simulation"],
        "description": "ドローンの種類"
      }
    },
    "required": ["drone_type"]
  }
}
```

**実行例**:
```json
{
  "name": "connect_drone",
  "arguments": {
    "drone_type": "tello"
  }
}
```

**応答例**:
```json
{
  "content": [
    {
      "type": "text",
      "text": "✅ ドローン接続成功\n\n📋 詳細:\n• ドローンID: AA\n• 接続種類: tello\n• 状態: 接続済み\n• バッテリー: 85%"
    }
  ]
}
```

### 2. takeoff_drone

**説明**: ドローンを離陸させます

```json
{
  "name": "takeoff_drone",
  "description": "ドローンを離陸させます",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      }
    },
    "required": ["drone_id"]
  }
}
```

### 3. land_drone

**説明**: ドローンを着陸させます

```json
{
  "name": "land_drone",
  "description": "ドローンを着陸させます",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      }
    },
    "required": ["drone_id"]
  }
}
```

### 4. move_drone

**説明**: ドローンを移動させます

```json
{
  "name": "move_drone",
  "description": "ドローンを移動させます",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      },
      "direction": {
        "type": "string",
        "enum": ["forward", "backward", "left", "right", "up", "down"],
        "description": "移動方向"
      },
      "distance": {
        "type": "integer",
        "minimum": 1,
        "maximum": 500,
        "description": "移動距離（cm）"
      },
      "speed": {
        "type": "integer",
        "minimum": 10,
        "maximum": 100,
        "description": "移動速度（cm/s）"
      }
    },
    "required": ["drone_id", "direction", "distance"]
  }
}
```

### 5. rotate_drone

**説明**: ドローンを回転させます

```json
{
  "name": "rotate_drone",
  "description": "ドローンを回転させます",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      },
      "direction": {
        "type": "string",
        "enum": ["clockwise", "counterclockwise"],
        "description": "回転方向"
      },
      "angle": {
        "type": "integer",
        "minimum": 1,
        "maximum": 360,
        "description": "回転角度（度）"
      }
    },
    "required": ["drone_id", "direction", "angle"]
  }
}
```

### 6. take_photo

**説明**: ドローンで写真を撮影します

```json
{
  "name": "take_photo",
  "description": "ドローンで写真を撮影します",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      },
      "filename": {
        "type": "string",
        "description": "保存するファイル名（オプション）"
      }
    },
    "required": ["drone_id"]
  }
}
```

### 7. execute_natural_language_command

**説明**: 自然言語コマンドを実行します

```json
{
  "name": "execute_natural_language_command",
  "description": "自然言語コマンドを実行します",
  "inputSchema": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "maxLength": 1000,
        "description": "日本語または英語のコマンド"
      },
      "drone_id": {
        "type": "string",
        "description": "ドローンのID（オプション）"
      }
    },
    "required": ["command"]
  }
}
```

### 8. emergency_stop

**説明**: 緊急停止を実行します

```json
{
  "name": "emergency_stop",
  "description": "緊急停止を実行します",
  "inputSchema": {
    "type": "object",
    "properties": {
      "drone_id": {
        "type": "string",
        "description": "ドローンのID"
      }
    },
    "required": ["drone_id"]
  }
}
```

## 📊 MCPリソース仕様

### 1. drone://available

**説明**: 利用可能なドローンの一覧を取得

```json
{
  "uri": "drone://available",
  "name": "利用可能なドローン一覧",
  "description": "現在利用可能なドローンの一覧を取得します",
  "mimeType": "application/json"
}
```

**応答例**:
```json
{
  "contents": [
    {
      "uri": "drone://available",
      "mimeType": "application/json",
      "text": "{\n  \"drones\": [\n    {\n      \"id\": \"AA\",\n      \"type\": \"tello\",\n      \"status\": \"connected\",\n      \"battery\": 85\n    },\n    {\n      \"id\": \"BB\",\n      \"type\": \"simulation\",\n      \"status\": \"disconnected\",\n      \"battery\": 100\n    }\n  ],\n  \"total\": 2\n}"
    }
  ]
}
```

### 2. drone://status/{drone_id}

**説明**: 指定されたドローンの状態を取得

```json
{
  "uri": "drone://status/AA",
  "name": "ドローン状態情報",
  "description": "指定されたドローンの詳細な状態情報を取得します",
  "mimeType": "application/json"
}
```

**応答例**:
```json
{
  "contents": [
    {
      "uri": "drone://status/AA",
      "mimeType": "application/json",
      "text": "{\n  \"id\": \"AA\",\n  \"type\": \"tello\",\n  \"status\": \"flying\",\n  \"battery\": 85,\n  \"position\": {\n    \"x\": 0,\n    \"y\": 0,\n    \"z\": 100\n  },\n  \"orientation\": {\n    \"pitch\": 0,\n    \"roll\": 0,\n    \"yaw\": 0\n  },\n  \"speed\": {\n    \"x\": 0,\n    \"y\": 0,\n    \"z\": 0\n  },\n  \"camera\": {\n    \"streaming\": false,\n    \"resolution\": \"720p\"\n  }\n}"
    }
  ]
}
```

### 3. system://status

**説明**: システム全体の状態を取得

```json
{
  "uri": "system://status",
  "name": "システム状態",
  "description": "システム全体の状態情報を取得します",
  "mimeType": "application/json"
}
```

**応答例**:
```json
{
  "contents": [
    {
      "uri": "system://status",
      "mimeType": "application/json",
      "text": "{\n  \"server\": {\n    \"status\": \"running\",\n    \"version\": \"1.0.0\",\n    \"uptime\": 3600\n  },\n  \"resources\": {\n    \"cpu\": 25.5,\n    \"memory\": 62.3,\n    \"disk\": 45.8\n  },\n  \"drones\": {\n    \"connected\": 1,\n    \"total\": 2\n  }\n}"
    }
  ]
}
```

## 🔄 プロトコル通信

### 初期化シーケンス

```json
// 1. クライアントからの初期化要求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {}
    },
    "clientInfo": {
      "name": "Claude Desktop",
      "version": "1.0.0"
    }
  }
}

// 2. サーバーからの応答
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "MFG Drone MCP Server",
      "version": "1.0.0"
    }
  }
}
```

### ツール一覧取得

```json
// 3. ツール一覧要求
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}

// 4. ツール一覧応答
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "connect_drone",
        "description": "ドローンに接続します",
        "inputSchema": { /* スキーマ */ }
      },
      {
        "name": "takeoff_drone",
        "description": "ドローンを離陸させます",
        "inputSchema": { /* スキーマ */ }
      }
      // ... 他のツール
    ]
  }
}
```

### リソース一覧取得

```json
// 5. リソース一覧要求
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "resources/list"
}

// 6. リソース一覧応答
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resources": [
      {
        "uri": "drone://available",
        "name": "利用可能なドローン一覧",
        "description": "現在利用可能なドローンの一覧を取得します",
        "mimeType": "application/json"
      },
      {
        "uri": "drone://status/{drone_id}",
        "name": "ドローン状態情報",
        "description": "指定されたドローンの詳細な状態情報を取得します",
        "mimeType": "application/json"
      }
      // ... 他のリソース
    ]
  }
}
```

## ⚠️ エラーハンドリング

### MCP エラー構造

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Tool execution failed",
    "data": {
      "tool_name": "takeoff_drone",
      "error_details": {
        "error_id": "DRONE_NOT_READY",
        "user_message": "ドローンが操作可能な状態ではありません",
        "technical_message": "Drone battery level too low",
        "suggestions": [
          "バッテリーを充電してください",
          "ドローンを再起動してください"
        ],
        "recovery_actions": ["CHARGE_BATTERY", "RESTART_DRONE"]
      }
    }
  }
}
```

### エラーコード一覧

| コード | 名前 | 説明 |
|-------|------|------|
| -32001 | Tool execution failed | ツール実行エラー |
| -32002 | Resource not found | リソース未発見 |
| -32003 | Invalid arguments | 引数エラー |
| -32004 | Security violation | セキュリティ違反 |
| -32005 | System overload | システム過負荷 |

### エラー対応手順

1. **エラー検出**: システムがエラーを検出
2. **エラー分類**: エラーの種類と重要度を判定
3. **詳細情報生成**: ユーザー向けとシステム向けの情報を生成
4. **復旧提案**: 自動復旧と手動復旧の提案
5. **MCP応答**: 標準的なMCPエラー応答を送信

## 🔒 セキュリティ

### 入力値検証

```python
def validate_drone_id(drone_id: str) -> bool:
    """ドローンIDの検証"""
    if not drone_id:
        return False
    if len(drone_id) > 50:
        return False
    if not re.match(r'^[a-zA-Z0-9_-]+$', drone_id):
        return False
    return True

def validate_command(command: str) -> bool:
    """自然言語コマンドの検証"""
    if not command:
        return False
    if len(command) > 1000:
        return False
    
    # 危険なパターンの検出
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'eval\s*\(',
        r'exec\s*\(',
        r'<iframe',
        r'<object',
        r'<embed'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    return True
```

### 認証・認可

```python
def check_permissions(tool_name: str, user_context: dict) -> bool:
    """ツール実行権限の確認"""
    required_permissions = {
        'connect_drone': ['read', 'write'],
        'takeoff_drone': ['write', 'control'],
        'land_drone': ['write', 'control'],
        'move_drone': ['write', 'control'],
        'rotate_drone': ['write', 'control'],
        'take_photo': ['write', 'camera'],
        'execute_natural_language_command': ['write', 'control'],
        'emergency_stop': ['write', 'emergency']
    }
    
    user_permissions = user_context.get('permissions', [])
    required = required_permissions.get(tool_name, [])
    
    return all(perm in user_permissions for perm in required)
```

### セキュリティ機能

- **入力値検証**: 全パラメータの厳密な検証
- **パターン検出**: 危険なパターンの自動検出
- **権限管理**: ツールベースの権限制御
- **レート制限**: API呼び出し頻度の制限
- **監査ログ**: 全操作の記録
- **暗号化**: 通信データの暗号化

## 📈 パフォーマンス

### 処理時間

| 処理 | 平均時間 | 最大時間 |
|------|----------|----------|
| ツール呼び出し | 420ms | 2,000ms |
| リソース取得 | 180ms | 1,000ms |
| 自然言語解析 | 580ms | 2,000ms |
| ドローン制御 | 1,200ms | 5,000ms |

### 最適化技術

- **非同期処理**: asyncio を使用した並行処理
- **キャッシュ**: 頻繁にアクセスされるデータのキャッシュ
- **プリコンパイル**: 正規表現の事前コンパイル
- **プールアクセス**: 接続プールによる効率的なリソース管理

### 監視指標

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'tool_calls': 0,
            'resource_reads': 0,
            'errors': 0,
            'average_response_time': 0.0,
            'peak_memory_usage': 0
        }
    
    def record_tool_call(self, tool_name: str, duration: float):
        self.metrics['tool_calls'] += 1
        self.update_response_time(duration)
    
    def record_resource_read(self, uri: str, duration: float):
        self.metrics['resource_reads'] += 1
        self.update_response_time(duration)
```

## 🚀 拡張性

### プラグインアーキテクチャ

```python
class MCPToolPlugin:
    """MCPツールプラグインベースクラス"""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_tool_definition(self) -> dict:
        """ツール定義を返す"""
        raise NotImplementedError
    
    async def execute(self, arguments: dict) -> dict:
        """ツールを実行する"""
        raise NotImplementedError
    
    def validate_arguments(self, arguments: dict) -> bool:
        """引数を検証する"""
        return True

class CustomDronePlugin(MCPToolPlugin):
    """カスタムドローンプラグイン例"""
    
    def __init__(self):
        super().__init__("custom_drone_control")
    
    def get_tool_definition(self) -> dict:
        return {
            "name": "custom_drone_control",
            "description": "カスタムドローン制御",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "parameters": {"type": "object"}
                }
            }
        }
    
    async def execute(self, arguments: dict) -> dict:
        action = arguments.get("action")
        parameters = arguments.get("parameters", {})
        
        # カスタム制御ロジック
        result = await self.perform_custom_action(action, parameters)
        
        return {
            "content": [{
                "type": "text",
                "text": f"カスタム制御実行: {action}\n結果: {result}"
            }]
        }
```

### 新しいツールの追加

```python
# 新しいツールの登録
def register_tool(server: MCPServer, plugin: MCPToolPlugin):
    tool_def = plugin.get_tool_definition()
    
    @server.call_tool()
    async def tool_handler(request: CallToolRequest) -> CallToolResult:
        if request.name == plugin.name:
            if not plugin.validate_arguments(request.arguments):
                raise ValueError("Invalid arguments")
            
            return await plugin.execute(request.arguments)
        
        raise ValueError(f"Unknown tool: {request.name}")

# 使用例
custom_plugin = CustomDronePlugin()
register_tool(server, custom_plugin)
```

### リソースの拡張

```python
class MCPResourceProvider:
    """MCPリソースプロバイダーベースクラス"""
    
    def __init__(self, uri_pattern: str):
        self.uri_pattern = uri_pattern
    
    def matches(self, uri: str) -> bool:
        """URIがパターンにマッチするかチェック"""
        return re.match(self.uri_pattern, uri) is not None
    
    async def read(self, uri: str) -> dict:
        """リソースを読み取る"""
        raise NotImplementedError
    
    def get_resource_definition(self) -> dict:
        """リソース定義を返す"""
        raise NotImplementedError

class CustomResourceProvider(MCPResourceProvider):
    """カスタムリソースプロバイダー例"""
    
    def __init__(self):
        super().__init__(r"custom://.*")
    
    async def read(self, uri: str) -> dict:
        # カスタムリソース読み取りロジック
        data = await self.fetch_custom_data(uri)
        
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(data, ensure_ascii=False)
            }]
        }
    
    def get_resource_definition(self) -> dict:
        return {
            "uri": "custom://{resource_id}",
            "name": "カスタムリソース",
            "description": "カスタムリソースの説明",
            "mimeType": "application/json"
        }
```

## 📋 開発者向け情報

### デバッグ

```python
import logging
import json

# デバッグレベルの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_mcp_request(request: dict):
    """MCP要求をデバッグ出力"""
    logger.debug(f"MCP Request: {json.dumps(request, indent=2, ensure_ascii=False)}")

def debug_mcp_response(response: dict):
    """MCP応答をデバッグ出力"""
    logger.debug(f"MCP Response: {json.dumps(response, indent=2, ensure_ascii=False)}")
```

### テスト

```python
import pytest
import asyncio
from unittest.mock import Mock

@pytest.fixture
def mcp_server():
    """テスト用MCPサーバー"""
    return create_test_mcp_server()

@pytest.mark.asyncio
async def test_takeoff_drone(mcp_server):
    """ドローン離陸テスト"""
    request = CallToolRequest(
        name="takeoff_drone",
        arguments={"drone_id": "test_drone"}
    )
    
    result = await mcp_server.call_tool(request)
    
    assert result.content[0].text.startswith("✅ ドローン離陸成功")

@pytest.mark.asyncio
async def test_resource_read(mcp_server):
    """リソース読み取りテスト"""
    result = await mcp_server.read_resource("drone://available")
    
    assert result.contents[0].mimeType == "application/json"
    data = json.loads(result.contents[0].text)
    assert "drones" in data
```

## 📚 参考資料

### MCP仕様

- [MCP 公式仕様](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [JSONRPC 2.0仕様](https://www.jsonrpc.org/specification)

### 関連ドキュメント

- [setup.md](./setup.md) - MCPホスト設定方法
- [command_reference.md](./command_reference.md) - コマンドリファレンス
- [error_reference.md](./error_reference.md) - エラーリファレンス
- [FAQ.md](./FAQ.md) - よくある質問

---

**🎉 MCP プロトコル仕様書完成！**

**📊 実装状況:**
- **MCPツール**: 8種類完全実装
- **MCPリソース**: 3種類完全実装
- **プロトコル準拠**: MCP仕様完全準拠
- **セキュリティ**: 包括的セキュリティ機能
- **拡張性**: プラグインアーキテクチャ対応

**🔧 技術スタック:**
- **プロトコル**: JSONRPC 2.0 over stdio
- **実装言語**: Python 3.9+
- **SDK**: MCP Python SDK 1.0.0+
- **非同期処理**: asyncio

**📅 最終更新**: 2025-07-16  
**バージョン**: Phase 4 - v1.0.0  
**作成者**: MFG Drone Team