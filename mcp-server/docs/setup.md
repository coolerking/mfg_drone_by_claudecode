# MCP ドローン制御システム セットアップガイド

このドキュメントでは、MCP（Model Context Protocol）ドローン制御システムを各MCPホストに登録する方法を説明します。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [Claude Desktop での設定](#claude-desktop-での設定)
4. [Visual Studio Code での設定](#visual-studio-code-での設定)
5. [Claude Code での設定](#claude-code-での設定)
6. [Dify での設定](#dify-での設定)
7. [トラブルシューティング](#トラブルシューティング)
8. [利用可能なツール](#利用可能なツール)
9. [利用可能なリソース](#利用可能なリソース)

## 概要

このMCPサーバーは、自然言語でドローンを制御できる包括的なシステムです。以下の機能を提供します：

- **ドローン制御**: 離陸、着陸、移動、回転
- **カメラ操作**: 写真撮影、ビデオ録画
- **自然言語処理**: 日本語コマンドの理解・実行
- **システム監視**: ドローン状態の確認
- **緊急停止**: 安全機能

## 前提条件

### システム要件

- Python 3.9以上
- MCP SDK 1.0.0以上
- 必要なPythonパッケージ（requirements.txtを参照）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-server

# 依存関係をインストール
pip install -r requirements.txt

# MCPサーバーをテスト
python test_mcp_server.py
```

### MCPサーバーの起動確認

```bash
# MCPモードでサーバーを起動
python start_mcp_server_unified.py --mode mcp

# または
python src/mcp_main.py
```

## Claude Desktop での設定

### 1. 設定ファイルの場所

Claude Desktopの設定ファイルは以下の場所にあります：

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/claude/claude_desktop_config.json
```

### 2. 設定の追加

設定ファイルに以下を追加します：

```json
{
  "mcpServers": {
    "mfg-drone-mcp-server": {
      "command": "python",
      "args": [
        "/path/to/mfg_drone_by_claudecode/mcp-server/src/mcp_main.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mfg_drone_by_claudecode/mcp-server",
        "DRONE_MODE": "auto",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Claude Desktopの再起動

設定を保存後、Claude Desktopを再起動してください。

### 4. 動作確認

Claude Desktopで以下のコマンドを試してください：

```
利用可能なドローンツールを表示してください
```

## Visual Studio Code での設定

### 1. MCP拡張機能のインストール

VS Code Marketplaceから「MCP」拡張機能をインストールします。

### 2. ワークスペース設定

プロジェクトの `.vscode/settings.json` に以下を追加：

```json
{
  "mcp.servers": {
    "mfg-drone-mcp-server": {
      "command": "python",
      "args": [
        "/path/to/mfg_drone_by_claudecode/mcp-server/src/mcp_main.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mfg_drone_by_claudecode/mcp-server",
        "DRONE_MODE": "auto"
      }
    }
  }
}
```

### 3. グローバル設定（オプション）

VS Codeのグローバル設定でも同様に設定できます：

1. `Ctrl+Shift+P` (Windows/Linux) または `Cmd+Shift+P` (macOS)
2. 「Preferences: Open Settings (JSON)」を選択
3. 上記の設定を追加

### 4. 動作確認

VS Codeのコマンドパレットで「MCP: Connect to Server」を選択し、「mfg-drone-mcp-server」を選択してください。

## Claude Code での設定

### 1. 設定ファイルの場所

Claude Codeの設定ファイルは以下の場所にあります：

**Windows:**
```
%APPDATA%\Claude Code\mcp_config.json
```

**macOS:**
```
~/Library/Application Support/Claude Code/mcp_config.json
```

**Linux:**
```
~/.config/claude-code/mcp_config.json
```

### 2. 設定の追加

設定ファイルに以下を追加します：

```json
{
  "mcpServers": {
    "mfg-drone-mcp-server": {
      "command": "python",
      "args": [
        "/path/to/mfg_drone_by_claudecode/mcp-server/src/mcp_main.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mfg_drone_by_claudecode/mcp-server",
        "DRONE_MODE": "auto",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. 環境変数の設定（オプション）

```bash
# 環境変数でMCPサーバーを指定
export CLAUDE_MCP_SERVER_CONFIG="/path/to/mfg_drone_by_claudecode/mcp-server/mcp_config.json"
```

### 4. 動作確認

Claude Codeで以下のコマンドを実行：

```bash
claude-code --mcp-server mfg-drone-mcp-server
```

## Dify での設定

### 1. プラグイン設定

Difyの管理画面で「プラグイン」→「MCPプラグイン」を選択します。

### 2. MCPサーバーの登録

以下の情報を入力します：

- **名前**: `MFG Drone MCP Server`
- **識別子**: `mfg-drone-mcp-server`
- **コマンド**: `python`
- **引数**: `/path/to/mfg_drone_by_claudecode/mcp-server/src/mcp_main.py`
- **環境変数**:
  ```
  PYTHONPATH=/path/to/mfg_drone_by_claudecode/mcp-server
  DRONE_MODE=auto
  LOG_LEVEL=INFO
  ```

### 3. 接続テスト

「接続テスト」ボタンをクリックして、MCPサーバーとの接続を確認します。

### 4. ワークフローでの使用

Difyのワークフローで「MCP Tool」ノードを追加し、登録したMCPサーバーを選択してください。

## トラブルシューティング

### よくある問題と解決方法

#### 1. MCPサーバーが起動しない

**症状**: MCPサーバーが起動しない、または接続できない

**解決方法**:
```bash
# 依存関係を確認
pip install -r requirements.txt

# 手動でテスト
python test_mcp_server.py

# ログを確認
tail -f /tmp/mcp_server.log
```

#### 2. パスが見つからない

**症状**: "No such file or directory" エラー

**解決方法**:
- 設定ファイルのパスを絶対パスに変更
- PYTHONPATHが正しく設定されているか確認

#### 3. 権限エラー

**症状**: Permission denied エラー

**解決方法**:
```bash
# 実行権限を付与
chmod +x src/mcp_main.py

# 仮想環境を使用
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. ドローン接続エラー

**症状**: ドローンに接続できない

**解決方法**:
```bash
# シミュレーションモードで起動
export DRONE_MODE=simulation
python src/mcp_main.py

# 実機検出を試す
export DRONE_MODE=auto
python src/mcp_main.py
```

### ログの確認

MCPサーバーのログは以下の場所に保存されます：

```bash
# ログファイルの場所
tail -f /tmp/mcp_server.log

# デバッグレベルでログを出力
export LOG_LEVEL=DEBUG
python src/mcp_main.py
```

## 利用可能なツール

このMCPサーバーでは以下のツールが利用可能です：

### 1. connect_drone
**説明**: ドローンに接続します
**パラメータ**: 
- `drone_type`: ドローンの種類（"tello"、"simulation"）

### 2. takeoff_drone
**説明**: ドローンを離陸させます
**パラメータ**: 
- `drone_id`: ドローンのID

### 3. land_drone
**説明**: ドローンを着陸させます
**パラメータ**: 
- `drone_id`: ドローンのID

### 4. move_drone
**説明**: ドローンを移動させます
**パラメータ**: 
- `drone_id`: ドローンのID
- `direction`: 移動方向（forward、backward、left、right、up、down）
- `distance`: 移動距離（1-500cm）
- `speed`: 移動速度（10-100cm/s）

### 5. rotate_drone
**説明**: ドローンを回転させます
**パラメータ**: 
- `drone_id`: ドローンのID
- `direction`: 回転方向（clockwise、counterclockwise）
- `angle`: 回転角度（1-360度）

### 6. take_photo
**説明**: ドローンで写真を撮影します
**パラメータ**: 
- `drone_id`: ドローンのID
- `filename`: 保存するファイル名（オプション）

### 7. execute_natural_language_command
**説明**: 自然言語コマンドを実行します
**パラメータ**: 
- `command`: 日本語のコマンド
- `drone_id`: ドローンのID（オプション）

### 8. emergency_stop
**説明**: 緊急停止を実行します
**パラメータ**: 
- `drone_id`: ドローンのID

## 利用可能なリソース

### 1. drone://available
**説明**: 利用可能なドローンの一覧を取得

### 2. drone://status/{drone_id}
**説明**: 指定されたドローンの状態を取得

### 3. system://status
**説明**: システム全体の状態を取得

## 使用例

### 基本的な使用方法

```
# ドローンに接続
ドローンに接続してください

# 離陸
ドローンを離陸させてください

# 移動
右に50センチ移動してください

# 写真撮影
写真を撮ってください

# 着陸
ドローンを着陸させてください
```

### 高度な使用方法

```
# 複雑なコマンド
ドローンを前方に100センチ移動させて、右に90度回転し、写真を撮影してください

# 状態確認
ドローンの状態を確認してください

# 緊急停止
緊急停止してください
```

## サポート

問題が発生した場合は、以下のリソースを参照してください：

- **FAQ**: [FAQ.md](./FAQ.md)
- **エラーリファレンス**: [error_reference.md](./error_reference.md)
- **コマンドリファレンス**: [command_reference.md](./command_reference.md)
- **GitHub Issues**: [プロジェクトのIssues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)

---

**更新日**: 2025-07-15  
**バージョン**: 1.0.0  
**作成者**: MFG Drone Team