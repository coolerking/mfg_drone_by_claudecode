# 統合監視・運用システム（Phase F対応）

**Node.js MCP Server中心**のMFG Drone システム統合監視・運用プラットフォーム

## 概要（Description）

Phase F統合版のMFG Drone Monitoring Systemは、Node.js版MCPサーバーを中心とした統一監視・運用体制を提供します。従来の分散した監視設定を統合し、Prometheus + Grafana + 統一ログ管理により、効率的な運用を実現します。実機制御とシミュレーション環境の両方に対応し、リアルタイム監視とインテリジェントアラートにより、システムの安定稼働を支援します。

## 🚀 Phase F 新機能・改善点

### Node.js中心運用体制
- **Node.js MCP Server最優先監視**: 10秒間隔の高頻度監視
- **統一設定ファイル**: 分散していた設定を一元化
- **智的アラート**: 優先度ベースの段階的通知
- **レガシーPython版**: 保守モードでの継続サポート

### 統合ログ管理
- **Winston（Node.js）+ Structlog（Python）**: 統一ログ形式
- **自動ローテーション**: サイズ・期間ベースの管理
- **セキュリティフィルタリング**: 機密情報の自動マスキング
- **パフォーマンス最適化**: 非同期ログ出力

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## 📦 インストール方法（Installation）

### 統一デプロイスクリプトを使用（推奨）

```bash
# プロジェクトルートディレクトリで実行
cd mfg_drone_by_claudecode

# フル統合デプロイ（Node.js MCP Server + 全サービス）
./scripts/unified_deploy.sh deploy -e production

# Node.js MCP Server のみデプロイ（軽量）
./scripts/unified_deploy.sh nodejs-only -e production

# デプロイ状態確認
./scripts/unified_deploy.sh status

# ログ確認（Node.js MCP Server）
./scripts/unified_deploy.sh logs mcp-server-nodejs
```

### Docker Compose手動セットアップ

```bash
# 統一監視設定の適用
cp monitoring/unified_prometheus.yml monitoring/prometheus.yml
cp monitoring/unified_alerts.yml monitoring/alerts.yml

# 環境設定ファイルの準備
cp .env.production.example .env.production
# 必要な環境変数を設定

# 統合監視スタックの起動
docker-compose -f docker-compose.prod.yml up -d

# Node.js MCP Server の優先起動確認
docker-compose -f docker-compose.prod.yml logs -f mcp-server-nodejs
```

### 手動セットアップ（ローカル環境）

```bash
# Prometheusのダウンロードと設定
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xzf prometheus-2.40.0.linux-amd64.tar.gz
cd prometheus-2.40.0.linux-amd64

# 設定ファイルのコピー
cp /path/to/mfg_drone_by_claudecode/monitoring/prometheus.yml ./prometheus.yml
cp /path/to/mfg_drone_by_claudecode/monitoring/alerts.yml ./alerts.yml

# Prometheus起動
./prometheus --config.file=prometheus.yml
```

### Grafanaダッシュボード設定

```bash
# Grafana起動後、ブラウザでアクセス
# http://localhost:3000 (admin/admin)

# データソース追加
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'
```

## 🛠️ 使い方（Usage）

### Node.js MCP Server中心の監視操作

```bash
# Node.js MCP Server ヘルスチェック（最重要）
curl http://localhost:3001/health

# Node.js MCP Server メトリクス取得
curl http://localhost:3001/metrics

# 統一Prometheusメトリクス確認
curl http://localhost:9090/api/v1/targets

# Node.js MCP Server特化クエリ
curl 'http://localhost:9090/api/v1/query?query=up{job="mcp-server-nodejs"}'

# 統合アラート状態確認（優先度別）
curl 'http://localhost:9090/api/v1/alerts?filter={priority="p1"}'

# システム全体ステータス
curl http://localhost:8000/api/system/status
```

### 統一ログ管理操作

```bash
# Node.js MCP Server ログ（リアルタイム）
tail -f logs/mcp-nodejs/combined.log

# エラーログのみ表示
tail -f logs/mcp-nodejs/error.log

# パフォーマンスログ分析
jq '.duration' logs/mcp-nodejs/performance.log | sort -n

# 全サービス統合ログ検索
grep -r "ERROR" logs/ --include="*.log" | tail -20

# セキュリティログ確認
tail -f logs/security/security.log
```

### アラート設定の変更

```yaml
# alerts.yml の編集例：新しいアラートルール追加
- name: custom_alerts
  rules:
    - alert: CustomDroneAlert
      expr: drone_altitude_meters > 100
      for: 2m
      labels:
        severity: warning
        category: application
      annotations:
        summary: "ドローン高度制限超過"
        description: "ドローン {{ $labels.drone_id }} が高度制限を超えています ({{ $value }}m)"
```

### 設定の再読み込み

```bash
# Prometheus設定の再読み込み（ダウンタイムなし）
curl -X POST http://localhost:9090/-/reload

# Docker環境での設定再読み込み
docker-compose restart prometheus
```

### Grafanaダッシュボード活用

1. **システム概要ダッシュボード**: http://localhost:3000/d/system-overview
2. **ドローン監視ダッシュボード**: http://localhost:3000/d/drone-monitoring
3. **インフラ監視ダッシュボード**: http://localhost:3000/d/infrastructure
4. **セキュリティ監視ダッシュボード**: http://localhost:3000/d/security

### アラート通知設定

```yaml
# alertmanager.yml 設定例
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@mfgdrone.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@mfgdrone.com'
    subject: 'MFG Drone Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      アラート: {{ .Annotations.summary }}
      詳細: {{ .Annotations.description }}
      {{ end }}
```

## 動作環境・要件（Requirements）

### システム要件

- **OS**: Linux, macOS, Windows (Docker対応)
- **CPU**: 2コア以上推奨
- **メモリ**: 4GB以上推奨（Grafana + Prometheus）
- **ストレージ**: 10GB以上（メトリクス保存用）
- **ネットワーク**: インターネット接続（初期セットアップ時）

### 必須コンポーネント

- **Prometheus**: 2.40.0+ (メトリクス収集・保存)
- **Grafana**: 9.0.0+ (可視化・ダッシュボード)
- **AlertManager**: 0.25.0+ (アラート管理・通知)
- **Node Exporter**: 1.5.0+ (システムメトリクス)
- **cAdvisor**: 0.46.0+ (コンテナメトリクス)

### オプション依存関係

- **PostgreSQL Exporter**: 0.11.0+ (データベース監視)
- **Redis Exporter**: 1.45.0+ (Redis監視)
- **Blackbox Exporter**: 0.22.0+ (エンドポイント監視)
- **Docker**: 20.10+ (コンテナ環境)
- **Docker Compose**: 2.0+ (オーケストレーション)

### ネットワーク要件

- **Prometheusポート**: 9090 (メトリクス・UI)
- **Grafanaポート**: 3000 (ダッシュボードUI)
- **AlertManagerポート**: 9093 (アラート管理)
- **Node Exporterポート**: 9100 (システムメトリクス)
- **ファイアウォール**: 上記ポートの許可設定

## 📁 ディレクトリ構成（Directory Structure）

```
monitoring/
├── README.md                   # 統合監視システムドキュメント
├── unified_prometheus.yml      # 🆕 統一Prometheus設定（Node.js中心）
├── unified_alerts.yml          # 🆕 統一アラート設定（優先度ベース）
├── unified_logging_config.yml  # 🆕 統一ログ管理設定
├── prometheus.yml              # 運用時設定（unified_prometheus.ymlからコピー）
├── alerts.yml                  # 運用時アラート（unified_alerts.ymlからコピー）
├── grafana/                    # Grafana設定
│   ├── dashboards/            # ダッシュボード定義
│   │   ├── mcp-nodejs-overview.json      # 🆕 Node.js MCP専用
│   │   ├── system-overview.json
│   │   ├── drone-monitoring.json
│   │   ├── infrastructure.json
│   │   └── security.json
│   └── provisioning/          # 自動プロビジョニング
│       ├── datasources/
│       └── dashboards/
├── alertmanager/              # AlertManager設定
│   └── alertmanager.yml
└── logs/                      # 🆕 統一ログディレクトリ
    ├── mcp-nodejs/           # Node.js MCP Server ログ（最優先）
    │   ├── combined.log
    │   ├── error.log
    │   ├── access.log
    │   └── performance.log
    ├── backend/              # Backend API ログ
    ├── frontend/             # Frontend ログ
    ├── mcp-python/           # Python MCP ログ（レガシー）
    ├── access/               # アクセスログ
    ├── error/                # エラーログ
    ├── security/             # セキュリティログ
    ├── performance/          # パフォーマンスログ
    └── audit/                # 監査ログ

scripts/
├── unified_deploy.sh          # 🆕 統一デプロイスクリプト（Node.js中心）
└── deploy.sh                 # 従来のデプロイスクリプト
```

### 🎯 統合監視対象（優先度順）

#### 🚨 P1: Node.js MCP Server（最重要・10秒間隔）
- **サービス死活**: 30秒ダウンで即座アラート
- **レスポンス時間**: 2秒超過時アラート（95パーセンタイル）
- **エラー率**: 5%超過時アラート
- **メモリ使用量**: 400MB超過時アラート
- **CPU使用率**: 80%超過時アラート
- **WebSocket接続**: リアルタイム監視

#### 🚨 P1: システム基盤（1分間隔）
- **CPU使用率**: 85%超過時アラート（従来より厳格化）
- **メモリ使用率**: 90%超過時アラート
- **ディスク使用率**: 90%超過時アラート
- **PostgreSQL**: 接続数80%・レプリケーション遅延30秒
- **Redis**: メモリ85%・接続拒否検出

#### 🟡 P2: Backend API・Frontend（30秒間隔）
- **Backend API**: 1分ダウン・1秒レスポンス・3%エラー率
- **Frontend**: ヘルスチェック・静的リソース配信
- **エンドポイント監視**: Blackbox Exporter経由

#### 🟢 P3: アプリケーション固有（1分間隔）
- **ドローン接続状態**: 30秒接続喪失でアラート
- **ドローンバッテリー**: 15%以下時アラート（従来20%から強化）
- **カメラストリーム**: 2分停止時アラート
- **モデル学習**: 10分間に2回失敗でアラート

#### 🔒 セキュリティ監視（30秒間隔）
- **失敗ログイン**: 5分間に20回超過（従来10回から強化）
- **不正APIアクセス**: 5分間に50回超過（従来20回から調整）
- **セキュリティ違反**: 検出時即座アラート
- **SSL証明書**: 7日前期限切れ警告

#### 📊 監視システム自体（2分間隔）
- **Prometheus**: 設定リロード失敗・スクレイプ失敗率5%
- **Grafana**: ダッシュボード応答性
- **AlertManager**: 通知配信状態

## 📋 更新履歴（Changelog/History）

### 🆕 Phase F: 監視・運用設定の統合（最新）
- **Node.js MCP Server中心運用**: 最優先監視・10秒間隔スクレイプ
- **統一設定ファイル**: 分散していたPrometheus/Alert設定を一元化
- **統合ログ管理**: Winston(Node.js) + Structlog(Python)統一フォーマット
- **優先度ベースアラート**: P1/P2/P3段階的通知システム
- **統一デプロイスクリプト**: Node.js中心の自動化デプロイ
- **レガシーサポート**: Python MCP Server保守モード継続
- **智的監視**: サービス重要度に応じた監視頻度調整
- **セキュリティ強化**: 機密情報自動マスキング・改ざん防止

### Phase 6: 実機統合監視対応
- **ドローン固有メトリクス**: バッテリー、接続状態、高度監視
- **動的サービス検出**: ドローンデバイスの自動検出・監視
- **実機・シミュレーション**: 統合環境の監視対応
- **カメラストリーム**: 映像配信状態の監視
- **セキュリティ強化**: 不正アクセス・ファイルアップロード監視

### Phase 5: プロダクション監視
- **包括的インフラ監視**: CPU、メモリ、ディスク、ネットワーク
- **サービス品質監視**: レスポンス時間、エラー率、可用性
- **データベース監視**: PostgreSQL、Redis状態監視
- **コンテナ監視**: Docker環境のメトリクス収集
- **アラート体系**: 6カテゴリの段階的アラート設定

### Phase 4: 基本監視機能
- **Prometheus導入**: メトリクス収集・保存基盤
- **基本アラート**: システム異常検出
- **Grafana統合**: 可視化ダッシュボード
- **メトリクス標準化**: 統一されたメトリクス命名規則

### Phase 3: 監視基盤構築
- **監視要件定義**: 監視項目・閾値の策定
- **アーキテクチャ設計**: 監視システム構成設計
- **基本設定**: Prometheus・Grafana基本設定

---

**ライセンス**: MIT License - 詳細は[LICENSE](../LICENSE)ファイルを参照してください。

**関連ドキュメント**:
- [バックエンドAPI仕様](../backend/docs/real_drone_api_specification.md)
- [システム構成図](../docs/system_architecture.md)
- [トラブルシューティング](../backend/docs/troubleshooting_real_drone.md)