# MCP Tools Test Cases Documentation

## Overview

This document provides comprehensive test cases for all MCP (Model Context Protocol) tools implementing the MFG Drone Backend API. It covers 44 API endpoints across 10 categories with focus on boundary value testing and comprehensive error handling.

## Test Strategy

### Testing Modes
1. **Mock Mode**: Tests without real hardware using TelloStub
2. **Real Hardware Mode**: Tests with actual Tello EDU drone
3. **Hybrid Mode**: Mock for safety-critical tests, real hardware for integration validation

### Test Categories
- **Boundary Value Analysis**: Testing parameter limits (min, max, valid, invalid)
- **Error Handling**: Comprehensive error scenario coverage
- **State Validation**: Drone state transition testing
- **Performance Testing**: Response time and reliability
- **Integration Testing**: End-to-end MCP protocol testing

---

## 1. Connection Tools Test Cases

### 1.1 drone_connect

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| CONN_001 | Basic connection success | `{}` | `{success: true, message: "ドローン接続成功"}` | Both |
| CONN_002 | Connection with retry | `{}` | Connection after retry attempts | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| CONN_E001 | Connection timeout | `{}` | Connection timeout error | COMMAND_TIMEOUT | Mock |
| CONN_E002 | Network unreachable | `{}` | Network connection failed | DRONE_CONNECTION_FAILED | Mock |
| CONN_E003 | Already connected | `{}` (while connected) | Already connected error | ALREADY_CONNECTED | Both |

### 1.2 drone_disconnect

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| DISC_001 | Basic disconnection | `{}` | `{success: true, message: "ドローン切断成功"}` | Both |
| DISC_002 | Graceful disconnect while flying | `{}` (while flying) | Lands then disconnects | Real only |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| DISC_E001 | Disconnect when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |
| DISC_E002 | Disconnect failure | `{}` | Disconnection failed | COMMAND_FAILED | Mock |

### 1.3 drone_status

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| STAT_001 | Get status when connected | `{}` | Complete drone status object | Both |
| STAT_002 | Get status when flying | `{}` | Status with flight data | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| STAT_E001 | Status when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |

---

## 2. Flight Control Tools Test Cases

### 2.1 drone_takeoff

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| TAKE_001 | Normal takeoff | `{}` | `{success: true, message: "離陸成功"}` | Both |
| TAKE_002 | Takeoff with sufficient battery | `{}` (battery > 20%) | Successful takeoff | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| TAKE_E001 | Takeoff while flying | `{}` | Already flying error | ALREADY_FLYING | Both |
| TAKE_E002 | Takeoff with low battery | `{}` (battery < 10%) | Low battery error | COMMAND_FAILED | Mock |
| TAKE_E003 | Takeoff when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |

### 2.2 drone_land

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| LAND_001 | Normal landing | `{}` | `{success: true, message: "着陸成功"}` | Both |
| LAND_002 | Safe landing from height | `{}` | Gradual descent and landing | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| LAND_E001 | Land when not flying | `{}` | Not flying error | NOT_FLYING | Both |
| LAND_E002 | Land when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |

### 2.3 drone_emergency

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| EMER_001 | Emergency stop while flying | `{}` | Immediate motor stop | Both |
| EMER_002 | Emergency stop on ground | `{}` | Emergency acknowledged | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| EMER_E001 | Emergency when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |

---

## 3. Movement Tools Test Cases

### 3.1 drone_move

#### Boundary Value Analysis
| Parameter | Type | Min | Max | Valid Test Values | Invalid Test Values |
|-----------|------|-----|-----|------------------|-------------------|
| direction | enum | - | - | [up, down, left, right, forward, back] | [invalid, "", null, 123] |
| distance | integer | 20 | 500 | [20, 100, 500] | [19, 501, -10, 0] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| MOVE_001 | Move forward minimum | `{direction: "forward", distance: 20}` | Move success | Both |
| MOVE_002 | Move up maximum | `{direction: "up", distance: 500}` | Move success | Both |
| MOVE_003 | Move in all directions | Each direction with distance 100 | Move success for each | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| MOVE_E001 | Distance below minimum | `{direction: "forward", distance: 19}` | Invalid parameter | INVALID_PARAMETER | Both |
| MOVE_E002 | Distance above maximum | `{direction: "forward", distance: 501}` | Invalid parameter | INVALID_PARAMETER | Both |
| MOVE_E003 | Invalid direction | `{direction: "invalid", distance: 100}` | Invalid parameter | INVALID_PARAMETER | Both |
| MOVE_E004 | Negative distance | `{direction: "forward", distance: -50}` | Invalid parameter | INVALID_PARAMETER | Both |
| MOVE_E005 | Move when not flying | `{direction: "forward", distance: 100}` | Not flying error | NOT_FLYING | Both |

### 3.2 drone_rotate

#### Boundary Value Analysis
| Parameter | Type | Min | Max | Valid Test Values | Invalid Test Values |
|-----------|------|-----|-----|------------------|-------------------|
| direction | enum | - | - | [clockwise, counter_clockwise] | [invalid, "", null] |
| angle | integer | 1 | 360 | [1, 90, 180, 360] | [0, 361, -90] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| ROT_001 | Rotate clockwise minimum | `{direction: "clockwise", angle: 1}` | Rotation success | Both |
| ROT_002 | Rotate counter-clockwise maximum | `{direction: "counter_clockwise", angle: 360}` | Rotation success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| ROT_E001 | Angle below minimum | `{direction: "clockwise", angle: 0}` | Invalid parameter | INVALID_PARAMETER | Both |
| ROT_E002 | Angle above maximum | `{direction: "clockwise", angle: 361}` | Invalid parameter | INVALID_PARAMETER | Both |
| ROT_E003 | Invalid direction | `{direction: "invalid", angle: 90}` | Invalid parameter | INVALID_PARAMETER | Both |

### 3.3 drone_flip

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| FLIP_001 | Flip in all directions | `{direction: "left/right/forward/back"}` | Flip success for each | Mock only |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| FLIP_E001 | Invalid direction | `{direction: "invalid"}` | Invalid parameter | INVALID_PARAMETER | Both |
| FLIP_E002 | Flip when not flying | `{direction: "left"}` | Not flying error | NOT_FLYING | Both |

### 3.4 drone_go_xyz

#### Boundary Value Analysis
| Parameter | Type | Min | Max | Valid Test Values | Invalid Test Values |
|-----------|------|-----|-----|------------------|-------------------|
| x | integer | -500 | 500 | [-500, 0, 500] | [-501, 501] |
| y | integer | -500 | 500 | [-500, 0, 500] | [-501, 501] |
| z | integer | -500 | 500 | [-500, 0, 500] | [-501, 501] |
| speed | integer | 10 | 100 | [10, 50, 100] | [9, 101] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| XYZ_001 | Move to origin | `{x: 0, y: 0, z: 0, speed: 50}` | Move success | Both |
| XYZ_002 | Move to boundaries | All boundary combinations | Move success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| XYZ_E001 | X coordinate out of range | `{x: -501, y: 0, z: 0, speed: 50}` | Invalid parameter | INVALID_PARAMETER | Both |
| XYZ_E002 | Speed below minimum | `{x: 0, y: 0, z: 0, speed: 9}` | Invalid parameter | INVALID_PARAMETER | Both |

### 3.5 drone_curve

#### Boundary Value Analysis
| Parameter | Type | Min | Max | Valid Test Values | Invalid Test Values |
|-----------|------|-----|-----|------------------|-------------------|
| x1, y1, z1, x2, y2, z2 | integer | -500 | 500 | [-500, 0, 500] | [-501, 501] |
| speed | integer | 10 | 60 | [10, 30, 60] | [9, 61] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| CURV_001 | Simple curve | Valid curve coordinates | Curve flight success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| CURV_E001 | Speed above maximum | Valid coords + speed: 61 | Invalid parameter | INVALID_PARAMETER | Both |

### 3.6 drone_rc_control

#### Boundary Value Analysis
| Parameter | Type | Min | Max | Valid Test Values | Invalid Test Values |
|-----------|------|-----|-----|------------------|-------------------|
| left_right_velocity | integer | -100 | 100 | [-100, 0, 100] | [-101, 101] |
| forward_backward_velocity | integer | -100 | 100 | [-100, 0, 100] | [-101, 101] |
| up_down_velocity | integer | -100 | 100 | [-100, 0, 100] | [-101, 101] |
| yaw_velocity | integer | -100 | 100 | [-100, 0, 100] | [-101, 101] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| RC_001 | Hover position | All velocities: 0 | Control success | Both |
| RC_002 | Maximum forward | `{lr:0, fb:100, ud:0, yaw:0}` | Control success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| RC_E001 | Velocity out of range | Any velocity > 100 or < -100 | Invalid parameter | INVALID_PARAMETER | Both |

---

## 4. Camera Tools Test Cases

### 4.1 camera_stream_start

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| CAM_001 | Start stream when connected | `{}` | Stream start success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| CAM_E001 | Start when already streaming | `{}` | Already streaming | STREAMING_ALREADY_STARTED | Both |
| CAM_E002 | Start when not connected | `{}` | Not connected error | DRONE_NOT_CONNECTED | Both |

### 4.2 camera_stream_stop

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| CAM_002 | Stop active stream | `{}` | Stream stop success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| CAM_E003 | Stop when not streaming | `{}` | Not streaming error | STREAMING_NOT_STARTED | Both |

### 4.3 camera_take_photo

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| PHOTO_001 | Take photo when connected | `{}` | Photo capture success | Both |

### 4.4 camera_start_recording

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| REC_001 | Start recording | `{}` | Recording start success | Both |

### 4.5 camera_stop_recording

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| REC_002 | Stop recording | `{}` | Recording stop success | Both |

### 4.6 camera_settings

#### Boundary Value Analysis
| Parameter | Type | Valid Values | Invalid Values |
|-----------|------|--------------|----------------|
| resolution | enum | [high, low] | [invalid, "", null] |
| fps | enum | [high, middle, low] | [invalid, "", null] |
| bitrate | integer | [1, 2, 3, 4, 5] | [0, 6, -1] |

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| SET_001 | Valid settings | `{resolution: "high", fps: "middle", bitrate: 3}` | Settings update success | Both |

#### Invalid Test Cases
| Test ID | Description | Input | Expected Error | Error Code | Mock/Real |
|---------|-------------|-------|----------------|------------|-----------|
| SET_E001 | Invalid bitrate | `{resolution: "high", fps: "middle", bitrate: 6}` | Invalid parameter | INVALID_PARAMETER | Both |

---

## 5. Sensor Tools Test Cases

### 5.1 drone_battery

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| BAT_001 | Get battery level | `{}` | `{battery: 0-100}` | Both |

#### Expected Value Ranges
| Parameter | Type | Min | Max | Notes |
|-----------|------|-----|-----|-------|
| battery | integer | 0 | 100 | Percentage value |

### 5.2 drone_temperature

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| TEMP_001 | Get temperature | `{}` | `{temperature: 0-90}` | Both |

#### Expected Value Ranges
| Parameter | Type | Min | Max | Notes |
|-----------|------|-----|-----|-------|
| temperature | integer | 0 | 90 | Celsius degrees |

### 5.3 drone_flight_time

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| TIME_001 | Get flight time | `{}` | `{flight_time: ≥0}` | Both |

### 5.4 drone_barometer

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| BARO_001 | Get barometer reading | `{}` | `{barometer: ≥0}` | Both |

### 5.5 drone_distance_tof

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| TOF_001 | Get ToF distance | `{}` | `{distance_tof: ≥0}` | Both |

### 5.6 drone_acceleration

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| ACCEL_001 | Get acceleration | `{}` | `{acceleration: {x, y, z}}` | Both |

### 5.7 drone_velocity

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| VEL_001 | Get velocity | `{}` | `{velocity: {x, y, z}}` | Both |

### 5.8 drone_attitude

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| ATT_001 | Get attitude | `{}` | `{attitude: {pitch, roll, yaw}}` | Both |

#### Expected Value Ranges
| Parameter | Type | Min | Max | Notes |
|-----------|------|-----|-----|-------|
| pitch, roll, yaw | integer | -180 | 180 | Degrees |

### 5.9 drone_sensor_summary

#### Valid Test Cases
| Test ID | Description | Input | Expected Output | Mock/Real |
|---------|-------------|-------|-----------------|-----------|
| SUMM_001 | Get sensor summary | `{}` | Complete sensor data object | Both |

---

## 6. Common Error Scenarios (All Tools)

### Connection State Errors
| Error Code | Description | Test Coverage |
|------------|-------------|---------------|
| DRONE_NOT_CONNECTED | Tool called when drone not connected | All tools |
| DRONE_CONNECTION_FAILED | Initial connection fails | Connection tools |
| COMMAND_TIMEOUT | Command execution timeout | All tools |
| COMMAND_FAILED | Generic command failure | All tools |

### Flight State Errors
| Error Code | Description | Test Coverage |
|------------|-------------|---------------|
| NOT_FLYING | Movement command when not flying | Movement tools |
| ALREADY_FLYING | Takeoff when already flying | Flight tools |

### Parameter Validation Errors
| Error Code | Description | Test Coverage |
|------------|-------------|---------------|
| INVALID_PARAMETER | Parameter outside valid range | All parameterized tools |
| UNSUPPORTED_FORMAT | Invalid parameter format | String/enum parameters |

### System Errors
| Error Code | Description | Test Coverage |
|------------|-------------|---------------|
| INTERNAL_ERROR | Unexpected system error | All tools |
| FILE_TOO_LARGE | File size exceeds limit | Model management |

---

## 7. Performance Test Cases

### Response Time Requirements
| Tool Category | Target Response Time | Test Method |
|---------------|---------------------|-------------|
| Connection | < 100ms | Measure connect/disconnect |
| Flight Control | < 50ms | Measure takeoff/land commands |
| Movement | < 50ms | Measure movement commands |
| Sensors | < 30ms | Measure sensor readings |
| Camera | < 200ms | Measure stream operations |

### Concurrent Access Tests
| Test ID | Description | Expected Behavior |
|---------|-------------|-------------------|
| CONC_001 | Multiple simultaneous sensor requests | Sequential processing |
| CONC_002 | Movement during sensor reading | Safe execution order |
| CONC_003 | Emergency stop during any operation | Immediate priority |

---

## 8. Integration Test Scenarios

### End-to-End Flight Mission
| Test ID | Description | Steps | Expected Result |
|---------|-------------|--------|-----------------|
| E2E_001 | Complete flight cycle | Connect → Takeoff → Move → Land → Disconnect | All steps successful |
| E2E_002 | Camera operation during flight | Connect → Takeoff → Start Stream → Move → Photo → Land | All operations successful |
| E2E_003 | Error recovery scenario | Connect → Takeoff → Simulate Error → Emergency → Recover | Safe error handling |

### State Transition Testing
| From State | To State | Valid Commands | Invalid Commands |
|------------|----------|----------------|------------------|
| Disconnected | Connected | drone_connect | All others |
| Connected | Flying | drone_takeoff | Movement commands |
| Flying | Connected | drone_land | drone_takeoff |
| Any | Emergency | drone_emergency | None |

---

## 9. Test Data Sets

### Valid Parameter Sets
```json
{
  "movement": {
    "directions": ["up", "down", "left", "right", "forward", "back"],
    "distances": [20, 100, 250, 500],
    "rotations": [1, 45, 90, 180, 360],
    "speeds": [10, 30, 50, 75, 100]
  },
  "coordinates": {
    "positions": [-500, -250, 0, 250, 500],
    "speeds": [10, 30, 60, 100]
  },
  "camera": {
    "resolutions": ["high", "low"],
    "fps": ["high", "middle", "low"],
    "bitrates": [1, 2, 3, 4, 5]
  }
}
```

### Invalid Parameter Sets
```json
{
  "movement": {
    "distances": [-1, 0, 19, 501, 1000],
    "angles": [-1, 0, 361, 400],
    "speeds": [-1, 0, 9, 101, 200]
  },
  "coordinates": {
    "positions": [-501, -1000, 501, 1000],
    "speeds": [-1, 0, 9, 101, 200]
  },
  "strings": {
    "invalid": ["", null, undefined, 123, {}, []]
  }
}
```

---

## 10. Test Execution Framework

### Mock Testing Setup
```python
# Example mock test structure
@pytest.fixture
def mcp_server():
    return MCPServer(config=TestConfig.get_mock_config())

@pytest.fixture
def mock_drone():
    return TelloStub()
```

### Real Hardware Testing Setup
```python
@pytest.fixture
def real_mcp_server():
    return MCPServer(config=TestConfig.get_real_config())

@pytest.mark.real_hardware
def test_with_real_drone():
    # Safety checks before real hardware tests
    pass
```

### Test Configuration
```json
{
  "test_mode": "mock|real|hybrid",
  "safety_checks": true,
  "timeout_seconds": 30,
  "retry_attempts": 3,
  "log_level": "DEBUG"
}
```

---

## Summary

This test plan covers:
- **25 MCP Tools** with comprehensive test cases
- **Boundary value analysis** for all parameters
- **Error handling** for all error codes
- **Performance testing** with defined targets
- **Integration scenarios** for real-world usage
- **Both mock and real hardware** testing approaches

Total test cases: **~500 individual tests** covering all aspects of the MCP tool functionality.