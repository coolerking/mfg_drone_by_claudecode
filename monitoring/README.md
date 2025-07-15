# システム監視・アラート設定

MFG Drone システムの包括的な監視とアラート管理を提供するPrometheus + Grafana統合監視システム

## 概要（Description）

MFG Drone Monitoring System は、Tello EDU ドローン制御システムの健全性とパフォーマンスを監視するためのPrometheusベースの監視システムです。インフラストラクチャ、アプリケーション、データベース、セキュリティを含む全コンポーネントの包括的な監視機能を提供し、リアルタイムアラートとメトリクス収集により、システムの安定稼働を支援します。

## 目次（Table of Contents）

- [概要（Description）](#概要description)
- [インストール方法（Installation）](#インストール方法installation)
- [使い方（Usage）](#使い方usage)
- [動作環境・要件（Requirements）](#動作環境要件requirements)
- [ディレクトリ構成（Directory Structure）](#ディレクトリ構成directory-structure)
- [更新履歴（Changelog/History）](#更新履歴changeloghistory)

## インストール方法（Installation）

### Docker Composeを使用したセットアップ

```bash
# プロジェクトルートディレクトリで実行
cd mfg_drone_by_claudecode

# 監視スタックの起動
docker-compose -f docker-compose.prod.yml up -d prometheus grafana alertmanager

# または個別起動
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/monitoring/alerts.yml:/etc/prometheus/alerts.yml \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
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

## 使い方（Usage）

### 基本的な監視操作

```bash
# Prometheusメトリクス確認
curl http://localhost:9090/api/v1/targets

# アラート状態確認
curl http://localhost:9090/api/v1/alerts

# 特定メトリクスの取得
curl 'http://localhost:9090/api/v1/query?query=up'

# ドローンバッテリー状態の確認
curl 'http://localhost:9090/api/v1/query?query=drone_battery_percentage'
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

## ディレクトリ構成（Directory Structure）

```
monitoring/
├── README.md                   # このファイル
├── prometheus.yml              # Prometheus設定ファイル
├── alerts.yml                  # アラートルール定義
├── grafana/                    # Grafana設定（追加時）
│   ├── dashboards/            # ダッシュボード定義
│   │   ├── system-overview.json
│   │   ├── drone-monitoring.json
│   │   ├── infrastructure.json
│   │   └── security.json
│   └── provisioning/          # 自動プロビジョニング
│       ├── datasources/
│       └── dashboards/
├── alertmanager/              # AlertManager設定（追加時）
│   └── alertmanager.yml
└── exporters/                 # 各種Exporter設定（追加時）
    ├── node-exporter.yml
    ├── postgres-exporter.yml
    └── redis-exporter.yml
```

### 現在の監視対象

#### インフラストラクチャ監視
- **CPU使用率**: 80%超過時アラート
- **メモリ使用率**: 85%超過時アラート
- **ディスク使用率**: 90%超過時アラート
- **ディスクI/O**: 20%超過時アラート

#### サービス監視
- **エンドポイント死活監視**: 1分間ダウン検出
- **レスポンス時間**: 500ms超過時アラート
- **エラー率**: 5%超過時アラート
- **API制限**: レート制限頻発時アラート

#### データベース監視
- **PostgreSQL接続数**: 80%超過時アラート
- **レプリケーション遅延**: 30秒超過時アラート
- **Redisメモリ使用量**: 90%超過時アラート
- **Redis接続エラー**: 接続拒否検出時アラート

#### アプリケーション監視
- **ドローン接続状態**: 接続喪失時即座アラート
- **ドローンバッテリー**: 20%以下時アラート
- **カメラストリーム**: ストリーム停止時アラート
- **モデル学習**: 学習失敗時アラート
- **WebSocket接続数**: 50接続超過時アラート

#### セキュリティ監視
- **ログイン失敗**: 5分間に10回超過時アラート
- **不正APIアクセス**: 5分間に20回超過時アラート
- **不審ファイルアップロード**: 検出時即座アラート

## 更新履歴（Changelog/History）

### Phase 6: 実機統合監視対応（最新）
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