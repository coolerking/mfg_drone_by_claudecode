# 単体テスト設計書

## テスト方針

### 基本方針
- **独立性**: ドローン実機やバックエンドサーバーなしで実行可能
- **網羅性**: 全パブリック関数をテスト、境界値・異常系を含む
- **自動化**: CI/CDパイプラインでの自動実行が可能
- **保守性**: テストコードも保守しやすい構造

### テスト対象

#### DroneAPIClient クラス
- **基本機能**: 初期化、リクエスト処理、ヘルスチェック
- **接続管理**: connect_drone, disconnect_drone
- **飛行制御**: takeoff, land, emergency_stop
- **基本移動**: move_*, rotate, flip
- **高度移動**: go_xyz, curve_xyz, rc_control
- **カメラ**: start_video_stream, stop_video_stream, take_photo, start_recording, stop_recording
- **センサー**: get_battery, get_altitude, get_temperature, get_attitude, get_velocity
- **設定**: set_wifi, set_speed, send_command
- **ミッションパッド**: enable_mission_pad, disable_mission_pad, set_detection_direction, go_to_mission_pad, get_mission_pad_status
- **追跡**: start_tracking, stop_tracking, get_tracking_status
- **モデル**: get_model_list, delete_model

#### Flask ルートハンドラ
- **基本ルート**: /, /health
- **ドローン制御**: /api/drone/*
- **移動制御**: /api/drone/move/*, /api/drone/rotate, /api/drone/go_xyz, /api/drone/curve_xyz, /api/drone/rc_control
- **センサー**: /api/sensors/all, /api/drone/battery, /api/drone/altitude, /api/drone/temperature, /api/drone/attitude
- **カメラ**: /api/camera/*
- **ミッションパッド**: /api/mission_pad/*
- **追跡**: /api/tracking/*
- **モデル**: /api/model/*
- **設定**: /api/settings/*
- **エラーハンドラ**: 404, 500, 503

### テストケース設計

#### 正常系テスト
- **期待される引数での動作確認**
- **デフォルト値での動作確認**
- **境界値での動作確認**
  - 最小値・最大値
  - 空文字列・None値

#### 異常系テスト
- **範囲外の引数値**
- **不正な引数タイプ**
- **必須パラメータの欠如**
- **HTTPエラーレスポンス**
- **ネットワークエラー**

#### エラーハンドリングテスト
- **例外処理の動作確認**
- **エラーメッセージの検証**
- **ログ出力の確認**

### モック設計

#### BackendAPIMock
- **全APIエンドポイントのシミュレーション**
- **成功レスポンスの提供**
- **失敗モードの設定**
- **リクエスト履歴の追跡**

#### MockResponse
- **HTTP レスポンスのシミュレーション**
- **ステータスコード・レスポンスボディの設定**
- **ストリーミングコンテンツの対応**

### テストデータ

#### 境界値データ
```python
# 距離・速度の境界値
DISTANCE_VALUES = [20, 30, 50, 100, 500]  # min, default, normal, high, max
SPEED_VALUES = [10, 30, 50, 60, 100]      # min, normal, normal, high, max
ANGLE_VALUES = [1, 90, 180, 270, 360]     # min, normal, normal, normal, max

# 座標の境界値
COORDINATE_VALUES = [-500, -100, 0, 100, 500]  # min, low, center, high, max

# WiFi設定の境界値
SSID_VALUES = ["A", "TestSSID", "A" * 32]      # min, normal, max
PASSWORD_VALUES = ["12345678", "TestPass", "A" * 63]  # min, normal, max

# 速度設定の境界値
FLIGHT_SPEED_VALUES = [1.0, 5.0, 10.0, 15.0]  # min, normal, high, max
```

#### エラーシナリオ
```python
# HTTP エラー
HTTP_ERRORS = [400, 401, 403, 404, 500, 502, 503, 504]

# ネットワークエラー
NETWORK_ERRORS = [
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.RequestException
]
```

### カバレッジ目標

- **ライン カバレッジ**: 85% 以上
- **ブランチ カバレッジ**: 80% 以上
- **関数 カバレッジ**: 100%

### テスト実行環境

#### 必要な依存関係
- pytest >= 7.4.3
- pytest-cov >= 4.1.0
- pytest-mock >= 3.12.0
- pytest-html >= 4.1.1
- requests >= 2.31.0
- flask (main.py の依存関係)

#### 実行環境要件
- Python 3.11+
- ローカル実行のみ
- 外部ネットワーク接続不要
- ドローンハードウェア不要
- バックエンドサーバー不要

### CI/CD 統合

#### 自動テスト実行
- プルリクエスト作成時
- メインブランチへのマージ時
- 定期実行（日次）

#### テスト結果の報告
- HTMLレポートの生成
- カバレッジレポートの生成
- テスト失敗時の通知

### 保守・改善計画

#### 定期的な見直し
- テストケースの追加・削除
- モックデータの更新
- カバレッジ目標の見直し

#### 品質向上
- テストコードのリファクタリング
- パフォーマンステストの追加
- セキュリティテストの検討