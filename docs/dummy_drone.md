# Tello EDU ダミーシステム設計

## 概要

Tello EDU実機なしでシステムを設計・開発するためのダミードローンシステムの設計書。

## 1. Tello EDU モック対象インターフェース分析

### djitellopy ライブラリの主要機能

```python
# 飛行制御
tello.takeoff()
tello.land()
tello.move_forward(30)
tello.rotate_clockwise(90)

# カメラ・ストリーミング
tello.streamon()
frame_reader = tello.get_frame_read()
cv_img = frame_reader.frame

# テレメトリ
battery = tello.get_battery()
height = tello.get_height()
speed = tello.get_speed_x()
```

## 2. ダミードローンアーキテクチャ設計

### コア設計方針

1. **djitellopyインターフェース完全互換**: 既存コードの変更を最小限に
2. **リアルタイム動作シミュレーション**: 実際の飛行時間やカメラフレームレートを再現
3. **設定可能な動作パターン**: テストシナリオに応じてカスタマイズ可能
4. **複数ドローンサポート**: 異なるIPアドレスで複数インスタンス起動

### 3つのレイヤー構成

#### Layer 1: djitellopy Mock Layer (`DummyTello`)

```python
class DummyTello:
    """djitellopy.Tello完全互換のモッククラス"""
    def __init__(self, host='192.168.0.100'):
        self.virtual_position = [0, 0, 0]  # x, y, z
        self.virtual_rotation = [0, 0, 0]  # pitch, roll, yaw
        self.battery_level = 100
        self.is_flying = False
        self.camera_stream = DummyCameraStream()
    
    def takeoff(self): 
        # 5秒の離陸シミュレーション
        self.is_flying = True
        
    def move_forward(self, distance):
        # 実際の移動時間を計算してsleep
        self.virtual_position[1] += distance
```

#### Layer 2: Virtual Environment Layer (`DroneSimulator`)

```python
class DroneSimulator:
    """3D空間でのドローン物理シミュレーション"""
    def __init__(self):
        self.virtual_world = Virtual3DSpace()
        self.objects = []  # 追跡対象オブジェクト
        self.obstacles = []  # 障害物
    
    def add_tracking_object(self, obj_model, position):
        """追跡対象をシミュレーション空間に配置"""
        
    def simulate_camera_view(self):
        """ドローンの現在位置から見える映像を生成"""
```

#### Layer 3: Content Generation Layer (`VirtualCameraStream`)

- **静的画像モード**: テスト用の固定画像セット
- **動的生成モード**: OpenCVで追跡対象を合成した映像
- **録画再生モード**: 実際のTello映像を録画して再生

## 3. 実装方針

### A. 段階的実装アプローチ

1. **Phase 1**: 基本djitellopy互換レイヤー（静的画像）
2. **Phase 2**: 動的カメラストリーム生成
3. **Phase 3**: 物理シミュレーション追加

### B. 設定ファイルドリブン

```yaml
# dummy_drone_config.yaml
dummy_drones:
  - ip: "192.168.0.100"
    name: "test_drone_1"
    camera_mode: "static_images"
    image_folder: "tests/fixtures/camera_images/"
    
  - ip: "192.168.0.101" 
    name: "test_drone_2"
    camera_mode: "dynamic_generation"
    tracking_objects:
      - type: "person"
        initial_position: [100, 200, 0]
        movement_pattern: "random_walk"
```

### C. システム統合ポイント

```python
# backend/src/core/drone_control.py
def create_drone_connection(ip_address):
    if is_dummy_mode() or not is_real_drone_available(ip_address):
        return DummyTello(ip_address)
    else:
        return djitellopy.Tello(ip_address)
```

## 4. テスト戦略

### 単体テスト

- djitellopy APIの全メソッド互換性テスト
- 各種エラーケース（バッテリー切れ、通信断等）

### 結合テスト

- 物体追跡アルゴリズムのテスト（固定パターン画像で検証）
- 複数ドローン制御のテスト
- 緊急停止機能のテスト

### システムテスト

- 実機テストと同じシナリオをダミーで実行
- 長時間動作テスト（メモリリーク等の確認）

## 5. 開発メリット

### 開発効率

- **実機不要**: ハードウェアなしで全機能テスト可能
- **再現性**: 同じテストケースを何度でも実行
- **並列開発**: 複数の開発者が同時にテスト可能

### テスト品質

- **エッジケース**: バッテリー切れや通信断などの異常系を確実にテスト
- **自動化**: CI/CDパイプラインに組み込み可能
- **デバッグ**: ドローンの内部状態を完全に制御・観測可能

## 6. 推奨実装順序

1. **`backend/src/core/dummy_drone.py`**: DummyTelloクラス（Phase 1）
2. **`backend/tests/fixtures/`**: テスト用画像・映像データ
3. **`backend/src/config/dummy_config.yaml`**: ダミードローン設定
4. **`backend/src/core/drone_factory.py`**: 実機/ダミー切り替えロジック

## 7. ファイル構成

```
backend/
├── src/
│   ├── core/
│   │   ├── dummy_drone.py          # DummyTelloクラス
│   │   ├── drone_simulator.py      # 物理シミュレーション
│   │   ├── virtual_camera.py       # カメラストリーム生成
│   │   └── drone_factory.py        # 実機/ダミー切り替え
│   └── config/
│       └── dummy_config.yaml       # ダミードローン設定
├── tests/
│   ├── fixtures/
│   │   ├── camera_images/          # テスト用静的画像
│   │   └── camera_videos/          # テスト用映像
│   └── unit/
│       └── test_dummy_drone.py     # ダミードローンテスト
```

この設計により、実機なしでの完全な開発・テスト環境が構築でき、品質の高いドローン制御システムが開発できます。