# ハイブリッドシステム運用ガイド - Phase 3

## 概要

Phase 3では、FastAPIサーバーとMCPサーバーを同時に実行できるハイブリッド運用モードを実装しました。これにより、HTTPベースのAPIとMCPプロトコルの両方を同時に提供できます。

## 主要機能

### 🔧 ハイブリッドプロセス管理
- **マルチプロセス実行**: FastAPIとMCPサーバーを独立したプロセスで並行実行
- **プロセス監視**: 各サーバーの状態を常時監視
- **自動復旧**: プロセス障害時の自動再起動機能
- **ポート管理**: 自動ポート競合回避

### 📊 統合システム監視
- **リアルタイムメトリクス**: CPU、メモリ、ディスク使用率の監視
- **サーバー個別監視**: 各サーバーの応答時間、ヘルス状態を監視
- **アラート機能**: 閾値超過時の自動アラート
- **メトリクス履歴**: 最大100件のメトリクス履歴保存

### 🚀 3つのハイブリッドモード

#### 1. 基本ハイブリッドモード
- **FastAPI Server** (ポート8000) + **MCP Server**
- HTTP APIとMCPプロトコルの基本機能

#### 2. 拡張ハイブリッドモード
- **Enhanced FastAPI Server** (ポート8001) + **MCP Server**
- 高度な自然言語処理とMCPプロトコル

#### 3. フルハイブリッドモード
- **FastAPI Server** (ポート8000) + **Enhanced FastAPI Server** (ポート8001) + **MCP Server**
- 全機能を同時提供

## 使用方法

### 1. 専用ハイブリッドサーバーの起動

```bash
# 基本ハイブリッドモード
python start_hybrid_server.py --mode basic

# 拡張ハイブリッドモード
python start_hybrid_server.py --mode enhanced

# フルハイブリッドモード
python start_hybrid_server.py --mode full

# ステータス確認
python start_hybrid_server.py --status
```

### 2. 統合起動スクリプトの使用

```bash
# 基本ハイブリッドモード
python start_mcp_server_unified.py --mode hybrid

# 拡張ハイブリッドモード
python start_mcp_server_unified.py --mode hybrid --enhanced

# フルハイブリッドモード
python start_mcp_server_unified.py --mode hybrid --full

# 従来の単一モード（下位互換）
python start_mcp_server_unified.py --mode fastapi
python start_mcp_server_unified.py --mode mcp
```

## サーバー構成

### 基本ハイブリッドモード
```
┌─────────────────────┐    ┌─────────────────────┐
│  FastAPI Server     │    │   MCP Server        │
│  (ポート: 8000)      │    │  (stdio protocol)   │
│                     │    │                     │
│  - HTTP REST API    │    │  - MCP Tools        │
│  - OpenAPI文書      │    │  - MCP Resources    │
│  - バッチ処理       │    │  - ドローン制御     │
│                     │    │  - 自然言語処理     │
└─────────────────────┘    └─────────────────────┘
           │                           │
           └─────────┬───────────────────┘
                     │
           ┌─────────────────────┐
           │ バックエンドAPI     │
           │  (共有リソース)     │
           └─────────────────────┘
```

### 拡張ハイブリッドモード
```
┌─────────────────────┐    ┌─────────────────────┐
│Enhanced FastAPI     │    │   MCP Server        │
│  (ポート: 8001)      │    │  (stdio protocol)   │
│                     │    │                     │
│  - 高度なNLP処理    │    │  - MCP Tools        │
│  - 依存関係分析     │    │  - MCP Resources    │
│  - スマートエラー回復│    │  - ドローン制御     │
│  - 実行分析         │    │  - 自然言語処理     │
└─────────────────────┘    └─────────────────────┘
           │                           │
           └─────────┬───────────────────┘
                     │
           ┌─────────────────────┐
           │ バックエンドAPI     │
           │  (共有リソース)     │
           └─────────────────────┘
```

### フルハイブリッドモード
```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  FastAPI Server     │  │Enhanced FastAPI     │  │   MCP Server        │
│  (ポート: 8000)      │  │  (ポート: 8001)      │  │  (stdio protocol)   │
│                     │  │                     │  │                     │
│  - HTTP REST API    │  │  - 高度なNLP処理    │  │  - MCP Tools        │
│  - OpenAPI文書      │  │  - 依存関係分析     │  │  - MCP Resources    │
│  - バッチ処理       │  │  - スマートエラー回復│  │  - ドローン制御     │
│                     │  │  - 実行分析         │  │  - 自然言語処理     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                           │                           │
           └─────────────────┬─────────────────────┬───────────────┘
                             │                     │
                   ┌─────────────────────┐
                   │ バックエンドAPI     │
                   │  (共有リソース)     │
                   └─────────────────────┘
```

## アクセス方法

### HTTP API アクセス

**基本ハイブリッドモード**:
- API: `http://localhost:8000`
- ドキュメント: `http://localhost:8000/docs`

**拡張ハイブリッドモード**:
- API: `http://localhost:8001`
- ドキュメント: `http://localhost:8001/docs`

**フルハイブリッドモード**:
- 基本API: `http://localhost:8000`
- 拡張API: `http://localhost:8001`
- 基本ドキュメント: `http://localhost:8000/docs`
- 拡張ドキュメント: `http://localhost:8001/docs`

### MCPサーバーアクセス

MCPサーバーは各MCPホストから利用可能です：

**Claude Desktop**:
```json
{
  "mcpServers": {
    "mfg-drone-mcp-server": {
      "command": "python",
      "args": ["/path/to/mcp-server/src/mcp_main.py"]
    }
  }
}
```

**VS Code**:
```json
{
  "mcp.servers": {
    "mfg-drone-mcp-server": {
      "command": "python",
      "args": ["/path/to/mcp-server/src/mcp_main.py"]
    }
  }
}
```

## 監視とメトリクス

### システムメトリクス
- **CPU使用率**: システム全体のCPU使用率
- **メモリ使用率**: システム全体のメモリ使用率
- **ディスク使用率**: システム全体のディスク使用率
- **ネットワーク接続数**: アクティブなネットワーク接続数
- **プロセス数**: アクティブなプロセス数

### サーバー個別メトリクス
- **プロセス状態**: 実行中、停止、エラー等
- **CPU使用率**: 各サーバーのCPU使用率
- **メモリ使用量**: 各サーバーのメモリ使用量（MB）
- **応答時間**: HTTPサーバーの応答時間（秒）
- **ヘルス状態**: Healthy、Degraded、Unhealthy
- **稼働時間**: 各サーバーの稼働時間

### アラート閾値
- **CPU使用率**: 80%以上で警告
- **メモリ使用率**: 85%以上で警告
- **ディスク使用率**: 90%以上で警告
- **応答時間**: 5秒以上で警告

## トラブルシューティング

### 1. ポート競合エラー
```bash
# エラー: Port 8000 is already in use
# 解決策: 他のプロセスを停止するか、別のポートを使用

# 使用中のポートを確認
lsof -i :8000
lsof -i :8001

# プロセスを停止
kill -9 <PID>
```

### 2. プロセス起動失敗
```bash
# ログを確認
tail -f /tmp/mcp_server.log

# 依存関係を確認
pip install -r requirements.txt

# 手動でサーバーを起動してテスト
python src/main.py
python src/enhanced_main.py
python src/mcp_main.py
```

### 3. メモリ不足
```bash
# システムメモリを確認
free -h

# 不要なプロセスを停止
# 単一モードでの実行を検討
python start_mcp_server_unified.py --mode fastapi
```

### 4. MCPサーバー接続エラー
```bash
# MCPサーバーを単独で起動してテスト
python src/mcp_main.py

# 設定ファイルを確認
cat docs/setup.md
```

## 開発・テスト

### テストの実行
```bash
# ハイブリッドシステムテスト
python test_hybrid_system.py

# 個別サーバーテスト
python test_mcp_server.py
```

### デバッグモード
```bash
# デバッグログレベルで起動
python start_hybrid_server.py --mode basic --log-level DEBUG

# 詳細なログ出力
export LOG_LEVEL=DEBUG
python start_hybrid_server.py --mode basic
```

## 設定ファイル

### サーバー設定
各サーバーの設定は `core/hybrid_process_manager.py` の `default_configs` で定義されています。

### 監視設定
監視設定は `core/hybrid_system_monitor.py` の `alert_thresholds` で定義されています。

## 注意事項

1. **リソース要件**: フルハイブリッドモードは大量のリソースを消費します
2. **ポート管理**: 複数のHTTPサーバーが異なるポートを使用します
3. **プロセス管理**: 各サーバーは独立したプロセスで動作します
4. **データ共有**: 全サーバーは同じバックエンドAPIを共有します
5. **監視**: 統合監視システムが全サーバーの状態を追跡します

## 今後の拡張

- **ロードバランシング**: 複数のサーバーインスタンス間でのロードバランシング
- **自動スケーリング**: 負荷に応じた自動スケーリング
- **メトリクス可視化**: Grafanaなどでのメトリクス可視化
- **アラート通知**: Slack、メール等での通知機能
- **設定管理**: 動的な設定変更機能

---

**作成日**: 2025-07-15  
**バージョン**: Phase 3 - v1.0.0  
**作成者**: MFG Drone Team