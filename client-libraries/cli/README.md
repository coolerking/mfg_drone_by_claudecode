# MCP Drone CLI

Command Line Interface for MCP Drone Control Server. This CLI tool provides a convenient way to control drones using natural language commands or direct API calls from the command line.

## Features

- 🗣️ **Natural Language Commands**: Execute drone operations using Japanese natural language
- 🚁 **Complete Drone Control**: Connect, takeoff, move, rotate, land, emergency stop
- 📸 **Camera Operations**: Photo capture, streaming control
- 📊 **System Monitoring**: Health checks, status monitoring, real-time events
- 🔧 **Easy Configuration**: Simple setup with configuration file
- 🌐 **WebSocket Support**: Real-time event monitoring
- 💡 **Interactive Mode**: Guided prompts for complex operations
- 🎨 **Beautiful Output**: Colorized output with progress indicators

## Installation

### Global Installation

```bash
npm install -g mcp-drone-cli
```

### Local Installation

```bash
npm install mcp-drone-cli
npx mcp-drone --help
```

### From Source

```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/cli
npm install
npm run build
npm link
```

## Quick Start

### 1. Configure the CLI

```bash
mcp-drone configure
```

This will prompt you for:
- MCP Server URL (default: http://localhost:8001)
- API Key (optional)
- Bearer Token (optional)
- Request timeout (default: 30000ms)

### 2. Check System Status

```bash
mcp-drone system
mcp-drone health
```

### 3. List Available Drones

```bash
mcp-drone drones
mcp-drone drones --available
```

### 4. Execute Natural Language Commands

```bash
mcp-drone exec "ドローンAAに接続して"
mcp-drone exec "離陸して"
mcp-drone exec "右に50センチ移動して"
mcp-drone exec "写真を撮って"
mcp-drone exec "着陸して"
```

## Command Reference

### Configuration

```bash
# Configure CLI settings
mcp-drone configure
```

### Natural Language Commands

```bash
# Execute single command
mcp-drone exec "ドローンAAに接続して"

# Execute with context
mcp-drone exec "離陸して" --context '{"drone_id": "drone_001"}'

# Dry run mode
mcp-drone exec "緊急停止して" --dry-run

# Confirm before execution
mcp-drone exec "離陸して" --confirm
```

### Batch Commands

```bash
# Execute multiple commands sequentially
mcp-drone batch "ドローンAAに接続して" "離陸して" "写真を撮って"

# Execute in parallel
mcp-drone batch "写真を撮って" "高度を確認して" --mode parallel

# Continue on error
mcp-drone batch "command1" "command2" --no-stop-on-error

# Verbose output
mcp-drone batch "command1" "command2" --verbose
```

### Drone Management

```bash
# List all drones
mcp-drone drones

# List only available drones
mcp-drone drones --available

# Get drone status
mcp-drone status drone_001

# Connect to drone
mcp-drone connect drone_001

# Disconnect from drone
mcp-drone disconnect drone_001
```

### Flight Control

```bash
# Takeoff
mcp-drone takeoff drone_001
mcp-drone takeoff drone_001 --height 100

# Land
mcp-drone land drone_001

# Move
mcp-drone move drone_001 forward 100
mcp-drone move drone_001 right 50 --speed 30

# Rotate
mcp-drone rotate drone_001 clockwise 90
mcp-drone rotate drone_001 left 45

# Emergency stop
mcp-drone emergency drone_001
```

### Camera Operations

```bash
# Take photo
mcp-drone photo drone_001
mcp-drone photo drone_001 --filename "photo.jpg" --quality high
```

### System Operations

```bash
# Get system status
mcp-drone system

# Health check
mcp-drone health

# Watch real-time events
mcp-drone watch
```

## Natural Language Commands

The CLI supports a wide range of Japanese natural language commands:

### Connection Commands
- `ドローンAAに接続して`
- `ドローンに繋げて`
- `ドローンから切断して`

### Flight Control Commands
- `離陸して`
- `ドローンを起動して`
- `飛び立って`
- `着陸して`
- `降りて`
- `緊急停止して`

### Movement Commands
- `右に50センチ移動して`
- `前に1メートル進んで`
- `上に30センチ上がって`
- `後ろに20センチ下がって`

### Rotation Commands
- `右に90度回転して`
- `左に45度向きを変えて`
- `180度回って`

### Altitude Commands
- `高度を1メートルにして`
- `2メートルの高さまで上がって`
- `高度を50センチ下げて`

### Camera Commands
- `写真を撮って`
- `撮影して`
- `カメラで撮って`
- `ストリーミングを開始して`
- `ストリーミングを停止して`

## Configuration File

The CLI stores its configuration in `~/.mcp-drone-cli.yaml`:

```yaml
baseURL: http://localhost:8001
apiKey: your-api-key
bearerToken: your-jwt-token
timeout: 30000
```

You can manually edit this file or use the `mcp-drone configure` command.

## Environment Variables

You can also configure the CLI using environment variables:

```bash
export MCP_DRONE_BASE_URL=http://localhost:8001
export MCP_DRONE_API_KEY=your-api-key
export MCP_DRONE_BEARER_TOKEN=your-jwt-token
export MCP_DRONE_TIMEOUT=30000
```

## Examples

### Basic Drone Operation

```bash
# Configure CLI
mcp-drone configure

# Check system status
mcp-drone health

# List available drones
mcp-drone drones --available

# Connect and operate drone
mcp-drone connect drone_001
mcp-drone takeoff drone_001 --height 100
mcp-drone photo drone_001 --filename "aerial_shot.jpg"
mcp-drone move drone_001 forward 200
mcp-drone rotate drone_001 clockwise 180
mcp-drone land drone_001
mcp-drone disconnect drone_001
```

### Natural Language Workflow

```bash
# Execute a complete workflow using natural language
mcp-drone batch \
  "ドローンAAに接続して" \
  "離陸して" \
  "高度を1.5メートルにして" \
  "右に1メートル移動して" \
  "写真を撮って" \
  "元の位置に戻って" \
  "着陸して"
```

### Real-time Monitoring

```bash
# Watch real-time events in one terminal
mcp-drone watch

# Execute commands in another terminal
mcp-drone exec "ドローンAAに接続して"
mcp-drone exec "離陸して"
```

### Advanced Usage

```bash
# Use dry run to test commands
mcp-drone exec "緊急停止して" --dry-run

# Use context for specific drone
mcp-drone exec "離陸して" --context '{"drone_id": "drone_002"}'

# Execute with confirmation
mcp-drone exec "危険な操作" --confirm

# Parallel batch execution
mcp-drone batch \
  "ドローンAAの状態を確認して" \
  "ドローンBBの状態を確認して" \
  --mode parallel
```

## Error Handling

The CLI provides clear error messages and appropriate exit codes:

```bash
# Exit codes:
# 0 - Success
# 1 - General error
# 2 - Configuration error
# 3 - Network error
# 4 - Authentication error
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/coolerking/mfg_drone_by_claudecode.git
cd mfg_drone_by_claudecode/client-libraries/cli
npm install
```

### Build

```bash
npm run build
```

### Development Mode

```bash
# Run in development mode
npm run dev -- --help

# Set development environment
NODE_ENV=development ./bin/mcp-drone --help
```

### Testing

```bash
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

## Support

For issues and questions, please open an issue in the [GitHub repository](https://github.com/coolerking/mfg_drone_by_claudecode/issues).

## Changelog

### 1.0.0
- Initial release
- Complete MCP API support
- Natural language command processing
- Real-time event monitoring
- Configuration management
- Beautiful CLI interface