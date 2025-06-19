# MCPツール シーケンス図

## 概要

MCPツールシステムの各ユースケースについて、正常系・代替系・異常系のシーケンス図を詳細に定義します。これらの図は、Claude Code、MCPサーバー、API Bridge、FastAPI Backend、Tello EDU間の相互作用を時系列で示します。

## UC01: ドローン接続管理

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 正常系: ドローン接続成功

    Claude->>MCP: tool_call("drone_connect", {})
    activate MCP
    MCP->>MCP: validate_request()
    MCP->>Bridge: connect_to_drone()
    activate Bridge
    Bridge->>Bridge: setup_http_client()
    Bridge->>API: POST /drone/connect
    activate API
    API->>API: initialize_drone_service()
    API->>Drone: UDP connection (8889)
    activate Drone
    Drone-->>API: connection_ack
    deactivate Drone
    API-->>Bridge: {"status": "connected", "drone_info": {...}}
    deactivate API
    Bridge-->>MCP: DroneConnectionResult
    deactivate Bridge
    MCP-->>Claude: "Successfully connected to Tello EDU drone. Battery: 85%, Temperature: 25°C"
    deactivate MCP
```

### 代替系シーケンス（リトライあり）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 代替系: 接続タイムアウト → リトライ成功

    Claude->>MCP: tool_call("drone_connect", {})
    activate MCP
    MCP->>Bridge: connect_to_drone()
    activate Bridge
    Bridge->>API: POST /drone/connect
    activate API
    API->>Drone: UDP connection (8889)
    Note over Drone: タイムアウト
    API-->>Bridge: {"error": "connection_timeout", "code": 408}
    deactivate API
    Bridge->>Bridge: start_retry_strategy(attempt=1)
    Note over Bridge: 2秒待機
    Bridge->>API: POST /drone/connect (retry 1)
    activate API
    API->>Drone: UDP connection (8889)
    activate Drone
    Drone-->>API: connection_ack
    deactivate Drone
    API-->>Bridge: {"status": "connected", "drone_info": {...}}
    deactivate API
    Bridge-->>MCP: DroneConnectionResult (success after retry)
    deactivate Bridge
    MCP-->>Claude: "Connected to drone after 1 retry. Battery: 82%, Temperature: 24°C"
    deactivate MCP
```

### 異常系シーケンス（接続失敗）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 異常系: 全リトライ失敗

    Claude->>MCP: tool_call("drone_connect", {})
    activate MCP
    MCP->>Bridge: connect_to_drone()
    activate Bridge
    
    loop 5 retries
        Bridge->>API: POST /drone/connect
        activate API
        API->>Drone: UDP connection attempt
        Note over Drone: 応答なし
        API-->>Bridge: {"error": "connection_failed", "code": 500}
        deactivate API
        Bridge->>Bridge: exponential_backoff()
    end
    
    Bridge->>Bridge: max_retries_exceeded()
    Bridge-->>MCP: DroneConnectionError("Max retries exceeded")
    deactivate Bridge
    MCP-->>Claude: "Failed to connect to drone after 5 attempts. Please check: 1) Drone power, 2) WiFi connectivity, 3) Drone proximity. Error: connection_failed"
    deactivate MCP
```

## UC04: 基本飛行操作（離陸）

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 正常系: 離陸成功

    Claude->>MCP: tool_call("drone_takeoff", {})
    activate MCP
    MCP->>Bridge: execute_takeoff()
    activate Bridge
    Bridge->>Bridge: pre_flight_safety_check()
    Bridge->>API: GET /drone/battery
    activate API
    API-->>Bridge: {"battery": 75}
    deactivate API
    Bridge->>Bridge: validate_battery_level(75) ✓
    Bridge->>API: POST /drone/takeoff
    activate API
    API->>Drone: takeoff command
    activate Drone
    Drone->>Drone: execute_takeoff()
    Drone-->>API: takeoff_success
    deactivate Drone
    API-->>Bridge: {"status": "airborne", "height": 1.2}
    deactivate API
    Bridge->>Bridge: post_flight_verification()
    Bridge-->>MCP: TakeoffResult(success=True, height=1.2)
    deactivate Bridge
    MCP-->>Claude: "Drone successfully took off and is now hovering at 1.2 meters altitude. Battery: 75%"
    deactivate MCP
```

### 代替系シーケンス（バッテリー低下警告）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 代替系: バッテリー低下でも離陸実行

    Claude->>MCP: tool_call("drone_takeoff", {})
    activate MCP
    MCP->>Bridge: execute_takeoff()
    activate Bridge
    Bridge->>API: GET /drone/battery
    activate API
    API-->>Bridge: {"battery": 25}
    deactivate API
    Bridge->>Bridge: validate_battery_level(25)
    Note over Bridge: 25% < 30% = WARNING level
    Bridge->>Bridge: calculate_flight_time(25%) = ~3min
    Bridge->>API: POST /drone/takeoff
    activate API
    API->>Drone: takeoff command
    activate Drone
    Drone-->>API: takeoff_success
    deactivate Drone
    API-->>Bridge: {"status": "airborne", "height": 1.1}
    deactivate API
    Bridge-->>MCP: TakeoffResult(success=True, warning="low_battery")
    deactivate Bridge
    MCP-->>Claude: "Drone took off successfully but battery is low (25%). Estimated flight time: 3 minutes. Consider landing soon for safety."
    deactivate MCP
```

### 異常系シーケンス（バッテリー不足）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 異常系: バッテリー不足で離陸拒否

    Claude->>MCP: tool_call("drone_takeoff", {})
    activate MCP
    MCP->>Bridge: execute_takeoff()
    activate Bridge
    Bridge->>API: GET /drone/battery
    activate API
    API-->>Bridge: {"battery": 15}
    deactivate API
    Bridge->>Bridge: validate_battery_level(15%)
    Note over Bridge: 15% < 20% = CRITICAL level
    Bridge-->>MCP: TakeoffError("battery_too_low", battery=15)
    deactivate Bridge
    MCP-->>Claude: "Takeoff cancelled: Battery level too low (15%). Minimum 20% required for safe flight. Please charge the drone before attempting takeoff."
    deactivate MCP
```

## UC05: 緊急停止制御

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Safety as Safety Monitor
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Safety,Drone: 正常系: 緊急停止成功

    Safety->>Claude: "EMERGENCY! Land immediately!"
    Claude->>MCP: tool_call("drone_emergency", {})
    activate MCP
    Note over MCP: 最優先処理
    MCP->>Bridge: execute_emergency_stop()
    activate Bridge
    Bridge->>Bridge: cancel_all_pending_commands()
    Bridge->>API: POST /drone/emergency
    activate API
    API->>API: emergency_mode_activation()
    API->>Drone: emergency command (highest priority)
    activate Drone
    Drone->>Drone: immediate_motor_stop()
    Drone-->>API: emergency_executed
    deactivate Drone
    API->>API: log_emergency_event()
    API-->>Bridge: {"status": "emergency_landed", "mode": "emergency"}
    deactivate API
    Bridge->>Bridge: set_system_mode("emergency")
    Bridge-->>MCP: EmergencyResult(success=True, time=0.8s)
    deactivate Bridge
    MCP-->>Claude: "EMERGENCY STOP EXECUTED. Drone landed immediately. All systems in emergency mode. Manual inspection required before next flight."
    deactivate MCP
    Claude-->>Safety: "Emergency landing completed successfully"
```

### 異常系シーケンス（通信断絶）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 異常系: 通信断絶時の緊急処理

    Claude->>MCP: tool_call("drone_emergency", {})
    activate MCP
    MCP->>Bridge: execute_emergency_stop()
    activate Bridge
    Bridge->>API: POST /drone/emergency
    Note over API: 通信断絶
    Bridge->>Bridge: detect_communication_failure()
    Bridge->>Bridge: start_connection_recovery()
    
    loop Recovery attempts
        Bridge->>API: Health check
        Note over API: Still disconnected
        Bridge->>Bridge: wait_and_retry()
    end
    
    Note over Bridge: Recovery timeout
    Bridge->>Bridge: assume_drone_failsafe_activated()
    Bridge-->>MCP: EmergencyResult(success=unknown, status="communication_lost")
    deactivate Bridge
    MCP-->>Claude: "EMERGENCY COMMAND SENT but communication lost. Drone should activate built-in failsafe (auto-land). Monitor drone visually and attempt manual recovery if needed."
    deactivate MCP
```

## UC07: 方向移動制御

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 正常系: 方向移動成功

    Claude->>MCP: tool_call("drone_move", {"direction": "forward", "distance": 200})
    activate MCP
    MCP->>MCP: validate_parameters(direction="forward", distance=200)
    MCP->>Bridge: execute_movement(forward, 200cm)
    activate Bridge
    Bridge->>Bridge: safety_check_movement()
    Bridge->>API: GET /drone/status
    activate API
    API-->>Bridge: {"status": "airborne", "height": 1.2, "position": {...}}
    deactivate API
    Bridge->>Bridge: calculate_safe_movement()
    Bridge->>API: POST /drone/move {"direction": "forward", "distance": 200}
    activate API
    API->>Drone: move forward 200
    activate Drone
    Drone->>Drone: execute_movement()
    Drone-->>API: movement_complete
    deactivate Drone
    API-->>Bridge: {"status": "completed", "new_position": {...}}
    deactivate API
    Bridge->>Bridge: verify_movement_completion()
    Bridge-->>MCP: MovementResult(success=True, distance=200)
    deactivate Bridge
    MCP-->>Claude: "Drone moved forward 200cm successfully. Current position updated."
    deactivate MCP
```

### 代替系シーケンス（パラメータ調整）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend

    Note over Claude,API: 代替系: 距離パラメータ調整

    Claude->>MCP: tool_call("drone_move", {"direction": "up", "distance": 600})
    activate MCP
    MCP->>MCP: validate_parameters(direction="up", distance=600)
    Note over MCP: 600 > 500 (max limit)
    MCP->>MCP: adjust_to_safe_parameters(500)
    MCP-->>Claude: "Requested distance (600cm) exceeds maximum safe limit. Adjusted to 500cm for safety. Proceeding with movement."
    MCP->>Bridge: execute_movement(up, 500cm)
    activate Bridge
    Bridge->>API: POST /drone/move {"direction": "up", "distance": 500}
    activate API
    API-->>Bridge: {"status": "completed"}
    deactivate API
    Bridge-->>MCP: MovementResult(success=True, adjusted=True)
    deactivate Bridge
    MCP-->>Claude: "Drone moved up 500cm (adjusted from 600cm for safety)."
    deactivate MCP
```

### 異常系シーケンス（移動中障害）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 異常系: 移動中の異常停止

    Claude->>MCP: tool_call("drone_move", {"direction": "right", "distance": 300})
    activate MCP
    MCP->>Bridge: execute_movement(right, 300cm)
    activate Bridge
    Bridge->>API: POST /drone/move {"direction": "right", "distance": 300}
    activate API
    API->>Drone: move right 300
    activate Drone
    Drone->>Drone: start_movement()
    Note over Drone: 150cm移動後に異常検知
    Drone->>Drone: emergency_stop()
    Drone-->>API: movement_interrupted (distance: 150)
    deactivate Drone
    API-->>Bridge: {"error": "movement_interrupted", "completed_distance": 150}
    deactivate API
    Bridge->>Bridge: analyze_interruption_cause()
    Bridge-->>MCP: MovementError("interrupted", completed=150, remaining=150)
    deactivate Bridge
    MCP-->>Claude: "Movement interrupted after 150cm due to safety system activation. Drone stopped at safe position. Remaining distance: 150cm. Please check surroundings before continuing."
    deactivate MCP
```

## UC10: 映像ストリーミング

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU
    participant Stream as Stream Handler

    Note over Claude,Stream: 正常系: ストリーミング開始成功

    Claude->>MCP: tool_call("camera_stream_start", {})
    activate MCP
    MCP->>Bridge: start_video_stream()
    activate Bridge
    Bridge->>API: POST /camera/stream/start
    activate API
    API->>Drone: enable video stream
    activate Drone
    Drone->>Stream: UDP video data (11111)
    activate Stream
    Drone-->>API: stream_started
    deactivate Drone
    API-->>Bridge: {"status": "streaming", "resolution": "720p", "fps": 30}
    deactivate API
    
    loop Continuous Streaming
        Stream->>API: video frame
        API->>API: process_frame()
        API->>Bridge: WebSocket frame data
        Bridge->>Bridge: monitor_stream_quality()
    end
    
    Bridge-->>MCP: StreamResult(status="active", quality="good")
    deactivate Bridge
    MCP-->>Claude: "Video streaming started successfully. Resolution: 720p, FPS: 30. Stream quality: good."
    deactivate MCP
    
    Note over Stream: ストリーミング継続中
    deactivate Stream
```

### 代替系シーケンス（品質低下対応）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 代替系: ネットワーク遅延による品質調整

    Note over Bridge: ストリーミング中
    Bridge->>Bridge: detect_network_latency(>200ms)
    Bridge->>API: POST /camera/settings {"quality": "medium"}
    activate API
    API->>Drone: adjust stream quality
    activate Drone
    Drone-->>API: quality_adjusted
    deactivate Drone
    API-->>Bridge: {"status": "quality_adjusted", "new_fps": 20}
    deactivate API
    Bridge->>Bridge: monitor_improvement()
    Bridge->>MCP: stream_quality_adjusted()
    MCP-->>Claude: "Stream quality automatically adjusted to medium (20 FPS) due to network latency. Monitoring for improvement."
    
    Note over Bridge: 30秒後
    Bridge->>Bridge: detect_network_improvement()
    Bridge->>API: POST /camera/settings {"quality": "high"}
    activate API
    API-->>Bridge: {"status": "restored", "fps": 30}
    deactivate API
    Bridge->>MCP: stream_quality_restored()
    MCP-->>Claude: "Network conditions improved. Stream quality restored to high (30 FPS)."
```

### 異常系シーケンス（ストリーミング停止）

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Claude,Drone: 異常系: ストリーミング突然停止

    Note over Bridge: ストリーミング中
    Bridge->>Bridge: detect_stream_loss()
    Bridge->>API: GET /camera/stream/status
    activate API
    API-->>Bridge: {"status": "disconnected", "error": "drone_communication_lost"}
    deactivate API
    Bridge->>Bridge: start_recovery_procedure()
    
    loop Recovery attempts (max 3)
        Bridge->>API: POST /camera/stream/start
        activate API
        API->>Drone: restart stream
        Note over Drone: 応答なし
        API-->>Bridge: {"error": "stream_restart_failed"}
        deactivate API
        Bridge->>Bridge: wait_and_retry(10s)
    end
    
    Bridge->>Bridge: recovery_failed()
    Bridge-->>MCP: StreamError("recovery_failed", last_error="drone_communication_lost")
    MCP-->>Claude: "Video stream lost and recovery failed after 3 attempts. Possible causes: 1) Drone communication issue, 2) Hardware malfunction. Please check drone status and restart if necessary."
```

## UC13: バッテリー監視

### 正常系シーケンス

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU
    participant Monitor as Battery Monitor

    Note over Claude,Monitor: 正常系: バッテリー監視開始

    Claude->>MCP: tool_call("drone_battery", {})
    activate MCP
    MCP->>Bridge: get_battery_status()
    activate Bridge
    Bridge->>API: GET /drone/battery
    activate API
    API->>Drone: battery query
    activate Drone
    Drone-->>API: battery_data
    deactivate Drone
    API-->>Bridge: {"battery": 65, "voltage": 3.8, "temperature": 26}
    deactivate API
    Bridge->>Monitor: start_continuous_monitoring()
    activate Monitor
    Bridge-->>MCP: BatteryResult(level=65, status="good")
    deactivate Bridge
    MCP-->>Claude: "Battery status: 65% (Good), Voltage: 3.8V, Temperature: 26°C. Continuous monitoring activated."
    deactivate MCP
    
    loop Continuous Monitoring
        Monitor->>API: GET /drone/battery
        activate API
        API-->>Monitor: current_battery_data
        deactivate API
        Monitor->>Monitor: analyze_trend()
    end
    
    deactivate Monitor
```

### 代替系シーケンス（バッテリー警告）

```mermaid
sequenceDiagram
    participant Monitor as Battery Monitor
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge

    Note over Monitor,Bridge: 代替系: バッテリー低下警告

    Note over Monitor: 監視中
    Monitor->>Monitor: detect_battery_drop(35% -> 25%)
    Monitor->>Bridge: battery_warning_trigger(25%)
    activate Bridge
    Bridge->>Bridge: assess_warning_level(25%)
    Note over Bridge: 25% = WARNING level
    Bridge->>MCP: battery_warning(level=25, recommended_action="land_soon")
    MCP-->>Claude: "⚠️ BATTERY WARNING: 25% remaining. Estimated flight time: 3-4 minutes. Recommend landing within 2 minutes for safety."
    Bridge->>Bridge: increase_monitoring_frequency()
    deactivate Bridge
    
    Note over Monitor: 高頻度監視開始
    loop High-frequency monitoring
        Monitor->>Monitor: check_battery_every_30s()
    end
```

### 異常系シーケンス（緊急バッテリー低下）

```mermaid
sequenceDiagram
    participant Monitor as Battery Monitor
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Monitor,Drone: 異常系: 緊急バッテリー低下

    Note over Monitor: 高頻度監視中
    Monitor->>Monitor: detect_critical_battery(15%)
    Monitor->>Bridge: critical_battery_alert(15%)
    activate Bridge
    Bridge->>Bridge: assess_critical_level(15%)
    Note over Bridge: 15% = CRITICAL level
    Bridge->>Bridge: initiate_emergency_protocol()
    Bridge->>MCP: critical_battery_emergency(level=15)
    MCP-->>Claude: "🚨 CRITICAL BATTERY: 15% remaining! Initiating emergency landing protocol."
    
    Bridge->>API: POST /drone/land (emergency=true)
    activate API
    API->>Drone: emergency land command
    activate Drone
    Drone->>Drone: emergency_land_procedure()
    Drone-->>API: emergency_land_initiated
    deactivate Drone
    API-->>Bridge: {"status": "emergency_landing", "eta": "30s"}
    deactivate API
    
    Bridge->>Bridge: monitor_emergency_landing()
    Bridge-->>MCP: EmergencyLandingResult(initiated=True, eta=30)
    deactivate Bridge
    MCP-->>Claude: "Emergency landing initiated due to critical battery (15%). Landing ETA: 30 seconds. Do not attempt further flight until fully charged."
```

## UC16: 自然言語コマンド処理

### 正常系シーケンス（複合コマンド）

```mermaid
sequenceDiagram
    participant Human as Human User
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge
    participant API as FastAPI Backend
    participant Drone as Tello EDU

    Note over Human,Drone: 正常系: 複合コマンド実行

    Human->>Claude: "Take off, move forward 3 meters, take a photo, then land"
    Claude->>Claude: parse_natural_language()
    Claude->>Claude: extract_action_sequence()
    Note over Claude: Sequence: [takeoff, move_forward_300cm, take_photo, land]
    
    Claude->>MCP: tool_call("drone_takeoff", {})
    activate MCP
    MCP->>Bridge: execute_takeoff()
    Bridge-->>MCP: success
    MCP-->>Claude: "takeoff_completed"
    deactivate MCP
    
    Claude->>MCP: tool_call("drone_move", {"direction": "forward", "distance": 300})
    activate MCP
    MCP->>Bridge: execute_movement()
    Bridge-->>MCP: success
    MCP-->>Claude: "movement_completed"
    deactivate MCP
    
    Claude->>MCP: tool_call("camera_take_photo", {})
    activate MCP
    MCP->>Bridge: capture_photo()
    Bridge-->>MCP: success
    MCP-->>Claude: "photo_captured"
    deactivate MCP
    
    Claude->>MCP: tool_call("drone_land", {})
    activate MCP
    MCP->>Bridge: execute_landing()
    Bridge-->>MCP: success
    MCP-->>Claude: "landing_completed"
    deactivate MCP
    
    Claude-->>Human: "Mission completed successfully: ✅ Took off ✅ Moved forward 3 meters ✅ Captured photo ✅ Landed safely. Photo saved to storage."
```

### 代替系シーケンス（曖昧な指示の明確化）

```mermaid
sequenceDiagram
    participant Human as Human User
    participant Claude as Claude Code
    participant MCP as MCP Server

    Note over Human,MCP: 代替系: 曖昧な指示の明確化

    Human->>Claude: "Move the drone a bit to the side"
    Claude->>Claude: parse_natural_language()
    Claude->>Claude: detect_ambiguity()
    Note over Claude: "a bit" = unclear distance<br/>"to the side" = left or right?
    
    Claude-->>Human: "I need clarification on your command: 1) How far should I move the drone? (suggest: 1-5 meters) 2) Which direction - left or right? 3) What speed - slow, normal, or fast?"
    Human->>Claude: "2 meters to the right, slowly"
    Claude->>Claude: parse_clarified_command()
    Note over Claude: direction=right, distance=200cm, speed=slow
    
    Claude->>MCP: tool_call("drone_move", {"direction": "right", "distance": 200, "speed": "slow"})
    activate MCP
    MCP-->>Claude: success
    deactivate MCP
    Claude-->>Human: "Moved drone 2 meters to the right at slow speed. Command completed."
```

### 異常系シーケンス（実行不可能な組み合わせ）

```mermaid
sequenceDiagram
    participant Human as Human User
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Bridge as API Bridge

    Note over Human,Bridge: 異常系: 実行不可能なコマンド

    Human->>Claude: "Take a photo while the drone is moving up 5 meters at maximum speed"
    Claude->>Claude: parse_natural_language()
    Claude->>Claude: analyze_feasibility()
    Note over Claude: 高速移動中の写真撮影<br/>= ブレの可能性 + 安全性問題
    
    Claude->>MCP: tool_call("drone_move", {"direction": "up", "distance": 500, "speed": "fast"})
    activate MCP
    MCP->>Bridge: validate_movement_safety()
    Bridge->>Bridge: check_photo_during_movement()
    Bridge-->>MCP: MovementError("unsafe_photo_during_fast_movement")
    deactivate MCP
    
    Claude-->>Human: "I cannot execute this command safely. Taking photos during fast upward movement may result in blurred images and pose safety risks. Alternative suggestions: 1) Move up 5 meters, then take photo, 2) Take photo first, then move up, 3) Move slowly while taking photo. Which would you prefer?"
    
    Human->>Claude: "Option 1 - move up first, then take photo"
    Claude->>Claude: execute_safe_alternative()
    Note over Claude: Safe sequence execution
```

## パフォーマンス・品質指標

### レスポンス時間目標

| 操作タイプ | 目標時間 | 測定ポイント |
|-----------|---------|-------------|
| MCP Tool Call | < 50ms | Claude → MCP Server |
| API Bridge Call | < 100ms | MCP → FastAPI |
| ドローンコマンド | < 200ms | API → Drone response |
| 緊急停止 | < 500ms | 最優先実行 |
| バッテリー取得 | < 30ms | センサーデータ取得 |
| 映像ストリーミング | < 150ms | フレーム遅延 |

### エラー処理基準

| エラータイプ | 自動リトライ | 最大試行回数 | 人的介入 |
|-------------|-------------|-------------|----------|
| 接続タイムアウト | ✓ | 5回 | リトライ失敗時 |
| 通信断絶 | ✓ | 3回 | 即座 |
| バッテリー不足 | ✗ | - | 即座 |
| 移動中断 | ✓ | 2回 | 2回失敗時 |
| ストリーミング失敗 | ✓ | 3回 | 回復不可時 |
| 緊急停止失敗 | ✗ | - | 即座 |

### 安全性保証

1. **多層防御**: Claude → MCP → API → Drone の各層で安全チェック
2. **フェイルセーフ**: 通信断絶時のドローン自動安全機能
3. **人的監視**: 全自動化ではなく人的監視者による最終安全確認
4. **ログ記録**: 全操作の詳細ログによる事後分析可能性