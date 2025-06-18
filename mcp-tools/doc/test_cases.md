# MCP Tools テストケース一覧

## 概要

この文書はMFG Drone Backend APIをMCPツール化する際の包括的なテストケースを定義します。
全44エンドポイント、10カテゴリに対して境界値テスト、異常系テストを網羅し、
実機なし（mock）・実機ありの両方の環境での動作を保証します。

## テスト環境分類

### Mock環境（drone_stub使用）
- **目的**: 安全かつ高速な開発・テスト
- **使用場面**: 境界値テスト、異常系テスト、CI/CD
- **特徴**: 実際のドローンハードウェア不要

### Real環境（実機Tello EDU使用）
- **目的**: 実環境での動作確認
- **使用場面**: 統合テスト、ユーザーシナリオテスト
- **特徴**: 安全制限あり（屋内・低高度・監視者必須）

## エラーコード一覧

| コード | 説明 | HTTPステータス |
|--------|------|---------------|
| DRONE_NOT_CONNECTED | ドローン未接続 | 503 |
| DRONE_CONNECTION_FAILED | 接続失敗 | 500 |
| INVALID_PARAMETER | 無効パラメータ | 400 |
| COMMAND_FAILED | コマンド実行失敗 | 400 |
| COMMAND_TIMEOUT | コマンドタイムアウト | 408 |
| NOT_FLYING | 非飛行状態 | 409 |
| ALREADY_FLYING | 既に飛行中 | 409 |
| STREAMING_NOT_STARTED | ストリーミング未開始 | 404 |
| STREAMING_ALREADY_STARTED | ストリーミング既開始 | 409 |
| MODEL_NOT_FOUND | モデル未発見 | 404 |
| TRAINING_IN_PROGRESS | 訓練中 | 409 |
| FILE_TOO_LARGE | ファイルサイズ超過 | 413 |
| UNSUPPORTED_FORMAT | 未対応フォーマット | 400 |
| INTERNAL_ERROR | 内部エラー | 500 |

---

## 1. System API テストケース

### 1.1 /health - ヘルスチェック

#### 正常系テスト
| ID | テスト名 | 環境 | 入力 | 期待結果 |
|----|----------|------|------|----------|
| SYS-001 | 基本ヘルスチェック | Mock/Real | GET /health | 200, {"status": "healthy"} |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| SYS-002 | サーバー停止時 | Mock | サーバー未起動 | 接続エラー |

---

## 2. Connection API テストケース

### 2.1 /drone/connect - ドローン接続

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CON-001 | 初回接続 | Mock | 未接続状態 | 200, success: true |
| CON-002 | 実機接続 | Real | Tello EDU電源ON | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CON-003 | 重複接続 | Mock | 既に接続済み | 200, success: true (idempotent) |
| CON-004 | ドローン電源OFF | Real | 電源OFF状態 | 500, DRONE_CONNECTION_FAILED |
| CON-005 | WiFi圏外 | Real | 通信範囲外 | 500, DRONE_CONNECTION_FAILED |

### 2.2 /drone/disconnect - ドローン切断

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CON-010 | 正常切断 | Mock/Real | 接続状態から | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CON-011 | 未接続状態切断 | Mock | 未接続状態 | 200, success: true (idempotent) |
| CON-012 | 飛行中切断 | Real | 飛行状態 | 200, 自動着陸後切断 |

---

## 3. Flight Control API テストケース

### 3.1 /drone/takeoff - 離陸

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-001 | 通常離陸 | Mock | 接続済み・地上 | 200, success: true |
| FLT-002 | 実機離陸 | Real | 安全な屋内環境 | 200, ホバリング状態 |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-003 | 未接続離陸 | Mock | 未接続状態 | 503, DRONE_NOT_CONNECTED |
| FLT-004 | 重複離陸 | Mock | 既に飛行中 | 409, ALREADY_FLYING |
| FLT-005 | 低バッテリー | Mock | バッテリー<10% | 400, COMMAND_FAILED |
| FLT-006 | 屋外離陸 | Real | GPS環境 | 400, 屋外制限エラー |

### 3.2 /drone/land - 着陸

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-010 | 通常着陸 | Mock/Real | 飛行状態から | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-011 | 地上状態着陸 | Mock | 既に地上 | 409, NOT_FLYING |
| FLT-012 | 未接続着陸 | Mock | 未接続状態 | 503, DRONE_NOT_CONNECTED |

### 3.3 /drone/emergency - 緊急停止

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-020 | 飛行中緊急停止 | Mock | 飛行状態 | 200, 即座停止 |
| FLT-021 | 地上緊急停止 | Mock | 地上状態 | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-022 | 未接続緊急停止 | Mock | 未接続状態 | 500, INTERNAL_ERROR |

### 3.4 /drone/stop - ホバリング

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-030 | 飛行中ホバリング | Mock/Real | 移動中 | 200, ホバリング状態 |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| FLT-031 | 地上ホバリング | Mock | 地上状態 | 409, NOT_FLYING |

---

## 4. Movement API テストケース

### 4.1 /drone/move - 基本移動

#### 境界値テスト
| ID | テスト名 | 環境 | direction | distance | 期待結果 |
|----|----------|------|-----------|----------|----------|
| MOV-001 | 最小距離 | Mock | "forward" | 20 | 200, success: true |
| MOV-002 | 最大距離 | Mock | "forward" | 500 | 200, success: true |
| MOV-003 | 範囲外小 | Mock | "forward" | 19 | 400, INVALID_PARAMETER |
| MOV-004 | 範囲外大 | Mock | "forward" | 501 | 400, INVALID_PARAMETER |
| MOV-005 | 全方向テスト | Mock | "up" | 100 | 200, success: true |
| MOV-006 | 全方向テスト | Mock | "down" | 100 | 200, success: true |
| MOV-007 | 全方向テスト | Mock | "left" | 100 | 200, success: true |
| MOV-008 | 全方向テスト | Mock | "right" | 100 | 200, success: true |
| MOV-009 | 全方向テスト | Mock | "back" | 100 | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| MOV-010 | 無効方向 | Mock | "invalid" | 400, INVALID_PARAMETER |
| MOV-011 | 文字列距離 | Mock | distance: "abc" | 400, INVALID_PARAMETER |
| MOV-012 | 未飛行移動 | Mock | 地上状態 | 409, NOT_FLYING |
| MOV-013 | 未接続移動 | Mock | 未接続 | 503, DRONE_NOT_CONNECTED |

### 4.2 /drone/rotate - 回転

#### 境界値テスト
| ID | テスト名 | 環境 | direction | angle | 期待結果 |
|----|----------|------|-----------|-------|----------|
| MOV-020 | 最小角度 | Mock | "clockwise" | 1 | 200, success: true |
| MOV-021 | 最大角度 | Mock | "clockwise" | 360 | 200, success: true |
| MOV-022 | 範囲外小 | Mock | "clockwise" | 0 | 400, INVALID_PARAMETER |
| MOV-023 | 範囲外大 | Mock | "clockwise" | 361 | 400, INVALID_PARAMETER |
| MOV-024 | 反時計回り | Mock | "counter_clockwise" | 180 | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| MOV-025 | 無効方向 | Mock | "invalid" | 400, INVALID_PARAMETER |
| MOV-026 | 負の角度 | Mock | angle: -10 | 400, INVALID_PARAMETER |
| MOV-027 | 未飛行回転 | Mock | 地上状態 | 409, NOT_FLYING |

### 4.3 /drone/flip - 宙返り

#### 正常系テスト
| ID | テスト名 | 環境 | direction | 期待結果 |
|----|----------|------|-----------|----------|
| MOV-030 | 左宙返り | Mock | "left" | 200, success: true |
| MOV-031 | 右宙返り | Mock | "right" | 200, success: true |
| MOV-032 | 前宙返り | Mock | "forward" | 200, success: true |
| MOV-033 | 後宙返り | Mock | "back" | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| MOV-034 | 無効方向 | Mock | "up" | 400, INVALID_PARAMETER |
| MOV-035 | 未飛行宙返り | Mock | 地上状態 | 409, NOT_FLYING |
| MOV-036 | 低高度宙返り | Real | 高度<100cm | 400, COMMAND_FAILED |

---

## 5. Advanced Movement API テストケース

### 5.1 /drone/go_xyz - 座標移動

#### 境界値テスト
| ID | テスト名 | 環境 | x | y | z | speed | 期待結果 |
|----|----------|------|---|---|---|-------|----------|
| ADV-001 | 最小座標 | Mock | -500 | -500 | -500 | 10 | 200, success: true |
| ADV-002 | 最大座標 | Mock | 500 | 500 | 500 | 100 | 200, success: true |
| ADV-003 | 範囲外X+ | Mock | 501 | 0 | 0 | 50 | 400, INVALID_PARAMETER |
| ADV-004 | 範囲外X- | Mock | -501 | 0 | 0 | 50 | 400, INVALID_PARAMETER |
| ADV-005 | 範囲外Y+ | Mock | 0 | 501 | 0 | 50 | 400, INVALID_PARAMETER |
| ADV-006 | 範囲外Y- | Mock | 0 | -501 | 0 | 50 | 400, INVALID_PARAMETER |
| ADV-007 | 範囲外Z+ | Mock | 0 | 0 | 501 | 50 | 400, INVALID_PARAMETER |
| ADV-008 | 範囲外Z- | Mock | 0 | 0 | -501 | 50 | 400, INVALID_PARAMETER |
| ADV-009 | 最小速度 | Mock | 100 | 100 | 100 | 10 | 200, success: true |
| ADV-010 | 最大速度 | Mock | 100 | 100 | 100 | 100 | 200, success: true |
| ADV-011 | 範囲外速度小 | Mock | 100 | 100 | 100 | 9 | 400, INVALID_PARAMETER |
| ADV-012 | 範囲外速度大 | Mock | 100 | 100 | 100 | 101 | 400, INVALID_PARAMETER |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| ADV-013 | 未飛行移動 | Mock | 地上状態 | 409, NOT_FLYING |
| ADV-014 | 無効座標型 | Mock | x: "abc" | 400, INVALID_PARAMETER |

### 5.2 /drone/curve_xyz - 曲線飛行

#### 境界値テスト
| ID | テスト名 | 環境 | すべてのパラメータ | 期待結果 |
|----|----------|------|-------------------|----------|
| ADV-020 | 最小座標・速度 | Mock | 全て最小値 | 200, success: true |
| ADV-021 | 最大座標・速度 | Mock | 全て最大値 | 200, success: true |
| ADV-022 | 速度範囲外 | Mock | speed: 61 | 400, INVALID_PARAMETER |

### 5.3 /drone/rc_control - リアルタイム制御

#### 境界値テスト
| ID | テスト名 | 環境 | 全速度 | 期待結果 |
|----|----------|------|--------|----------|
| ADV-030 | 最小速度 | Mock | -100 | 200, success: true |
| ADV-031 | 最大速度 | Mock | 100 | 200, success: true |
| ADV-032 | 速度0 | Mock | 0 | 200, success: true |
| ADV-033 | 範囲外+ | Mock | 101 | 400, INVALID_PARAMETER |
| ADV-034 | 範囲外- | Mock | -101 | 400, INVALID_PARAMETER |

---

## 6. Camera API テストケース

### 6.1 /camera/stream/start - ストリーミング開始

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-001 | 初回開始 | Mock | 未開始状態 | 200, success: true |
| CAM-002 | 実機開始 | Real | ドローン接続済み | 200, stream available |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-003 | 重複開始 | Mock | 既に開始済み | 409, STREAMING_ALREADY_STARTED |
| CAM-004 | 未接続開始 | Mock | ドローン未接続 | 503, DRONE_NOT_CONNECTED |

### 6.2 /camera/stream/stop - ストリーミング停止

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-010 | 正常停止 | Mock | 開始状態から | 200, success: true |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-011 | 未開始停止 | Mock | 未開始状態 | 200, success: true (idempotent) |

### 6.3 /camera/stream - ストリーム取得

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-020 | ストリーム取得 | Mock | 開始済み | 200, multipart/x-mixed-replace |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-021 | 未開始取得 | Mock | 未開始状態 | 404, STREAMING_NOT_STARTED |
| CAM-022 | 未接続取得 | Mock | ドローン未接続 | 503, DRONE_NOT_CONNECTED |

### 6.4 /camera/photo - 写真撮影

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-030 | 通常撮影 | Mock/Real | ドローン接続済み | 200, success: true |

### 6.5 /camera/video/start、/camera/video/stop - 動画録画

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| CAM-040 | 録画開始 | Mock | 接続済み | 200, success: true |
| CAM-041 | 録画停止 | Mock | 録画中 | 200, success: true |

### 6.6 /camera/settings - カメラ設定

#### 境界値テスト
| ID | テスト名 | 環境 | resolution | fps | bitrate | 期待結果 |
|----|----------|------|------------|-----|---------|----------|
| CAM-050 | 高解像度設定 | Mock | "high" | "high" | 5 | 200, success: true |
| CAM-051 | 低解像度設定 | Mock | "low" | "low" | 1 | 200, success: true |
| CAM-052 | 範囲外bitrate | Mock | "high" | "high" | 6 | 400, INVALID_PARAMETER |
| CAM-053 | 無効resolution | Mock | "invalid" | "high" | 3 | 400, INVALID_PARAMETER |

---

## 7. Sensors API テストケース

### 7.1 /drone/status - ドローン状態取得

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| SEN-001 | 状態取得 | Mock | 接続済み | 200, 全センサーデータ |
| SEN-002 | 実機状態取得 | Real | 接続済み | 200, リアルセンサーデータ |

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| SEN-003 | 未接続状態取得 | Mock | 未接続 | 503, DRONE_NOT_CONNECTED |

### 7.2 /drone/battery - バッテリー取得

#### 境界値テスト
| ID | テスト名 | 環境 | mock battery | 期待結果 |
|----|----------|------|--------------|----------|
| SEN-010 | 満充電 | Mock | 100 | 200, battery: 100 |
| SEN-011 | 空バッテリー | Mock | 0 | 200, battery: 0 |
| SEN-012 | 中間値 | Mock | 50 | 200, battery: 50 |

### 7.3 /drone/height - 高度取得

#### 境界値テスト
| ID | テスト名 | 環境 | mock height | 期待結果 |
|----|----------|------|-------------|----------|
| SEN-020 | 地上 | Mock | 0 | 200, height: 0 |
| SEN-021 | 最大高度 | Mock | 3000 | 200, height: 3000 |
| SEN-022 | 通常飛行高度 | Mock | 100 | 200, height: 100 |

### 7.4 /drone/temperature - 温度取得

#### 境界値テスト
| ID | テスト名 | 環境 | mock temp | 期待結果 |
|----|----------|------|-----------|----------|
| SEN-030 | 最低温度 | Mock | 0 | 200, temperature: 0 |
| SEN-031 | 最高温度 | Mock | 90 | 200, temperature: 90 |
| SEN-032 | 正常温度 | Mock | 25 | 200, temperature: 25 |

### 7.5-7.9 その他センサー

各センサー（flight_time, barometer, distance_tof, acceleration, velocity, attitude）について、
正常値・境界値・異常系のテストケースを同様に定義。

---

## 8. Settings API テストケース

### 8.1 /drone/wifi - WiFi設定

#### 境界値テスト
| ID | テスト名 | 環境 | ssid | password | 期待結果 |
|----|----------|------|------|----------|----------|
| SET-001 | 最短SSID | Mock | "a" | "password123" | 200, success: true |
| SET-002 | 最長SSID | Mock | "a"×32 | "password123" | 200, success: true |
| SET-003 | 最短パスワード | Mock | "MyWiFi" | "a" | 200, success: true |
| SET-004 | 最長パスワード | Mock | "MyWiFi" | "a"×64 | 200, success: true |
| SET-005 | 範囲外SSID | Mock | "a"×33 | "pass" | 400, INVALID_PARAMETER |
| SET-006 | 範囲外パスワード | Mock | "MyWiFi" | "a"×65 | 400, INVALID_PARAMETER |

### 8.2 /drone/command - 任意コマンド

#### 境界値テスト
| ID | テスト名 | 環境 | timeout | 期待結果 |
|----|----------|------|---------|----------|
| SET-010 | 最短タイムアウト | Mock | 1 | 200, response data |
| SET-011 | 最長タイムアウト | Mock | 30 | 200, response data |
| SET-012 | 範囲外小 | Mock | 0 | 400, INVALID_PARAMETER |
| SET-013 | 範囲外大 | Mock | 31 | 400, INVALID_PARAMETER |

### 8.3 /drone/speed - 速度設定

#### 境界値テスト
| ID | テスト名 | 環境 | speed | 期待結果 |
|----|----------|------|-------|----------|
| SET-020 | 最小速度 | Mock | 1.0 | 200, success: true |
| SET-021 | 最大速度 | Mock | 15.0 | 200, success: true |
| SET-022 | 範囲外小 | Mock | 0.9 | 400, INVALID_PARAMETER |
| SET-023 | 範囲外大 | Mock | 15.1 | 400, INVALID_PARAMETER |

---

## 9. Mission Pad API テストケース

### 9.1-9.5 ミッションパッド関連

各ミッションパッドAPI（enable, disable, detection_direction, go_xyz, status）について、
正常系・異常系・境界値テストを定義。

#### 特記事項
- mission_pad_id: 1-8の範囲
- detection_direction: 0,1,2の値
- 座標系は通常移動と同じ-500〜500cm

---

## 10. Object Tracking API テストケース

### 10.1-10.3 物体追跡関連

tracking_mode: "center" / "follow"の境界値テストを含む。

---

## 11. Model Management API テストケース

### 11.1 /model/train - モデル訓練

#### 異常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| MOD-001 | 大ファイル | Mock | ファイル>制限 | 413, FILE_TOO_LARGE |
| MOD-002 | 無効フォーマット | Mock | .txt画像 | 400, UNSUPPORTED_FORMAT |

### 11.2 /model/list - モデル一覧

#### 正常系テスト
| ID | テスト名 | 環境 | 条件 | 期待結果 |
|----|----------|------|------|----------|
| MOD-010 | 一覧取得 | Mock | - | 200, models配列 |

---

## 性能テストケース

### レスポンス時間テスト
| API種別 | 目標レスポンス時間 | 測定環境 |
|---------|-------------------|----------|
| 軽量API (status, sensors) | <50ms | Mock/Real |
| 制御API (move, rotate) | <100ms | Mock/Real |
| 重API (stream, train) | <500ms | Mock/Real |

### 負荷テストケース
| シナリオ | 同時接続数 | 持続時間 | 成功率目標 |
|----------|------------|----------|------------|
| センサー監視 | 10 | 30分 | >99% |
| 制御コマンド | 5 | 10分 | >95% |
| ストリーミング | 3 | 60分 | >98% |

---

## 統合テストシナリオ

### シナリオ1: 基本飛行ミッション
1. connect → takeoff → move(forward,100) → rotate(clockwise,90) → land → disconnect

### シナリオ2: 撮影ミッション  
1. connect → takeoff → stream/start → move(up,50) → photo → stream/stop → land

### シナリオ3: 緊急時対応
1. connect → takeoff → move → emergency → 状態確認

### シナリオ4: 物体追跡ミッション
1. connect → takeoff → tracking/start → 一定時間待機 → tracking/stop → land

---

## 安全対策（Real環境）

### 必須条件
- 屋内飛行のみ（GPS無効環境）
- 最大高度150cm制限
- 飛行範囲2m×2m以内
- 人的監視者必須配置
- 緊急停止装置準備

### 禁止事項
- 屋外飛行
- 無人実行
- 高度制限解除
- 制限区域外飛行

---

## 総テストケース数

| カテゴリ | 正常系 | 境界値 | 異常系 | 小計 |
|----------|--------|--------|--------|------|
| System | 1 | 0 | 1 | 2 |
| Connection | 2 | 0 | 5 | 7 |
| Flight Control | 4 | 0 | 8 | 12 |
| Movement | 9 | 9 | 8 | 26 |
| Advanced Movement | 3 | 12 | 2 | 17 |
| Camera | 5 | 4 | 5 | 14 |
| Sensors | 9 | 9 | 1 | 19 |
| Settings | 3 | 12 | 0 | 15 |
| Mission Pad | 5 | 8 | 2 | 15 |
| Object Tracking | 3 | 2 | 1 | 6 |
| Model Management | 1 | 0 | 2 | 3 |
| 性能・統合 | 4 | 3 | 0 | 7 |
| **合計** | **49** | **59** | **35** | **143** |

**各MCPツール別テストケース詳細展開により、実際のテストケース総数は約500個となります。**

---

## 実装優先度

### P0 (必須・Week 4内)
- Connection, Flight Control, Movement基本API
- Mock環境での全境界値・異常系テスト
- 基本的な統合テストシナリオ

### P1 (高優先度)
- Camera, Sensors API
- Real環境での安全テスト
- 性能テスト基盤

### P2 (中優先度)  
- Advanced Movement, Settings API
- 負荷テスト
- 複雑な統合シナリオ

### P3 (低優先度)
- Mission Pad, Object Tracking, Model Management
- エッジケーステスト
- 最適化テスト

---

この包括的なテストケース定義により、MCP Tools の品質と信頼性を保証し、
Claude Code との統合時の安全性を確保します。