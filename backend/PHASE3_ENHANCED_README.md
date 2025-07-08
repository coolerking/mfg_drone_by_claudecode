# Phase 3: Enhanced Drone Control Features

## 概要

Phase 3 Enhanced では、既存のPhase 3基盤を拡張し、ドローン制御システムに高度な機能を追加しました。精密な飛行制御、安全性の向上、ビジョン処理の強化、学習データ収集の自動化を実現し、産業用途に適用可能な高精度・高安全性システムを構築しました。

## 🚀 新機能一覧

### 1. Enhanced Drone Manager
- **精密飛行制御**: 5cm精度の高度制御
- **高度安全システム**: 多層防御と境界チェック
- **飛行計画実行**: ウェイポイントナビゲーション
- **リアルタイム監視**: 継続的なステータス監視
- **学習データ収集**: 多角度・多高度撮影の自動化

### 2. Enhanced Vision Service
- **高度物体検出**: YOLOv8シミュレーション（6種類のモデル）
- **OpenCV追跡**: 複数の追跡アルゴリズム対応
- **学習セッション**: データ品質管理と統計
- **パフォーマンス分析**: リアルタイム統計

### 3. Enhanced API Endpoints
- **25+ 新エンドポイント**: 強化されたドローン制御API
- **分析・監視API**: 詳細なメトリクスと統計
- **システム管理**: 設定更新とクリーンアップ

## 📋 システムアーキテクチャ

```
MCPサーバー (Phase 1/2)
    ↓ 自然言語処理
Enhanced Drone Manager ←→ Enhanced Vision Service
    ↓ 精密制御              ↓ 高度処理
ドローンシミュレーター    ← OpenCV追跡・学習データ
    ↓
Tello EDU ドローン
```

### アーキテクチャ構成

```
backend/api_server/
├── core/
│   ├── enhanced_drone_manager.py    # 🆕 強化されたドローン管理
│   ├── enhanced_vision_service.py   # 🆕 強化されたビジョン処理
│   └── ...
├── api/
│   ├── enhanced_drones.py          # 🆕 強化されたドローンAPI
│   └── ...
├── tests/
│   ├── test_phase3_enhanced_features.py  # 🆕 強化機能テスト
│   └── ...
└── PHASE3_ENHANCED_README.md       # 🆕 このドキュメント
```

## 🎯 飛行モード

Phase 3 Enhanced では6つの飛行モードを提供：

1. **Manual**: 手動制御（デフォルト）
2. **Auto**: 自動飛行計画実行
3. **Guided**: ガイド付き制御
4. **Tracking**: 物体追跡モード
5. **Learning Data Collection**: 学習データ収集モード
6. **Emergency**: 緊急モード

## 🛡️ 安全システム

### 安全境界
```python
FlightBounds:
  min_x: -10.0m, max_x: 10.0m
  min_y: -10.0m, max_y: 10.0m  
  min_z: 0.2m,   max_z: 5.0m
```

### 安全チェック項目
- バッテリーレベル監視（最小15%、緊急10%）
- 飛行境界チェック
- 最大飛行時間（1200秒）
- 衝突回避
- 風速制限（5.0m/s）

### 安全違反の自動記録
```python
SafetyViolation:
  type: str                # 違反タイプ
  timestamp: datetime      # 発生時刻
  details: Dict[str, Any]  # 詳細情報
  severity: SafetyLevel    # 重要度
```

## 🔧 API使用例

### 基本的な制御

#### 1. 強化された接続
```bash
curl -X POST "http://localhost:8000/api/drones/drone_001/connect/enhanced" \
  -H "X-API-Key: your-api-key"
```

#### 2. 飛行モード設定
```bash
curl -X POST "http://localhost:8000/api/drones/drone_001/flight_mode" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '"auto"'
```

#### 3. 精密高度制御
```bash
curl -X POST "http://localhost:8000/api/drones/drone_001/altitude/precise" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "target_height": 150,
    "mode": "absolute", 
    "speed": 0.5,
    "timeout": 30.0
  }'
```

### 飛行計画実行

```bash
curl -X POST "http://localhost:8000/api/drones/drone_001/flight_plan" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "waypoints": [
      [1.0, 1.0, 1.0],
      [2.0, 2.0, 1.5],
      [0.0, 2.0, 1.0]
    ],
    "speed": 1.0,
    "altitude_mode": "absolute",
    "safety_checks": true
  }'
```

### 学習データ収集

```bash
curl -X POST "http://localhost:8000/api/drones/drone_001/learning_data/collect/enhanced" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "object_name": "person",
    "capture_positions": ["front", "back", "left", "right"],
    "movement_distance": 50,
    "photos_per_position": 3,
    "altitude_levels": [100, 150, 200],
    "rotation_angles": [0, 45, 90, 135, 180, 225, 270, 315],
    "quality": "high"
  }'
```

### 高度物体検出

```bash
curl -X POST "http://localhost:8000/api/vision/detection/enhanced" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "image_data": "<base64_encoded_image>",
    "model_id": "yolo_v8_person_detector",
    "confidence_threshold": 0.7,
    "filter_labels": ["person"],
    "max_detections": 5
  }'
```

### 強化された追跡

```bash
curl -X POST "http://localhost:8000/api/vision/tracking/start/enhanced" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "model_id": "yolo_v8_general",
    "drone_id": "drone_001",
    "config": {
      "algorithm": "csrt",
      "confidence_threshold": 0.5,
      "follow_distance": 200,
      "max_tracking_loss": 30,
      "update_interval": 0.1
    }
  }'
```

## 📊 監視・分析API

### ドローンメトリクス
```bash
curl -X GET "http://localhost:8000/api/drones/drone_001/metrics" \
  -H "X-API-Key: your-api-key"
```

レスポンス例：
```json
{
  "total_flight_time": 1234.5,
  "total_distance": 567.8,
  "total_photos": 89,
  "emergency_stops": 0,
  "safety_violations": 2,
  "performance_score": 95.3,
  "last_maintenance": null
}
```

### 安全違反履歴
```bash
curl -X GET "http://localhost:8000/api/drones/drone_001/safety/violations" \
  -H "X-API-Key: your-api-key"
```

### 飛行ログ
```bash
curl -X GET "http://localhost:8000/api/drones/drone_001/logs/flight?limit=100" \
  -H "X-API-Key: your-api-key"
```

### 総合分析
```bash
curl -X GET "http://localhost:8000/api/system/analytics/overall" \
  -H "X-API-Key: your-api-key"
```

## 🔍 ビジョンモデル

### 利用可能なモデル

1. **yolo_v8_general**: 汎用物体検出（80クラス）
2. **yolo_v8_person_detector**: 人物検出専用
3. **yolo_v8_vehicle_detector**: 車両検出専用
4. **ssd_mobilenet_v2**: 軽量物体検出
5. **faster_rcnn_resnet50**: 高精度物体検出
6. **custom_people_tracker**: カスタム人物追跡

### 追跡アルゴリズム

- **CSRT**: 高精度追跡（推奨）
- **KCF**: 高速追跡
- **MOSSE**: 超高速追跡
- **MEDIANFLOW**: 予測型追跡
- **TLD**: 長期追跡
- **BOOSTING**: 基本追跡

### モデル一覧取得
```bash
curl -X GET "http://localhost:8000/api/vision/models/enhanced" \
  -H "X-API-Key: your-api-key"
```

## 🧪 学習データ収集

### 自動化された撮影パターン

Phase 3 Enhanced の学習データ収集では以下の自動化を提供：

1. **多角度撮影**: 前後左右の複数角度
2. **多高度撮影**: 複数の高度レベル
3. **回転撮影**: 指定角度での回転撮影
4. **品質評価**: 自動的な画像品質スコア算出
5. **メタデータ**: 撮影条件の詳細記録

### 学習セッション管理

#### セッション開始
```bash
curl -X POST "http://localhost:8000/api/learning_data/session/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "object_name": "industrial_robot",
    "session_config": {
      "quality_threshold": 0.8,
      "auto_annotation": true
    }
  }'
```

#### サンプル追加
```bash
curl -X POST "http://localhost:8000/api/learning_data/session/{session_id}/add_sample" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "image_data": "<base64_image>",
    "annotation": {
      "label": "industrial_robot",
      "bbox": [100, 100, 200, 200],
      "metadata": {
        "position": "front",
        "altitude": 150,
        "angle": 45
      }
    },
    "quality_score": 0.85
  }'
```

#### セッション完了
```bash
curl -X POST "http://localhost:8000/api/learning_data/session/{session_id}/finish" \
  -H "X-API-Key: your-api-key"
```

## ⚙️ 設定とカスタマイズ

### 安全設定の更新

```bash
curl -X PUT "http://localhost:8000/api/system/safety/config" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "min_battery_level": 20,
    "max_flight_time": 1800,
    "emergency_landing_battery": 15,
    "collision_avoidance": true,
    "wind_speed_limit": 8.0,
    "max_velocity": 3.0,
    "flight_bounds": {
      "min_x": -15.0,
      "max_x": 15.0,
      "min_y": -15.0,
      "max_y": 15.0,
      "min_z": 0.5,
      "max_z": 8.0
    }
  }'
```

### 現在の安全設定確認
```bash
curl -X GET "http://localhost:8000/api/system/safety/config" \
  -H "X-API-Key: your-api-key"
```

## 🚦 システム管理

### 強化されたヘルスチェック
```bash
curl -X GET "http://localhost:8000/api/system/health/enhanced" \
  -H "X-API-Key: your-api-key"
```

レスポンス例：
```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "overall_status": "healthy",
  "components": {
    "enhanced_drone_manager": {
      "status": "running",
      "monitoring_active": true,
      "connected_drones": 2,
      "active_tasks": 1
    },
    "enhanced_vision_service": {
      "status": "running",
      "tracking_active": true,
      "active_trackers": 1,
      "available_models": 6
    }
  },
  "performance_metrics": {
    "total_flight_time": 3600.0,
    "average_performance_score": 94.2,
    "recent_safety_violations": 0
  }
}
```

### システムクリーンアップ
```bash
curl -X POST "http://localhost:8000/api/system/cleanup" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"max_age_hours": 24}'
```

## 📈 パフォーマンス指標

### ドローン性能スコア計算
パフォーマンススコア（0-100）は以下の要素で計算：
- **基本スコア**: 100点
- **バッテリー効率**: 時間あたりのバッテリー消費効率
- **安全違反**: -5点/件
- **緊急停止**: -15点/件

### ビジョン処理統計
- **平均検出数**: フレームあたりの平均検出数
- **平均信頼度**: 検出の平均信頼度スコア
- **総推論回数**: 実行された推論の総数
- **追跡成功率**: 追跡成功フレーム数 / 総フレーム数

### システム統計取得
```bash
curl -X GET "http://localhost:8000/api/system/analytics/vision" \
  -H "X-API-Key: your-api-key"
```

## 🔧 開発・テスト

### テスト実行
```bash
# Phase 3 Enhanced の全テストを実行
cd backend
python -m pytest tests/test_phase3_enhanced_features.py -v

# 特定のテストクラスのみ実行
python -m pytest tests/test_phase3_enhanced_features.py::TestEnhancedDroneManager -v
python -m pytest tests/test_phase3_enhanced_features.py::TestEnhancedVisionService -v
python -m pytest tests/test_phase3_enhanced_features.py::TestIntegration -v

# パフォーマンステスト
python -m pytest tests/test_phase3_enhanced_features.py::TestPerformance -v

# カバレッジレポート
pytest tests/test_phase3_enhanced_features.py --cov=api_server.core --cov-report=html
```

### 開発用サーバー起動
```bash
cd backend
python start_api_server.py
```

### 強化機能付きMCPサーバー起動
```bash
cd mcp-server
python start_mcp_server.py --enhanced
```

## 🌟 使用例・シナリオ

### シナリオ1: 産業施設点検
```python
# 1. ドローン接続・離陸
await connect_drone("drone_001")
await set_flight_mode("drone_001", "auto")
await takeoff_drone("drone_001")

# 2. 施設周囲の詳細飛行計画実行
flight_plan = {
    "waypoints": [
        [0, 0, 2],      # 開始点
        [10, 0, 2],     # 施設東側
        [10, 10, 3],    # 施設北東角（高度上げ）
        [0, 10, 3],     # 施設北側
        [-10, 10, 2],   # 施設北西角
        [-10, 0, 2],    # 施設西側
        [0, 0, 2]       # 帰還
    ],
    "speed": 0.8,
    "altitude_mode": "absolute",
    "safety_checks": True,
    "completion_timeout": 600.0
}
await execute_flight_plan("drone_001", flight_plan)

# 3. 飛行計画の進捗監視
status = await get_flight_plan_status("drone_001")
while status["task_running"]:
    await asyncio.sleep(5)
    status = await get_flight_plan_status("drone_001")
```

### シナリオ2: 高精度人物追跡
```python
# 1. 人物検出・追跡システム設定
tracking_config = {
    "algorithm": "csrt",        # 高精度追跡
    "confidence_threshold": 0.7, # 高信頼度
    "follow_distance": 300,     # 3m距離維持
    "max_tracking_loss": 50,    # 長期ロスト許容
    "update_interval": 0.05     # 20FPS更新
}

await start_tracking_enhanced(
    model_id="yolo_v8_person_detector",
    drone_id="drone_001",
    config=tracking_config
)

# 2. 追跡状況のリアルタイム監視
while True:
    status = await get_tracking_status_enhanced()
    for session in status["active_sessions"]:
        print(f"Target detected: {session['target_detected']}")
        print(f"Success rate: {session['success_rate']:.2f}")
        
        if session['success_rate'] < 0.7:
            print("Warning: Low tracking success rate")
    
    await asyncio.sleep(1)
```

### シナリオ3: 包括的学習データ収集
```python
# 1. 高品質学習セッション開始
session_id = await start_learning_session(
    object_name="manufacturing_part",
    session_config={
        "quality_threshold": 0.85,
        "auto_quality_filter": True,
        "metadata_extraction": True
    }
)

# 2. 包括的多角度・多高度撮影
collection_config = {
    "object_name": "manufacturing_part",
    "capture_positions": [
        "front", "back", "left", "right", 
        "front_left", "front_right", 
        "back_left", "back_right"
    ],
    "altitude_levels": [80, 100, 120, 150, 180, 200],  # 6レベル
    "rotation_angles": list(range(0, 360, 15)),         # 24角度
    "photos_per_position": 5,                           # 高密度撮影
    "movement_distance": 40,                            # 近距離精密
    "quality": "high"
}

collection_result = await collect_learning_data_enhanced(
    drone_id="drone_001",
    config=collection_config
)

# 3. 品質分析とフィードバック
summary = await finish_learning_session(session_id)
print(f"Collected {summary['total_samples']} samples")
print(f"High quality: {summary['high_quality_samples']}")
print(f"Average quality: {summary['average_quality']:.3f}")

quality_dist = summary['quality_distribution']
print(f"Quality distribution - High: {quality_dist['high']}, "
      f"Medium: {quality_dist['medium']}, Low: {quality_dist['low']}")
```

### シナリオ4: 安全性重視運用
```python
# 1. 厳格な安全設定
safety_config = {
    "min_battery_level": 25,        # 高めのバッテリー閾値
    "max_flight_time": 900,         # 15分制限
    "emergency_landing_battery": 20, # 早期緊急着陸
    "wind_speed_limit": 3.0,        # 低風速制限
    "max_velocity": 1.5,            # 低速制限
    "flight_bounds": {
        "min_x": -5.0, "max_x": 5.0,   # 狭い範囲
        "min_y": -5.0, "max_y": 5.0,
        "min_z": 0.5,  "max_z": 3.0    # 低高度制限
    }
}
await update_safety_config(safety_config)

# 2. 安全チェック付き操作
try:
    await takeoff_drone("drone_001")
    await set_altitude_precise("drone_001", 100, "absolute", speed=0.3)
    await move_drone_enhanced("drone_001", {"direction": "forward", "distance": 200})
except ValueError as e:
    if "安全チェック" in str(e):
        print("Safety check prevented unsafe operation")
        # 安全違反の詳細確認
        violations = await get_safety_violations("drone_001")
        for violation in violations[-5:]:  # 最新5件
            print(f"Violation: {violation['type']} at {violation['timestamp']}")

# 3. 継続的安全監視
while True:
    violations = await get_safety_violations("drone_001")
    recent_violations = [v for v in violations 
                        if (datetime.now() - v['timestamp']).seconds < 300]
    
    if recent_violations:
        print(f"Alert: {len(recent_violations)} safety violations in last 5 minutes")
        for v in recent_violations:
            if v['severity'] == 'critical':
                await emergency_stop_enhanced("drone_001")
                break
    
    await asyncio.sleep(10)
```

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. 精密高度制御の失敗
```
Error: Target height too low/high
```
**解決策**: 
- 安全境界内の高度か確認 (0.2m - 5.0m)
- 現在の高度から妥当な変化量か確認
- 相対モードと絶対モードの使い分けを確認

#### 2. 飛行計画実行エラー
```
Error: Safety check failed at waypoint N
```
**解決策**:
- 全ウェイポイントが飛行境界内か確認
- バッテリーレベルが十分か確認
- ウェイポイント間の距離が適切か確認

#### 3. 学習データ収集の品質問題
```
Warning: Low quality images detected (quality < 0.4)
```
**解決策**:
- 照明条件を改善
- ドローンの安定性を確認（風の影響等）
- 対象物との距離を調整
- カメラのフォーカス設定を確認

#### 4. 追跡の失敗・ロスト
```
Warning: Tracking lost for session
```
**解決策**:
- より高精度なアルゴリズム（CSRT）を使用
- 信頼度閾値を調整
- 追跡対象が適切にフレーム内にいるか確認
- 背景とのコントラストを改善

#### 5. メモリ不足・性能問題
```
Error: System performance degraded
```
**解決策**:
- システムクリーンアップを実行
- 古い学習セッションを削除
- 同時追跡数を制限
- システムリソースを確認

### デバッグ用コマンド

```bash
# 1. ドローン詳細ステータス確認
curl -X GET "http://localhost:8000/api/drones/drone_001/status/enhanced" \
  -H "X-API-Key: your-api-key"

# 2. 安全違反履歴確認
curl -X GET "http://localhost:8000/api/drones/drone_001/safety/violations" \
  -H "X-API-Key: your-api-key"

# 3. 飛行ログ確認
curl -X GET "http://localhost:8000/api/drones/drone_001/logs/flight?limit=50" \
  -H "X-API-Key: your-api-key"

# 4. システム全体ヘルス確認
curl -X GET "http://localhost:8000/api/system/health/enhanced" \
  -H "X-API-Key: your-api-key"

# 5. ビジョンシステム分析
curl -X GET "http://localhost:8000/api/system/analytics/vision" \
  -H "X-API-Key: your-api-key"

# 6. 総合システム分析
curl -X GET "http://localhost:8000/api/system/analytics/overall" \
  -H "X-API-Key: your-api-key"
```

### ログファイル確認

```bash
# APIサーバーログ
tail -f logs/api_server.log | grep -E "(ERROR|WARNING|CRITICAL)"

# 特定ドローンの操作ログ
tail -f logs/api_server.log | grep "drone_001"

# 安全違反ログ
tail -f logs/api_server.log | grep "safety_violation"

# 追跡関連ログ
tail -f logs/api_server.log | grep -E "(tracking|detection)"
```

## 📚 次のステップ

Phase 3 Enhanced の実装により、以下の高度な機能が利用可能になりました：

### ✅ 達成された機能
1. **産業用途対応の精密制御**: 5cm精度の位置制御
2. **包括的安全システム**: 多層防御による事故防止
3. **高度なビジョン処理**: リアルタイム検出・追跡
4. **効率的な学習データ生成**: AI開発の大幅な加速
5. **詳細な監視・分析**: 運用最適化のためのインサイト

### 🚀 Phase 4への展開予定
1. **マルチドローン協調制御**: 複数機体の連携飛行
2. **リアルタイム機械学習**: エッジでの学習・推論
3. **高度センサー統合**: LiDAR、IMU等の統合
4. **クラウド連携**: リモート監視・制御システム
5. **Web UI Dashboard**: 包括的な操作・監視インターフェース

### 🔧 カスタマイズ・拡張ポイント
1. **カスタム安全ルール**: 特定用途に応じた安全設定
2. **独自ビジョンモデル**: 特定物体に特化したモデル
3. **飛行パターン**: 特定タスク用の飛行アルゴリズム
4. **データ処理パイプライン**: 収集データの自動処理
5. **外部システム連携**: 既存システムとの統合

## 📄 関連ドキュメント

- [Phase 1 README](../mcp-server/README.md) - 基盤システム
- [Phase 2 README](../mcp-server/PHASE2_README.md) - 自然言語処理
- [Phase 3 README](./PHASE3_README.md) - 基本ビジョン・モデル管理
- [API仕様](../shared/api-specs/mcp-api.yaml) - MCP API仕様
- [バックエンドAPI仕様](../shared/api-specs/backend-api.yaml) - バックエンドAPI

## 🤝 貢献・サポート

### 貢献方法
1. **Issue作成**: 機能要求やバグレポート
2. **Pull Request**: 実装改善や新機能
3. **テストケース追加**: カバレッジ向上
4. **ドキュメント改善**: 使用例や説明の追加

### サポート
- 技術的な質問: GitHub Issues
- 機能要求: Feature Request テンプレート
- バグレポート: Bug Report テンプレート

---

**Phase 3 Enhanced Drone Control Features** - 次世代ドローン制御システムで、安全で精密で賢い飛行を実現