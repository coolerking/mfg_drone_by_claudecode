# MCP Node.js Server デプロイメントガイド

Node.js/TypeScript版 MCP（Model Context Protocol）サーバーのデプロイメント手順です。

## 概要

MCP Node.js サーバーは以下の方法でデプロイできます：

1. **npm パッケージとして直接インストール**
2. **npx を使った実行**
3. **Docker コンテナとしてデプロイ**
4. **ソースコードからビルド・実行**

## 1. npm パッケージインストール

### グローバルインストール

```bash
# npmでグローバルインストール
npm install -g mcp-drone-server-nodejs

# 実行
mcp-drone-server
```

### ローカルプロジェクトでの利用

```bash
# プロジェクトに追加
npm install mcp-drone-server-nodejs

# package.json scripts で実行
{
  "scripts": {
    "mcp": "mcp-drone-server"
  }
}

npm run mcp
```

## 2. npx を使った実行

```bash
# パッケージをインストールせずに実行
npx mcp-drone-server-nodejs

# 特定バージョンを指定して実行
npx mcp-drone-server-nodejs@latest
```

## 3. Docker デプロイメント

### 単体コンテナとして実行

```bash
# プロジェクトルートディレクトリで
cd mcp-server-nodejs

# Dockerイメージをビルド
docker build -t mcp-drone-server:latest .

# コンテナを実行
docker run -d \
  --name mcp-drone-server \
  -p 3001:3001 \
  -e BACKEND_URL=http://localhost:8000 \
  -e LOG_LEVEL=info \
  mcp-drone-server:latest
```

### Docker Compose を使った実行

```bash
# 本番環境用の構成で実行
docker-compose -f docker-compose.prod.yml up -d

# MCP Node.js サーバーのログを確認
docker-compose -f docker-compose.prod.yml logs -f mcp-server-nodejs
```

## 4. ソースコードからビルド・実行

### 開発環境でのセットアップ

```bash
# リポジトリクローン
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-server-nodejs

# 依存関係インストール
npm install

# TypeScript ビルド
npm run build

# 本番モードで実行
npm start

# または開発モードで実行（ホットリロード付き）
npm run dev
```

### ビルドの最適化

```bash
# クリーンビルド
npm run clean
npm run build

# テスト実行
npm test

# カバレッジレポート生成
npm run test:coverage

# コード品質チェック
npm run lint
npm run format:check
```

## 環境設定

### 環境変数

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `NODE_ENV` | `development` | 実行環境（development/production） |
| `MCP_PORT` | `3001` | MCPサーバーのリスニングポート |
| `BACKEND_URL` | `http://localhost:8000` | バックエンドAPIのURL |
| `LOG_LEVEL` | `info` | ログレベル（debug/info/warn/error） |
| `TIMEOUT` | `10000` | HTTPリクエストタイムアウト（ms） |

### .env ファイル例

プロジェクトルートまたは `mcp-server-nodejs/` ディレクトリに `.env` ファイルを作成：

```bash
# MCP Server 設定
NODE_ENV=production
MCP_PORT=3001
BACKEND_URL=http://localhost:8000
LOG_LEVEL=info
TIMEOUT=10000

# セキュリティ設定（本番環境）
JWT_SECRET=your-secret-key-here
API_RATE_LIMIT=100
```

## 運用監視

### ヘルスチェック

```bash
# HTTP ヘルスチェック
curl -f http://localhost:3001/health

# または内蔵のヘルスチェック（Dockerの場合自動実行）
docker exec mcp-drone-server node -e "const http = require('http'); /* ... */"
```

### ログ監視

```bash
# Dockerコンテナのログ
docker logs -f mcp-drone-server

# ローカル実行時のログ
tail -f logs/combined.log
tail -f logs/error.log
```

### システム監視

```bash
# プロセス監視
ps aux | grep mcp-drone-server

# ポート使用状況
netstat -tulpn | grep 3001

# システムリソース使用量
docker stats mcp-drone-server  # Docker環境
top -p $(pgrep -f mcp-drone-server)  # ローカル環境
```

## トラブルシューティング

### よくある問題

#### 1. バックエンド接続エラー

**症状**：
```
Error: Backend connection failed: http://localhost:8000
```

**解決方法**：
- FastAPI バックエンドが起動していることを確認
- `BACKEND_URL` 環境変数が正しく設定されていることを確認
- ネットワーク接続・ファイアウォール設定を確認

```bash
# バックエンド接続テスト
npm run test:connection

# カスタムURLでテスト  
BACKEND_URL=http://192.168.1.100:8000 npm run test:connection
```

#### 2. ポート競合エラー

**症状**：
```
Error: listen EADDRINUSE :::3001
```

**解決方法**：
```bash
# ポート使用状況確認
netstat -tulpn | grep 3001

# 別のポートを使用
MCP_PORT=3002 npm start

# または競合プロセスを終了
sudo kill -9 $(lsof -t -i:3001)
```

#### 3. npm パッケージ公開の準備

```bash
# パッケージの検証
npm run prepublishOnly

# パッケージ内容の確認
npm pack --dry-run

# 公開前テスト
npm publish --dry-run
```

## セキュリティ考慮事項

### 本番環境での設定

```bash
# 環境変数設定（本番環境）
export NODE_ENV=production
export LOG_LEVEL=warn
export BACKEND_URL=https://api.yourdomain.com

# セキュリティヘッダー（nginx等のリバースプロキシで設定）
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### Docker セキュリティ

```bash
# 非rootユーザーでの実行（Dockerfile内で自動設定）
USER mcp

# 読み取り専用ファイルシステム
docker run --read-only \
  --tmpfs /app/logs \
  --tmpfs /tmp \
  mcp-drone-server:latest
```

## パフォーマンス最適化

### Node.js 設定

```bash
# メモリ制限設定
node --max-old-space-size=512 dist/index.js

# クラスタリング（PM2使用）
npm install -g pm2
pm2 start dist/index.js --name mcp-drone-server --instances 2
```

### Docker リソース制限

```yaml
# docker-compose.yml での設定例
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.3'
    reservations:
      memory: 256M
      cpus: '0.1'
```

## サポート・問い合わせ

問題が解決しない場合は、以下をお知らせください：

1. **環境情報**：
   ```bash
   node --version
   npm --version
   docker --version
   ```

2. **エラーログ**：
   ```bash
   # ログファイルの内容
   cat logs/error.log
   
   # 環境変数（機密情報は除く）
   env | grep -E "NODE_ENV|MCP_|BACKEND_"
   ```

3. **GitHub Issues**: https://github.com/coolerking/mfg_drone_by_claudecode/issues

---

詳細な技術情報については、[mcp-server-nodejs/README.md](../mcp-server-nodejs/README.md) も参照してください。