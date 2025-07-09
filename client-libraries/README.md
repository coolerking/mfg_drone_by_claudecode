# MCP Drone Client Libraries

Complete client libraries and tools for the MCP Drone Control Server. This collection provides multiple ways to interact with the MCP server, from natural language commands to direct API calls.

## 📦 Libraries & Tools

### [JavaScript SDK](./javascript/)
- **Full-featured JavaScript/TypeScript SDK**
- WebSocket support for real-time communication
- Complete API coverage with TypeScript definitions
- Works in both Node.js and browser environments
- Comprehensive error handling and retry logic

### [Python SDK](./python/)
- **Async/await Python SDK with Pydantic models**
- Full type safety with modern Python features
- Context manager support for resource management
- WebSocket integration for real-time events
- Extensive test coverage with pytest

### [CLI Tool](./cli/)
- **Command-line interface for direct drone control**
- Interactive configuration and guided prompts
- Supports both natural language and direct commands
- Real-time event monitoring with WebSocket
- Batch command execution with parallel processing

### [TypeScript Types](./types/)
- **Comprehensive type definitions for all MCP APIs**
- Type guards and validation utilities
- API endpoint constants and configuration defaults
- WebSocket event type definitions
- Complete IntelliSense support

## 🚀 Quick Start

### 1. Install Your Preferred Library

```bash
# JavaScript/TypeScript SDK
npm install mcp-drone-client

# Python SDK
pip install mcp-drone-client

# CLI Tool
npm install -g mcp-drone-cli

# TypeScript Types (for development)
npm install @mcp-drone/types
```

### 2. Basic Usage Examples

#### JavaScript SDK

```javascript
import { MCPClient } from 'mcp-drone-client';

const client = new MCPClient({
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key'
});

// Natural language command
const response = await client.executeCommand({
  command: 'ドローンAAに接続して'
});

// Direct API call
const drones = await client.getDrones();
await client.connectDrone('drone_001');
await client.takeoff('drone_001', { target_height: 100 });
```

#### Python SDK

```python
import asyncio
from mcp_drone_client import MCPClient, MCPClientConfig, NaturalLanguageCommand

async def main():
    config = MCPClientConfig(
        base_url="http://localhost:8001",
        api_key="your-api-key"
    )
    
    async with MCPClient(config) as client:
        # Natural language command
        response = await client.execute_command(
            NaturalLanguageCommand(command="ドローンAAに接続して")
        )
        
        # Direct API calls
        drones = await client.get_drones()
        await client.connect_drone("drone_001")
        await client.takeoff("drone_001")

asyncio.run(main())
```

#### CLI Tool

```bash
# Configure CLI
mcp-drone configure

# Natural language commands
mcp-drone exec "ドローンAAに接続して"
mcp-drone exec "離陸して"
mcp-drone exec "写真を撮って"

# Direct commands
mcp-drone connect drone_001
mcp-drone takeoff drone_001 --height 100
mcp-drone photo drone_001 --quality high

# Batch commands
mcp-drone batch "ドローンAAに接続して" "離陸して" "写真を撮って"
```

## 🎯 Features

### Natural Language Processing
- **Japanese Command Support**: Execute operations using natural Japanese phrases
- **Intent Recognition**: Automatic parsing of commands with confidence scoring
- **Parameter Extraction**: Intelligent extraction of values like distances, angles, heights
- **Error Suggestions**: Helpful corrections for misunderstood commands

### Complete Drone Control
- **Connection Management**: Connect/disconnect from drones
- **Flight Control**: Takeoff, land, emergency stop with safety checks
- **Movement**: Precise positioning with cm-level accuracy
- **Rotation**: Clockwise/counter-clockwise rotation with degree precision
- **Altitude Control**: Absolute and relative altitude adjustment

### Camera & Vision
- **Photo Capture**: High-quality image capture with metadata
- **Video Streaming**: Real-time video streaming control
- **Object Detection**: AI-powered object recognition
- **Object Tracking**: Automatic object following
- **Learning Data Collection**: Automated multi-angle dataset creation

### System Monitoring
- **Health Checks**: Comprehensive system health monitoring
- **Status Tracking**: Real-time drone and system status
- **Performance Metrics**: Detailed execution statistics
- **Error Reporting**: Comprehensive error tracking and analysis

### Security & Authentication
- **Multiple Auth Methods**: API Key and JWT Bearer token support
- **Rate Limiting**: Built-in protection against abuse
- **Input Validation**: Comprehensive validation of all inputs
- **Secure Communication**: HTTPS and WSS support

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   CLI Tool      │    │   Web Frontend │
│  (JS/Python)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MCP Server    │
                    │  (FastAPI)      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Backend API    │
                    │ (Raspberry Pi)  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Tello Drone    │
                    │   Hardware      │
                    └─────────────────┘
```

## 🛠️ Development

### Prerequisites
- Node.js 16+ (for JavaScript SDK and CLI)
- Python 3.8+ (for Python SDK)
- TypeScript 5.0+ (for type definitions)

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries

# Install dependencies for all projects
npm install  # JavaScript SDK
cd python && pip install -e .[dev]  # Python SDK
cd ../cli && npm install  # CLI Tool
cd ../types && npm install  # TypeScript Types
```

### Running Tests

```bash
# Run all tests
node test_all.js

# Run specific library tests
node test_all.js javascript
node test_all.js python
node test_all.js cli
node test_all.js types

# Run multiple specific tests
node test_all.js javascript python
```

### Build All Libraries

```bash
# Build JavaScript SDK
cd javascript && npm run build

# Build Python SDK
cd python && python setup.py sdist bdist_wheel

# Build CLI Tool
cd cli && npm run build

# Build TypeScript Types
cd types && npm run build
```

## 📊 Comparison Matrix

| Feature | JavaScript SDK | Python SDK | CLI Tool | TypeScript Types |
|---------|---------------|------------|----------|-----------------|
| **Natural Language** | ✅ | ✅ | ✅ | ✅ (Types) |
| **Async/Await** | ✅ | ✅ | ✅ | ✅ (Types) |
| **WebSocket** | ✅ | ✅ | ✅ | ✅ (Types) |
| **Type Safety** | ✅ | ✅ | ✅ | ✅ |
| **Error Handling** | ✅ | ✅ | ✅ | ✅ (Types) |
| **Authentication** | ✅ | ✅ | ✅ | ✅ (Types) |
| **Batch Commands** | ✅ | ✅ | ✅ | ✅ (Types) |
| **Interactive Mode** | ❌ | ❌ | ✅ | ❌ |
| **Browser Support** | ✅ | ❌ | ❌ | ✅ |
| **Command Line** | ❌ | ❌ | ✅ | ❌ |
| **Installation** | npm | pip | npm global | npm dev |

## 🔧 Configuration

All libraries support similar configuration options:

```javascript
// JavaScript/TypeScript
const config = {
  baseURL: 'http://localhost:8001',
  apiKey: 'your-api-key',
  bearerToken: 'your-jwt-token',
  timeout: 30000
};
```

```python
# Python
config = MCPClientConfig(
    base_url="http://localhost:8001",
    api_key="your-api-key",
    bearer_token="your-jwt-token",
    timeout=30.0
)
```

```yaml
# CLI Tool (~/.mcp-drone-cli.yaml)
baseURL: http://localhost:8001
apiKey: your-api-key
bearerToken: your-jwt-token
timeout: 30000
```

## 📚 Documentation

### API Documentation
- [JavaScript SDK Documentation](./javascript/README.md)
- [Python SDK Documentation](./python/README.md)
- [CLI Tool Documentation](./cli/README.md)
- [TypeScript Types Documentation](./types/README.md)

### Examples
- [JavaScript Examples](./javascript/examples/)
- [Python Examples](./python/examples/)
- [CLI Examples](./cli/examples/)

### Natural Language Commands
All libraries support the same natural language commands:

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

## 🤝 Contributing

We welcome contributions to all client libraries! Please follow these guidelines:

1. **Choose the right library**: Make sure your contribution goes to the appropriate library
2. **Follow the existing patterns**: Each library has its own coding style and patterns
3. **Add tests**: All new features should include comprehensive tests
4. **Update documentation**: Keep README files and inline documentation up to date
5. **Test across libraries**: Ensure API changes work across all client libraries

### Development Workflow

```bash
# 1. Fork the repository
git clone https://github.com/yourusername/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
node test_all.js  # Test all libraries
# or
node test_all.js javascript  # Test specific library

# 4. Commit and push
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature

# 5. Create Pull Request
```

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🆘 Support

For issues and questions:
- [GitHub Issues](https://github.com/coolerking/mfg_drone_by_claudecode/issues)
- [Discussions](https://github.com/coolerking/mfg_drone_by_claudecode/discussions)

## 🎯 Roadmap

### v1.1.0
- [ ] React Native SDK
- [ ] Go SDK
- [ ] Rust SDK
- [ ] GraphQL API support

### v1.2.0
- [ ] Real-time collaborative control
- [ ] Advanced AI/ML integration
- [ ] Multi-language natural language support
- [ ] Enhanced security features

### v1.3.0
- [ ] Cloud deployment tools
- [ ] Monitoring and analytics dashboard
- [ ] Plugin system for custom commands
- [ ] Advanced drone swarm coordination

## 🌟 Acknowledgments

- Built with modern development practices and comprehensive testing
- Inspired by best practices from leading API client libraries
- Designed for both beginners and advanced users
- Committed to maintaining high code quality and documentation standards