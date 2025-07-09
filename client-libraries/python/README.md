# MCP Drone Client SDK (Python)

Python SDK for MCP Drone Control Server. This SDK provides a complete interface for controlling drones through natural language commands and direct API calls.

## Features

- 🗣️ **Natural Language Commands**: Execute drone operations using Japanese natural language
- 🚁 **Complete Drone Control**: Connect, takeoff, move, rotate, land, emergency stop
- 📸 **Camera & Vision**: Photo capture, streaming, object detection, tracking
- 📊 **System Monitoring**: Health checks, status monitoring, system information
- 🔒 **Authentication**: API Key and JWT Bearer token support
- 🌐 **WebSocket Support**: Real-time communication with async/await
- 📝 **Type Safety**: Full Pydantic model support for type validation
- 🔄 **Async/Await**: Modern async/await syntax throughout
- 🧪 **Well Tested**: Comprehensive test suite with >85% coverage

## Installation

```bash
pip install mcp-drone-client
```

## Quick Start

```python
import asyncio
from mcp_drone_client import MCPClient, MCPClientConfig, NaturalLanguageCommand

async def main():
    # Configure client
    config = MCPClientConfig(
        base_url="http://localhost:8001",
        api_key="your-api-key",  # or use bearer_token
        timeout=30.0,
    )
    
    # Use as async context manager
    async with MCPClient(config) as client:
        # Execute natural language command
        response = await client.execute_command(
            NaturalLanguageCommand(command="ドローンAAに接続して")
        )
        print(f"Command result: {response.message}")
        
        # Direct API calls
        drones = await client.get_drones()
        print(f"Available drones: {len(drones.drones)}")
        
        # Drone operations
        await client.connect_drone("drone_001")
        await client.takeoff("drone_001")
        await client.move_drone("drone_001", MoveCommand(
            direction="forward", distance=100
        ))

# Run the async function
asyncio.run(main())
```

## API Reference

### Configuration

```python
from mcp_drone_client.models import MCPClientConfig

config = MCPClientConfig(
    base_url="http://localhost:8001",      # MCP server URL
    api_key="your-api-key",                # API key authentication
    bearer_token="your-jwt-token",         # Or JWT bearer token
    timeout=30.0,                          # Request timeout in seconds
)
```

### Natural Language Commands

```python
from mcp_drone_client.models import NaturalLanguageCommand, BatchCommand

# Single command
command = NaturalLanguageCommand(
    command="ドローンAAに接続して",
    context={"drone_id": "drone_001", "language": "ja"},
    options={"confirm_before_execution": False, "dry_run": False}
)
response = await client.execute_command(command)

# Batch commands
batch = BatchCommand(
    commands=[
        NaturalLanguageCommand(command="ドローンAAに接続して"),
        NaturalLanguageCommand(command="離陸して"),
        NaturalLanguageCommand(command="写真を撮って"),
    ],
    execution_mode="sequential",
    stop_on_error=True,
)
batch_response = await client.execute_batch_command(batch)
```

### Drone Control

```python
from mcp_drone_client.models import (
    TakeoffCommand, MoveCommand, RotateCommand, AltitudeCommand
)

# Connection management
await client.connect_drone("drone_001")
await client.disconnect_drone("drone_001")

# Flight control
await client.takeoff("drone_001", TakeoffCommand(target_height=100))
await client.land("drone_001")
await client.emergency_stop("drone_001")

# Movement
await client.move_drone("drone_001", MoveCommand(
    direction="forward", distance=100, speed=50
))

await client.rotate_drone("drone_001", RotateCommand(
    direction="clockwise", angle=90
))

await client.set_altitude("drone_001", AltitudeCommand(
    target_height=150, mode="absolute"
))
```

### Camera Operations

```python
from mcp_drone_client.models import (
    PhotoCommand, StreamingCommand, LearningDataCommand
)

# Take photo
photo_result = await client.take_photo("drone_001", PhotoCommand(
    filename="photo.jpg", quality="high"
))

# Control streaming
await client.control_streaming("drone_001", StreamingCommand(
    action="start", quality="high", resolution="720p"
))

# Collect learning data
learning_result = await client.collect_learning_data("drone_001", LearningDataCommand(
    object_name="product_sample",
    capture_positions=["front", "back", "left", "right"],
    photos_per_position=3,
))
```

### Vision & AI

```python
from mcp_drone_client.models import DetectionCommand, TrackingCommand

# Object detection
detections = await client.detect_objects(DetectionCommand(
    drone_id="drone_001",
    model_id="yolo_v8",
    confidence_threshold=0.7,
))

# Object tracking
await client.control_tracking(TrackingCommand(
    action="start",
    drone_id="drone_001",
    model_id="yolo_v8",
    follow_distance=200,
))
```

### System Information

```python
# Get system status
status = await client.get_system_status()
print(f"System health: {status.system_health}")
print(f"Connected drones: {status.connected_drones}")

# Health check
health = await client.get_health_check()
print(f"Health status: {health.status}")

# Get drone information
drones = await client.get_drones()
available_drones = await client.get_available_drones()
drone_status = await client.get_drone_status("drone_001")
```

### WebSocket Support

```python
async def on_message(data):
    print(f"Received: {data}")

async def on_error(error):
    print(f"WebSocket error: {error}")

async def on_connect():
    print("WebSocket connected")

async def on_disconnect():
    print("WebSocket disconnected")

# Connect WebSocket
await client.connect_websocket(
    on_message=on_message,
    on_error=on_error,
    on_connect=on_connect,
    on_disconnect=on_disconnect,
)

# Send message
await client.send_websocket_message({"type": "ping"})

# Disconnect
await client.disconnect_websocket()
```

## Error Handling

```python
from mcp_drone_client import MCPClientError

try:
    await client.connect_drone("invalid_drone")
except MCPClientError as e:
    print(f"MCP Error: {e.error_code}")
    print(f"Message: {e.message}")
    print(f"Details: {e.details}")
    print(f"Timestamp: {e.timestamp}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Natural Language Commands

The SDK supports a wide range of Japanese natural language commands:

| Command Type | Examples |
|-------------|----------|
| Connection | `ドローンAAに接続して`, `ドローンに繋げて` |
| Takeoff | `離陸して`, `ドローンを起動して`, `飛び立って` |
| Movement | `右に50センチ移動して`, `前に1メートル進んで` |
| Rotation | `右に90度回転して`, `左に45度向きを変えて` |
| Altitude | `高度を1メートルにして`, `2メートルの高さまで上がって` |
| Camera | `写真を撮って`, `撮影して`, `カメラで撮って` |
| Landing | `着陸して`, `降りて`, `ドローンを着陸させて` |
| Emergency | `緊急停止して`, `止まって`, `ストップ` |

## Advanced Usage

### Custom Configuration

```python
from mcp_drone_client import create_client

# Using convenience function
client = create_client(
    base_url="http://localhost:8001",
    api_key="your-api-key",
    timeout=60.0,
)

# Manual configuration
config = MCPClientConfig(
    base_url="https://production-mcp-server.com",
    bearer_token="your-jwt-token",
    timeout=45.0,
)
client = MCPClient(config)
```

### Connection Testing

```python
# Test connection
is_connected = await client.ping()
if is_connected:
    print("Server is reachable")
else:
    print("Server is not reachable")
```

### Waiting for Operations

```python
# Wait for long-running operation
operation_id = "operation_123"
success = await client.wait_for_operation(operation_id, max_wait_time=60.0)
if success:
    print("Operation completed successfully")
else:
    print("Operation timed out")
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/python

# Install in development mode
pip install -e .[dev]

# Install test dependencies
pip install -e .[test]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_drone_client --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run tests with specific markers
pytest -m "not slow"
pytest -m "integration"
```

### Code Quality

```bash
# Format code
black mcp_drone_client tests

# Check style
flake8 mcp_drone_client tests

# Type checking
mypy mcp_drone_client
```

### Build Documentation

```bash
# Generate documentation
sphinx-build -b html docs docs/_build/html
```

## Requirements

- Python 3.8+
- aiohttp >= 3.8.0
- httpx >= 0.24.0
- websockets >= 11.0.0
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please open an issue in the [GitHub repository](https://github.com/coolerking/mfg_drone_by_claudecode/issues).

## Changelog

### 1.0.0
- Initial release
- Complete MCP API support
- Natural language command processing
- WebSocket support
- Comprehensive test suite
- Full type safety with Pydantic models