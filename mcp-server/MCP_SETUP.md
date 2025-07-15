# MCP ドローン制御システム クイックセットアップ

このドキュメントは、MCPドローン制御システムを各MCPホストで素早く設定するためのクイックガイドです。

## 🚀 クイックスタート

### 1. 前提条件の確認

```bash
# Python バージョン確認
python --version  # 3.9以上が必要

# 依存関係のインストール
pip install -r requirements.txt

# 設定検証スクリプトの実行
python validate_mcp_config.py
```

### 2. MCPサーバーの動作確認

```bash
# MCPサーバーのテスト
python test_mcp_server.py

# 実際の起動テスト
python src/mcp_main.py
```

### 3. 設定ファイルの準備

設定検証スクリプトを実行すると、各MCPホスト用の設定ファイルが自動生成されます：

- `claude_desktop_config.json` - Claude Desktop用
- `vscode_settings.json` - VS Code用
- `mcp_config.json` - 汎用設定

## 📋 各MCPホストでの設定

### Claude Desktop

1. 設定ファイルの場所を確認：
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. 生成された `claude_desktop_config.json` の内容を設定ファイルに追加

3. Claude Desktop を再起動

### VS Code

1. プロジェクトの `.vscode/settings.json` に `vscode_settings.json` の内容を追加

2. VS Code を再起動

### Claude Code

1. 設定ファイルの場所：
   - **Windows**: `%APPDATA%\Claude Code\mcp_config.json`
   - **macOS**: `~/Library/Application Support/Claude Code/mcp_config.json`
   - **Linux**: `~/.config/claude-code/mcp_config.json`

2. 生成された `mcp_config.json` の内容を設定ファイルに追加

### Dify

1. Dify管理画面で「プラグイン」→「MCPプラグイン」を選択

2. 以下の情報を入力：
   - **名前**: `MFG Drone MCP Server`
   - **コマンド**: `python`
   - **引数**: `[絶対パス]/src/mcp_main.py`
   - **環境変数**: `PYTHONPATH=[絶対パス]`

## 🔧 利用可能なコマンド

MCPサーバーが正常に設定されると、以下のコマンドが利用可能になります：

### 基本操作
```
ドローンに接続してください
ドローンを離陸させてください
右に50センチ移動してください
時計回りに90度回転してください
写真を撮ってください
ドローンを着陸させてください
```

### 状態確認
```
ドローンの状態を確認してください
利用可能なドローンを表示してください
システムの状態を確認してください
```

### 緊急時
```
緊急停止してください
```

## 🛠️ トラブルシューティング

### よくある問題

1. **MCPサーバーが起動しない**
   ```bash
   # ログを確認
   python src/mcp_main.py
   
   # 依存関係を再インストール
   pip install --force-reinstall -r requirements.txt
   ```

2. **パスエラー**
   ```bash
   # 絶対パスを使用
   python validate_mcp_config.py  # サンプル設定を再生成
   ```

3. **権限エラー**
   ```bash
   # 実行権限を付与
   chmod +x src/mcp_main.py
   ```

### ログの確認

```bash
# デバッグモードで実行
export LOG_LEVEL=DEBUG
python src/mcp_main.py

# ログファイルの確認
tail -f /tmp/mcp_server.log
```

## 📚 詳細ドキュメント

より詳細な設定手順や使用方法については、以下のドキュメントを参照してください：

- [setup.md](./docs/setup.md) - 詳細なセットアップガイド
- [FAQ.md](./docs/FAQ.md) - よくある質問
- [command_reference.md](./docs/command_reference.md) - コマンドリファレンス
- [error_reference.md](./docs/error_reference.md) - エラーリファレンス

## 🤝 サポート

問題が発生した場合は、以下のリソースを利用してください：

- [GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- [プロジェクトWiki](https://github.com/coolerking/mfg_drone_by_claudecode/wiki)
- [FAQ](./docs/FAQ.md)

---

**最終更新**: 2025-07-15  
**バージョン**: 1.0.0