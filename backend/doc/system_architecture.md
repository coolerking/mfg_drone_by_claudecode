# システム構成図

## 概要

MFG Drone Backend API は、Tello EDU ドローンの自動追従撮影システムのコアとなるバックエンドサービスです。Raspberry Pi 5 上で動作し、ドローン制御、AI による物体認識・追跡、リアルタイム映像配信を統合的に提供します。

## 全体システム構成

```mermaid
graph TB
    subgraph "External Devices"
        Drone[Tello EDU Drone]
        AdminPC[Admin PC<br/>Windows 11 Pro]
        UserPC[User PC<br/>Windows 11 Pro]
        iPad[iPad Air<br/>Safari Browser]
    end

    subgraph "Raspberry Pi 5 Environment"
        subgraph "Backend API Server"
            FastAPI[FastAPI Application]
            DroneService[Drone Service Layer]
            AI[AI Processing Module]
            Camera[Camera Handler]
            WebSocket[WebSocket Manager]
        end
        
        subgraph "Data Layer"
            Models[AI Models Storage]
            Config[Configuration Files]
            Logs[Log Files]
        end
    end

    subgraph "Windows PC Environment"
        AdminFE[Admin Frontend<br/>Flask App]
        UserFE[User Frontend<br/>Flask App]
    end

    subgraph "Network Infrastructure"
        Router[Home Network Router<br/>192.168.1.x]
        WiFi[WiFi Access Point]
    end

    %% Connections
    Drone <-.->|WiFi AP Mode| Router
    AdminPC <-->|HTTP/WebSocket| Router
    UserPC <-->|HTTP/WebSocket| Router
    iPad <-->|HTTP/WebSocket| Router
    
    Router <-->|Ethernet/WiFi| FastAPI
    FastAPI <--> DroneService
    DroneService <--> AI
    DroneService <--> Camera
    FastAPI <--> WebSocket
    
    DroneService <--> Models
    FastAPI <--> Config
    FastAPI <--> Logs
    
    AdminFE <-->|API Calls| FastAPI
    UserFE <-->|API Calls| FastAPI
    
    style Drone fill:#e1f5fe
    style FastAPI fill:#f3e5f5
    style AI fill:#fff3e0
    style Router fill:#e8f5e8
```

## バックエンド内部アーキテクチャ

```mermaid
graph TB
    subgraph "Presentation Layer"
        REST[REST API Endpoints]
        WS[WebSocket Endpoints]
        Docs[OpenAPI Documentation]
    end
    
    subgraph "Application Layer"
        Routers[FastAPI Routers]
        Middleware[CORS Middleware]
        Auth[Authentication<br/>Future]
    end
    
    subgraph "Business Logic Layer"
        DroneService[Drone Service]
        TrackingService[Tracking Service]
        ModelService[Model Management]
        CameraService[Camera Service]
    end
    
    subgraph "Infrastructure Layer"
        TelloSDK[djitellopy SDK]
        OpenCV[OpenCV Vision]
        FileSystem[File System]
        Network[Network Layer]
    end
    
    subgraph "External Systems"
        TelloDrone[Tello EDU Drone]
        Storage[Local Storage]
    end

    %% Flow connections
    REST --> Routers
    WS --> Routers
    Routers --> Middleware
    Middleware --> DroneService
    Middleware --> TrackingService
    Middleware --> ModelService
    Middleware --> CameraService
    
    DroneService --> TelloSDK
    TrackingService --> OpenCV
    ModelService --> FileSystem
    CameraService --> OpenCV
    
    TelloSDK <--> TelloDrone
    OpenCV --> FileSystem
    FileSystem --> Storage
    Network --> TelloDrone
    
    style REST fill:#e3f2fd
    style DroneService fill:#f3e5f5
    style TelloSDK fill:#fff3e0
    style TelloDrone fill:#e1f5fe
```

## ネットワーク構成

```mermaid
graph LR
    subgraph "Home Network (192.168.1.0/24)"
        Router[Router/Gateway<br/>192.168.1.1]
        RaspberryPi[Raspberry Pi 5<br/>192.168.1.100<br/>Backend API]
        AdminPC[Admin PC<br/>192.168.1.101<br/>Flask Admin]
        UserPC[User PC<br/>192.168.1.102<br/>Flask User]
        iPad[iPad Air<br/>192.168.1.103<br/>Safari Browser]
    end
    
    subgraph "Drone Network"
        TelloDrone[Tello EDU<br/>WiFi AP Mode<br/>192.168.10.1]
    end
    
    Internet[Internet] <--> Router
    Router <--> RaspberryPi
    Router <--> AdminPC
    Router <--> UserPC
    Router <--> iPad
    
    RaspberryPi <-.->|UDP 8889<br/>Control| TelloDrone
    RaspberryPi <-.->|UDP 11111<br/>Video Stream| TelloDrone
    
    AdminPC -->|HTTP 8000<br/>API Calls| RaspberryPi
    UserPC -->|HTTP 8000<br/>API Calls| RaspberryPi
    iPad -->|HTTP 8000<br/>WebSocket| RaspberryPi
    
    style TelloDrone fill:#e1f5fe
    style RaspberryPi fill:#f3e5f5
    style Router fill:#e8f5e8
```

## データフロー図

```mermaid
sequenceDiagram
    participant Admin as Admin Interface
    participant API as Backend API
    participant Drone as Tello EDU
    participant AI as AI Processing
    participant User as User Interface

    Note over Admin,User: System Initialization
    Admin->>API: Connect to Drone
    API->>Drone: Establish Connection
    Drone-->>API: Connection Confirmed
    API-->>Admin: Connection Status

    Note over Admin,User: Flight & Streaming Setup
    Admin->>API: Start Video Stream
    API->>Drone: Enable Video Stream
    Admin->>API: Takeoff Command
    API->>Drone: Execute Takeoff
    
    Note over Admin,User: Object Detection & Tracking
    Admin->>API: Upload Training Images
    API->>AI: Train Object Model
    AI-->>API: Model Ready
    Admin->>API: Start Object Tracking
    
    loop Real-time Tracking
        Drone->>API: Video Frame
        API->>AI: Process Frame
        AI->>AI: Object Detection
        AI-->>API: Object Position
        API->>Drone: Movement Commands
        API-->>User: Live Video Stream
        API-->>Admin: Tracking Status
    end

    Note over Admin,User: System Shutdown
    Admin->>API: Stop Tracking
    Admin->>API: Land Drone
    API->>Drone: Execute Landing
    Admin->>API: Disconnect
```

## コンポーネント相互作用

```mermaid
graph TB
    subgraph "Client Applications"
        AdminUI[Admin UI<br/>Training & Control]
        UserUI[User UI<br/>Video Display]
        MobileUI[Mobile UI<br/>Basic Control]
    end
    
    subgraph "Backend API Core"
        Router[Router Layer]
        Service[Service Layer]
        Infrastructure[Infrastructure Layer]
    end
    
    subgraph "Hardware Integration"
        DroneComm[Drone Communication]
        VideoCapture[Video Capture]
        AIProcessor[AI Processor]
    end
    
    AdminUI -->|Model Training<br/>Flight Control| Router
    UserUI -->|Video Stream<br/>Status Monitor| Router
    MobileUI -->|Basic Commands| Router
    
    Router --> Service
    Service --> Infrastructure
    
    Infrastructure --> DroneComm
    Infrastructure --> VideoCapture
    Infrastructure --> AIProcessor
    
    DroneComm <--> VideoCapture
    VideoCapture --> AIProcessor
    AIProcessor --> DroneComm
    
    style AdminUI fill:#ffebee
    style UserUI fill:#e8f5e8
    style MobileUI fill:#fff3e0
    style Service fill:#f3e5f5
```

## 技術スタック

```mermaid
graph TB
    subgraph "Frontend Technologies"
        Flask[Flask 2.3+]
        HTML[HTML5/CSS3]
        JS[JavaScript ES6+]
        Bootstrap[Bootstrap 5]
    end
    
    subgraph "Backend Technologies"
        FastAPI[FastAPI 0.104+]
        Python[Python 3.11]
        Uvicorn[Uvicorn ASGI]
        Pydantic[Pydantic Models]
    end
    
    subgraph "AI/Computer Vision"
        OpenCV[OpenCV 4.8+]
        NumPy[NumPy 1.24+]
        Pillow[Pillow 10.1+]
        TensorFlow[TensorFlow Lite<br/>Future]
    end
    
    subgraph "Drone Integration"
        djitellopy[djitellopy 2.5]
        UDP[UDP Protocol]
        WiFi[WiFi Communication]
    end
    
    subgraph "Infrastructure"
        RaspberryPi[Raspberry Pi OS 64-bit]
        Docker[Docker<br/>Future]
        Systemd[Systemd Services]
    end
    
    Frontend --> Backend
    Backend --> AI
    Backend --> Drone
    AI --> Infrastructure
    Drone --> Infrastructure
    
    style Python fill:#3776ab,color:#fff
    style FastAPI fill:#009688,color:#fff
    style OpenCV fill:#5c3ee8,color:#fff
    style RaspberryPi fill:#c51a4a,color:#fff
```

## 性能特性

| 項目 | 仕様 | 備考 |
|------|------|------|
| **フレームレート** | 30 FPS | Tello EDU標準 |
| **映像解像度** | 720p (1280x720) | HD品質 |
| **制御遅延** | < 100ms | UDP通信 |
| **AI処理遅延** | < 50ms | 軽量モデル使用 |
| **同時接続** | 最大10クライアント | WebSocket制限 |
| **ネットワーク帯域** | 5-10 Mbps | 映像ストリーミング |

## セキュリティ境界

```mermaid
graph TB
    subgraph "Trusted Zone"
        BackendAPI[Backend API<br/>Raspberry Pi 5]
        LocalStorage[Local File System]
    end
    
    subgraph "Semi-Trusted Zone"
        HomeNetwork[Home Network<br/>192.168.1.0/24]
        AdminPC[Admin PC]
        UserPC[User PC]
    end
    
    subgraph "External Zone"
        Internet[Internet]
        TelloDrone[Tello EDU<br/>WiFi AP Mode]
    end
    
    HomeNetwork -.->|Firewall| Internet
    AdminPC <-->|HTTPS Future| BackendAPI
    UserPC <-->|HTTPS Future| BackendAPI
    BackendAPI <-->|Encrypted Future| LocalStorage
    BackendAPI <-.->|UDP/WiFi| TelloDrone
    
    style BackendAPI fill:#c8e6c9
    style HomeNetwork fill:#fff3e0
    style Internet fill:#ffebee
```

## 拡張性と将来計画

### 水平スケーリング
- 複数ドローン同時制御対応
- ロードバランサー導入
- マイクロサービス分離

### 機能拡張
- HTTPS/TLS暗号化
- ユーザー認証システム
- データベース永続化
- クラウド連携

### パフォーマンス最適化
- GPU加速AI処理
- キャッシュ層導入
- CDN配信対応