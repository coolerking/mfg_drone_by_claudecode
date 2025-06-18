# MFG Drone MCP Tools

[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-v0.5.0-purple.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive **Model Context Protocol (MCP)** server providing AI assistants like Claude with direct control over **Tello EDU drones**. This implementation bridges natural language commands with precise drone operations through a robust, production-ready architecture.

## 🚁 Features

### **Complete Drone Control**
- **Connection Management**: Connect, disconnect, and monitor drone status
- **Flight Operations**: Takeoff, landing, emergency stop with safety checks
- **Precision Movement**: Directional movement, rotation, 3D positioning, curved flight paths
- **Camera Operations**: Live streaming, photo capture, video recording with quality control
- **Sensor Monitoring**: Real-time battery, temperature, altitude, attitude, and velocity data

### **Advanced MCP Integration**
- **25+ Specialized Tools**: Comprehensive drone control through natural language
- **Real-time Communication**: WebSocket support for live sensor data and video streams
- **Performance Optimized**: Sub-50ms response times with intelligent retry logic
- **Type-Safe**: Full TypeScript implementation with Zod validation
- **Claude-Optimized**: Human-readable responses with safety recommendations

### **Production Features**
- **Health Monitoring**: Automatic health checks and performance metrics
- **Graceful Degradation**: Intelligent error handling and recovery
- **Structured Logging**: JSON logging with configurable levels and file rotation
- **Configuration Management**: Environment-based configuration with validation
- **WebSocket Bridge**: Real-time bidirectional communication for live operations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Claude Code   │◀──▶│   MCP Server    │◀──▶│  FastAPI Bridge │◀──▶│   Tello EDU     │
│   (AI Client)   │    │   (Node.js)     │    │   (Python)      │    │   (Drone)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │                        │
        │              ┌─────────────────┐               │                        │
        │              │   Tool Registry │               │                        │
        │              │  (25+ Tools)    │               │                        │
        │              └─────────────────┘               │                        │
        │                        │                        │                        │
        │              ┌─────────────────┐    ┌─────────────────┐                │
        └──────────────│  WebSocket      │◀──▶│   Event System  │────────────────┘
                       │  Real-time      │    │   Notifications │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ 
- **TypeScript** 5.0+
- **FastAPI Backend** (MFG Drone system)
- **Tello EDU Drone** (for actual operations)

### Installation

```bash
# Clone the repository
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-tools

# Install dependencies
npm install

# Build the project
npm run build

# Run in development mode
npm run dev
```

### Configuration

Create or modify configuration files:

```bash
# Development configuration
cp config/development.json config/local.json
```

```json
{
  "backend": {
    "baseUrl": "http://localhost:8000",
    "timeout": 30000,
    "retries": 5
  },
  "websocket": {
    "enabled": true,
    "reconnectInterval": 5000
  },
  "logging": {
    "level": "debug",
    "format": "pretty"
  }
}
```

### Environment Variables

```bash
# Required
export BACKEND_URL="http://your-drone-backend:8000"

# Optional
export LOG_LEVEL="info"
export DEBUG="true"
export NODE_ENV="development"
```

## 🛠️ Usage

### Starting the MCP Server

```bash
# Production mode
npm start

# Development mode with auto-reload
npm run dev

# With custom configuration
BACKEND_URL=http://192.168.1.100:8000 npm start
```

### Claude Integration

Add to your Claude MCP configuration (`mcp-workspace.json`):

```json
{
  "mcpServers": {
    "drone-tools": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "./mcp-tools",
      "env": {
        "BACKEND_URL": "http://localhost:8000",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Example Commands with Claude

Once integrated, you can control the drone using natural language:

```
# Basic Operations
"Connect to the drone and check its status"
"Take off and hover at safe altitude"
"Move forward 2 meters slowly"
"Rotate 90 degrees clockwise"
"Take a high-quality photo"
"Land the drone safely"

# Advanced Operations
"Start video streaming and move in a square pattern"
"Get comprehensive sensor data with temperature in Fahrenheit"
"Perform emergency stop if battery is below 20%"
"Fly to coordinates (100, 200, 50) at medium speed"

# Monitoring
"Show me detailed battery information"
"Monitor sensor data for the next 30 seconds"
"Check drone attitude and stability"
```

## 📋 Available Tools

### Connection Tools (3)
- `drone_connect` - Establish drone communication
- `drone_disconnect` - Safely terminate connection  
- `drone_status` - Comprehensive status with health metrics

### Flight Control Tools (5)
- `drone_takeoff` - Automatic takeoff to hover altitude
- `drone_land` - Safe landing procedure
- `drone_emergency` - Immediate motor stop (emergency only)
- `drone_stop` - Stop movement and hover in place
- `drone_get_height` - Current altitude measurement

### Movement Tools (6)
- `drone_move` - Directional movement (left/right/forward/back/up/down)
- `drone_rotate` - Clockwise/counter-clockwise rotation
- `drone_flip` - Acrobatic flip maneuvers
- `drone_go_xyz` - 3D coordinate movement
- `drone_curve` - Smooth curved flight paths
- `drone_rc_control` - Direct velocity control (like RC transmitter)

### Camera Tools (6)
- `camera_stream_start` - Start live video streaming
- `camera_stream_stop` - Stop video streaming
- `camera_take_photo` - Capture high-resolution photos
- `camera_start_recording` - Begin video recording
- `camera_stop_recording` - Stop and save video
- `camera_settings` - Adjust quality and performance settings

### Sensor Tools (9)
- `drone_battery` - Battery level with flight time estimates
- `drone_temperature` - Internal temperature monitoring
- `drone_flight_time` - Session flight time tracking
- `drone_barometer` - Atmospheric pressure readings
- `drone_distance_tof` - Ground distance (Time-of-Flight sensor)
- `drone_acceleration` - 3-axis acceleration data
- `drone_velocity` - 3D velocity measurements
- `drone_attitude` - Orientation (pitch, roll, yaw)
- `drone_sensor_summary` - Comprehensive sensor overview

## 🔧 Development

### Project Structure

```
mcp-tools/
├── src/
│   ├── bridge/               # FastAPI integration
│   │   ├── enhanced-api-client.ts    # HTTP client with retry logic
│   │   ├── websocket-bridge.ts       # Real-time communication
│   │   └── metrics-collector.ts      # Performance monitoring
│   ├── tools/                # MCP tool implementations
│   │   ├── connection.ts     # Connection management
│   │   ├── flight.ts         # Flight control
│   │   ├── movement.ts       # Movement control
│   │   ├── camera.ts         # Camera operations
│   │   ├── sensors.ts        # Sensor data
│   │   └── registry.ts       # Tool management
│   ├── types/                # TypeScript definitions
│   ├── utils/                # Utilities
│   │   ├── config.ts         # Configuration management
│   │   └── logger.ts         # Structured logging
│   ├── server.ts             # Main MCP server
│   └── index.ts              # Entry point
├── config/                   # Environment configurations
├── tests/                    # Test suite
└── dist/                     # Compiled JavaScript
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run integration tests only
npm run test:integration

# Watch mode for development
npm run test:watch
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

### Building

```bash
# Development build
npm run build

# Production build
npm run build:prod

# Watch mode for development
npm run build:watch
```

## 📊 Performance & Monitoring

### Performance Targets

- **Tool Response Time**: < 50ms average
- **WebSocket Latency**: < 20ms
- **Video Stream Delay**: < 200ms
- **API Success Rate**: > 99%

### Monitoring Features

- **Real-time Metrics**: API response times, error rates, connection health
- **Health Checks**: Automatic drone connectivity and system health monitoring
- **Structured Logs**: JSON-formatted logs with configurable levels
- **Performance Alerts**: Automatic warnings for degraded performance

### Metrics Endpoint

```bash
# Get current metrics
curl http://localhost:8000/mcp/metrics

# Health check
curl http://localhost:8000/mcp/health
```

## 🔒 Safety Features

### Automated Safety Checks
- **Battery Monitoring**: Automatic low battery warnings and recommendations
- **Temperature Monitoring**: Overheating protection and cooling recommendations
- **Connection Monitoring**: Automatic reconnection and connection health checks
- **Altitude Limits**: Ground proximity warnings and regulatory compliance alerts

### Emergency Procedures
- **Emergency Stop**: Immediate motor shutdown for critical situations
- **Graceful Landing**: Safe landing with multiple fallback options
- **Connection Recovery**: Automatic reconnection with exponential backoff
- **Error Recovery**: Intelligent error handling with user-friendly messages

## 🌐 WebSocket Real-time Features

### Live Data Streaming
- **Sensor Data**: Real-time battery, temperature, altitude, attitude updates
- **Video Feed**: Low-latency video streaming with quality adaptation
- **Status Updates**: Live connection status and flight mode changes
- **Event Notifications**: Real-time alerts for warnings and state changes

### WebSocket API
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/mcp/ws/bridge');

// Subscribe to sensor updates
ws.send(JSON.stringify({
  type: 'subscribe',
  data: { topic: 'sensor_updates' }
}));

// Handle real-time sensor data
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'sensor_update') {
    console.log('Live sensor data:', message.data);
  }
};
```

## 🐛 Troubleshooting

### Common Issues

**Connection Problems**
```bash
# Check backend connectivity
curl http://localhost:8000/health

# Verify MCP server logs
tail -f logs/mcp-drone-tools.log

# Test tool execution
echo '{"type": "tool_call", "name": "drone_status"}' | node dist/index.js
```

**Performance Issues**
```bash
# Check performance metrics
curl http://localhost:8000/mcp/metrics

# Monitor resource usage
npm run monitor

# Enable debug logging
LOG_LEVEL=debug npm start
```

**WebSocket Issues**
```bash
# Test WebSocket connectivity
wscat -c ws://localhost:8000/mcp/ws/bridge

# Check WebSocket logs
grep "websocket" logs/mcp-drone-tools.log
```

### Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `CONN_001` | Backend connection failed | Check BACKEND_URL and network connectivity |
| `TOOL_002` | Invalid tool arguments | Verify argument format and required fields |
| `WS_003` | WebSocket connection lost | Check network stability, auto-reconnection enabled |
| `PERF_004` | Response time exceeded | Check system load and backend performance |

## 📚 Documentation

### API Reference
- [Tool Specifications](docs/tools-reference.md)
- [Configuration Guide](docs/configuration.md)
- [WebSocket API](docs/websocket-api.md)
- [Error Handling](docs/error-handling.md)

### Integration Guides
- [Claude Code Integration](docs/claude-integration.md)
- [Backend API Integration](docs/backend-integration.md)
- [Custom Tool Development](docs/custom-tools.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-tools

# Install dependencies
npm install

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes and test
npm test

# Submit a pull request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Model Context Protocol specification
- [Claude Code](https://claude.ai/code) for AI-powered development capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API framework
- [DJI Tello SDK](https://github.com/dji-sdk/Tello-Python) for drone communication

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- **Discussions**: [GitHub Discussions](https://github.com/coolerking/mfg_drone_by_claudecode/discussions)
- **Documentation**: [Project Wiki](https://github.com/coolerking/mfg_drone_by_claudecode/wiki)

---

**⚠️ Safety Notice**: Always follow local regulations for drone operation. Ensure adequate insurance coverage and maintain visual contact with the drone during flight. This software is for educational and research purposes.