# MFG Drone System - デプロイメントガイド

このドキュメントでは、MFGドローンシステムのプロダクション環境への完全なデプロイメント手順を説明します。

## 📋 前提条件

### システム要件
- **OS**: Ubuntu 20.04 LTS 以上 / CentOS 8 以上 / macOS 12 以上
- **CPU**: 4コア以上推奨
- **メモリ**: 8GB以上必須、16GB推奨
- **ストレージ**: 50GB以上の空き容量
- **ネットワーク**: 安定したインターネット接続

### 必要なソフトウェア
- Docker Engine 24.0以上
- Docker Compose v2.0以上
- Git 2.30以上
- curl, wget, jq

### インストール確認
```bash
# バージョン確認
docker --version
docker compose version
git --version

# Docker サービス状態確認
sudo systemctl status docker
```

## 🚀 クイックスタート

### 1. リポジトリのクローン
```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode
```

### 2. 環境設定
```bash
# 環境変数ファイルのコピー
cp .env.production .env

# 重要: パスワードとシークレットキーを変更
nano .env
```

**必須変更項目:**
- `DB_PASSWORD`: データベースパスワード
- `JWT_SECRET`: JWT署名用シークレットキー（32文字以上）
- `GRAFANA_PASSWORD`: Grafana管理者パスワード
- `VITE_API_BASE_URL`: フロントエンドのAPIベースURL
- `VITE_WS_URL`: WebSocketサーバーURL

### 3. 一括デプロイ
```bash
# デプロイスクリプトに実行権限を付与
chmod +x scripts/deploy.sh

# デプロイ実行
./scripts/deploy.sh
```

### 4. アクセス確認
```bash
# ヘルスチェック
curl http://localhost/health
curl http://localhost:8000/health

# サービス状態確認
docker-compose -f docker-compose.prod.yml ps
```

## 🔧 詳細設定

### CI/CD パイプライン設定

#### GitHub Actions
```bash
# ワークフローファイルをコピー
mkdir -p .github/workflows
cp .github-workflows-templates/* .github/workflows/

# Dependabot設定
cp .github-workflows-templates/dependabot.yml .github/dependabot.yml
```

#### 必要なシークレット設定
GitHub リポジトリの Settings > Secrets で以下を設定：

| シークレット名 | 説明 | 例 |
|---------------|------|-----|
| `DOCKER_USERNAME` | Docker Hubユーザー名 | `your-username` |
| `DOCKER_PASSWORD` | Docker Hubパスワード | `your-password` |
| `SLACK_WEBHOOK` | Slack通知用Webhook URL | `https://hooks.slack.com/...` |
| `SSH_PRIVATE_KEY` | サーバー接続用SSH秘密鍵 | `-----BEGIN OPENSSH PRIVATE KEY-----` |
| `PROD_SERVER_HOST` | プロダクションサーバーホスト | `prod.yourdomain.com` |

### SSL/TLS 証明書設定

#### Let's Encrypt（推奨）
```bash
# Certbot インストール
sudo apt update
sudo apt install certbot

# 証明書取得
sudo certbot certonly --standalone -d yourdomain.com

# nginx設定更新
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/private.key

# 自動更新設定
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

#### 自己署名証明書（開発用）
```bash
# SSL ディレクトリ作成
mkdir -p ssl

# 自己署名証明書生成
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key \
  -out ssl/cert.pem \
  -subj "/C=JP/ST=Tokyo/L=Tokyo/O=MFG-Drone/CN=localhost"
```

### データベース設定

#### PostgreSQL 初期設定
```bash
# PostgreSQL 起動確認
docker-compose -f docker-compose.prod.yml exec postgres psql -U mfg_user -d mfg_drone_db

# データベースバックアップ
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U mfg_user mfg_drone_db > backup.sql

# データベース復元
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U mfg_user -d mfg_drone_db
```

#### Redis 設定
```bash
# Redis 設定ファイル作成
cat > monitoring/redis.conf << EOF
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF
```

## 📊 監視・ログ設定

### Prometheus 設定
監視メトリクスの確認とカスタマイズ：

```bash
# Prometheus 設定確認
cat monitoring/prometheus.yml

# カスタムアラート追加
nano monitoring/alerts.yml

# 設定再読み込み
curl -X POST http://localhost:9090/-/reload
```

### Grafana ダッシュボード

初回ログイン後の設定：

1. **ログイン**: http://localhost:3001
   - ユーザー: `admin`
   - パスワード: `GRAFANA_PASSWORD`の値

2. **データソース追加**:
   - Prometheus: `http://prometheus:9090`
   - InfluxDB（オプション）: `http://influxdb:8086`

3. **推奨ダッシュボード**:
   - Node Exporter Full: ID `1860`
   - Docker Container Metrics: ID `193`
   - Nginx Log Metrics: ID `12559`

### ログ集約設定

#### ELK Stack（オプション）
```yaml
# docker-compose.prod.yml に追加
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./monitoring/logstash:/usr/share/logstash/pipeline

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## 🔒 セキュリティ設定

### ファイアウォール設定
```bash
# UFW有効化
sudo ufw enable

# 必要ポートのみ開放
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw deny 8000     # Backend（外部からの直接アクセス拒否）
sudo ufw deny 5432     # PostgreSQL
sudo ufw deny 6379     # Redis
```

### Docker セキュリティ
```bash
# Docker daemon セキュリティ設定
sudo cat > /etc/docker/daemon.json << EOF
{
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json"
}
EOF

sudo systemctl restart docker
```

### 定期セキュリティ更新
```bash
# システム更新スクリプト
cat > scripts/security-update.sh << 'EOF'
#!/bin/bash
# システムパッケージ更新
sudo apt update && sudo apt upgrade -y

# Docker イメージ更新
docker-compose -f docker-compose.prod.yml pull

# 脆弱性スキャン
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --exit-code 1 mfg-drone-frontend:latest

# 設定ファイル権限確認
chmod 600 .env
chmod 600 ssl/private.key
EOF

chmod +x scripts/security-update.sh

# 週次実行設定
echo "0 2 * * 0 $(pwd)/scripts/security-update.sh" | crontab -
```

## 📈 パフォーマンス最適化

### nginx 最適化
既存の nginx.conf は本番環境用に最適化済みですが、追加設定：

```nginx
# /etc/nginx/nginx.conf に追加
worker_rlimit_nofile 65535;
worker_connections 4096;

# キャッシュ設定
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=cache:10m max_size=1g inactive=60m;
```

### データベース最適化
```sql
-- PostgreSQL 設定調整
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

SELECT pg_reload_conf();
```

### Redis 最適化
```bash
# Redis 設定追加
echo "
tcp-keepalive 300
timeout 0
maxclients 10000
" >> monitoring/redis.conf
```

## 🔄 バックアップ・復元手順

### 自動バックアップ設定
```bash
# バックアップスクリプト作成
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# データベースバックアップ
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U mfg_user mfg_drone_db > "$BACKUP_DIR/database.sql"

# ボリュームバックアップ
for volume in postgres_data redis_data grafana_data prometheus_data; do
  docker run --rm -v "mfg-drone_${volume}:/source" -v "$(pwd)/$BACKUP_DIR:/backup" \
    alpine tar czf "/backup/${volume}.tar.gz" -C /source .
done

# 設定ファイルバックアップ
cp -r monitoring "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/"

# 古いバックアップ削除（7日以上前）
find ./backups -type d -name "backup_*" -mtime +7 -exec rm -rf {} \;
EOF

chmod +x scripts/backup.sh

# 日次バックアップ設定
echo "0 2 * * * $(pwd)/scripts/backup.sh" | crontab -
```

### 災害復旧手順
```bash
# 1. サービス停止
docker-compose -f docker-compose.prod.yml down

# 2. ボリューム復元
BACKUP_PATH="./backups/backup_YYYYMMDD_HHMMSS"
for volume in postgres_data redis_data grafana_data prometheus_data; do
  docker volume rm "mfg-drone_${volume}" 2>/dev/null || true
  docker volume create "mfg-drone_${volume}"
  docker run --rm -v "mfg-drone_${volume}:/target" -v "$(pwd)/$BACKUP_PATH:/backup" \
    alpine tar xzf "/backup/${volume}.tar.gz" -C /target
done

# 3. サービス再起動
docker-compose -f docker-compose.prod.yml up -d

# 4. データベース復元
cat "$BACKUP_PATH/database.sql" | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U mfg_user -d mfg_drone_db
```

## 🔍 トラブルシューティング

### 一般的な問題と解決方法

#### 1. サービスが起動しない
```bash
# ログ確認
docker-compose -f docker-compose.prod.yml logs [service-name]

# コンテナ状態確認
docker-compose -f docker-compose.prod.yml ps

# リソース使用量確認
docker stats
```

#### 2. フロントエンドにアクセスできない
```bash
# nginx ログ確認
docker-compose -f docker-compose.prod.yml logs frontend

# ポート確認
netstat -tlnp | grep :80

# nginx 設定テスト
docker-compose -f docker-compose.prod.yml exec frontend nginx -t
```

#### 3. データベース接続エラー
```bash
# PostgreSQL ログ確認
docker-compose -f docker-compose.prod.yml logs postgres

# 接続テスト
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U mfg_user -d mfg_drone_db -c "SELECT 1;"

# 権限確認
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U mfg_user -d mfg_drone_db -c "\du"
```

#### 4. メモリ不足エラー
```bash
# メモリ使用量確認
free -h
docker stats --no-stream

# スワップ設定
sudo swapon --show
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### ログ分析

#### 主要ログファイル
```bash
# アプリケーションログ
docker-compose -f docker-compose.prod.yml logs --tail=100 frontend
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# システムログ
journalctl -u docker --tail=100

# nginx アクセスログ
docker-compose -f docker-compose.prod.yml exec frontend tail -f /var/log/nginx/access.log
```

#### ログ分析ツール
```bash
# エラー率分析
docker-compose -f docker-compose.prod.yml exec frontend \
  awk '$9 >= 400 {errors++} END {print "Error rate:", errors/NR*100"%"}' /var/log/nginx/access.log

# レスポンス時間分析
docker-compose -f docker-compose.prod.yml exec frontend \
  awk '{sum+=$10; count++} END {print "Average response time:", sum/count"ms"}' /var/log/nginx/access.log
```

## 📱 スケーリング

### 水平スケーリング
```yaml
# docker-compose.prod.yml でサービス複製
  frontend:
    deploy:
      replicas: 3
    
  backend:
    deploy:
      replicas: 2
```

### ロードバランサー設定
```nginx
# nginx upstream 設定
upstream backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}

upstream frontend {
    server frontend_1:80;
    server frontend_2:80;
    server frontend_3:80;
}
```

## 📞 サポート・問い合わせ

### ヘルプリソース
- **GitHub Issues**: [リポジトリのIssues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- **ドキュメント**: `/docs` ディレクトリ内の関連文書
- **ログファイル**: `./logs/` ディレクトリ

### 問題報告時の情報
問題を報告する際は、以下の情報を含めてください：

1. **環境情報**:
   ```bash
   # システム情報収集
   uname -a
   docker --version
   docker-compose version
   df -h
   free -h
   ```

2. **サービス状態**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml logs --tail=50
   ```

3. **設定ファイル**: 機密情報を除いた設定ファイル内容

---

**このガイドが MFGドローンシステムの安全で効率的なデプロイメントに役立つことを願っています。**

最終更新: 2025-07-04  
バージョン: 1.0.0