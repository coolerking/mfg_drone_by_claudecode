# Tello EDU実機ドローントラブルシューティングガイド

## 概要
このガイドでは、Tello EDU実機ドローンの接続・制御・カメラ操作で発生する一般的な問題と解決方法を説明します。

## 1. 接続問題

### 1.1 WiFi接続失敗

**症状:**
- ドローンが検出されない
- `Connection timeout` エラー
- `No route to host` エラー

**原因と解決方法:**

#### ドローンが起動していない
```bash
# 対処法
1. ドローンの電源ボタンを押して起動
2. LEDが点滅から点灯に変わるまで待機（約30秒）
3. WiFi設定でTello-XXXXXXネットワークを確認
```

#### WiFiパスワード問題
```bash
# 対処法
1. Tello EDUのデフォルトパスワードを確認
2. 一般的なパスワード: なし、または機体に記載
3. WiFi設定を削除して再接続
```

#### IPアドレス競合
```bash
# 問題確認
ping 192.168.10.1

# 対処法
1. ネットワーク設定をリセット
2. 他のTelloが同一ネットワークにないか確認
3. ルーター再起動
```

### 1.2 自動検出失敗

**症状:**
- スキャンでドローンが見つからない
- `scan_for_real_drones`が空の結果を返す

**診断手順:**
```bash
# 手動接続テスト
curl -X POST http://localhost:8000/api/drones/verify_connection \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.10.1"}'

# ネットワーク状態確認
curl -X GET http://localhost:8000/api/system/network_status
```

**解決方法:**
```yaml
# config/drone_config.yaml
drones:
  - id: "manual_tello_001"
    name: "Manual Tello #1"
    mode: "real"
    ip_address: "192.168.10.1"  # 手動指定
    auto_detect: false          # 自動検出無効
```

### 1.3 接続タイムアウト

**設定調整:**
```bash
# 環境変数
export TELLO_CONNECTION_TIMEOUT=30
export TELLO_RETRY_COUNT=3
export TELLO_RETRY_DELAY=5
```

```yaml
# config/drone_config.yaml
global:
  connection_timeout: 30
  max_retries: 3
  retry_delay: 5
```

## 2. 制御問題

### 2.1 コマンド応答なし

**症状:**
- takeoff/land コマンドが無視される
- 移動コマンドが実行されない
- `Command failed` エラー

**診断手順:**
```python
# Python診断スクリプト
import djitellopy

tello = djitellopy.Tello()
tello.connect()

# 基本テスト
print(f"Battery: {tello.get_battery()}")
print(f"Temperature: {tello.get_temperature()}")

# コマンドテスト
response = tello.send_command_with_return("command")
print(f"Command response: {response}")
```

**解決方法:**

#### バッテリー不足
```bash
# 対処法
1. バッテリー残量確認（最低20%必要）
2. 充電後に再試行
3. 予備バッテリーへの交換
```

#### フライト制限モード
```bash
# 対処法
1. 屋内での使用を確認
2. プロペラガードの装着
3. 十分な飛行スペースの確保（3m x 3m以上）
```

#### SDK接続失敗
```python
# 修復手順
def reset_tello_connection():
    try:
        tello = djitellopy.Tello()
        tello.connect()
        tello.end()  # 接続終了
        time.sleep(2)
        tello.connect()  # 再接続
        return tello
    except Exception as e:
        print(f"Reset failed: {e}")
        return None
```

### 2.2 飛行制御異常

**症状:**
- ドリフト（意図しない移動）
- 高度維持困難
- 回転制御不安定

**キャリブレーション手順:**
```bash
# IMUキャリブレーション
1. 平らな面にドローンを置く
2. 電源オン後30秒待機
3. 自動キャリブレーション完了まで待機
4. LEDが安定点灯することを確認
```

**環境要因の確認:**
```bash
# チェック項目
□ 強い光源（直射日光、ライト）の回避
□ 風のない環境
□ 反射面（鏡、ガラス）の回避
□ WiFi干渉の確認（2.4GHz帯）
```

### 2.3 位置精度問題

**VPS（Vision Positioning System）最適化:**
```bash
# 推奨環境
- 地面にパターンや模様がある
- 照明が十分（暗すぎない）
- 高さ0.5m〜10m
- 地面が平坦
```

**設定調整:**
```yaml
# config/drone_config.yaml
real_drones:
  - id: "tello_001"
    positioning_mode: "vps"  # GPS, VPS, or hybrid
    flight_limits:
      max_height: 500        # cm
      max_distance: 1000     # cm
      max_speed: 100         # cm/s
```

## 3. カメラストリーム問題

### 3.1 ストリーム開始失敗

**症状:**
- カメラ映像が表示されない
- `Stream not available` エラー
- 接続後にストリームが停止

**診断コマンド:**
```bash
# ffmpeg でストリーム確認
ffmpeg -i udp://192.168.10.1:11111 -t 10 test_stream.mp4

# VLC での確認
vlc udp://@:11111
```

**解決方法:**

#### UDP ポート競合
```bash
# ポート使用状況確認
netstat -an | grep 11111
lsof -i :11111

# 競合プロセス終了
sudo kill -9 <PID>
```

#### ファイアウォール設定
```bash
# Ubuntu/Debian
sudo ufw allow 11111/udp
sudo ufw allow 8889/udp

# CentOS/RHEL
sudo firewall-cmd --add-port=11111/udp --permanent
sudo firewall-cmd --add-port=8889/udp --permanent
sudo firewall-cmd --reload
```

### 3.2 フレーム取得エラー

**症状:**
- フレームが空（None）
- 画像が破損
- フレームレート低下

**OpenCV 設定最適化:**
```python
# 推奨設定
import cv2

cap = cv2.VideoCapture('udp://192.168.10.1:11111')
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # バッファサイズ最小化
cap.set(cv2.CAP_PROP_FPS, 30)        # フレームレート設定
```

**フレーム処理最適化:**
```python
# 非同期フレーム取得
import asyncio
import threading
from queue import Queue

class AsyncFrameCapture:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame_queue = Queue(maxsize=2)
        self.running = False
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()
    
    def _capture_loop(self):
        cap = cv2.VideoCapture(self.stream_url)
        while self.running:
            ret, frame = cap.read()
            if ret:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
    
    def get_frame(self):
        return self.frame_queue.get() if not self.frame_queue.empty() else None
```

### 3.3 ビジョンAPI統合問題

**症状:**
- 物体検出が機能しない
- 追跡が開始されない
- カメラ初期化失敗

**統合テスト:**
```python
# 統合テストスクリプト
async def test_vision_integration():
    from api_server.core.drone_manager import DroneManager
    from api_server.core.vision_service import VisionService
    
    drone_manager = DroneManager()
    vision_service = VisionService()
    vision_service.set_drone_manager(drone_manager)
    
    # ドローン接続
    await drone_manager.connect_drone("tello_001")
    
    # カメラ初期化
    success = await vision_service.initialize_drone_camera("tello_001")
    print(f"Camera initialization: {success}")
    
    # 物体検出テスト
    if success:
        result = await vision_service.detect_objects_from_drone_camera(
            "tello_001", "yolo_v8_general", 0.5
        )
        print(f"Detections: {len(result.detections)}")
```

## 4. 性能問題

### 4.1 応答時間の遅延

**症状:**
- コマンド実行が遅い
- ストリーム遅延が大きい
- APIレスポンス遅延

**ネットワーク最適化:**
```bash
# WiFi設定最適化
1. 2.4GHz専用接続
2. チャンネル1, 6, 11 を選択
3. 他の2.4GHzデバイスを無効化
4. ルーターとの距離を最小化（5m以内）
```

**システム設定:**
```bash
# CPU使用率監視
htop

# メモリ使用量確認
free -h

# ネットワーク遅延測定
ping -c 10 192.168.10.1
```

### 4.2 メモリリーク

**症状:**
- 長時間使用でメモリ使用量増加
- システムが重くなる
- プロセスクラッシュ

**監視・対策:**
```python
# メモリ監視
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # ガベージコレクション強制実行
    gc.collect()

# 定期実行
import schedule
schedule.every(10).minutes.do(monitor_memory)
```

## 5. エラーコード対応表

### システムエラー
| エラーコード | 説明 | 対処法 |
|-------------|------|--------|
| CONN_001 | 接続タイムアウト | WiFi確認、ドローン再起動 |
| CONN_002 | IPアドレス到達不可 | ネットワーク設定確認 |
| CONN_003 | 認証失敗 | WiFiパスワード確認 |
| BATT_001 | バッテリー不足 | 充電または交換 |
| CMD_001 | コマンド実行失敗 | ドローン状態確認 |
| CAM_001 | カメラ初期化失敗 | ストリーム設定確認 |
| CAM_002 | フレーム取得失敗 | UDP設定確認 |

### ドローン状態エラー
| 状態 | 説明 | 対処法 |
|------|------|--------|
| emergency | 緊急停止状態 | 手動リセット、再起動 |
| error | システムエラー | ドローン再起動 |
| low_battery | バッテリー警告 | 即座に着陸、充電 |
| motor_error | モーター異常 | プロペラ確認、再起動 |

## 6. ログ分析

### ログレベル設定
```python
# config/logging.conf
[logger_tello]
level=DEBUG
handlers=file_handler
qualname=tello_edu_controller

[logger_vision]
level=INFO
handlers=file_handler
qualname=vision_service
```

### 重要なログパターン
```bash
# 接続成功
"Real drone tello_001 connected at 192.168.10.1"

# 接続失敗
"Failed to connect to Tello at 192.168.10.1: timeout"

# カメラ問題
"Error in frame capture loop: No frame received"

# バッテリー警告
"Battery level critical: 15%"
```

## 7. 開発者向けデバッグ

### デバッグモード有効化
```bash
# 環境変数
export TELLO_DEBUG=true
export VISION_DEBUG=true
export LOG_LEVEL=DEBUG
```

### 詳細診断ツール
```python
# 診断スクリプト
async def comprehensive_diagnosis():
    """包括的診断スクリプト"""
    
    # ネットワーク診断
    print("=== Network Diagnosis ===")
    network_status = await drone_manager.get_network_status()
    print(json.dumps(network_status, indent=2))
    
    # ドローン接続診断
    print("=== Drone Connection Diagnosis ===")
    verification = await drone_manager.verify_real_drone_connection("192.168.10.1")
    print(json.dumps(verification, indent=2))
    
    # カメラ診断
    print("=== Camera Diagnosis ===")
    camera_status = await vision_service.get_camera_status("tello_001")
    print(json.dumps(camera_status, indent=2))
    
    # システム状態
    print("=== System Status ===")
    system_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict()
    }
    print(json.dumps(system_info, indent=2))
```

## 8. 緊急時対応

### 緊急停止手順
```bash
# 即座にドローンを停止
curl -X POST http://localhost:8000/api/drones/tello_001/emergency_stop

# 全ドローン緊急停止
curl -X POST http://localhost:8000/api/system/emergency_stop_all
```

### システム復旧手順
```bash
# 1. サービス停止
sudo systemctl stop drone_backend

# 2. プロセス確認・終了
ps aux | grep python
sudo kill -9 <PID>

# 3. ネットワークリセット
sudo systemctl restart networking

# 4. サービス再起動
sudo systemctl start drone_backend

# 5. 健全性確認
curl -X GET http://localhost:8000/health
```

## 9. 予防保守

### 定期チェック項目
```bash
# 週次チェック
□ バッテリー状態確認
□ プロペラ損傷確認
□ ファームウェア更新確認
□ WiFi信号強度測定
□ ログファイル容量確認

# 月次チェック
□ システム全体更新
□ 設定ファイルバックアップ
□ 性能ベンチマーク実行
□ セキュリティ設定確認
```

### 自動監視設定
```python
# 監視スクリプト
import schedule
import time

def health_check():
    """定期健全性チェック"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            alert_admin("Health check failed")
    except Exception as e:
        alert_admin(f"Health check error: {e}")

schedule.every(5).minutes.do(health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 関連リンク
- [Tello EDU公式ドキュメント](https://www.ryzerobotics.com/tello-edu)
- [djitellopy GitHub](https://github.com/damiafuentes/DJITelloPy)
- [ネットワーク設定ガイド](./network_configuration_guide.md)
- [API仕様書](./real_drone_api_specification.md)