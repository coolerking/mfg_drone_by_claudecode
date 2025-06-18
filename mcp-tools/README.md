# MFG Drone MCP Tools

Model Context Protocol (MCP) tools for controlling Tello EDU drones through the MFG Drone Backend API. This package provides seamless integration between Claude AI and drone operations.

## Features

- **Complete Drone Control**: 25+ MCP tools covering all drone operations
- **Real-time Integration**: Direct communication with FastAPI backend
- **Robust Error Handling**: Automatic retries and comprehensive error reporting  
- **Type Safety**: Full TypeScript implementation with Zod validation
- **Comprehensive Logging**: Structured logging with file output
- **Health Monitoring**: Automatic backend health checks
- **Production Ready**: Configurable for development and production environments

## Installation

### Prerequisites

- Node.js 18+
- TypeScript 5+
- MFG Drone Backend API running
- Tello EDU drone

### Development Setup

```bash
# Clone the repository
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/mcp-tools

# Install dependencies
npm install

# Build the project
npm run build

# Start in development mode
npm run dev
```

### Production Installation

```bash
# Install globally
npm install -g mfg-drone-mcp-tools

# Or run directly
npx mfg-drone-mcp-tools
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment (development/production) | `development` |
| `BACKEND_URL` | FastAPI backend URL | `http://localhost:8000` |
| `DEBUG` | Enable debug logging | `false` |
| `LOG_FILE` | Log file path | (none) |
| `TIMEOUT` | HTTP timeout in milliseconds | `30000` |
| `RETRY_ATTEMPTS` | Number of retry attempts | `3` |
| `RETRY_DELAY` | Delay between retries in ms | `1000` |

### Configuration Files

Create configuration files in the `config/` directory:

**config/development.json**
```json
{
  "backendUrl": "http://localhost:8000",
  "timeout": 30000,
  "retryAttempts": 3,
  "retryDelay": 1000,
  "debug": true,
  "logFile": "./logs/mcp-drone-dev.log",
  "maxLogSize": 10485760,
  "healthCheckInterval": 30000
}
```

**config/production.json**
```json
{
  "backendUrl": "http://192.168.1.100:8000",
  "timeout": 30000,
  "retryAttempts": 5,
  "retryDelay": 2000,
  "debug": false,
  "logFile": "/var/log/mcp-drone/mcp-drone.log",
  "maxLogSize": 52428800,
  "healthCheckInterval": 60000
}
```

## Usage

### Command Line

```bash
# Start with default configuration
node dist/index.js

# Start with custom config
node dist/index.js --config=./config/production.json

# Start with environment variables
BACKEND_URL=http://192.168.1.100:8000 DEBUG=true node dist/index.js

# Show help
node dist/index.js --help

# Show version
node dist/index.js --version
```

### Claude Integration

Add to your Claude workspace configuration:

```json
{
  "mcpServers": {
    "drone-tools": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "./mcp-tools",
      "env": {
        "BACKEND_URL": "http://localhost:8000",
        "DEBUG": "true"
      }
    }
  }
}
```

## Available Tools

### Connection Tools

| Tool | Description |
|------|-------------|
| `drone_connect` | Connect to Tello EDU drone |
| `drone_disconnect` | Disconnect from drone |
| `drone_status` | Get comprehensive drone status |

### Flight Control Tools

| Tool | Description |
|------|-------------|
| `drone_takeoff` | Takeoff and hover (0.8-1.2m) |
| `drone_land` | Land safely at current position |
| `drone_emergency` | Emergency stop (⚠️ drops drone!) |
| `drone_stop` | Stop movement and hover in place |
| `drone_get_height` | Get current flight height |

### Movement Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `drone_move` | Basic directional movement | `direction`, `distance` |
| `drone_rotate` | Rotate clockwise/counter-clockwise | `direction`, `angle` |
| `drone_flip` | Perform flip maneuver | `direction` |
| `drone_go_xyz` | Move to XYZ coordinates | `x`, `y`, `z`, `speed` |
| `drone_curve` | Curved flight through waypoint | `x1`, `y1`, `z1`, `x2`, `y2`, `z2`, `speed` |
| `drone_rc_control` | Real-time RC control | `left_right_velocity`, `forward_backward_velocity`, `up_down_velocity`, `yaw_velocity` |

### Camera Tools

| Tool | Description |
|------|-------------|
| `camera_stream_start` | Start video streaming |
| `camera_stream_stop` | Stop video streaming |
| `camera_take_photo` | Capture single photo |
| `camera_start_recording` | Start video recording |
| `camera_stop_recording` | Stop video recording |
| `camera_settings` | Configure resolution, FPS, bitrate |

### Sensor Tools

| Tool | Description |
|------|-------------|
| `drone_battery` | Get battery level (%) |
| `drone_temperature` | Get internal temperature (°C) |
| `drone_flight_time` | Get cumulative flight time |
| `drone_barometer` | Get barometric pressure (hPa) |
| `drone_distance_tof` | Get ToF sensor distance (mm) |
| `drone_acceleration` | Get X/Y/Z acceleration (g) |
| `drone_velocity` | Get X/Y/Z velocity (cm/s) |
| `drone_attitude` | Get pitch/roll/yaw angles (°) |
| `drone_sensor_summary` | Get comprehensive sensor data |

## Example Usage with Claude

### Basic Flight Operations

```
Human: Connect to the drone and take off

Claude: I'll help you connect to the drone and take off. Let me do this step by step.

*Uses drone_connect tool*
✅ Successfully connected to Tello EDU drone

*Uses drone_takeoff tool*  
✅ Takeoff successful! Drone is now hovering at 95cm height.

The drone is now connected and hovering safely. The battery level is 89% which is good for flight operations.
```

### Advanced Movement

```
Human: Move the drone in a square pattern 100cm on each side

Claude: I'll move the drone in a square pattern with 100cm sides.

*Uses drone_move with direction: "forward", distance: 100*
*Uses drone_move with direction: "right", distance: 100*  
*Uses drone_move with direction: "back", distance: 100*
*Uses drone_move with direction: "left", distance: 100*

✅ Square pattern completed! The drone has returned to its starting position.
```

### Sensor Monitoring

```
Human: Check all the drone sensors and tell me if everything is okay

Claude: *Uses drone_sensor_summary tool*

📊 Drone Health Summary:
✅ All systems normal - Flying
- 🔋 Battery: 76% (Good)
- 🌡️ Temperature: 42°C (Normal) 
- ✈️ Flying at 95cm height
- 📡 Sensors all reading normally
- 🧭 Attitude: Level (pitch: 2°, roll: -1°, yaw: 45°)

Everything looks good! The drone is operating normally with good battery life.
```

## Architecture

```
Claude AI ←─ MCP Protocol ─→ MCP Server ←─ HTTP ─→ FastAPI Backend ←─ djitellopy ─→ Tello EDU
   (AI)                      (Node.js)              (Python)                        (Drone)
```

### Key Components

- **MCP Server**: Core server handling MCP protocol communication
- **Tool Registry**: Manages all available tools and their execution
- **FastAPI Client**: HTTP client with retry logic and health monitoring
- **Tool Categories**: Organized tool implementations (Connection, Flight, Movement, Camera, Sensors)
- **Configuration Management**: Environment-based configuration with validation
- **Logging System**: Structured logging with file rotation

## Development

### Project Structure

```
mcp-tools/
├── src/
│   ├── bridge/           # FastAPI integration
│   ├── tools/            # MCP tool implementations
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── server.ts         # Main MCP server
│   └── index.ts          # Entry point
├── config/               # Configuration files
├── tests/                # Test suites
└── dist/                 # Compiled JavaScript
```

### Building

```bash
# Clean build
npm run clean
npm run build

# Development build with watching
npm run dev

# Linting
npm run lint
npm run lint:fix
```

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch
```

## Production Deployment

### systemd Service

Create `/etc/systemd/system/mcp-drone-tools.service`:

```ini
[Unit]
Description=MFG Drone MCP Tools Server
After=network.target

[Service]
Type=simple
User=drone
WorkingDirectory=/opt/mfg-drone-mcp-tools
ExecStart=/usr/bin/node dist/index.js --config=/etc/mcp-drone/production.json
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist/ ./dist/
COPY config/ ./config/

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Health Monitoring

The server includes built-in health monitoring:

- Automatic backend connectivity checks
- Tool execution metrics
- Log file rotation
- Graceful shutdown handling

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   ```
   Error: Backend connection verification failed
   ```
   - Check if FastAPI backend is running
   - Verify `BACKEND_URL` configuration
   - Check network connectivity

2. **Tool Execution Timeout**
   ```
   Error: Tool execution failed: timeout
   ```
   - Increase `timeout` configuration
   - Check drone connectivity
   - Verify drone is responsive

3. **Permission Denied**
   ```
   Error: EACCES: permission denied
   ```
   - Check log file directory permissions
   - Ensure user has write access
   - Use appropriate file paths

### Debug Mode

Enable debug logging:

```bash
DEBUG=true node dist/index.js
```

Or set in configuration:
```json
{
  "debug": true,
  "logFile": "./debug.log"
}
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -am 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`  
5. Create Pull Request

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Support

- 📖 Documentation: [MFG Drone Documentation](../backend/doc/)
- 🐛 Issues: [GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/coolerking/mfg_drone_by_claudecode/discussions)

## Related Projects

- [MFG Drone Backend API](../backend/) - Python FastAPI backend
- [MFG Drone Frontend](../frontend/) - Web interfaces
- [Tello EDU](https://www.ryzerobotics.com/tello-edu) - Target drone platform