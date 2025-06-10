# Phase 3: Integration Test B - Raspberry Pi + Real Drone Plan

## 概要
ドローン実機ありRaspberry Piありでのテスト。OpenAPI定義のすべての機能に対して引数戻り値アサーション、エラー発生時の挙動、引数の境界値超前後と中央値の挙動が想定内かどうか。

## 環境設定
- 実行環境: Raspberry Pi 5 (Raspberry Pi OS Lite 64bit)
- Python: 3.11
- ドローン: **Tello EDU実機**
- ネットワーク: Pi WiFi + Tello EDU WiFi
- 物理環境: 屋内テスト環境 (安全措置完備)

## 安全対策・前提条件

### 必須安全措置
```python
"""
実機ドローンテスト用安全設定
"""

class SafetyConfiguration:
    # 飛行制限
    MAX_FLIGHT_HEIGHT = 150  # cm (室内上限)
    MAX_FLIGHT_DISTANCE = 300  # cm (水平移動上限)
    EMERGENCY_LANDING_TIMEOUT = 30  # 秒
    
    # 安全境界
    SAFETY_BOUNDARY = {
        "min_x": -200, "max_x": 200,  # cm
        "min_y": -200, "max_y": 200,  # cm
        "min_z": 50, "max_z": 150     # cm
    }
    
    # バッテリー安全閾値
    MIN_BATTERY_FOR_FLIGHT = 30  # %
    MIN_BATTERY_FOR_TEST = 50    # %
```

### テスト実行前チェックリスト
- [ ] ドローン充電済み (バッテリー80%以上)
- [ ] プロペラガード装着
- [ ] 飛行エリア安全確認 (障害物なし)
- [ ] 緊急停止手順確認
- [ ] 実機接続テスト完了

## テスト対象: 実機ドローンでのOpenAPI完全検証

### 1. **実機接続・通信テスト**

#### 新規テストファイル: `test_real_drone_connection_integration.py`

```python
"""
実機Tello EDUドローン接続・通信統合テスト
"""

class TestRealDroneConnectionIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_real_drone_environment(self):
        """実機ドローン環境セットアップ"""
        # 実機ドローン接続確認
        # バッテリー残量確認
        # WiFi接続状況確認
        # 安全設定適用
        
    def test_real_drone_connect_boundary_values(self):
        """実機接続 - 境界値・エラーハンドリングテスト"""
        # 正常系: 実機への初回接続
        # 異常系: バッテリー低下時の接続拒否
        # 境界値: 接続タイムアウト値前後
        # 実機特有: djitellopy接続プロトコル
        # 戻り値検証: 実機からの実際のレスポンス
        
    def test_real_drone_communication_boundary_values(self):
        """実機通信 - 境界値・遅延テスト"""
        # WiFi信号強度による通信品質変化
        # 距離による通信遅延測定
        # 境界値: 通信可能距離上限
        # 通信エラー時の再送・復旧処理
        # 実機特有: Tello SDK通信プロトコル
        
    def test_real_drone_disconnect_boundary_values(self):
        """実機切断 - 境界値・安全性テスト"""
        # 正常系: 安全な切断処理
        # 異常系: 通信断絶時の自動切断
        # 安全確認: 切断時の自動着陸
        # 実機状態: 切断後のドローン状態確認
```

### 2. **実機飛行制御テスト**

#### 新規テストファイル: `test_real_drone_flight_integration.py`

```python
"""
実機Tello EDU飛行制御統合テスト
"""

class TestRealDroneFlightIntegration:
    
    def test_real_drone_takeoff_boundary_values(self):
        """実機離陸 - 境界値・安全性テスト"""
        # 正常系: 実機離陸処理
        # 異常系: バッテリー低下時の離陸拒否
        # 境界値: 最小バッテリー残量での離陸
        # 安全確認: 離陸高度制限 (80cm固定)
        # 実機検証: 実際の高度センサー値確認
        # 物理法則: 実際の離陸時間・消費電力
        
    def test_real_drone_land_boundary_values(self):
        """実機着陸 - 境界値・安全性テスト"""
        # 正常系: 飛行状態からの安全着陸
        # 異常系: 低バッテリー時の緊急着陸
        # 境界値: 着陸可能高度範囲
        # 安全確認: 着陸地点の自動検出
        # 実機検証: 着陸精度・時間測定
        
    def test_real_drone_emergency_boundary_values(self):
        """実機緊急停止 - 境界値・安全性テスト"""
        # 緊急停止の即座実行確認
        # 全飛行状態からの緊急停止
        # 応答時間: 1秒以内の即座停止
        # 安全確認: プロペラ完全停止確認
        # 実機検証: 緊急停止後の状態復旧
```

### 3. **実機移動・センサーテスト**

#### 新規テストファイル: `test_real_drone_movement_integration.py`

```python
"""
実機Tello EDU移動・センサー統合テスト
"""

class TestRealDroneMovementIntegration:
    
    def test_real_drone_directional_movement_boundary_values(self):
        """実機方向移動 - 境界値・精度テスト"""
        # 各方向移動の実測精度確認
        # 境界値: 最小移動距離 20cm
        # 境界値: 最大移動距離 500cm  
        # 中央値: 260cm移動精度確認
        # 実機特有: 風・気圧による誤差測定
        # 物理検証: 実際の移動距離測定
        
    def test_real_drone_rotation_boundary_values(self):
        """実機回転 - 境界値・精度テスト"""
        # 時計回り・反時計回り精度確認
        # 境界値: 最小回転角度 1度
        # 境界値: 最大回転角度 360度
        # 中央値: 180度回転精度確認
        # 実機特有: ジャイロセンサー精度確認
        # 物理検証: 実際の回転角度測定
        
    def test_real_drone_sensors_boundary_values(self):
        """実機センサー - 境界値・精度テスト"""
        # バッテリー残量: 実測値vs表示値
        # 高度センサー: 実測高度vs表示値
        # 速度センサー: 移動時の速度測定
        # 姿勢センサー: pitch, roll, yaw精度
        # 境界値: センサー測定範囲上下限
        # 実機特有: センサー誤差・ノイズ測定
```

### 4. **実機カメラ・画像処理テスト**

#### 新規テストファイル: `test_real_drone_camera_integration.py`

```python
"""
実機Tello EDUカメラ・画像処理統合テスト
"""

class TestRealDroneCameraIntegration:
    
    def test_real_drone_camera_stream_boundary_values(self):
        """実機カメラストリーミング - 境界値・品質テスト"""
        # ストリーミング開始・停止の実機動作
        # 画像品質: 解像度・フレームレート確認
        # 境界値: 長時間ストリーミング安定性
        # 通信品質: WiFi遅延による画像遅延
        # 実機特有: カメラハードウェア性能限界
        # Pi処理: 実機画像のリアルタイム処理負荷
        
    def test_real_drone_photo_capture_boundary_values(self):
        """実機写真撮影 - 境界値・品質テスト"""
        # 写真撮影機能の実機動作確認
        # 画像品質: 解像度・色精度確認
        # ファイルサイズ: 実機画像データ量
        # 保存時間: Pi環境での保存処理性能
        # 境界値: 連続撮影時の処理限界
        
    def test_real_drone_image_processing_boundary_values(self):
        """実機画像処理 - 境界値・AI処理テスト"""
        # 実機画像での物体認識処理
        # AI処理: 実環境での認識精度
        # 境界値: 認識可能距離・角度
        # Pi負荷: 実機画像でのAI処理負荷
        # 実時間: リアルタイム処理可能性
```

### 5. **実機追跡・ミッションパッドテスト**

#### 新規テストファイル: `test_real_drone_advanced_integration.py`

```python
"""
実機Tello EDU高度機能統合テスト
"""

class TestRealDroneAdvancedIntegration:
    
    def test_real_drone_tracking_boundary_values(self):
        """実機追跡機能 - 境界値・精度テスト"""
        # 実物体の追跡処理確認
        # 追跡精度: 中心維持・距離維持
        # 境界値: 追跡可能対象サイズ
        # 境界値: 追跡可能距離範囲
        # 実機制御: 追跡時の移動制御精度
        # 環境変化: 照明・背景変化への対応
        
    def test_real_drone_mission_pad_boundary_values(self):
        """実機ミッションパッド - 境界値・認識テスト"""
        # 実ミッションパッドの認識処理
        # 認識精度: パッドID・位置認識
        # 境界値: 認識可能距離・角度
        # 飛行制御: パッド基準の正確な移動
        # 実機特有: カメラ角度・照明による影響
        
    def test_real_drone_curve_flight_boundary_values(self):
        """実機カーブ飛行 - 境界値・軌道テスト"""
        # カーブ飛行の実機実行確認
        # 軌道精度: 設定軌道vs実飛行軌道
        # 境界値: カーブ半径・角度制限
        # 実機制御: 複雑な3D軌道制御精度
        # 物理法則: 慣性・重力の影響確認
```

## 実機テスト固有の検証項目

### 1. **物理的制約・精度検証**
```python
class TestPhysicalConstraints:
    
    def test_gravity_wind_effects(self):
        """重力・風の影響テスト"""
        # 静止ホバリング時のドリフト測定
        # 風による移動精度への影響
        # 重力による高度変化測定
        
    def test_battery_consumption_patterns(self):
        """バッテリー消費パターンテスト"""
        # 各動作でのバッテリー消費量
        # 連続飛行可能時間測定
        # 低バッテリー時の動作制限
        
    def test_hardware_limits(self):
        """ハードウェア限界テスト"""
        # 最大速度・加速度測定
        # 連続動作時間限界
        # 温度による性能変化
```

### 2. **安全性・信頼性検証**
```python
class TestSafetyReliability:
    
    def test_failsafe_mechanisms(self):
        """フェイルセーフ機構テスト"""
        # 通信断絶時の自動着陸
        # 低バッテリー時の安全制御
        # 境界領域超過時の自動停止
        
    def test_error_recovery(self):
        """エラー復旧機能テスト"""
        # 一時的通信エラーからの復旧
        # センサーエラー時の代替制御
        # 予期しない状況での安全停止
```

## 実行環境・手順

### テスト実行前準備
```bash
# 実機環境変数設定
export USE_REAL_DRONE=true
export DRONE_TYPE=tello_edu
export SAFETY_MODE=enabled
export MAX_FLIGHT_HEIGHT=150

# 安全設定確認
python -c "from config.safety import check_safety_environment; check_safety_environment()"
```

### 段階的テスト実行
```bash
# Stage 1: 基本機能テスト (地上)
python -m pytest test_real_drone_connection_integration.py -v

# Stage 2: 基本飛行テスト (安全高度)
python -m pytest test_real_drone_flight_integration.py -v --max-height=100

# Stage 3: 移動・センサーテスト
python -m pytest test_real_drone_movement_integration.py -v --safety-bounds

# Stage 4: 高度機能テスト
python -m pytest test_real_drone_advanced_integration.py -v --supervised
```

## 成功基準

### 基本動作基準
- 実機接続・切断: 100%成功率
- 離陸・着陸: 100%成功率 (安全確保)
- 緊急停止: 1秒以内応答
- 移動精度: ±5cm以内
- 回転精度: ±3度以内

### 安全性基準
- バッテリー監視: 常時20%以上維持
- 飛行範囲: 設定境界内100%維持
- 通信品質: 95%以上の信号品質維持
- エラー復旧: 全エラーケースでの安全着陸

### 性能基準
- カメラFPS: 30fps安定維持
- 追跡精度: 対象中心±10pixel以内
- AI処理遅延: 100ms以内
- 総合飛行時間: 15分以上連続動作

## 実機テスト特有のリスク管理

### High Risk項目
- プロペラ回転中の安全確保
- バッテリー切れによる墜落防止
- 通信断絶時の自動制御
- 予期しない障害物回避

### Medium Risk項目
- カメラ画質の環境依存性
- WiFi干渉による通信品質低下
- センサー精度の個体差
- 長時間飛行時の温度上昇

### Risk Mitigation Strategy
- 全テスト時の監視員配置
- 緊急停止装置の常時準備
- バッテリー残量の厳格管理
- テスト環境の安全確保