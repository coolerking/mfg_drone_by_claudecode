# MFG Drone MCP Tools

MCP (Model Context Protocol) server that enables Claude to interact with the MFG Drone Backend API for controlling Tello EDU drones.

## Overview

This MCP server provides tools for:
- **Connection Management**: Connect/disconnect from Tello EDU drone
- **Flight Control**: Takeoff, landing, emergency stop
- **Status Monitoring**: Get real-time drone status and sensor data

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

### Production

```bash
# Build for production
npm run build

# Start production server
npm start
```

## MCP Tools

### Connection Tools

- `drone_connect` - Connect to Tello EDU drone
- `drone_disconnect` - Disconnect from drone
- `drone_status` - Get current drone status

### Flight Control Tools

- `drone_takeoff` - Make drone take off
- `drone_land` - Make drone land safely
- `drone_emergency` - Emergency stop (drops drone immediately)

## Configuration

Configuration is loaded from:
1. `config/{environment}.json` files
2. Environment variables (override file config)

### Environment Variables

- `NODE_ENV` - Environment (development/production/test)
- `MCP_BACKEND_URL` - Backend API URL
- `MCP_BACKEND_TIMEOUT` - Request timeout in ms
- `MCP_LOG_LEVEL` - Log level (debug/info/warn/error)
- `MCP_LOG_FILE` - Log file path

## Architecture

```
┌─────────────────┐
│   Claude Code   │
└─────────┬───────┘
          │ MCP Protocol
┌─────────▼───────┐
│  MCP Server     │
│  (Node.js/TS)   │
└─────────┬───────┘
          │ HTTP/WebSocket
┌─────────▼───────┐
│  FastAPI        │
│  Backend        │
└─────────┬───────┘
          │ djitellopy
┌─────────▼───────┐
│  Tello EDU      │
│  Drone          │
└─────────────────┘
```

## Backend Integration

The MCP server communicates with the existing FastAPI backend via HTTP:
- Base URL: `http://localhost:8000` (development)
- Connection: `/drone/connect`, `/drone/disconnect`, `/drone/status`
- Flight: `/flight/takeoff`, `/flight/land`, `/flight/emergency`

## Development Status

✅ **Phase 1 Complete**: Basic MCP foundation
- [x] Project structure and configuration
- [x] MCP server implementation
- [x] Tool registry system
- [x] Connection and flight control tools
- [x] FastAPI bridge client
- [x] Error handling and logging

🚧 **Phase 2 Planned**: Extended functionality
- [ ] Movement control tools
- [ ] Camera operation tools
- [ ] Sensor data tools
- [ ] Real-time streaming support

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Integration tests with backend
npm run test:integration
```

## License

MIT License - see LICENSE file for details.