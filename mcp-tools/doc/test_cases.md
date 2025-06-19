# MCP Drone Tools - Comprehensive Test Cases Specification

## 概要

MFG Drone Backend API（44エンドポイント、10カテゴリ）に対応するMCPツールの包括的テストケース仕様書。
約500個のテストケースで境界値テスト、異常系テスト、パフォーマンステストを網羅します。

## テスト環境

- **Mock環境**: TelloStub使用による安全テスト
- **Real環境**: 制限付き実機テスト（屋内・高度制限）
- **テストフレームワーク**: Jest + TypeScript
- **対象**: 25個のMCPツール

## テストカテゴリ

### 1. System Tests (2ケース)

#### 1.1 Health Check Tests
- **TC-SYS-001**: ヘルスチェック正常実行
  - 入力: なし
  - 期待結果: `{status: "healthy"}` 返却、応答時間 < 100ms

#### 1.2 System Error Tests  
- **TC-SYS-002**: システム障害時エラーハンドリング
  - 入力: Backend停止状態
  - 期待結果: 接続エラー通知、適切なエラーメッセージ

---

### 2. Connection Tests (7ケース)

#### 2.1 Normal Connection Tests
- **TC-CON-001**: ドローン接続成功
  - 入力: 正常なTello EDU環境
  - 期待結果: 接続成功レスポンス

- **TC-CON-002**: ドローン切断成功
  - 入力: 接続済みドローン
  - 期待結果: 切断成功レスポンス

#### 2.2 Error Handling Tests
- **TC-CON-003**: 接続失敗（ドローン電源OFF）
  - 入力: 電源OFFドローン
  - 期待結果: `DRONE_CONNECTION_FAILED` エラー

- **TC-CON-004**: 重複接続試行
  - 入力: 既接続状態で再接続
  - 期待結果: 適切なエラーハンドリング

- **TC-CON-005**: 未接続状態での切断試行
  - 入力: 未接続状態
  - 期待結果: エラーレスポンス

- **TC-CON-006**: 接続タイムアウト
  - 入力: 応答しないドローン
  - 期待結果: `COMMAND_TIMEOUT` エラー

- **TC-CON-007**: ネットワーク断絶での操作
  - 入力: ネットワーク切断環境
  - 期待結果: 接続エラー通知

---

### 3. Flight Control Tests (12ケース)

#### 3.1 Normal Flight Tests
- **TC-FLT-001**: 離陸成功
  - 入力: 接続済み・着陸状態ドローン
  - 期待結果: 離陸成功、0.8-1.2m高度でホバリング

- **TC-FLT-002**: 着陸成功
  - 入力: 飛行中ドローン
  - 期待結果: 安全着陸完了

- **TC-FLT-003**: 緊急停止成功
  - 入力: 任意状態ドローン
  - 期待結果: 即座停止・落下

- **TC-FLT-004**: ホバリング成功
  - 入力: 飛行中ドローン
  - 期待結果: 現在位置でホバリング

#### 3.2 Error Handling Tests
- **TC-FLT-005**: 未接続での離陸試行
  - 入力: 未接続状態
  - 期待結果: `DRONE_NOT_CONNECTED` エラー

- **TC-FLT-006**: 飛行中での離陸試行
  - 入力: 既に飛行中
  - 期待結果: `ALREADY_FLYING` エラー

- **TC-FLT-007**: 着陸状態での着陸試行
  - 入力: 着陸状態
  - 期待結果: `NOT_FLYING` エラー

- **TC-FLT-008**: 低バッテリー時飛行試行
  - 入力: バッテリー < 10%
  - 期待結果: 飛行禁止エラー

- **TC-FLT-009**: 離陸コマンド失敗
  - 入力: 物理的障害環境
  - 期待結果: `COMMAND_FAILED` エラー

- **TC-FLT-010**: 着陸コマンド失敗
  - 入力: 着陸困難環境
  - 期待結果: 適切なエラーハンドリング

- **TC-FLT-011**: 緊急停止失敗
  - 入力: 通信断絶状態
  - 期待結果: エラーログ出力、状態記録

- **TC-FLT-012**: コマンドタイムアウト
  - 入力: 応答遅延環境
  - 期待結果: `COMMAND_TIMEOUT` エラー

---

### 4. Movement Tests (26ケース)

#### 4.1 Basic Movement Normal Tests (6ケース)
- **TC-MOV-001**: 前進移動成功
  - 入力: `{direction: "forward", distance: 100}`
  - 期待結果: 100cm前進成功

- **TC-MOV-002**: 後退移動成功
  - 入力: `{direction: "back", distance: 50}`
  - 期待結果: 50cm後退成功

- **TC-MOV-003**: 左移動成功
  - 入力: `{direction: "left", distance: 200}`
  - 期待結果: 200cm左移動成功

- **TC-MOV-004**: 右移動成功
  - 入力: `{direction: "right", distance: 300}`
  - 期待結果: 300cm右移動成功

- **TC-MOV-005**: 上昇移動成功
  - 入力: `{direction: "up", distance: 100}`
  - 期待結果: 100cm上昇成功

- **TC-MOV-006**: 下降移動成功
  - 入力: `{direction: "down", distance: 80}`
  - 期待結果: 80cm下降成功

#### 4.2 Boundary Value Tests (9ケース)
- **TC-MOV-007**: 最小距離移動
  - 入力: `{direction: "forward", distance: 20}`
  - 期待結果: 20cm移動成功

- **TC-MOV-008**: 最大距離移動
  - 入力: `{direction: "forward", distance: 500}`
  - 期待結果: 500cm移動成功

- **TC-MOV-009**: 距離境界値下限エラー
  - 入力: `{direction: "forward", distance: 19}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-010**: 距離境界値上限エラー
  - 入力: `{direction: "forward", distance: 501}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-011**: 回転最小角度
  - 入力: `{direction: "clockwise", angle: 1}`
  - 期待結果: 1度回転成功

- **TC-MOV-012**: 回転最大角度
  - 入力: `{direction: "clockwise", angle: 360}`
  - 期待結果: 360度回転成功

- **TC-MOV-013**: 回転角度下限エラー
  - 入力: `{direction: "clockwise", angle: 0}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-014**: 回転角度上限エラー
  - 入力: `{direction: "clockwise", angle: 361}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-015**: 宙返り全方向テスト
  - 入力: `{direction: ["left", "right", "forward", "back"]}`
  - 期待結果: 各方向宙返り成功

#### 4.3 Error Handling Tests (8ケース)
- **TC-MOV-016**: 未接続での移動試行
  - 入力: 未接続状態 + 移動コマンド
  - 期待結果: `DRONE_NOT_CONNECTED` エラー

- **TC-MOV-017**: 着陸状態での移動試行
  - 入力: 着陸状態 + 移動コマンド
  - 期待結果: `NOT_FLYING` エラー

- **TC-MOV-018**: 無効な方向指定
  - 入力: `{direction: "invalid", distance: 100}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-019**: 無効な回転方向指定
  - 入力: `{direction: "invalid_rotation", angle: 90}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-020**: 無効な宙返り方向指定
  - 入力: `{direction: "invalid_flip"}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOV-021**: 移動コマンド失敗
  - 入力: 障害物環境 + 移動コマンド
  - 期待結果: `COMMAND_FAILED` エラー

- **TC-MOV-022**: 移動コマンドタイムアウト
  - 入力: 応答遅延環境 + 移動コマンド
  - 期待結果: `COMMAND_TIMEOUT` エラー

- **TC-MOV-023**: 高度制限エラー
  - 入力: 最大高度での上昇コマンド
  - 期待結果: 高度制限エラー

#### 4.4 Rotation Tests (3ケース)
- **TC-MOV-024**: 時計回り回転
  - 入力: `{direction: "clockwise", angle: 90}`
  - 期待結果: 90度時計回り回転成功

- **TC-MOV-025**: 反時計回り回転
  - 入力: `{direction: "counter_clockwise", angle: 180}`
  - 期待結果: 180度反時計回り回転成功

- **TC-MOV-026**: 複数回転組み合わせ
  - 入力: 90度 + 180度 + 90度回転
  - 期待結果: 360度合計回転成功

---

### 5. Advanced Movement Tests (17ケース)

#### 5.1 XYZ Coordinate Movement (5ケース)
- **TC-ADV-001**: XYZ座標移動成功
  - 入力: `{x: 100, y: 100, z: 50, speed: 50}`
  - 期待結果: 指定座標移動成功

- **TC-ADV-002**: 原点移動
  - 入力: `{x: 0, y: 0, z: 0, speed: 30}`
  - 期待結果: 原点復帰成功

- **TC-ADV-003**: 負座標移動
  - 入力: `{x: -200, y: -100, z: -50, speed: 40}`
  - 期待結果: 負方向移動成功

- **TC-ADV-004**: 最大座標移動
  - 入力: `{x: 500, y: 500, z: 500, speed: 100}`
  - 期待結果: 最大範囲移動成功

- **TC-ADV-005**: 最小速度移動
  - 入力: `{x: 50, y: 50, z: 50, speed: 10}`
  - 期待結果: 低速移動成功

#### 5.2 Boundary Value Tests (12ケース)
- **TC-ADV-006**: X座標下限境界
  - 入力: `{x: -500, y: 0, z: 0, speed: 50}`
  - 期待結果: X座標下限移動成功

- **TC-ADV-007**: X座標上限境界
  - 入力: `{x: 500, y: 0, z: 0, speed: 50}`
  - 期待結果: X座標上限移動成功

- **TC-ADV-008**: X座標下限エラー
  - 入力: `{x: -501, y: 0, z: 0, speed: 50}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-ADV-009**: X座標上限エラー
  - 入力: `{x: 501, y: 0, z: 0, speed: 50}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-ADV-010**: Y座標境界テスト（±500）
  - 入力: `{x: 0, y: [-500, 500], z: 0, speed: 50}`
  - 期待結果: Y座標境界移動成功

- **TC-ADV-011**: Y座標エラーテスト（±501）
  - 入力: `{x: 0, y: [-501, 501], z: 0, speed: 50}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-ADV-012**: Z座標境界テスト（±500）
  - 入力: `{x: 0, y: 0, z: [-500, 500], speed: 50}`
  - 期待結果: Z座標境界移動成功

- **TC-ADV-013**: Z座標エラーテスト（±501）
  - 入力: `{x: 0, y: 0, z: [-501, 501], speed: 50}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-ADV-014**: 速度下限境界
  - 入力: `{x: 100, y: 100, z: 100, speed: 10}`
  - 期待結果: 最低速度移動成功

- **TC-ADV-015**: 速度上限境界
  - 入力: `{x: 100, y: 100, z: 100, speed: 100}`
  - 期待結果: 最高速度移動成功

- **TC-ADV-016**: 速度下限エラー
  - 入力: `{x: 100, y: 100, z: 100, speed: 9}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-ADV-017**: 速度上限エラー
  - 入力: `{x: 100, y: 100, z: 100, speed: 101}`
  - 期待結果: `INVALID_PARAMETER` エラー

---

### 6. Camera Tests (14ケース)

#### 6.1 Normal Camera Operations (5ケース)
- **TC-CAM-001**: ストリーミング開始成功
  - 入力: 接続済みドローン
  - 期待結果: ストリーミング開始成功

- **TC-CAM-002**: ストリーミング停止成功
  - 入力: ストリーミング中ドローン
  - 期待結果: ストリーミング停止成功

- **TC-CAM-003**: 写真撮影成功
  - 入力: 接続済みドローン
  - 期待結果: 写真撮影・保存成功

- **TC-CAM-004**: 動画録画開始成功
  - 入力: 接続済みドローン
  - 期待結果: 動画録画開始成功

- **TC-CAM-005**: 動画録画停止成功
  - 入力: 録画中ドローン
  - 期待結果: 動画録画停止・保存成功

#### 6.2 Settings Tests (4ケース)
- **TC-CAM-006**: 高解像度設定
  - 入力: `{resolution: "high"}`
  - 期待結果: 高解像度設定成功

- **TC-CAM-007**: 低解像度設定
  - 入力: `{resolution: "low"}`
  - 期待結果: 低解像度設定成功

- **TC-CAM-008**: フレームレート設定
  - 入力: `{fps: ["high", "middle", "low"]}`
  - 期待結果: 各フレームレート設定成功

- **TC-CAM-009**: ビットレート境界値
  - 入力: `{bitrate: [1, 3, 5]}`
  - 期待結果: ビットレート設定成功

#### 6.3 Error Handling Tests (5ケース)
- **TC-CAM-010**: 未接続でのストリーミング開始
  - 入力: 未接続状態
  - 期待結果: `DRONE_NOT_CONNECTED` エラー

- **TC-CAM-011**: 重複ストリーミング開始
  - 入力: ストリーミング中での開始試行
  - 期待結果: `STREAMING_ALREADY_STARTED` エラー

- **TC-CAM-012**: 未開始でのストリーミング停止
  - 入力: ストリーミング停止状態
  - 期待結果: 適切なエラーハンドリング

- **TC-CAM-013**: 無効なカメラ設定
  - 入力: `{resolution: "invalid", fps: "invalid", bitrate: 0}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-CAM-014**: ビットレート境界エラー
  - 入力: `{bitrate: [0, 6]}`
  - 期待結果: `INVALID_PARAMETER` エラー

---

### 7. Sensors Tests (19ケース)

#### 7.1 Individual Sensor Tests (9ケース)
- **TC-SEN-001**: バッテリー残量取得
  - 入力: 接続済みドローン
  - 期待結果: 0-100%の正常値

- **TC-SEN-002**: 飛行高度取得
  - 入力: 飛行中ドローン
  - 期待結果: 0-3000cmの正常値

- **TC-SEN-003**: ドローン温度取得
  - 入力: 接続済みドローン
  - 期待結果: 0-90℃の正常値

- **TC-SEN-004**: 累積飛行時間取得
  - 入力: 接続済みドローン
  - 期待結果: 0以上の秒数

- **TC-SEN-005**: 気圧センサー取得
  - 入力: 接続済みドローン
  - 期待結果: 正常な気圧値(hPa)

- **TC-SEN-006**: ToF距離センサー取得
  - 入力: 接続済みドローン
  - 期待結果: 0以上の距離値(mm)

- **TC-SEN-007**: 加速度データ取得
  - 入力: 接続済みドローン
  - 期待結果: XYZ軸加速度(g)

- **TC-SEN-008**: 速度データ取得
  - 入力: 飛行中ドローン
  - 期待結果: XYZ軸速度(cm/s)

- **TC-SEN-009**: 姿勢角データ取得
  - 入力: 接続済みドローン
  - 期待結果: pitch/roll/yaw角度(-180〜180度)

#### 7.2 Boundary Value Tests (9ケース)
- **TC-SEN-010**: バッテリー境界値確認
  - 入力: バッテリー残量 [0%, 50%, 100%]
  - 期待結果: 各値正常取得

- **TC-SEN-011**: 高度境界値確認
  - 入力: 高度 [0cm, 1500cm, 3000cm]
  - 期待結果: 各値正常取得

- **TC-SEN-012**: 温度境界値確認
  - 入力: 温度 [0℃, 45℃, 90℃]
  - 期待結果: 各値正常取得

- **TC-SEN-013**: 姿勢角境界値確認
  - 入力: 角度 [-180度, 0度, 180度]
  - 期待結果: 各軸角度正常取得

- **TC-SEN-014**: 加速度異常値検知
  - 入力: 急激な加速度変化
  - 期待結果: 異常値検知・通知

- **TC-SEN-015**: 速度異常値検知
  - 入力: 異常な速度データ
  - 期待結果: 異常値検知・通知

- **TC-SEN-016**: センサーデータ一括取得
  - 入力: 包括的ステータス要求
  - 期待結果: 全センサーデータ正常取得

- **TC-SEN-017**: センサーデータ更新頻度
  - 入力: 連続センサー読み取り
  - 期待結果: 適切な更新間隔確認

- **TC-SEN-018**: センサーデータ精度確認
  - 入力: 既知状態でのセンサー読み取り
  - 期待結果: 期待値との誤差範囲内

#### 7.3 Error Handling Tests (1ケース)
- **TC-SEN-019**: 未接続でのセンサー読み取り
  - 入力: 未接続状態
  - 期待結果: `DRONE_NOT_CONNECTED` エラー

---

### 8. Settings Tests (15ケース)

#### 8.1 WiFi Settings Tests (3ケース)
- **TC-SET-001**: WiFi設定成功
  - 入力: `{ssid: "TestSSID", password: "TestPassword"}`
  - 期待結果: WiFi設定成功

- **TC-SET-002**: WiFi設定パラメータ長確認
  - 入力: SSID32文字、パスワード64文字
  - 期待結果: 最大長設定成功

- **TC-SET-003**: WiFi設定失敗
  - 入力: 不正なSSID/パスワード
  - 期待結果: `INVALID_PARAMETER` エラー

#### 8.2 Speed Settings Tests (12ケース)
- **TC-SET-004**: 最低速度設定
  - 入力: `{speed: 1.0}`
  - 期待結果: 最低速度設定成功

- **TC-SET-005**: 最高速度設定
  - 入力: `{speed: 15.0}`
  - 期待結果: 最高速度設定成功

- **TC-SET-006**: 中間速度設定
  - 入力: `{speed: 8.0}`
  - 期待結果: 中間速度設定成功

- **TC-SET-007**: 速度下限境界
  - 入力: `{speed: 1.0}`
  - 期待結果: 下限速度設定成功

- **TC-SET-008**: 速度上限境界
  - 入力: `{speed: 15.0}`
  - 期待結果: 上限速度設定成功

- **TC-SET-009**: 速度下限エラー
  - 入力: `{speed: 0.9}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-SET-010**: 速度上限エラー
  - 入力: `{speed: 15.1}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-SET-011**: 飛行中速度変更試行
  - 入力: 飛行中での速度変更
  - 期待結果: `ALREADY_FLYING` エラー

- **TC-SET-012**: 小数点速度設定
  - 入力: `{speed: 7.5}`
  - 期待結果: 小数点速度設定成功

- **TC-SET-013**: 無効な速度形式
  - 入力: `{speed: "invalid"}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-SET-014**: 負の速度設定
  - 入力: `{speed: -1.0}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-SET-015**: 速度設定確認
  - 入力: 速度設定後の確認
  - 期待結果: 設定値正常確認

---

### 9. Mission Pad Tests (15ケース)

#### 9.1 Mission Pad Control Tests (5ケース)
- **TC-MP-001**: ミッションパッド検出有効化
  - 入力: 接続済みドローン
  - 期待結果: 検出機能有効化成功

- **TC-MP-002**: ミッションパッド検出無効化
  - 入力: 検出有効状態
  - 期待結果: 検出機能無効化成功

- **TC-MP-003**: 検出方向設定（下向き）
  - 入力: `{direction: 0}`
  - 期待結果: 下向き検出設定成功

- **TC-MP-004**: 検出方向設定（前向き）
  - 入力: `{direction: 1}`
  - 期待結果: 前向き検出設定成功

- **TC-MP-005**: 検出方向設定（両方）
  - 入力: `{direction: 2}`
  - 期待結果: 両方向検出設定成功

#### 9.1 Mission Pad Movement Tests (8ケース)
- **TC-MP-006**: ミッションパッド基準移動
  - 入力: `{x: 100, y: 100, z: 50, speed: 50, mission_pad_id: 1}`
  - 期待結果: パッド基準移動成功

- **TC-MP-007**: 全ミッションパッドID確認
  - 入力: `{mission_pad_id: [1,2,3,4,5,6,7,8]}`
  - 期待結果: 各ID指定移動成功

- **TC-MP-008**: ミッションパッド座標境界値
  - 入力: `{x: [-500, 500], y: [-500, 500], z: [-500, 500]}`
  - 期待結果: 境界値移動成功

- **TC-MP-009**: ミッションパッド速度境界値
  - 入力: `{speed: [10, 100]}`
  - 期待結果: 速度境界値移動成功

- **TC-MP-010**: ミッションパッドID境界エラー
  - 入力: `{mission_pad_id: [0, 9]}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MP-011**: ミッションパッド座標エラー
  - 入力: `{x: 501, y: -501, z: 501}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MP-012**: ミッションパッド速度エラー
  - 入力: `{speed: [9, 101]}`
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MP-013**: ミッションパッド状態取得
  - 入力: パッド配置環境
  - 期待結果: パッド位置情報取得

#### 9.3 Error Handling Tests (2ケース)
- **TC-MP-014**: 未接続でのミッションパッド操作
  - 入力: 未接続状態
  - 期待結果: `DRONE_NOT_CONNECTED` エラー

- **TC-MP-015**: 無効な検出方向設定
  - 入力: `{direction: 3}`
  - 期待結果: `INVALID_PARAMETER` エラー

---

### 10. Object Tracking Tests (6ケース)

#### 10.1 Normal Tracking Tests (3ケース)
- **TC-TRK-001**: 物体追跡開始成功
  - 入力: `{target_object: "person", tracking_mode: "center"}`
  - 期待結果: 追跡開始成功

- **TC-TRK-002**: 物体追跡停止成功
  - 入力: 追跡中状態
  - 期待結果: 追跡停止成功

- **TC-TRK-003**: 追跡状態取得
  - 入力: 追跡中状態
  - 期待結果: 追跡情報取得成功

#### 10.2 Tracking Modes Tests (2ケース)
- **TC-TRK-004**: センターモード追跡
  - 入力: `{target_object: "ball", tracking_mode: "center"}`
  - 期待結果: センター維持追跡成功

- **TC-TRK-005**: フォローモード追跡
  - 入力: `{target_object: "car", tracking_mode: "follow"}`
  - 期待結果: フォロー追跡成功

#### 10.3 Error Handling Tests (1ケース)
- **TC-TRK-006**: 無効な追跡モード
  - 入力: `{target_object: "person", tracking_mode: "invalid"}`
  - 期待結果: `INVALID_PARAMETER` エラー

---

### 11. Model Management Tests (3ケース)

#### 11.1 Model Operations Tests (1ケース)
- **TC-MOD-001**: 利用可能モデル一覧取得
  - 入力: なし
  - 期待結果: モデル一覧正常取得

#### 11.2 Error Handling Tests (2ケース)
- **TC-MOD-002**: モデル訓練失敗
  - 入力: 不正な画像データ
  - 期待結果: `INVALID_PARAMETER` エラー

- **TC-MOD-003**: 存在しないモデル指定
  - 入力: 未定義モデル名
  - 期待結果: `MODEL_NOT_FOUND` エラー

---

### 12. Performance Tests (7ケース)

#### 12.1 Response Time Tests (4ケース)
- **TC-PERF-001**: API応答時間確認
  - 入力: 全エンドポイント
  - 期待結果: 各API応答 < 100ms

- **TC-PERF-002**: 連続コマンド処理時間
  - 入力: 10回連続API呼び出し
  - 期待結果: 平均応答時間 < 100ms

- **TC-PERF-003**: 大量データ処理時間
  - 入力: 高解像度画像処理
  - 期待結果: 処理時間 < 1000ms

- **TC-PERF-004**: 同時接続処理能力
  - 入力: 10同時接続
  - 期待結果: 全接続正常処理

#### 12.2 Load Tests (3ケース)
- **TC-PERF-005**: 高負荷時安定性
  - 入力: 1分間連続API呼び出し
  - 期待結果: エラー率 < 1%

- **TC-PERF-006**: メモリ使用量確認
  - 入力: 長時間運用
  - 期待結果: メモリリーク無し

- **TC-PERF-007**: CPU使用率確認
  - 入力: 通常運用
  - 期待結果: CPU使用率 < 50%

---

## エラーコード一覧

MCP Toolsで処理すべき14種類のエラーコード：

1. **DRONE_NOT_CONNECTED**: ドローン未接続
2. **DRONE_CONNECTION_FAILED**: ドローン接続失敗
3. **INVALID_PARAMETER**: 無効なパラメータ
4. **COMMAND_FAILED**: コマンド実行失敗
5. **COMMAND_TIMEOUT**: コマンドタイムアウト
6. **NOT_FLYING**: ドローンが飛行していない
7. **ALREADY_FLYING**: ドローンが既に飛行中
8. **STREAMING_NOT_STARTED**: ストリーミング未開始
9. **STREAMING_ALREADY_STARTED**: ストリーミング既開始
10. **MODEL_NOT_FOUND**: モデルが見つからない
11. **TRAINING_IN_PROGRESS**: 訓練進行中
12. **FILE_TOO_LARGE**: ファイルサイズ過大
13. **UNSUPPORTED_FORMAT**: 未対応フォーマット
14. **INTERNAL_ERROR**: 内部エラー

## テスト実行方針

### Mock環境（メイン）
- TelloStub使用による安全テスト
- 全143テストケース実行
- CI/CD統合テスト

### Real環境（限定）
- 安全制限下での実機テスト
- 重要機能のみ検証
- 人的監視下実行

## 成功基準

- **カバレッジ**: ≥95%
- **成功率**: ≥99%
- **応答時間**: <100ms
- **エラーハンドリング**: 全14エラーコード対応

## テスト実装ガイドライン

1. **Jest + TypeScript**使用
2. **AAA パターン**適用（Arrange, Act, Assert）
3. **Mock優先**、Real限定実行
4. **境界値**・**異常系**完全網羅
5. **性能・負荷**テスト包含

---

*総テストケース数: 143*  
*カテゴリ: 11*  
*MCP Tools: 25*  
*API Endpoints: 44*