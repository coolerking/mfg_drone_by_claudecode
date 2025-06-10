# Phase 2: Integration Test A - Raspberry Pi + Mock Drone Plan

## 概要
Raspberry Pi環境でドローン実機なしのテスト。OpenAPI定義のすべての機能に対して引数戻り値アサーション、エラー発生時の挙動、引数の境界値超前後と中央値の挙動が想定内かどうか。

## 環境設定
- 実行環境: Raspberry Pi 5 (Raspberry Pi OS Lite 64bit)
- Python: 3.11
- ドローン: TelloStub (モック) + Pi固有最適化
- ネットワーク: Raspberry Pi WiFi環境
- FastAPI: 完全動作状態

## テスト対象: OpenAPI定義の全エンドポイント

### 1. **Raspberry Pi固有環境テスト**

#### 新規テストファイル: `test_pi_environment_integration.py`

```python
"""
Raspberry Pi環境での統合テスト
ハードウェア制約・リソース制限・環境固有動作の検証
"""

class TestRaspberryPiEnvironmentIntegration:
    
    def test_pi_resource_constraints_boundary_values(self):
        """Pi環境リソース制約 - 境界値テスト"""
        # メモリ使用量: 8GB制限内での動作確認
        # CPU使用率: 高負荷時の動作検証
        # ストレージ I/O: microSD読み書き性能
        # 同時リクエスト処理限界
        
    def test_pi_wifi_network_boundary_values(self):
        """Pi WiFi接続 - 境界値・エラーハンドリングテスト"""
        # WiFi接続安定性テスト
        # ネットワーク遅延境界値 (100ms, 500ms, 1000ms)
        # 接続断絶時の復旧処理
        # 複数クライアント同時接続限界
        
    def test_pi_camera_hardware_integration_boundary_values(self):
        """Piカメラハードウェア統合 - 境界値テスト"""
        # カメラモジュール初期化時間
        # 画像処理負荷での性能劣化
        # 長時間ストリーミング時の安定性
        # 解像度・フレームレート境界値
```

### 2. **OpenAPI完全エンドポイントテスト**

#### 新規テストファイル: `test_openapi_complete_integration.py`

```python
"""
OpenAPI仕様書定義の全エンドポイント統合テスト
Pi環境での完全なAPI動作検証
"""

class TestOpenAPICompleteIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_pi_environment(self):
        """Pi環境セットアップ"""
        # Pi固有設定の適用
        # TelloStub with Pi optimization
        # リソース監視の開始
        
    # System Endpoints
    def test_health_endpoint_integration_boundary_values(self):
        """GET /health - Pi環境統合境界値テスト"""
        # 正常系: システム正常状態確認
        # 負荷系: 高CPU/メモリ使用時の応答
        # ネットワーク系: WiFi遅延時の応答時間
        # 戻り値検証: {"status": "healthy"}形式
        
    # Connection Endpoints  
    def test_drone_connect_integration_boundary_values(self):
        """POST /drone/connect - Pi環境統合境界値テスト"""
        # 正常系: WiFi経由でのモック接続
        # 異常系: ネットワーク不安定時の接続
        # 境界値: 接続タイムアウト設定値前後
        # エラー系: 接続失敗時の適切なエラーレスポンス
        # 戻り値検証: StatusResponse形式
        
    def test_drone_disconnect_integration_boundary_values(self):
        """POST /drone/disconnect - Pi環境統合境界値テスト"""
        # 正常系: 接続済み状態からの切断
        # 異常系: 未接続状態での切断試行
        # ネットワーク断時の切断処理
        # 戻り値検証: StatusResponse形式
        
    # Flight Control Endpoints
    def test_drone_takeoff_integration_boundary_values(self):
        """POST /drone/takeoff - Pi環境統合境界値テスト"""
        # 正常系: 接続済み状態からの離陸
        # 異常系: 未接続・バッテリー低下時の離陸
        # 境界値: バッテリー閾値前後での動作
        # Pi性能: 離陸処理時のリソース使用量
        # 戻り値検証: StatusResponse形式
        
    def test_drone_land_integration_boundary_values(self):
        """POST /drone/land - Pi環境統合境界値テスト"""
        # 正常系: 飛行状態からの着陸
        # 異常系: 未飛行状態での着陸試行
        # 緊急時: 通信エラー時の着陸処理
        # 戻り値検証: StatusResponse形式
        
    def test_drone_emergency_integration_boundary_values(self):
        """POST /drone/emergency - Pi環境統合境界値テスト"""
        # 全状態からの緊急停止実行
        # 高負荷時の緊急停止応答速度
        # ネットワーク障害時の緊急停止
        # 戻り値検証: StatusResponse形式
        
    # Movement Endpoints
    def test_drone_movement_integration_boundary_values(self):
        """POST /drone/move/* - Pi環境統合境界値テスト"""
        # 各方向移動エンドポイント (up, down, left, right, forward, back)
        # 境界値: 移動距離 20cm, 260cm, 500cm
        # 異常値: 19cm, 501cm での適切なエラー処理
        # Pi処理: 移動計算処理時間・精度
        # 戻り値検証: StatusResponse形式
        
    def test_drone_rotation_integration_boundary_values(self):
        """POST /drone/rotate/* - Pi環境統合境界値テスト"""
        # 回転エンドポイント (clockwise, counter_clockwise)
        # 境界値: 回転角度 1度, 180度, 360度
        # 異常値: 0度, 361度での適切なエラー処理
        # Pi処理: 回転計算処理時間・精度
        # 戻り値検証: StatusResponse形式
        
    # Advanced Movement Endpoints
    def test_drone_curve_integration_boundary_values(self):
        """POST /drone/curve - Pi環境統合境界値テスト"""
        # カーブ飛行の境界値テスト
        # 座標値の境界確認
        # Pi計算: 複雑な軌道計算処理性能
        # 戻り値検証: StatusResponse形式
        
    def test_drone_flip_integration_boundary_values(self):
        """POST /drone/flip - Pi環境統合境界値テスト"""
        # フリップ方向の全パターン確認
        # 飛行状態確認とエラーハンドリング
        # 戻り値検証: StatusResponse形式
        
    # Camera Endpoints
    def test_camera_stream_integration_boundary_values(self):
        """POST /camera/* - Pi環境統合境界値テスト"""
        # start_stream, stop_stream統合テスト
        # Pi環境: カメラストリーミング負荷テスト
        # 境界値: 長時間ストリーミング安定性
        # 複数クライアント同時ストリーミング
        # 戻り値検証: StatusResponse形式
        
    def test_camera_capture_integration_boundary_values(self):
        """POST /camera/capture - Pi環境統合境界値テスト"""
        # 写真撮影機能の統合テスト
        # Pi性能: 画像処理・保存処理時間
        # ストレージ: microSD書き込み性能
        # 戻り値検証: 画像データ形式
        
    # Sensor Endpoints
    def test_sensors_integration_boundary_values(self):
        """GET /sensors/* - Pi環境統合境界値テスト"""
        # battery, height, speed, position, attitude取得
        # Pi通信: センサーデータ取得遅延
        # 境界値: センサー値の範囲確認
        # エラー系: センサー通信エラー時の処理
        # 戻り値検証: センサーデータ型・範囲
        
    # Settings Endpoints  
    def test_settings_integration_boundary_values(self):
        """GET/POST /settings/* - Pi環境統合境界値テスト"""
        # 設定取得・更新の統合テスト
        # Pi環境: 設定ファイル読み書き性能
        # 境界値: 設定値の妥当性確認
        # 戻り値検証: 設定データ形式
        
    # Mission Pad Endpoints
    def test_mission_pad_integration_boundary_values(self):
        """POST /mission_pad/* - Pi環境統合境界値テスト"""
        # ミッションパッド機能統合テスト
        # Pi画像処理: パッド認識処理性能
        # 境界値: 認識距離・角度制限
        # 戻り値検証: StatusResponse形式
        
    # Tracking Endpoints
    def test_tracking_integration_boundary_values(self):
        """POST /tracking/* - Pi環境統合境界値テスト"""
        # 追跡機能統合テスト
        # Pi AI処理: 物体認識処理負荷
        # 境界値: 追跡対象サイズ・距離制限
        # 戻り値検証: TrackingResponse形式
        
    # Model Management Endpoints
    def test_model_integration_boundary_values(self):
        """GET/POST /model/* - Pi環境統合境界値テスト"""
        # AIモデル管理統合テスト
        # Pi性能: モデル読み込み・実行時間
        # ストレージ: モデルファイル容量制限
        # 戻り値検証: ModelInfo形式
```

### 3. **Pi環境パフォーマンステスト**

#### 新規テストファイル: `test_pi_performance_integration.py`

```python
"""
Raspberry Pi環境でのパフォーマンス統合テスト
"""

class TestPiPerformanceIntegration:
    
    def test_concurrent_requests_boundary_values(self):
        """同時リクエスト処理 - 境界値テスト"""
        # 同時接続数: 1, 5, 10, 20クライアント
        # 境界値超過時のレスポンス劣化確認
        # リソース制限到達時のエラー処理
        
    def test_memory_usage_boundary_values(self):
        """メモリ使用量 - 境界値テスト"""
        # 長時間動作時のメモリリーク確認
        # 大容量画像処理時のメモリ消費
        # メモリ制限到達時のエラー処理
        
    def test_cpu_usage_boundary_values(self):
        """CPU使用率 - 境界値テスト"""
        # AI処理・画像処理時のCPU負荷
        # 高負荷時のレスポンス時間劣化
        # CPU制限到達時の処理優先度
        
    def test_network_latency_boundary_values(self):
        """ネットワーク遅延 - 境界値テスト"""
        # WiFi遅延: 50ms, 200ms, 500ms, 1000ms
        # 遅延増加時のタイムアウト処理
        # 接続断絶時の自動復旧機能
```

## Pi環境固有設定

### 環境変数設定
```bash
# Pi環境識別
export ENVIRONMENT=raspberry_pi
export PI_OPTIMIZATION=true
export RESOURCE_LIMIT_MODE=true

# パフォーマンス調整
export MAX_CONCURRENT_REQUESTS=10
export MEMORY_LIMIT_MB=6144
export CPU_LIMIT_PERCENT=80
```

### pytest設定 (Pi最適化)
```python
# conftest.py に追加
@pytest.fixture(scope="session")
def pi_environment_setup():
    """Pi環境固有セットアップ"""
    # リソース監視開始
    # TelloStub Pi最適化設定
    # ログレベル調整 (Pi性能考慮)
    
@pytest.fixture
def pi_performance_monitor():
    """Pi性能監視fixture"""
    # CPU, Memory, Network監視
    # テスト前後でのリソース使用量確認
```

## 実行コマンド

```bash
# Phase 2 Pi環境統合テスト実行
python -m pytest backend/tests/test_*_integration.py -v --pi-environment

# OpenAPI完全テスト
python -m pytest backend/tests/test_openapi_complete_integration.py -v

# パフォーマンステスト
python -m pytest backend/tests/test_pi_performance_integration.py -v --timeout=300

# リソース監視付き実行
python -m pytest backend/tests/test_*_integration.py --cov=backend --resource-monitor
```

## 成功基準

- OpenAPI全エンドポイント: 100%動作確認
- Pi環境リソース制約: 制限内での安定動作
- 同時リクエスト処理: 10クライアント対応
- レスポンス時間: 95%のリクエストが1秒以内
- メモリ使用量: 6GB以内での安定動作
- 長時間動作: 8時間連続動作可能

## Pi環境でのみ発見される問題の例

1. **メモリ制約**: 大容量画像処理時のOOM
2. **CPU制約**: AI処理時のレスポンス遅延
3. **I/O制約**: microSD書き込み時の遅延
4. **WiFi制約**: 不安定なネットワーク接続
5. **温度制約**: 長時間動作時の熱throttling