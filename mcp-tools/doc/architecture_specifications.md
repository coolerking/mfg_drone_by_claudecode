# MCPツール アーキテクチャ仕様書

## 概要

MCPツールシステムのアーキテクチャ仕様を、アプリケーションアーキテクチャとインフラストラクチャアーキテクチャの両面から詳細に定義します。本システムは、Claude Code によるドローン制御を実現するための分散システムです。

## アプリケーションアーキテクチャ

### 全体アーキテクチャ概要

```mermaid
graph TB
    subgraph "Claude Code Environment"
        ClaudeCode[Claude Code<br/>AI Assistant]
        MCPWorkspace[MCP Workspace<br/>Configuration]
    end
    
    subgraph "MCP Tools Application Layer"
        subgraph "Protocol Layer"
            MCPProtocol[MCP Protocol Handler<br/>stdio transport]
            RequestRouter[Request Router<br/>Tool Dispatcher]
        end
        
        subgraph "Tool Management Layer"
            ToolRegistry[Tool Registry<br/>Dynamic Registration]
            ToolExecutor[Tool Executor<br/>Validation & Execution]
        end
        
        subgraph "Business Logic Layer"
            ConnectionMgmt[Connection Management<br/>drone_connect/disconnect/status]
            FlightControl[Flight Control<br/>takeoff/land/emergency/stop]
            MovementControl[Movement Control<br/>move/rotate/coordinate]
            CameraControl[Camera Control<br/>stream/photo/video/settings]
            SensorMgmt[Sensor Management<br/>battery/status/monitoring]
        end
        
        subgraph "Integration Layer"
            APIBridge[API Bridge<br/>HTTP/WebSocket Client]
            TypeSystem[Type System<br/>Zod Validation]
            ErrorHandler[Error Handler<br/>Recovery & Retry]
        end
        
        subgraph "Infrastructure Layer"
            ConfigMgmt[Configuration Management<br/>Environment-based Config]
            LogSystem[Logging System<br/>Structured JSON Logging]
            MetricsCollector[Metrics Collector<br/>Performance Monitoring]
        end
    end
    
    subgraph "Backend API Layer"
        FastAPIBackend[FastAPI Backend<br/>Python REST API]
        DroneService[Drone Service<br/>djitellopy Integration]
    end
    
    subgraph "Hardware Layer"
        TelloDrone[Tello EDU Drone<br/>Physical Device]
    end

    %% Flow connections
    ClaudeCode <-->|MCP Protocol| MCPProtocol
    MCPWorkspace -->|Configuration| ConfigMgmt
    MCPProtocol --> RequestRouter
    RequestRouter --> ToolRegistry
    ToolRegistry --> ToolExecutor
    
    ToolExecutor --> ConnectionMgmt
    ToolExecutor --> FlightControl
    ToolExecutor --> MovementControl
    ToolExecutor --> CameraControl
    ToolExecutor --> SensorMgmt
    
    ConnectionMgmt --> APIBridge
    FlightControl --> APIBridge
    MovementControl --> APIBridge
    CameraControl --> APIBridge
    SensorMgmt --> APIBridge
    
    APIBridge --> TypeSystem
    APIBridge --> ErrorHandler
    APIBridge <-->|HTTP/REST| FastAPIBackend
    
    ConfigMgmt --> LogSystem
    LogSystem --> MetricsCollector
    
    FastAPIBackend <--> DroneService
    DroneService <-->|UDP 8889/11111| TelloDrone

    style ClaudeCode fill:#e1f5fe
    style MCPProtocol fill:#f3e5f5
    style APIBridge fill:#fff3e0
    style FastAPIBackend fill:#e8f5e8
    style TelloDrone fill:#ffebee
```

### モジュール・コンポーネント構成

#### 1. MCP Server Core Module

```mermaid
graph TB
    subgraph "MCP Server Core (@mcp-tools/src/)"
        subgraph "server.ts - Main Server"
            MCPServer[MCPServer Class]
            TransportMgr[Transport Manager]
            RequestHandler[Request Handler]
        end
        
        subgraph "index.ts - Entry Point"
            AppBootstrap[Application Bootstrap]
            ConfigLoader[Configuration Loader]
            ErrorSetup[Error Handler Setup]
        end
        
        subgraph "types/ - Type Definitions"
            ConfigTypes[config.ts<br/>Configuration Types]
            APITypes[api.ts<br/>API Response Types]
            DroneTypes[drone.ts<br/>Drone-specific Types]
            MCPTypes[mcp.ts<br/>MCP Protocol Types]
        end
        
        subgraph "utils/ - Utility Functions"
            ConfigUtil[config.ts<br/>Configuration Management]
            LoggerUtil[logger.ts<br/>Structured Logging]
            ValidatorUtil[validators.ts<br/>Input Validation]
        end
    end

    MCPServer --> TransportMgr
    MCPServer --> RequestHandler
    AppBootstrap --> ConfigLoader
    AppBootstrap --> ErrorSetup
    ConfigLoader --> ConfigTypes
    RequestHandler --> APITypes
    RequestHandler --> DroneTypes
    ConfigUtil --> ConfigTypes
    LoggerUtil --> ConfigTypes
    RequestHandler --> ValidatorUtil

    style MCPServer fill:#e3f2fd
    style ConfigTypes fill:#f3e5f5
    style LoggerUtil fill:#fff3e0
```

#### 2. Tool Management Module

```mermaid
graph TB
    subgraph "Tools Module (@mcp-tools/src/tools/)"
        subgraph "registry.ts - Tool Registry"
            ToolRegistry[Tool Registry]
            ToolLoader[Dynamic Tool Loader]
            ToolValidator[Tool Validator]
        end
        
        subgraph "connection.ts - Connection Tools"
            DroneConnect[drone_connect Tool]
            DroneDisconnect[drone_disconnect Tool]
            DroneStatus[drone_status Tool]
        end
        
        subgraph "flight.ts - Flight Control Tools"
            DroneTakeoff[drone_takeoff Tool]
            DroneLand[drone_land Tool]
            DroneEmergency[drone_emergency Tool]
            DroneStop[drone_stop Tool]
            DroneGetHeight[drone_get_height Tool]
        end
        
        subgraph "movement.ts - Movement Tools"
            DroneMove[drone_move Tool]
            DroneRotate[drone_rotate Tool]
            DroneFlip[drone_flip Tool]
            DroneGoXYZ[drone_go_xyz Tool]
            DroneCurve[drone_curve Tool]
            DroneRCControl[drone_rc_control Tool]
        end
        
        subgraph "camera.ts - Camera Tools"
            CameraStreamStart[camera_stream_start Tool]
            CameraStreamStop[camera_stream_stop Tool]
            CameraTakePhoto[camera_take_photo Tool]
            CameraStartRecording[camera_start_recording Tool]
            CameraStopRecording[camera_stop_recording Tool]
            CameraSettings[camera_settings Tool]
        end
        
        subgraph "sensors.ts - Sensor Tools"
            DroneBattery[drone_battery Tool]
            DroneTemperature[drone_temperature Tool]
            DroneFlightTime[drone_flight_time Tool]
            DroneBarometer[drone_barometer Tool]
            DroneDistanceTOF[drone_distance_tof Tool]
            DroneAcceleration[drone_acceleration Tool]
            DroneVelocity[drone_velocity Tool]
            DroneAttitude[drone_attitude Tool]
            DroneSensorSummary[drone_sensor_summary Tool]
        end
    end

    ToolRegistry --> ToolLoader
    ToolRegistry --> ToolValidator
    
    ToolLoader --> DroneConnect
    ToolLoader --> DroneTakeoff
    ToolLoader --> DroneMove
    ToolLoader --> CameraStreamStart
    ToolLoader --> DroneBattery

    style ToolRegistry fill:#e3f2fd
    style DroneConnect fill:#f3e5f5
    style DroneTakeoff fill:#fff3e0
    style DroneMove fill:#e8f5e8
    style CameraStreamStart fill:#ffebee
```

#### 3. API Bridge Module

```mermaid
graph TB
    subgraph "Bridge Module (@mcp-tools/src/bridge/)"
        subgraph "api-client.ts - Main Client"
            FastAPIClient[FastAPIClient Class]
            HTTPManager[HTTP Connection Manager]
            RequestBuilder[Request Builder]
            ResponseParser[Response Parser]
        end
        
        subgraph "retry-strategy.ts - Retry Logic"
            RetryManager[Retry Manager]
            ExponentialBackoff[Exponential Backoff]
            CircuitBreaker[Circuit Breaker]
        end
        
        subgraph "health-monitor.ts - Health Monitoring"
            HealthChecker[Health Checker]
            MetricsCollector[Metrics Collector]
            AlertManager[Alert Manager]
        end
        
        subgraph "websocket-handler.ts - WebSocket Support"
            WebSocketClient[WebSocket Client]
            StreamManager[Stream Manager]
            EventHandler[Event Handler]
        end
        
        subgraph "error-handler.ts - Error Management"
            ErrorAnalyzer[Error Analyzer]
            ErrorMapper[Error Code Mapper]
            RecoveryManager[Recovery Manager]
        end
    end

    FastAPIClient --> HTTPManager
    FastAPIClient --> RequestBuilder
    FastAPIClient --> ResponseParser
    FastAPIClient --> RetryManager
    
    RetryManager --> ExponentialBackoff
    RetryManager --> CircuitBreaker
    
    HealthChecker --> MetricsCollector
    HealthChecker --> AlertManager
    
    WebSocketClient --> StreamManager
    WebSocketClient --> EventHandler
    
    ErrorAnalyzer --> ErrorMapper
    ErrorAnalyzer --> RecoveryManager

    style FastAPIClient fill:#e3f2fd
    style RetryManager fill:#f3e5f5
    style HealthChecker fill:#fff3e0
    style ErrorAnalyzer fill:#e8f5e8
```

### データフロー・処理パターン

#### Request-Response パターン

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant MCP as MCP Server
    participant Tool as Tool Handler
    participant Bridge as API Bridge
    participant Backend as FastAPI Backend

    Claude->>MCP: MCP Request<br/>{"method": "tools/call", "params": {...}}
    activate MCP
    MCP->>MCP: Validate Request Schema
    MCP->>Tool: Execute Tool<br/>tool_name(params)
    activate Tool
    Tool->>Tool: Validate Parameters
    Tool->>Bridge: API Call
    activate Bridge
    Bridge->>Bridge: Build HTTP Request
    Bridge->>Backend: HTTP Request
    activate Backend
    Backend-->>Bridge: HTTP Response
    deactivate Backend
    Bridge->>Bridge: Parse Response
    Bridge-->>Tool: Parsed Result
    deactivate Bridge
    Tool->>Tool: Format Result
    Tool-->>MCP: Tool Result
    deactivate Tool
    MCP->>MCP: Build MCP Response
    MCP-->>Claude: MCP Response<br/>{"result": {...}}
    deactivate MCP
```

#### Error Handling パターン

```mermaid
graph TB
    subgraph "Error Detection"
        APIError[API Error<br/>HTTP 4xx/5xx]
        NetworkError[Network Error<br/>Timeout/Connection]
        ValidationError[Validation Error<br/>Parameter Issues]
        DroneError[Drone Error<br/>Hardware Issues]
    end
    
    subgraph "Error Analysis"
        ErrorClassifier[Error Classifier<br/>Type & Severity]
        RetryDecision[Retry Decision<br/>Recoverable?]
        SeverityAssessment[Severity Assessment<br/>Critical/Warning/Info]
    end
    
    subgraph "Error Response"
        AutoRetry[Auto Retry<br/>Exponential Backoff]
        UserNotification[User Notification<br/>Error Message]
        EmergencyAction[Emergency Action<br/>Safety Protocol]
        LogRecording[Log Recording<br/>Incident Report]
    end

    APIError --> ErrorClassifier
    NetworkError --> ErrorClassifier
    ValidationError --> ErrorClassifier
    DroneError --> ErrorClassifier
    
    ErrorClassifier --> RetryDecision
    ErrorClassifier --> SeverityAssessment
    
    RetryDecision -->|Recoverable| AutoRetry
    RetryDecision -->|Non-recoverable| UserNotification
    SeverityAssessment -->|Critical| EmergencyAction
    SeverityAssessment -->|All levels| LogRecording

    style APIError fill:#ffebee
    style ErrorClassifier fill:#fff3e0
    style EmergencyAction fill:#ffcdd2
```

## インフラストラクチャアーキテクチャ

### システム構成図

```mermaid
graph TB
    subgraph "Client Environment"
        subgraph "Windows PC / macOS / Linux"
            ClaudeCodeApp[Claude Code Application]
            MCPWorkspaceConfig[mcp-workspace.json<br/>Configuration File]
        end
    end
    
    subgraph "Server Environment (Raspberry Pi 5)"
        subgraph "Node.js Runtime"
            MCPServer[MCP Server Process<br/>Node.js 18+]
            NPMPackages[NPM Dependencies<br/>@modelcontextprotocol/sdk]
        end
        
        subgraph "Python Runtime"
            FastAPIProcess[FastAPI Server Process<br/>Python 3.11+]
            PythonPackages[Python Dependencies<br/>djitellopy, FastAPI, OpenCV]
        end
        
        subgraph "System Services"
            SystemdServices[Systemd Services<br/>mcp-drone-tools.service]
            LogRotation[Log Rotation<br/>logrotate config]
            ProcessMonitoring[Process Monitoring<br/>healthcheck]
        end
        
        subgraph "Storage"
            ConfigFiles[Configuration Files<br/>/opt/mcp-tools/config/]
            LogFiles[Log Files<br/>/var/log/mcp-tools/]
            TempFiles[Temporary Files<br/>/tmp/mcp-tools/]
        end
    end
    
    subgraph "Network Infrastructure"
        HomeRouter[Home Network Router<br/>192.168.1.0/24]
        WiFiAP[WiFi Access Point<br/>Drone Communication]
    end
    
    subgraph "Hardware"
        TelloDroneHW[Tello EDU Drone<br/>WiFi: 192.168.10.1<br/>UDP: 8889/11111]
    end

    %% Connections
    ClaudeCodeApp <-->|stdio transport| MCPServer
    MCPWorkspaceConfig -->|Configuration| MCPServer
    MCPServer <-->|HTTP/REST API| FastAPIProcess
    FastAPIProcess <-->|UDP Commands| TelloDroneHW
    
    SystemdServices --> MCPServer
    SystemdServices --> FastAPIProcess
    ProcessMonitoring --> MCPServer
    ProcessMonitoring --> FastAPIProcess
    
    MCPServer --> ConfigFiles
    FastAPIProcess --> ConfigFiles
    MCPServer --> LogFiles
    FastAPIProcess --> LogFiles
    
    HomeRouter <--> ClaudeCodeApp
    HomeRouter <--> MCPServer
    HomeRouter <--> FastAPIProcess
    WiFiAP <--> TelloDroneHW
    HomeRouter <--> WiFiAP

    style ClaudeCodeApp fill:#e1f5fe
    style MCPServer fill:#f3e5f5
    style FastAPIProcess fill:#e8f5e8
    style TelloDroneHW fill:#ffebee
    style HomeRouter fill:#fff3e0
```

### デプロイメント構成

#### Production Environment (Raspberry Pi 5)

```mermaid
graph TB
    subgraph "Operating System Layer"
        RaspberryPiOS[Raspberry Pi OS<br/>64-bit Lite Version]
        SystemPackages[System Packages<br/>nodejs, python3.11, npm]
        SystemServices[System Services<br/>SSH, NetworkManager]
    end
    
    subgraph "Application Runtime Layer"
        subgraph "Node.js Environment"
            NodeJS[Node.js 18.17.0+]
            NPM[NPM Package Manager]
            MCPToolsApp[MCP Tools Application<br/>Built TypeScript]
        end
        
        subgraph "Python Environment"
            Python311[Python 3.11+]
            PipManager[Pip Package Manager]
            FastAPIApp[FastAPI Application<br/>Backend Server]
        end
    end
    
    subgraph "Service Management Layer"
        SystemdMCP[systemd Service<br/>mcp-drone-tools.service]
        SystemdAPI[systemd Service<br/>mfg-drone-backend.service]
        SystemdHealthcheck[systemd Timer<br/>healthcheck.timer]
    end
    
    subgraph "Configuration Management Layer"
        ConfigProduction[Production Config<br/>/opt/mcp-tools/config/production.json]
        EnvironmentVars[Environment Variables<br/>BACKEND_URL, DEBUG, etc.]
        LogConfig[Log Configuration<br/>/etc/logrotate.d/mcp-tools]
    end
    
    subgraph "Storage & Persistence Layer"
        ApplicationLogs[Application Logs<br/>/var/log/mcp-tools/]
        SystemLogs[System Logs<br/>/var/log/syslog]
        TempStorage[Temporary Storage<br/>/tmp/mcp-tools/]
        BackupStorage[Backup Storage<br/>/opt/backups/]
    end

    RaspberryPiOS --> SystemPackages
    SystemPackages --> NodeJS
    SystemPackages --> Python311
    
    NodeJS --> NPM
    NPM --> MCPToolsApp
    Python311 --> PipManager
    PipManager --> FastAPIApp
    
    SystemdMCP --> MCPToolsApp
    SystemdAPI --> FastAPIApp
    SystemdHealthcheck --> MCPToolsApp
    SystemdHealthcheck --> FastAPIApp
    
    ConfigProduction --> MCPToolsApp
    ConfigProduction --> FastAPIApp
    EnvironmentVars --> MCPToolsApp
    EnvironmentVars --> FastAPIApp
    
    MCPToolsApp --> ApplicationLogs
    FastAPIApp --> ApplicationLogs
    MCPToolsApp --> TempStorage
    ApplicationLogs --> BackupStorage

    style RaspberryPiOS fill:#e3f2fd
    style MCPToolsApp fill:#f3e5f5
    style FastAPIApp fill:#e8f5e8
    style SystemdMCP fill:#fff3e0
```

#### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        subgraph "Local Development"
            VSCode[VS Code / IDE]
            LocalNodeJS[Node.js Development]
            LocalPython[Python Development]
            LocalTesting[Local Testing<br/>Jest + Mock Backend]
        end
        
        subgraph "Development Tools"
            ESLint[ESLint + Prettier<br/>Code Quality]
            TypeScriptCompiler[TypeScript Compiler<br/>Type Checking]
            TestRunner[Test Runner<br/>Jest + Coverage]
            DevServer[Development Server<br/>npm run dev]
        end
    end
    
    subgraph "Mock Environment"
        MockBackend[Mock FastAPI Backend<br/>Test Responses]
        MockDrone[Mock Drone Simulator<br/>TelloStub]
        TestDatabase[Test Data<br/>Fixtures & Scenarios]
    end
    
    subgraph "CI/CD Pipeline"
        GitHubActions[GitHub Actions<br/>Automated Testing]
        BuildProcess[Build Process<br/>TypeScript → JavaScript]
        TestExecution[Test Execution<br/>Unit + Integration]
        QualityGates[Quality Gates<br/>Coverage + Linting]
    end

    VSCode --> LocalNodeJS
    VSCode --> LocalPython
    LocalNodeJS --> DevServer
    LocalPython --> MockBackend
    
    ESLint --> LocalNodeJS
    TypeScriptCompiler --> LocalNodeJS
    TestRunner --> LocalTesting
    DevServer --> MockBackend
    
    MockBackend --> MockDrone
    MockDrone --> TestDatabase
    LocalTesting --> MockBackend
    
    GitHubActions --> BuildProcess
    BuildProcess --> TestExecution
    TestExecution --> QualityGates

    style VSCode fill:#e3f2fd
    style DevServer fill:#f3e5f5
    style MockBackend fill:#e8f5e8
    style GitHubActions fill:#fff3e0
```

### ネットワーク構成

#### Communication Protocols & Ports

```mermaid
graph TB
    subgraph "Client Network"
        ClientPC[Client PC<br/>192.168.1.100]
    end
    
    subgraph "Server Network"
        RaspberryPi[Raspberry Pi 5<br/>192.168.1.101]
        MCPServerPort[MCP Server<br/>stdio (no network port)]
        FastAPIPort[FastAPI Backend<br/>:8000 HTTP]
        HealthCheckPort[Health Check<br/>:8000/health]
    end
    
    subgraph "Drone Network"
        TelloDrone[Tello EDU<br/>192.168.10.1]
        ControlPort[Control Commands<br/>UDP :8889]
        VideoPort[Video Stream<br/>UDP :11111]
    end
    
    subgraph "Network Infrastructure"
        Router[Home Router<br/>192.168.1.1]
        WiFiNetwork[WiFi Network<br/>SSID: home_network]
        DroneWiFi[Drone WiFi AP<br/>SSID: TELLO-XXXXXX]
    end

    ClientPC <-->|MCP stdio| MCPServerPort
    MCPServerPort <-->|HTTP :8000| FastAPIPort
    FastAPIPort <-->|Health Check| HealthCheckPort
    
    FastAPIPort <-->|UDP :8889| ControlPort
    FastAPIPort <-->|UDP :11111| VideoPort
    
    ClientPC <--> Router
    RaspberryPi <--> Router
    Router <--> WiFiNetwork
    WiFiNetwork <--> DroneWiFi
    ControlPort <--> TelloDrone
    VideoPort <--> TelloDrone

    style ClientPC fill:#e1f5fe
    style MCPServerPort fill:#f3e5f5
    style FastAPIPort fill:#e8f5e8
    style TelloDrone fill:#ffebee
```

#### Security & Firewall Configuration

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            FirewallRules[Firewall Rules<br/>iptables / ufw]
            NetworkSegmentation[Network Segmentation<br/>IoT Device Isolation]
            WiFiSecurity[WiFi Security<br/>WPA3 Encryption]
        end
        
        subgraph "Application Security"
            InputValidation[Input Validation<br/>Zod Schema Validation]
            APIAuthentication[API Authentication<br/>Future: API Keys]
            RateLimiting[Rate Limiting<br/>Request Throttling]
        end
        
        subgraph "System Security"
            UserPermissions[User Permissions<br/>Non-root Execution]
            FilePermissions[File Permissions<br/>Secure Configuration]
            LogSecurity[Log Security<br/>Secure Log Access]
        end
        
        subgraph "Monitoring & Alerts"
            SecurityLogging[Security Logging<br/>Access & Error Logs]
            IntrusionDetection[Intrusion Detection<br/>Fail2ban]
            HealthMonitoring[Health Monitoring<br/>System Status]
        end
    end

    FirewallRules -->|Block unauthorized| NetworkSegmentation
    NetworkSegmentation -->|Isolate IoT| WiFiSecurity
    
    InputValidation -->|Validate MCP calls| APIAuthentication
    APIAuthentication -->|Limit access| RateLimiting
    
    UserPermissions -->|Restrict access| FilePermissions
    FilePermissions -->|Secure config| LogSecurity
    
    SecurityLogging -->|Monitor access| IntrusionDetection
    IntrusionDetection -->|Alert on issues| HealthMonitoring

    style FirewallRules fill:#ffebee
    style InputValidation fill:#fff3e0
    style UserPermissions fill:#e8f5e8
    style SecurityLogging fill:#e1f5fe
```

### 運用・監視

#### System Monitoring

```mermaid
graph TB
    subgraph "Performance Monitoring"
        CPUMonitoring[CPU Usage<br/>System Load]
        MemoryMonitoring[Memory Usage<br/>Heap & RSS]
        NetworkMonitoring[Network I/O<br/>Bandwidth Usage]
        DiskMonitoring[Disk I/O<br/>Storage Usage]
    end
    
    subgraph "Application Monitoring"
        MCPMetrics[MCP Server Metrics<br/>Request Count & Latency]
        APIMetrics[API Bridge Metrics<br/>Success Rate & Response Time]
        DroneMetrics[Drone Metrics<br/>Connection Status & Battery]
        ErrorMetrics[Error Metrics<br/>Error Rate & Types]
    end
    
    subgraph "Health Checks"
        SystemHealth[System Health<br/>Service Status]
        ApplicationHealth[Application Health<br/>Component Status]
        ExternalHealth[External Health<br/>Drone Connectivity]
        EndToEndHealth[End-to-End Health<br/>Full Flow Test]
    end
    
    subgraph "Alerting System"
        CriticalAlerts[Critical Alerts<br/>System Down / Emergency]
        WarningAlerts[Warning Alerts<br/>Performance Degradation]
        InfoAlerts[Info Alerts<br/>Status Changes]
        AlertChannels[Alert Channels<br/>Log Files / Email (Future)]
    end

    CPUMonitoring --> SystemHealth
    MemoryMonitoring --> SystemHealth
    NetworkMonitoring --> ApplicationHealth
    DiskMonitoring --> SystemHealth
    
    MCPMetrics --> ApplicationHealth
    APIMetrics --> ApplicationHealth
    DroneMetrics --> ExternalHealth
    ErrorMetrics --> ApplicationHealth
    
    SystemHealth --> CriticalAlerts
    ApplicationHealth --> WarningAlerts
    ExternalHealth --> CriticalAlerts
    EndToEndHealth --> WarningAlerts
    
    CriticalAlerts --> AlertChannels
    WarningAlerts --> AlertChannels
    InfoAlerts --> AlertChannels

    style CPUMonitoring fill:#e3f2fd
    style MCPMetrics fill:#f3e5f5
    style SystemHealth fill:#e8f5e8
    style CriticalAlerts fill:#ffebee
```

### スケーラビリティ・可用性

#### High Availability Considerations

```mermaid
graph TB
    subgraph "Redundancy Planning"
        ServiceRedundancy[Service Redundancy<br/>Multiple MCP Server Instances]
        DataBackup[Data Backup<br/>Configuration & Logs]
        FailoverPlanning[Failover Planning<br/>Backup Raspberry Pi]
    end
    
    subgraph "Load Management"
        ConnectionPooling[Connection Pooling<br/>HTTP Client Optimization]
        RequestQueueing[Request Queueing<br/>Async Processing]
        ResourceManagement[Resource Management<br/>Memory & CPU Limits]
    end
    
    subgraph "Recovery Mechanisms"
        AutoRestart[Auto Restart<br/>Systemd Service Recovery]
        GracefulShutdown[Graceful Shutdown<br/>Clean Process Termination]
        StateRecovery[State Recovery<br/>Connection Re-establishment]
    end
    
    subgraph "Capacity Planning"
        ConcurrentConnections[Concurrent Connections<br/>Multiple Claude Instances]
        DroneFleet[Drone Fleet<br/>Multi-Drone Support (Future)]
        CloudIntegration[Cloud Integration<br/>Remote MCP Server (Future)]
    end

    ServiceRedundancy --> AutoRestart
    DataBackup --> StateRecovery
    FailoverPlanning --> GracefulShutdown
    
    ConnectionPooling --> RequestQueueing
    RequestQueueing --> ResourceManagement
    
    AutoRestart --> GracefulShutdown
    GracefulShutdown --> StateRecovery
    
    ConcurrentConnections --> DroneFleet
    DroneFleet --> CloudIntegration

    style ServiceRedundancy fill:#e3f2fd
    style ConnectionPooling fill:#f3e5f5
    style AutoRestart fill:#e8f5e8
    style ConcurrentConnections fill:#fff3e0
```

## 技術仕様詳細

### パフォーマンス要件

| 項目 | 要件 | 測定方法 |
|------|------|----------|
| MCP Tool Response | < 50ms | Claude → MCP Server → Response |
| API Bridge Latency | < 100ms | MCP → FastAPI → Response |
| Drone Command Execution | < 200ms | API → Drone → Confirmation |
| Emergency Stop Response | < 500ms | 最優先処理での応答時間 |
| Video Stream Latency | < 150ms | フレーム取得から配信まで |
| Battery Monitoring Frequency | 30秒間隔 | 定期バッテリー状態取得 |
| Memory Usage (MCP Server) | < 256MB | RSS Memory |
| Memory Usage (API Bridge) | < 128MB | HTTP Client Memory |
| CPU Usage (Normal Operation) | < 30% | Raspberry Pi 5 CPU |
| Disk Storage (Logs) | < 1GB/month | Log file rotation |

### 信頼性要件

| 項目 | 要件 | 実装方法 |
|------|------|----------|
| System Uptime | 99.5% | Systemd auto-restart |
| Request Success Rate | > 95% | Retry mechanism |
| Error Recovery Time | < 30秒 | Automatic recovery |
| Data Persistence | 100% | Structured logging |
| Connection Recovery | < 10秒 | Auto-reconnection |
| Graceful Degradation | 対応済み | Fallback mechanisms |

### セキュリティ要件

| 項目 | 要件 | 実装状況 |
|------|------|----------|
| Input Validation | 全パラメータ | Zod schema validation |
| Authentication | 基本実装 | Local network only |
| Authorization | 基本実装 | Tool-level permissions |
| Audit Logging | 完全実装 | Structured JSON logs |
| Data Encryption | 将来実装 | HTTPS/TLS support |
| Network Security | 基本実装 | Firewall rules |