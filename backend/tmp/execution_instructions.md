# 4 Phase Test Execution Instructions

## 概要
各フェーズの詳細実行手順、環境設定、コマンド例、チェックリスト

---

## Phase 1: Unit Tests (Development Environment)

### 環境準備

#### 1. 開発環境セットアップ
```bash
# 1. Python仮想環境作成
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 2. 依存関係インストール
cd backend
pip install -e .[dev]
pip install pytest pytest-cov pytest-asyncio

# 3. 環境変数設定
export ENVIRONMENT=development
export USE_REAL_DRONE=false
export TESTING_MODE=unit_tests
```

#### 2. テスト環境検証
```bash
# 開発環境確認
python -c "from config.test_config import TestConfig; print('Test config loaded')"

# Mock drone確認
python -c "from tests.stubs.drone_stub import TelloStub; print('Mock drone available')"
```

### 実行手順

#### Step 1: 既存テスト動作確認
```bash
# 現在のテストが正常動作することを確認
python -m pytest backend/tests/ -v --tb=short
```

#### Step 2: 単体テスト実行
```bash
# Phase 1 単体テスト実行
python -m pytest backend/tests/test_*_units.py -v

# カバレッジ付き実行
python -m pytest backend/tests/test_*_units.py --cov=backend --cov-report=html --cov-report=term

# 境界値テストのみ実行
python -m pytest backend/tests/test_*_units.py -k "boundary_values" -v

# エラーハンドリングテストのみ実行
python -m pytest backend/tests/test_*_units.py -k "error_handling" -v
```

#### Step 3: 結果検証
```bash
# テストレポート生成
python -m pytest backend/tests/test_*_units.py --html=reports/phase1_report.html --self-contained-html

# カバレッジレポート確認
open htmlcov/index.html  # Mac/Linux
# または
start htmlcov/index.html  # Windows
```

### 成功基準チェックリスト
- [ ] 全単体テスト100%合格
- [ ] コードカバレッジ95%以上
- [ ] 実行時間30秒以内
- [ ] 境界値テスト全パターン実装
- [ ] エラーハンドリング全パターン実装

---

## Phase 2: Integration Test A (Raspberry Pi + Mock Drone)

### 環境準備

#### 1. Raspberry Pi環境セットアップ
```bash
# Pi上での実行 (SSH接続後)
ssh pi@192.168.1.100

# システム更新
sudo apt update && sudo apt upgrade -y

# Python環境構築
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# プロジェクトダウンロード
git clone https://github.com/your-org/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/backend

# 仮想環境作成
python3.11 -m venv venv
source venv/bin/activate

# 依存関係インストール (Pi最適化版)
pip install -e .[dev]
pip install pytest-xdist pytest-timeout pytest-benchmark
```

#### 2. Pi固有設定
```bash
# Pi環境変数設定
export ENVIRONMENT=raspberry_pi
export USE_REAL_DRONE=false
export PI_OPTIMIZATION=true
export RESOURCE_LIMIT_MODE=true
export MAX_CONCURRENT_REQUESTS=10
export MEMORY_LIMIT_MB=6144
```

#### 3. Pi環境検証
```bash
# リソース状況確認
free -h
df -h
cat /proc/cpuinfo | grep "model name"

# ネットワーク確認
ping -c 4 8.8.8.8
iwconfig wlan0

# Python環境確認
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().total // (1024**3)}GB')"
```

### 実行手順

#### Step 1: Pi環境テスト
```bash
# Pi環境固有テスト実行
python -m pytest backend/tests/test_pi_environment_integration.py -v

# リソース監視付き実行
python -m pytest backend/tests/test_pi_environment_integration.py -v --resource-monitor
```

#### Step 2: OpenAPI完全テスト
```bash
# 全エンドポイントテスト
python -m pytest backend/tests/test_openapi_complete_integration.py -v

# 並列実行 (Pi性能に応じて調整)
python -m pytest backend/tests/test_openapi_complete_integration.py -v -n 4

# タイムアウト設定付き実行
python -m pytest backend/tests/test_openapi_complete_integration.py -v --timeout=300
```

#### Step 3: パフォーマンステスト
```bash
# Pi性能テスト
python -m pytest backend/tests/test_pi_performance_integration.py -v

# 長時間動作テスト
python -m pytest backend/tests/test_pi_performance_integration.py -v --timeout=3600

# メモリ・CPU監視付き実行
python -m pytest backend/tests/test_pi_performance_integration.py -v --profile
```

#### Step 4: 統合レポート生成
```bash
# 包括的レポート生成
python -m pytest backend/tests/test_*_integration.py --html=reports/phase2_pi_report.html --self-contained-html

# パフォーマンスレポート
python -m pytest backend/tests/ --benchmark-only --benchmark-html=reports/phase2_performance.html
```

### 成功基準チェックリスト
- [ ] 全OpenAPIエンドポイント100%動作
- [ ] Pi環境リソース制約内で安定動作
- [ ] 10並行リクエスト処理可能
- [ ] レスポンス時間95%が1秒以内
- [ ] メモリ使用量6GB以内
- [ ] 4時間連続動作確認

---

## Phase 3: Integration Test B (Raspberry Pi + Real Drone)

### 環境準備

#### 1. 安全環境セットアップ
```bash
# 物理環境準備チェックリスト
echo "=== 安全環境チェック ==="
echo "[ ] 屋内環境 (天井高3m以上)"
echo "[ ] 障害物なし (半径3m円内)"
echo "[ ] プロペラガード装着済み"
echo "[ ] 緊急停止手順確認済み"
echo "[ ] バッテリー80%以上充電済み"
echo "[ ] Tello EDU WiFi接続確認済み"
```

#### 2. 実機ドローン環境設定
```bash
# 実機環境変数設定
export ENVIRONMENT=raspberry_pi
export USE_REAL_DRONE=true
export DRONE_TYPE=tello_edu
export SAFETY_MODE=enabled
export MAX_FLIGHT_HEIGHT=150
export MAX_FLIGHT_DISTANCE=300
export MIN_BATTERY_LEVEL=50

# 安全設定確認
python -c "from config.safety import SafetyController; SafetyController.verify_safety_settings()"
```

#### 3. 実機接続テスト
```bash
# ドローン接続確認
python -c "
from djitellopy import Tello
tello = Tello()
try:
    tello.connect()
    print(f'Battery: {tello.get_battery()}%')
    print('Connection successful')
    tello.end()
except Exception as e:
    print(f'Connection failed: {e}')
"
```

### 実行手順

#### Step 1: 地上テスト (Safety Level 1)
```bash
# 接続・センサーテスト (飛行なし)
python -m pytest backend/tests/test_real_drone_connection_integration.py -v --safety-level=1

# 地上でのセンサー確認
python -m pytest backend/tests/test_real_drone_sensors_integration.py -v --no-flight
```

#### Step 2: 基本飛行テスト (Safety Level 2)
```bash
# 基本離着陸テスト
python -m pytest backend/tests/test_real_drone_flight_integration.py::test_takeoff_land -v --safety-level=2

# 短距離移動テスト (50cm以内)
python -m pytest backend/tests/test_real_drone_movement_integration.py -v --max-distance=50 --safety-level=2
```

#### Step 3: 標準飛行テスト (Safety Level 3)
```bash
# 全移動機能テスト
python -m pytest backend/tests/test_real_drone_movement_integration.py -v --safety-level=3

# カメラ・センサー統合テスト
python -m pytest backend/tests/test_real_drone_camera_integration.py -v --safety-level=3
```

#### Step 4: 高度機能テスト (Safety Level 4)
```bash
# 追跡・認識機能テスト (監視員必須)
python -m pytest backend/tests/test_real_drone_advanced_integration.py -v --safety-level=4 --supervised

# ミッションパッドテスト
python -m pytest backend/tests/test_real_drone_mission_pad_integration.py -v --safety-level=4 --supervised
```

### 緊急手順

#### 緊急停止手順
```bash
# 緊急停止コマンド (別ターミナルで常時準備)
python -c "
from djitellopy import Tello
tello = Tello()
tello.connect()
tello.emergency()
print('EMERGENCY STOP EXECUTED')
"

# または物理的緊急停止
# Tello EDUの電源ボタン長押し (5秒)
```

#### エラー時対応
```bash
# 通信断絶時の復旧
python scripts/recover_drone_connection.py

# バッテリー低下時の強制着陸
python scripts/emergency_land.py

# テスト中断・環境リセット
python scripts/reset_test_environment.py
```

### 成功基準チェックリスト
- [ ] 全安全テスト100%合格
- [ ] 移動精度±5cm以内
- [ ] 回転精度±3度以内
- [ ] 15分連続飛行動作
- [ ] カメラ30fps安定維持
- [ ] 緊急停止1秒以内応答
- [ ] バッテリー監視適切動作

---

## Phase 4: Integration Test C (Comprehensive Testing)

### 環境準備

#### 1. 全フェーズ統合環境
```bash
# Phase 3環境 + 包括テスト設定
export COMPREHENSIVE_TEST_MODE=true
export E2E_TEST_ENABLED=true
export PERFORMANCE_MONITORING=true
export SECURITY_SCAN_ENABLED=true
export QUALITY_GATE_ENABLED=true

# 長期テスト用設定
export LONG_TERM_TEST_DURATION=28800  # 8時間
export STRESS_TEST_ENABLED=true
export RESOURCE_PROFILING=true
```

#### 2. 監視システム設定
```bash
# システム監視開始
python scripts/start_system_monitoring.py

# ログ収集設定
python scripts/configure_comprehensive_logging.py

# パフォーマンス測定開始
python scripts/start_performance_monitoring.py
```

### 実行手順

#### Step 1: エンドツーエンドテスト
```bash
# 完全ワークフローテスト
python -m pytest backend/tests/test_e2e_comprehensive_integration.py -v --timeout=3600

# 複数ユーザー同時テスト
python -m pytest backend/tests/test_e2e_comprehensive_integration.py::test_multi_user_concurrent -v --workers=5

# 長期運用テスト (8時間)
python -m pytest backend/tests/test_e2e_comprehensive_integration.py::test_long_term_operation -v --timeout=28800
```

#### Step 2: システム性能テスト
```bash
# 負荷分散テスト
python -m pytest backend/tests/test_system_performance_comprehensive.py -v --load-test

# メモリ最適化テスト
python -m pytest backend/tests/test_system_performance_comprehensive.py -v --memory-profile

# ネットワーク耐性テスト
python -m pytest backend/tests/test_system_performance_comprehensive.py -v --network-stress
```

#### Step 3: セキュリティ・信頼性テスト
```bash
# セキュリティスキャン
python -m pytest backend/tests/test_security_reliability_comprehensive.py -v --security-audit

# 障害耐性テスト
python -m pytest backend/tests/test_security_reliability_comprehensive.py -v --fault-injection

# データ整合性テスト
python -m pytest backend/tests/test_security_reliability_comprehensive.py -v --data-integrity
```

#### Step 4: AI・ML包括テスト
```bash
# AIモデル性能テスト
python -m pytest backend/tests/test_ai_ml_comprehensive.py -v --model-evaluation

# 適応学習テスト
python -m pytest backend/tests/test_ai_ml_comprehensive.py -v --adaptive-learning

# モデル配置テスト
python -m pytest backend/tests/test_ai_ml_comprehensive.py -v --deployment-test
```

#### Step 5: 品質ゲート評価
```bash
# 全品質ゲート実行
python scripts/run_quality_gates.py --comprehensive

# 品質レポート生成
python scripts/generate_quality_report.py --all-phases

# 最終判定
python scripts/make_production_decision.py
```

### 成功基準チェックリスト

#### Critical Gates (必須)
- [ ] 全Phase 1-3テスト100%合格
- [ ] エンドツーエンドテスト100%合格
- [ ] セキュリティテスト脆弱性0件
- [ ] 安全性テスト100%合格

#### Performance Gates (性能)
- [ ] パフォーマンステスト95%以上目標達成
- [ ] 8時間長期運用テスト合格
- [ ] 負荷テスト設計上限値で安定動作
- [ ] AI精度テスト90%以上認識精度

#### Quality Gates (品質)
- [ ] 可用性99.9%達成
- [ ] レスポンス時間SLA達成
- [ ] リソース使用効率目標達成
- [ ] 運用自動化90%以上

---

## 全フェーズ共通事項

### ログ・レポート管理
```bash
# ログディレクトリ構造
backend/
├── logs/
│   ├── phase1_unit_tests.log
│   ├── phase2_pi_integration.log
│   ├── phase3_real_drone.log
│   └── phase4_comprehensive.log
├── reports/
│   ├── phase1_coverage_report.html
│   ├── phase2_performance_report.html
│   ├── phase3_safety_report.html
│   └── phase4_quality_gate_report.html
```

### トラブルシューティング

#### 共通問題と対処法
```bash
# 1. テスト環境初期化
python scripts/reset_test_environment.py --phase=<1|2|3|4>

# 2. 依存関係問題
pip install --force-reinstall -e .[dev]

# 3. Pi環境性能問題
sudo systemctl stop unnecessary_services
export PYTEST_WORKERS=2  # 並列数削減

# 4. 実機ドローン接続問題
python scripts/diagnose_drone_connection.py
python scripts/reset_drone_wifi.py

# 5. リソース不足問題
sudo sync; echo 3 > /proc/sys/vm/drop_caches  # Pi memory clear
```

### 継続的改善
```bash
# テスト結果分析
python scripts/analyze_test_trends.py --all-phases

# 性能ボトルネック特定
python scripts/identify_performance_bottlenecks.py

# 品質改善提案生成
python scripts/generate_improvement_recommendations.py
```

---

## 最終チェックリスト

### 各フェーズ完了確認
- [ ] Phase 1: 単体テスト完全実装・100%合格
- [ ] Phase 2: Pi統合テスト・性能基準達成
- [ ] Phase 3: 実機テスト・安全基準達成
- [ ] Phase 4: 包括テスト・品質ゲート全通過

### 運用準備確認
- [ ] 本番環境設定ガイド作成
- [ ] 運用監視システム構築
- [ ] 障害対応手順書作成
- [ ] 品質維持プロセス確立

### ドキュメント完備確認
- [ ] テスト仕様書作成
- [ ] 実行手順書作成
- [ ] 結果分析レポート作成
- [ ] 継続改善計画作成

**🎯 Phase 4完了時: Production Ready システムの実現**