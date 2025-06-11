# システムコンテキストダイヤグラム

## 概要

システムコンテキスト図は、MFG Drone Backend API の外部環境との関係性を示し、システム境界と外部アクターとの相互作用を明確に定義します。

## システムコンテキスト図

```mermaid
graph TB
    subgraph "External Actors"
        Admin[システム管理者<br/>Admin User]
        GeneralUser[一般ユーザー<br/>General User]
        Operator[ドローン操縦者<br/>Drone Operator]
    end
    
    subgraph "Hardware Actors"
        TelloDrone[Tello EDU Drone<br/>Physical Device]
        RaspberryPi[Raspberry Pi 5<br/>Edge Computer]
        NetworkRouter[Network Router<br/>Infrastructure]
    end
    
    subgraph "MFG Drone System Boundary" 
        subgraph "Frontend Applications"
            AdminApp[Admin Frontend<br/>Flask Application]
            UserApp[User Frontend<br/>Flask Application]
        end
        
        subgraph "Backend Core System"
            BackendAPI[MFG Drone Backend API<br/>FastAPI Service]
        end
        
        subgraph "Data Storage"
            ModelStorage[AI Model Storage<br/>Local File System]
            ConfigStorage[Configuration Storage<br/>Local Files]
            LogStorage[Log Storage<br/>Local Files]
        end
    end
    
    subgraph "External Systems"
        InternetServices[インターネットサービス<br/>Future Integration]
        CloudStorage[クラウドストレージ<br/>Future Integration]
    end

    %% User Interactions
    Admin -->|モデル訓練<br/>システム設定<br/>飛行制御| AdminApp
    GeneralUser -->|映像視聴<br/>状態監視| UserApp
    Operator -->|緊急操作<br/>手動制御| AdminApp
    
    %% Application Interactions
    AdminApp <-->|REST API<br/>WebSocket| BackendAPI
    UserApp <-->|REST API<br/>WebSocket| BackendAPI
    
    %% Hardware Interactions
    BackendAPI <-.->|UDP 8889 Control<br/>UDP 11111 Video| TelloDrone
    BackendAPI <-->|システム運用| RaspberryPi
    
    %% Data Interactions
    BackendAPI <-->|モデル読み書き| ModelStorage
    BackendAPI <-->|設定管理| ConfigStorage
    BackendAPI <-->|ログ出力| LogStorage
    
    %% Network Infrastructure
    NetworkRouter <--> AdminApp
    NetworkRouter <--> UserApp
    NetworkRouter <--> BackendAPI
    NetworkRouter <-.-> TelloDrone
    
    %% Future Integrations
    BackendAPI -.->|将来連携| InternetServices
    BackendAPI -.->|将来連携| CloudStorage

    style Admin fill:#e1f5fe
    style GeneralUser fill:#e8f5e8
    style Operator fill:#fff3e0
    style BackendAPI fill:#f3e5f5
    style TelloDrone fill:#ffebee
```

## 外部アクター定義

### 人的アクター

#### 1. システム管理者 (Admin User)
**役割**: システム全体の管理・設定・監視を行う上級ユーザー

**責任範囲**:
- AI モデルの訓練・管理
- ドローンの飛行制御
- システム設定の変更
- セキュリティ設定の管理
- システム監視・メンテナンス

**システムとの関係**:
- Admin Frontend を通じた高権限操作
- 全ての API エンドポイントへのアクセス権
- システム状態の詳細監視

#### 2. 一般ユーザー (General User)
**役割**: リアルタイム映像の視聴とシステム状態の監視を行うエンドユーザー

**責任範囲**:
- ライブ映像ストリームの視聴
- ドローン状態の確認
- 基本的な情報取得

**システムとの関係**:
- User Frontend を通じた読み取り専用操作
- 制限された API エンドポイントへのアクセス
- リアルタイムデータの受信

#### 3. ドローン操縦者 (Drone Operator)
**役割**: 緊急時または手動制御が必要な場合の直接操縦担当者

**責任範囲**:
- 緊急時の手動介入
- 安全確保のための直接制御
- 飛行エリアの監視

**システムとの関係**:
- Admin Frontend または専用インターフェースを使用
- 緊急停止・手動制御の実行権限
- リアルタイム制御コマンドの送信

### ハードウェアアクター

#### 1. Tello EDU Drone
**特性**: DJI製の教育用小型ドローン

**機能**:
- 映像撮影・ストリーミング
- 自律飛行制御
- センサーデータ提供
- WiFi AP モードでの通信

**通信プロトコル**:
- UDP 8889: 制御コマンド送受信
- UDP 11111: 映像ストリーム受信

#### 2. Raspberry Pi 5
**特性**: バックエンド API のホスト環境

**役割**:
- FastAPI サーバーの実行環境
- AI 処理の計算リソース提供
- ローカルストレージの管理
- ネットワーク通信の処理

#### 3. Network Router
**特性**: ホームネットワークのインフラストラクチャ

**役割**:
- デバイス間通信の仲介
- インターネット接続の提供
- ネットワークセキュリティの確保

## システム境界

```mermaid
graph TB
    subgraph "External Environment"
        ExtUsers[External Users]
        Internet[Internet]
        Hardware[Physical Hardware]
    end
    
    subgraph "System Boundary"
        subgraph "Application Layer"
            Frontend[Frontend Applications]
            API[Backend API]
        end
        
        subgraph "Data Layer"
            Storage[Local Storage]
        end
    end
    
    subgraph "Infrastructure Layer"
        Network[Network Infrastructure]
        OS[Operating System]
    end

    ExtUsers <--> Frontend
    Frontend <--> API
    API <--> Storage
    API <--> Hardware
    
    Frontend <--> Network
    API <--> OS
    Storage <--> OS
    
    style Frontend fill:#e3f2fd
    style API fill:#f3e5f5
    style Storage fill:#fff3e0
```

## データ交換フロー

### 1. ユーザー認証フロー (将来実装)

```mermaid
sequenceDiagram
    participant User as User/Admin
    participant Frontend as Frontend App
    participant API as Backend API
    participant Auth as Auth Service

    User->>Frontend: Login Request
    Frontend->>API: Authentication
    API->>Auth: Validate Credentials
    Auth-->>API: Auth Token
    API-->>Frontend: Login Success
    Frontend-->>User: Dashboard Access
```

### 2. ドローン制御フロー

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant AdminApp as Admin Frontend
    participant API as Backend API
    participant Drone as Tello EDU

    Admin->>AdminApp: Flight Command
    AdminApp->>API: REST API Call
    API->>Drone: UDP Command
    Drone-->>API: Status Response
    API-->>AdminApp: Command Result
    AdminApp-->>Admin: Status Update
```

### 3. 映像ストリーミングフロー

```mermaid
sequenceDiagram
    participant Drone as Tello EDU
    participant API as Backend API
    participant UserApp as User Frontend
    participant User as General User

    Drone->>API: Video Frame (UDP)
    API->>API: Process Frame
    API->>UserApp: WebSocket Stream
    UserApp->>User: Display Video
    
    loop Continuous Streaming
        Drone->>API: Next Frame
        API->>UserApp: Stream Frame
    end
```

### 4. AI モデル訓練フロー

```mermaid
sequenceDiagram
    participant Admin as Admin User
    participant AdminApp as Admin Frontend
    participant API as Backend API
    participant Storage as Model Storage
    participant AI as AI Processing

    Admin->>AdminApp: Upload Training Images
    AdminApp->>API: POST /model/train
    API->>Storage: Save Training Data
    API->>AI: Start Training Process
    
    loop Training Progress
        AI->>API: Training Status
        API->>AdminApp: Progress Update
        AdminApp->>Admin: Status Display
    end
    
    AI->>Storage: Save Trained Model
    AI-->>API: Training Complete
    API-->>AdminApp: Model Ready
    AdminApp-->>Admin: Training Success
```

## セキュリティ境界

```mermaid
graph TB
    subgraph "Trust Zone: High"
        BackendCore[Backend API Core]
        LocalData[Local Data Storage]
    end
    
    subgraph "Trust Zone: Medium"
        FrontendApps[Frontend Applications]
        HomeNetwork[Home Network Devices]
    end
    
    subgraph "Trust Zone: Low"
        DroneComm[Drone Communication]
        ExternalAccess[External Access Points]
    end
    
    subgraph "Untrusted Zone"
        Internet[Internet Services]
        PublicWiFi[Public Networks]
    end

    %% Security boundaries
    FrontendApps -.->|Input Validation| BackendCore
    HomeNetwork -.->|Network Security| BackendCore
    DroneComm -.->|Protocol Security| BackendCore
    BackendCore -.->|Access Control| LocalData
    
    %% Threats and mitigations
    Internet -.->|Firewall| HomeNetwork
    PublicWiFi -.->|VPN Future| HomeNetwork
    
    style BackendCore fill:#c8e6c9
    style LocalData fill:#c8e6c9
    style FrontendApps fill:#fff3e0
    style DroneComm fill:#ffecb3
    style Internet fill:#ffebee
```

## 外部依存関係

### ハードウェア依存
- **Tello EDU Drone**: djitellopy SDK での通信
- **Raspberry Pi 5**: ARM64 アーキテクチャ対応
- **Network Infrastructure**: WiFi 802.11n/ac 対応

### ソフトウェア依存
- **Python 3.11+**: 実行環境
- **FastAPI**: Web フレームワーク
- **OpenCV**: 画像処理
- **djitellopy**: ドローン制御 SDK

### ネットワーク依存
- **UDP プロトコル**: ドローン通信
- **HTTP/WebSocket**: クライアント通信
- **WiFi 接続**: すべての通信の基盤

## 制約と前提条件

### 技術制約
1. **ドローン通信範囲**: WiFi 接続可能範囲内（約100m）
2. **映像品質**: 720p 最大、30fps 制限
3. **同時接続数**: WebSocket 接続10台まで
4. **処理能力**: Raspberry Pi 5 の計算リソース制限

### 運用制約
1. **飛行時間**: バッテリー寿命による制限（約13分）
2. **天候条件**: 屋内または良好な屋外環境
3. **ネットワーク**: 安定したWiFi環境必須
4. **法的制限**: ドローン飛行に関する法規制遵守

### 将来拡張計画
1. **クラウド連携**: AWS/Azure との統合
2. **セキュリティ強化**: HTTPS、認証システム
3. **スケーラビリティ**: マルチドローン対応
4. **データ分析**: 飛行ログ解析機能