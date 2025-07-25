# MFG Drone Backend API Server - ユーザガイド

本ガイドでは、MFG Drone Backend API Serverのインストールから動作確認まで、Tello EDU実機の有無に応じた詳細な手順を説明します。

## 📋 目次

1. [事前準備・システム要件](#1-事前準備システム要件)
2. [インストール手順](#2-インストール手順)
3. [起動手順](#3-起動手順)
4. [動作確認](#4-動作確認)
5. [テスト実行手順](#5-テスト実行手順)
6. [停止手順](#6-停止手順)
7. [アンインストール手順](#7-アンインストール手順)
8. [トラブルシューティング](#8-トラブルシューティング)

---

## 1. 事前準備・システム要件

### 1.1 システム要件

- **OS**: Linux, macOS, Windows 10/11
- **Python**: 3.8以上（推奨: 3.11）
- **メモリ**: 最低4GB（推奨: 8GB以上）
- **ストレージ**: 最低2GB（データセット用に追加容量）
- **ネットワーク**: WiFi対応（Tello EDU実機使用時）

### 1.2 Tello EDU 実機を使用する場合の追加要件

- **Tello EDU**: DJI Tello EDU ドローン
- **ファームウェア**: v02.05.01.17以上（SDK 3.0対応）
- **WiFi環境**: 2.4GHz WiFi対応デバイス

---

## 2. インストール手順

### 2.1 リポジトリのクローン

```bash
# リポジトリをクローン
git clone <repository-url>
cd mfg_drone_by_claudecode/backend
```

### 2.2 Python仮想環境の作成（推奨）

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境の有効化
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2.3 依存関係のインストール

```bash
# 依存関係インストール
pip install -r requirements.txt

# インストール確認
python test_imports.py
```

**成功時の出力例:**
```
✓ All imports successful! System is ready.
```

---

## 3. 起動手順

### 3.1 【実機なし】シミュレーションモードでの起動

現在のバックエンドは主にシミュレーションベースで動作します。実機なしでも全機能をテストできます。

#### 3.1.1 基本起動

```bash
# APIサーバー起動
python start_api_server.py
```

#### 3.1.2 Docker起動（推奨）

```bash
# 開発環境での起動
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# ログ確認
docker-compose logs -f mfg-drone-api
```

#### 3.1.3 環境変数設定（オプション）

```bash
# 基本設定
export HOST=0.0.0.0
export PORT=8000
export LOG_LEVEL=INFO

# シミュレーション設定
export MFG_DATASETS_ROOT=/app/data/datasets
export MFG_MODELS_ROOT=/app/data/models

# ドローン動作モード設定
export DRONE_MODE=simulation        # simulation, auto, real
export TELLO_AUTO_DETECT=false      # シミュレーション時は自動検出無効

# セキュリティ設定
export MFG_DRONE_ADMIN_KEY=mfg-drone-admin-key-2024
export MFG_DRONE_READONLY_KEY=mfg-drone-readonly-2024

# パフォーマンス・監視設定（オプション）
export NETWORK_SCAN_INTERVAL=60     # 自動スキャン間隔(秒)  
export MAX_WORKER_THREADS=10        # 最大ワーカースレッド数
export CACHE_TTL=30                 # キャッシュ有効期限(秒)

# サーバー起動
python start_api_server.py
```

### 3.2 【実機あり】Tello EDU実機との接続（Phase 6対応）

> **Phase 6実装完了**: Tello EDU実機との完全統合が実装されました。ハイブリッドモード（実機・シミュレーション）をサポートします。

#### 3.2.1 Tello EDU の準備

1. **電源投入と基本確認**
   ```bash
   # 1. Tello EDUの電源ボタンを押して起動
   # 2. LEDが点滅から点灯に変わるまで待機（約30秒）
   # 3. バッテリー残量が20%以上であることを確認
   ```

2. **WiFi接続の確認**
   ```bash
   # 利用可能なWiFiネットワークを確認
   # Windows:
   netsh wlan show profiles
   
   # Linux/macOS:
   iwlist scan | grep TELLO
   ```

3. **Tello WiFiに接続**
   - WiFi設定から「TELLO-XXXXXX」を選択
   - パスワードなしで接続

#### 3.2.2 実機自動検出とIPアドレス確認

```bash
# 1. 自動検出用環境変数（オプション）
export DRONE_MODE=auto              # auto, simulation, real
export TELLO_AUTO_DETECT=true       # 自動検出有効
export TELLO_CONNECTION_TIMEOUT=10  # 接続タイムアウト(秒)
export NETWORK_SCAN_INTERVAL=60     # 自動スキャン間隔(秒)

# セキュリティ・API設定
export MFG_DRONE_ADMIN_KEY=mfg-drone-admin-key-2024
export MFG_DRONE_READONLY_KEY=mfg-drone-readonly-2024

# ログ・監視設定
export LOG_LEVEL=INFO               # ログレベル（DEBUG, INFO, WARNING, ERROR）

# 2. 手動IPアドレス確認
ping 192.168.10.1  # Tello EDU標準IP

# 3. 複数Tello EDUの検出テスト
nmap -sn 192.168.10.0/24 | grep -B2 "Nmap scan report"
```

#### 3.2.3 実機対応設定ファイル

Tello EDU実機用の設定ファイルを編集：

```yaml
# config/drone_config.yaml
global:
  default_mode: "auto"  # 実機優先、フォールバック有効
  space_bounds: [20.0, 20.0, 10.0]  # シミュレーション空間境界 (幅, 奥行き, 高さ)
  auto_detection:
    enabled: true
    timeout: 5.0
    scan_interval: 30.0  # 再スキャン間隔（秒）
  fallback:
    enabled: true
    simulation_on_failure: true

drones:
  # 自動検出モード（推奨）
  - id: "drone_001"
    name: "Tello EDU #1"
    mode: "auto"
    ip_address: null     # 自動検出
    auto_detect: true
    initial_position: [0.0, 0.0, 0.0]
    fallback_to_simulation: true
    settings:
      max_altitude: 3.0  # 最大高度（メートル）
      speed_limit: 2.0   # 最大速度（m/s）
      battery_warning: 20  # バッテリー警告レベル（%）
    
  # 手動IP指定モード
  - id: "drone_002"
    name: "Tello EDU #2"
    mode: "auto"
    ip_address: "192.168.10.1"
    auto_detect: false
    initial_position: [2.0, 2.0, 0.0]
    fallback_to_simulation: true
    settings:
      max_altitude: 3.0
      speed_limit: 2.0
      battery_warning: 20
  
  # シミュレーション専用ドローン
  - id: "drone_003"
    name: "Simulator #1"
    mode: "simulation"
    ip_address: null
    auto_detect: false
    initial_position: [-2.0, 2.0, 0.0]
    fallback_to_simulation: false
    settings:
      max_altitude: 10.0  # シミュレーションでは高度制限緩和
      speed_limit: 5.0
      battery_warning: 10

network:
  discovery:
    default_ips:
      - "192.168.10.1"  # Tello EDU標準IP
      - "192.168.1.1"   # 一般的なIP
      - "192.168.4.1"
    scan_ranges:
      - "192.168.1.0/24"
      - "192.168.10.0/24"
      - "192.168.4.0/24"
    connection_timeout: 3.0
    retry_attempts: 3
    retry_delay: 1.0
  
  # セキュリティ設定
  security:
    allowed_ip_ranges:
      - "192.168.0.0/16"
      - "10.0.0.0/8"
    max_concurrent_connections: 5
    connection_rate_limit: 10  # 秒あたり

# 監視・ログ設定
monitoring:
  # 状態更新間隔
  update_intervals:
    real_drone_state: 0.1      # 実機状態更新間隔（秒）
    simulation_state: 0.01     # シミュレーション更新間隔（秒）
    health_check: 5.0          # ヘルスチェック間隔（秒）
  
  # アラート設定
  alerts:
    battery_low: 15            # 低バッテリーアラート（%）
    connection_lost: true      # 接続切断アラート
    collision_detected: true   # 衝突検出アラート
  
  # ログ設定
  logging:
    level: "INFO"
    real_drone_events: true
    simulation_events: false
    network_events: true

# パフォーマンス設定
performance:
  # スレッド・処理設定
  threading:
    max_worker_threads: 10
    state_update_workers: 2
    network_scan_workers: 2
  
  # キャッシュ設定
  cache:
    drone_state_ttl: 1.0       # ドローン状態キャッシュ有効期限（秒）
    network_scan_ttl: 30.0     # ネットワークスキャン結果キャッシュ（秒）
  
  # リソース制限
  limits:
    max_flight_time: 900       # 最大飛行時間（秒）
    max_simultaneous_drones: 5 # 同時制御可能ドローン数
```

#### 3.2.4 実機対応バックエンド起動

```bash
# 1. 環境変数設定（オプション）
export DRONE_MODE=auto              # 自動モード（実機優先）
export TELLO_AUTO_DETECT=true       # 自動検出有効
export TELLO_CONNECTION_TIMEOUT=10  # 接続タイムアウト
export NETWORK_SCAN_INTERVAL=60     # 自動スキャン間隔(秒)

# セキュリティ・API設定
export MFG_DRONE_ADMIN_KEY=mfg-drone-admin-key-2024
export MFG_DRONE_READONLY_KEY=mfg-drone-readonly-2024

# ログ・監視設定
export LOG_LEVEL=INFO               # ログレベル（DEBUG, INFO, WARNING, ERROR）

# 2. APIサーバー起動
python start_api_server.py

# 3. 起動ログの確認
# 以下のようなログが表示されることを確認:
# INFO: DroneManager initialized with Phase 6 integration
# INFO: NetworkService initialized
# INFO: Real drone detected: 192.168.10.1
# INFO: Drone initialized from config: drone_001 (auto)
```

#### 3.2.5 実機接続確認

```bash
# 1. 実機ドローン検出API
curl -X GET "http://localhost:8000/api/drones/detect?timeout=10"

# 期待する出力:
# [
#   {
#     "ip_address": "192.168.10.1",
#     "battery_level": 85,
#     "signal_strength": 90,
#     "is_available": true,
#     "detection_method": "tello_command"
#   }
# ]

# 2. ドローン一覧（実機・シミュレーション混在）
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones

# 3. ドローンタイプ情報確認
curl -X GET "http://localhost:8000/api/drones/drone_001/type-info"

# 期待する出力:
# {
#   "drone_id": "drone_001",
#   "is_real_drone": true,
#   "drone_class": "real",
#   "real_ip_address": "192.168.10.1",
#   "connection_state": "connected"
# }
```

#### 3.2.6 実機ドローン操作テスト

```bash
# 1. 実機ドローンに接続
curl -X POST -H "X-API-Key: mfg-drone-admin-key-2024" \
     "http://localhost:8000/api/drones/drone_001/connect"

# 2. 実機状態確認
curl -X GET -H "X-API-Key: mfg-drone-admin-key-2024" \
     "http://localhost:8000/api/drones/drone_001/status"

# 3. 離陸テスト（注意: 安全な場所で実行）
curl -X POST -H "X-API-Key: mfg-drone-admin-key-2024" \
     "http://localhost:8000/api/drones/drone_001/takeoff"

# 4. 着陸
curl -X POST -H "X-API-Key: mfg-drone-admin-key-2024" \
     "http://localhost:8000/api/drones/drone_001/land"

# 5. 切断
curl -X POST -H "X-API-Key: mfg-drone-admin-key-2024" \
     "http://localhost:8000/api/drones/drone_001/disconnect"
```

#### 3.2.7 自動スキャン機能

```bash
# 1. 自動スキャン開始（60秒間隔）
curl -X POST "http://localhost:8000/api/system/auto-scan/start?interval_seconds=60"

# 2. ネットワーク状態確認
curl -X GET "http://localhost:8000/api/system/network-status"

# 3. 自動スキャン停止
curl -X POST "http://localhost:8000/api/system/auto-scan/stop"
```

#### 3.2.8 トラブルシューティング

**実機が検出されない場合:**

```bash
# 1. 基本的な接続確認
ping 192.168.10.1

# 2. 手動接続検証
curl -X POST -H "Content-Type: application/json" \
     -d '{"ip_address": "192.168.10.1"}' \
     "http://localhost:8000/api/drones/verify-connection"

# 3. ログ確認
tail -f /var/log/drone_api.log | grep -E "(real_drone|network|tello)"

# 4. 設定確認
curl -X GET "http://localhost:8000/api/system/network-status"
```

**一般的な問題と解決方法:**

1. **WiFi接続問題**
   - Tello EDUの電源を再投入
   - 他のWiFiネットワークから切断
   - WiFiアダプターのリセット

2. **IP検出問題**
   - スキャン範囲の設定確認
   - ファイアウォールの無効化（一時的）
   - 手動IP指定への切り替え

3. **バッテリー不足**
   - 20%以上の充電確認
   - 充電後の再起動

---

## 4. 動作確認

### 4.1 疎通テスト

#### 4.1.1 【実機なし】シミュレーションモードでのテスト

```bash
# 1. ヘルスチェック
curl http://localhost:8000/health

# 期待する出力:
# {"status":"healthy","timestamp":"2024-XX-XX...","services":{"drone_manager":true,...}}

# 2. API ドキュメント確認
curl http://localhost:8000/docs
# ブラウザで http://localhost:8000/docs にアクセス

# 3. ドローン一覧取得
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones

# 期待する出力:
# [{"id":"drone_001","name":"Tello EDU #1","type":"dummy","status":"disconnected",...}]

# 4. ドローン接続テスト
curl -X POST \
     -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/drone_001/connect

# 期待する出力:
# {"success":true,"message":"ドローン drone_001 に正常に接続しました","timestamp":"..."}

# 5. ドローン状態確認
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/drone_001/status

# 6. 離陸テスト
curl -X POST \
     -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/drone_001/takeoff

# 7. 着陸テスト
curl -X POST \
     -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/drone_001/land
```

#### 4.1.2 【実機あり】実機接続テスト（将来対応）

```bash
# 実機接続確認（将来実装）
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/tello_real_001/connect

# 実機状態監視
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/tello_real_001/status
```

### 4.2 ログ確認

#### 4.2.1 ログファイルの場所

```bash
# 標準起動時のログ
# コンソール出力のみ（--log-level INFO）

# Docker起動時のログ
docker-compose logs mfg-drone-api

# ログファイル保存場所（カスタム設定時）
ls -la /app/data/logs/
# または
ls -la ./logs/
```

#### 4.2.2 ログ内容の確認方法

```bash
# 1. リアルタイムログ監視
# Docker使用時:
docker-compose logs -f mfg-drone-api

# 標準起動時:
tail -f nohup.out  # バックグラウンド起動時

# 2. エラーログの抽出
docker-compose logs mfg-drone-api | grep ERROR

# 3. 特定期間のログ確認
docker-compose logs --since="1h" mfg-drone-api
```

#### 4.2.3 ログのクリア方法

```bash
# 1. Dockerログのクリア
docker-compose down
docker system prune -f
docker-compose up -d

# 2. ログファイルのクリア（カスタム設定時）
rm -f /app/data/logs/*.log
sudo journalctl --vacuum-time=1d  # systemdログ
```

---

## 5. テスト実行手順

### 5.1 単体テスト

```bash
# 1. 全単体テスト実行
pytest tests/ -m unit -v

# 2. 特定モジュールのテスト
pytest tests/test_drone_simulator.py -v
pytest tests/test_virtual_camera.py -v
pytest tests/test_vision_service.py -v

# 3. カバレッジ付きテスト
pytest tests/ -m unit --cov=src --cov-report=html
```

### 5.2 結合テスト

#### 5.2.1 【実機なし】シミュレーションモード

```bash
# 1. Phase2-Phase3統合テスト
pytest tests/test_integration_phase2_phase3.py -v

# 2. 設定統合テスト
pytest tests/test_configuration_integration.py -v

# 3. フルワークフロー統合テスト
pytest tests/test_full_workflow_integration.py -v

# 4. API統合テスト
pytest tests/test_api_basic.py -v
pytest tests/test_websocket_api.py -v

# 5. 全統合テスト実行
pytest tests/ -m integration -v
```

#### 5.2.2 【実機あり】実機連携テスト（将来対応）

```bash
# 実機テスト（将来実装）
export TELLO_REAL_MODE=true
pytest tests/test_real_drone_integration.py -v --tb=short
```

### 5.3 包括的テスト実行

```bash
# 1. テストランナー使用
python run_tests.py --category all

# 2. 段階的テスト実行
python run_tests.py --category unit
python run_tests.py --category integration
python run_tests.py --category edge_cases

# 3. パフォーマンステスト
pytest tests/ -m performance -v

# 4. 全テスト（時間がかかります）
pytest tests/ -v --cov=src --cov-report=html --html=test_report.html
```

---

## 6. 停止手順

### 6.1 【実機なし】シミュレーションモード停止

#### 6.1.1 標準起動時の停止

```bash
# 1. プロセス確認
ps aux | grep python | grep api_server

# 2. 安全な停止（Ctrl+C または）
pkill -f "api_server.main"

# 3. 強制停止（必要時のみ）
pkill -9 -f "api_server.main"
```

#### 6.1.2 Docker起動時の停止

```bash
# 1. 安全な停止
docker-compose down

# 2. ボリューム付き停止（データ削除注意）
docker-compose down -v

# 3. 強制停止
docker-compose kill
docker-compose down
```

### 6.2 【実機あり】実機接続時の安全停止（将来対応）

#### 6.2.1 Tello EDU の安全着陸

```bash
# 1. 飛行中の場合、緊急着陸実行
curl -X POST \
     -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/tello_real_001/land

# 2. ドローン状態確認（着陸完了まで待機）
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/tello_real_001/status

# 状態が "landed" になることを確認

# 3. ドローン切断
curl -X POST \
     -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/api/drones/tello_real_001/disconnect
```

#### 6.2.2 バックエンドサーバーの停止

```bash
# 上記「実機なし」と同じ手順でサーバー停止
docker-compose down
```

#### 6.2.3 Tello EDU の電源停止

```bash
# 1. WiFi接続切断
# デバイスのWiFi設定から通常のWiFiに再接続

# 2. Tello EDU電源オフ
# 電源ボタンを5秒間長押しして電源オフ
# LEDが消灯することを確認
```

---

## 7. アンインストール手順

停止手順完了後、以下の手順でアンインストールを実行してください。

### 7.1 Dockerリソースの削除

```bash
# 1. コンテナとイメージ削除
docker-compose down -v --rmi all

# 2. 関連ボリューム削除
docker volume ls | grep mfg-drone | awk '{print $2}' | xargs docker volume rm

# 3. 不要なDockerリソース削除
docker system prune -af
```

### 7.2 Python環境のクリーンアップ

```bash
# 1. 仮想環境の削除（仮想環境使用時）
deactivate
rm -rf venv/

# 2. キャッシュ削除
rm -rf __pycache__/
find . -name "*.pyc" -delete
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -f .coverage
```

### 7.3 データとログの削除

```bash
# 1. データディレクトリ削除（注意：データが失われます）
rm -rf data/
rm -rf logs/
rm -rf dev_data/

# 2. 一時ファイル削除
rm -f *.log
rm -f test_report.html
rm -f nohup.out
```

### 7.4 設定ファイルのバックアップ（オプション）

```bash
# 重要な設定ファイルをバックアップ
mkdir -p ~/mfg_drone_backup
cp docker-compose.yml ~/mfg_drone_backup/
cp .env ~/mfg_drone_backup/ 2>/dev/null || true
```

### 7.5 完全削除

```bash
# リポジトリディレクトリ削除
cd ..
rm -rf mfg_drone_by_claudecode/
```

---

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法

#### 8.1.1 起動時のエラー

**問題**: `ModuleNotFoundError`
```bash
# 解決方法:
pip install -r requirements.txt
python test_imports.py
```

**問題**: ポート8000が使用中
```bash
# 解決方法:
netstat -tlnp | grep :8000
export PORT=8001  # 別ポート使用
```

#### 8.1.2 Docker関連の問題

**問題**: Docker起動失敗
```bash
# 解決方法:
docker-compose down
docker system prune -f
docker-compose up -d --force-recreate
```

**問題**: メモリ不足
```bash
# 解決方法: docker-compose.yml の resources 設定を調整
# memory: 2G に変更
```

#### 8.1.3 API接続エラー

**問題**: 401 Unauthorized
```bash
# 解決方法: API Keyが正しいか確認
curl -H "X-API-Key: mfg-drone-admin-key-2024" \
     http://localhost:8000/health
```

**問題**: 429 Too Many Requests
```bash
# 解決方法: レート制限を緩和または無効化
export RATE_LIMIT_ENABLED=false
```

### 8.2 ログレベルの変更

```bash
# デバッグモードで起動
export LOG_LEVEL=DEBUG
python start_api_server.py

# Dockerでのデバッグ
docker-compose -f docker-compose.dev.yml up -d
```

### 8.3 サポート情報

- **ドキュメント**: `/docs/` フォルダ内の各種READMEファイル
- **API仕様**: http://localhost:8000/docs
- **ログ分析**: Docker使用時は `docker-compose logs` コマンド

---

## 📝 補足事項

### Tello EDU 実機接続について

現在のバージョン（Phase 5）では、実機接続機能は将来の拡張として設計されています：

- **現在**: 高度なシミュレーション環境での開発・テスト
- **将来**: djitellopy互換インターフェースによる実機統合

### パフォーマンス最適化

- **メモリ使用量**: 基本動作 ~50MB、学習時 +200-500MB
- **CPU使用率**: 通常 10-20%、学習時 70-90%
- **レスポンス時間**: API <0.1秒、WebSocket接続 <5秒

### セキュリティ考慮事項

- 本番環境では、デフォルトのAPI Keyを変更してください
- HTTPS使用を推奨します（Nginx設定）
- ファイアウォール設定でポート8000へのアクセスを制限してください

---

**🎯 これで MFG Drone Backend API Server の環境構築と基本操作が完了しました！**

追加の機能や詳細な設定については、各フェーズのREADMEファイルを参照してください。