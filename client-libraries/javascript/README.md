# MCP Drone Client SDK (JavaScript/TypeScript)

JavaScript/TypeScript SDK for MCP Drone Control Server. This SDK provides a complete interface for controlling drones through natural language commands and direct API calls.

## Features

- 🗣️ **Natural Language Commands**: Execute drone operations using Japanese natural language
- 🚁 **Complete Drone Control**: Connect, takeoff, move, rotate, land, emergency stop
- 📸 **Camera & Vision**: Photo capture, streaming, object detection, tracking
- 📊 **System Monitoring**: Health checks, status monitoring, system information
- 🔒 **Authentication**: API Key and JWT Bearer token support
- 🌐 **WebSocket Support**: Real-time communication
- 📝 **TypeScript Support**: Full TypeScript definitions included
- 🧪 **Well Tested**: Comprehensive test suite with >90% coverage

## Installation

```bash
npm install mcp-drone-client
```

## Quick Start

```javascript
import { MCPClient } from 'mcp-drone-client';

// Initialize client
const client = new MCPClient({
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key', // or use bearerToken
});

// Execute natural language command
const response = await client.executeCommand({
  command: 'ドローンAAに接続して'
});

// Direct API calls
const drones = await client.getDrones();
await client.connectDrone('drone_001');
await client.takeoff('drone_001', { target_height: 100 });
await client.moveDrone('drone_001', {
  direction: 'forward',
  distance: 100
});
```

## API Reference

### Configuration

```typescript
interface MCPClientConfig {
  baseURL: string;          // MCP server URL
  apiKey?: string;          // API key for authentication
  bearerToken?: string;     // JWT bearer token for authentication
  timeout?: number;         // Request timeout in milliseconds (default: 30000)
}
```

### Natural Language Commands

```typescript
// Execute single command
await client.executeCommand({
  command: 'ドローンAAに接続して',
  context: {
    drone_id: 'drone_001',
    language: 'ja'
  },
  options: {
    confirm_before_execution: false,
    dry_run: false
  }
});

// Execute batch commands
await client.executeBatchCommand({
  commands: [
    { command: 'ドローンAAに接続して' },
    { command: '離陸して' },
    { command: '写真を撮って' }
  ],
  execution_mode: 'sequential',
  stop_on_error: true
});
```

### Drone Control

```typescript
// Connection management
await client.connectDrone('drone_001');
await client.disconnectDrone('drone_001');

// Flight control
await client.takeoff('drone_001', { target_height: 100 });
await client.land('drone_001');
await client.emergencyStop('drone_001');

// Movement
await client.moveDrone('drone_001', {
  direction: 'forward',
  distance: 100,
  speed: 50
});

await client.rotateDrone('drone_001', {
  direction: 'clockwise',
  angle: 90
});

await client.setAltitude('drone_001', {
  target_height: 150,
  mode: 'absolute'
});
```

### Camera Operations

```typescript
// Take photo
const photo = await client.takePhoto('drone_001', {
  filename: 'photo.jpg',
  quality: 'high'
});

// Control streaming
await client.controlStreaming('drone_001', {
  action: 'start',
  quality: 'high',
  resolution: '720p'
});

// Collect learning data
await client.collectLearningData('drone_001', {
  object_name: 'product_sample',
  capture_positions: ['front', 'back', 'left', 'right'],
  photos_per_position: 3
});
```

### Vision & AI

```typescript
// Object detection
const detections = await client.detectObjects({
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  confidence_threshold: 0.7
});

// Object tracking
await client.controlTracking({
  action: 'start',
  drone_id: 'drone_001',
  model_id: 'yolo_v8',
  follow_distance: 200
});
```

### System Information

```typescript
// Get system status
const status = await client.getSystemStatus();

// Health check
const health = await client.getHealthCheck();

// Get drone information
const drones = await client.getDrones();
const availableDrones = await client.getAvailableDrones();
const droneStatus = await client.getDroneStatus('drone_001');
```

### WebSocket Support

```typescript
// Connect to WebSocket for real-time updates
client.connectWebSocket(
  (data) => {
    console.log('Received:', data);
  },
  (error) => {
    console.error('WebSocket error:', error);
  }
);

// Disconnect WebSocket
client.disconnectWebSocket();
```

## Error Handling

```typescript
import { MCPClientError } from 'mcp-drone-client';

try {
  await client.connectDrone('invalid_drone');
} catch (error) {
  if (error instanceof MCPClientError) {
    console.error('MCP Error:', error.errorCode, error.message);
    console.error('Details:', error.details);
    console.error('Timestamp:', error.timestamp);
  } else {
    console.error('Unexpected error:', error);
  }
}
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

## Development

```bash
# Install dependencies
npm install

# Build the SDK
npm run build

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Lint code
npm run lint

# Generate documentation
npm run docs
```

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