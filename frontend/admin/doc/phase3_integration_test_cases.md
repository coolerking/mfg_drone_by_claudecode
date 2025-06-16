# フェーズ3 結合テストケース仕様

## 概要

管理者用フロントエンドサーバのフェーズ3結合テストにおいて実装すべきテストケースを体系的に整理した文書です。

### テスト種別

1. **モックバックエンド結合テスト**: バックエンドサーバをモック化して実行するテスト
2. **実機バックエンド結合テスト**: 実際のバックエンドサーバ及びドローンを使用するテスト

---

## 1. モックバックエンド結合テストケース

### 1.1 システム・接続管理テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-SYS-001 | ヘルスチェック | GET /health | 正常なヘルスチェック呼び出し | 200 OK, {"status": "healthy"} | High | 30分 |
| MOCK-SYS-002 | ヘルスチェック | GET /health | ネットワークエラー時の処理 | Connection Error | High | 30分 |
| MOCK-CON-001 | ドローン接続 | POST /drone/connect | 正常な接続処理 | 200 OK, {"success": true} | High | 45分 |
| MOCK-CON-002 | ドローン接続 | POST /drone/connect | 接続失敗の処理 | 500 Error, {"error": "接続失敗"} | High | 45分 |
| MOCK-CON-003 | ドローン切断 | POST /drone/disconnect | 正常な切断処理 | 200 OK, {"success": true} | High | 30分 |
| MOCK-CON-004 | ドローン切断 | POST /drone/disconnect | 切断失敗の処理 | 500 Error, {"error": "切断失敗"} | Medium | 30分 |
| MOCK-CON-005 | 接続状態管理 | 複数API | 接続前後での状態変化確認 | 状態遷移の正確性 | High | 60分 |

### 1.2 基本飛行制御テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-FLT-001 | 離陸制御 | POST /drone/takeoff | 正常な離陸処理 | 200 OK, {"success": true} | High | 45分 |
| MOCK-FLT-002 | 離陸制御 | POST /drone/takeoff | 未接続時の離陸失敗 | 400 Error, {"error": "未接続"} | High | 30分 |
| MOCK-FLT-003 | 着陸制御 | POST /drone/land | 正常な着陸処理 | 200 OK, {"success": true} | High | 45分 |
| MOCK-FLT-004 | 着陸制御 | POST /drone/land | 非飛行時の着陸失敗 | 409 Error, {"error": "飛行中でない"} | High | 30分 |
| MOCK-FLT-005 | 緊急停止 | POST /drone/emergency | 緊急停止の正常実行 | 200 OK, {"success": true} | High | 30分 |
| MOCK-FLT-006 | 緊急停止 | POST /drone/emergency | 緊急停止失敗 | 500 Error, {"error": "緊急停止失敗"} | High | 30分 |
| MOCK-FLT-007 | ホバリング | POST /drone/stop | 正常なホバリング処理 | 200 OK, {"success": true} | Medium | 30分 |
| MOCK-FLT-008 | 飛行状態管理 | 複数API | 離陸→着陸フロー確認 | 状態遷移の正確性 | High | 90分 |

### 1.3 移動制御テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-MOV-001 | 基本移動 | POST /drone/move | 有効な方向・距離での移動 | 200 OK, {"success": true} | High | 45分 |
| MOCK-MOV-002 | 基本移動 | POST /drone/move | 無効な方向指定 | 400 Error, {"error": "無効な方向"} | High | 30分 |
| MOCK-MOV-003 | 基本移動 | POST /drone/move | 距離範囲外指定(20cm未満) | 400 Error, {"error": "距離範囲外"} | High | 30分 |
| MOCK-MOV-004 | 基本移動 | POST /drone/move | 距離範囲外指定(500cm超過) | 400 Error, {"error": "距離範囲外"} | High | 30分 |
| MOCK-MOV-005 | 基本移動 | POST /drone/move | 非飛行時の移動失敗 | 409 Error, {"error": "飛行中でない"} | High | 30分 |
| MOCK-MOV-006 | 回転制御 | POST /drone/rotate | 時計回り回転 | 200 OK, {"success": true} | High | 30分 |
| MOCK-MOV-007 | 回転制御 | POST /drone/rotate | 反時計回り回転 | 200 OK, {"success": true} | High | 30分 |
| MOCK-MOV-008 | 回転制御 | POST /drone/rotate | 無効な角度指定(0度以下) | 400 Error, {"error": "無効な角度"} | Medium | 30分 |
| MOCK-MOV-009 | 回転制御 | POST /drone/rotate | 無効な角度指定(360度超過) | 400 Error, {"error": "無効な角度"} | Medium | 30分 |
| MOCK-MOV-010 | 宙返り | POST /drone/flip | 各方向の宙返り | 200 OK, {"success": true} | Medium | 45分 |

### 1.4 高度移動制御テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-ADV-001 | 座標移動 | POST /drone/go_xyz | 有効なXYZ座標・速度指定 | 200 OK, {"success": true} | High | 60分 |
| MOCK-ADV-002 | 座標移動 | POST /drone/go_xyz | 座標範囲外指定 | 400 Error, {"error": "座標範囲外"} | High | 30分 |
| MOCK-ADV-003 | 座標移動 | POST /drone/go_xyz | 速度範囲外指定 | 400 Error, {"error": "速度範囲外"} | High | 30分 |
| MOCK-ADV-004 | 曲線飛行 | POST /drone/curve_xyz | 有効な中間点・終点指定 | 200 OK, {"success": true} | Medium | 60分 |
| MOCK-ADV-005 | 曲線飛行 | POST /drone/curve_xyz | 無効な座標範囲 | 400 Error, {"error": "座標範囲外"} | Medium | 30分 |
| MOCK-ADV-006 | リアルタイム制御 | POST /drone/rc_control | 有効な速度パラメータ | 200 OK, {"success": true} | Medium | 45分 |
| MOCK-ADV-007 | リアルタイム制御 | POST /drone/rc_control | 速度範囲外パラメータ | 400 Error, {"error": "速度範囲外"} | Medium | 30分 |

### 1.5 カメラ操作テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-CAM-001 | ストリーミング | POST /camera/stream/start | ストリーミング開始 | 200 OK, {"success": true} | High | 45分 |
| MOCK-CAM-002 | ストリーミング | POST /camera/stream/start | 既に開始済みの場合 | 409 Error, {"error": "開始済み"} | High | 30分 |
| MOCK-CAM-003 | ストリーミング | POST /camera/stream/start | ドローン未接続時 | 503 Error, {"error": "未接続"} | High | 30分 |
| MOCK-CAM-004 | ストリーミング | POST /camera/stream/stop | ストリーミング停止 | 200 OK, {"success": true} | High | 30分 |
| MOCK-CAM-005 | ストリーミング | GET /camera/stream | ストリーム取得 | 200 multipart/x-mixed-replace | High | 60分 |
| MOCK-CAM-006 | ストリーミング | GET /camera/stream | 未開始時のストリーム取得 | 404 Error, {"error": "未開始"} | High | 30分 |
| MOCK-CAM-007 | 写真撮影 | POST /camera/photo | 正常な撮影 | 200 OK, {"success": true} | High | 30分 |
| MOCK-CAM-008 | 動画録画 | POST /camera/video/start | 録画開始 | 200 OK, {"success": true} | High | 30分 |
| MOCK-CAM-009 | 動画録画 | POST /camera/video/stop | 録画停止 | 200 OK, {"success": true} | High | 30分 |
| MOCK-CAM-010 | カメラ設定 | PUT /camera/settings | 解像度・FPS・ビットレート変更 | 200 OK, {"success": true} | Medium | 45分 |
| MOCK-CAM-011 | カメラ設定 | PUT /camera/settings | 無効な設定値 | 400 Error, {"error": "無効な設定"} | Medium | 30分 |

### 1.6 センサー情報テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-SEN-001 | ドローン状態 | GET /drone/status | 接続中の状態取得 | 200 OK, 完全ステータス | High | 45分 |
| MOCK-SEN-002 | ドローン状態 | GET /drone/status | 未接続時の状態取得 | 503 Error, {"error": "未接続"} | High | 30分 |
| MOCK-SEN-003 | バッテリー | GET /drone/battery | バッテリー残量取得 | 200 OK, {"battery": 85} | High | 30分 |
| MOCK-SEN-004 | 高度 | GET /drone/height | 飛行高度取得 | 200 OK, {"height": 120} | High | 30分 |
| MOCK-SEN-005 | 温度 | GET /drone/temperature | ドローン温度取得 | 200 OK, {"temperature": 35} | Medium | 30分 |
| MOCK-SEN-006 | 飛行時間 | GET /drone/flight_time | 累積飛行時間取得 | 200 OK, {"flight_time": 1800} | Medium | 30分 |
| MOCK-SEN-007 | 気圧センサー | GET /drone/barometer | 気圧値取得 | 200 OK, {"barometer": 1013.25} | Medium | 30分 |
| MOCK-SEN-008 | ToFセンサー | GET /drone/distance_tof | 距離センサー値取得 | 200 OK, {"distance_tof": 850} | Medium | 30分 |
| MOCK-SEN-009 | 加速度 | GET /drone/acceleration | 加速度情報取得 | 200 OK, xyz軸加速度 | Medium | 30分 |
| MOCK-SEN-010 | 速度 | GET /drone/velocity | 速度情報取得 | 200 OK, xyz軸速度 | Medium | 30分 |
| MOCK-SEN-011 | 姿勢角 | GET /drone/attitude | 姿勢角情報取得 | 200 OK, pitch/roll/yaw | Medium | 30分 |

### 1.7 設定管理テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-SET-001 | WiFi設定 | PUT /drone/wifi | 有効なSSID・パスワード設定 | 200 OK, {"success": true} | Medium | 45分 |
| MOCK-SET-002 | WiFi設定 | PUT /drone/wifi | 無効なパラメータ | 400 Error, {"error": "無効なパラメータ"} | Medium | 30分 |
| MOCK-SET-003 | 任意コマンド | POST /drone/command | 有効なTello SDKコマンド | 200 OK, ドローンレスポンス | Low | 45分 |
| MOCK-SET-004 | 任意コマンド | POST /drone/command | コマンドタイムアウト | 408 Error, {"error": "タイムアウト"} | Low | 30分 |
| MOCK-SET-005 | 飛行速度設定 | PUT /drone/speed | 有効な速度設定 | 200 OK, {"success": true} | Medium | 30分 |
| MOCK-SET-006 | 飛行速度設定 | PUT /drone/speed | 速度範囲外設定 | 400 Error, {"error": "速度範囲外"} | Medium | 30分 |

### 1.8 ミッションパッドテスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-MIS-001 | パッド検出 | POST /mission_pad/enable | 検出有効化 | 200 OK, {"success": true} | Low | 30分 |
| MOCK-MIS-002 | パッド検出 | POST /mission_pad/disable | 検出無効化 | 200 OK, {"success": true} | Low | 30分 |
| MOCK-MIS-003 | 検出方向設定 | PUT /mission_pad/detection_direction | 各検出方向設定 | 200 OK, {"success": true} | Low | 30分 |
| MOCK-MIS-004 | パッド基準移動 | POST /mission_pad/go_xyz | 有効なパッドID・座標指定 | 200 OK, {"success": true} | Low | 45分 |
| MOCK-MIS-005 | パッド状態 | GET /mission_pad/status | パッド検出状態取得 | 200 OK, パッド情報 | Low | 30分 |

### 1.9 物体追跡テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-TRK-001 | 追跡開始 | POST /tracking/start | 有効なオブジェクト・モード指定 | 200 OK, {"success": true} | High | 45分 |
| MOCK-TRK-002 | 追跡開始 | POST /tracking/start | 無効なオブジェクト指定 | 400 Error, {"error": "無効なオブジェクト"} | High | 30分 |
| MOCK-TRK-003 | 追跡停止 | POST /tracking/stop | 追跡停止 | 200 OK, {"success": true} | High | 30分 |
| MOCK-TRK-004 | 追跡状態 | GET /tracking/status | 追跡中の状態取得 | 200 OK, 追跡情報 | High | 45分 |
| MOCK-TRK-005 | 追跡状態 | GET /tracking/status | 非追跡時の状態取得 | 200 OK, 非追跡状態 | High | 30分 |
| MOCK-TRK-006 | 追跡フロー | 複数API | 開始→監視→停止フロー | 状態遷移の正確性 | High | 90分 |

### 1.10 モデル管理テスト

| テストケースID | テストカテゴリ | API エンドポイント | テストシナリオ | 想定レスポンス | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-MOD-001 | モデル訓練 | POST /model/train | 有効な画像・オブジェクト名 | 200 OK, {"task_id": "xxx"} | High | 60分 |
| MOCK-MOD-002 | モデル訓練 | POST /model/train | 無効なパラメータ | 400 Error, {"error": "無効なパラメータ"} | High | 30分 |
| MOCK-MOD-003 | モデル訓練 | POST /model/train | ファイルサイズ過大 | 413 Error, {"error": "ファイル過大"} | High | 30分 |
| MOCK-MOD-004 | モデル一覧 | GET /model/list | 利用可能モデル取得 | 200 OK, モデル配列 | High | 30分 |
| MOCK-MOD-005 | モデル一覧 | GET /model/list | モデル未存在時 | 200 OK, 空配列 | Medium | 30分 |

### 1.11 WebSocket・リアルタイム通信テスト

| テストケースID | テストカテゴリ | 通信方式 | テストシナリオ | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| MOCK-WS-001 | WebSocket接続 | Socket.IO | 正常な接続・切断 | 接続・切断成功 | High | 60分 |
| MOCK-WS-002 | リアルタイム状態 | Socket.IO | センサーデータ配信 | 1秒間隔更新 | High | 90分 |
| MOCK-WS-003 | リアルタイム状態 | Socket.IO | 追跡状態配信 | リアルタイム追跡情報 | High | 90分 |
| MOCK-WS-004 | エラー処理 | Socket.IO | 接続断絶・復旧 | 自動再接続 | High | 60分 |
| MOCK-WS-005 | イベント処理 | Socket.IO | 複数イベント同期 | 正確なイベント配信 | Medium | 90分 |

---

## 2. 実機バックエンド結合テストケース

### 2.1 ドローン実機制御テスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-DRN-001 | 実機接続 | Tello EDU実機接続・切断 | 実機+バックエンド | 物理的接続確立 | High | 120分 |
| REAL-DRN-002 | 実機飛行 | 離陸→ホバリング→着陸 | 実機+バックエンド | 安全な飛行制御 | High | 180分 |
| REAL-DRN-003 | 実機移動 | 基本6方向移動 | 実機+バックエンド | 正確な移動制御 | High | 180分 |
| REAL-DRN-004 | 実機回転 | 時計回り・反時計回り回転 | 実機+バックエンド | 正確な回転制御 | High | 120分 |
| REAL-DRN-005 | 実機緊急停止 | 飛行中緊急停止 | 実機+バックエンド | 即座の安全停止 | High | 60分 |

### 2.2 実機カメラ・ストリーミングテスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-CAM-001 | 実機ストリーミング | ライブビデオストリーム取得 | 実機+バックエンド | リアルタイム映像配信 | High | 120分 |
| REAL-CAM-002 | 実機撮影 | 写真撮影・保存 | 実機+バックエンド | 画質確認・ファイル保存 | High | 90分 |
| REAL-CAM-003 | 実機録画 | 動画録画・保存 | 実機+バックエンド | 動画品質確認・ファイル保存 | High | 120分 |
| REAL-CAM-004 | カメラ設定 | 解像度・FPS変更 | 実機+バックエンド | 設定反映確認 | Medium | 90分 |

### 2.3 実機センサー・テレメトリテスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-SEN-001 | 実機センサー | 全センサー値取得・検証 | 実機+バックエンド | 現実的センサー値 | High | 120分 |
| REAL-SEN-002 | バッテリー監視 | 飛行中バッテリー消費監視 | 実機+バックエンド | 減少トレンド確認 | High | 90分 |
| REAL-SEN-003 | 高度センサー | 離陸・着陸高度変化 | 実機+バックエンド | 高度変化の正確性 | High | 90分 |
| REAL-SEN-004 | 姿勢センサー | 移動・回転時の姿勢変化 | 実機+バックエンド | 姿勢角の正確性 | Medium | 120分 |

### 2.4 実機物体追跡テスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-TRK-001 | 実機追跡 | 静止物体の検出・追跡 | 実機+バックエンド+対象物 | 対象物の正確な検出 | High | 180分 |
| REAL-TRK-002 | 実機追跡 | 移動物体の追従追跡 | 実機+バックエンド+対象物 | 移動物体への追従 | High | 240分 |
| REAL-TRK-003 | 実機追跡 | 中央維持モード | 実機+バックエンド+対象物 | 画面中央への位置制御 | High | 180分 |
| REAL-TRK-004 | 実機追跡 | 追従モード | 実機+バックエンド+対象物 | 対象物への能動的追従 | Medium | 240分 |
| REAL-TRK-005 | 実機追跡 | 対象物ロスト・再検出 | 実機+バックエンド+対象物 | ロスト検知・復旧処理 | Medium | 180分 |

### 2.5 実機モデル訓練・運用テスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-MOD-001 | 実機訓練 | 実画像を使用した新規モデル訓練 | 実機+バックエンド+訓練画像 | モデル生成・保存 | High | 300分 |
| REAL-MOD-002 | 実機訓練 | 訓練済みモデルの推論確認 | 実機+バックエンド+対象物 | 高精度な物体認識 | High | 180分 |
| REAL-MOD-003 | 実機訓練 | 複数モデルの切り替え運用 | 実機+バックエンド+複数対象物 | モデル切り替え・認識確認 | Medium | 240分 |

### 2.6 E2Eワークフローテスト

| テストケースID | テストカテゴリ | テストシナリオ | 実行環境 | 想定動作 | 優先度 | 実装時間 |
|:---|:---|:---|:---|:---|:---|:---|
| REAL-E2E-001 | 完全ワークフロー | 接続→訓練→追跡→切断 | フル環境 | 全機能統合動作 | High | 480分 |
| REAL-E2E-002 | 運用シナリオ | 実運用想定の連続稼働 | フル環境 | 安定した長時間運用 | High | 600分 |
| REAL-E2E-003 | 異常回復 | エラー発生→回復→継続 | フル環境 | 堅牢なエラー回復 | High | 360分 |

---

## 3. テスト実装優先度・スケジュール

### 3.1 優先度別実装順序

| 優先度 | 実装対象 | 推定工数 | 実装順序 |
|:---|:---|:---|:---|
| **High** | モック基本API（接続・飛行・移動・カメラ・センサー・追跡・モデル） | 35-40時間 | 第1フェーズ |
| **High** | WebSocket・リアルタイム通信 | 8-10時間 | 第2フェーズ |
| **High** | 実機基本制御（接続・飛行・移動・緊急停止） | 12-15時間 | 第3フェーズ |
| **High** | 実機追跡・E2Eワークフロー | 20-25時間 | 第4フェーズ |
| **Medium** | モック詳細機能（高度移動・設定・詳細センサー） | 10-12時間 | 第5フェーズ |
| **Medium** | 実機詳細機能（カメラ設定・センサー詳細・複数モデル） | 15-18時間 | 第6フェーズ |
| **Low** | ミッションパッド・任意コマンド | 5-8時間 | 第7フェーズ |

### 3.2 総実装時間見積もり

- **モックバックエンド結合テスト**: 約55-65時間
- **実機バックエンド結合テスト**: 約50-60時間
- **テスト基盤・インフラ**: 約10-15時間
- **総合計**: **約115-140時間** (約3-4週間・フルタイム)

### 3.3 段階的実装スケジュール

| 週 | フェーズ | 実装内容 | 累積進捗 |
|:---|:---|:---|:---|
| **1週目** | 第1-2フェーズ | モック基本API + WebSocket | 40% |
| **2週目** | 第3フェーズ | 実機基本制御 | 60% |
| **3週目** | 第4フェーズ | 実機追跡・E2Eワークフロー | 85% |
| **4週目** | 第5-7フェーズ | 詳細機能・最終調整 | 100% |

---

## 4. テスト実装要件・制約

### 4.1 技術要件

- **テストフレームワーク**: pytest + Flask-Testing + coverage
- **モックライブラリ**: responses + pytest-mock + wiremock
- **WebSocketテスト**: Flask-SocketIO + socketio-client
- **実機制御**: djitellopy + OpenCV + AI モデル

### 4.2 実行環境要件

- **モックテスト**: 開発環境のみ（実機不要）
- **実機テスト**: Tello EDU + Raspberry Pi 5 + 物体認識用対象物
- **安全要件**: 実機テスト時の飛行安全確保・緊急停止手順

### 4.3 テストデータ要件

- **モック応答**: 現実的なセンサー値・エラーコード
- **テスト画像**: 物体認識訓練用多様な画像セット
- **シナリオデータ**: E2Eワークフロー用テストシーケンス

---

## 5. 成功基準・品質目標

### 5.1 カバレッジ目標

- **APIエンドポイントカバレッジ**: 100% (60+エンドポイント)
- **エラーシナリオカバレッジ**: 90%以上
- **WebSocket機能カバレッジ**: 100%
- **実機制御カバレッジ**: 80%以上

### 5.2 性能・信頼性目標

- **テスト実行時間**: モックテスト 30分以内、実機テスト 3時間以内
- **テスト成功率**: 95%以上 (安定した実行)
- **実機安全性**: 100% (飛行安全確保)

---

この文書に基づき、段階的で包括的なフェーズ3結合テストの実装を行います。