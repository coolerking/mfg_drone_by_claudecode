# Multi-stage Docker build for MCP Drone Server Node.js
FROM node:18-alpine AS builder

# アプリケーション作業ディレクトリ設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール（開発依存関係も含む）
RUN npm ci

# ソースコードをコピー
COPY . .

# TypeScriptビルド
RUN npm run build

# テスト実行（ビルド検証）
RUN npm test

# 本番用イメージ
FROM node:18-alpine AS production

# セキュリティ: 非rootユーザー作成
RUN addgroup -g 1001 -S nodejs && \
    adduser -S mcp -u 1001

# アプリケーション作業ディレクトリ設定
WORKDIR /app

# package.jsonをコピー
COPY package*.json ./

# 本番用依存関係のみインストール
RUN npm ci --only=production && npm cache clean --force

# ビルド済みアプリケーションをコピー
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/README.md ./

# ログディレクトリ作成
RUN mkdir -p logs && chown -R mcp:nodejs /app

# 非rootユーザーに切り替え
USER mcp

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "const http = require('http'); const options = { host: 'localhost', port: process.env.MCP_PORT || 3001, path: '/health', timeout: 2000 }; const req = http.request(options, (res) => { res.statusCode === 200 ? process.exit(0) : process.exit(1); }); req.on('error', () => process.exit(1)); req.end();"

# 環境変数
ENV NODE_ENV=production
ENV MCP_PORT=3001
ENV LOG_LEVEL=info

# ポート公開
EXPOSE 3001

# アプリケーション起動
CMD ["npm", "start"]