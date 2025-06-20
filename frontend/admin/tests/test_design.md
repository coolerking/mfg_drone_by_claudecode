# 管理用フロントエンドサーバ単体テスト設計書

## テスト対象関数一覧

### 1. DroneAPIClient クラス
**初期化・基本機能**
- `__init__(base_url: str = BACKEND_API_URL)` - APIクライアント初期化
- `_make_request(method: str, endpoint: str, data: Optional[Dict] = None)` - HTTP リクエスト基盤

**ヘルスチェック**
- `health_check()` - バックエンドサーバーのヘルスチェック

**ドローン接続管理**
- `connect_drone()` - ドローン接続開始
- `disconnect_drone()` - ドローン接続終了

**基本飛行制御**
- `takeoff()` - 離陸
- `land()` - 着陸
- `emergency_stop()` - 緊急停止

**基本移動制御**
- `move_forward(distance: int)` - 前進
- `move_backward(distance: int)` - 後退
- `move_left(distance: int)` - 左移動
- `move_right(distance: int)` - 右移動
- `move_up(distance: int)` - 上昇
- `move_down(distance: int)` - 下降
- `rotate(direction: str, angle: int)` - 回転
- `flip(direction: str)` - フリップ

**高度移動制御**
- `go_xyz(x: int, y: int, z: int, speed: int)` - 3D座標移動
- `curve_xyz(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int)` - 曲線飛行
- `rc_control(left_right: int, forward_backward: int, up_down: int, yaw: int)` - リアルタイム制御

**カメラ操作**
- `start_video_stream()` - ビデオストリーミング開始
- `stop_video_stream()` - ビデオストリーミング停止
- `take_photo()` - 写真撮影
- `start_recording()` - 録画開始
- `stop_recording()` - 録画停止

**センサーデータ**
- `get_battery()` - バッテリー残量取得
- `get_altitude()` - 高度取得
- `get_temperature()` - 温度取得
- `get_attitude()` - 姿勢情報取得
- `get_velocity()` - 速度情報取得

**WiFi・設定**
- `set_wifi(ssid: str, password: str)` - WiFi設定
- `set_speed(speed: float)` - 飛行速度設定
- `send_command(command: str, timeout: int = 7)` - カスタムコマンド送信

**ミッションパッド**
- `enable_mission_pad()` - ミッションパッド有効化
- `disable_mission_pad()` - ミッションパッド無効化
- `set_detection_direction(direction: int)` - 検出方向設定
- `go_to_mission_pad(x: int, y: int, z: int, speed: int, pad_id: int)` - ミッションパッドへの移動
- `get_mission_pad_status()` - ミッションパッドステータス取得

**物体追跡**
- `start_tracking(target_object: str, tracking_mode: str = 'center')` - 物体追跡開始
- `stop_tracking()` - 物体追跡停止
- `get_tracking_status()` - 追跡ステータス取得

**モデル管理**
- `get_model_list()` - モデル一覧取得
- `delete_model(model_name: str)` - モデル削除

### 2. Flask ルートハンドラ関数

**基本ページ**
- `index()` - メインページ表示
- `health_check()` - フロントエンドヘルスチェック

**ドローン制御 API プロキシ**
- `connect_drone()` - 接続プロキシ
- `disconnect_drone()` - 切断プロキシ
- `takeoff()` - 離陸プロキシ
- `land()` - 着陸プロキシ
- `emergency_stop()` - 緊急停止プロキシ
- `move_drone(direction)` - 移動プロキシ
- `rotate_drone()` - 回転プロキシ
- `go_xyz()` - 3D移動プロキシ
- `curve_xyz()` - 曲線飛行プロキシ
- `rc_control()` - リアルタイム制御プロキシ

**センサーデータ API**
- `get_all_sensors()` - 全センサーデータ取得
- `get_battery()` - バッテリー取得プロキシ
- `get_altitude()` - 高度取得プロキシ
- `get_temperature()` - 温度取得プロキシ
- `get_attitude()` - 姿勢取得プロキシ

**カメラ制御 API**
- `start_video_stream()` - ストリーミング開始プロキシ
- `stop_video_stream()` - ストリーミング停止プロキシ
- `take_photo()` - 写真撮影プロキシ
- `start_recording()` - 録画開始プロキシ
- `stop_recording()` - 録画停止プロキシ
- `video_stream()` - ビデオストリーミングプロキシ

**ミッションパッド API**
- `enable_mission_pad()` - ミッションパッド有効化プロキシ
- `disable_mission_pad()` - ミッションパッド無効化プロキシ
- `set_detection_direction()` - 検出方向設定プロキシ
- `go_to_mission_pad()` - ミッションパッド移動プロキシ
- `get_mission_pad_status()` - ステータス取得プロキシ

**物体追跡 API**
- `start_tracking()` - 追跡開始プロキシ
- `stop_tracking()` - 追跡停止プロキシ
- `get_tracking_status()` - 追跡ステータスプロキシ

**モデル管理 API**
- `train_model()` - モデル訓練プロキシ
- `get_model_list()` - モデル一覧プロキシ
- `delete_model(model_name)` - モデル削除プロキシ

**設定管理 API**
- `set_wifi_settings()` - WiFi設定プロキシ
- `set_flight_speed()` - 飛行速度設定プロキシ
- `send_custom_command()` - カスタムコマンドプロキシ

### 3. エラーハンドラ関数
- `not_found(error)` - 404エラーハンドラ
- `internal_error(error)` - 500エラーハンドラ
- `service_unavailable(error)` - 503エラーハンドラ

## テストケース設計方針

### 1. 正常系テスト
- **境界値テスト**: 引数の最小値・最大値での動作確認
- **中間値テスト**: 引数の典型的な値での動作確認
- **デフォルト値テスト**: オプション引数のデフォルト値テスト

### 2. 異常系テスト
- **範囲外値テスト**: 引数の範囲外値でのエラーハンドリング確認
- **不正型テスト**: 不正な型の引数でのエラーハンドリング確認
- **None値テスト**: None値での動作確認

### 3. エラーハンドリングテスト
- **ネットワークエラー**: requests.exceptions.RequestException のシミュレーション
- **HTTPエラー**: 各種HTTPステータスコード（4xx, 5xx）のレスポンス処理確認
- **タイムアウトエラー**: 接続タイムアウト・読み取りタイムアウトの処理確認

## モック戦略

### 1. requests モジュールのモック
- `requests.Session` クラスをモック化
- 各HTTPメソッド（GET, POST, PUT, DELETE）のレスポンスを制御
- 成功・失敗・タイムアウトのシナリオをシミュレーション

### 2. Flask アプリケーションテスト
- `app.test_client()` を使用したテストクライアント
- APIクライアントの依存性注入によるモック化
- リクエスト・レスポンスの詳細検証

### 3. 外部依存関係の分離
- 環境変数のモック化（`os.environ`）
- ファイルシステム操作のモック化（必要に応じて）

## カバレッジ目標
- **関数カバレッジ**: 100%（全ての公開関数をテスト）
- **ライン カバレッジ**: 90%以上
- **ブランチカバレッジ**: 85%以上